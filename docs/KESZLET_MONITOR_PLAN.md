# Készlet Monitor — Feature Plan

**Date**: March 22, 2026
**Feature**: Dynamic inventory monitoring tab in Analytics, tenant-ready from day one
**Computation**: Supabase SQL function, parameterized by lookback period, lead time, service level

---

## 1. Architecture Overview

```
User changes lookback period (1–5 years)
         │
         ▼
Reflex UI calls tharanis_client.get_inventory_monitor(
    lookback_years=2, top_n=100, lead_time=3, service_level=0.95
)
         │
         ▼
Python client calls Supabase RPC:
    SELECT * FROM analysis.compute_inventory_monitor(
        p_tenant_id := 'samansport',
        p_lookback_years := 2,
        p_top_n := 100,
        p_lead_time_months := 3,
        p_z_score := 1.65
    )
         │
         ▼
SQL function computes EVERYTHING from raw.szamlak_analitika:
    1. Rank SKUs by revenue in lookback window
    2. Classify demand stability (CV)
    3. Compute seasonal avg + stddev (stockout-adjusted)
    4. Forecast H+1, H+2, H+3
    5. Calculate ROP at 1/2/3 month lead times
    6. Join live inventory from inventory_snapshot
    7. Compute IP = stock + on_order - backlogs
    8. Compute suggested order qty = max(0, ROP - IP)
         │
         ▼
Returns table with all columns matching the PDF report
```

---

## 2. Database Changes

### 2.1 — Tenant Config Table (new)

```sql
CREATE TABLE public.tenant_config (
    tenant_id       TEXT PRIMARY KEY,
    tenant_name     TEXT NOT NULL,
    -- Inventory monitor defaults
    default_lookback_years  INT DEFAULT 2,
    default_top_n           INT DEFAULT 100,
    default_lead_time       INT DEFAULT 3,      -- months
    default_service_level   NUMERIC DEFAULT 0.95,
    default_z_score         NUMERIC DEFAULT 1.65, -- derived from service_level
    -- Display preferences
    date_format     TEXT DEFAULT 'YYYY.MM.DD',
    currency        TEXT DEFAULT 'HUF',
    locale          TEXT DEFAULT 'hu-HU',
    theme           TEXT DEFAULT 'light',       -- 'light' or 'dark'
    -- Metadata
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Seed SamanSport as first tenant
INSERT INTO public.tenant_config (tenant_id, tenant_name)
VALUES ('samansport', 'SamanSport Kft.');
```

### 2.2 — Add tenant_id to Raw Data Tables

```sql
-- Add tenant_id with default for existing data
ALTER TABLE raw.szamlak_analitika
    ADD COLUMN tenant_id TEXT DEFAULT 'samansport';

ALTER TABLE raw.raktari_mozgas
    ADD COLUMN tenant_id TEXT DEFAULT 'samansport';

-- Index for performance (the function filters by tenant_id first)
CREATE INDEX idx_szamlak_tenant_date ON raw.szamlak_analitika(tenant_id, telj_d);
CREATE INDEX idx_mozgas_tenant_date ON raw.raktari_mozgas(tenant_id, kelt);

-- Add to inventory tables too (for live stock joins)
ALTER TABLE public.inventory_snapshot
    ADD COLUMN tenant_id TEXT DEFAULT 'samansport';

CREATE INDEX idx_inventory_tenant ON public.inventory_snapshot(tenant_id, sku);
```

### 2.3 — RLS Policies

```sql
-- Enable RLS
ALTER TABLE raw.szamlak_analitika ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenant_config ENABLE ROW LEVEL SECURITY;

-- For now: service_role bypasses RLS (Edge Functions + app backend)
-- When auth is added (Phase 7): policies will check auth.jwt() → tenant_id mapping
-- Placeholder policy: allow authenticated users to see their tenant's data
CREATE POLICY tenant_isolation_szamlak ON raw.szamlak_analitika
    FOR SELECT USING (true);  -- Open for now; tighten with auth later

CREATE POLICY tenant_isolation_config ON public.tenant_config
    FOR SELECT USING (true);
```

### 2.4 — The SQL Function

This is the core computation engine. It replaces the n8n workflow entirely.

