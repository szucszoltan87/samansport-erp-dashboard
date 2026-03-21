"""
Tharanis ERP Dashboard – SamanSport
Thin entry point: config → CSS → layout → page routing.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from config import ALL_PRODUCTS_LABEL
from theme import inject_css
from layout import render_sidebar, render_header
from helpers import (
    find_sku_col, find_name_col, load_product_master, build_product_opts,
    fetch_sales, funny_loader, load_warn,
)
from pages.dashboard import render_dashboard
from pages.analytics import render_analytics

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SamanSport ERP",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Session state ─────────────────────────────────────────────────────────────
_init_today = datetime.now().date()
for _k, _v in [
    ("sidebar_collapsed", False),
    ("page",              "dashboard"),
    ("sales_df",          None),
    ("mozgas_df",         None),
    ("last_query",        {}),
    ("last_mozgas_query", {}),
    ("start_date",        _init_today.replace(year=_init_today.year - 1)),
    ("end_date",          _init_today),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    load_product_master()   # warm cache
    render_sidebar()
    start_date, end_date, refresh_clicked = render_header()

    page = st.session_state.page

    # ── Dashboard: auto-load sales data; Analytics loads independently ────
    if page == "dashboard":
        if refresh_clicked:
            with st.spinner("Friss adatok letöltése az API-ból..."):
                _r_df = fetch_sales(None, start_date, end_date, force_refresh=True)
            if _r_df is not None:
                st.session_state.sales_df = _r_df
                st.session_state.last_query = {
                    "cikkszam": None,
                    "label":    ALL_PRODUCTS_LABEL,
                    "start":    start_date,
                    "end":      end_date,
                }
                st.session_state.mozgas_df = None
                st.session_state.last_mozgas_query = {}

        _last      = st.session_state.last_query or {}
        _need_load = (
            st.session_state.sales_df is None
            or _last.get("start") != start_date
            or _last.get("end") != end_date
        )

        if _need_load:
            if (end_date - start_date).days > 365:
                st.warning("⚠️ Ez sok adatot tölthet be, ami lassabb betöltést eredményezhet.")
            with funny_loader("Dashboard adatok betöltése...", load_warn(start_date, end_date)):
                _df = fetch_sales(None, start_date, end_date)
            if _df is not None:
                st.session_state.sales_df   = _df
                st.session_state.last_query = {
                    "cikkszam": None,
                    "label":    ALL_PRODUCTS_LABEL,
                    "start":    start_date,
                    "end":      end_date,
                }
                st.session_state.mozgas_df = None
                st.session_state.last_mozgas_query = {}
                st.session_state["_prod_opts_cache"] = build_product_opts(_df)

    elif page == "analytics":
        # Auto-reload sales data when dates change on analytics page too
        _last_an = st.session_state.last_query or {}
        if (
            st.session_state.sales_df is not None
            and (_last_an.get("start") != start_date or _last_an.get("end") != end_date)
        ):
            with funny_loader("Adatok frissítése...", load_warn(start_date, end_date)):
                _df = fetch_sales(None, start_date, end_date)
            if _df is not None:
                st.session_state.sales_df = _df
                st.session_state.last_query = {
                    "cikkszam": None,
                    "label":    ALL_PRODUCTS_LABEL,
                    "start":    start_date,
                    "end":      end_date,
                }
                st.session_state.mozgas_df = None
                st.session_state.last_mozgas_query = {}
                st.session_state["_prod_opts_cache"] = build_product_opts(_df)

    # ── Page routing ──────────────────────────────────────────────────────
    if page == "dashboard":
        render_dashboard()
    elif page == "analytics":
        render_analytics()


if __name__ == "__main__":
    main()
