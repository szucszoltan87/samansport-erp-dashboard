"""
Analytics page – Sales analysis and warehouse movements.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from config import (
    ALL_PRODUCTS_LABEL, ALL_PRODUCTS_CODE,
    PERIOD_OPTIONS, METRIC_CFG,
)
from charts import metric_chart, movements_chart
from helpers import (
    period_key, find_sku_col, find_name_col, load_product_master,
    build_product_opts, section_header, empty_state, funny_loader,
    fetch_sales, fetch_movements, load_warn,
)

_PAGE_SIZE = 1000

# ── Sales view ────────────────────────────────────────────────────────────────
def _analytics_sales():
    # ── Pre-load: product selector (full-width) ───────────────────────────────
    products = load_product_master()
    if not products.empty:
        # Source 1: CSV product master (vectorized)
        prod_opts = build_product_opts(products)
    elif st.session_state.get("_prod_opts_cache"):
        # Source 2: list cached from initial all-products load
        prod_opts = st.session_state["_prod_opts_cache"]
    elif st.session_state.sales_df is not None and (st.session_state.last_query or {}).get("cikkszam") is None:
        # Source 3: build from sales_df (vectorized)
        prod_opts = build_product_opts(st.session_state.sales_df)
        st.session_state["_prod_opts_cache"] = prod_opts
    else:
        prod_opts = {ALL_PRODUCTS_LABEL: None}

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

    # ── Product details (shown when a specific product is selected) ──────────
    if sel_sku != ALL_PRODUCTS_CODE:
        _sku_code = sel_sku
        _sku_name = sel_label.split("  –  ", 1)[1] if "  –  " in sel_label else sel_label
        st.markdown(
            f'<div style="padding:0.5rem 0 0.25rem;color:#374151;font-size:0.78rem;">'
            f'<b>Cikkszám:</b> {_sku_code} &nbsp;&middot;&nbsp; '
            f'<b>Terméknév:</b> {_sku_name}</div>',
            unsafe_allow_html=True,
        )

    # ── Guard: nothing loaded yet — offer on-demand load ─────────────────────
    df   = st.session_state.sales_df
    meta = st.session_state.last_query or {}
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        _today = datetime.now().date()
        _an_start = st.session_state.get("start_date", _today.replace(year=_today.year - 1))
        _an_end   = st.session_state.get("end_date", _today)
        if (_an_end - _an_start).days > 365:
            st.warning("⚠️ Ez sok adatot tölthet be, ami lassabb betöltést eredményezhet.")
        if st.button("Értékesítési adatok betöltése", key="load_sales_an", type="primary"):
            warn = load_warn(_an_start, _an_end)
            with funny_loader("Értékesítési adatok betöltése...", warn):
                _an_df = fetch_sales(None, _an_start, _an_end)
            if _an_df is not None:
                st.session_state.sales_df = _an_df
                st.session_state.last_query = {
                    "cikkszam": None,
                    "label": ALL_PRODUCTS_LABEL,
                    "start": _an_start,
                    "end": _an_end,
                }
                st.session_state["_prod_opts_cache"] = build_product_opts(_an_df)
                st.rerun()
        else:
            empty_state(
                "bar-chart",
                "Nincs betöltött adat",
                "Kattintson az <b>Értékesítési adatok betöltése</b> gombra, "
                "vagy váltson a <b>Dashboard</b> oldalra az automatikus betöltéshez.",
            )
        return

    # ── Filter by selected product from the top selectbox ─────────────────────
    sc = find_sku_col(df)
    nc = find_name_col(df)
    loaded_cikkszam = meta.get("cikkszam")   # None → all products in memory
    display_label   = sel_label
    filter_sku      = None if sel_sku == ALL_PRODUCTS_CODE else sel_sku

    if loaded_cikkszam is None and sc and sel_sku != ALL_PRODUCTS_CODE:
        # All products loaded – filter to the selected one without re-fetching
        df            = df[df[sc] == sel_sku]
        display_label = sel_label
        filter_sku    = sel_sku

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
    section_header(
        metric,
        f"{display_label}  ·  {meta.get('start', '')} – {meta.get('end', '')}",
        "bar-chart",
    )
    metric_chart(grouped, col_name, metric, unit, ytitle, chart_type)

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
    # Add Terméknév from product master or existing name column
    _sc_full = find_sku_col(full)
    _nc_full = find_name_col(full)
    if _nc_full:
        full = full.rename(columns={_nc_full: "Terméknév"})
    elif _sc_full:
        _pm = load_product_master()
        if not _pm.empty:
            _name_map = _pm.set_index("Cikkszám")["Cikknév"]
            full.insert(
                full.columns.get_loc(_sc_full) + 1,
                "Terméknév",
                full[_sc_full].map(_name_map).fillna(""),
            )
    _total_rows = len(full)
    if _total_rows > _PAGE_SIZE:
        _total_pages = (_total_rows + _PAGE_SIZE - 1) // _PAGE_SIZE
        _page_num = st.number_input(
            f"Oldal (1–{_total_pages})", min_value=1, max_value=_total_pages,
            value=1, step=1, key="sales_table_page",
        )
        _start = (_page_num - 1) * _PAGE_SIZE
        _end = min(_start + _PAGE_SIZE, _total_rows)
        st.caption(f"{_start + 1}–{_end} / {_total_rows:,} sor")
        st.dataframe(full.iloc[_start:_end].reset_index(drop=True), use_container_width=True, height=400)
    else:
        st.dataframe(full.reset_index(drop=True), use_container_width=True, height=400)
    fn_sku = filter_sku.replace("/", "-") if filter_sku else "osszes"
    csv_bytes = full.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSV letöltése",
        data=csv_bytes,
        file_name=f"ertekesites_{fn_sku}_{meta.get('start', '')}.csv",
        mime="text/csv",
    )


# ── Movements view ────────────────────────────────────────────────────────────
def _analytics_movements():
    _today = datetime.now().date()
    start  = st.session_state.get("start_date", _today.replace(year=_today.year - 1))
    end    = st.session_state.get("end_date",   _today)

    # ── Load button ───────────────────────────────────────────────────────────
    if (end - start).days > 365:
        st.warning("⚠️ Ez sok adatot tölthet be, ami lassabb betöltést eredményezhet.")
    col_btn, col_status = st.columns([2, 3])
    with col_btn:
        if st.button("  Mozgástörténet betöltése", key="load_mozgas_an", type="secondary"):
            warn = load_warn(start, end)
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
    if mdf is None or (isinstance(mdf, pd.DataFrame) and mdf.empty):
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

    section_header(
        "Raktári mozgások",
        f"{meta_m.get('start', '')} – {meta_m.get('end', '')}",
        "activity",
    )
    movements_chart(all_p, be_v, ki_v, chart_m)

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
        _m_total = len(show_m)
        if _m_total > _PAGE_SIZE:
            _m_pages = (_m_total + _PAGE_SIZE - 1) // _PAGE_SIZE
            _m_page = st.number_input(
                f"Oldal (1–{_m_pages})", min_value=1, max_value=_m_pages,
                value=1, step=1, key="mozgas_table_page",
            )
            _m_start = (_m_page - 1) * _PAGE_SIZE
            _m_end = min(_m_start + _PAGE_SIZE, _m_total)
            st.caption(f"{_m_start + 1}–{_m_end} / {_m_total:,} sor")
            st.dataframe(show_m.iloc[_m_start:_m_end].reset_index(drop=True), use_container_width=True, height=300)
        else:
            st.dataframe(show_m.reset_index(drop=True), use_container_width=True, height=300)
        csv = show_m.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "CSV letöltése",
            data=csv,
            file_name=f"mozgas_osszes_{meta_m.get('start','')}.csv",
            mime="text/csv",
        )


# ── Analytics page entry point ────────────────────────────────────────────────
def render_analytics():
    view = st.radio(
        "Adatnézet",
        ["Értékesítés", "Mozgástörténet"],
        horizontal=True,
        key="an_view",
    )

    if view == "Értékesítés":
        _analytics_sales()
    else:
        _analytics_movements()
