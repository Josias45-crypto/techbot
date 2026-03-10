-- ============================================================
-- TECHBOT — Módulo 2: Catálogo de productos e inventario
-- ============================================================
CREATE TABLE categories (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id   UUID REFERENCES categories(id) ON DELETE SET NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE TRIGGER trg_categories_updated_at
    BEFORE UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE brands (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name       VARCHAR(100) NOT NULL UNIQUE,
    country    VARCHAR(60),
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_brands_updated_at
    BEFORE UPDATE ON brands FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE products (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID          NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    brand_id    UUID          NOT NULL REFERENCES brands(id)     ON DELETE RESTRICT,
    sku         VARCHAR(100)  NOT NULL UNIQUE,
    name        VARCHAR(200)  NOT NULL,
    model       VARCHAR(100),
    description TEXT,
    price       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    is_active   BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP     NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_brand_id    ON products(brand_id);
CREATE INDEX idx_products_sku         ON products(sku);
CREATE INDEX idx_products_is_active   ON products(is_active);
CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE product_specs (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID         NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    spec_key   VARCHAR(100) NOT NULL,
    spec_value VARCHAR(255) NOT NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_product_specs_product_id ON product_specs(product_id);

CREATE TABLE inventory (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id   UUID    NOT NULL UNIQUE REFERENCES products(id) ON DELETE CASCADE,
    stock        INTEGER NOT NULL DEFAULT 0,
    min_stock    INTEGER NOT NULL DEFAULT 5,
    location     VARCHAR(100),
    restock_date DATE,
    updated_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE compatibility (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id_a  UUID    NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    product_id_b  UUID    NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    is_compatible BOOLEAN NOT NULL DEFAULT TRUE,
    notes         TEXT,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(product_id_a, product_id_b),
    CHECK (product_id_a <> product_id_b)
);
