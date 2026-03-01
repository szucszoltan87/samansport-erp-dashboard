"""
Tharanis ERP Dashboard – SamanSport
Modern analytics UI: Dashboard · Analitika
"""

import contextlib
import os
import random

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import tharanis_client as api

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE     = os.path.dirname(os.path.abspath(__file__))
_CSV_PATH = os.path.join(
    _HERE, "..", "..", "inventory_analysis_2020_2026",
    "rakbiz_analitika_012020_012026.csv"
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SamanSport ERP",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SVG Icon Library ───────────────────────────────────────────────────────────
_ICONS = {
    "grid":         '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
    "bar-chart":    '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>',
    "file-text":    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    "dollar-sign":  '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "package":      '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "tag":          '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
    "receipt":      '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1-2-1z"/><line x1="16" y1="8" x2="8" y2="8"/><line x1="16" y1="12" x2="8" y2="12"/>',
    "trending-up":  '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "warehouse":    '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "download":     '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "refresh-cw":   '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
    "activity":     '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "layers":       '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "info":         '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "database":     '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    "users":        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "calendar":     '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "filter":       '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "arrow-up-right":'<line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/>',
}

def svg(name: str, size: int = 16, color: str = "currentColor") -> str:
    p = _ICONS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{p}</svg>'
    )

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* ── Layout ── */
.main .block-container { padding: 2rem 2.5rem 2rem; max-width: 100%; }
.main { background-color: #f8fafc; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar – flush to top ── */
[data-testid="stSidebar"] > div:first-child {
    background: #ffffff;
    padding: 0;
    border-right: 1px solid #e5e7eb;
}
[data-testid="stSidebarUserContent"] {
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div > div:first-child {
    padding-top: 0 !important;
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p { color: #374151; }

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label {
    color: #9ca3af !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.11em !important;
    font-weight: 700 !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] .stDateInput label p,
[data-testid="stSidebar"] .stSelectbox label p {
    font-size: inherit !important;
    font-weight: inherit !important;
    color: inherit !important;
    text-transform: inherit !important;
    letter-spacing: inherit !important;
}
[data-testid="stSidebar"] .stDateInput input {
    background: #f9fafb !important;
    border-color: #e5e7eb !important;
    color: #111827 !important;
    border-radius: 8px !important;
    font-size: 0.72rem !important;
}

/* ── Sidebar nav + data load buttons ── */
[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #6b7280 !important;
    text-align: left !important;
    width: 100% !important;
    padding: 0.35rem 0.75rem !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    transition: background 0.12s, color 0.12s !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] div.stButton > button:hover {
    background: #f9fafb !important;
    color: #111827 !important;
    border: none !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: #eff6ff !important;
    color: #2563eb !important;
    font-weight: 600 !important;
    border: none !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: #f9fafb !important;
    color: #374151 !important;
    border: none !important;
    margin-top: 0.1rem !important;
    font-size: 0.78rem !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background: #f3f4f6 !important;
    border: none !important;
}
[data-testid="stSidebar"] .stSuccess {
    background: #f0fdf4 !important;
    color: #166534 !important;
    border: 1px solid #bbf7d0 !important;
    border-radius: 8px !important;
    font-size: 0.72rem !important;
    padding: 0.3rem 0.65rem !important;
}

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.625rem;
    margin-bottom: 0.75rem;
}
.kpi-card {
    background: white;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}
.kpi-left { flex: 1; min-width: 0; }
.kpi-label {
    font-size: 0.72rem;
    font-weight: 500;
    color: #6b7280;
    margin-bottom: 0.3rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-value {
    font-size: 1.35rem;
    font-weight: 800;
    color: #111827;
    line-height: 1.1;
    letter-spacing: -0.03em;
}
.kpi-sub {
    font-size: 0.7rem;
    font-weight: 500;
    color: #9ca3af;
    margin-top: 0.25rem;
}
.kpi-icon-box {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-left: 0.625rem;
}

/* ── Section card ── */
.section-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    padding: 1.5rem 1.5rem 1rem;
    margin-bottom: 1.25rem;
}
.section-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin-bottom: 0.2rem;
}
.section-sub {
    font-size: 0.78rem;
    color: #9ca3af;
    margin-bottom: 0.875rem;
}

/* ── Page header ── */
.page-hdr { margin-bottom: 1.5rem; }
.page-hdr-title {
    font-size: 1.625rem;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.03em;
}
.page-hdr-sub {
    font-size: 0.875rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f3f4f6;
    border-radius: 10px;
    padding: 0.25rem;
    gap: 0.15rem;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.4rem 1.1rem;
    font-size: 0.85rem;
    font-weight: 500;
    color: #6b7280;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #111827 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem; }

/* ── st.metric ── */
[data-testid="stMetricValue"] {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 600 !important;
}

/* ── Radio controls ── */
.stRadio > label {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}
.stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
}
div[role="radiogroup"] { gap: 0.2rem !important; }

/* ── Selectbox (main area) ── */
.stSelectbox div[data-baseweb="select"] > div {
    background: #f9fafb !important;
    border-color: #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    color: #111827 !important;
}
.stSelectbox > label {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3.5rem 2rem;
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}
.empty-icon { margin: 0 auto 1rem; display: flex; justify-content: center; }
.empty-title { font-size: 1rem; font-weight: 700; color: #374151; }
.empty-sub { font-size: 0.85rem; color: #9ca3af; margin-top: 0.4rem; line-height: 1.6; }

/* ── Badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.55rem;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    white-space: nowrap;
}
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-orange { background: #fff7ed; color: #c2410c; }
.badge-yellow { background: #fef9c3; color: #854d0e; }
.badge-green  { background: #f0fdf4; color: #166534; }
.badge-gray   { background: #f3f4f6; color: #6b7280; }
.badge-blue   { background: #eff6ff; color: #1d4ed8; }

/* ── Risk table ── */
.risk-table { width: 100%; border-collapse: collapse; font-size: 0.84rem; }
.risk-table th {
    text-align: left;
    padding: 0.45rem 0.75rem;
    font-size: 0.68rem;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    border-bottom: 1px solid #f1f5f9;
}
.risk-table td {
    padding: 0.55rem 0.75rem;
    border-bottom: 1px solid #f9fafb;
    color: #374151;
    vertical-align: middle;
}
.risk-table tr:last-child td { border-bottom: none; }
.risk-table tr:hover td { background: #f9fafb; }

/* ── Selectbox dropdown – widen + horizontal scroll for long product names ── */
/* Target only the menu inside popovers, NOT the datepicker calendar popover */
[data-baseweb="menu"] {
    min-width: min(720px, 90vw) !important;
    overflow-x: auto !important;
}
[data-baseweb="menu"] [role="option"] {
    white-space: nowrap !important;
}

/* ── Main area primary button (Betöltés) – blue, compact ── */
.main div.stButton > button[kind="primary"] {
    background: #2563eb !important;
    border-color: #2563eb !important;
    color: white !important;
    padding: 0.28rem 0.9rem !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    min-height: 0 !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(37,99,235,0.25) !important;
}
.main div.stButton > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
}

/* ── Misc ── */
.hline { height: 1px; background: #f1f5f9; margin: 1.25rem 0; }
.stDownloadButton > button {
    background: #f9fafb !important;
    border: 1px solid #e5e7eb !important;
    color: #374151 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: #f3f4f6 !important;
    border-color: #d1d5db !important;
}

/* ── Info banner ── */
.info-banner {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.75rem 1rem;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    font-size: 0.84rem;
    color: #1d4ed8;
    margin-bottom: 1rem;
}

/* ── Professional loading overlay ── */
@keyframes spinRing {
    0%   { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
@keyframes dashGrow {
    0%   { stroke-dasharray: 1 150; stroke-dashoffset: 0; }
    50%  { stroke-dasharray: 90 150; stroke-dashoffset: -35; }
    100% { stroke-dasharray: 90 150; stroke-dashoffset: -125; }
}
.load-overlay {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: rgba(248, 250, 252, 0.97);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}
.load-spinner-wrap {
    position: relative;
    width: 68px;
    height: 68px;
}
.load-ring-svg  { animation: spinRing 2s linear infinite; }
.load-ring-arc  { animation: dashGrow 1.5s ease-in-out infinite; }
.load-icon-center {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1.6rem;
    line-height: 1;
}
.load-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1e40af;
    text-align: center;
    letter-spacing: -0.01em;
}
.load-warn {
    font-size: 0.82rem;
    color: #374151;
    text-align: center;
    max-width: 380px;
    line-height: 1.6;
    padding: 0.65rem 1.1rem;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
ALL_PRODUCTS_LABEL = "— Összes termék —"
ALL_PRODUCTS_CODE  = "__ALL__"
PERIOD_OPTIONS = ["Havi", "Heti", "Napi"]

METRIC_CFG = {
    "Bruttó forgalom":  ("Bruttó érték", "sum",   "HUF", "Bruttó forgalom (HUF)"),
    "Nettó forgalom":   ("Nettó érték",  "sum",   "HUF", "Nettó forgalom (HUF)"),
    "Mennyiség":        ("Mennyiség",    "sum",   "db",  "Mennyiség (db)"),
    "Átl. bruttó ár":   ("Bruttó ár",    "mean",  "HUF", "Átl. bruttó ár (HUF)"),
    "Átl. nettó ár":    ("Nettó ár",     "mean",  "HUF", "Átl. nettó ár (HUF)"),
    "Tranzakciók":      ("Mennyiség",    "count", "db",  "Tranzakciók száma"),
}

C = {
    "blue":   "#2563eb",   # primary accent (was teal)
    "teal":   "#2563eb",   # alias kept for chart references
    "indigo": "#4f46e5",
    "green":  "#10b981",
    "red":    "#ef4444",
    "orange": "#f59e0b",
    "purple": "#8b5cf6",
    "slate":  "#64748b",
}

# ── Professional loading overlay ──────────────────────────────────────────────
# Center icon rotates randomly between inventory-themed choices each load
_LOADER_ICONS = ["📦", "🗂️", "📊", "🏷️", "🔄"]

@contextlib.contextmanager
def funny_loader(label: str = "Adatok betöltése...", warn: str = ""):
    icon = random.choice(_LOADER_ICONS)
    warn_html = f'<div class="load-warn">{warn}</div>' if warn else ""
    ph = st.empty()
    ph.markdown(
        f'<div class="load-overlay">'
        f'  <div class="load-spinner-wrap">'
        f'    <svg class="load-ring-svg" width="68" height="68" viewBox="0 0 68 68"'
        f'         xmlns="http://www.w3.org/2000/svg">'
        f'      <circle cx="34" cy="34" r="28" fill="none"'
        f'              stroke="#dbeafe" stroke-width="5"/>'
        f'      <circle class="load-ring-arc" cx="34" cy="34" r="28" fill="none"'
        f'              stroke="#2563eb" stroke-width="5" stroke-linecap="round"'
        f'              stroke-dasharray="1 175" stroke-dashoffset="0"/>'
        f'    </svg>'
        f'    <div class="load-icon-center">{icon}</div>'
        f'  </div>'
        f'  <div class="load-title">{label}</div>'
        f'  {warn_html}'
        f'</div>',
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        ph.empty()


# ── Product master ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Termék lista betöltése…")
def load_product_master() -> pd.DataFrame:
    if not os.path.exists(_CSV_PATH):
        return pd.DataFrame(columns=["Cikkszám", "Cikknév"])
    df = pd.read_csv(
        _CSV_PATH, usecols=[9, 10], dtype=str,
        encoding="utf-8-sig", on_bad_lines="skip",
    )
    df.columns = ["Cikkszám", "Cikknév"]
    return (
        df.dropna(subset=["Cikkszám", "Cikknév"])
        .drop_duplicates(subset=["Cikkszám"])
        .sort_values("Cikknév")
        .reset_index(drop=True)
    )

# ── Session state ──────────────────────────────────────────────────────────────
for _k, _v in [
    ("page",              "dashboard"),
    ("sales_df",          None),
    ("mozgas_df",         None),
    ("last_query",        {}),
    ("last_mozgas_query", {}),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Cached API wrappers (Tier 1: in-memory, shared across sessions) ──────────

@st.cache_data(ttl=timedelta(hours=24), show_spinner=False)
def _cached_get_sales(start_str: str, end_str: str,
                      cikkszam: str | None) -> pd.DataFrame | None:
    """In-memory cache (24h TTL) backed by Parquet disk cache in tharanis_client."""
    return api.get_sales(start_str, end_str, cikkszam)


@st.cache_data(ttl=timedelta(hours=24), show_spinner=False)
def _cached_get_movements(start_str: str, end_str: str,
                          cikkszam: str | None) -> pd.DataFrame | None:
    """In-memory cache (24h TTL) backed by Parquet disk cache in tharanis_client."""
    return api.get_stock_movements(start_str, end_str, cikkszam)


# ── Helpers ────────────────────────────────────────────────────────────────────
def period_key(series: pd.Series, period: str) -> pd.Series:
    if period == "Havi":
        return series.dt.to_period("M").astype(str)
    if period == "Heti":
        return series.dt.to_period("W").astype(str)
    return series.dt.strftime("%Y-%m-%d")


def find_sku_col(df: pd.DataFrame):
    for c in ["Cikkszám", "cikkszam", "SKU", "sku"]:
        if c in df.columns:
            return c
    return None


def find_name_col(df: pd.DataFrame):
    for c in ["Cikknév", "cikknev", "Megnevezés"]:
        if c in df.columns:
            return c
    return None


def kpi_card(label: str, value: str, icon_name: str,
             icon_bg: str = "#eff6ff", icon_color: str = "#2563eb",
             sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-left">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{sub_html}'
        f'</div>'
        f'<div class="kpi-icon-box" style="background:{icon_bg};">'
        f'{svg(icon_name, 16, icon_color)}'
        f'</div>'
        f'</div>'
    )


def kpi_grid(*cards, cols: int = 4) -> None:
    st.markdown(
        f'<div class="kpi-grid" style="grid-template-columns:repeat({cols},1fr);">'
        + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def section_header(title: str, sub: str = "", icon_name: str = "") -> None:
    icon_html = (
        f'<span style="display:inline-flex;align-items:center;">'
        f'{svg(icon_name, 15, "#2563eb")}</span>'
        if icon_name else ""
    )
    sub_html = f'<div class="section-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="section-title">{icon_html}{title}</div>{sub_html}',
        unsafe_allow_html=True,
    )


def page_header(title: str, sub: str = "") -> None:
    sub_html = f'<div class="page-hdr-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="page-hdr"><div class="page-hdr-title">{title}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def empty_state(icon_name: str, title: str, sub: str) -> None:
    st.markdown(
        f'<div class="empty-state">'
        f'<div class="empty-icon">{svg(icon_name, 40, "#d1d5db")}</div>'
        f'<div class="empty-title">{title}</div>'
        f'<div class="empty-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def info_banner(text: str, icon_name: str = "info") -> None:
    st.markdown(
        f'<div class="info-banner">{svg(icon_name, 15, "#2563eb")}{text}</div>',
        unsafe_allow_html=True,
    )


def chart_style(fig: go.Figure, height: int = 380, title: str = "") -> None:
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#374151", family="Inter"), x=0) if title else dict(text=""),
        paper_bgcolor="white",
        plot_bgcolor="#f9fafb",
        height=height,
        margin=dict(l=0, r=0, t=40 if title else 10, b=0),
        font=dict(color="#374151", size=12, family="Inter"),
        xaxis=dict(
            gridcolor="#f1f5f9", linecolor="#e5e7eb",
            tickfont=dict(color="#9ca3af", size=11), tickangle=-30,
        ),
        yaxis=dict(
            gridcolor="#f1f5f9", linecolor="#e5e7eb",
            tickfont=dict(color="#9ca3af", size=11), zeroline=False,
        ),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=13, family="Inter", color="#374151"), bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def hbar_chart(labels, values, color: str, height: int = 300) -> None:
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=color, opacity=0.85),
        hovertemplate="%{y}<br><b>%{x:,.0f}</b><extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="white", plot_bgcolor="#f9fafb",
        height=height, margin=dict(l=0, r=16, t=0, b=0),
        font=dict(color="#374151", size=11, family="Inter"),
        xaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#9ca3af", size=10)),
        yaxis=dict(gridcolor="#f1f5f9", tickfont=dict(color="#374151", size=10), automargin=True),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Fetch helpers ──────────────────────────────────────────────────────────────
def fetch_sales(cikkszam, start, end, force_refresh=False):
    start_str = start.strftime("%Y.%m.%d")
    end_str   = end.strftime("%Y.%m.%d")
    try:
        if force_refresh:
            _cached_get_sales.clear()
            df = api.get_sales(start_str, end_str, cikkszam, force_refresh=True)
        else:
            df = _cached_get_sales(start_str, end_str, cikkszam)
        if df is None or df.empty:
            st.warning("Nincs értékesítési adat a megadott feltételekre.")
            return None
        return df
    except Exception as e:
        st.error(f"API hiba: {e}")
        return None


def fetch_movements(cikkszam, start, end, force_refresh=False):
    start_str = start.strftime("%Y.%m.%d")
    end_str   = end.strftime("%Y.%m.%d")
    try:
        if force_refresh:
            _cached_get_movements.clear()
            df = api.get_stock_movements(start_str, end_str, cikkszam, force_refresh=True)
        else:
            df = _cached_get_movements(start_str, end_str, cikkszam)
        if df is None or df.empty:
            st.warning("Nincs mozgásadat.")
            return None
        return df
    except Exception as e:
        st.error(f"API hiba: {e}")
        return None


def _load_warn(start, end) -> str:
    """Return a warning string for potentially slow loads, otherwise empty."""
    days = (end - start).days
    if days > 365 * 3:
        return (
            "Hosszú időhorizontot kértél – ez eltarthat egy kicsit. "
            "Nyújtózz egyet, vagy igyál meg egy kávét, mire visszajössz, kész lesz. ☕"
        )
    if days > 365 * 2:
        return (
            "2 évnél hosszabb időszakot kértél. "
            "Az adatok betöltése pár másodpercet vehet igénybe."
        )
    return ""


# ── Sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # ── Brand header – flush to the very top ──────────────────────────────
        st.markdown("""
        <div style="padding:0.65rem 1rem 0.45rem;margin-top:0;">
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <div style="width:26px;height:26px;background:#2563eb;border-radius:6px;
                            display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                    <svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24'
                         fill='none' stroke='white' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>
                        <polyline points='23 6 13.5 15.5 8.5 10.5 1 18'/>
                        <polyline points='17 6 23 6 23 12'/>
                    </svg>
                </div>
                <div>
                    <div style="font-size:0.85rem;font-weight:800;color:#111827;letter-spacing:-0.02em;line-height:1.2;">SamanSport</div>
                    <div style="font-size:0.56rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;">ERP Analytics</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────────────────────────────
        st.markdown(
            '<div style="padding:0.35rem 0 0.15rem;font-size:0.78rem;font-weight:700;'
            'color:#9ca3af;text-transform:uppercase;letter-spacing:0.11em;">Navigáció</div>',
            unsafe_allow_html=True,
        )

        pages = [
            ("dashboard", "grid",      "Dashboard"),
            ("analytics",  "bar-chart", "Analitika"),
        ]
        for page_id, _, label in pages:
            is_active = st.session_state.page == page_id
            if st.button(
                f"  {label}", key=f"nav_{page_id}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.page = page_id
                st.rerun()

        # ── Divider ──────────────────────────────────────────────────────────
        st.markdown('<div style="height:1px;background:#f3f4f6;margin:0.35rem 0;"></div>', unsafe_allow_html=True)

        # ── Date range ───────────────────────────────────────────────────────
        _today = datetime.now().date()
        _default_start = _today.replace(year=_today.year - 1)
        start_date = st.date_input(
            "Kezdő dátum", key="start_date",
            value=_default_start, max_value=_today,
        )
        end_date = st.date_input(
            "Záró dátum", key="end_date",
            value=_today, max_value=_today,
        )

        # ── Refresh data button ─────────────────────────────────────────
        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
        if st.button("🔄  Adatok frissítése", key="force_refresh_btn",
                     use_container_width=True, type="secondary"):
            _r_start = st.session_state.get("start_date", _default_start)
            _r_end   = st.session_state.get("end_date", _today)
            with st.spinner("Friss adatok letöltése az API-ból..."):
                _r_df = fetch_sales(None, _r_start, _r_end, force_refresh=True)
            if _r_df is not None:
                st.session_state.sales_df = _r_df
                st.session_state.last_query = {
                    "cikkszam": None,
                    "label":    ALL_PRODUCTS_LABEL,
                    "start":    _r_start,
                    "end":      _r_end,
                }
                st.session_state.mozgas_df = None
                st.session_state.last_mozgas_query = {}
                st.rerun()

        st.markdown(
            '<div style="position:fixed;bottom:1rem;left:0;width:16rem;text-align:center;'
            'font-size:0.6rem;color:#d1d5db;">Tharanis ERP  ·  SamanSport MVP</div>',
            unsafe_allow_html=True,
        )

    return start_date, end_date


# ── Dashboard page ─────────────────────────────────────────────────────────────
def render_dashboard():
    df   = st.session_state.sales_df
    meta = st.session_state.last_query or {}

    date_sub = (
        f"{meta.get('start', '')} – {meta.get('end', '')}"
        if meta.get("start") else ""
    )
    page_header(
        "Dashboard",
        f"Összes termék  ·  {date_sub}" if date_sub
        else "Töltse be az értékesítési adatokat a bal oldali panelből",
    )

    if df is None:
        empty_state(
            "database",
            "Nincs betöltött adat",
            "Nyissa meg az <b>Analitika</b> oldalt, válasszon terméket és időszakot,<br>"
            "majd kattintson a <b>Betöltése</b> gombra.",
        )
        return

    # ── KPI row ────────────────────────────────────────────────────────────────
    kpi_grid(
        kpi_card("Bruttó forgalom", f"{df['Bruttó érték'].sum():,.0f} HUF",
                 "dollar-sign", "#eff6ff", "#2563eb",
                 sub=f"{df['kelt'].dt.to_period('M').nunique()} aktív hónap"),
        kpi_card("Értékesített mennyiség", f"{df['Mennyiség'].sum():,.0f} db",
                 "package", "#fef9c3", "#d97706",
                 sub=f"Nettó: {df['Nettó érték'].sum():,.0f} HUF"),
        kpi_card("Átlagos bruttó ár", f"{df['Bruttó ár'].mean():,.0f} HUF",
                 "tag", "#faf5ff", "#7c3aed",
                 sub=f"Átl. nettó: {df['Nettó ár'].mean():,.0f} HUF"),
        kpi_card("Tranzakciók", f"{len(df):,}",
                 "receipt", "#fff1f2", "#e11d48",
                 sub=f"{df['kelt'].dt.year.nunique()} aktív év"),
    )

    # ── Period toggle for dashboard charts ────────────────────────────────────
    dash_period = st.radio(
        "Periódus", ["Éves", "Havi", "Heti", "Napi"],
        horizontal=True, key="dash_period", index=1,
    )
    _period_map = {"Éves": "Y", "Havi": "M", "Heti": "W", "Napi": "D"}
    df2 = df.copy()
    if dash_period == "Napi":
        df2["Periódus"] = df2["kelt"].dt.strftime("%Y-%m-%d")
    elif dash_period == "Heti":
        df2["Periódus"] = df2["kelt"].dt.to_period("W").astype(str)
    elif dash_period == "Éves":
        df2["Periódus"] = df2["kelt"].dt.to_period("Y").astype(str)
    else:
        df2["Periódus"] = df2["kelt"].dt.to_period("M").astype(str)

    # ── Revenue trend ──────────────────────────────────────────────────────────
    section_header("Bruttó forgalom", f"{dash_period} bontás  ·  Értékesítési trend az időszakra", "trending-up")
    monthly = df2.groupby("Periódus")["Bruttó érték"].sum().reset_index().sort_values("Periódus")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Periódus"], y=monthly["Bruttó érték"],
        mode="lines", name="Bruttó forgalom",
        line=dict(color=C["blue"], width=2.5),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.08)",
        hovertemplate="%{x}<br><b>%{y:,.0f} HUF</b><extra></extra>",
    ))
    chart_style(fig, height=260)

    # ── Quantities chart ──────────────────────────────────────────────────────
    section_header("Értékesített mennyiség", f"{dash_period} bontás", "activity")
    mq = df2.groupby("Periódus")["Mennyiség"].sum().reset_index().sort_values("Periódus")
    fig_q = go.Figure(go.Bar(
        x=mq["Periódus"], y=mq["Mennyiség"],
        marker=dict(color=C["indigo"], opacity=0.8),
        hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>",
    ))
    chart_style(fig_q, height=230)

    # ── Top 10 products ────────────────────────────────────────────────────────
    sc = find_sku_col(df)
    section_header("Top 10 termék", "Bruttó forgalom szerint", "bar-chart")
    if sc:
        total_revenue = df["Bruttó érték"].sum()
        grp = df.groupby(sc)["Bruttó érték"].sum().nlargest(10).reset_index()
        grp.columns = ["Cikkszám", "Forgalom"]
        nc = find_name_col(df)
        if nc:
            names = df[[sc, nc]].drop_duplicates().rename(columns={sc: "Cikkszám", nc: "Cikknév"})
            grp = grp.merge(names, on="Cikkszám", how="left")
            grp["Label"] = grp.apply(
                lambda r: f"{r['Cikknév'][:28]} ({r['Cikkszám']})" if pd.notna(r.get("Cikknév")) else str(r["Cikkszám"]),
                axis=1,
            )
        else:
            grp["Label"] = grp["Cikkszám"].astype(str)
        grp["Pct"] = (grp["Forgalom"] / total_revenue * 100) if total_revenue else 0
        # If name column wasn't in the grouped data, try the product master CSV
        if "Cikknév" not in grp.columns or grp["Cikknév"].isna().all():
            pm = load_product_master()
            if not pm.empty:
                grp = grp.drop(columns=["Cikknév"], errors="ignore")
                grp = grp.merge(
                    pm[["Cikkszám", "Cikknév"]].drop_duplicates(subset=["Cikkszám"]),
                    on="Cikkszám", how="left",
                )
                grp["Label"] = grp.apply(
                    lambda r: f"{r['Cikknév'][:28]} ({r['Cikkszám']})" if pd.notna(r.get("Cikknév")) else str(r["Cikkszám"]),
                    axis=1,
                )
        grp = grp.sort_values("Forgalom").reset_index(drop=True)

        max_val = grp["Forgalom"].max()
        fig = go.Figure(go.Bar(
            x=grp["Forgalom"], y=grp["Label"].tolist(), orientation="h",
            marker=dict(color=C["blue"], opacity=0.85),
            text=grp.apply(lambda r: f"  {r['Forgalom']:,.0f} Ft  ({r['Pct']:.1f}%)", axis=1),
            textposition="outside",
            textfont=dict(size=11, color="#374151"),
            hovertemplate="%{y}<br><b>%{x:,.0f} Ft</b><br>Arány: %{customdata:.1f}%<extra></extra>",
            customdata=grp["Pct"],
            cliponaxis=False,
        ))
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f9fafb",
            height=max(400, len(grp) * 42),
            margin=dict(l=0, r=20, t=0, b=30),
            font=dict(color="#374151", size=11, family="Inter"),
            xaxis=dict(range=[0, max_val * 1.35], gridcolor="#f1f5f9",
                       tickfont=dict(color="#9ca3af", size=10),
                       tickformat=",",
                       title=dict(text="Bruttó forgalom (HUF)", font=dict(size=11, color="#9ca3af"))),
            yaxis=dict(type="category", gridcolor="#f1f5f9",
                       tickfont=dict(color="#374151", size=10),
                       automargin=True, title=None),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Analytics – Sales view ─────────────────────────────────────────────────────
def _analytics_sales(load_triggered: bool = False):
    _today = datetime.now().date()
    start  = st.session_state.get("start_date", _today.replace(year=_today.year - 1))
    end    = st.session_state.get("end_date",   _today)

    # ── Pre-load: product selector (full-width) ───────────────────────────────
    products = load_product_master()
    prod_opts: dict = {ALL_PRODUCTS_LABEL: None}
    if not products.empty:
        # Source 1: CSV product master
        for _, r in products.iterrows():
            prod_opts[f"{r['Cikkszám']}  –  {r['Cikknév']}"] = r["Cikkszám"]
    elif st.session_state.get("_prod_opts_cache"):
        # Source 2: list cached from initial all-products load (survives filtered reloads)
        prod_opts = st.session_state["_prod_opts_cache"]
    elif st.session_state.sales_df is not None and (st.session_state.last_query or {}).get("cikkszam") is None:
        # Source 3: build fresh from sales_df only when it contains all-products data
        _pm = st.session_state.sales_df
        _sc = find_sku_col(_pm)
        _nc = find_name_col(_pm)
        if _sc:
            _rows = (
                _pm[[_sc] + ([_nc] if _nc else [])]
                .drop_duplicates(subset=[_sc])
                .dropna(subset=[_sc])
                .sort_values(_nc if _nc else _sc)
            )
            for _, r in _rows.iterrows():
                lbl = (
                    f"{r[_sc]}  –  {r[_nc]}"
                    if _nc and pd.notna(r.get(_nc))
                    else str(r[_sc])
                )
                prod_opts[lbl] = r[_sc]
            st.session_state["_prod_opts_cache"] = prod_opts  # cache for subsequent runs

    # ── Stable-ID selectbox ───────────────────────────────────────────────────
    # Store the SHORT cikkszam code (e.g. "4633") as the widget value instead of
    # the long label string.  Label strings differ between CSV / cache / API and
    # cause _an_sku not in _sku_opts → stale guard → visible-empty selectbox.
    _sku_opts: list = []
    _sku_label_map: dict = {}
    for _lbl, _sku in prod_opts.items():
        _code = _sku if _sku is not None else ALL_PRODUCTS_CODE
        _sku_opts.append(_code)
        _sku_label_map[_code] = _lbl

    # Resolve which SKU to highlight (prefer last explicit pick, then last loaded)
    _last_loaded_sku = (st.session_state.last_query or {}).get("cikkszam")
    _stored_sku      = st.session_state.get("_sel_sku")
    # _stored_sku may legitimately be ALL_PRODUCTS_CODE (non-falsy), so avoid `or`
    _target_sku = (
        _stored_sku if (_stored_sku is not None and _stored_sku in _sku_opts)
        else (_last_loaded_sku if _last_loaded_sku in _sku_opts else ALL_PRODUCTS_CODE)
    )
    _sel_sku_idx = _sku_opts.index(_target_sku)

    # Guard: delete stale key only – never assign to a widget key before render
    # (assigning raises StreamlitAPIException in Streamlit 1.29).
    if "_an_sku" in st.session_state and st.session_state["_an_sku"] not in _sku_opts:
        del st.session_state["_an_sku"]

    sel_sku   = st.selectbox(
        "Termék", _sku_opts,
        format_func=lambda c: _sku_label_map.get(c, c),
        index=_sel_sku_idx, key="_an_sku",
    )
    sel_label = _sku_label_map.get(sel_sku, ALL_PRODUCTS_LABEL)
    st.session_state["_sel_sku"]     = sel_sku
    st.session_state["_sel_product"] = sel_label  # keep for legacy references

    if load_triggered:
        cikkszam = None if sel_sku == ALL_PRODUCTS_CODE else sel_sku
        warn = _load_warn(start, end)
        with funny_loader("Értékesítési adatok betöltése...", warn):
            df_new = fetch_sales(cikkszam, start, end)
        if df_new is not None:
            st.session_state.sales_df = df_new
            st.session_state.last_query = {
                "cikkszam": cikkszam,
                "label":    sel_label,
                "start":    start,
                "end":      end,
            }
            st.session_state["_sel_sku"]     = sel_sku
            st.session_state["_sel_product"] = sel_label

    # ── Guard: nothing loaded yet ─────────────────────────────────────────────
    df   = st.session_state.sales_df
    meta = st.session_state.last_query or {}
    if df is None:
        st.markdown('<div style="height:0.75rem;"></div>', unsafe_allow_html=True)
        empty_state(
            "bar-chart",
            "Nincs betöltött adat",
            "Válasszon terméket a fenti listából, majd kattintson a <b>Betöltése</b> gombra.",
        )
        return

    # ── Optional in-page filter (only when all products were loaded) ──────────
    sc = find_sku_col(df)
    nc = find_name_col(df)
    loaded_cikkszam = meta.get("cikkszam")   # None → all products in memory
    display_label   = meta.get("label", "—")
    filter_sku      = loaded_cikkszam        # tracks currently-viewed SKU

    if loaded_cikkszam is None and sc:
        # All products loaded – let user drill into one without re-fetching
        sku_rows = (
            df[[sc] + ([nc] if nc else [])]
            .drop_duplicates(subset=[sc])
            .dropna(subset=[sc])
            .sort_values(sc)
        )
        sku_label_map: dict = {ALL_PRODUCTS_LABEL: None}
        for _, r in sku_rows.iterrows():
            lbl = (f"{r[sc]}  –  {r[nc]}" if nc and pd.notna(r.get(nc)) else str(r[sc]))
            sku_label_map[lbl] = r[sc]
        info_banner(
            f"Összes termék betöltve ({len(sku_label_map) - 1:,} db). "
            "Az alábbi szűrővel egy termékre szűkíthet újratöltés nélkül.",
            "filter",
        )
        inner_choice = st.selectbox(
            "Termék szűrő", list(sku_label_map.keys()), key="an_sku_filter",
        )
        inner_sku = sku_label_map[inner_choice]
        if inner_sku is not None:
            df            = df[df[sc] == inner_sku]
            display_label = inner_choice
            filter_sku    = inner_sku
    else:
        # Specific product loaded – just show a status line
        info_banner(
            f"Betöltve: {meta.get('label', '—')}  ·  "
            f"{meta.get('start', '')} – {meta.get('end', '')}  ·  {len(df):,} tranzakció",
            "database",
        )

    # ── Controls row ─────────────────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([4, 2, 2])
    with ctrl1:
        metric = st.radio("Mutató", list(METRIC_CFG.keys()), horizontal=True, key="an_metric")
    with ctrl2:
        period = st.radio("Periódus", PERIOD_OPTIONS, horizontal=True, key="an_period")
    with ctrl3:
        chart_type = st.radio("Diagram", ["Oszlop", "Vonal"], horizontal=True, key="an_chart")

    col_name, agg_fn, unit, ytitle = METRIC_CFG[metric]
    df2 = df.copy()
    df2["Periódus"] = period_key(df2["kelt"], period)
    grouped = df2.groupby("Periódus")[col_name].agg(agg_fn).reset_index().sort_values("Periódus")

    # ── Chart ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header(
        metric,
        f"{display_label}  ·  {meta.get('start', '')} – {meta.get('end', '')}",
        "bar-chart",
    )
    fig = go.Figure()
    ht  = f"%{{x}}<br><b>%{{y:,.0f}} {unit}</b><extra></extra>"
    if chart_type == "Oszlop":
        fig.add_trace(go.Bar(
            x=grouped["Periódus"], y=grouped[col_name],
            marker_color=C["blue"], name=metric, hovertemplate=ht,
        ))
    else:
        fig.add_trace(go.Scatter(
            x=grouped["Periódus"], y=grouped[col_name],
            mode="lines+markers", name=metric,
            line=dict(color=C["blue"], width=2.5),
            marker=dict(size=6, color=C["blue"]),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.07)",
            hovertemplate=ht,
        ))
    fig.update_layout(yaxis_title=ytitle)
    chart_style(fig, height=380)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Summary metrics (always reflect current filter/product) ──────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("Összes mennyiség",  f"{df['Mennyiség'].sum():,.0f} db")
    with m2: st.metric("Bruttó forgalom",   f"{df['Bruttó érték'].sum():,.0f} HUF")
    with m3: st.metric("Nettó forgalom",    f"{df['Nettó érték'].sum():,.0f} HUF")
    with m4: st.metric("Átl. bruttó ár",    f"{df['Bruttó ár'].mean():,.0f} HUF")
    with m5: st.metric("Aktív periódusok",  f"{grouped['Periódus'].nunique()}")

    # ── Full data table ───────────────────────────────────────────────────────
    st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
    section_header(
        "Teljes értékesítési adatok",
        f"{display_label}  ·  {len(df):,} tranzakció",
        "file-text",
    )
    full = df.copy()
    full["kelt"] = full["kelt"].dt.strftime("%Y-%m-%d")
    st.dataframe(full.reset_index(drop=True), use_container_width=True, height=400)
    fn_sku = filter_sku.replace("/", "-") if filter_sku else "osszes"
    csv_bytes = full.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSV letöltése",
        data=csv_bytes,
        file_name=f"ertekesites_{fn_sku}_{meta.get('start', '')}.csv",
        mime="text/csv",
    )


# ── Analytics – Movements view (incl. load button) ────────────────────────────
def _analytics_movements():
    _today = datetime.now().date()
    start  = st.session_state.get("start_date", _today.replace(year=_today.year - 1))
    end    = st.session_state.get("end_date",   _today)

    # ── Load button ───────────────────────────────────────────────────────────
    col_btn, col_status = st.columns([2, 3])
    with col_btn:
        if st.button("  Mozgástörténet betöltése", key="load_mozgas_an", type="secondary"):
            warn = _load_warn(start, end)
            with funny_loader("Mozgástörténet betöltése...", warn):
                mdf = fetch_movements(None, start, end)
            if mdf is not None:
                st.session_state.mozgas_df = mdf
                st.session_state.last_mozgas_query = {
                    "cikkszam": None, "label": ALL_PRODUCTS_LABEL,
                    "start": start, "end": end,
                }
    with col_status:
        pass

    mdf = st.session_state.mozgas_df
    if mdf is None:
        st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
        empty_state("activity", "Nincs mozgástörténet", "Kattints a gombra a mozgásadatok betöltéséhez.")
        return

    meta_m = st.session_state.last_mozgas_query or {}

    cp, cc = st.columns([2, 2])
    with cp: period_m = st.radio("Periódus", PERIOD_OPTIONS, horizontal=True, key="mz_period")
    with cc: chart_m  = st.radio("Diagram",  ["Oszlop", "Vonal"], horizontal=True, key="mz_chart")

    mdf2  = mdf.copy()
    mdf2["Periódus"] = period_key(mdf2["kelt"], period_m)
    be_map = mdf2[mdf2["Irány"] == "B"].groupby("Periódus")["Mennyiség"].sum().to_dict()
    ki_map = mdf2[mdf2["Irány"] == "K"].groupby("Periódus")["Mennyiség"].sum().to_dict()
    all_p  = sorted(set(be_map) | set(ki_map))
    be_v   = [be_map.get(p, 0) for p in all_p]
    ki_v   = [ki_map.get(p, 0) for p in all_p]

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    section_header(
        "Raktári mozgások",
        f"{meta_m.get('start', '')} – {meta_m.get('end', '')}",
        "activity",
    )
    fig = go.Figure()
    if chart_m == "Oszlop":
        fig.add_trace(go.Bar(x=all_p, y=be_v, name="Beérkező", marker_color=C["blue"],
                             hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>"))
        fig.add_trace(go.Bar(x=all_p, y=ki_v, name="Kiadó",    marker_color=C["orange"],
                             hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>"))
        fig.update_layout(barmode="group")
    else:
        fig.add_trace(go.Scatter(x=all_p, y=be_v, name="Beérkező",
                                 mode="lines+markers", line=dict(color=C["blue"], width=2.5),
                                 marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=all_p, y=ki_v, name="Kiadó",
                                 mode="lines+markers", line=dict(color=C["orange"], width=2.5),
                                 marker=dict(size=6)))
    chart_style(fig, height=380)
    st.markdown('</div>', unsafe_allow_html=True)

    total_be = mdf[mdf["Irány"] == "B"]["Mennyiség"].sum()
    total_ki = mdf[mdf["Irány"] == "K"]["Mennyiség"].sum()
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("Összes beérkező", f"{total_be:,.0f} db")
    with s2: st.metric("Összes kiadó",    f"{total_ki:,.0f} db")
    with s3: st.metric("Nettó mozgás",    f"{total_be - total_ki:+,.0f} db")
    with s4: st.metric("Mozgástípusok",   f"{mdf['Mozgástípus'].nunique()}")

    st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
    with st.expander("Mozgás adattáblázat"):
        show_m = mdf.copy()
        show_m["kelt"] = show_m["kelt"].dt.strftime("%Y-%m-%d")
        st.dataframe(show_m.reset_index(drop=True), use_container_width=True, height=300)
        csv = show_m.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "CSV letöltése",
            data=csv,
            file_name=f"mozgas_osszes_{meta_m.get('start','')}.csv",
            mime="text/csv",
        )


# ── Analytics page ─────────────────────────────────────────────────────────────
def render_analytics():
    meta = st.session_state.last_query or {}

    # Page header + top-right load button on the same row
    hdr_col, btn_col = st.columns([7, 1])
    with hdr_col:
        page_header("Analitika", meta.get("label", "—"))
    with btn_col:
        st.write("")
        load_triggered = st.button(
            "Betöltés", key="an_load_top", type="primary", use_container_width=True,
        )

    view = st.radio(
        "Adatnézet",
        ["Értékesítés", "Mozgástörténet"],
        horizontal=True,
        key="an_view",
    )

    st.markdown('<div class="hline"></div>', unsafe_allow_html=True)

    if view == "Értékesítés":
        _analytics_sales(load_triggered=load_triggered)
    else:
        _analytics_movements()



# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    load_product_master()   # warm cache
    render_sidebar()

    # ── Auto-load / reload when sidebar dates change ─────────────────────────
    _today  = datetime.now().date()
    _cur_start = st.session_state.get("start_date", _today.replace(year=_today.year - 1))
    _cur_end   = st.session_state.get("end_date",   _today)
    _last      = st.session_state.last_query or {}
    _need_load = (
        st.session_state.sales_df is None
        or _last.get("start") != _cur_start
        or _last.get("end") != _cur_end
    )

    if _need_load:
        with funny_loader("Dashboard adatok betöltése...", _load_warn(_cur_start, _cur_end)):
            _df = fetch_sales(None, _cur_start, _cur_end)
        if _df is not None:
            st.session_state.sales_df   = _df
            st.session_state.last_query = {
                "cikkszam": None,
                "label":    ALL_PRODUCTS_LABEL,
                "start":    _cur_start,
                "end":      _cur_end,
            }
            # Reset movements since dates changed
            st.session_state.mozgas_df = None
            st.session_state.last_mozgas_query = {}
            # Cache product list so it survives later filtered loads
            _sc = find_sku_col(_df)
            _nc = find_name_col(_df)
            if _sc:
                _prows = (
                    _df[[_sc] + ([_nc] if _nc else [])]
                    .drop_duplicates(subset=[_sc])
                    .dropna(subset=[_sc])
                    .sort_values(_nc if _nc else _sc)
                )
                _cache: dict = {ALL_PRODUCTS_LABEL: None}
                for _, _r in _prows.iterrows():
                    _lbl = (
                        f"{_r[_sc]}  –  {_r[_nc]}"
                        if _nc and pd.notna(_r.get(_nc))
                        else str(_r[_sc])
                    )
                    _cache[_lbl] = _r[_sc]
                st.session_state["_prod_opts_cache"] = _cache

    page = st.session_state.page
    if page == "dashboard":
        render_dashboard()
    elif page == "analytics":
        render_analytics()


if __name__ == "__main__":
    main()
