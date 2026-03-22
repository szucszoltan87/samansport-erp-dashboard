-- ============================================================
-- INVENTORY MONITOR — tenant config, tenant_id columns,
-- analysis schema, and computation functions
-- ============================================================

-- 1. Tenant config table
CREATE TABLE IF NOT EXISTS public.tenant_config (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    default_lookback_years  INT DEFAULT 2,
    default_top_n           INT DEFAULT 100,
    default_service_level   NUMERIC DEFAULT 0.95,
    default_lead_time_months INT DEFAULT 3,
    date_format     TEXT DEFAULT 'YYYY.MM.DD',
    currency        TEXT DEFAULT 'HUF',
    theme           TEXT DEFAULT 'light',
    language        TEXT DEFAULT 'hu',
    active          BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
INSERT INTO public.tenant_config (slug, name)
VALUES ('samansport', 'SamanSport') ON CONFLICT DO NOTHING;

-- 2. Add tenant_id columns (uuid FK to tenant_config)
ALTER TABLE raw.szamlak_analitika ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE raw.raktari_mozgas ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE public.inventory_snapshot ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'samansport';

-- Backfill tenant_id from tenant_config
UPDATE raw.szamlak_analitika SET tenant_id = (SELECT id FROM tenant_config WHERE slug = 'samansport') WHERE tenant_id IS NULL;
UPDATE raw.raktari_mozgas SET tenant_id = (SELECT id FROM tenant_config WHERE slug = 'samansport') WHERE tenant_id IS NULL;

-- 3. Indexes
CREATE INDEX IF NOT EXISTS idx_szamlak_tenant_date ON raw.szamlak_analitika(tenant_id, telj_d);
CREATE INDEX IF NOT EXISTS idx_szamlak_tenant_sku ON raw.szamlak_analitika(tenant_id, cikkszam);
CREATE INDEX IF NOT EXISTS idx_mozgas_tenant_date ON raw.raktari_mozgas(tenant_id, kelt);
CREATE INDEX IF NOT EXISTS idx_inventory_tenant ON public.inventory_snapshot(tenant_id, sku);

-- 4. Analysis schema
CREATE SCHEMA IF NOT EXISTS analysis;
GRANT USAGE ON SCHEMA analysis TO anon, authenticated;

-- Expose analysis schema to PostgREST
ALTER ROLE authenticator SET pgrst.db_schemas = 'public, raw, analysis';
NOTIFY pgrst, 'reload config';

-- 5. Public computation function (used by the app via RPC)
--    Filters: cikktipus='T' (products only), HAVING COUNT(*)>=3 (no one-offs)
--    Inventory source: analysis.computed_inventory
CREATE OR REPLACE FUNCTION public.compute_inventory_monitor(
    p_tenant_id uuid,
    p_lookback_years integer DEFAULT 2,
    p_top_n integer DEFAULT 100,
    p_service_level numeric DEFAULT 0.95,
    p_lead_time_months integer DEFAULT 3
)
RETURNS TABLE(
    out_rank integer, out_cikkszam text, out_cikknev text, out_stability text,
    out_month_sold_qty numeric, out_month_remaining_qty numeric,
    out_forecast_m1 numeric, out_forecast_m2 numeric, out_forecast_m3 numeric,
    out_on_inventory numeric, out_inventory_position numeric,
    out_rop numeric, out_rop_1m numeric, out_rop_2m numeric, out_rop_3m numeric,
    out_javasolt_1m numeric, out_javasolt_2m numeric, out_javasolt_3m numeric,
    out_below_rop boolean, out_status text
)
LANGUAGE plpgsql
STABLE
AS $function$
DECLARE
    v_z numeric;
    v_cutoff text;
    v_cur_month int := EXTRACT(MONTH FROM CURRENT_DATE)::int;
    v_cur_year int := EXTRACT(YEAR FROM CURRENT_DATE)::int;
    v_m1 int; v_m2 int; v_m3 int;
BEGIN
    v_z := CASE
        WHEN p_service_level >= 0.99  THEN 2.33
        WHEN p_service_level >= 0.975 THEN 1.96
        WHEN p_service_level >= 0.95  THEN 1.65
        WHEN p_service_level >= 0.90  THEN 1.28
        ELSE 1.04
    END;
    v_cutoff := TO_CHAR(CURRENT_DATE - (p_lookback_years || ' years')::interval, 'YYYY.MM.DD');
    v_m1 := (v_cur_month % 12) + 1;
    v_m2 := ((v_cur_month + 1) % 12) + 1;
    v_m3 := ((v_cur_month + 2) % 12) + 1;

    RETURN QUERY
    WITH
    parsed AS (
        SELECT s.cikkszam AS p_sku, s.cikknev AS p_name,
            EXTRACT(YEAR  FROM TO_DATE(s.telj_d,'YYYY.MM.DD'))::int AS p_yr,
            EXTRACT(MONTH FROM TO_DATE(s.telj_d,'YYYY.MM.DD'))::int AS p_mo,
            COALESCE(NULLIF(REPLACE(REPLACE(s.mennyiseg,' ',''),',','.'),'')::numeric, 0) AS p_qty,
            COALESCE(NULLIF(REPLACE(REPLACE(s.brutto_ertek,' ',''),',','.'),'')::numeric, 0) AS p_gval
        FROM raw.szamlak_analitika s
        WHERE s.tenant_id = p_tenant_id
          AND s.telj_d >= v_cutoff AND s.telj_d IS NOT NULL AND s.telj_d <> ''
          AND s.cikktipus = 'T'
    ),
    sku_rev AS (
        SELECT p.p_sku, MAX(p.p_name) AS sr_name, SUM(p.p_gval) AS sr_rev
        FROM parsed p WHERE p.p_gval > 0
        GROUP BY p.p_sku
        HAVING COUNT(*) >= 3
    ),
    ranked AS (
        SELECT sr.p_sku, sr.sr_name, ROW_NUMBER() OVER (ORDER BY sr.sr_rev DESC) AS sr_rnk
        FROM sku_rev sr
    ),
    top AS (SELECT r.sr_rnk, r.p_sku, r.sr_name FROM ranked r WHERE r.sr_rnk <= p_top_n),
    monthly AS (
        SELECT p.p_sku, p.p_yr, p.p_mo, SUM(p.p_qty) AS m_qty
        FROM parsed p INNER JOIN top t ON p.p_sku = t.p_sku
        GROUP BY p.p_sku, p.p_yr, p.p_mo
    ),
    seasonal AS (
        SELECT m.p_sku AS s_sku, m.p_mo AS s_mo,
            COALESCE(AVG(CASE WHEN m.m_qty > 0 THEN m.m_qty END), 0) AS s_avg,
            COALESCE(STDDEV_SAMP(CASE WHEN m.m_qty > 0 THEN m.m_qty END), 0) AS s_std
        FROM monthly m GROUP BY m.p_sku, m.p_mo
    ),
    stab AS (
        SELECT ss.s_sku,
            CASE
              WHEN NULLIF(AVG(NULLIF(ss.s_avg,0)),0) IS NULL THEN 'volatile'
              WHEN COALESCE(STDDEV(ss.s_avg),0)/AVG(NULLIF(ss.s_avg,0)) < 0.3 THEN 'stable'
              WHEN COALESCE(STDDEV(ss.s_avg),0)/AVG(NULLIF(ss.s_avg,0)) < 0.6 THEN 'light_volatile'
              ELSE 'volatile'
            END AS st_val
        FROM seasonal ss GROUP BY ss.s_sku
    ),
    fc AS (
        SELECT t.p_sku AS f_sku,
            COALESCE(s1.s_avg,0) AS f1, COALESCE(s1.s_std,0) AS d1,
            COALESCE(s2.s_avg,0) AS f2, COALESCE(s2.s_std,0) AS d2,
            COALESCE(s3.s_avg,0) AS f3, COALESCE(s3.s_std,0) AS d3
        FROM top t
        LEFT JOIN seasonal s1 ON t.p_sku=s1.s_sku AND s1.s_mo=v_m1
        LEFT JOIN seasonal s2 ON t.p_sku=s2.s_sku AND s2.s_mo=v_m2
        LEFT JOIN seasonal s3 ON t.p_sku=s3.s_sku AND s3.s_mo=v_m3
    ),
    cur_month AS (
        SELECT p.p_sku AS cm_sku, SUM(p.p_qty) AS cm_sold
        FROM parsed p INNER JOIN top t ON p.p_sku=t.p_sku
        WHERE p.p_yr=v_cur_year AND p.p_mo=v_cur_month GROUP BY p.p_sku
    ),
    cur_exp AS (
        SELECT ss.s_sku AS ce_sku, ss.s_avg AS ce_exp FROM seasonal ss WHERE ss.s_mo=v_cur_month
    ),
    inv AS (
        SELECT ci.cikkszam AS i_sku, ci.on_inventory AS i_stock
        FROM analysis.computed_inventory ci WHERE ci.tenant_id=p_tenant_id
    ),
    assembled AS (
        SELECT
            t.sr_rnk::int AS a_rank, t.p_sku AS a_sku, t.sr_name AS a_name,
            COALESCE(st.st_val,'volatile') AS a_stab,
            COALESCE(cm.cm_sold,0) AS a_sold,
            GREATEST(COALESCE(ce.ce_exp,0)-COALESCE(cm.cm_sold,0),0) AS a_remain,
            ROUND(f.f1,1) AS a_f1, ROUND(f.f2,1) AS a_f2, ROUND(f.f3,1) AS a_f3,
            COALESCE(i.i_stock,0) AS a_inv,
            ROUND(CASE p_lead_time_months
                WHEN 1 THEN f.f1+v_z*f.d1
                WHEN 2 THEN (f.f1+f.f2)+v_z*SQRT(f.d1^2+f.d2^2)
                ELSE (f.f1+f.f2+f.f3)+v_z*SQRT(f.d1^2+f.d2^2+f.d3^2)
            END,1) AS a_rop,
            ROUND(f.f1+v_z*f.d1,1) AS a_rop1,
            ROUND((f.f1+f.f2)+v_z*SQRT(f.d1^2+f.d2^2),1) AS a_rop2,
            ROUND((f.f1+f.f2+f.f3)+v_z*SQRT(f.d1^2+f.d2^2+f.d3^2),1) AS a_rop3
        FROM top t
        LEFT JOIN stab st ON t.p_sku=st.s_sku
        LEFT JOIN fc f ON t.p_sku=f.f_sku
        LEFT JOIN cur_month cm ON t.p_sku=cm.cm_sku
        LEFT JOIN cur_exp ce ON t.p_sku=ce.ce_sku
        LEFT JOIN inv i ON t.p_sku=i.i_sku
    )
    SELECT a.a_rank, a.a_sku, a.a_name, a.a_stab,
        a.a_sold, a.a_remain, a.a_f1, a.a_f2, a.a_f3,
        a.a_inv, a.a_inv,
        a.a_rop, a.a_rop1, a.a_rop2, a.a_rop3,
        GREATEST(0,a.a_rop1-a.a_inv)::numeric,
        GREATEST(0,a.a_rop2-a.a_inv)::numeric,
        GREATEST(0,a.a_rop3-a.a_inv)::numeric,
        (a.a_inv < a.a_rop),
        CASE WHEN a.a_inv >= a.a_rop THEN 'OK' ELSE 'RENDELJ' END
    FROM assembled a ORDER BY a.a_rank;
END;
$function$;

GRANT EXECUTE ON FUNCTION public.compute_inventory_monitor(uuid, integer, integer, numeric, integer) TO anon, authenticated;
