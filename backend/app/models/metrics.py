from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, Integer, Date, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id          = Column(String, primary_key=True)
    user_id     = Column(String, ForeignKey("users.id"))
    action      = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id   = Column(String)
    detail      = Column(JSON, nullable=False, default=dict)
    ip_address  = Column(String(45))
    channel     = Column(String(20))
    created_at  = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    user = relationship("User")


class MetricsDaily(Base):
    __tablename__ = "metrics_daily"

    id                      = Column(String, primary_key=True)
    date                    = Column(Date, nullable=False, unique=True)
    total_conversations     = Column(Integer, nullable=False, default=0)
    resolved_by_bot         = Column(Integer, nullable=False, default=0)
    resolved_by_agent       = Column(Integer, nullable=False, default=0)
    escalated               = Column(Integer, nullable=False, default=0)
    avg_response_time_sec   = Column(Numeric(6, 2), nullable=False, default=0.00)
    avg_resolution_time_min = Column(Numeric(8, 2), nullable=False, default=0.00)
    top_intent              = Column(String(100))
    by_channel              = Column(JSON, nullable=False, default=dict)
    by_category             = Column(JSON, nullable=False, default=dict)
    created_at              = Column(DateTime, nullable=False, server_default=func.now())
