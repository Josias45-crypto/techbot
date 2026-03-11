# ==================================================
# backend/app/api/v1/endpoints/catalog.py
# Endpoints para gestion del catalogo de productos:
# categorias, marcas, productos e inventario.
# Solo admin puede crear/editar/eliminar.
# Cualquiera puede consultar productos activos.
# ==================================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.models.user import User
from backend.app.models.catalog import Category, Brand, Product, ProductSpec, Inventory
from backend.app.schemas.catalog import (
    CategoryCreate, CategoryResponse,
    BrandCreate, BrandResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductDetail,
    ProductSpecCreate, ProductSpecResponse,
    InventoryUpdate, InventoryResponse
)

router = APIRouter(prefix="/catalog", tags=["Catalogo"])


# ==================================================
# CATEGORIAS
# ==================================================

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    only_active: bool = True,
    db: Session = Depends(get_db)
):
    # Retorna todas las categorias
    # Si only_active=True solo retorna las activas
    query = db.query(Category)
    if only_active:
        query = query.filter(Category.is_active == True)
    return query.all()


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Crea una nueva categoria — solo admin
    # Verifica que no exista una categoria con el mismo nombre
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise HTTPException(400, detail="Ya existe una categoria con ese nombre")

    category = Category(id=str(uuid.uuid4()), **data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ==================================================
# MARCAS
# ==================================================

@router.get("/brands", response_model=List[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    # Retorna todas las marcas activas
    return db.query(Brand).filter(Brand.is_active == True).all()


@router.post("/brands", response_model=BrandResponse, status_code=201)
def create_brand(
    data: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Crea una nueva marca — solo admin
    existing = db.query(Brand).filter(Brand.name == data.name).first()
    if existing:
        raise HTTPException(400, detail="Ya existe una marca con ese nombre")

    brand = Brand(id=str(uuid.uuid4()), **data.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


# ==================================================
# PRODUCTOS
# ==================================================

@router.get("/products", response_model=List[ProductResponse])
def list_products(
    category_id: Optional[str] = Query(None),   # Filtra por categoria
    brand_id: Optional[str] = Query(None),       # Filtra por marca
    search: Optional[str] = Query(None),         # Busca por nombre o modelo
    only_active: bool = True,
    skip: int = 0,                               # Paginacion — desde
    limit: int = 20,                             # Paginacion — cantidad
    db: Session = Depends(get_db)
):
    # Lista productos con filtros opcionales y paginacion
    query = db.query(Product)

    if only_active:
        query = query.filter(Product.is_active == True)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if search:
        # Busqueda por nombre o modelo (insensible a mayusculas)
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.model.ilike(f"%{search}%")
        )

    return query.offset(skip).limit(limit).all()


@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str, db: Session = Depends(get_db)):
    # Retorna un producto con todos sus detalles:
    # categoria, marca y especificaciones tecnicas
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, detail="Producto no encontrado")
    return product


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Crea un nuevo producto — solo admin
    # Verifica que el SKU sea unico
    existing = db.query(Product).filter(Product.sku == data.sku).first()
    if existing:
        raise HTTPException(400, detail="Ya existe un producto con ese SKU")

    product = Product(id=str(uuid.uuid4()), **data.model_dump())
    db.add(product)

    # Crea el registro de inventario inicial con stock 0
    inventory = Inventory(
        id=str(uuid.uuid4()),
        product_id=product.id,
        stock=0,
        min_stock=5
    )
    db.add(inventory)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Actualiza campos del producto — solo admin
    # Solo actualiza los campos enviados (PATCH semantics)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, detail="Producto no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Elimina logicamente el producto (is_active=False)
    # No se borra fisicamente para conservar historial
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, detail="Producto no encontrado")

    product.is_active = False
    db.commit()


# ==================================================
# INVENTARIO
# ==================================================

@router.get("/products/{product_id}/inventory", response_model=InventoryResponse)
def get_inventory(product_id: str, db: Session = Depends(get_db)):
    # Retorna el stock actual de un producto
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()
    if not inventory:
        raise HTTPException(404, detail="Inventario no encontrado")
    return inventory


@router.put("/products/{product_id}/inventory", response_model=InventoryResponse)
def update_inventory(
    product_id: str,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Actualiza el stock de un producto — solo admin
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id
    ).first()
    if not inventory:
        raise HTTPException(404, detail="Inventario no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inventory, field, value)

    db.commit()
    db.refresh(inventory)
    return inventory


# ==================================================
# ESPECIFICACIONES TECNICAS
# ==================================================

@router.post("/products/{product_id}/specs", response_model=ProductSpecResponse, status_code=201)
def add_spec(
    product_id: str,
    data: ProductSpecCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    # Agrega una especificacion tecnica a un producto
    # Ejemplo: {"spec_key": "RAM", "spec_value": "16GB"}
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, detail="Producto no encontrado")

    spec = ProductSpec(
        id=str(uuid.uuid4()),
        product_id=product_id,
        spec_key=data.spec_key,
        spec_value=data.spec_value
    )
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return spec
