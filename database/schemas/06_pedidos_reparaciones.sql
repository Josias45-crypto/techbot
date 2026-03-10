-- ============================================================
-- TECHBOT — Módulo 6: Pedidos y reparaciones
-- ============================================================
CREATE TABLE orders (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id        UUID        REFERENCES users(id) ON DELETE SET NULL,
    reference_code VARCHAR(20) NOT NULL UNIQUE,
    status         VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
    total          DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    channel_origin VARCHAR(20) NOT NULL CHECK (channel_origin IN ('web', 'whatsapp', 'phone', 'in_person')),
    notes          TEXT,
    created_at     TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_orders_updated_at
    BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE order_items (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id   UUID          NOT NULL REFERENCES orders(id)   ON DELETE CASCADE,
    product_id UUID          NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity   INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP     NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);

CREATE TABLE repairs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID        REFERENCES users(id) ON DELETE SET NULL,
    technician_id       UUID        REFERENCES users(id) ON DELETE SET NULL,
    reference_code      VARCHAR(20) NOT NULL UNIQUE,
    type                VARCHAR(10) NOT NULL CHECK (type IN ('physical', 'remote')),
    device_description  TEXT        NOT NULL,
    problem_description TEXT        NOT NULL,
    diagnosis           TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'received' CHECK (status IN ('received', 'diagnosing', 'waiting_part', 'repairing', 'ready', 'delivered')),
    estimated_cost      DECIMAL(10,2),
    final_cost          DECIMAL(10,2),
    estimated_delivery  DATE,
    actual_delivery     DATE,
    created_at          TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_repairs_status ON repairs(status);
CREATE TRIGGER trg_repairs_updated_at
    BEFORE UPDATE ON repairs FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE repair_history (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repair_id       UUID        NOT NULL REFERENCES repairs(id) ON DELETE CASCADE,
    previous_status VARCHAR(20),
    new_status      VARCHAR(20) NOT NULL,
    technical_note  TEXT,
    changed_by_id   UUID        REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_repair_history_repair_id ON repair_history(repair_id);
