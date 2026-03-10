-- ============================================================
-- TECHBOT — Módulo 4: Chatbot y conversaciones
-- ============================================================
CREATE TABLE intents (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                 VARCHAR(100) NOT NULL UNIQUE,
    description          TEXT,
    training_examples    JSONB        NOT NULL DEFAULT '[]',
    confidence_threshold DECIMAL(3,2) NOT NULL DEFAULT 0.75,
    is_active            BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_intents_updated_at
    BEFORE UPDATE ON intents FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE conversations (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id        UUID        NOT NULL REFERENCES sessions(id) ON DELETE RESTRICT,
    user_id           UUID        REFERENCES users(id) ON DELETE SET NULL,
    channel           VARCHAR(20) NOT NULL CHECK (channel IN ('web', 'whatsapp', 'phone', 'in_person')),
    status            VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'escalated', 'resolved', 'abandoned')),
    assigned_agent_id UUID        REFERENCES users(id) ON DELETE SET NULL,
    resolved_by       VARCHAR(10) CHECK (resolved_by IN ('bot', 'agent')),
    started_at        TIMESTAMP   NOT NULL DEFAULT NOW(),
    closed_at         TIMESTAMP,
    created_at        TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_status     ON conversations(status);
CREATE TRIGGER trg_conversations_updated_at
    BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID        NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type     VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'bot', 'agent')),
    sender_id       UUID        REFERENCES users(id) ON DELETE SET NULL,
    content         TEXT        NOT NULL,
    metadata        JSONB       NOT NULL DEFAULT '{}',
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);

CREATE TABLE message_intents (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id        UUID         NOT NULL REFERENCES messages(id)  ON DELETE CASCADE,
    intent_id         UUID         NOT NULL REFERENCES intents(id)   ON DELETE RESTRICT,
    confidence        DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    detected_entities JSONB        NOT NULL DEFAULT '{}',
    created_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_message_intents_message_id ON message_intents(message_id);

CREATE TABLE escalations (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id  UUID         NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    reason           VARCHAR(50)  NOT NULL CHECK (reason IN ('low_confidence', 'user_request', 'out_of_hours', 'complex_issue')),
    confidence_score DECIMAL(5,4),
    agent_id         UUID         REFERENCES users(id) ON DELETE SET NULL,
    escalated_at     TIMESTAMP    NOT NULL DEFAULT NOW(),
    attended_at      TIMESTAMP,
    resolved_at      TIMESTAMP
);
CREATE INDEX idx_escalations_conversation_id ON escalations(conversation_id);
