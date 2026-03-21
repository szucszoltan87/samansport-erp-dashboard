"""
Configuration constants for SamanSport ERP Dashboard.
"""

import os

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE     = os.path.dirname(os.path.abspath(__file__))
CSV_PATH  = os.path.join(
    _HERE, "..", "..", "inventory_analysis_2020_2026",
    "rakbiz_analitika_012020_012026.csv"
)

# ── Product constants ─────────────────────────────────────────────────────────
ALL_PRODUCTS_LABEL = "— Összes termék —"
ALL_PRODUCTS_CODE  = "__ALL__"

# ── Analytics config ──────────────────────────────────────────────────────────
PERIOD_OPTIONS = ["Havi", "Heti", "Napi"]

METRIC_CFG = {
    "Bruttó forgalom":  ("Bruttó érték", "sum",   "HUF", "Bruttó forgalom (HUF)"),
    "Nettó forgalom":   ("Nettó érték",  "sum",   "HUF", "Nettó forgalom (HUF)"),
    "Mennyiség":        ("Mennyiség",    "sum",   "db",  "Mennyiség (db)"),
    "Átl. bruttó ár":   ("Bruttó ár",    "mean",  "HUF", "Átl. bruttó ár (HUF)"),
    "Átl. nettó ár":    ("Nettó ár",     "mean",  "HUF", "Átl. nettó ár (HUF)"),
    "Tranzakciók":      ("Mennyiség",    "count", "db",  "Tranzakciók száma"),
}
