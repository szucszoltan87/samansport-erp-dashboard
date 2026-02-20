"""
Tharanis API V3 Client
Calls the Tharanis ERP SOAP V3 endpoint (apiv3.php) using raw HTTP POST.
No WSDL required — envelope built manually from the confirmed working format.
"""

import os
import re
import html
import warnings
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore", message="Unverified HTTPS")

_API_URL    = os.getenv("THARANIS_API_URL",   "https://login.tharanis.hu/apiv3.php")
_UGYFELKOD  = os.getenv("THARANIS_UGYFELKOD", "7354")
_CEGKOD     = os.getenv("THARANIS_CEGKOD",    "ab")
_APIKULCS   = os.getenv("THARANIS_API_KEY",   "")

_HEADERS = {"Content-Type": "text/xml; charset=utf-8"}


# ── Low-level helpers ─────────────────────────────────────────────────────────

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
    """Build the inner <leker> XML payload for kimeno_szamla. Date format: YYYY.MM.DD"""
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
    """Build the inner <leker> XML payload for the keszlet (inventory) entity."""
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
    """Build the inner <leker> XML payload for raktari_mozgas. Date format: YYYY.MM.DD"""
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
    """Pull the inner XML out of the SOAP envelope and check for API errors."""
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
    """Parse all <elem>/<tetel> records from a valasz XML block.

    If cikkszam_filter is given, only line items with a matching cikksz are kept.
    This is necessary because the API cikksz filter operates at the invoice level —
    it returns whole invoices that contain the product, not just the matching rows.
    """
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
    """Parse <elem> records from a keszlet (inventory) valasz block.

    Each elem has cikksz and kiadhato1..6 (per-warehouse available qty).
    Returns one row per SKU with individual warehouse columns and a total.
    """
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
    """Parse <elem> records from a raktari_mozgas valasz block.

    Same invoice-level filter caveat as kimeno_szamla: the API returns whole
    movement documents; we filter tetelek client-side by cikksz.
    irany: B = beérkező (stock in), K = kiadó (stock out)
    """
    records = []
    for elem_m in re.finditer(r"<elem>(.*?)</elem>", valasz_xml, re.DOTALL):
        elem = elem_m.group(1)
        fej_m = re.search(r"<fej>(.*?)</fej>", elem, re.DOTALL)
        if not fej_m:
            continue
        fej   = fej_m.group(1)
        kelt  = _tag(fej, "kelt")
        irany = _tag(fej, "irany")   # B or K
        mozgas = _tag(fej, "mozgas") # movement type label

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
              limit: int = 200) -> pd.DataFrame:
    """
    Fetch outgoing invoice line items (kimeno_szamla) from Tharanis V3.

    Args:
        start_date: 'YYYY.MM.DD'
        end_date:   'YYYY.MM.DD'
        cikkszam:   optional product code filter; None = all products
        limit:      page size (default 200)

    Returns:
        DataFrame with columns:
            kelt (datetime), Cikkszám (str),
            Mennyiség (float), Nettó ár (float), Bruttó ár (float),
            Nettó érték (float), Bruttó érték (float)
    """
    all_records: list[dict] = []
    page = 0

    while True:
        leker_xml = _build_leker(start_date, end_date, cikkszam, page, limit)
        raw = _post_soap("kimeno_szamla", leker_xml)
        valasz = _extract_valasz(raw)

        if not valasz:
            break

        # Count raw <elem> tags to decide pagination — NOT filtered row count.
        # The API limit applies to invoices (elems); each invoice may have
        # many tetelek, and we filter tetelek client-side by cikksz.
        # Using filtered count would stop after page 0 since a page of 200
        # invoices typically yields far fewer rows for any single product.
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
    return df


def get_inventory(cikkszam: str | None = None, limit: int = 200) -> pd.DataFrame:
    """
    Fetch current inventory levels (keszlet) from Tharanis V3.

    Args:
        cikkszam: optional product code filter; None = all products
        limit:    page size (default 200)

    Returns:
        DataFrame with columns:
            Cikkszám (str), Készlet (float), Raktár 1..6 (float)
    """
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
                        limit: int = 200) -> pd.DataFrame:
    """
    Fetch warehouse movement history (raktari_mozgas) from Tharanis V3.

    Args:
        start_date: 'YYYY.MM.DD'
        end_date:   'YYYY.MM.DD'
        cikkszam:   optional product code filter; None = all products
        limit:      page size (default 200)

    Returns:
        DataFrame with columns:
            kelt (datetime), Cikkszám (str), Irány (str: B/K),
            Mozgástípus (str), Mennyiség (float)
        Irány: B = beérkező (stock in), K = kiadó (stock out)
    """
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
    return df


# ── Quick connection test ────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import datetime, timedelta

    print("=" * 60)
    print("Tharanis V3 API -- connection test")
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
        print(f"Unique products : {df['Cikkszam'].nunique()}")
        print(f"Total Brutto ert: {df['Brutto ertek'].sum():,.0f} HUF")
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