```sql
CREATE OR REPLACE FUNCTION analysis.compute_inventory_monitor(
    p_tenant_id         TEXT DEFAULT 'samansport',
    p_lookback_years    INT DEFAULT 2,
    p_top_n             INT DEFAULT 100,
    p_lead_time_months  INT DEFAULT 3,
    p_z_score           NUMERIC DEFAULT 1.65
)
RETURNS TABLE (
    rank                INT,
    cikkszam            TEXT,
    cikknev             TEXT,
    stability           TEXT,
    month_sold_qty      NUMERIC,
    month_remaining_qty NUMERIC,
    forecast_qty_m1     NUMERIC,
    forecast_qty_m2     NUMERIC,
    forecast_qty_m3     NUMERIC,
    on_inventory        NUMERIC,
    on_order            NUMERIC,
    backlogs            NUMERIC,
    inventory_position  NUMERIC,
    rop_1m              NUMERIC,
    rop_2m              NUMERIC,
    rop_3m              NUMERIC,
    javasolt_1m         NUMERIC,
    javasolt_2m         NUMERIC,
    javasolt_3m         NUMERIC,
    below_rop           BOOLEAN,
    status              TEXT      -- 'RENDELJ' or 'OK'
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_cutoff_date   TEXT;
    v_current_month INT;
    v_current_year  INT;
    v_month_day     INT;
    v_days_in_month INT;
BEGIN
    -- Compute lookback cutoff date
    v_cutoff_date := TO_CHAR(CURRENT_DATE - (p_lookback_years * INTERVAL '1 year'), 'YYYY.MM.DD');
    v_current_month := EXTRACT(MONTH FROM CURRENT_DATE);
    v_current_year := EXTRACT(YEAR FROM CURRENT_DATE);
    v_month_day := EXTRACT(DAY FROM CURRENT_DATE);
    v_days_in_month := EXTRACT(DAY FROM (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' - INTERVAL '1 day'));

    RETURN QUERY
    WITH
    -- STEP 1: Rank SKUs by revenue in lookback window
    sku_revenue AS (
        SELECT
            s.cikkszam,
            MAX(s.cikknev) AS cikknev,
            SUM(COALESCE(s.brutto_ertek::NUMERIC, 0)) AS total_revenue,
            SUM(COALESCE(s.mennyiseg::NUMERIC, 0)) AS total_quantity,
            COUNT(*) AS transaction_count
        FROM raw.szamlak_analitika s
        WHERE s.tenant_id = p_tenant_id
          AND s.telj_d >= v_cutoff_date
          AND s.telj_d IS NOT NULL
          AND s.cikkszam IS NOT NULL
          AND COALESCE(s.stornopar, '') = ''  -- exclude stornos
        GROUP BY s.cikkszam
        ORDER BY total_revenue DESC
        LIMIT p_top_n
    ),
    ranked AS (
        SELECT
            ROW_NUMBER() OVER (ORDER BY total_revenue DESC)::INT AS rnk,
            sr.*
        FROM sku_revenue sr
    ),

    -- STEP 2: Monthly sales pivot for seasonal analysis
    -- Group sales by SKU + year + month, using ALL available history
    monthly_sales AS (
        SELECT
            s.cikkszam,
            EXTRACT(YEAR FROM TO_DATE(s.telj_d, 'YYYY.MM.DD'))::INT AS yr,
            EXTRACT(MONTH FROM TO_DATE(s.telj_d, 'YYYY.MM.DD'))::INT AS mo,
            SUM(COALESCE(s.mennyiseg::NUMERIC, 0)) AS qty
        FROM raw.szamlak_analitika s
        INNER JOIN ranked r ON r.cikkszam = s.cikkszam
        WHERE s.tenant_id = p_tenant_id
          AND s.telj_d IS NOT NULL
          AND COALESCE(s.stornopar, '') = ''
        GROUP BY s.cikkszam, yr, mo
    ),

    -- STEP 3: Stability classification (CV on monthly totals in lookback)
    monthly_totals_in_window AS (
        SELECT
            ms.cikkszam,
            ms.yr,
            ms.mo,
            ms.qty
        FROM monthly_sales ms
        WHERE TO_DATE(ms.yr::TEXT || '.' || LPAD(ms.mo::TEXT, 2, '0') || '.01', 'YYYY.MM.DD')
              >= (CURRENT_DATE - (p_lookback_years * INTERVAL '1 year'))
    ),
    cv_calc AS (
        SELECT
            cikkszam,
            AVG(qty) AS avg_qty,
            STDDEV_POP(qty) AS std_qty,
            CASE
                WHEN AVG(qty) = 0 THEN 0
                ELSE STDDEV_POP(qty) / NULLIF(AVG(qty), 0)
            END AS cv
        FROM monthly_totals_in_window
        GROUP BY cikkszam
    ),
    stability_class AS (
        SELECT
            cikkszam,
            CASE
                WHEN cv < 0.5 THEN 'stable'
                WHEN cv < 0.75 THEN 'light_volatile'
                ELSE 'volatile'
            END AS stability
        FROM cv_calc
    ),

    -- STEP 4: Seasonal averages + stddev (stockout-adjusted: exclude zero months)
    seasonal_stats AS (
        SELECT
            ms.cikkszam,
            ms.mo,
            AVG(CASE WHEN ms.qty > 0 THEN ms.qty END) AS avg_qty,
            COALESCE(STDDEV_POP(CASE WHEN ms.qty > 0 THEN ms.qty END), 0) AS stddev_qty
        FROM monthly_sales ms
        GROUP BY ms.cikkszam, ms.mo
    ),

    -- STEP 5: Forecasts for next 3 months (seasonal naive)
    forecast AS (
        SELECT
            r.cikkszam,
            COALESCE(s1.avg_qty, 0) AS fc_m1,
            COALESCE(s2.avg_qty, 0) AS fc_m2,
            COALESCE(s3.avg_qty, 0) AS fc_m3,
            -- Stddevs for ROP calculation
            COALESCE(s1.stddev_qty, 0) AS sd_m1,
            COALESCE(s2.stddev_qty, 0) AS sd_m2,
            COALESCE(s3.stddev_qty, 0) AS sd_m3
        FROM ranked r
        LEFT JOIN seasonal_stats s1 ON s1.cikkszam = r.cikkszam
            AND s1.mo = ((v_current_month % 12) + 1)         -- next month
        LEFT JOIN seasonal_stats s2 ON s2.cikkszam = r.cikkszam
            AND s2.mo = (((v_current_month + 1) % 12) + 1)   -- month+2
        LEFT JOIN seasonal_stats s3 ON s3.cikkszam = r.cikkszam
            AND s3.mo = (((v_current_month + 2) % 12) + 1)   -- month+3
    ),

    -- STEP 6: ROP calculation
    -- ROP(L) = μ(L) + z × σ(L)
    -- μ(L) = sum of forecasts over lead time months
    -- σ(L) = sqrt(sum of variance over lead time months)
    rop_calc AS (
        SELECT
            f.cikkszam,
            f.fc_m1, f.fc_m2, f.fc_m3,
            -- ROP for 1-month lead time
            (f.fc_m1 + p_z_score * f.sd_m1) AS rop_1m,
            -- ROP for 2-month lead time
            (f.fc_m1 + f.fc_m2 + p_z_score * SQRT(f.sd_m1^2 + f.sd_m2^2)) AS rop_2m,
            -- ROP for 3-month lead time
            (f.fc_m1 + f.fc_m2 + f.fc_m3 + p_z_score * SQRT(f.sd_m1^2 + f.sd_m2^2 + f.sd_m3^2)) AS rop_3m
        FROM forecast f
    ),

    -- STEP 7: Current month sales + remaining estimate
    current_month_sales AS (
        SELECT
            s.cikkszam,
            SUM(COALESCE(s.mennyiseg::NUMERIC, 0)) AS month_sold
        FROM raw.szamlak_analitika s
        INNER JOIN ranked r ON r.cikkszam = s.cikkszam
        WHERE s.tenant_id = p_tenant_id
          AND EXTRACT(YEAR FROM TO_DATE(s.telj_d, 'YYYY.MM.DD')) = v_current_year
          AND EXTRACT(MONTH FROM TO_DATE(s.telj_d, 'YYYY.MM.DD')) = v_current_month
          AND COALESCE(s.stornopar, '') = ''
        GROUP BY s.cikkszam
    ),
    current_month_forecast AS (
        SELECT
            r.cikkszam,
            COALESCE(ss.avg_qty, 0) AS expected_full_month
        FROM ranked r
        LEFT JOIN seasonal_stats ss ON ss.cikkszam = r.cikkszam AND ss.mo = v_current_month
    ),

    -- STEP 8: Live inventory (from the most recent snapshot)
    live_stock AS (
        SELECT
            sku AS cikkszam,
            COALESCE(total_available, 0) AS on_inventory
        FROM public.inventory_snapshot
        WHERE tenant_id = p_tenant_id
    )

    -- FINAL: Assemble the output
    SELECT
        r.rnk AS rank,
        r.cikkszam,
        r.cikknev,
        COALESCE(sc.stability, 'volatile') AS stability,
        COALESCE(cms.month_sold, 0) AS month_sold_qty,
        GREATEST(0, ROUND(COALESCE(cmf.expected_full_month, 0) - COALESCE(cms.month_sold, 0), 0)) AS month_remaining_qty,
        ROUND(COALESCE(rc.fc_m1, 0), 1) AS forecast_qty_m1,
        ROUND(COALESCE(rc.fc_m2, 0), 1) AS forecast_qty_m2,
        ROUND(COALESCE(rc.fc_m3, 0), 1) AS forecast_qty_m3,
        COALESCE(ls.on_inventory, 0) AS on_inventory,
        0::NUMERIC AS on_order,      -- placeholder until purchase order data available
        0::NUMERIC AS backlogs,      -- placeholder until backlog data available
        COALESCE(ls.on_inventory, 0) AS inventory_position,  -- IP = stock + on_order - backlogs
        ROUND(COALESCE(rc.rop_1m, 0), 1) AS rop_1m,
        ROUND(COALESCE(rc.rop_2m, 0), 1) AS rop_2m,
        ROUND(COALESCE(rc.rop_3m, 0), 1) AS rop_3m,
        GREATEST(0, ROUND(COALESCE(rc.rop_1m, 0) - COALESCE(ls.on_inventory, 0), 0)) AS javasolt_1m,
        GREATEST(0, ROUND(COALESCE(rc.rop_2m, 0) - COALESCE(ls.on_inventory, 0), 0)) AS javasolt_2m,
        GREATEST(0, ROUND(COALESCE(rc.rop_3m, 0) - COALESCE(ls.on_inventory, 0), 0)) AS javasolt_3m,
        (COALESCE(ls.on_inventory, 0) < COALESCE(rc.rop_3m, 0)) AS below_rop,
        CASE
            WHEN COALESCE(ls.on_inventory, 0) < COALESCE(rc.rop_3m, 0) THEN 'RENDELJ'
            ELSE 'OK'
        END AS status
    FROM ranked r
    LEFT JOIN stability_class sc ON sc.cikkszam = r.cikkszam
    LEFT JOIN rop_calc rc ON rc.cikkszam = r.cikkszam
    LEFT JOIN current_month_sales cms ON cms.cikkszam = r.cikkszam
    LEFT JOIN current_month_forecast cmf ON cmf.cikkszam = r.cikkszam
    LEFT JOIN live_stock ls ON ls.cikkszam = r.cikkszam
    ORDER BY r.rnk;
END;
$$;
```

