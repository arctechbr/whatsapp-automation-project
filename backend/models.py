from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Group(Base):
    """Modelo para grupos de WhatsApp gerenciados"""
    __tablename__ = "groups"
    
    id = Column(String, primary_key=True)  # ID do grupo no WhatsApp
    name = Column(String, nullable=False)
    invite_link = Column(String, nullable=False, unique=True)
    max_capacity = Column(Integer, default=257)
    current_members = Column(Integer, default=0)
    status = Column(String, default="DISPONIVEL")  # DISPONIVEL ou CHEIO
    order = Column(Integer, default=0)  # Ordem de prioridade
    bot_number = Column(String, nullable=False)  # Número do bot responsável
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_member_count_update = Column(DateTime, nullable=True)
    
    # Relacionamentos
    posted_messages = relationship("PostedMessage", back_populates="group")
    
    def __repr__(self):
        return f"<Group {self.name} - {self.status}>"


class AffiliateLink(Base):
    """Modelo para mapeamento de links de afiliado"""
    __tablename__ = "affiliate_links"
    
    id = Column(Integer, primary_key=True)
    domain_base = Column(String, nullable=False, unique=True)  # Ex: shopee.com.br
    affiliate_link = Column(String, nullable=False)  # Seu link de afiliado
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AffiliateLink {self.domain_base}>"


class ProcessedMessage(Base):
    """Modelo para rastrear mensagens já processadas (evitar duplicação)"""
    __tablename__ = "processed_messages"
    
    id = Column(String, primary_key=True)  # ID único da mensagem original
    source_group_id = Column(String, nullable=False)
    message_text = Column(Text, nullable=False)
    original_links = Column(Text, nullable=True)  # JSON com links encontrados
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProcessedMessage {self.id}>"


class PostedMessage(Base):
    """Modelo para rastrear mensagens postadas nos grupos de destino"""
    __tablename__ = "posted_messages"
    
    id = Column(Integer, primary_key=True)
    group_id = Column(String, ForeignKey("groups.id"), nullable=False)
    original_message_id = Column(String, ForeignKey("processed_messages.id"), nullable=False)
    processed_text = Column(Text, nullable=False)
    posted_at = Column(DateTime, default=datetime.utcnow)
    whatsapp_message_id = Column(String, nullable=True)  # ID da mensagem no WhatsApp
    status = Column(String, default="ENVIADO")  # ENVIADO, FALHA, PENDENTE
    error_message = Column(Text, nullable=True)
    
    # Relacionamentos
    group = relationship("Group", back_populates="posted_messages")
    
    def __repr__(self):
        return f"<PostedMessage {self.id} - {self.status}>"


class BotSession(Base):
    """Modelo para rastrear sessões de bots"""
    __tablename__ = "bot_sessions"
    
    id = Column(Integer, primary_key=True)
    bot_number = Column(String, nullable=False, unique=True)
    bot_type = Column(String, nullable=False)  # READER ou POSTER
    is_connected = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    session_data = Column(Text, nullable=True)  # JSON com dados da sessão
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BotSession {self.bot_number} - {self.bot_type}>"


class ActivityLog(Base):
    """Modelo para registrar atividades do sistema"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)  # Ex: MESSAGE_POSTED, GROUP_UPDATED, ERROR
    description = Column(Text, nullable=False)
    related_group_id = Column(String, nullable=True)
    related_message_id = Column(String, nullable=True)
    status = Column(String, default="SUCCESS")  # SUCCESS ou FAILURE
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ActivityLog {self.action} - {self.status}>"
