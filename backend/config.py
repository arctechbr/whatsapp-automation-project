from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/whatsapp_automation"
    
    # Whapi Configuration
    whapi_api_key: str = ""
    whapi_api_url: str = "https://api.whapi.cloud"
    
    # Bot Numbers
    bot_reader_number: str = ""
    bot_poster_number: str = ""
    
    # Source Group
    source_group_id: str = ""
    
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    environment: str = "development"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # JWT
    secret_key: str = "sua_chave_secreta_super_segura_aqui"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
