"""
Tharanis API V3 Client — Supabase-backed with SOAP fallback.

Primary reads come from Supabase (fast JSON, ~50ms).
If data is stale, a background Edge Function syncs from the Tharanis SOAP API.
Falls back to direct SOAP calls if Supabase is not configured.
"""

import os
import re
import html
import json
import hashlib
import warnings
import contextlib
import threading
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore", message="Unverified HTTPS")

# ── Tharanis SOAP credentials ────────────────────────────────────────────────
_API_URL    = os.getenv("THARANIS_API_URL",   "https://login.tharanis.hu/apiv3.php")
_UGYFELKOD  = os.getenv("THARANIS_UGYFELKOD", "7354")
_CEGKOD     = os.getenv("THARANIS_CEGKOD",    "ab")
_APIKULCS   = os.getenv("THARANIS_API_KEY",   "")

_HEADERS = {"Content-Type": "text/xml; charset=utf-8"}

# ── Supabase config ──────────────────────────────────────────────────────────
_SUPABASE_URL  = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY  = os.getenv("SUPABASE_ANON_KEY", "")
_USE_SUPABASE  = bool(_SUPABASE_URL and _SUPABASE_KEY)

_supabase_client = None


def _get_supabase():
    """Lazy-init Supabase client."""
    global _supabase_client
    if _supabase_client is None and _USE_SUPABASE:
        from supabase import create_client
        _supabase_client = create_client(_SUPABASE_URL, _SUPABASE_KEY)
    return _supabase_client


# ── Supabase helpers ─────────────────────────────────────────────────────────

