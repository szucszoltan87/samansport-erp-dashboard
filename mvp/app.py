"""
Tharanis ERP Dashboard – MVP
Sales analytics + live inventory · SamanSport
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

# ── Constants ─────────────────────────────────────────────────────────────────

ALL_PRODUCTS_LABEL = "— Összes termék (cégszintű) —"
ALL_PRODUCTS_CODE  = "__ALL__"

PERIOD_OPTIONS = ["Havi", "Heti", "Napi"]

# Metric config: label -> (column, aggregation, unit, y-axis title)
METRIC_CFG = {
    "Bruttó forgalom":    ("Bruttó érték",  "sum",   "HUF", "Bruttó forgalom (HUF)"),
    "Nettó forgalom":     ("Nettó érték",   "sum",   "HUF", "Nettó forgalom (HUF)"),
    "Mennyiség":          ("Mennyiség",     "sum",   "db",  "Mennyiség (db)"),
    "Átl. bruttó ár":     ("Bruttó ár",     "mean",  "HUF", "Átlag bruttó ár (HUF)"),
    "Átl. nettó ár":      ("Nettó ár",      "mean",  "HUF", "Átlag nettó ár (HUF)"),
    "Tranzakciók száma":  ("Mennyiség",     "count", "db",  "Tranzakciók száma"),
}


# ── Product master (loaded once from CSV) ─────────────────────────────────────

@st.cache_data(show_spinner="Termék lista betöltése…")
def load_product_master() -> pd.DataFrame:
    if not os.path.exists(_CSV_PATH):
        return pd.DataFrame(columns=["Cikkszám", "Cikknév"])
    df = pd.read_csv(
        _CSV_PATH,
        usecols=[9, 10],
        dtype=str,
        encoding="utf-8-sig",
        on_bad_lines="skip",
    )
    df.columns = ["Cikkszám", "Cikknév"]
    return (
        df.dropna(subset=["Cikkszám", "Cikknév"])
        .drop_duplicates(subset=["Cikkszám"])
        .sort_values("Cikknév")
        .reset_index(drop=True)
    )


# ── Session state ─────────────────────────────────────────────────────────────

for _key, _default in [
    ("sales_df",       None),
    ("inv_df",         None),
    ("last_query",     {}),
    ("last_inv_query", {}),
]:
    if _key not in st.session_state:
        st.session_state[_key] = _default


# ── Helpers ───────────────────────────────────────────────────────────────────

def period_key(series: pd.Series, period: str) -> pd.Series:
    if period == "Havi":
        return series.dt.to_period("M").astype(str)
    if period == "Heti":
        return series.dt.to_period("W").astype(str)
    return series.dt.strftime("%Y-%m-%d")


def fetch_sales(cikkszam: str | None, start: datetime, end: datetime) -> pd.DataFrame | None:
    start_s = start.strftime("%Y.%m.%d")
    end_s   = end.strftime("%Y.%m.%d")
    with st.spinner("Értékesítési adatok betöltése…"):
        try:
            df = api.get_sales(start_s, end_s, cikkszam)
            if df.empty:
                st.warning("Nincs értékesítési adat a kiválasztott feltételekre.")
                return None
            return df
        except Exception as e:
            st.error(f"API hiba: {e}")
            return None


def fetch_inventory(cikkszam: str | None) -> pd.DataFrame | None:
    with st.spinner("Készlet betöltése…"):
        try:
            df = api.get_inventory(cikkszam)
            if df.empty:
                st.warning("Nincs készletadat a kiválasztott termékre.")
                return None
            return df
        except Exception as e:
            st.error(f"API hiba: {e}")
            return None


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(products: pd.DataFrame):
    with st.sidebar:
        st.header("⚙️ Beállítások")

        # Product selector — "all products" is always first
        st.subheader("🎯 Termék")
        if products.empty:
            st.warning("Termék lista nem érhető el.")
            product_options = {ALL_PRODUCTS_LABEL: ALL_PRODUCTS_CODE}
        else:
            product_options = {ALL_PRODUCTS_LABEL: ALL_PRODUCTS_CODE}
            product_options.update({
                f"{row['Cikkszám']} – {row['Cikknév']}": row["Cikkszám"]
                for _, row in products.iterrows()
            })

        selected_label = st.selectbox(
            "Cikkszám – Cikknév",
            options=list(product_options.keys()),
            label_visibility="collapsed",
        )
        selected_code = product_options[selected_label]
        # None = all products (no cikksz filter sent to API)
        cikkszam_api = None if selected_code == ALL_PRODUCTS_CODE else selected_code

        # Date range (sales only)
        st.subheader("📅 Időszak (értékesítés)")
        start_date = st.date_input(
            "Kezdő dátum",
            key="date_start",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now(),
        )
        end_date = st.date_input(
            "Záró dátum",
            key="date_end",
            value=datetime.now(),
            max_value=datetime.now(),
        )

        st.markdown("---")

        load_sales = st.button(
            "🔄 Értékesítés betöltése",
            type="primary",
            use_container_width=True,
        )
        if load_sales:
            df = fetch_sales(cikkszam_api, start_date, end_date)
            if df is not None:
                st.session_state.sales_df = df
                st.session_state.last_query = {
                    "cikkszam": cikkszam_api,
                    "label":    selected_label,
                    "start":    start_date,
                    "end":      end_date,
                }

        if st.session_state.sales_df is not None:
            n = len(st.session_state.sales_df)
            st.success(f"✅ {n} értékesítési sor")

        st.markdown("---")

        load_inv = st.button(
            "📦 Készlet betöltése",
            use_container_width=True,
        )
        if load_inv:
            inv = fetch_inventory(cikkszam_api)
            if inv is not None:
                st.session_state.inv_df = inv
                st.session_state.last_inv_query = {
                    "cikkszam": cikkszam_api,
                    "label":    selected_label,
                }

        if st.session_state.inv_df is not None:
            n = len(st.session_state.inv_df)
            st.success(f"✅ {n} termék készlete")

        st.markdown("---")
        st.caption("Tharanis ERP • SamanSport MVP")

    return selected_label, cikkszam_api, start_date, end_date


# ── Sales tab ─────────────────────────────────────────────────────────────────

def render_sales_tab():
    if st.session_state.sales_df is None:
        st.info(
            "👈 Válasszon terméket és időszakot, "
            "majd kattintson az **Értékesítés betöltése** gombra."
        )
        return

    df   = st.session_state.sales_df
    meta = st.session_state.last_query

    # Controls
    col_metric, col_period, col_chart = st.columns([4, 2, 2])

    with col_metric:
        metric = st.radio(
            "📊 Mutató",
            options=list(METRIC_CFG.keys()),
            horizontal=True,
        )

    with col_period:
        period = st.radio(
            "🗓️ Periódus",
            options=PERIOD_OPTIONS,
            horizontal=True,
        )

    with col_chart:
        chart_type = st.radio(
            "📈 Diagram",
            options=["Oszlop", "Vonal"],
            horizontal=True,
        )

    # Aggregate
    col_name, agg_fn, unit, ytitle = METRIC_CFG[metric]

    df2 = df.copy()
    df2["Periódus"] = period_key(df2["kelt"], period)
    grouped = (
        df2.groupby("Periódus")[col_name]
        .agg(agg_fn)
        .reset_index()
        .sort_values("Periódus")
    )

    # Chart
    label = meta.get("label", "")
    fig = go.Figure()
    hover_sfx = f" {unit}"

    if chart_type == "Oszlop":
        fig.add_trace(go.Bar(
            x=grouped["Periódus"],
            y=grouped[col_name],
            name=metric,
            marker_color="#1f77b4",
            hovertemplate=f"%{{x}}<br>{metric}: %{{y:,.0f}}{hover_sfx}<extra></extra>",
        ))
    else:
        fig.add_trace(go.Scatter(
            x=grouped["Periódus"],
            y=grouped[col_name],
            mode="lines+markers",
            name=metric,
            line=dict(color="#1f77b4", width=2.5),
            marker=dict(size=7),
            hovertemplate=f"%{{x}}<br>{metric}: %{{y:,.0f}}{hover_sfx}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(
            text=(
                f"<b>{label}</b><br>"
                f"<sup>{metric} — {meta.get('start')} – {meta.get('end')}</sup>"
            ),
            font=dict(size=17),
        ),
        xaxis_title=period,
        yaxis_title=ytitle,
        hovermode="x unified",
        height=500,
        xaxis=dict(tickangle=-45),
        margin=dict(t=90),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary metrics
    st.markdown("---")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Összes mennyiség",   f"{df['Mennyiség'].sum():,.0f} db")
    with m2:
        st.metric("Bruttó forgalom",    f"{df['Bruttó érték'].sum():,.0f} HUF")
    with m3:
        st.metric("Nettó forgalom",     f"{df['Nettó érték'].sum():,.0f} HUF")
    with m4:
        st.metric("Átl. bruttó ár",     f"{df['Bruttó ár'].mean():,.0f} HUF")
    with m5:
        st.metric("Aktív periódusok",   f"{grouped['Periódus'].nunique()}")

    # Raw data
    with st.expander("📋 Részletes adatok"):
        show = df.copy()
        show["kelt"] = show["kelt"].dt.strftime("%Y-%m-%d")
        st.dataframe(show, use_container_width=True)


# ── Inventory tab ─────────────────────────────────────────────────────────────

def render_inventory_tab():
    if st.session_state.inv_df is None:
        st.info(
            "👈 Válasszon terméket, "
            "majd kattintson a **Készlet betöltése** gombra."
        )
        return

    inv  = st.session_state.inv_df
    meta = st.session_state.last_inv_query
    label    = meta.get("label", "")
    is_all   = meta.get("cikkszam") is None

    if is_all:
        # ── Company-wide inventory ─────────────────────────────────────────────
        inv_pos  = inv[inv["Készlet"] > 0].sort_values("Készlet", ascending=False)
        inv_zero = inv[inv["Készlet"] == 0]

        st.subheader(f"Cégszintű készlet — {len(inv)} termék")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Készletes termékek",  f"{len(inv_pos)}")
        with c2:
            st.metric("Nulla készlet",        f"{len(inv_zero)}")
        with c3:
            st.metric("Összes készlet (db)",  f"{inv['Készlet'].sum():,.0f}")

        st.markdown("---")

        top_n = st.slider("Top N termék megjelenítése", 10, 100, 30, step=10)
        top   = inv_pos.head(top_n)

        fig = go.Figure(go.Bar(
            x=top["Cikkszám"],
            y=top["Készlet"],
            marker_color="#2ca02c",
            hovertemplate="%{x}<br>Készlet: %{y:,.0f} db<extra></extra>",
        ))
        fig.update_layout(
            title=dict(
                text=f"<b>Top {top_n} termék — elérhető készlet</b>",
                font=dict(size=16),
            ),
            xaxis_title="Cikkszám",
            yaxis_title="Elérhető készlet (db)",
            height=500,
            xaxis=dict(tickangle=-45),
            margin=dict(t=60),
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Teljes készlet táblázat"):
            st.dataframe(inv_pos.reset_index(drop=True), use_container_width=True)

    else:
        # ── Single-product inventory ───────────────────────────────────────────
        row   = inv.iloc[0]
        total = row["Készlet"]

        st.subheader(f"Készlet: {label}")
        st.metric("Összes elérhető készlet", f"{total:,.0f} db")
        st.markdown("---")

        wh_cols = [c for c in inv.columns if c.startswith("Raktár")]
        wh_data = {c: row[c] for c in wh_cols if row[c] > 0}

        if wh_data:
            fig = go.Figure(go.Bar(
                x=list(wh_data.keys()),
                y=list(wh_data.values()),
                marker_color="#2ca02c",
                text=[f"{v:,.0f}" for v in wh_data.values()],
                textposition="outside",
                hovertemplate="%{x}<br>Készlet: %{y:,.0f} db<extra></extra>",
            ))
            fig.update_layout(
                title=dict(
                    text=f"<b>{label}</b><br><sup>Készlet raktáranként</sup>",
                    font=dict(size=16),
                ),
                xaxis_title="Raktár",
                yaxis_title="Elérhető készlet (db)",
                height=400,
                margin=dict(t=80),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Minden raktárban nulla a készlet.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.title("📊 Tharanis ERP – Értékesítés & Készlet")

    products = load_product_master()
    render_sidebar(products)

    tab_sales, tab_inv = st.tabs(["📈 Értékesítés", "📦 Készlet"])

    with tab_sales:
        render_sales_tab()

    with tab_inv:
        render_inventory_tab()


if __name__ == "__main__":
    main()
