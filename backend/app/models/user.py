from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id            = Column(String, primary_key=True)
    name          = Column(String(50), nullable=False, unique=True)
    description   = Column(Text)
    permissions   = Column(JSON, nullable=False, default=list)
    is_active     = Column(Boolean, nullable=False, default=True)
    created_at    = Column(DateTime, nullable=False, server_default=func.now())
    updated_at    = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id            = Column(String, primary_key=True)
    role_id       = Column(String, ForeignKey("roles.id"), nullable=False)
    full_name     = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True)
    phone         = Column(String(20))
    password_hash = Column(String(255))
    is_active     = Column(Boolean, nullable=False, default=True)
    last_login    = Column(DateTime)
    created_at    = Column(DateTime, nullable=False, server_default=func.now())
    updated_at    = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    role          = relationship("Role", back_populates="users")
    sessions      = relationship("Session", back_populates="user")
    conversations = relationship("Conversation", foreign_keys="Conversation.user_id", back_populates="user")
    assigned_conversations = relationship("Conversation", foreign_keys="Conversation.assigned_agent_id", back_populates="assigned_agent")
    messages      = relationship("Message", back_populates="sender")
    escalations   = relationship("Escalation", back_populates="agent")
    tickets       = relationship("Ticket", back_populates="user")
    orders        = relationship("Order", back_populates="user")
    repairs_as_client     = relationship("Repair", foreign_keys="Repair.user_id", back_populates="client")
    repairs_as_technician = relationship("Repair", foreign_keys="Repair.technician_id", back_populates="technician")


class Session(Base):
    __tablename__ = "sessions"

    id         = Column(String, primary_key=True)
    user_id    = Column(String, ForeignKey("users.id"))
    token      = Column(String(500), nullable=False, unique=True)
    channel    = Column(String(20), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active  = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    user          = relationship("User", back_populates="sessions")
    conversations = relationship("Conversation", back_populates="session")
