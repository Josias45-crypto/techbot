from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# -- TICKET ----------------------------------------
class TicketBase(BaseModel):
    category: str
    priority: str = "medium"
    channel_origin: str
    notes: Optional[str] = None

class TicketCreate(TicketBase):
    conversation_id: str
    user_id: Optional[str] = None

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    resolved_by: Optional[str] = None

class TicketResponse(TicketBase):
    id: str
    conversation_id: str
    user_id: Optional[str] = None
    reference_code: str
    status: str
    resolved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# -- TICKET HISTORY --------------------------------
class TicketHistoryCreate(BaseModel):
    ticket_id: str
    previous_status: Optional[str] = None
    new_status: str
    changed_by_id: Optional[str] = None
    note: Optional[str] = None

class TicketHistoryResponse(BaseModel):
    id: str
    ticket_id: str
    previous_status: Optional[str] = None
    new_status: str
    changed_by_id: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TicketWithHistory(TicketResponse):
    history: List[TicketHistoryResponse] = []
