from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Numeric, Integer, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id             = Column(String, primary_key=True)
    user_id        = Column(String, ForeignKey("users.id"))
    reference_code = Column(String(20), nullable=False, unique=True)
    status         = Column(String(20), nullable=False, default="pending")
    total          = Column(Numeric(10, 2), nullable=False, default=0.00)
    channel_origin = Column(String(20), nullable=False)
    notes          = Column(Text)
    created_at     = Column(DateTime, nullable=False, server_default=func.now())
    updated_at     = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    user  = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(String, primary_key=True)
    order_id   = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity   = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    order   = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Repair(Base):
    __tablename__ = "repairs"

    id                  = Column(String, primary_key=True)
    user_id             = Column(String, ForeignKey("users.id"))
    technician_id       = Column(String, ForeignKey("users.id"))
    reference_code      = Column(String(20), nullable=False, unique=True)
    type                = Column(String(10), nullable=False)
    device_description  = Column(Text, nullable=False)
    problem_description = Column(Text, nullable=False)
    diagnosis           = Column(Text)
    status              = Column(String(20), nullable=False, default="received")
    estimated_cost      = Column(Numeric(10, 2))
    final_cost          = Column(Numeric(10, 2))
    estimated_delivery  = Column(Date)
    actual_delivery     = Column(Date)
    created_at          = Column(DateTime, nullable=False, server_default=func.now())
    updated_at          = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    client     = relationship("User", foreign_keys=[user_id], back_populates="repairs_as_client")
    technician = relationship("User", foreign_keys=[technician_id], back_populates="repairs_as_technician")
    history    = relationship("RepairHistory", back_populates="repair")


class RepairHistory(Base):
    __tablename__ = "repair_history"

    id              = Column(String, primary_key=True)
    repair_id       = Column(String, ForeignKey("repairs.id"), nullable=False)
    previous_status = Column(String(20))
    new_status      = Column(String(20), nullable=False)
    technical_note  = Column(Text)
    changed_by_id   = Column(String, ForeignKey("users.id"))
    created_at      = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    repair     = relationship("Repair", back_populates="history")
    changed_by = relationship("User")


class Waitlist(Base):
    __tablename__ = "waitlist"

    id         = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    user_id    = Column(String, ForeignKey("users.id"))
    email      = Column(String(150))
    phone      = Column(String(20))
    notified   = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    product = relationship("Product", back_populates="waitlist")
    user    = relationship("User")
