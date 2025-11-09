import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import random

from models import Group, AffiliateLink, ProcessedMessage, PostedMessage, ActivityLog
from whapi_client import WhapiClient, LinkProcessor
from database import SessionLocal

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Gerenciador de tarefas em background"""
    
    def __init__(self, whapi_client: WhapiClient = None):
        self.whapi_client = whapi_client or WhapiClient()
        self.is_running = False
    
    async def start_monitoring(self, source_group_id: str, check_interval: int = 60):
        """
        Iniciar monitoramento contínuo do grupo de origem
        
        Args:
            source_group_id: ID do grupo a monitorar
            check_interval: Intervalo em segundos entre verificações
        """
        self.is_running = True
        logger.info(f"Iniciando monitoramento do grupo {source_group_id}")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_running:
            db = None
            try:
                db = SessionLocal()
                await self._check_and_process_messages(source_group_id, db)
                
                # Reset contador de erros em caso de sucesso
                consecutive_errors = 0
                
                await asyncio.sleep(check_interval)
            
            except asyncio.CancelledError:
                logger.info("Monitoramento cancelado")
                break
            
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Erro no monitoramento (tentativa {consecutive_errors}/{max_consecutive_errors}): {str(e)}")
                
                # Se muitos erros consecutivos, aumentar intervalo
                if consecutive_errors >= max_consecutive_errors:
                    logger.warning(f"Muitos erros consecutivos. Aumentando intervalo para {check_interval * 2}s")
                    await asyncio.sleep(check_interval * 2)
                    consecutive_errors = 0  # Reset após espera longa
                else:
                    await asyncio.sleep(check_interval)
            
            finally:
                if db:
                    db.close()
    
    async def _check_and_process_messages(self, source_group_id: str, db: Session):
        """
        Verificar novas mensagens e processá-las
        
        Args:
            source_group_id: ID do grupo de origem
            db: Sessão do banco de dados
        """
        try:
            # Obter mensagens recentes do grupo
            messages = await self.whapi_client.get_messages(source_group_id, limit=10)
            
            if not messages:
                logger.debug(f"Nenhuma mensagem encontrada no grupo {source_group_id}")
                return
            
            # Processar cada mensagem
            for message in messages:
                try:
                    await self._process_message(message, source_group_id, db)
                except Exception as e:
                    logger.error(f"Erro ao processar mensagem individual: {str(e)}")
                    # Continuar processando outras mensagens
                    continue
        
        except Exception as e:
            logger.error(f"Erro ao verificar mensagens: {str(e)}")
            raise
    
    async def _process_message(self, message: Dict[str, Any], source_group_id: str, db: Session):
        """
        Processar uma mensagem individual
        
        Args:
            message: Dados da mensagem
            source_group_id: ID do grupo de origem
            db: Sessão do banco de dados
        """
        try:
            message_id = message.get("id")
            message_text = message.get("body", "")
            
            if not message_id or not message_text:
                logger.debug("Mensagem sem ID ou texto, ignorando")
                return
            
            # Verificar se já foi processada
            existing = db.query(ProcessedMessage).filter(
                ProcessedMessage.id == message_id
            ).first()
            
            if existing:
                logger.debug(f"Mensagem {message_id} já foi processada")
                return
            
            # Extrair links
            links = LinkProcessor.extract_links(message_text)
            
            if not links:
                logger.debug(f"Mensagem {message_id} não contém links")
                return
            
            logger.info(f"Processando mensagem {message_id} com {len(links)} link(s)")
            
            # Registrar mensagem processada
            processed_msg = ProcessedMessage(
                id=message_id,
                source_group_id=source_group_id,
                message_text=message_text,
                original_links=str(links)
            )
            db.add(processed_msg)
            db.commit()
            
            # Obter mapa de links de afiliado
            affiliate_links = db.query(AffiliateLink).filter(
                AffiliateLink.is_active == True
            ).all()
            
            if not affiliate_links:
                logger.warning("Nenhum link de afiliado configurado")
                affiliate_map = {}
            else:
                affiliate_map = {link.domain_base: link.affiliate_link for link in affiliate_links}
            
            # Substituir links
            processed_text = LinkProcessor.replace_links(message_text, affiliate_map)
            
            # Postar em todos os grupos de destino
            await self._post_to_groups(processed_text, message_id, db)
            
            logger.info(f"Mensagem {message_id} processada e postada com sucesso")
        
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            db.rollback()
            raise
    
    async def _post_to_groups(self, text: str, original_message_id: str, db: Session):
        """
        Postar mensagem em todos os grupos de destino
        
        Args:
            text: Texto processado
            original_message_id: ID da mensagem original
            db: Sessão do banco de dados
        """
        try:
            # Obter todos os grupos ativos
            groups = db.query(Group).filter(Group.is_active == True).all()
            
            if not groups:
                logger.warning("Nenhum grupo de destino ativo encontrado")
                return
            
            logger.info(f"Postando mensagem em {len(groups)} grupo(s)")
            
            for group in groups:
                try:
                    # Delay aleatório entre 5 e 15 segundos para simular comportamento humano
                    delay = random.uniform(5, 15)
                    
                    logger.debug(f"Enviando para grupo {group.name} após {delay:.1f}s")
                    
                    # Enviar mensagem
                    result = await self.whapi_client.send_message(
                        group.id,
                        text,
                        delay=delay
                    )
                    
                    # Verificar se houve erro
                    has_error = "error" in result
                    
                    # Registrar postagem
                    posted_msg = PostedMessage(
                        group_id=group.id,
                        original_message_id=original_message_id,
                        processed_text=text,
                        whatsapp_message_id=result.get("id"),
                        status="ENVIADO" if not has_error else "FALHA",
                        error_message=result.get("error") if has_error else None
                    )
                    db.add(posted_msg)
                    
                    # Registrar atividade
                    log = ActivityLog(
                        action="MESSAGE_POSTED" if not has_error else "MESSAGE_POST_FAILED",
                        description=f"Mensagem {'postada' if not has_error else 'falhou'} no grupo {group.name}",
                        related_group_id=group.id,
                        related_message_id=original_message_id,
                        status="SUCCESS" if not has_error else "FAILURE"
                    )
                    db.add(log)
                    db.commit()
                    
                    if not has_error:
                        logger.info(f"✓ Mensagem postada no grupo {group.name}")
                    else:
                        logger.error(f"✗ Falha ao postar no grupo {group.name}: {result.get('error')}")
                
                except Exception as e:
                    logger.error(f"Exceção ao postar no grupo {group.id}: {str(e)}")
                    
                    # Registrar falha
                    try:
                        posted_msg = PostedMessage(
                            group_id=group.id,
                            original_message_id=original_message_id,
                            processed_text=text,
                            status="FALHA",
                            error_message=str(e)
                        )
                        db.add(posted_msg)
                        
                        log = ActivityLog(
                            action="MESSAGE_POST_FAILED",
                            description=f"Erro ao postar no grupo {group.id}: {str(e)}",
                            related_group_id=group.id,
                            related_message_id=original_message_id,
                            status="FAILURE"
                        )
                        db.add(log)
                        db.commit()
                    except Exception as log_error:
                        logger.error(f"Erro ao registrar falha: {str(log_error)}")
                        db.rollback()
        
        except Exception as e:
            logger.error(f"Erro ao postar em grupos: {str(e)}")
            raise
    
    async def update_group_members_count(self, check_interval: int = 3600):
        """
        Atualizar contagem de membros de todos os grupos periodicamente
        
        Args:
            check_interval: Intervalo em segundos entre atualizações (padrão: 1 hora)
        """
        self.is_running = True
        logger.info("Iniciando atualização periódica de membros")
        
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while self.is_running:
            db = None
            try:
                db = SessionLocal()
                
                groups = db.query(Group).filter(Group.is_active == True).all()
                
                if not groups:
                    logger.debug("Nenhum grupo ativo para atualizar")
                else:
                    logger.info(f"Atualizando contagem de membros de {len(groups)} grupo(s)")
                
                for group in groups:
                    try:
                        member_count = await self.whapi_client.get_group_members_count(group.id)
                        
                        if member_count is not None:
                            old_count = group.current_members
                            old_status = group.status
                            
                            group.current_members = member_count
                            group.last_member_count_update = datetime.utcnow()
                            
                            # Atualizar status baseado na capacidade
                            if member_count >= group.max_capacity:
                                if group.status != "CHEIO":
                                    group.status = "CHEIO"
                                    logger.info(f"Grupo {group.name} está cheio ({member_count}/{group.max_capacity})")
                            else:
                                # Se estava cheio e agora tem vagas, voltar a disponível
                                if group.status == "CHEIO" and (group.max_capacity - member_count) > 5:
                                    group.status = "DISPONIVEL"
                                    logger.info(f"Grupo {group.name} voltou a estar disponível ({member_count}/{group.max_capacity})")
                            
                            db.commit()
                            
                            if old_count != member_count or old_status != group.status:
                                logger.info(f"Grupo {group.name}: {old_count} → {member_count} membros, status: {old_status} → {group.status}")
                        else:
                            logger.warning(f"Não foi possível obter contagem de membros do grupo {group.name}")
                    
                    except Exception as e:
                        logger.error(f"Erro ao atualizar membros do grupo {group.id}: {str(e)}")
                        # Continuar com próximo grupo
                        continue
                
                # Reset contador de erros em caso de sucesso
                consecutive_errors = 0
                
                await asyncio.sleep(check_interval)
            
            except asyncio.CancelledError:
                logger.info("Atualização de membros cancelada")
                break
            
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Erro na atualização de membros (tentativa {consecutive_errors}/{max_consecutive_errors}): {str(e)}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.warning(f"Muitos erros consecutivos. Aumentando intervalo para {check_interval * 2}s")
                    await asyncio.sleep(check_interval * 2)
                    consecutive_errors = 0
                else:
                    await asyncio.sleep(check_interval)
            
            finally:
                if db:
                    db.close()
    
    def stop(self):
        """Parar tarefas em background"""
        self.is_running = False
        logger.info("Tarefas em background paradas")