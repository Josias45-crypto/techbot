from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id               = Column(String, primary_key=True)
    product_id       = Column(String, ForeignKey("products.id"), nullable=False)
    name             = Column(String(200), nullable=False)
    version          = Column(String(50), nullable=False)
    operating_system = Column(String(50), nullable=False)
    architecture     = Column(String(10), nullable=False)
    download_url     = Column(Text, nullable=False)
    release_date     = Column(Date)
    is_active        = Column(Boolean, nullable=False, default=True)
    created_at       = Column(DateTime, nullable=False, server_default=func.now())
    updated_at       = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    product = relationship("Product", back_populates="drivers")


class KnownIssue(Base):
    __tablename__ = "known_issues"

    id             = Column(String, primary_key=True)
    product_id     = Column(String, ForeignKey("products.id"))
    title          = Column(String(200), nullable=False)
    error_code     = Column(String(100))
    description    = Column(Text, nullable=False)
    solution_steps = Column(JSON, nullable=False, default=list)
    category       = Column(String(50), nullable=False)
    difficulty     = Column(String(20), nullable=False)
    is_active      = Column(Boolean, nullable=False, default=True)
    created_at     = Column(DateTime, nullable=False, server_default=func.now())
    updated_at     = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    product = relationship("Product", back_populates="known_issues")


class FAQ(Base):
    __tablename__ = "faqs"

    id         = Column(String, primary_key=True)
    question   = Column(Text, nullable=False)
    answer     = Column(Text, nullable=False)
    category   = Column(String(50))
    times_used = Column(Integer, nullable=False, default=0)
    is_active  = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())


class KnowledgeEmbedding(Base):
    __tablename__ = "knowledge_embeddings"

    id           = Column(String, primary_key=True)
    source_type  = Column(String(50), nullable=False)
    source_id    = Column(String, nullable=False)
    content_text = Column(Text, nullable=False)
    embedding    = Column(Text)
    created_at   = Column(DateTime, nullable=False, server_default=func.now())
    updated_at   = Column(DateTime, nullable=False, server_default=func.now())
