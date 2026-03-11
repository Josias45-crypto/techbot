from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# -- CATEGORY --------------------------------------
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -- BRAND -----------------------------------------
class BrandBase(BaseModel):
    name: str
    country: Optional[str] = None

class BrandCreate(BrandBase):
    pass

class BrandResponse(BrandBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -- PRODUCT SPEC ----------------------------------
class ProductSpecBase(BaseModel):
    spec_key: str
    spec_value: str

class ProductSpecCreate(ProductSpecBase):
    product_id: str

class ProductSpecResponse(ProductSpecBase):
    id: str
    product_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# -- PRODUCT ---------------------------------------
class ProductBase(BaseModel):
    name: str
    model: Optional[str] = None
    description: Optional[str] = None
    price: Decimal
    sku: str

class ProductCreate(ProductBase):
    category_id: str
    brand_id: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: str
    category_id: str
    brand_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ProductDetail(ProductResponse):
    category: CategoryResponse
    brand: BrandResponse
    specs: List[ProductSpecResponse] = []


# -- INVENTORY -------------------------------------
class InventoryBase(BaseModel):
    stock: int
    min_stock: int = 5
    location: Optional[str] = None

class InventoryUpdate(BaseModel):
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    location: Optional[str] = None

class InventoryResponse(InventoryBase):
    id: str
    product_id: str
    updated_at: datetime

    class Config:
        from_attributes = True


# -- COMPATIBILITY ---------------------------------
class CompatibilityBase(BaseModel):
    product_id_a: str
    product_id_b: str
    is_compatible: bool
    notes: Optional[str] = None

class CompatibilityCreate(CompatibilityBase):
    pass

class CompatibilityResponse(CompatibilityBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
