from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import random
import asyncio

from config import settings
from database import get_db, init_db
from models import Group, AffiliateLink, ProcessedMessage, PostedMessage, ActivityLog
from schemas import (
    GroupCreate, GroupUpdate, GroupResponse, GroupStats,
    AffiliateLinkCreate, AffiliateLinkUpdate, AffiliateLinkResponse,
    DashboardStats, RedirectResponse
)
from whapi_client import WhapiClient, LinkProcessor
from background_tasks import BackgroundTaskManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="WhatsApp Automation API",
    description="API para automação de WhatsApp com gerenciamento de grupos e links de afiliado",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar cliente Whapi
whapi_client = WhapiClient()

# Inicializar gerenciador de tarefas em background
background_manager = BackgroundTaskManager(whapi_client)

# Variável para armazenar as tasks
monitoring_task = None
members_update_task = None

# ============ Startup & Shutdown ============

@app.on_event("startup")
async def startup_event():
    """Executar ao iniciar a aplicação"""
    global monitoring_task, members_update_task
    
    logger.info("Iniciando aplicação...")
    
    # Validar configurações críticas
    if not settings.whapi_api_key:
        logger.error("ERRO: WHAPI_API_KEY não configurada!")
        logger.error("Configure a variável de ambiente WHAPI_API_KEY no arquivo .env")
        # Não impedir inicialização, mas avisar
    
    if not settings.source_group_id:
        logger.warning("AVISO: SOURCE_GROUP_ID não configurado. Monitoramento não será iniciado.")
    
    # Inicializar banco de dados
    try:
        init_db()
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise
    
    # Iniciar tarefas em background apenas se configurado
    if settings.whapi_api_key and settings.source_group_id:
        try:
            # Iniciar monitoramento do grupo de origem
            monitoring_task = asyncio.create_task(
                background_manager.start_monitoring(
                    source_group_id=settings.source_group_id,
                    check_interval=60  # Verificar a cada 60 segundos
                )
            )
            logger.info(f"Monitoramento do grupo {settings.source_group_id} iniciado")
            
            # Iniciar atualização de contagem de membros
            members_update_task = asyncio.create_task(
                background_manager.update_group_members_count(
                    check_interval=3600  # Atualizar a cada 1 hora
                )
            )
            logger.info("Atualização periódica de membros iniciada")
        except Exception as e:
            logger.error(f"Erro ao iniciar tarefas em background: {str(e)}")
    else:
        logger.warning("Tarefas em background não iniciadas. Verifique configurações.")

@app.on_event("shutdown")
async def shutdown_event():
    """Executar ao desligar a aplicação"""
    global monitoring_task, members_update_task
    
    logger.info("Desligando aplicação...")
    
    # Parar tarefas em background
    background_manager.stop()
    
    # Cancelar tasks
    if monitoring_task:
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            logger.info("Task de monitoramento cancelada")
    
    if members_update_task:
        members_update_task.cancel()
        try:
            await members_update_task
        except asyncio.CancelledError:
            logger.info("Task de atualização de membros cancelada")
    
    logger.info("Aplicação desligada com sucesso")

# ============ Health Check ============

@app.get("/health")
async def health_check():
    """Verificar saúde da API"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "monitoring_active": background_manager.is_running,
        "whapi_configured": bool(settings.whapi_api_key),
        "source_group_configured": bool(settings.source_group_id)
    }

# ============ Groups Endpoints ============

@app.post("/api/groups", response_model=GroupResponse)
async def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db)
):
    """Criar um novo grupo"""
    try:
        # Verificar se o grupo já existe
        existing = db.query(Group).filter(Group.id == group.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Grupo já existe")
        
        # Criar novo grupo
        new_group = Group(
            id=group.name,
            name=group.name,
            invite_link=group.invite_link,
            max_capacity=group.max_capacity,
            bot_number=group.bot_number,
            order=group.order
        )
        
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        
        # Registrar atividade
        log = ActivityLog(
            action="GROUP_CREATED",
            description=f"Grupo '{group.name}' criado",
            related_group_id=new_group.id,
            status="SUCCESS"
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Grupo criado: {group.name}")
        return new_group
    
    except Exception as e:
        logger.error(f"Erro ao criar grupo: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/groups", response_model=list[GroupResponse])
async def list_groups(
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """Listar todos os grupos"""
    query = db.query(Group)
    if active_only:
        query = query.filter(Group.is_active == True)
    
    groups = query.order_by(Group.order).all()
    return groups

@app.get("/api/groups/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    db: Session = Depends(get_db)
):
    """Obter detalhes de um grupo"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return group

