"""
Local hydration script — loads historical data into Supabase by calling
the sync-entity Edge Function month by month.

Usage: python hydrate.py [start_year] [end_year]
       python hydrate.py 2010 2026
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from calendar import monthrange
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SYNC_URL = f"{SUPABASE_URL}/functions/v1/sync-entity"
HEADERS = {
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

DELAY_BETWEEN_CHUNKS = 2  # seconds


def sync_entity(entity: str, filters: dict) -> dict:
    try:
        resp = requests.post(SYNC_URL, headers=HEADERS, json={"entity": entity, "filters": filters}, timeout=180)
        if resp.status_code != 200:
            return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text[:200]}", "records": 0}
        try:
            return resp.json()
        except Exception:
            return {"status": "error", "error": f"Non-JSON response: {resp.text[:200]}", "records": 0}
    except requests.Timeout:
        return {"status": "error", "error": "Request timed out (180s)", "records": 0}
    except Exception as e:
        return {"status": "error", "error": str(e), "records": 0}


def hydrate_entity(entity: str, start_year: int, end_year: int):
    now = datetime.now()
    total_records = 0
    errors = 0

    for year in range(start_year, end_year + 1):
        max_month = now.month if year == now.year else 12
        for month in range(1, max_month + 1):
            if datetime(year, month, 1) > now:
                break

            last_day = monthrange(year, month)[1]
            start_date = f"{year}.{month:02d}.01"
            end_date = f"{year}.{month:02d}.{last_day:02d}"
            chunk = f"{year}-{month:02d}"

            result = sync_entity(entity, {"start_date": start_date, "end_date": end_date})
            records = result.get("records", 0)
            status = result.get("status", "unknown")
            total_records += records

            if status == "error":
                errors += 1
                print(f"  {chunk}  ERROR: {result.get('error', '?')}")
            elif status == "skipped":
                print(f"  {chunk}  skipped (fresh or already syncing)")
            else:
                print(f"  {chunk}  {records:>6} records")

            time.sleep(DELAY_BETWEEN_CHUNKS)

    return total_records, errors


def main():
    start_year = int(sys.argv[1]) if len(sys.argv) > 1 else 2010
    end_year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year

    print(f"Hydrating Supabase: {start_year} -> {end_year}")
    print(f"Endpoint: {SYNC_URL}")
    print()

    # 1. Products (no date dimension)
    print("=== Products (cikk) ===")
    result = sync_entity("cikk", {})
    print(f"  {result.get('status')}: {result.get('records', 0)} records")
    time.sleep(DELAY_BETWEEN_CHUNKS)

    # 2. Inventory (no date dimension)
    print()
    print("=== Inventory (keszlet) ===")
    result = sync_entity("keszlet", {})
    print(f"  {result.get('status')}: {result.get('records', 0)} records")
    time.sleep(DELAY_BETWEEN_CHUNKS)

    # 3. Sales (monthly chunks)
    print()
    print("=== Sales (kimeno_szamla) ===")
    sales_total, sales_err = hydrate_entity("kimeno_szamla", start_year, end_year)
    print(f"  Total: {sales_total} records, {sales_err} errors")

    # 4. Movements (monthly chunks)
    print()
    print("=== Movements (raktari_mozgas) ===")
    mov_total, mov_err = hydrate_entity("raktari_mozgas", start_year, end_year)
    print(f"  Total: {mov_total} records, {mov_err} errors")

    print()
    print("Hydration complete!")


if __name__ == "__main__":
    main()
