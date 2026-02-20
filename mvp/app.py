"""
Tharanis ERP Dashboard – MVP
Product-level sales analysis: Bruttó ár / Bruttó érték / Mennyiség
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import tharanis_client as api

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE    = os.path.dirname(os.path.abspath(__file__))
_CSV_DIR = os.path.join(_HERE, "..", "..", "inventory_analysis_2020_2026")
_CSV_PATH = os.path.join(
    _CSV_DIR, "rakbiz_analitika_012020_012026.csv"
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tharanis ERP Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .block-container { padding-top: 1.5rem; }
  div[data-testid="stMetricValue"] { font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)


# ── Product master (loaded once from CSV) ─────────────────────────────────────

@st.cache_data(show_spinner="Termék lista betöltése…")
def load_product_master() -> pd.DataFrame:
    """
    Build a unique (Cikkszám, Cikknév) lookup from the historical CSV.
    Returns DataFrame sorted by Cikknév.
    """
    if not os.path.exists(_CSV_PATH):
        return pd.DataFrame(columns=["Cikkszám", "Cikknév"])

    # Col 9 = Cikkszám, Col 10 = Cikknév  (0-indexed column positions)
    df = pd.read_csv(
        _CSV_PATH,
        usecols=[9, 10],
        dtype=str,
        encoding="utf-8-sig",
        on_bad_lines="skip",
    )
    df.columns = ["Cikkszám", "Cikknév"]
    products = (
        df.dropna(subset=["Cikkszám", "Cikknév"])
        .drop_duplicates(subset=["Cikkszám"])
        .sort_values("Cikknév")
        .reset_index(drop=True)
    )
    return products


# ── Session state ─────────────────────────────────────────────────────────────
if "sales_df" not in st.session_state:
    st.session_state.sales_df = None
if "last_query" not in st.session_state:
    st.session_state.last_query = {}


# ── Data fetch ────────────────────────────────────────────────────────────────

def fetch_sales(cikkszam: str, start: datetime, end: datetime) -> pd.DataFrame | None:
    start_s = start.strftime("%Y.%m.%d")
    end_s   = end.strftime("%Y.%m.%d")
    with st.spinner("Adatok betöltése a Tharanis API-ból…"):
        try:
            df = api.get_sales(start_s, end_s, cikkszam)
            if df.empty:
                st.warning("Nincs értékesítési adat a kiválasztott termékhez és időszakhoz.")
                return None
            return df
        except Exception as e:
            st.error(f"API hiba: {e}")
            return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    st.title("📊 Tharanis ERP – Termék Elemzés")

    products = load_product_master()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Beállítások")

        # Product selector
        st.subheader("🎯 Termék")
        if products.empty:
            st.warning("Termék lista nem érhető el. Ellenőrizze a CSV fájlt.")
            product_options = {}
        else:
            product_options = {
                f"{row['Cikkszám']} – {row['Cikknév']}": row["Cikkszám"]
                for _, row in products.iterrows()
            }

        selected_label = st.selectbox(
            "Cikkszám – Cikknév",
            options=list(product_options.keys()) if product_options else ["(nincs adat)"],
            label_visibility="collapsed",
        )
        selected_code = product_options.get(selected_label)

        # Date range
        st.subheader("📅 Időszak")
        start_date = st.date_input(
            "Kezdő dátum",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now(),
        )
        end_date = st.date_input(
            "Záró dátum",
            value=datetime.now(),
            max_value=datetime.now(),
        )

        # Load button
        st.markdown("---")
        load_clicked = st.button(
            "🔄 Adatok betöltése",
            type="primary",
            use_container_width=True,
            disabled=(selected_code is None),
        )

        if load_clicked and selected_code:
            df = fetch_sales(selected_code, start_date, end_date)
            if df is not None:
                st.session_state.sales_df = df
                st.session_state.last_query = {
                    "cikkszam": selected_code,
                    "label":    selected_label,
                    "start":    start_date,
                    "end":      end_date,
                }

        if st.session_state.sales_df is not None:
            n = len(st.session_state.sales_df)
            st.success(f"✅ {n} tétel betöltve")

        st.markdown("---")
        st.caption("Tharanis ERP • SamanSport MVP")

    # ── Guard ─────────────────────────────────────────────────────────────────
    if st.session_state.sales_df is None:
        st.info(
            "👈 Válasszon terméket és időszakot, "
            "majd kattintson az **Adatok betöltése** gombra."
        )
        return

    df   = st.session_state.sales_df
    meta = st.session_state.last_query

    # ── Controls ──────────────────────────────────────────────────────────────
    col_metric, col_chart = st.columns([3, 2])

    with col_metric:
        metric = st.radio(
            "📊 Mutató",
            options=["Bruttó érték", "Mennyiség", "Bruttó ár"],
            horizontal=True,
        )

    with col_chart:
        chart_type = st.radio(
            "📈 Diagram",
            options=["Oszlop", "Vonal"],
            horizontal=True,
        )

    # ── Aggregate ─────────────────────────────────────────────────────────────
    df2 = df.copy()
    df2["Hónap"] = df2["kelt"].dt.to_period("M").astype(str)

    METRIC_CFG = {
        "Bruttó érték": {"col": "Bruttó érték", "agg": "sum",  "unit": "HUF",
                         "ytitle": "Bruttó érték (HUF)"},
        "Mennyiség":    {"col": "Mennyiség",    "agg": "sum",  "unit": "db",
                         "ytitle": "Mennyiség (db)"},
        "Bruttó ár":    {"col": "Bruttó ár",    "agg": "mean", "unit": "HUF",
                         "ytitle": "Átlag bruttó ár (HUF)"},
    }
    cfg = METRIC_CFG[metric]

    monthly = (
        df2.groupby("Hónap")[cfg["col"]]
        .agg(cfg["agg"])
        .reset_index()
        .sort_values("Hónap")
    )

    # ── Chart ─────────────────────────────────────────────────────────────────
    fig = go.Figure()
    hover_fmt = ",.0f"
    hover_sfx = f" {cfg['unit']}"

    if chart_type == "Oszlop":
        fig.add_trace(go.Bar(
            x=monthly["Hónap"],
            y=monthly[cfg["col"]],
            name=metric,
            marker_color="#1f77b4",
            hovertemplate=(
                f"%{{x}}<br>{metric}: %{{y:{hover_fmt}}}{hover_sfx}<extra></extra>"
            ),
        ))
    else:
        fig.add_trace(go.Scatter(
            x=monthly["Hónap"],
            y=monthly[cfg["col"]],
            mode="lines+markers",
            name=metric,
            line=dict(color="#1f77b4", width=2.5),
            marker=dict(size=7),
            hovertemplate=(
                f"%{{x}}<br>{metric}: %{{y:{hover_fmt}}}{hover_sfx}<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(
            text=(
                f"<b>{meta['label']}</b><br>"
                f"<sup>{metric} — {meta['start']} – {meta['end']}</sup>"
            ),
            font=dict(size=17),
        ),
        xaxis_title="Hónap",
        yaxis_title=cfg["ytitle"],
        hovermode="x unified",
        height=500,
        xaxis=dict(tickangle=-45),
        margin=dict(t=90),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Summary metrics ───────────────────────────────────────────────────────
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Összes mennyiség",
                  f"{df['Mennyiség'].sum():,.0f} db")
    with m2:
        st.metric("Bruttó forgalom",
                  f"{df['Bruttó érték'].sum():,.0f} HUF")
    with m3:
        st.metric("Átl. bruttó ár",
                  f"{df['Bruttó ár'].mean():,.0f} HUF")
    with m4:
        st.metric("Aktív hónapok",
                  f"{monthly['Hónap'].nunique()}")


if __name__ == "__main__":
    main()
