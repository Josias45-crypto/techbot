-- ============================================================
-- TECHBOT — Módulo 5: Tickets y soporte
-- ============================================================
CREATE TABLE tickets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID        NOT NULL REFERENCES conversations(id) ON DELETE RESTRICT,
    user_id         UUID        REFERENCES users(id) ON DELETE SET NULL,
    reference_code  VARCHAR(20) NOT NULL UNIQUE,
    category        VARCHAR(50) NOT NULL CHECK (category IN ('compatibility', 'driver', 'error', 'order', 'repair', 'general')),
    priority        VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status          VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'escalated', 'closed')),
    resolved_by     VARCHAR(10) CHECK (resolved_by IN ('bot', 'agent')),
    channel_origin  VARCHAR(20) NOT NULL CHECK (channel_origin IN ('web', 'whatsapp', 'phone', 'in_person')),
    notes           TEXT,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMP
);
CREATE INDEX idx_tickets_status   ON tickets(status);
CREATE INDEX idx_tickets_category ON tickets(category);
CREATE TRIGGER trg_tickets_updated_at
    BEFORE UPDATE ON tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE ticket_history (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id       UUID        NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    previous_status VARCHAR(20),
    new_status      VARCHAR(20) NOT NULL,
    changed_by_id   UUID        REFERENCES users(id) ON DELETE SET NULL,
    note            TEXT,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_ticket_history_ticket_id ON ticket_history(ticket_id);
