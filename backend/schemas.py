from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ============ Group Schemas ============

class GroupCreate(BaseModel):
    """Schema para criar um novo grupo"""
    name: str
    invite_link: str
    max_capacity: int = 257
    bot_number: str
    order: int = 0

class GroupUpdate(BaseModel):
    """Schema para atualizar um grupo"""
    name: Optional[str] = None
    invite_link: Optional[str] = None
    max_capacity: Optional[int] = None
    status: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

class GroupResponse(BaseModel):
    """Schema para resposta de grupo"""
    id: str
    name: str
    invite_link: str
    max_capacity: int
    current_members: int
    status: str
    order: int
    bot_number: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============ Affiliate Link Schemas ============

class AffiliateLinkCreate(BaseModel):
    """Schema para criar um novo link de afiliado"""
    domain_base: str
    affiliate_link: str
    description: Optional[str] = None

class AffiliateLinkUpdate(BaseModel):
    """Schema para atualizar um link de afiliado"""
    domain_base: Optional[str] = None
    affiliate_link: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class AffiliateLinkResponse(BaseModel):
    """Schema para resposta de link de afiliado"""
    id: int
    domain_base: str
    affiliate_link: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============ Message Schemas ============

class ProcessedMessageResponse(BaseModel):
    """Schema para resposta de mensagem processada"""
    id: str
    source_group_id: str
    message_text: str
    original_links: Optional[str]
    processed_at: datetime
    
    class Config:
        from_attributes = True

class PostedMessageResponse(BaseModel):
    """Schema para resposta de mensagem postada"""
    id: int
    group_id: str
    original_message_id: str
    processed_text: str
    posted_at: datetime
    status: str
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

# ============ Bot Session Schemas ============

class BotSessionResponse(BaseModel):
    """Schema para resposta de sessão de bot"""
    id: int
    bot_number: str
    bot_type: str
    is_connected: bool
    last_heartbeat: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============ Activity Log Schemas ============

class ActivityLogResponse(BaseModel):
    """Schema para resposta de log de atividade"""
    id: int
    action: str
    description: str
    related_group_id: Optional[str]
    related_message_id: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============ Dashboard Schemas ============

class DashboardStats(BaseModel):
    """Schema para estatísticas do dashboard"""
    total_groups: int
    active_groups: int
    full_groups: int
    available_groups: int
    total_affiliate_links: int
    total_messages_processed: int
    total_messages_posted: int
    bots_connected: int

class GroupStats(BaseModel):
    """Schema para estatísticas de um grupo"""
    group: GroupResponse
    messages_posted_count: int
    last_message_posted_at: Optional[datetime]
    capacity_percentage: float

# ============ Redirect Schemas ============

class RedirectResponse(BaseModel):
    """Schema para resposta de redirecionamento"""
    redirect_url: str
    group_id: str
    group_name: str
    message: str
