-- ============================================================
-- claim_sync_lock: Atomic lock for debouncing concurrent syncs
-- Returns TRUE if this caller should proceed with the sync.
-- ============================================================
CREATE OR REPLACE FUNCTION claim_sync_lock(
    p_entity TEXT,
    p_filter_hash TEXT,
    p_filter_params JSONB,
    p_ttl_seconds INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_row sync_metadata%ROWTYPE;
    v_now TIMESTAMPTZ := NOW();
    v_stale_threshold INTERVAL;
    v_lock_timeout INTERVAL := INTERVAL '5 minutes';
BEGIN
    v_stale_threshold := (p_ttl_seconds || ' seconds')::INTERVAL;

    -- Upsert the metadata row
    INSERT INTO sync_metadata (entity, filter_hash, filter_params, ttl_seconds)
    VALUES (p_entity, p_filter_hash, p_filter_params, p_ttl_seconds)
    ON CONFLICT (entity, filter_hash) DO NOTHING;

    -- Try to acquire the lock atomically
    UPDATE sync_metadata
    SET sync_started_at = v_now,
        sync_status = 'running',
        error_message = NULL
    WHERE entity = p_entity
      AND filter_hash = p_filter_hash
      AND sync_status != 'running'
      AND (
          last_synced_at IS NULL
          OR (v_now - last_synced_at) > v_stale_threshold
      )
    RETURNING * INTO v_row;

    IF v_row.id IS NOT NULL THEN
        RETURN TRUE;
    END IF;

    -- Check if a running sync is stuck (older than lock_timeout)
    UPDATE sync_metadata
    SET sync_started_at = v_now,
        sync_status = 'running',
        error_message = 'Previous sync timed out, retrying'
    WHERE entity = p_entity
      AND filter_hash = p_filter_hash
      AND sync_status = 'running'
      AND (v_now - sync_started_at) > v_lock_timeout
    RETURNING * INTO v_row;

    RETURN v_row.id IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- release_sync_lock: Mark sync as complete or failed
-- ============================================================
CREATE OR REPLACE FUNCTION release_sync_lock(
    p_entity TEXT,
    p_filter_hash TEXT,
    p_records_synced INTEGER,
    p_pages_fetched INTEGER,
    p_error TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE sync_metadata
    SET sync_status = CASE WHEN p_error IS NULL THEN 'idle' ELSE 'error' END,
        last_synced_at = CASE WHEN p_error IS NULL THEN NOW() ELSE last_synced_at END,
        sync_started_at = NULL,
        records_synced = p_records_synced,
        pages_fetched = p_pages_fetched,
        error_message = p_error
    WHERE entity = p_entity
      AND filter_hash = p_filter_hash;
END;
$$ LANGUAGE plpgsql;
