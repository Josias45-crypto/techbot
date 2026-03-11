# ==================================================
# backend/app/api/v1/endpoints/knowledge.py
# Endpoints para base de conocimiento:
# FAQs, problemas conocidos y drivers.
# Lectura publica, escritura solo admin.
# ==================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.knowledge import FAQ, KnownIssue, Driver
from backend.app.schemas.knowledge import (
    FAQCreate, FAQUpdate, FAQResponse,
    KnownIssueCreate, KnownIssueUpdate, KnownIssueResponse,
    DriverCreate, DriverUpdate, DriverResponse
)

router = APIRouter(prefix="/knowledge", tags=["Base de Conocimiento"])


# ==================================================
# FAQS
# ==================================================

@router.get("/faqs", response_model=List[FAQResponse])
def list_faqs(
    category: Optional[str] = Query(None),  # Filtra por categoria
    search: Optional[str] = Query(None),    # Busca en pregunta y respuesta
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Lista FAQs activas con filtros opcionales
    # Acceso publico — no requiere autenticacion
    query = db.query(FAQ).filter(FAQ.is_active == True)

    if category:
        query = query.filter(FAQ.category == category)
    if search:
        # Busqueda en pregunta y respuesta
        query = query.filter(
            FAQ.question.ilike(f"%{search}%") |
            FAQ.answer.ilike(f"%{search}%")
        )

    return query.offset(skip).limit(limit).all()


@router.get("/faqs/{faq_id}", response_model=FAQResponse)
def get_faq(faq_id: str, db: Session = Depends(get_db)):
    # Retorna una FAQ por ID e incrementa su contador de uso
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(404, detail="FAQ no encontrada")

    # Incrementa contador de veces usada para analytics
    faq.times_used += 1
    db.commit()
    return faq


@router.post("/faqs", response_model=FAQResponse, status_code=201)
def create_faq(
    data: FAQCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Crea una nueva FAQ — solo admin
    faq = FAQ(id=str(uuid.uuid4()), **data.model_dump())
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


@router.put("/faqs/{faq_id}", response_model=FAQResponse)
def update_faq(
    faq_id: str,
    data: FAQUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Actualiza una FAQ — solo admin
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(404, detail="FAQ no encontrada")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(faq, field, value)

    db.commit()
    db.refresh(faq)
    return faq


@router.delete("/faqs/{faq_id}", status_code=204)
def delete_faq(
    faq_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Elimina logicamente la FAQ — solo admin
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(404, detail="FAQ no encontrada")

    faq.is_active = False
    db.commit()


# ==================================================
# PROBLEMAS CONOCIDOS (KNOWN ISSUES)
# ==================================================

@router.get("/issues", response_model=List[KnownIssueResponse])
def list_issues(
    product_id: Optional[str] = Query(None),   # Filtra por producto
    category: Optional[str] = Query(None),     # Filtra por categoria
    difficulty: Optional[str] = Query(None),   # easy, medium, hard
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Lista problemas conocidos con filtros
    # Acceso publico para que el chatbot y clientes consulten
    query = db.query(KnownIssue).filter(KnownIssue.is_active == True)

    if product_id:
        query = query.filter(KnownIssue.product_id == product_id)
    if category:
        query = query.filter(KnownIssue.category == category)
    if difficulty:
        query = query.filter(KnownIssue.difficulty == difficulty)
    if search:
        query = query.filter(
            KnownIssue.title.ilike(f"%{search}%") |
            KnownIssue.description.ilike(f"%{search}%") |
            KnownIssue.error_code.ilike(f"%{search}%")
        )

    return query.offset(skip).limit(limit).all()


@router.get("/issues/{issue_id}", response_model=KnownIssueResponse)
def get_issue(issue_id: str, db: Session = Depends(get_db)):
    # Retorna un problema conocido con sus pasos de solucion
    issue = db.query(KnownIssue).filter(KnownIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(404, detail="Problema no encontrado")
    return issue


@router.post("/issues", response_model=KnownIssueResponse, status_code=201)
def create_issue(
    data: KnownIssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Crea un nuevo problema conocido con pasos de solucion
    issue = KnownIssue(id=str(uuid.uuid4()), **data.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.put("/issues/{issue_id}", response_model=KnownIssueResponse)
def update_issue(
    issue_id: str,
    data: KnownIssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Actualiza un problema conocido — solo admin
    issue = db.query(KnownIssue).filter(KnownIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(404, detail="Problema no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)
    return issue


# ==================================================
# DRIVERS
# ==================================================

@router.get("/drivers", response_model=List[DriverResponse])
def list_drivers(
    product_id: Optional[str] = Query(None),        # Filtra por producto
    operating_system: Optional[str] = Query(None),  # windows, linux, mac
    architecture: Optional[str] = Query(None),      # x64, x86, arm
    db: Session = Depends(get_db)
):
    # Lista drivers disponibles con filtros
    # Acceso publico para descarga de drivers
    query = db.query(Driver).filter(Driver.is_active == True)

    if product_id:
        query = query.filter(Driver.product_id == product_id)
    if operating_system:
        query = query.filter(Driver.operating_system == operating_system)
    if architecture:
        query = query.filter(Driver.architecture == architecture)

    return query.all()


@router.post("/drivers", response_model=DriverResponse, status_code=201)
def create_driver(
    data: DriverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Agrega un nuevo driver al sistema — solo admin
    driver = Driver(id=str(uuid.uuid4()), **data.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.put("/drivers/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: str,
    data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Actualiza informacion del driver — solo admin
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(404, detail="Driver no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)

    db.commit()
    db.refresh(driver)
    return driver
