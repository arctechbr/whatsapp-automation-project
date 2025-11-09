import httpx
import asyncio
import re
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from config import settings
import logging

logger = logging.getLogger(__name__)

class WhapiClient:
    """Cliente para interagir com a API Whapi.Cloud"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or settings.whapi_api_key
        self.api_url = api_url or settings.whapi_api_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_message(self, chat_id: str, message: str, delay: float = 0) -> Dict[str, Any]:
        """
        Enviar uma mensagem para um chat/grupo
        
        Args:
            chat_id: ID do chat (grupo ou contato)
            message: Texto da mensagem
            delay: Delay em segundos antes de enviar (para simular comportamento humano)
        
        Returns:
            Resposta da API
        """
        if delay > 0:
            await asyncio.sleep(delay)
        
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "to": chat_id,
                    "body": message
                }
                
                response = await client.post(
                    f"{self.api_url}/messages/text",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Mensagem enviada para {chat_id}")
                    return response.json()
                else:
                    logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                    return {"error": response.text, "status_code": response.status_code}
            
            except Exception as e:
                logger.error(f"Exceção ao enviar mensagem: {str(e)}")
                return {"error": str(e)}
    
    async def get_group_members_count(self, group_id: str) -> Optional[int]:
        """
        Obter a contagem de membros de um grupo
        
        Args:
            group_id: ID do grupo
        
        Returns:
            Número de membros ou None se erro
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_url}/groups/{group_id}",
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # A resposta pode variar, tente diferentes estruturas
                    if "members_count" in data:
                        return data["members_count"]
                    elif "participants" in data:
                        return len(data["participants"])
                    else:
                        logger.warning(f"Estrutura de resposta inesperada: {data}")
                        return None
                else:
                    logger.error(f"Erro ao obter membros: {response.status_code}")
                    return None
            
            except Exception as e:
                logger.error(f"Exceção ao obter membros: {str(e)}")
                return None
    
    async def get_messages(self, chat_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obter mensagens de um chat/grupo
        
        Args:
            chat_id: ID do chat
            limit: Número máximo de mensagens
        
        Returns:
            Lista de mensagens
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_url}/messages",
                    params={"chat_id": chat_id, "limit": limit},
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("messages", [])
                else:
                    logger.error(f"Erro ao obter mensagens: {response.status_code}")
                    return []
            
            except Exception as e:
                logger.error(f"Exceção ao obter mensagens: {str(e)}")
                return []
    
    async def get_group_info(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        Obter informações de um grupo
        
        Args:
            group_id: ID do grupo
        
        Returns:
            Informações do grupo ou None se erro
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_url}/groups/{group_id}",
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Erro ao obter info do grupo: {response.status_code}")
                    return None
            
            except Exception as e:
                logger.error(f"Exceção ao obter info do grupo: {str(e)}")
                return None


class LinkProcessor:
    """Processador de links para substituição de afiliados"""
    
    # Regex para encontrar URLs
    URL_REGEX = r'https?://(?:www\.)?[\w\.-]+\.\w+[\w\./\-\?&=%]*'
    
    @staticmethod
    def extract_links(text: str) -> List[str]:
        """
        Extrair todos os links de um texto
        
        Args:
            text: Texto contendo links
        
        Returns:
            Lista de links encontrados
        """
        return re.findall(LinkProcessor.URL_REGEX, text)
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """
        Extrair domínio de uma URL
        
        Args:
            url: URL completa
        
        Returns:
            Domínio (ex: shopee.com.br)
        """
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            return match.group(1)
        return ""
    
    @staticmethod
    def replace_links(text: str, affiliate_map: Dict[str, str]) -> str:
        """
        Substituir links originais por links de afiliado
        
        Args:
            text: Texto original
            affiliate_map: Mapa de domínios para links de afiliado
        
        Returns:
            Texto com links substituídos
        """
        def replace_match(match):
            original_link = match.group(0)
            domain = LinkProcessor.extract_domain(original_link)
            
            # Procurar por correspondência exata ou parcial
            if domain in affiliate_map:
                return affiliate_map[domain]
            
            # Tentar correspondência parcial (ex: shopee.com.br em shopee.com)
            for key, value in affiliate_map.items():
                if key in domain or domain in key:
                    return value
            
            return original_link
        
        return re.sub(LinkProcessor.URL_REGEX, replace_match, text)
    
    @staticmethod
    def extract_links_with_context(text: str) -> Dict[str, str]:
        """
        Extrair links e seus domínios
        
        Args:
            text: Texto contendo links
        
        Returns:
            Dicionário com links e seus domínios
        """
        links = LinkProcessor.extract_links(text)
        result = {}
        
        for link in links:
            domain = LinkProcessor.extract_domain(link)
            result[link] = domain
        
        return result