**Performance note**: On 274K rows, this should execute in 1–3 seconds. The `idx_szamlak_tenant_date` index makes the initial filter fast. For larger datasets (1M+ rows), consider materializing the seasonal stats nightly and having the function use the materialized view for everything except live inventory.

---

## 3. What Changes When User Adjusts the Lookback Period

| Parameter | What recalculates | Why |
|-----------|-------------------|-----|
| **lookback_years** (1–5) | Which 100 SKUs are in the list + their revenue rank | Different time window = different top sellers |
| | Stability classification | CV is computed on the lookback window |
| | Note: seasonal averages use ALL history (not just lookback) | More data = better seasonal patterns |
| **lead_time** (1–3 months) | ROP values | Longer lead time = higher ROP = more reorder suggestions |
| **service_level** (90–99%) | z-score → ROP | Higher SL = higher safety stock |
| **top_n** (50–200) | Number of rows returned | More/fewer products to monitor |

**Important design decision baked in**: The function uses the lookback window for SKU ranking and stability, but uses ALL available history for seasonal averages. This is because seasonal patterns are more accurate with more years of data, even if recent revenue determines which products to monitor.

---

## 4. UI Design — "Készlet Monitor" Tab

### Tab Location
Third tab inside the Analytics page: Értékesítés | Mozgástörténet | **Készlet Monitor**