@app.put("/api/groups/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    group_update: GroupUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar um grupo"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    
    # Atualizar campos - CORRIGIDO: usar model_dump ao invés de dict
    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)
    
    group.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(group)
    
    logger.info(f"Grupo atualizado: {group_id}")
    return group

@app.delete("/api/groups/{group_id}")
async def delete_group(
    group_id: str,
    db: Session = Depends(get_db)
):
    """Deletar um grupo"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    
    db.delete(group)
    db.commit()
    
    logger.info(f"Grupo deletado: {group_id}")
    return {"message": "Grupo deletado com sucesso"}

# ============ Affiliate Links Endpoints ============

@app.post("/api/affiliate-links", response_model=AffiliateLinkResponse)
async def create_affiliate_link(
    link: AffiliateLinkCreate,
    db: Session = Depends(get_db)
):
    """Criar um novo link de afiliado"""
    try:
        # Verificar se já existe
        existing = db.query(AffiliateLink).filter(
            AffiliateLink.domain_base == link.domain_base
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Link de afiliado para este domínio já existe")
        
        new_link = AffiliateLink(
            domain_base=link.domain_base,
            affiliate_link=link.affiliate_link,
            description=link.description
        )
        
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
        
        logger.info(f"Link de afiliado criado: {link.domain_base}")
        return new_link
    
    except Exception as e:
        logger.error(f"Erro ao criar link de afiliado: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/affiliate-links", response_model=list[AffiliateLinkResponse])
async def list_affiliate_links(
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """Listar todos os links de afiliado"""
    query = db.query(AffiliateLink)
    if active_only:
        query = query.filter(AffiliateLink.is_active == True)
    
    links = query.all()
    return links

@app.put("/api/affiliate-links/{link_id}", response_model=AffiliateLinkResponse)
async def update_affiliate_link(
    link_id: int,
    link_update: AffiliateLinkUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar um link de afiliado"""
    link = db.query(AffiliateLink).filter(AffiliateLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link de afiliado não encontrado")
    
    # CORRIGIDO: usar model_dump ao invés de dict
    update_data = link_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(link, field, value)
    
    link.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(link)
    
    logger.info(f"Link de afiliado atualizado: {link_id}")
    return link

@app.delete("/api/affiliate-links/{link_id}")
async def delete_affiliate_link(
    link_id: int,
    db: Session = Depends(get_db)
):
    """Deletar um link de afiliado"""
    link = db.query(AffiliateLink).filter(AffiliateLink.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link de afiliado não encontrado")
    
    db.delete(link)
    db.commit()
    
    logger.info(f"Link de afiliado deletado: {link_id}")
    return {"message": "Link de afiliado deletado com sucesso"}

# ============ Dashboard Endpoints ============

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obter estatísticas do dashboard"""
    total_groups = db.query(Group).count()
    active_groups = db.query(Group).filter(Group.is_active == True).count()
    full_groups = db.query(Group).filter(Group.status == "CHEIO").count()
    available_groups = db.query(Group).filter(Group.status == "DISPONIVEL").count()
    total_affiliate_links = db.query(AffiliateLink).count()
    total_messages_processed = db.query(ProcessedMessage).count()
    total_messages_posted = db.query(PostedMessage).count()
    bots_connected = 1 if background_manager.is_running else 0
    
    return DashboardStats(
        total_groups=total_groups,
        active_groups=active_groups,
        full_groups=full_groups,
        available_groups=available_groups,
        total_affiliate_links=total_affiliate_links,
        total_messages_processed=total_messages_processed,
        total_messages_posted=total_messages_posted,
        bots_connected=bots_connected
    )

@app.get("/api/dashboard/group-stats/{group_id}", response_model=GroupStats)
async def get_group_stats(
    group_id: str,
    db: Session = Depends(get_db)
):
    """Obter estatísticas de um grupo específico"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    
    messages_posted = db.query(PostedMessage).filter(
        PostedMessage.group_id == group_id
    ).count()
    
    last_message = db.query(PostedMessage).filter(
        PostedMessage.group_id == group_id
    ).order_by(PostedMessage.posted_at.desc()).first()
    
    capacity_percentage = (group.current_members / group.max_capacity * 100) if group.max_capacity > 0 else 0
    
    return GroupStats(
        group=group,
        messages_posted_count=messages_posted,
        last_message_posted_at=last_message.posted_at if last_message else None,
        capacity_percentage=capacity_percentage
    )

# ============ Redirect Endpoint ============

@app.get("/api/redirect", response_model=RedirectResponse)
async def redirect_to_group(
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Redirecionar para o próximo grupo disponível
    Este é o link único que será publicado no site
    """
    try:
        # Buscar o primeiro grupo disponível
        available_group = db.query(Group).filter(
            Group.status == "DISPONIVEL",
            Group.is_active == True
        ).order_by(Group.order).first()
        
        if not available_group:
            # Se não houver grupos disponíveis, pegar o primeiro ativo
            available_group = db.query(Group).filter(
                Group.is_active == True
            ).order_by(Group.order).first()
            
            if not available_group:
                raise HTTPException(status_code=404, detail="Nenhum grupo disponível")
        
        # Registrar atividade
        log = ActivityLog(
            action="REDIRECT_CLICKED",
            description=f"Usuário redirecionado para grupo: {available_group.name}",
            related_group_id=available_group.id,
            status="SUCCESS"
        )
        db.add(log)
        db.commit()
        
        return RedirectResponse(
            redirect_url=available_group.invite_link,
            group_id=available_group.id,
            group_name=available_group.name,
            message=f"Bem-vindo ao grupo {available_group.name}!"
        )
    
    except Exception as e:
        logger.error(f"Erro ao redirecionar: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Activity Logs Endpoints ============

@app.get("/api/activity-logs")
async def get_activity_logs(
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Obter logs de atividade"""
    logs = db.query(ActivityLog).order_by(
        ActivityLog.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return logs

# ============ Control Endpoints ============

@app.post("/api/control/start-monitoring")
async def start_monitoring_manual(db: Session = Depends(get_db)):
    """Iniciar monitoramento manualmente"""
    global monitoring_task
    
    if not settings.source_group_id:
        raise HTTPException(status_code=400, detail="SOURCE_GROUP_ID não configurado")
    
    if background_manager.is_running:
        return {"message": "Monitoramento já está ativo"}
    
    try:
        monitoring_task = asyncio.create_task(
            background_manager.start_monitoring(
                source_group_id=settings.source_group_id,
                check_interval=60
            )
        )
        logger.info("Monitoramento iniciado manualmente")
        return {"message": "Monitoramento iniciado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao iniciar monitoramento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/control/stop-monitoring")
async def stop_monitoring_manual():
    """Parar monitoramento manualmente"""
    global monitoring_task
    
    background_manager.stop()
    
    if monitoring_task:
        monitoring_task.cancel()
    
    logger.info("Monitoramento parado manualmente")
    return {"message": "Monitoramento parado com sucesso"}

# ============ Utility Endpoints ============

@app.post("/api/test/send-message")
async def test_send_message(
    chat_id: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Endpoint de teste para enviar mensagem (apenas para desenvolvimento)"""
    if settings.environment != "development":
        raise HTTPException(status_code=403, detail="Endpoint não disponível em produção")
    
    try:
        result = await whapi_client.send_message(chat_id, message)
        return result
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem de teste: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test/update-group-members")
async def test_update_group_members(
    group_id: str,
    db: Session = Depends(get_db)
):
    """Endpoint de teste para atualizar contagem de membros"""
    if settings.environment != "development":
        raise HTTPException(status_code=403, detail="Endpoint não disponível em produção")
    
    try:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Grupo não encontrado")
        
        # Obter contagem de membros da API Whapi
        member_count = await whapi_client.get_group_members_count(group_id)
        
        if member_count is not None:
            group.current_members = member_count
            group.last_member_count_update = datetime.utcnow()
            
            # Atualizar status
            if member_count >= group.max_capacity:
                group.status = "CHEIO"
            else:
                group.status = "DISPONIVEL"
            
            db.commit()
            db.refresh(group)
            
            return {
                "group_id": group_id,
                "current_members": member_count,
                "max_capacity": group.max_capacity,
                "status": group.status
            }
        else:
            raise HTTPException(status_code=500, detail="Não foi possível obter contagem de membros")
    
    except Exception as e:
        logger.error(f"Erro ao atualizar membros: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.environment == "development"
    )