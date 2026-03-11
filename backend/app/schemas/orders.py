from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# --------------------------------------------------
# ESQUEMAS DE ITEMS DE PEDIDO
# Cada producto dentro de un pedido
# --------------------------------------------------

class OrderItemBase(BaseModel):
    product_id: str         # Producto solicitado
    quantity: int           # Cantidad pedida
    unit_price: Decimal     # Precio al momento de la compra

class OrderItemCreate(OrderItemBase):
    order_id: str           # Pedido al que pertenece

class OrderItemResponse(OrderItemBase):
    id: str
    order_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# --------------------------------------------------
# ESQUEMAS DE PEDIDOS (ORDERS)
# --------------------------------------------------

class OrderBase(BaseModel):
    channel_origin: str             # web, whatsapp, phone, in_person
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    user_id: Optional[str] = None  # Nullable: puede ser anonimo
    items: List[OrderItemBase]     # Productos del pedido

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class OrderResponse(OrderBase):
    id: str
    user_id: Optional[str] = None
    reference_code: str            # ORD-2024-00001
    status: str
    total: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderWithItems(OrderResponse):
    items: List[OrderItemResponse] = []


# --------------------------------------------------
# ESQUEMAS DE REPARACIONES (REPAIRS)
# --------------------------------------------------

class RepairBase(BaseModel):
    type: str                       # physical o remote
    device_description: str         # Descripcion del equipo
    problem_description: str        # Lo que reporta el cliente

class RepairCreate(RepairBase):
    user_id: Optional[str] = None

class RepairUpdate(BaseModel):
    technician_id: Optional[str] = None
    diagnosis: Optional[str] = None
    status: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    final_cost: Optional[Decimal] = None
    estimated_delivery: Optional[date] = None
    actual_delivery: Optional[date] = None

class RepairResponse(RepairBase):
    id: str
    user_id: Optional[str] = None
    technician_id: Optional[str] = None
    reference_code: str             # REP-2024-00001
    diagnosis: Optional[str] = None
    status: str
    estimated_cost: Optional[Decimal] = None
    final_cost: Optional[Decimal] = None
    estimated_delivery: Optional[date] = None
    actual_delivery: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --------------------------------------------------
# ESQUEMAS DE HISTORIAL DE REPARACION
# --------------------------------------------------

class RepairHistoryCreate(BaseModel):
    repair_id: str
    previous_status: Optional[str] = None
    new_status: str
    technical_note: Optional[str] = None
    changed_by_id: Optional[str] = None

class RepairHistoryResponse(BaseModel):
    id: str
    repair_id: str
    previous_status: Optional[str] = None
    new_status: str
    technical_note: Optional[str] = None
    changed_by_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RepairWithHistory(RepairResponse):
    history: List[RepairHistoryResponse] = []


# --------------------------------------------------
# ESQUEMA DE LISTA DE ESPERA (WAITLIST)
# --------------------------------------------------

class WaitlistCreate(BaseModel):
    product_id: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class WaitlistResponse(BaseModel):
    id: str
    product_id: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notified: bool
    created_at: datetime

    class Config:
        from_attributes = True
