"""
Dashboard page – KPI cards, revenue trend, quantities, top 10 products.
"""

import streamlit as st
import pandas as pd

from helpers import (
    empty_state, kpi_card, kpi_grid, section_header,
    find_sku_col, find_name_col, load_product_master,
)
from charts import revenue_trend_chart, quantity_bar_chart, top10_products_chart


def render_dashboard():
    df   = st.session_state.sales_df
    meta = st.session_state.last_query or {}

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
                 "dollar-sign", "rgba(231,76,60,0.1)", "#e74c3c",
                 sub=f"{df['kelt'].dt.to_period('M').nunique()} aktív hónap"),
        kpi_card("Értékesített mennyiség", f"{df['Mennyiség'].sum():,.0f} db",
                 "package", "#fef9c3", "#d97706",
                 sub=f"Nettó: {df['Nettó érték'].sum():,.0f} HUF"),
        kpi_card("Átlagos bruttó ár", f"{df['Bruttó ár'].mean():,.0f} HUF",
                 "tag", "#f3f4f6", "#1c1c2e",
                 sub=f"Átl. nettó: {df['Nettó ár'].mean():,.0f} HUF"),
        kpi_card("Tranzakciók", f"{len(df):,}",
                 "receipt", "rgba(231,76,60,0.06)", "#e74c3c",
                 sub=f"{df['kelt'].dt.year.nunique()} aktív év"),
    )

    # ── Period toggle for dashboard charts ────────────────────────────────────
    dash_period = st.radio(
        "Periódus", ["Éves", "Havi", "Heti", "Napi"],
        horizontal=True, key="dash_period", index=1,
    )
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
