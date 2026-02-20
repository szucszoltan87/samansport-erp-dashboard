"""
Tharanis ERP Dashboard – SamanSport
Modern analytics UI: Dashboard · Analitika · Riport
"""

import os
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

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SamanSport ERP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* ── Main area ── */
.main .block-container {
    padding: 1.75rem 2.5rem 2rem 2.5rem;
    max-width: 100%;
}
.main { background-color: #f1f5f9; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar base ── */
[data-testid="stSidebar"] > div:first-child {
    background: #0f172a;
    padding: 0;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p { color: #94a3b8; }

/* ── Sidebar inputs ── */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] .stSelectbox label {
    color: #475569 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
[data-testid="stSidebar"] .stDateInput input {
    background: #1e293b !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stSelectbox svg { fill: #64748b !important; }
[data-testid="stSidebar"] .stSuccess {
    background: #064e3b !important;
    color: #6ee7b7 !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
}

/* ── Nav buttons ── */
[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #64748b !important;
    text-align: left !important;
    width: 100% !important;
    padding: 0.55rem 0.9rem !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    transition: all 0.12s !important;
    justify-content: flex-start !important;
    letter-spacing: 0 !important;
}
[data-testid="stSidebar"] div.stButton > button:hover {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border: none !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.4) !important;
}
/* Load buttons inside sidebar */
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: #1e293b !important;
    color: #93c5fd !important;
    border: 1px solid #334155 !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background: #2563eb !important;
    color: white !important;
    border-color: #2563eb !important;
}

/* ── KPI grid ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 1.25rem 1.5rem 1.1rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.blue::after   { background: linear-gradient(90deg,#2563eb,#60a5fa); }
.kpi-card.green::after  { background: linear-gradient(90deg,#10b981,#34d399); }
.kpi-card.orange::after { background: linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-card.purple::after { background: linear-gradient(90deg,#8b5cf6,#a78bfa); }
.kpi-card.red::after    { background: linear-gradient(90deg,#ef4444,#f87171); }
.kpi-icon { font-size: 1.3rem; margin-bottom: 0.55rem; opacity: 0.85; }
.kpi-value {
    font-size: 1.65rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    letter-spacing: -0.03em;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}
.kpi-sub {
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 0.2rem;
}

/* ── Section / chart card ── */
.section-card {
    background: white;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    padding: 1.5rem 1.5rem 0.75rem;
    margin-bottom: 1.25rem;
}
.section-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
}
.section-sub {
    font-size: 0.78rem;
    color: #94a3b8;
    margin-top: 0.15rem;
    margin-bottom: 0.75rem;
}

/* ── Page header ── */
.page-hdr { margin-bottom: 1.75rem; }
.page-hdr-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.2;
}
.page-hdr-sub {
    font-size: 0.875rem;
    color: #64748b;
    margin-top: 0.3rem;
}

