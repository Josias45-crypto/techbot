from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id              = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    user_id         = Column(String, ForeignKey("users.id"))
    reference_code  = Column(String(20), nullable=False, unique=True)
    category        = Column(String(50), nullable=False)
    priority        = Column(String(20), nullable=False, default="medium")
    status          = Column(String(20), nullable=False, default="open")
    resolved_by     = Column(String(10))
    channel_origin  = Column(String(20), nullable=False)
    notes           = Column(Text)
    created_at      = Column(DateTime, nullable=False, server_default=func.now())
    updated_at      = Column(DateTime, nullable=False, server_default=func.now())
    closed_at       = Column(DateTime)

    # Relaciones
    conversation = relationship("Conversation", back_populates="ticket")
    user         = relationship("User", back_populates="tickets")
    history      = relationship("TicketHistory", back_populates="ticket")


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id              = Column(String, primary_key=True)
    ticket_id       = Column(String, ForeignKey("tickets.id"), nullable=False)
    previous_status = Column(String(20))
    new_status      = Column(String(20), nullable=False)
    changed_by_id   = Column(String, ForeignKey("users.id"))
    note            = Column(Text)
    created_at      = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    ticket     = relationship("Ticket", back_populates="history")
    changed_by = relationship("User")
