-- ============================================================
-- TECHBOT — Módulo 3: Drivers y base de conocimiento
-- ============================================================
CREATE TABLE drivers (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id       UUID         NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    name             VARCHAR(200) NOT NULL,
    version          VARCHAR(50)  NOT NULL,
    operating_system VARCHAR(50)  NOT NULL,
    architecture     VARCHAR(10)  NOT NULL CHECK (architecture IN ('x64', 'x86', 'ARM')),
    download_url     TEXT         NOT NULL,
    release_date     DATE,
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_drivers_product_id ON drivers(product_id);
CREATE TRIGGER trg_drivers_updated_at
    BEFORE UPDATE ON drivers FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE known_issues (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id     UUID REFERENCES products(id) ON DELETE SET NULL,
    title          VARCHAR(200) NOT NULL,
    error_code     VARCHAR(100),
    description    TEXT         NOT NULL,
    solution_steps JSONB        NOT NULL DEFAULT '[]',
    category       VARCHAR(50)  NOT NULL CHECK (category IN ('hardware', 'software', 'red', 'drivers', 'general')),
    difficulty     VARCHAR(20)  NOT NULL CHECK (difficulty IN ('basico', 'intermedio', 'avanzado')),
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_known_issues_error_code ON known_issues(error_code);
CREATE TRIGGER trg_known_issues_updated_at
    BEFORE UPDATE ON known_issues FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE faqs (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question   TEXT        NOT NULL,
    answer     TEXT        NOT NULL,
    category   VARCHAR(50),
    times_used INTEGER     NOT NULL DEFAULT 0,
    is_active  BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_faqs_updated_at
    BEFORE UPDATE ON faqs FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TABLE knowledge_embeddings (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type  VARCHAR(50) NOT NULL CHECK (source_type IN ('faq', 'known_issue', 'driver', 'product')),
    source_id    UUID        NOT NULL,
    content_text TEXT        NOT NULL,
    embedding    TEXT,
    created_at   TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_knowledge_embeddings_source_type ON knowledge_embeddings(source_type);
CREATE TRIGGER trg_knowledge_embeddings_updated_at
    BEFORE UPDATE ON knowledge_embeddings FOR EACH ROW EXECUTE FUNCTION update_updated_at();