/* ── Badge ── */
.badge {
    display: inline-flex; align-items: center;
    padding: 0.18rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-green  { background: #d1fae5; color: #065f46; }
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-gray   { background: #f1f5f9; color: #475569; }
.badge-orange { background: #fef3c7; color: #92400e; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
}
.empty-icon { font-size: 2.5rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.05rem; font-weight: 700; color: #334155; }
.empty-sub { font-size: 0.85rem; color: #94a3b8; margin-top: 0.4rem; line-height: 1.5; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 10px;
    padding: 0.25rem;
    gap: 0.2rem;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 0.4rem 1.1rem;
    font-size: 0.85rem; font-weight: 500; color: #64748b;
    background: transparent; border: none;
}
.stTabs [aria-selected="true"] {
    background: white !important; color: #0f172a !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem; }

/* ── st.metric override ── */
[data-testid="stMetricValue"] {
    font-size: 1.4rem !important; font-weight: 800 !important; color: #0f172a !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important; color: #94a3b8 !important;
    text-transform: uppercase !important; letter-spacing: 0.07em !important; font-weight: 600 !important;
}

/* ── Radio controls ── */
.stRadio label { font-size: 0.85rem !important; font-weight: 500 !important; }
.stRadio [data-testid="stMarkdownContainer"] p { font-size: 0.85rem !important; }
div[role="radiogroup"] { gap: 0.25rem !important; }

/* ── Divider ── */
.hline { height: 1px; background: #e2e8f0; margin: 1.25rem 0; }

/* ── Download button ── */
.stDownloadButton > button {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    color: #374151 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────

ALL_PRODUCTS_LABEL = "— Összes termék (cégszintű) —"
ALL_PRODUCTS_CODE  = "__ALL__"
PERIOD_OPTIONS = ["Havi", "Heti", "Napi"]

METRIC_CFG = {
    "Bruttó forgalom":   ("Bruttó érték", "sum",   "HUF", "Bruttó forgalom (HUF)"),
    "Nettó forgalom":    ("Nettó érték",  "sum",   "HUF", "Nettó forgalom (HUF)"),
    "Mennyiség":         ("Mennyiség",    "sum",   "db",  "Mennyiség (db)"),
    "Átl. bruttó ár":    ("Bruttó ár",    "mean",  "HUF", "Átlag bruttó ár (HUF)"),
    "Átl. nettó ár":     ("Nettó ár",     "mean",  "HUF", "Átlag nettó ár (HUF)"),
    "Tranzakciók száma": ("Mennyiség",    "count", "db",  "Tranzakciók száma"),
}

C = {  # chart color palette
    "blue":   "#2563eb",
    "green":  "#10b981",
    "red":    "#ef4444",
    "orange": "#f59e0b",
    "purple": "#8b5cf6",
    "slate":  "#64748b",
    "sky":    "#38bdf8",
}


# ── Product master ────────────────────────────────────────────────────────────

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


# ── Session state ─────────────────────────────────────────────────────────────

for _k, _v in [
    ("page",            "dashboard"),
    ("sales_df",        None),
    ("inv_df",          None),
    ("mozgas_df",       None),
    ("last_query",      {}),
    ("last_inv_query",  {}),
    ("last_mozgas_query", {}),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Helpers ───────────────────────────────────────────────────────────────────

def period_key(series: pd.Series, period: str) -> pd.Series:
    if period == "Havi":
        return series.dt.to_period("M").astype(str)
    if period == "Heti":
        return series.dt.to_period("W").astype(str)
    return series.dt.strftime("%Y-%m-%d")


def kpi(icon: str, value: str, label: str, color: str = "blue", sub: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="kpi-card {color}">'
        f'<div class="kpi-icon">{icon}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'{sub_html}'
        f'</div>'
    )


def kpi_row(*cards: str) -> None:
    st.markdown(
        '<div class="kpi-grid">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def section(title: str, sub: str = "") -> None:
    sub_html = f'<div class="section-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="section-title">{title}</div>{sub_html}',
        unsafe_allow_html=True,
    )


def chart_style(fig: go.Figure, height: int = 420, title: str = "") -> None:
    """Apply consistent modern styling and render a plotly chart."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#0f172a"), x=0) if title else None,
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        height=height,
        margin=dict(l=0, r=0, t=40 if title else 10, b=0),
        font=dict(color="#374151", size=12),
        xaxis=dict(
            gridcolor="#f1f5f9", linecolor="#e2e8f0",
            tickfont=dict(color="#94a3b8", size=11), tickangle=-35,
        ),
        yaxis=dict(
            gridcolor="#f1f5f9", linecolor="#e2e8f0",
            tickfont=dict(color="#94a3b8", size=11), zeroline=False,
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=11), bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def page_header(title: str, sub: str = "") -> None:
    sub_html = f'<div class="page-hdr-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="page-hdr"><div class="page-hdr-title">{title}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, sub: str) -> None:
    st.markdown(
        f'<div class="empty-state"><div class="empty-icon">{icon}</div>'
        f'<div class="empty-title">{title}</div>'
        f'<div class="empty-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


# ── Fetch helpers ─────────────────────────────────────────────────────────────

def fetch_sales(cikkszam, start, end):
    with st.spinner("Értékesítési adatok betöltése…"):
        try:
            df = api.get_sales(start.strftime("%Y.%m.%d"), end.strftime("%Y.%m.%d"), cikkszam)
            if df.empty:
                st.warning("Nincs értékesítési adat a kiválasztott feltételekre.")
                return None
            return df
        except Exception as e:
            st.error(f"API hiba: {e}")
            return None


def fetch_inventory(cikkszam):
    with st.spinner("Készlet betöltése…"):
        try:
            df = api.get_inventory(cikkszam)
            if df.empty:
                st.warning("Nincs készletadat.")
                return None
            return df
        except Exception as e:
            st.error(f"API hiba: {e}")
            return None


def fetch_movements(cikkszam, start, end):
    with st.spinner("Mozgástörténet betöltése…"):
        try:
            df = api.get_stock_movements(
                start.strftime("%Y.%m.%d"), end.strftime("%Y.%m.%d"), cikkszam
            )
            if df.empty:
                st.warning("Nincs mozgásadat.")
                return None
            return df
        except Exception as e:
            st.error(f"API hiba: {e}")
            return None


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(products: pd.DataFrame):
    with st.sidebar:
        # Brand header
        st.markdown("""
        <div style="padding:1.5rem 1.25rem 1rem; border-bottom:1px solid #1e293b; margin-bottom:0.5rem;">
            <div style="font-size:1.15rem;font-weight:800;color:#f8fafc;letter-spacing:-0.02em;">⚡ SamanSport</div>
            <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:0.1em;margin-top:3px;">Tharanis ERP Analytics</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown('<div style="padding:0.75rem 1.25rem 0.3rem;font-size:0.68rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.1em;">Navigáció</div>', unsafe_allow_html=True)

        pages = [
            ("dashboard", "🏠  Dashboard"),
            ("analytics",  "📊  Analitika"),
            ("report",     "📋  Riport"),
        ]
        for page_id, label in pages:
            is_active = st.session_state.page == page_id
            if st.button(label, key=f"nav_{page_id}",
                         type="primary" if is_active else "secondary",
                         use_container_width=True):
                st.session_state.page = page_id

        st.markdown('<div style="height:1px;background:#1e293b;margin:0.75rem 0;"></div>', unsafe_allow_html=True)

        # Product selector
        st.markdown('<div style="padding:0 1.25rem 0.3rem;font-size:0.68rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.1em;">Termék</div>', unsafe_allow_html=True)

        if products.empty:
            product_options = {ALL_PRODUCTS_LABEL: ALL_PRODUCTS_CODE}
        else:
            product_options = {ALL_PRODUCTS_LABEL: ALL_PRODUCTS_CODE}
            product_options.update({
                f"{r['Cikkszám']} – {r['Cikknév']}": r["Cikkszám"]
                for _, r in products.iterrows()
            })

        selected_label = st.selectbox(
            "Termék", options=list(product_options.keys()),
            label_visibility="collapsed",
        )
        selected_code = product_options[selected_label]
        cikkszam_api  = None if selected_code == ALL_PRODUCTS_CODE else selected_code

        # Date range
        st.markdown('<div style="padding:0.75rem 1.25rem 0.3rem;font-size:0.68rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.1em;">Időszak</div>', unsafe_allow_html=True)
        _today = datetime.now().date()
        date_range = st.date_input(
            "Időszak", key="date_range",
            value=(_today.replace(year=_today.year - 1), _today),
            max_value=_today, label_visibility="collapsed",
        )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range[0] if date_range else _today

        st.markdown('<div style="height:1px;background:#1e293b;margin:0.75rem 0;"></div>', unsafe_allow_html=True)

        # Load buttons
        st.markdown('<div style="padding:0 1.25rem 0.3rem;font-size:0.68rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.1em;">Adatok betöltése</div>', unsafe_allow_html=True)

        if st.button("🔄  Értékesítés", key="load_sales", type="secondary", use_container_width=True):
            df = fetch_sales(cikkszam_api, start_date, end_date)
            if df is not None:
                st.session_state.sales_df = df
                st.session_state.last_query = {
                    "cikkszam": cikkszam_api, "label": selected_label,
                    "start": start_date, "end": end_date,
                }
        if st.session_state.sales_df is not None:
            st.success(f"✓ {len(st.session_state.sales_df):,} értékesítési sor")

        if st.button("📦  Készlet", key="load_inv", type="secondary", use_container_width=True):
            inv = fetch_inventory(cikkszam_api)
            if inv is not None:
                st.session_state.inv_df = inv
                st.session_state.last_inv_query = {
                    "cikkszam": cikkszam_api, "label": selected_label,
                }
        if st.session_state.inv_df is not None:
            st.success(f"✓ {len(st.session_state.inv_df):,} termék készlete")

        if st.button("📋  Mozgástörténet", key="load_mozgas", type="secondary", use_container_width=True):
            mdf = fetch_movements(cikkszam_api, start_date, end_date)
            if mdf is not None:
                st.session_state.mozgas_df = mdf
                st.session_state.last_mozgas_query = {
                    "cikkszam": cikkszam_api, "label": selected_label,
                    "start": start_date, "end": end_date,
                }
        if st.session_state.mozgas_df is not None:
            st.success(f"✓ {len(st.session_state.mozgas_df):,} mozgássor")

        st.markdown('<div style="position:fixed;bottom:1rem;left:0;width:16rem;text-align:center;font-size:0.68rem;color:#334155;">Tharanis ERP · SamanSport MVP</div>', unsafe_allow_html=True)

    return selected_label, cikkszam_api, start_date, end_date


# ── Dashboard page ────────────────────────────────────────────────────────────

def render_dashboard():
    df   = st.session_state.sales_df
    inv  = st.session_state.inv_df
    meta = st.session_state.last_query or {}

    product_label = meta.get("label", "—")
    date_sub = f"{meta.get('start', '')} – {meta.get('end', '')}" if meta else ""
    page_header("Dashboard", f"{product_label}  ·  {date_sub}" if date_sub else "Töltse be az adatokat a bal oldali panelből")

    if df is None and inv is None:
        empty_state("📊", "Még nincs betöltött adat",
                    "Válasszon terméket és időszakot,<br>majd kattintson a betöltés gombokra a bal oldali panelben.")
        return

    # ── KPI cards ──────────────────────────────────────────────────────────────
    if df is not None:
        stock_val = "—"
        if inv is not None and not inv.empty:
            keszlet_col = inv.columns[1]
            if meta.get("cikkszam"):
                row = inv[inv.iloc[:, 0] == meta["cikkszam"]]
                stock_val = f"{row[keszlet_col].values[0]:,.0f} db" if not row.empty else "0 db"
            else:
                stock_val = f"{inv[keszlet_col].sum():,.0f} db"

        kpi_row(
            kpi("💰", f"{df['Bruttó érték'].sum():,.0f}", "Bruttó forgalom (HUF)", "blue"),
            kpi("📦", f"{df['Mennyiség'].sum():,.0f}", "Értékesített db", "green"),
            kpi("🏷️", f"{df['Bruttó ár'].mean():,.0f}", "Átl. bruttó ár (HUF)", "orange"),
            kpi("🧾", f"{len(df):,}", "Tranzakciók", "purple"),
        )
        if inv is not None:
            kpi_row(
                kpi("🏬", stock_val, "Jelenlegi készlet", "red"),
                kpi("📅", str(df["kelt"].dt.year.nunique()), "Aktív évek", "slate" if "slate" in C else "blue"),
                kpi("📈", f"{df['kelt'].dt.to_period('M').nunique()}", "Aktív hónapok", "green"),
                kpi("💵", f"{df['Nettó érték'].sum():,.0f}", "Nettó forgalom (HUF)", "blue"),
            )

        # ── Monthly revenue chart ───────────────────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section("Havi bruttó forgalom", product_label)
        df2 = df.copy()
        df2["Hónap"] = df2["kelt"].dt.to_period("M").astype(str)
        monthly = df2.groupby("Hónap")["Bruttó érték"].sum().reset_index().sort_values("Hónap")
        fig = go.Figure(go.Bar(
            x=monthly["Hónap"], y=monthly["Bruttó érték"],
            marker=dict(color=C["blue"], opacity=0.85,
                        line=dict(color=C["blue"], width=0)),
            hovertemplate="%{x}<br><b>%{y:,.0f} HUF</b><extra></extra>",
        ))
        chart_style(fig, height=300)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Two-column: quantity trend + top months ─────────────────────────────
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            section("Havi értékesített mennyiség")
            mq = df2.groupby("Hónap")["Mennyiség"].sum().reset_index().sort_values("Hónap")
            fig2 = go.Figure(go.Scatter(
                x=mq["Hónap"], y=mq["Mennyiség"],
                mode="lines+markers",
                line=dict(color=C["green"], width=2.5),
                marker=dict(size=6, color=C["green"]),
                fill="tozeroy", fillcolor="rgba(16,185,129,0.08)",
                hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>",
            ))
            chart_style(fig2, height=260)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            section("Átlagos bruttó ár trend")
            mp = df2.groupby("Hónap")["Bruttó ár"].mean().reset_index().sort_values("Hónap")
            fig3 = go.Figure(go.Scatter(
                x=mp["Hónap"], y=mp["Bruttó ár"],
                mode="lines+markers",
                line=dict(color=C["orange"], width=2.5),
                marker=dict(size=6, color=C["orange"]),
                fill="tozeroy", fillcolor="rgba(245,158,11,0.08)",
                hovertemplate="%{x}<br><b>%{y:,.0f} HUF</b><extra></extra>",
            ))
            chart_style(fig3, height=260)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Recent transactions ─────────────────────────────────────────────────
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        section("Legutóbbi tranzakciók", "Utolsó 20 sor")
        recent = df.copy().sort_values("kelt", ascending=False).head(20)
        recent["kelt"] = recent["kelt"].dt.strftime("%Y-%m-%d")
        st.dataframe(recent.reset_index(drop=True), use_container_width=True, height=280)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Analytics page ────────────────────────────────────────────────────────────

def render_analytics():
    meta = st.session_state.last_query or {}
    product_label = meta.get("label", "—")
    page_header("Analitika", product_label)

    tab_sales, tab_inv, tab_mozgas = st.tabs(
        ["📈  Értékesítés", "📦  Készlet", "📋  Mozgástörténet"]
    )

    # ── Értékesítés tab ────────────────────────────────────────────────────────
    with tab_sales:
        if st.session_state.sales_df is None:
            empty_state("📈", "Nincs értékesítési adat", "Töltse be az adatokat a bal oldali panelből.")
        else:
            df   = st.session_state.sales_df
            meta = st.session_state.last_query

            ctrl1, ctrl2, ctrl3 = st.columns([5, 2, 2])
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

            fig = go.Figure()
            ht = f"%{{x}}<br><b>%{{y:,.0f}} {unit}</b><extra></extra>"
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
                    marker=dict(size=7, color=C["blue"]),
                    fill="tozeroy", fillcolor="rgba(37,99,235,0.07)",
                    hovertemplate=ht,
                ))
            fig.update_layout(yaxis_title=ytitle)
            chart_style(fig, height=420,
                        title=f"{meta.get('label','')}"
                              f"  ·  {metric}  ·  {meta.get('start','')} – {meta.get('end','')}")

            st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1: st.metric("Összes mennyiség",   f"{df['Mennyiség'].sum():,.0f} db")
            with m2: st.metric("Bruttó forgalom",    f"{df['Bruttó érték'].sum():,.0f} HUF")
            with m3: st.metric("Nettó forgalom",     f"{df['Nettó érték'].sum():,.0f} HUF")
            with m4: st.metric("Átl. bruttó ár",     f"{df['Bruttó ár'].mean():,.0f} HUF")
            with m5: st.metric("Aktív periódusok",   f"{grouped['Periódus'].nunique()}")

    # ── Készlet tab ────────────────────────────────────────────────────────────
    with tab_inv:
        if st.session_state.inv_df is None:
            empty_state("📦", "Nincs készletadat", "Töltse be a készletet a bal oldali panelből.")
        else:
            inv  = st.session_state.inv_df
            meta_inv = st.session_state.last_inv_query
            label    = meta_inv.get("label", "")
            is_all   = meta_inv.get("cikkszam") is None
            keszlet_col = inv.columns[1]

            if is_all:
                inv_pos  = inv[inv[keszlet_col] > 0].sort_values(keszlet_col, ascending=False)
                inv_zero = inv[inv[keszlet_col] == 0]
                kpi_row(
                    kpi("📦", f"{len(inv_pos):,}", "Készletes termékek", "green"),
                    kpi("⬜", f"{len(inv_zero):,}", "Nulla készlet", "red"),
                    kpi("🏬", f"{inv[keszlet_col].sum():,.0f}", "Összes készlet (db)", "blue"),
                    kpi("📊", f"{len(inv):,}", "Termékek összesen", "orange"),
                )
                top_n = st.slider("Top N termék", 10, 100, 30, step=10)
                top   = inv_pos.head(top_n)
                fig = go.Figure(go.Bar(
                    x=top.iloc[:, 0], y=top[keszlet_col],
                    marker_color=C["green"], opacity=0.85,
                    hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>",
                ))
                chart_style(fig, height=400, title=f"Top {top_n} termék — elérhető készlet")
                with st.expander("Teljes készlet táblázat"):
                    st.dataframe(inv_pos.reset_index(drop=True), use_container_width=True)
            else:
                row   = inv.iloc[0]
                total = row[keszlet_col]
                st.markdown(f'<div style="margin-bottom:1.25rem;">', unsafe_allow_html=True)
                kpi_row(kpi("🏬", f"{total:,.0f} db", "Elérhető készlet", "green" if total > 0 else "red"))
                st.markdown('</div>', unsafe_allow_html=True)
                wh_cols = [c for c in inv.columns if c.startswith("Raktár")]
                wh_data = {c: row[c] for c in wh_cols if row[c] > 0}
                if wh_data:
                    fig = go.Figure(go.Bar(
                        x=list(wh_data.keys()), y=list(wh_data.values()),
                        marker_color=C["green"],
                        text=[f"{v:,.0f}" for v in wh_data.values()],
                        textposition="outside",
                        hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>",
                    ))
                    chart_style(fig, height=350, title=f"{label} – készlet raktáranként")
                else:
                    st.warning("Minden raktárban nulla a készlet.")

    # ── Mozgástörténet tab ─────────────────────────────────────────────────────
    with tab_mozgas:
        if st.session_state.mozgas_df is None:
            empty_state("📋", "Nincs mozgástörténet", "Töltse be a mozgásokat a bal oldali panelből.")
        else:
            mdf  = st.session_state.mozgas_df
            meta_m = st.session_state.last_mozgas_query

            cp, cc = st.columns([2, 2])
            with cp: period_m  = st.radio("Periódus", PERIOD_OPTIONS, horizontal=True, key="mz_period")
            with cc: chart_m   = st.radio("Diagram", ["Oszlop", "Vonal"], horizontal=True, key="mz_chart")

            mdf2 = mdf.copy()
            mdf2["Periódus"] = period_key(mdf2["kelt"], period_m)
            be_map = mdf2[mdf2["Irány"] == "B"].groupby("Periódus")["Mennyiség"].sum().to_dict()
            ki_map = mdf2[mdf2["Irány"] == "K"].groupby("Periódus")["Mennyiség"].sum().to_dict()
            all_p  = sorted(set(be_map) | set(ki_map))
            be_v   = [be_map.get(p, 0) for p in all_p]
            ki_v   = [ki_map.get(p, 0) for p in all_p]

            fig = go.Figure()
            if chart_m == "Oszlop":
                fig.add_trace(go.Bar(x=all_p, y=be_v, name="Beérkező", marker_color=C["green"],
                                     hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>"))
                fig.add_trace(go.Bar(x=all_p, y=ki_v, name="Kiadó",    marker_color=C["red"],
                                     hovertemplate="%{x}<br><b>%{y:,.0f} db</b><extra></extra>"))
                fig.update_layout(barmode="group")
            else:
                fig.add_trace(go.Scatter(x=all_p, y=be_v, name="Beérkező",
                                         mode="lines+markers", line=dict(color=C["green"], width=2.5),
                                         marker=dict(size=6)))
                fig.add_trace(go.Scatter(x=all_p, y=ki_v, name="Kiadó",
                                         mode="lines+markers", line=dict(color=C["red"], width=2.5),
                                         marker=dict(size=6)))
            chart_style(fig, height=420,
                        title=f"{meta_m.get('label','')}  ·  Raktári mozgások")

            st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
            total_be = mdf[mdf["Irány"] == "B"]["Mennyiség"].sum()
            total_ki = mdf[mdf["Irány"] == "K"]["Mennyiség"].sum()
            s1, s2, s3, s4 = st.columns(4)
            with s1: st.metric("Összes beérkező", f"{total_be:,.0f} db")
            with s2: st.metric("Összes kiadó",    f"{total_ki:,.0f} db")
            with s3: st.metric("Nettó mozgás",    f"{total_be - total_ki:+,.0f} db")
            with s4: st.metric("Mozgástípusok",   f"{mdf['Mozgástípus'].nunique()}")


# ── Report page ───────────────────────────────────────────────────────────────

def render_report():
    meta = st.session_state.last_query or {}
    page_header("Riport", meta.get("label", "—"))

    tabs = []
    if st.session_state.sales_df is not None:   tabs.append("📈  Értékesítés")
    if st.session_state.inv_df is not None:      tabs.append("📦  Készlet")
    if st.session_state.mozgas_df is not None:   tabs.append("📋  Mozgástörténet")

    if not tabs:
        empty_state("📋", "Nincs betöltött adat", "Töltse be az adatokat a bal oldali panelből.")
        return

    tab_objs = st.tabs(tabs)
    tab_idx  = 0

    # ── Sales report ──────────────────────────────────────────────────────────
    if st.session_state.sales_df is not None:
        with tab_objs[tab_idx]:
            tab_idx += 1
            df   = st.session_state.sales_df
            meta = st.session_state.last_query

            # Summary stats
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            section("Összefoglaló statisztikák")
            stats = pd.DataFrame({
                "Mutató": ["Bruttó forgalom (HUF)", "Nettó forgalom (HUF)",
                           "Összes mennyiség (db)", "Átl. bruttó ár (HUF)",
                           "Átl. nettó ár (HUF)", "Tranzakciók száma",
                           "Időszak (nap)", "Aktív hónapok"],
                "Érték": [
                    f"{df['Bruttó érték'].sum():,.0f}",
                    f"{df['Nettó érték'].sum():,.0f}",
                    f"{df['Mennyiség'].sum():,.0f}",
                    f"{df['Bruttó ár'].mean():,.0f}",
                    f"{df['Nettó ár'].mean():,.0f}",
                    f"{len(df):,}",
                    f"{(meta.get('end', meta.get('start')) - meta.get('start', meta.get('end'))).days + 1 if meta.get('start') else '—'}",
                    f"{df['kelt'].dt.to_period('M').nunique()}",
                ],
            })
            st.dataframe(stats, use_container_width=True, hide_index=True, height=318)
            st.markdown('</div>', unsafe_allow_html=True)

            # Full table
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            section("Teljes értékesítési adatok", f"{len(df):,} sor")
            show = df.copy()
            show["kelt"] = show["kelt"].dt.strftime("%Y-%m-%d")
            st.dataframe(show.reset_index(drop=True), use_container_width=True, height=400)
            csv = show.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇  CSV letöltése",
                data=csv,
                file_name=f"ertekesites_{meta.get('cikkszam','osszes')}_{meta.get('start','')}.csv",
                mime="text/csv",
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Inventory report ──────────────────────────────────────────────────────
    if st.session_state.inv_df is not None:
        with tab_objs[tab_idx]:
            tab_idx += 1
            inv  = st.session_state.inv_df
            meta_inv = st.session_state.last_inv_query
            keszlet_col = inv.columns[1]

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            section("Készlet adatok", f"{len(inv):,} termék · {inv[keszlet_col].sum():,.0f} db összesen")
            inv_sorted = inv.sort_values(keszlet_col, ascending=False)
            st.dataframe(inv_sorted.reset_index(drop=True), use_container_width=True, height=450)
            csv = inv_sorted.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇  CSV letöltése",
                data=csv,
                file_name=f"keszlet_{meta_inv.get('cikkszam','osszes')}.csv",
                mime="text/csv",
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Movements report ──────────────────────────────────────────────────────
    if st.session_state.mozgas_df is not None:
        with tab_objs[tab_idx]:
            mdf      = st.session_state.mozgas_df
            meta_m   = st.session_state.last_mozgas_query
            total_be = mdf[mdf["Irány"] == "B"]["Mennyiség"].sum()
            total_ki = mdf[mdf["Irány"] == "K"]["Mennyiség"].sum()

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            section("Mozgástörténet", f"{len(mdf):,} sor · {meta_m.get('start','')} – {meta_m.get('end','')}")
            c1, c2 = st.columns([1, 3])
            with c1:
                st.metric("Beérkező (B)", f"{total_be:,.0f} db")
                st.metric("Kiadó (K)",    f"{total_ki:,.0f} db")
                st.metric("Nettó mozgás", f"{total_be - total_ki:+,.0f} db")
            with c2:
                show_m = mdf.copy()
                show_m["kelt"] = show_m["kelt"].dt.strftime("%Y-%m-%d")
                st.dataframe(show_m.reset_index(drop=True), use_container_width=True, height=320)
            csv = show_m.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇  CSV letöltése",
                data=csv,
                file_name=f"mozgas_{meta_m.get('cikkszam','osszes')}_{meta_m.get('start','')}.csv",
                mime="text/csv",
            )
            st.markdown('</div>', unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    products = load_product_master()
    render_sidebar(products)

    page = st.session_state.page
    if page == "dashboard":
        render_dashboard()
    elif page == "analytics":
        render_analytics()
    elif page == "report":
        render_report()


if __name__ == "__main__":
    main()
