-- ============================================================
-- SYNC METADATA — freshness tracking & debounce locks
-- ============================================================
CREATE TABLE IF NOT EXISTS sync_metadata (
    id              BIGSERIAL PRIMARY KEY,
    entity          TEXT NOT NULL,
    filter_hash     TEXT NOT NULL,
    filter_params   JSONB NOT NULL,
    last_synced_at  TIMESTAMPTZ,
    sync_started_at TIMESTAMPTZ,
    sync_status     TEXT DEFAULT 'idle',
    error_message   TEXT,
    ttl_seconds     INTEGER NOT NULL,
    pages_fetched   INTEGER DEFAULT 0,
    records_synced  INTEGER DEFAULT 0,

    CONSTRAINT uq_sync_entity_filter UNIQUE (entity, filter_hash)
);

CREATE INDEX IF NOT EXISTS idx_sync_entity ON sync_metadata (entity);
CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_metadata (sync_status);

-- ============================================================
-- ENTITY CONFIG — TTL and sync settings per entity
-- ============================================================
CREATE TABLE IF NOT EXISTS entity_config (
    entity          TEXT PRIMARY KEY,
    ttl_seconds     INTEGER NOT NULL,
    page_size       INTEGER DEFAULT 200,
    enabled         BOOLEAN DEFAULT TRUE,
    description     TEXT
);

INSERT INTO entity_config (entity, ttl_seconds, page_size, description) VALUES
    ('keszlet',         300,  200, 'Inventory snapshot - 5 min TTL'),
    ('kimeno_szamla',  1800,  200, 'Sales invoices - 30 min TTL'),
    ('raktari_mozgas', 1800,  200, 'Warehouse movements - 30 min TTL'),
    ('cikk',          86400,  200, 'Products master - 24 hour TTL')
ON CONFLICT (entity) DO NOTHING;
