-- Enable Realtime on sync_metadata so frontends get notified when syncs complete.
-- Do NOT enable on large data tables to avoid massive change streams during bulk upserts.
ALTER PUBLICATION supabase_realtime ADD TABLE sync_metadata;
