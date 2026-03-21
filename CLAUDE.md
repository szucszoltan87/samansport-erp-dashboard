# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SamanSport ERP Dashboard — a Streamlit analytics dashboard that caches data from a legacy Tharanis SOAP API via Supabase (PostgreSQL + Deno Edge Functions). Uses a stale-while-revalidate pattern for fast reads with background sync.

## Commands

```bash
# Run the Streamlit app
cd mvp && source venv/bin/activate && streamlit run app.py

# Install Python dependencies
cd mvp && pip install -r requirements.txt

# Run Supabase locally
cd supabase && supabase start

# Serve Edge Functions locally
cd supabase && supabase functions serve sync-entity check-freshness cron-refresh hydrate-all

# Apply database migrations
cd supabase && supabase db push

# Bulk-load historical data
cd mvp && python hydrate.py
```

No test suite or linter is configured yet.

## Architecture

### Data Flow (Stale-While-Revalidate)
1. Streamlit UI → `tharanis_client.py` queries Supabase (cached data, ~50ms)
2. Checks `sync_metadata` for freshness (TTL per entity: 5min inventory, 30min sales/movements, 24h products)
3. If stale → fires background HTTP call to `sync-entity` Edge Function
4. Edge Function claims atomic PL/pgSQL lock → paginates Tharanis SOAP API (200 records/page) → upserts to Supabase
5. Lock released, metadata updated

### Key Layers
- **`mvp/app.py`** — Main Streamlit dashboard (~1500 lines). Handles UI, charting (Plotly), session state, sidebar navigation
- **`mvp/tharanis_client.py`** — Data access layer. Abstracts Supabase queries with SOAP fallback
- **`mvp/seasonality_analyzer.py`** — Analytics for seasonal sales patterns
- **`supabase/functions/sync-entity/`** — Core sync orchestrator (Deno/TypeScript)
- **`supabase/functions/_shared/`** — SOAP client, XML parser (regex-based, not zeep), Supabase admin client, types
- **`supabase/migrations/`** — PostgreSQL schema (4 entity tables + sync metadata)

### Database Tables
- `sales_invoice_lines`, `inventory_snapshot`, `warehouse_movements`, `products` — entity data
- `sync_metadata`, `entity_config` — sync tracking and freshness locks

## Conventions

- **All UI text is in Hungarian** (Terméknév, Raktár, Mennyiség, etc.)
- **Date formats:** `YYYY.MM.DD` in Tharanis API, `YYYY-MM-DD` in PostgreSQL
- **DataFrame columns** use Hungarian field names; database columns use snake_case
- **SOAP XML parsing** uses regex (not the zeep library) for control over legacy quirks
- **Concurrent sync prevention:** atomic `UPDATE ... RETURNING` locks in PL/pgSQL
- **Environment config:** `.env` file in `mvp/` (see `.env.example` for required vars: Tharanis API credentials + Supabase keys)
- **Edge Functions:** Deno runtime, JWT verification disabled in `supabase/config.toml`
- **UI theme:** Grey-blue color scheme (palette in `theme.py`) with custom SVG icons