### Controls (top of tab)
- **Időszak** (lookback): Segmented buttons — 1 év / 2 év / 3 év / 5 év (default from tenant_config)
- **Átfutási idő** (lead time): Segmented — 1 hó / 2 hó / 3 hó (default from tenant_config)
- **Kiszolgálási szint**: Segmented — 90% / 95% / 99% (default from tenant_config)
- **Frissítés** button (optional — or auto-refresh on any param change)

### Summary KPIs (below controls)
- Monitorozott termékek: [100]
- Rendelést igényel: [76] (count where status = 'RENDELJ')
- OK: [24] (count where status = 'OK')
- Utolsó frissítés: [timestamp]

### Main Table
Sortable, scrollable table matching the PDF report layout:

| # | Cikksz. | Terméknév | Stab. | Havi el. | Havi hátra | H+1 | H+2 | H+3 | Készlet | IP | ROP | Jav 1h/2h/3h | St. |
|---|---------|-----------|-------|----------|------------|-----|-----|-----|---------|----|----|-------------|-----|

- **St.** column: colored badge — red "RENDELJ" / green "OK"
- **Készlet** column: highlight red if below ROP
- Row click could expand to show the product's monthly sales history chart (nice-to-have)

### CSV Export
"CSV Exportálás" button that downloads the full table with a Hungarian filename like:
`samansport_keszlet_riport_2026-03-22.csv`