def _compute_filter_hash(entity: str, **kwargs) -> str:
    raw = json.dumps({"entity": entity, **{k: v for k, v in kwargs.items() if v}}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _is_stale(supabase, entity: str, filter_hash: str) -> bool:
    """Check sync_metadata to see if data needs refreshing."""
    try:
        result = supabase.table("sync_metadata") \
            .select("last_synced_at, ttl_seconds, sync_status") \
            .eq("entity", entity) \
            .eq("filter_hash", filter_hash) \
            .execute()

        if not result.data:
            return True  # Never synced

        meta = result.data[0]
        if meta["sync_status"] == "running":
            return False  # Already syncing

        if not meta["last_synced_at"]:
            return True

        last_synced = datetime.fromisoformat(meta["last_synced_at"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - last_synced).total_seconds()
        return age > meta["ttl_seconds"]
    except Exception:
        return True


def _supabase_select_all(supabase, table: str, select: str, filters: list[tuple] = None) -> list[dict]:
    """Paginated Supabase read to bypass the default 1000-row limit."""
    all_rows = []
    page_size = 1000
    offset = 0
    while True:
        query = supabase.table(table).select(select).range(offset, offset + page_size - 1)
        if filters:
            for method, args in filters:
                query = getattr(query, method)(*args)
        result = query.execute()
        rows = result.data or []
        all_rows.extend(rows)
        if len(rows) < page_size:
            break
        offset += page_size
    return all_rows


def _trigger_sync_background(entity: str, filters: dict):
    """Fire-and-forget: trigger the sync-entity Edge Function in a background thread."""
    def _do_sync():
        try:
            supabase = _get_supabase()
            if supabase:
                supabase.functions.invoke(
                    "sync-entity",
                    invoke_options={"body": {"entity": entity, "filters": filters}}
                )
        except Exception:
            pass  # Non-fatal — stale data is still served

    thread = threading.Thread(target=_do_sync, daemon=True)
    thread.start()


# ── Supabase read functions ──────────────────────────────────────────────────

def _supabase_get_sales(start_date: str, end_date: str,
                         cikkszam: str | None = None) -> pd.DataFrame | None:
    """Read sales data from Supabase. Returns None if Supabase is unavailable."""
    supabase = _get_supabase()
    if not supabase:
        return None

    try:
        # Convert YYYY.MM.DD to YYYY-MM-DD for PostgreSQL
        start_pg = start_date.replace(".", "-")
        end_pg = end_date.replace(".", "-")

        filters = [
            ("gte", ("fulfillment_date", start_pg)),
            ("lte", ("fulfillment_date", end_pg)),
        ]
        if cikkszam:
            filters.append(("eq", ("sku", cikkszam)))

        rows = _supabase_select_all(
            supabase, "sales_invoice_lines",
            "fulfillment_date, sku, quantity, net_price, vat_pct, gross_price, net_value, gross_value",
            filters
        )

        if not rows:
            return pd.DataFrame(
                columns=["kelt", "Cikkszám", "Mennyiség",
                         "Nettó ár", "Bruttó ár", "Nettó érték", "Bruttó érték"]
            )

        df = pd.DataFrame(rows)
        # Map Supabase columns to legacy Hungarian column names
        df = df.rename(columns={
            "fulfillment_date": "kelt",
            "sku": "Cikkszám",
            "quantity": "Mennyiség",
            "net_price": "Nettó ár",
            "gross_price": "Bruttó ár",
            "net_value": "Nettó érték",
            "gross_value": "Bruttó érték",
        })
        df = df[["kelt", "Cikkszám", "Mennyiség", "Nettó ár", "Bruttó ár", "Nettó érték", "Bruttó érték"]]
        df["kelt"] = pd.to_datetime(df["kelt"], errors="coerce")

        # Check freshness and trigger background refresh if stale
        fh = _compute_filter_hash("kimeno_szamla", start_date=start_date, end_date=end_date, cikkszam=cikkszam)
        if _is_stale(supabase, "kimeno_szamla", fh):
            _trigger_sync_background("kimeno_szamla", {
                "start_date": start_date, "end_date": end_date, "cikkszam": cikkszam
            })

        return df
    except Exception:
        return None


def _supabase_get_inventory(cikkszam: str | None = None) -> pd.DataFrame | None:
    """Read inventory data from Supabase."""
    supabase = _get_supabase()
    if not supabase:
        return None

    try:
        filters = []
        if cikkszam:
            filters.append(("eq", ("sku", cikkszam)))

        rows = _supabase_select_all(
            supabase, "inventory_snapshot",
            "sku, total_available, warehouse_1, warehouse_2, warehouse_3, warehouse_4, warehouse_5, warehouse_6",
            filters
        )

        if not rows:
            return pd.DataFrame(
                columns=["Cikkszám", "Készlet",
                         "Raktár 1", "Raktár 2", "Raktár 3",
                         "Raktár 4", "Raktár 5", "Raktár 6"]
            )

        df = pd.DataFrame(rows)
        df = df.rename(columns={
            "sku": "Cikkszám",
            "total_available": "Készlet",
            "warehouse_1": "Raktár 1",
            "warehouse_2": "Raktár 2",
            "warehouse_3": "Raktár 3",
            "warehouse_4": "Raktár 4",
            "warehouse_5": "Raktár 5",
            "warehouse_6": "Raktár 6",
        })

        # Check freshness
        fh = _compute_filter_hash("keszlet", cikkszam=cikkszam)
        if _is_stale(supabase, "keszlet", fh):
            _trigger_sync_background("keszlet", {"cikkszam": cikkszam} if cikkszam else {})

        return df
    except Exception:
        return None


def _supabase_get_movements(start_date: str, end_date: str,
                             cikkszam: str | None = None) -> pd.DataFrame | None:
    """Read warehouse movements from Supabase."""
    supabase = _get_supabase()
    if not supabase:
        return None

    try:
        start_pg = start_date.replace(".", "-")
        end_pg = end_date.replace(".", "-")

        filters = [
            ("gte", ("movement_date", start_pg)),
            ("lte", ("movement_date", end_pg)),
        ]
        if cikkszam:
            filters.append(("eq", ("sku", cikkszam)))

        rows = _supabase_select_all(
            supabase, "warehouse_movements",
            "movement_date, sku, direction, movement_type, quantity",
            filters
        )

        if not rows:
            return pd.DataFrame(
                columns=["kelt", "Cikkszám", "Irány", "Mozgástípus", "Mennyiség"]
            )

        df = pd.DataFrame(rows)
        df = df.rename(columns={
            "movement_date": "kelt",
            "sku": "Cikkszám",
            "direction": "Irány",
            "movement_type": "Mozgástípus",
            "quantity": "Mennyiség",
        })
        df = df[["kelt", "Cikkszám", "Irány", "Mozgástípus", "Mennyiség"]]
        df["kelt"] = pd.to_datetime(df["kelt"], errors="coerce")

        # Check freshness
        fh = _compute_filter_hash("raktari_mozgas", start_date=start_date, end_date=end_date, cikkszam=cikkszam)
        if _is_stale(supabase, "raktari_mozgas", fh):
            _trigger_sync_background("raktari_mozgas", {
                "start_date": start_date, "end_date": end_date, "cikkszam": cikkszam
            })

        return df
    except Exception:
        return None


# ── Low-level SOAP helpers (fallback) ────────────────────────────────────────

def _tag(xml: str, tag: str) -> str:
    """Return the text content of the first matching XML tag (CDATA-aware)."""
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", xml, re.DOTALL)
    if not m:
        return ""
    val = m.group(1).strip()
    cdata = re.match(r"<!\[CDATA\[(.*?)\]\]>", val, re.DOTALL)
    return (cdata.group(1) if cdata else val).strip()


def _build_envelope(entity: str, leker_xml: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:ns1="urn://apiv3"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <SOAP-ENV:Body>
    <ns1:leker>
      <param0 xsi:type="xsd:string">{_UGYFELKOD}</param0>
      <param1 xsi:type="xsd:string">{_CEGKOD}</param1>
      <param2 xsi:type="xsd:string">{_APIKULCS}</param2>
      <param3 xsi:type="xsd:string">{entity}</param3>
      <param4 xsi:type="xsd:string"><![CDATA[{leker_xml}]]></param4>
    </ns1:leker>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""


def _build_leker(start_date: str, end_date: str, cikkszam: str | None,
                 page: int = 0, limit: int = 200) -> str:
    szurok = (
        f"<szuro><mezo>teljdat</mezo><relacio>&gt;=</relacio><ertek>{start_date}</ertek></szuro>"
        f"<szuro><mezo>teljdat</mezo><relacio>&lt;=</relacio><ertek>{end_date}</ertek></szuro>"
        f"<szuro><mezo>storno</mezo><relacio>=</relacio><ertek>0</ertek></szuro>"
    )
    if cikkszam:
        szurok += (
            f"<szuro><mezo>cikksz</mezo><relacio>=</relacio>"
            f"<ertek>{cikkszam}</ertek></szuro>"
        )
    return (
        f"<leker><limit>{limit}</limit><oldal>{page}</oldal>"
        f"<szurok>{szurok}</szurok>"
        f"<adatok><fej>I</fej></adatok></leker>"
    )


def _build_keszlet_leker(cikkszam: str | None, page: int = 0, limit: int = 200) -> str:
    if cikkszam:
        szurok = (
            f"<szurok><szuro><mezo>cikksz</mezo><relacio>=</relacio>"
            f"<ertek>{cikkszam}</ertek></szuro></szurok>"
        )
    else:
        szurok = ""
    return f"<leker><limit>{limit}</limit><oldal>{page}</oldal>{szurok}</leker>"


def _build_mozgas_leker(start_date: str, end_date: str, cikkszam: str | None,
                        page: int = 0, limit: int = 200) -> str:
    szurok = (
        f"<szuro><mezo>kelt</mezo><relacio>&gt;=</relacio><ertek>{start_date}</ertek></szuro>"
        f"<szuro><mezo>kelt</mezo><relacio>&lt;=</relacio><ertek>{end_date}</ertek></szuro>"
        f"<szuro><mezo>torolt</mezo><relacio>=</relacio><ertek>0</ertek></szuro>"
    )
    if cikkszam:
        szurok += (
            f"<szuro><mezo>cikksz</mezo><relacio>=</relacio>"
            f"<ertek>{cikkszam}</ertek></szuro>"
        )
    return (
        f"<leker><limit>{limit}</limit><oldal>{page}</oldal>"
        f"<szurok>{szurok}</szurok>"
        f"<adatok><fej>I</fej></adatok></leker>"
    )


def _post_soap(entity: str, leker_xml: str) -> str:
    envelope = _build_envelope(entity, leker_xml)
    r = requests.post(
        _API_URL,
        data=envelope.encode("utf-8"),
        headers=_HEADERS,
        verify=False,
        timeout=120,
    )
    r.raise_for_status()
    return r.text


def _extract_valasz(soap_text: str) -> str:
    m = re.search(r"<return[^>]*>(.*?)</return>", soap_text, re.DOTALL)
    if not m:
        raise ValueError("No <return> element found in SOAP response.")
    inner = html.unescape(m.group(1)).strip()
    inner = re.sub(r"^<\?xml[^?]*\?>\s*", "", inner, flags=re.IGNORECASE)
    hiba_m = re.search(r"<hiba>(\d+)</hiba>", inner)
    if hiba_m and int(hiba_m.group(1)) != 0:
        msg = _tag(inner, "valasz") or "(no message)"
        raise ValueError(f"Tharanis API hiba {hiba_m.group(1)}: {msg}")
    valasz_m = re.search(r"<valasz>(.*?)</valasz>", inner, re.DOTALL)
    return valasz_m.group(1).strip() if valasz_m else ""


def _parse_tetelek(valasz_xml: str, cikkszam_filter: str | None = None) -> list[dict]:
    records = []
    for elem_m in re.finditer(r"<elem>(.*?)</elem>", valasz_xml, re.DOTALL):
        elem = elem_m.group(1)
        kelt = _tag(elem, "telj_dat")
        fej = re.search(r"<fej>(.*?)</fej>", elem, re.DOTALL)
        if fej:
            kelt = _tag(fej.group(1), "telj_dat") or kelt
        for tet_m in re.finditer(r"<tetel>(.*?)</tetel>", elem, re.DOTALL):
            t = tet_m.group(1)
            cikksz     = _tag(t, "cikksz")
            if cikkszam_filter and cikksz != cikkszam_filter:
                continue
            menny_s    = _tag(t, "menny")
            netto_ar_s = _tag(t, "netto_ar")
            afa_s      = _tag(t, "afa_szaz")
            try:
                menny    = float(menny_s)
                netto_ar = float(netto_ar_s)
                afa      = float(afa_s) if afa_s else 27.0
                brutto_ar    = round(netto_ar * (1 + afa / 100), 4)
                brutto_ertek = round(brutto_ar * menny, 2)
                netto_ertek  = round(netto_ar * menny, 2)
            except (ValueError, TypeError):
                continue
            if cikksz and menny > 0:
                records.append({
                    "kelt":          kelt,
                    "Cikkszám":      cikksz,
                    "Mennyiség":     menny,
                    "Nettó ár":      netto_ar,
                    "Bruttó ár":     brutto_ar,
                    "Nettó érték":   netto_ertek,
                    "Bruttó érték":  brutto_ertek,
                })
    return records


def _parse_keszlet(valasz_xml: str) -> list[dict]:
    records = []
    for elem_m in re.finditer(r"<elem>(.*?)</elem>", valasz_xml, re.DOTALL):
        elem = elem_m.group(1)
        cikksz = _tag(elem, "cikksz")
        if not cikksz:
            continue
        warehouses = {}
        total = 0.0
        for i in range(1, 7):
            v = _tag(elem, f"kiadhato{i}")
            qty = float(v) if v else 0.0
            warehouses[f"Raktár {i}"] = qty
            total += qty
        records.append({
            "Cikkszám": cikksz,
            "Készlet":  round(total, 2),
            **warehouses,
        })
    return records


def _parse_mozgas(valasz_xml: str, cikkszam_filter: str | None = None) -> list[dict]:
    records = []
    for elem_m in re.finditer(r"<elem>(.*?)</elem>", valasz_xml, re.DOTALL):
        elem = elem_m.group(1)
        fej_m = re.search(r"<fej>(.*?)</fej>", elem, re.DOTALL)
        if not fej_m:
            continue
        fej   = fej_m.group(1)
        kelt  = _tag(fej, "kelt")
        irany = _tag(fej, "irany")
        mozgas = _tag(fej, "mozgas")
        for tet_m in re.finditer(r"<tetel>(.*?)</tetel>", elem, re.DOTALL):
            t = tet_m.group(1)
            cikksz = _tag(t, "cikksz")
            if cikkszam_filter and cikksz != cikkszam_filter:
                continue
            menny_s = _tag(t, "menny")
            try:
                menny = float(menny_s)
            except (ValueError, TypeError):
                continue
            if not cikksz or menny == 0:
                continue
            records.append({
                "kelt":        kelt,
                "Cikkszám":    cikksz,
                "Irány":       irany,
                "Mozgástípus": mozgas,
                "Mennyiség":   abs(menny),
            })
    return records


# ── Public API ────────────────────────────────────────────────────────────────

def get_sales(start_date: str, end_date: str, cikkszam: str | None = None,
              limit: int = 200, force_refresh: bool = False) -> pd.DataFrame:
    """
    Fetch outgoing invoice line items (kimeno_szamla).
    Reads from Supabase first (fast), falls back to direct SOAP if unavailable.

    Args:
        start_date:    'YYYY.MM.DD'
        end_date:      'YYYY.MM.DD'
        cikkszam:      optional product code filter; None = all products
        limit:         page size (default 200, used for SOAP fallback only)
        force_refresh: bypass cache and re-fetch from API

    Returns:
        DataFrame with columns:
            kelt (datetime), Cikkszám (str),
            Mennyiség (float), Nettó ár (float), Bruttó ár (float),
            Nettó érték (float), Bruttó érték (float)
    """
    # Try Supabase first (unless force_refresh is set)
    if _USE_SUPABASE and not force_refresh:
        df = _supabase_get_sales(start_date, end_date, cikkszam)
        if df is not None:
            return df

    # If force_refresh with Supabase, trigger sync then read
    if _USE_SUPABASE and force_refresh:
        _trigger_sync_background("kimeno_szamla", {
            "start_date": start_date, "end_date": end_date, "cikkszam": cikkszam
        })
        # Still try to read current data from Supabase
        df = _supabase_get_sales(start_date, end_date, cikkszam)
        if df is not None:
            return df

    # Fallback: direct SOAP call
    cache_file = _cache_path("kimeno_szamla", start_date, end_date, cikkszam)

    if not force_refresh and _cache_is_fresh(cache_file):
        cached = _load_cache(cache_file)
        if cached is not None:
            return cached

    try:
        all_records: list[dict] = []
        page = 0
        while True:
            leker_xml = _build_leker(start_date, end_date, cikkszam, page, limit)
            raw = _post_soap("kimeno_szamla", leker_xml)
            valasz = _extract_valasz(raw)
            if not valasz:
                break
            raw_elem_count = len(re.findall(r"<elem>", valasz))
            page_records = _parse_tetelek(valasz, cikkszam_filter=cikkszam)
            all_records.extend(page_records)
            if raw_elem_count < limit:
                break
            page += 1

        if not all_records:
            return pd.DataFrame(
                columns=["kelt", "Cikkszám", "Mennyiség",
                         "Nettó ár", "Bruttó ár", "Nettó érték", "Bruttó érték"]
            )

        df = pd.DataFrame(all_records)
        df["kelt"] = pd.to_datetime(df["kelt"], format="%Y.%m.%d", errors="coerce")
        _save_cache(df, cache_file)
        return df

    except requests.RequestException:
        stale = _load_cache(cache_file)
        if stale is not None:
            warnings.warn("Tharanis API elérhetetlen, gyorsítótárazott adat használata.")
            return stale
        raise


def get_inventory(cikkszam: str | None = None, limit: int = 200) -> pd.DataFrame:
    """
    Fetch current inventory levels (keszlet).
    Reads from Supabase first, falls back to direct SOAP.

    Returns:
        DataFrame with columns:
            Cikkszám (str), Készlet (float), Raktár 1..6 (float)
    """
    # Try Supabase first
    if _USE_SUPABASE:
        df = _supabase_get_inventory(cikkszam)
        if df is not None:
            return df

    # Fallback: direct SOAP call
    all_records: list[dict] = []
    page = 0
    while True:
        leker_xml = _build_keszlet_leker(cikkszam, page, limit)
        raw = _post_soap("keszlet", leker_xml)
        valasz = _extract_valasz(raw)
        if not valasz:
            break
        page_records = _parse_keszlet(valasz)
        all_records.extend(page_records)
        if len(page_records) < limit:
            break
        page += 1

    if not all_records:
        return pd.DataFrame(
            columns=["Cikkszám", "Készlet",
                     "Raktár 1", "Raktár 2", "Raktár 3",
                     "Raktár 4", "Raktár 5", "Raktár 6"]
        )

    return pd.DataFrame(all_records)


def get_stock_movements(start_date: str, end_date: str, cikkszam: str | None = None,
                        limit: int = 200, force_refresh: bool = False) -> pd.DataFrame:
    """
    Fetch warehouse movement history (raktari_mozgas).
    Reads from Supabase first, falls back to direct SOAP.

    Returns:
        DataFrame with columns:
            kelt (datetime), Cikkszám (str), Irány (str: B/K),
            Mozgástípus (str), Mennyiség (float)
    """
    # Try Supabase first
    if _USE_SUPABASE and not force_refresh:
        df = _supabase_get_movements(start_date, end_date, cikkszam)
        if df is not None:
            return df

    if _USE_SUPABASE and force_refresh:
        _trigger_sync_background("raktari_mozgas", {
            "start_date": start_date, "end_date": end_date, "cikkszam": cikkszam
        })
        df = _supabase_get_movements(start_date, end_date, cikkszam)
        if df is not None:
            return df

    # Fallback: direct SOAP call
    cache_file = _cache_path("raktari_mozgas", start_date, end_date, cikkszam)

    if not force_refresh and _cache_is_fresh(cache_file):
        cached = _load_cache(cache_file)
        if cached is not None:
            return cached

    try:
        all_records: list[dict] = []
        page = 0
        while True:
            leker_xml = _build_mozgas_leker(start_date, end_date, cikkszam, page, limit)
            raw = _post_soap("raktari_mozgas", leker_xml)
            valasz = _extract_valasz(raw)
            if not valasz:
                break
            raw_elem_count = len(re.findall(r"<elem>", valasz))
            page_records = _parse_mozgas(valasz, cikkszam_filter=cikkszam)
            all_records.extend(page_records)
            if raw_elem_count < limit:
                break
            page += 1

        if not all_records:
            return pd.DataFrame(
                columns=["kelt", "Cikkszám", "Irány", "Mozgástípus", "Mennyiség"]
            )

        df = pd.DataFrame(all_records)
        df["kelt"] = pd.to_datetime(df["kelt"], format="%Y.%m.%d", errors="coerce")
        _save_cache(df, cache_file)
        return df

    except requests.RequestException:
        stale = _load_cache(cache_file)
        if stale is not None:
            warnings.warn("Tharanis API elérhetetlen, gyorsítótárazott adat használata.")
            return stale
        raise


# ── Disk cache (Parquet) — used as SOAP fallback only ─────────────────────

_CACHE_DIR = Path(__file__).parent / ".cache"


def _cache_path(entity: str, start_date: str, end_date: str,
                cikkszam: str | None) -> Path:
    raw = f"{entity}|{start_date}|{end_date}|{cikkszam or 'ALL'}"
    key = hashlib.md5(raw.encode()).hexdigest()
    return _CACHE_DIR / f"{entity}_{key}.parquet"


def _cache_is_fresh(path: Path, max_age_hours: float = 24.0) -> bool:
    if not path.exists():
        return False
    age = datetime.now(timezone.utc) - datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc
    )
    return age.total_seconds() < max_age_hours * 3600


def _save_cache(df: pd.DataFrame, path: Path) -> None:
    try:
        path.parent.mkdir(exist_ok=True)
        df.to_parquet(path, index=False)
    except Exception:
        pass


def _load_cache(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_parquet(path)
    except Exception:
        with contextlib.suppress(OSError):
            path.unlink()
        return None


def _cleanup_stale_cache(max_age_days: int = 7) -> None:
    if not _CACHE_DIR.exists():
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    for f in _CACHE_DIR.glob("*.parquet"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            with contextlib.suppress(OSError):
                f.unlink()


_cleanup_stale_cache()


# ── Quick connection test ────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import datetime, timedelta

    print("=" * 60)
    print("Tharanis V3 API -- connection test")
    print(f"Supabase mode: {'ON' if _USE_SUPABASE else 'OFF (direct SOAP)'}")
    print("=" * 60)

    today = datetime.now()
    end   = today.strftime("%Y.%m.%d")
    start = (today - timedelta(days=30)).strftime("%Y.%m.%d")

    print(f"Fetching kimeno_szamla: {start} to {end}")
    df = get_sales(start, end)

    if df.empty:
        print("No data returned.")
    else:
        print(f"Records fetched : {len(df)}")
        print(f"Unique products : {df['Cikkszám'].nunique()}")
        print(f"Total Bruttó ért: {df['Bruttó érték'].sum():,.0f} HUF")
        print()
        print("Sample (first 5 rows):")
        print(df.head().to_string(index=False))

    print()
    print("Fetching keszlet (inventory) for product 4633...")
    inv = get_inventory("4633")
    if inv.empty:
        print("No inventory data.")
    else:
        print(inv.to_string(index=False))

    print()
    print("Test complete.")
