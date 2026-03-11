# ==================================================
# backend/app/api/v1/endpoints/orders.py
# Endpoints para pedidos y reparaciones.
# Clientes ven sus propios registros.
# Tecnicos y admin gestionan reparaciones.
# Admin gestiona pedidos.
# ==================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.orders import Order, OrderItem, Repair, RepairHistory, Waitlist
from backend.app.models.catalog import Inventory
from backend.app.schemas.orders import (
    OrderCreate, OrderUpdate, OrderResponse, OrderWithItems,
    RepairCreate, RepairUpdate, RepairResponse, RepairWithHistory,
    RepairHistoryCreate, RepairHistoryResponse,
    WaitlistCreate, WaitlistResponse
)

router = APIRouter(prefix="/orders", tags=["Pedidos y Reparaciones"])


# ==================================================
# PEDIDOS (ORDERS)
# ==================================================

@router.get("", response_model=List[OrderResponse])
def list_orders(
    status_filter: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista pedidos segun rol:
    - client: solo sus pedidos
    - admin: todos los pedidos
    """
    query = db.query(Order)

    if current_user.role.name == "client":
        query = query.filter(Order.user_id == current_user.id)
    if status_filter:
        query = query.filter(Order.status == status_filter)

    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{order_id}", response_model=OrderWithItems)
def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Retorna pedido completo con todos sus items
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, detail="Pedido no encontrado")

    # Cliente solo puede ver sus propios pedidos
    if current_user.role.name == "client" and order.user_id != current_user.id:
        raise HTTPException(403, detail="Acceso denegado")

    return order


@router.get("/track/{reference_code}", response_model=OrderWithItems)
def track_order(reference_code: str, db: Session = Depends(get_db)):
    """
    Seguimiento publico de pedido por codigo.
    No requiere autenticacion.
    """
    order = db.query(Order).filter(Order.reference_code == reference_code).first()
    if not order:
        raise HTTPException(404, detail="Pedido no encontrado")
    return order


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo pedido con sus items.
    Verifica stock disponible antes de confirmar.
    Descuenta automaticamente del inventario.
    """
    # Genera codigo de referencia unico
    count = db.query(Order).count() + 1
    reference_code = f"ORD-{datetime.utcnow().year}{count:04d}"

    total = 0
    items_to_create = []

    # Valida stock y calcula total
    for item_data in data.items:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item_data.product_id
        ).first()

        if not inventory or inventory.stock < item_data.quantity:
            raise HTTPException(
                400,
                detail=f"Stock insuficiente para producto {item_data.product_id}"
            )

        total += float(item_data.unit_price) * item_data.quantity
        items_to_create.append(item_data)

    # Crea el pedido
    order = Order(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        reference_code=reference_code,
        status="pending",
        total=total,
        channel_origin=data.channel_origin,
        notes=data.notes
    )
    db.add(order)

    # Crea los items y descuenta inventario
    for item_data in items_to_create:
        item = OrderItem(
            id=str(uuid.uuid4()),
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price
        )
        db.add(item)

        # Descuenta del inventario
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item_data.product_id
        ).first()
        inventory.stock -= item_data.quantity

    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: str,
    data: OrderUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    # Actualiza estado del pedido — solo admin
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, detail="Pedido no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return order


# ==================================================
# REPARACIONES (REPAIRS)
# ==================================================

@router.get("/repairs", response_model=List[RepairResponse])
def list_repairs(
    status_filter: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista reparaciones segun rol:
    - client: solo sus reparaciones
    - technician: reparaciones asignadas
    - admin: todas las reparaciones
    """
    query = db.query(Repair)

    if current_user.role.name == "client":
        query = query.filter(Repair.user_id == current_user.id)
    elif current_user.role.name == "technician":
        query = query.filter(Repair.technician_id == current_user.id)

    if status_filter:
        query = query.filter(Repair.status == status_filter)

    return query.order_by(Repair.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/repairs/{repair_id}", response_model=RepairWithHistory)
def get_repair(
    repair_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Retorna reparacion completa con historial de estados
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(404, detail="Reparacion no encontrada")

    if current_user.role.name == "client" and repair.user_id != current_user.id:
        raise HTTPException(403, detail="Acceso denegado")

    return repair


@router.get("/repairs/track/{reference_code}", response_model=RepairWithHistory)
def track_repair(reference_code: str, db: Session = Depends(get_db)):
    """
    Seguimiento publico de reparacion por codigo.
    No requiere autenticacion.
    """
    repair = db.query(Repair).filter(
        Repair.reference_code == reference_code
    ).first()
    if not repair:
        raise HTTPException(404, detail="Reparacion no encontrada")
    return repair


@router.post("/repairs", response_model=RepairResponse, status_code=201)
def create_repair(
    data: RepairCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registra una nueva reparacion.
    Genera codigo de referencia automaticamente.
    Estado inicial: received.
    """
    count = db.query(Repair).count() + 1
    reference_code = f"REP-{datetime.utcnow().year}{count:04d}"

    repair = Repair(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        reference_code=reference_code,
        type=data.type,
        device_description=data.device_description,
        problem_description=data.problem_description,
        status="received"
    )
    db.add(repair)

    # Registra estado inicial en historial
    history = RepairHistory(
        id=str(uuid.uuid4()),
        repair_id=repair.id,
        previous_status=None,
        new_status="received",
        changed_by_id=current_user.id,
        technical_note="Reparacion registrada"
    )
    db.add(history)
    db.commit()
    db.refresh(repair)
    return repair


@router.put("/repairs/{repair_id}", response_model=RepairResponse)
def update_repair(
    repair_id: str,
    data: RepairUpdate,
    current_user: User = Depends(require_role("admin", "technician")),
    db: Session = Depends(get_db)
):
    """
    Actualiza estado y datos de la reparacion.
    Registra automaticamente el cambio en historial.
    """
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(404, detail="Reparacion no encontrada")

    previous_status = repair.status

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(repair, field, value)

    # Registra en historial si cambio el estado
    if data.status and data.status != previous_status:
        history = RepairHistory(
            id=str(uuid.uuid4()),
            repair_id=repair.id,
            previous_status=previous_status,
            new_status=data.status,
            changed_by_id=current_user.id,
            technical_note=f"Estado actualizado a {data.status}"
        )
        db.add(history)

    db.commit()
    db.refresh(repair)
    return repair


# ==================================================
# LISTA DE ESPERA (WAITLIST)
# ==================================================

@router.post("/waitlist", response_model=WaitlistResponse, status_code=201)
def join_waitlist(
    data: WaitlistCreate,
    db: Session = Depends(get_db)
):
    """
    Agrega un cliente a la lista de espera
    para un producto sin stock.
    No requiere autenticacion.
    """
    entry = Waitlist(
        id=str(uuid.uuid4()),
        product_id=data.product_id,
        user_id=data.user_id,
        email=data.email,
        phone=data.phone,
        notified=False
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