---

## 5. Settings Page Integration

The tenant_config defaults feed into the Készlet Monitor tab as initial values. When the user changes params in the tab, those are session-level overrides. When they change defaults in Settings, those persist for next time.

Settings → Adatkonfiguráció section:
- Alapértelmezett időszak: [1–5 év dropdown]
- Alapértelmezett átfutási idő: [1–3 hó dropdown]
- Kiszolgálási szint: [90/95/99% dropdown]
- Monitorozott termékek száma: [50/100/150/200]

---

## 6. File Changes in the App

### New/Modified Files

| File | Change |
|------|--------|
| `tharanis_client.py` | Add `get_inventory_monitor(tenant_id, lookback, top_n, lead_time, z_score)` that calls the Supabase RPC function |
| `samansport/pages/analytics.py` | Add third tab "Készlet Monitor" with InventoryMonitorState |
| `samansport/state.py` | Add inventory monitor params to AppState or as a new substate |

### New Supabase Objects (applied via migration)

| Object | Type |
|--------|------|
| `public.tenant_config` | Table |
| `analysis.compute_inventory_monitor()` | Function |
| Indexes on `raw.szamlak_analitika(tenant_id, telj_d)` | Index |
| `tenant_id` column on raw tables | Column |

---

## 7. Execution Plan

### Step 1 — Database migration
Apply the migration that creates `tenant_config`, adds `tenant_id` columns, indexes, and the SQL function. Test the function directly:
```sql
SELECT * FROM analysis.compute_inventory_monitor('samansport', 2, 100, 3, 1.65);
```

### Step 2 — Backend client
Add the Python function in `tharanis_client.py` that calls the Supabase RPC.

### Step 3 — UI tab
Claude Code prompt to build the "Készlet Monitor" tab with controls and table.

### Step 4 — Settings integration
Wire the tenant_config defaults into the Settings page (if it exists by then) and into the tab's initial state.

---

## 8. Claude Code Prompt — Step 1: Database Migration

> **IMPORTANT**: Do NOT run this prompt yet. First, let's apply the Supabase migration together here, test the SQL function, and confirm the output matches your PDF report. Only then do we move to the app code.

---

## 9. Claude Code Prompt — Steps 2+3: App Integration

