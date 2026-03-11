from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Intent(Base):
    __tablename__ = "intents"

    id                   = Column(String, primary_key=True)
    name                 = Column(String(100), nullable=False, unique=True)
    description          = Column(Text)
    training_examples    = Column(JSON, nullable=False, default=list)
    confidence_threshold = Column(Numeric(3, 2), nullable=False, default=0.75)
    is_active            = Column(Boolean, nullable=False, default=True)
    created_at           = Column(DateTime, nullable=False, server_default=func.now())
    updated_at           = Column(DateTime, nullable=False, server_default=func.now())

    message_intents = relationship("MessageIntent", back_populates="intent")


class Conversation(Base):
    __tablename__ = "conversations"

    id                = Column(String, primary_key=True)
    session_id        = Column(String, ForeignKey("sessions.id"), nullable=False)
    user_id           = Column(String, ForeignKey("users.id"))
    channel           = Column(String(20), nullable=False)
    status            = Column(String(20), nullable=False, default="active")
    assigned_agent_id = Column(String, ForeignKey("users.id"))
    resolved_by       = Column(String(10))
    started_at        = Column(DateTime, nullable=False, server_default=func.now())
    closed_at         = Column(DateTime)
    created_at        = Column(DateTime, nullable=False, server_default=func.now())
    updated_at        = Column(DateTime, nullable=False, server_default=func.now())

    session        = relationship("Session", back_populates="conversations")
    user           = relationship("User", foreign_keys=[user_id], back_populates="conversations")
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id], back_populates="assigned_conversations")
    messages       = relationship("Message", back_populates="conversation")
    escalations    = relationship("Escalation", back_populates="conversation")
    ticket         = relationship("Ticket", back_populates="conversation", uselist=False)


class Message(Base):
    __tablename__ = "messages"

    id              = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    sender_type     = Column(String(10), nullable=False)
    sender_id       = Column(String, ForeignKey("users.id"))
    content         = Column(Text, nullable=False)
    extra_data      = Column(JSON, nullable=False, default=dict)
    created_at      = Column(DateTime, nullable=False, server_default=func.now())

    conversation    = relationship("Conversation", back_populates="messages")
    sender          = relationship("User", back_populates="messages")
    message_intents = relationship("MessageIntent", back_populates="message")


class MessageIntent(Base):
    __tablename__ = "message_intents"

    id                = Column(String, primary_key=True)
    message_id        = Column(String, ForeignKey("messages.id"), nullable=False)
    intent_id         = Column(String, ForeignKey("intents.id"), nullable=False)
    confidence        = Column(Numeric(5, 4), nullable=False)
    detected_entities = Column(JSON, nullable=False, default=dict)
    created_at        = Column(DateTime, nullable=False, server_default=func.now())

    message = relationship("Message", back_populates="message_intents")
    intent  = relationship("Intent", back_populates="message_intents")


class Escalation(Base):
    __tablename__ = "escalations"

    id               = Column(String, primary_key=True)
    conversation_id  = Column(String, ForeignKey("conversations.id"), nullable=False)
    reason           = Column(String(50), nullable=False)
    confidence_score = Column(Numeric(5, 4))
    agent_id         = Column(String, ForeignKey("users.id"))
    escalated_at     = Column(DateTime, nullable=False, server_default=func.now())
    attended_at      = Column(DateTime)
    resolved_at      = Column(DateTime)

    conversation = relationship("Conversation", back_populates="escalations")
    agent        = relationship("User", back_populates="escalations")
