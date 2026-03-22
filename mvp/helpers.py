"""
Shared UI components and data helpers for SamanSport ERP Dashboard.
"""

import contextlib
import logging
import os
import random

import streamlit as st
import pandas as pd
from datetime import timedelta

import tharanis_client as api
from config import CSV_PATH, ALL_PRODUCTS_LABEL
from theme import LOADER_ICONS, svg

logger = logging.getLogger(__name__)


# ── Data helpers ──────────────────────────────────────────────────────────────

def period_key(series: pd.Series, period: str) -> pd.Series:
    if period == "Éves":
        return series.dt.to_period("Y").astype(str)
    if period == "Havi":
        return series.dt.strftime("%Y-%m")
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


@st.cache_data(ttl=timedelta(hours=6), show_spinner="Termék lista betöltése…")
def load_product_master() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=["Cikkszám", "Cikknév"])
    df = pd.read_csv(
        CSV_PATH, usecols=[9, 10], dtype=str,
        encoding="utf-8-sig", on_bad_lines="skip",
    )
    df.columns = ["Cikkszám", "Cikknév"]
    return (
        df.dropna(subset=["Cikkszám", "Cikknév"])
        .drop_duplicates(subset=["Cikkszám"])
        .sort_values("Cikknév")
        .reset_index(drop=True)
    )


def build_product_opts(products: pd.DataFrame) -> dict[str, str | None]:
    """Build {label: sku} dict from a product DataFrame using vectorized ops."""
    opts: dict[str, str | None] = {ALL_PRODUCTS_LABEL: None}
    if products.empty:
        return opts
    sc = find_sku_col(products)
    nc = find_name_col(products)
    if not sc:
        return opts
    subset = (
        products[[sc] + ([nc] if nc else [])]
        .drop_duplicates(subset=[sc])
        .dropna(subset=[sc])
        .sort_values(nc if nc else sc)
    )
    if nc:
        labels = subset[sc].astype(str) + "  –  " + subset[nc].fillna("").astype(str)
    else:
        labels = subset[sc].astype(str)
    skus = subset[sc].tolist()
    for lbl, sku in zip(labels.tolist(), skus):
        opts[lbl] = sku
    return opts


# ── UI components ─────────────────────────────────────────────────────────────

def kpi_card(label: str, value: str, icon_name: str,
             icon_bg: str = "#eff6ff", icon_color: str = "#2563eb",
             sub: str = "", tooltip: str = "") -> str:
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    tip_attr = f' title="{tooltip}"' if tooltip else ""
    tip_icon = (
        '<span style="margin-left:0.3rem;color:#9ca3af;font-size:0.5rem;'
        'cursor:help;">&#9432;</span>'
        if tooltip else ""
    )
    return (
        f'<div class="kpi-card"{tip_attr}>'
        f'<div class="kpi-left">'
        f'<div class="kpi-label">{label}{tip_icon}</div>'
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
        f'{svg(icon_name, 15, "#4E5BA6")}</span>'
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
        f'<div class="info-banner">{svg(icon_name, 15, "#4E5BA6")}{text}</div>',
        unsafe_allow_html=True,
    )


# ── Fetch helpers ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=timedelta(hours=24), show_spinner="Értékesítési adatok betöltése…")
def _cached_get_sales(start_str: str, end_str: str,
                      cikkszam: str | None) -> pd.DataFrame | None:
    """In-memory cache (24h TTL) backed by Parquet disk cache in tharanis_client."""
    return api.get_sales(start_str, end_str, cikkszam)


@st.cache_data(ttl=timedelta(hours=24), show_spinner="Mozgásadatok betöltése…")
def _cached_get_movements(start_str: str, end_str: str,
                          cikkszam: str | None) -> pd.DataFrame | None:
    """In-memory cache (24h TTL) backed by Parquet disk cache in tharanis_client."""
    return api.get_stock_movements(start_str, end_str, cikkszam)


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
        logger.exception("fetch_sales failed (start=%s, end=%s, sku=%s)", start_str, end_str, cikkszam)
        st.error("Nem sikerült az értékesítési adatok lekérése. Kérjük, próbálja újra később.")
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
        logger.exception("fetch_movements failed (start=%s, end=%s, sku=%s)", start_str, end_str, cikkszam)
        st.error("Nem sikerült a mozgásadatok lekérése. Kérjük, próbálja újra később.")
        return None


def load_warn(start, end) -> str:
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
    return "Az adatok első betöltése folyamatban, ez eltarthat néhány másodpercig..."


# ── Loading overlay ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def funny_loader(label: str = "Adatok betöltése...", warn: str = ""):
    icon = random.choice(LOADER_ICONS)
    warn_html = f'<div class="load-warn">{warn}</div>' if warn else ""
    ph = st.empty()
    ph.markdown(
        f'<div class="load-overlay">'
        f'  <div class="load-spinner-wrap">'
        f'    <svg class="load-ring-svg" width="68" height="68" viewBox="0 0 68 68"'
        f'         xmlns="http://www.w3.org/2000/svg">'
        f'      <circle cx="34" cy="34" r="28" fill="none"'
        f'              stroke="rgba(78,91,166,0.15)" stroke-width="5"/>'
        f'      <circle class="load-ring-arc" cx="34" cy="34" r="28" fill="none"'
        f'              stroke="#4E5BA6" stroke-width="5" stroke-linecap="round"'
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
