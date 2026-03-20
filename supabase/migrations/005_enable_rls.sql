-- Migration: Enable Row Level Security on all tables
-- Restricts anon role to read-only access, grants full access to service_role.
-- The service_role is used by Edge Functions for sync operations (upserts, deletes).
-- The anon role is used by the Streamlit dashboard for read-only queries.

-- ============================================================================
-- 1. Enable RLS on all entity and metadata tables
-- ============================================================================

ALTER TABLE sales_invoice_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_snapshot   ENABLE ROW LEVEL SECURITY;
ALTER TABLE warehouse_movements  ENABLE ROW LEVEL SECURITY;
ALTER TABLE products             ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_metadata        ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_config        ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. Anon role: SELECT-only policies
--    The Streamlit dashboard connects with the anon key and only needs to read.
-- ============================================================================

-- Sales invoice lines: anon can read all rows (date filtering happens in app)
CREATE POLICY anon_select_sales_invoice_lines
    ON sales_invoice_lines
    FOR SELECT
    TO anon
    USING (true);

-- Inventory snapshots: anon can read current stock levels
CREATE POLICY anon_select_inventory_snapshot
    ON inventory_snapshot
    FOR SELECT
    TO anon
    USING (true);

-- Warehouse movements: anon can read movement history
CREATE POLICY anon_select_warehouse_movements
    ON warehouse_movements
    FOR SELECT
    TO anon
    USING (true);

-- Products: anon can read the product catalog
CREATE POLICY anon_select_products
    ON products
    FOR SELECT
    TO anon
    USING (true);

-- Sync metadata: anon can read freshness info to decide whether to trigger sync
CREATE POLICY anon_select_sync_metadata
    ON sync_metadata
    FOR SELECT
    TO anon
    USING (true);

-- Entity config: anon can read TTL and sync configuration
CREATE POLICY anon_select_entity_config
    ON entity_config
    FOR SELECT
    TO anon
    USING (true);

-- ============================================================================
-- 3. Service role: full access (SELECT, INSERT, UPDATE, DELETE)
--    Edge Functions use the service_role key for sync operations that
--    upsert data from the Tharanis SOAP API and update sync metadata/locks.
-- ============================================================================

CREATE POLICY service_role_all_sales_invoice_lines
    ON sales_invoice_lines
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY service_role_all_inventory_snapshot
    ON inventory_snapshot
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY service_role_all_warehouse_movements
    ON warehouse_movements
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY service_role_all_products
    ON products
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY service_role_all_sync_metadata
    ON sync_metadata
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY service_role_all_entity_config
    ON entity_config
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
