"""
App shell layout – sidebar navigation and header bar.
"""

import streamlit as st
from datetime import datetime

import tharanis_client as api
from theme import svg, NAV_ACTIVE_STYLE, NAV_INACTIVE_STYLE


def render_sidebar():
    with st.sidebar:
        # ── Brand header ──────────────────────────────────────────────────
        st.markdown(
            '<div style="padding:1.5rem 1.5rem 1rem;">'
            '<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1.02rem;'
            'font-weight:700;color:#e0d9d1;letter-spacing:-0.025em;line-height:1.2;">'
            '<span style="color:#e07a5f;">&#9632;</span> '
            'Saman<span style="color:rgba(224,217,209,0.6);">Sport</span></div>'
            '<div style="font-family:\'DM Sans\',sans-serif;font-size:0.63rem;'
            'color:rgba(224,217,209,0.4);margin-top:0.25rem;">ERP Analytics</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Connection health check ─────────────────────────────────────
        if "_conn_health" not in st.session_state:
            st.session_state["_conn_health"] = api.check_connection()
        _health = st.session_state["_conn_health"]
        _dot_color = "#22c55e" if _health["ok"] else "#ef4444"
        _status_label = _health["mode"]
        st.markdown(
            f'<div style="padding:0 1.5rem 0.75rem;font-size:0.6rem;'
            f'color:rgba(224,217,209,0.5);display:flex;align-items:center;gap:0.4rem;">'
            f'<span style="width:7px;height:7px;border-radius:50%;'
            f'background:{_dot_color};display:inline-block;"></span>'
            f'{_status_label}</div>',
            unsafe_allow_html=True,
        )

        # ── Navigation items (PulseERP style) ─────────────────────────────
        _pages = [
            ("dashboard", "layout-dashboard", "Dashboard"),
            ("analytics", "chart-column",     "Analitika"),
        ]
        for page_id, icon_name, label in _pages:
            is_active = st.session_state.page == page_id
            style = NAV_ACTIVE_STYLE if is_active else NAV_INACTIVE_STYLE
            icon_c = "#f9f7f4" if is_active else "rgba(224,217,209,0.6)"
            # Chevron on right for active item
            chevron = (
                f'<span style="margin-left:auto;opacity:0.7;">'
                f'{svg("chevron-right", 16, "#f9f7f4")}</span>'
                if is_active else ""
            )
            # Render the visual HTML nav row (wrapped with horizontal padding)
            st.markdown(
                f'<div style="padding:0 0.75rem;">'
                f'<div style="{style}">'
                f'{svg(icon_name, 18, icon_c)}'
                f'<span>{label}</span>'
                f'{chevron}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            # Invisible clickable button overlaid via CSS margin-top: -2.55rem
            if st.button(
                label, key=f"nav_{page_id}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.page = page_id
                st.rerun()

        # ── Bottom: Settings + User profile (fixed to bottom) ─────────────
        st.markdown(
            '<div style="position:fixed;bottom:0;width:15rem;'
            'background:#221e1b;padding:0 0.75rem 1rem;z-index:20;">'
            # Settings row (same style as inactive nav)
            f'<div style="{NAV_INACTIVE_STYLE}cursor:pointer;">'
            f'{svg("settings", 18, "rgba(224,217,209,0.6)")}'
            '<span>Beállítások</span>'
            '</div>'
            # User profile
            '<div style="display:flex;align-items:center;gap:0.75rem;'
            'padding:0.75rem 0.75rem 0.25rem;border-top:1px solid #37322f;'
            'margin-top:0.75rem;">'
            '<div style="width:32px;height:32px;border-radius:50%;'
            'background:rgba(224,122,95,0.2);'
            'display:flex;align-items:center;justify-content:center;'
            'color:#e07a5f;font-size:0.54rem;font-weight:700;'
            'font-family:\'Space Grotesk\',sans-serif;flex-shrink:0;">SS</div>'
            '<div style="min-width:0;">'
            '<div style="font-size:0.63rem;font-weight:500;color:#e0d9d1;'
            'line-height:1.2;white-space:nowrap;overflow:hidden;'
            'text-overflow:ellipsis;">SamanSport</div>'
            '<div style="font-size:0.53rem;color:rgba(224,217,209,0.4);">Admin</div>'
            '</div>'
            '<div style="margin-left:auto;flex-shrink:0;cursor:pointer;color:rgba(224,217,209,0.4);">'
            + svg("log-out", 16, "rgba(224,217,209,0.4)") +
            '</div></div></div>',
            unsafe_allow_html=True,
        )


def render_header():
    """Top greeting + date display, then inline date range picker row."""
    _today = datetime.now().date()
    _hour = datetime.now().hour
    if _hour < 12:
        greeting = "Jó reggelt"
    elif _hour < 18:
        greeting = "Jó napot"
    else:
        greeting = "Jó estét"

    _hu_months = {
        1: "jan.", 2: "febr.", 3: "márc.", 4: "ápr.", 5: "máj.", 6: "jún.",
        7: "júl.", 8: "aug.", 9: "szept.", 10: "okt.", 11: "nov.", 12: "dec.",
    }
    date_str = f"{_today.year}. {_hu_months[_today.month]} {_today.day}."

    st.markdown(
        f'<div class="top-header">'
        f'  <div>'
        f'    <div class="greeting-text">{greeting}! 👋</div>'
        f'    <div class="greeting-sub">Itt találod az üzleti áttekintést és elemzéseket.</div>'
        f'  </div>'
        f'  <div class="header-date">'
        f'    {svg("calendar", 15, "#6b7280")} {date_str}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    dc1, dc2, dc3 = st.columns([5, 5, 1])
    with dc1:
        start_date = st.date_input(
            "Kezdő dátum", key="start_date",
            max_value=_today,
        )
    with dc2:
        end_date = st.date_input(
            "Záró dátum", key="end_date",
            max_value=_today,
        )
    with dc3:
        st.markdown('<div class="refresh-icon-spacer"></div>', unsafe_allow_html=True)
        refresh_clicked = st.button(
            "⟳", key="force_refresh_btn",
            help="Frissítés",
        )

    return start_date, end_date, refresh_clicked
