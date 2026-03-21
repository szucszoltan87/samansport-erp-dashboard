"""
Dashboard page – KPI cards, revenue trend, quantities, top 10 products.
"""

import streamlit as st
import pandas as pd

from helpers import (
    empty_state, kpi_card, kpi_grid, section_header,
    find_sku_col, find_name_col, load_product_master,
    period_key,
)
from charts import revenue_trend_chart, quantity_bar_chart, top10_products_chart
from theme import hu_thousands


def render_dashboard():
    df   = st.session_state.sales_df
    meta = st.session_state.last_query or {}

    if df is None or df.empty:
        empty_state(
            "database",
            "Nincs betöltött adat",
            "Nyissa meg az <b>Analitika</b> oldalt, válasszon terméket és időszakot,<br>"
            "majd kattintson a <b>Betöltése</b> gombra.",
        )
        return

    # ── KPI row ────────────────────────────────────────────────────────────────
    kpi_grid(
        kpi_card("Bruttó forgalom", f"{hu_thousands(df['Bruttó érték'].sum())} HUF",
                 "dollar-sign", "rgba(78,91,166,0.1)", "#4E5BA6",
                 sub=f"{df['kelt'].dt.to_period('M').nunique()} aktív hónap",
                 tooltip="Összes bruttó értékesítés a kiválasztott időszakban (ÁFA-val)"),
        kpi_card("Értékesített mennyiség", f"{hu_thousands(df['Mennyiség'].sum())} db",
                 "package", "#fef9c3", "#d97706",
                 sub=f"Nettó: {hu_thousands(df['Nettó érték'].sum())} HUF",
                 tooltip="Összes eladott tétel darabszáma a kiválasztott időszakban"),
        kpi_card("Átlagos bruttó ár", f"{hu_thousands(df['Bruttó ár'].mean())} HUF",
                 "tag", "#F8F9FC", "#293056",
                 sub=f"Átl. nettó: {hu_thousands(df['Nettó ár'].mean())} HUF",
                 tooltip="Egy eladott tétel átlagos bruttó ára (ÁFA-val)"),
        kpi_card("Tranzakciók", f"{hu_thousands(len(df))}",
                 "receipt", "rgba(78,91,166,0.06)", "#4E5BA6",
                 sub=f"{df['kelt'].dt.year.nunique()} aktív év",
                 tooltip="Számlasorok száma a kiválasztott időszakban"),
    )

    # ── Period toggle for dashboard charts ────────────────────────────────────
    _period_opts = ["Éves", "Havi", "Heti", "Napi"]
    if "dash_period" not in st.session_state:
        st.session_state["dash_period"] = "Havi"
    dash_period = st.radio(
        "Periódus", _period_opts,
        horizontal=True, key="dash_period",
    )
    df2 = df.copy()
    df2["Periódus"] = period_key(df2["kelt"], dash_period)

    # ── Revenue trend ──────────────────────────────────────────────────────────
    section_header("Bruttó forgalom", f"{dash_period} bontás  ·  Értékesítési trend az időszakra", "trending-up")
    monthly = df2.groupby("Periódus")["Bruttó érték"].sum().reset_index().sort_values("Periódus")
    revenue_trend_chart(monthly)

    # ── Quantities chart ──────────────────────────────────────────────────────
    section_header("Értékesített mennyiség", f"{dash_period} bontás", "activity")
    mq = df2.groupby("Periódus")["Mennyiség"].sum().reset_index().sort_values("Periódus")
    quantity_bar_chart(mq)

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

        top10_products_chart(grp)
