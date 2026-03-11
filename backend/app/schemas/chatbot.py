from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal


# -- INTENT ----------------------------------------
class IntentBase(BaseModel):
    name: str
    description: Optional[str] = None
    training_examples: List[str] = []
    confidence_threshold: float = 0.75

class IntentCreate(IntentBase):
    pass

class IntentResponse(IntentBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -- CONVERSATION ----------------------------------
class ConversationCreate(BaseModel):
    channel: str
    user_id: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    session_id: str
    user_id: Optional[str] = None
    channel: str
    status: str
    assigned_agent_id: Optional[str] = None
    resolved_by: Optional[str] = None
    started_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# -- MESSAGE ---------------------------------------
class MessageCreate(BaseModel):
    content: str
    sender_type: str
    sender_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_type: str
    sender_id: Optional[str] = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# -- CHAT (entrada del usuario al chatbot) ---------
class ChatInput(BaseModel):
    message: str
    session_token: str
    user_id: Optional[str] = None
    channel: str = "web"

class ChatResponse(BaseModel):
    message: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    escalated: bool = False
    conversation_id: str
    suggestions: List[str] = []


# -- ESCALATION ------------------------------------
class EscalationResponse(BaseModel):
    id: str
    conversation_id: str
    reason: str
    confidence_score: Optional[Decimal] = None
    agent_id: Optional[str] = None
    escalated_at: datetime
    attended_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# -- MESSAGE INTENT --------------------------------
class MessageIntentResponse(BaseModel):
    id: str
    message_id: str
    intent_id: str
    confidence: Decimal
    detected_entities: Any
    created_at: datetime

    class Config:
        from_attributes = True
