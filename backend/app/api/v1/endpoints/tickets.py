# ==================================================
# backend/app/api/v1/endpoints/tickets.py
# Endpoints para gestion de tickets de soporte.
# Clientes ven sus propios tickets.
# Agentes y admin ven todos los tickets.
# ==================================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.tickets import Ticket, TicketHistory
from backend.app.schemas.tickets import (
    TicketCreate, TicketUpdate, TicketResponse,
    TicketWithHistory, TicketHistoryResponse
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# ==================================================
# LISTAR TICKETS
# ==================================================

@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status_filter: Optional[str] = Query(None),     # Filtra por estado: open, closed
    priority: Optional[str] = Query(None),           # Filtra por prioridad
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista tickets segun el rol del usuario:
    - client: solo ve sus propios tickets
    - agent/admin: ve todos los tickets
    """
    query = db.query(Ticket)

    # Los clientes solo ven sus propios tickets
    if current_user.role.name == "client":
        query = query.filter(Ticket.user_id == current_user.id)

    # Filtros opcionales
    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    if priority:
        query = query.filter(Ticket.priority == priority)

    # Ordena por fecha de creacion descendente (mas reciente primero)
    return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()


# ==================================================
# OBTENER TICKET POR ID
# ==================================================

@router.get("/{ticket_id}", response_model=TicketWithHistory)
def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna un ticket con todo su historial de cambios.
    Los clientes solo pueden ver sus propios tickets.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, detail="Ticket no encontrado")

    # Verifica que el cliente solo acceda a sus tickets
    if current_user.role.name == "client" and ticket.user_id != current_user.id:
        raise HTTPException(403, detail="Acceso denegado")

    return ticket


# ==================================================
# CREAR TICKET
# ==================================================

@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo ticket de soporte.
    Genera automaticamente el codigo de referencia.
    Registra el primer estado en el historial.
    """
    # Genera codigo de referencia unico: TKT-20240001
    count = db.query(Ticket).count() + 1
    reference_code = f"TKT-{datetime.utcnow().year}{count:04d}"

    ticket = Ticket(
        id=str(uuid.uuid4()),
        conversation_id=data.conversation_id,
        user_id=current_user.id,
        reference_code=reference_code,
        category=data.category,
        priority=data.priority,
        status="open",
        channel_origin=data.channel_origin,
        notes=data.notes
    )
    db.add(ticket)

    # Registra el estado inicial en el historial
    history = TicketHistory(
        id=str(uuid.uuid4()),
        ticket_id=ticket.id,
        previous_status=None,
        new_status="open",
        changed_by_id=current_user.id,
        note="Ticket creado"
    )
    db.add(history)
    db.commit()
    db.refresh(ticket)
    return ticket


# ==================================================
# ACTUALIZAR TICKET
# ==================================================

@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    data: TicketUpdate,
    current_user: User = Depends(require_role("admin", "agent")),
    db: Session = Depends(get_db)
):
    """
    Actualiza estado y datos del ticket.
    Solo agentes y admin pueden actualizar tickets.
    Registra automaticamente el cambio en el historial.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, detail="Ticket no encontrado")

    previous_status = ticket.status

    # Actualiza solo los campos enviados
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)

    # Si cambia a closed registra la fecha de cierre
    if data.status == "closed":
        ticket.closed_at = datetime.utcnow()

    # Registra el cambio en el historial si cambio el estado
    if data.status and data.status != previous_status:
        history = TicketHistory(
            id=str(uuid.uuid4()),
            ticket_id=ticket.id,
            previous_status=previous_status,
            new_status=data.status,
            changed_by_id=current_user.id,
            note=data.notes
        )
        db.add(history)

    db.commit()
    db.refresh(ticket)
    return ticket


# ==================================================
# BUSCAR TICKET POR CODIGO DE REFERENCIA
# ==================================================

@router.get("/track/{reference_code}", response_model=TicketWithHistory)
def track_ticket(
    reference_code: str,
    db: Session = Depends(get_db)
):
    """
    Permite seguimiento publico de un ticket
    usando solo el codigo de referencia.
    No requiere autenticacion.
    """
    ticket = db.query(Ticket).filter(
        Ticket.reference_code == reference_code
    ).first()
    if not ticket:
        raise HTTPException(404, detail="Ticket no encontrado")
    return ticket