```
# TASK: Add "Készlet Monitor" tab to Analytics page

## CONTEXT
Read KESZLET_MONITOR_PLAN.md for full architecture details.

A Supabase SQL function `analysis.compute_inventory_monitor()` already exists and returns the full inventory monitoring dataset. It takes parameters: tenant_id, lookback_years, top_n, lead_time_months, z_score. Your job is to wire this into the Reflex app.

## STEP 1 — Backend Client
In `tharanis_client.py`, add:

```python
def get_inventory_monitor(
    lookback_years: int = 2,
    top_n: int = 100,
    lead_time: int = 3,
    service_level: float = 0.95,
    tenant_id: str = "samansport"
) -> list[dict]:
    """Call the inventory monitor SQL function via Supabase RPC."""
    z_score = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}.get(service_level, 1.65)
    result = supabase.rpc("compute_inventory_monitor", {
        "p_tenant_id": tenant_id,
        "p_lookback_years": lookback_years,
        "p_top_n": top_n,
        "p_lead_time_months": lead_time,
        "p_z_score": z_score
    }).execute()
    return result.data or []
```

Note: the function is in the `analysis` schema, so you may need to set `search_path` or call it with the schema prefix. Check the Supabase Python client docs for calling RPC functions in non-public schemas.

## STEP 2 — State
In the Analytics page, add `InventoryMonitorState` as a substate of `AppState`:

```python
class InventoryMonitorState(AppState):
    # Parameters
    lookback_years: int = 2
    lead_time: int = 3
    service_level: float = 0.95
    
    # Data
    monitor_data: list[dict] = []
    loading: bool = False
    
    # Computed
    @rx.var
    def total_monitored(self) -> int:
        return len(self.monitor_data)
    
    @rx.var
    def needs_reorder(self) -> int:
        return len([r for r in self.monitor_data if r.get("status") == "RENDELJ"])
    
    @rx.var
    def is_ok(self) -> int:
        return len([r for r in self.monitor_data if r.get("status") == "OK"])
    
    async def load_monitor_data(self):
        self.loading = True
        yield
        self.monitor_data = tharanis_client.get_inventory_monitor(
            lookback_years=self.lookback_years,
            lead_time=self.lead_time,
            service_level=self.service_level
        )
        self.loading = False
    
    def set_lookback(self, years: str):
        self.lookback_years = int(years)
        return self.load_monitor_data()
    
    def set_lead_time(self, months: str):
        self.lead_time = int(months)
        return self.load_monitor_data()
    
    def set_service_level(self, level: str):
        self.service_level = float(level)
        return self.load_monitor_data()
    
    def export_csv(self):
        # Generate CSV with Hungarian filename
        # samansport_keszlet_riport_YYYY-MM-DD.csv
        ...
```

## STEP 3 — UI Tab
Add a third tab "Készlet Monitor" in the Analytics page with:

### Controls row:
- Időszak: segmented buttons — 1 év / 2 év / 3 év / 5 év
- Átfutási idő: segmented — 1 hó / 2 hó / 3 hó
- Kiszolgálási szint: segmented — 90% / 95% / 99%

### Summary KPIs row:
- "Monitorozott" count
- "Rendelést igényel" count (red badge)
- "OK" count (green badge)

### Main data table:
Columns matching the PDF report:
- # (rank)
- Cikksz. (cikkszam)
- Terméknév (cikknev) — this should be the widest column
- Stab. (stability) — color-coded: stable=green, light_volatile=yellow, volatile=red
- Havi el. (month_sold_qty)
- Havi hátra (month_remaining_qty)
- H+1 (forecast_qty_m1)
- H+2 (forecast_qty_m2)
- H+3 (forecast_qty_m3)
- Készlet (on_inventory) — highlight red if below_rop
- IP (inventory_position)
- ROP (rop_3m for the configured lead time — show rop_1m/2m/3m based on lead_time setting)
- Jav 1h/2h/3h (javasolt_1m / javasolt_2m / javasolt_3m)
- St. (status) — colored badge: red "RENDELJ" / green "OK"

Table should be sortable by any column.
Table should show all rows (scrollable), not paginated.
Numbers should use Hungarian formatting (space as thousands separator).

### CSV export button:
"CSV Exportálás" button below the table.
Filename: samansport_keszlet_riport_YYYY-MM-DD.csv

### On page load:
When the Készlet Monitor tab is first opened, auto-load data with default parameters.

## RULES
- All UI text in Hungarian
- Use existing styles from styles.py for colors and card styling
- Apply @template decorator for sidebar
- Match the visual style of the existing Dashboard and Analytics tabs
- Use Playwright to verify the tab renders with real data
- Don't change anything in the Dashboard or existing Analytics tabs

Don't change anything else.
```
