-- ============================================================
-- TECHBOT — Módulo 7: Métricas y auditoría
-- ============================================================
CREATE TABLE audit_logs (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID         REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50)  NOT NULL,
    entity_id   UUID,
    detail      JSONB        NOT NULL DEFAULT '{}',
    ip_address  VARCHAR(45),
    channel     VARCHAR(20),
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_logs_action      ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX idx_audit_logs_created_at  ON audit_logs(created_at);

CREATE TABLE metrics_daily (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date                    DATE         NOT NULL UNIQUE,
    total_conversations     INTEGER      NOT NULL DEFAULT 0,
    resolved_by_bot         INTEGER      NOT NULL DEFAULT 0,
    resolved_by_agent       INTEGER      NOT NULL DEFAULT 0,
    escalated               INTEGER      NOT NULL DEFAULT 0,
    avg_response_time_sec   DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    avg_resolution_time_min DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    top_intent              VARCHAR(100),
    by_channel              JSONB        NOT NULL DEFAULT '{}',
    by_category             JSONB        NOT NULL DEFAULT '{}',
    created_at              TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE waitlist (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID        NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id    UUID        REFERENCES users(id) ON DELETE SET NULL,
    email      VARCHAR(150),
    phone      VARCHAR(20),
    notified   BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_waitlist_product_id ON waitlist(product_id);
