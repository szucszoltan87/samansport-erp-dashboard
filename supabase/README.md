# Supabase Edge Functions

This directory contains the Supabase backend for the SamanSport ERP Dashboard. Four Deno Edge Functions sync data from the legacy Tharanis SOAP API into Supabase PostgreSQL tables.

## Functions

| Function | Purpose |
|---|---|
| **sync-entity** | Core sync orchestrator — claims an atomic lock, paginates the Tharanis SOAP API, and upserts records into Supabase. |
| **check-freshness** | Lightweight read-only check — queries `sync_metadata` to determine whether cached data is still within its TTL. |
| **cron-refresh** | Scheduled refresh — triggers `sync-entity` for inventory, current-month sales, and current-month warehouse movements. |
| **hydrate-all** | Admin bulk loader — iterates month-by-month from a start year to the present, calling `sync-entity` for each chunk. |

## Shared Modules (`functions/_shared/`)

| Module | Role |
|---|---|
| `soap-client.ts` | Builds SOAP envelopes and POSTs them to the Tharanis API. |
| `xml-parser.ts` | Regex-based XML parser — extracts entity records from SOAP responses. |
| `supabase-admin.ts` | Creates a singleton Supabase client using the service-role key. |
| `types.ts` | TypeScript interfaces for all entity records and sync metadata. |
| `constants.ts` | API URL, timeouts, entity/table name mappings. |

## Deno / TypeScript Setup

Functions run on the **Supabase Deno runtime**. There is no `deno.json` or import map — dependencies are imported directly via URL:

- `https://deno.land/std@0.168.0/http/server.ts` — HTTP server
- `https://esm.sh/@supabase/supabase-js@2` — Supabase JS client

No lock file is used; Deno resolves URLs at runtime.

## Environment Variables

Set these in the Supabase dashboard (Project Settings > Edge Functions) for production, or export them before running `supabase functions serve` locally.

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | Yes | Supabase project URL (e.g. `https://<ref>.supabase.co`) |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service-role key — grants full DB access for upserts |
| `THARANIS_UGYFELKOD` | Yes | Tharanis customer code (default: `7354`) |
| `THARANIS_CEGKOD` | Yes | Tharanis company code (default: `ab`) |
| `THARANIS_APIKULCS` | Yes | Tharanis API authentication key |

> **Note:** JWT verification is disabled for all functions in `config.toml`. If you enable it, callers must pass a valid Supabase JWT in the `Authorization` header.

## Local Development

```bash
# Start local Supabase (Postgres, Auth, Storage, etc.)
supabase start

# Apply database migrations
supabase db push

# Serve all Edge Functions locally (hot-reload)
supabase functions serve sync-entity check-freshness cron-refresh hydrate-all
```

Functions are served at `http://localhost:54321/functions/v1/<function-name>`.

## Deploying to Production

```bash
# Deploy a single function
supabase functions deploy sync-entity

# Deploy all functions
supabase functions deploy sync-entity check-freshness cron-refresh hydrate-all
```

After deploying, set the environment variables in the Supabase dashboard. Functions are available at:

```
https://<project-ref>.supabase.co/functions/v1/<function-name>
```

## Database Migrations

Migrations in `migrations/` create the required tables and PL/pgSQL lock functions:

1. `001_create_entity_tables.sql` — `sales_invoice_lines`, `inventory_snapshot`, `warehouse_movements`, `products`
2. `002_create_sync_metadata.sql` — `sync_metadata`, `entity_config` + TTL seed data
3. `003_create_sync_functions.sql` — `claim_sync_lock()`, `release_sync_lock()` (atomic locking)
4. `004_enable_realtime.sql` — Enables Realtime on `sync_metadata`
