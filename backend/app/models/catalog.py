from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Numeric, Integer, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id          = Column(String, primary_key=True)
    parent_id   = Column(String, ForeignKey("categories.id"))
    name        = Column(String(100), nullable=False)
    description = Column(Text)
    is_active   = Column(Boolean, nullable=False, default=True)
    created_at  = Column(DateTime, nullable=False, server_default=func.now())
    updated_at  = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    parent     = relationship("Category", remote_side="Category.id", back_populates="children")
    children   = relationship("Category", back_populates="parent")
    products   = relationship("Product", back_populates="category")


class Brand(Base):
    __tablename__ = "brands"

    id         = Column(String, primary_key=True)
    name       = Column(String(100), nullable=False, unique=True)
    country    = Column(String(60))
    is_active  = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    products = relationship("Product", back_populates="brand")


class Product(Base):
    __tablename__ = "products"

    id          = Column(String, primary_key=True)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    brand_id    = Column(String, ForeignKey("brands.id"), nullable=False)
    sku         = Column(String(100), nullable=False, unique=True)
    name        = Column(String(200), nullable=False)
    model       = Column(String(100))
    description = Column(Text)
    price       = Column(Numeric(10, 2), nullable=False, default=0.00)
    is_active   = Column(Boolean, nullable=False, default=True)
    created_at  = Column(DateTime, nullable=False, server_default=func.now())
    updated_at  = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    category        = relationship("Category", back_populates="products")
    brand           = relationship("Brand", back_populates="products")
    specs           = relationship("ProductSpec", back_populates="product")
    inventory       = relationship("Inventory", back_populates="product", uselist=False)
    drivers         = relationship("Driver", back_populates="product")
    known_issues    = relationship("KnownIssue", back_populates="product")
    order_items     = relationship("OrderItem", back_populates="product")
    waitlist        = relationship("Waitlist", back_populates="product")
    compatible_with = relationship("Compatibility", foreign_keys="Compatibility.product_id_a", back_populates="product_a")


class ProductSpec(Base):
    __tablename__ = "product_specs"

    id         = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    spec_key   = Column(String(100), nullable=False)
    spec_value = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    product = relationship("Product", back_populates="specs")


class Inventory(Base):
    __tablename__ = "inventory"

    id           = Column(String, primary_key=True)
    product_id   = Column(String, ForeignKey("products.id"), nullable=False, unique=True)
    stock        = Column(Integer, nullable=False, default=0)
    min_stock    = Column(Integer, nullable=False, default=5)
    location     = Column(String(100))
    restock_date = Column(Date)
    updated_at   = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    product = relationship("Product", back_populates="inventory")


class Compatibility(Base):
    __tablename__ = "compatibility"

    id            = Column(String, primary_key=True)
    product_id_a  = Column(String, ForeignKey("products.id"), nullable=False)
    product_id_b  = Column(String, ForeignKey("products.id"), nullable=False)
    is_compatible = Column(Boolean, nullable=False, default=True)
    notes         = Column(Text)
    created_at    = Column(DateTime, nullable=False, server_default=func.now())

    # Relaciones
    product_a = relationship("Product", foreign_keys=[product_id_a], back_populates="compatible_with")
    product_b = relationship("Product", foreign_keys=[product_id_b])
