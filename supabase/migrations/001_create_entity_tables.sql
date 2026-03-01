-- ============================================================
-- SALES INVOICE LINE ITEMS (kimeno_szamla tetelek)
-- ============================================================
CREATE TABLE IF NOT EXISTS sales_invoice_lines (
    id              BIGSERIAL PRIMARY KEY,
    fulfillment_date DATE NOT NULL,
    sku             TEXT NOT NULL,
    quantity        NUMERIC(12,4) NOT NULL,
    net_price       NUMERIC(14,4) NOT NULL,
    vat_pct         NUMERIC(5,2) DEFAULT 27.0,
    gross_price     NUMERIC(14,4) NOT NULL,
    net_value       NUMERIC(16,2) NOT NULL,
    gross_value     NUMERIC(16,2) NOT NULL,
    is_storno       BOOLEAN DEFAULT FALSE,
    raw_xml_hash    TEXT,
    synced_at       TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_sales_line UNIQUE (fulfillment_date, sku, quantity, net_price, raw_xml_hash)
);

CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_invoice_lines (fulfillment_date);
CREATE INDEX IF NOT EXISTS idx_sales_sku ON sales_invoice_lines (sku);
CREATE INDEX IF NOT EXISTS idx_sales_date_sku ON sales_invoice_lines (fulfillment_date, sku);

-- ============================================================
-- INVENTORY SNAPSHOT (keszlet)
-- ============================================================
CREATE TABLE IF NOT EXISTS inventory_snapshot (
    id              BIGSERIAL PRIMARY KEY,
    sku             TEXT NOT NULL UNIQUE,
    total_available NUMERIC(12,2) NOT NULL,
    warehouse_1     NUMERIC(12,2) DEFAULT 0,
    warehouse_2     NUMERIC(12,2) DEFAULT 0,
    warehouse_3     NUMERIC(12,2) DEFAULT 0,
    warehouse_4     NUMERIC(12,2) DEFAULT 0,
    warehouse_5     NUMERIC(12,2) DEFAULT 0,
    warehouse_6     NUMERIC(12,2) DEFAULT 0,
    synced_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory_snapshot (sku);

-- ============================================================
-- WAREHOUSE MOVEMENTS (raktari_mozgas)
-- ============================================================
CREATE TABLE IF NOT EXISTS warehouse_movements (
    id              BIGSERIAL PRIMARY KEY,
    movement_date   DATE NOT NULL,
    sku             TEXT NOT NULL,
    direction       CHAR(1) NOT NULL,
    movement_type   TEXT,
    quantity        NUMERIC(12,4) NOT NULL,
    raw_xml_hash    TEXT,
    synced_at       TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_movement UNIQUE (movement_date, sku, direction, quantity, raw_xml_hash)
);

CREATE INDEX IF NOT EXISTS idx_movements_date ON warehouse_movements (movement_date);
CREATE INDEX IF NOT EXISTS idx_movements_sku ON warehouse_movements (sku);
CREATE INDEX IF NOT EXISTS idx_movements_date_dir ON warehouse_movements (movement_date, direction);

-- ============================================================
-- PRODUCTS (cikk)
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    id              BIGSERIAL PRIMARY KEY,
    sku             TEXT NOT NULL UNIQUE,
    name            TEXT,
    category        TEXT,
    manufacturer    TEXT,
    unit            TEXT,
    active          BOOLEAN DEFAULT TRUE,
    synced_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_sku ON products (sku);
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
