"""
App shell layout – sidebar navigation and header bar.
"""

import logging
from datetime import datetime, timedelta

import streamlit as st

import tharanis_client as api
from theme import (
    svg, NAV_ACTIVE_STYLE, NAV_INACTIVE_STYLE,
    SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH,
)

logger = logging.getLogger(__name__)


def _inject_sidebar_width_css(collapsed: bool) -> None:
    """Inject CSS that sets the sidebar width based on collapsed state."""
    if collapsed:
        _w = SIDEBAR_COLLAPSED_WIDTH
        st.markdown(f"""<style>
section[data-testid="stSidebar"] {{
    width: {_w} !important; min-width: {_w} !important; max-width: {_w} !important;
}}
section[data-testid="stSidebar"] > div {{
    width: {_w} !important;
}}
/* Hide text labels when collapsed */
.sb-label, .sb-brand-text, .sb-status-block, .sb-bottom-text {{ display: none !important; }}
/* Centre icons in collapsed mode */
.sb-nav-row {{ justify-content: center !important; padding: 0.4rem !important; }}
.sb-bottom-block {{ width: {_w} !important; }}
.sb-bottom-block .sb-settings-row {{ justify-content: center !important; padding: 0.4rem !important; }}
.sb-bottom-block .sb-profile-row {{ justify-content: center !important; }}
.sb-bottom-block .sb-profile-details {{ display: none !important; }}
.sb-bottom-block .sb-logout-btn {{ display: none !important; }}
</style>""", unsafe_allow_html=True)


def render_sidebar():
    # ── Sidebar collapsed state ──────────────────────────────────────────
    if "sidebar_collapsed" not in st.session_state:
        st.session_state["sidebar_collapsed"] = False
    collapsed = st.session_state["sidebar_collapsed"]

    with st.sidebar:
        # Inject dynamic width CSS
        _inject_sidebar_width_css(collapsed)

        # ── Brand header + collapse toggle ───────────────────────────────
        _toggle_icon = "panel-left-close" if not collapsed else "panel-left-open"
        _brand_text = (
            '<span class="sb-brand-text">'
            ' Saman<span style="color:rgba(179,184,219,0.6);">Sport</span>'
            '</span>'
        )
        st.markdown(
            '<div style="padding:1.2rem 0.75rem 0.5rem;display:flex;'
            'align-items:center;justify-content:space-between;">'
            '<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1.02rem;'
            'font-weight:700;color:#D5D9EB;letter-spacing:-0.025em;line-height:1.2;'
            'display:flex;align-items:center;">'
            f'<span style="color:#4E5BA6;">&#9632;</span>{_brand_text}</div>'
            f'<div class="sb-toggle-icon">{svg(_toggle_icon, 18, "rgba(179,184,219,0.5)")}</div>'
            '</div>'
            '<div class="sb-status-block" style="padding:0 0.75rem 0.1rem;">'
            '<div style="font-family:\'DM Sans\',sans-serif;font-size:0.63rem;'
            'color:rgba(179,184,219,0.4);">ERP Elemzések</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        # Invisible toggle button overlaid on the icon
        if st.button("\u200b", key="sb_toggle"):
            st.session_state["sidebar_collapsed"] = not collapsed
            st.rerun()

        # ── Connection health check ─────────────────────────────────────
        if "_conn_health" not in st.session_state:
            st.session_state["_conn_health"] = api.check_connection()
        _health = st.session_state["_conn_health"]
        _dot_color = "#22c55e" if _health["ok"] else "#ef4444"
        _status_label = _health["mode"]
        if "_last_sync_ts" not in st.session_state:
            _raw_ts = api.get_last_sync_time()
            if _raw_ts:
                try:
                    _parsed = datetime.fromisoformat(_raw_ts.replace("Z", "+00:00"))
                    st.session_state["_last_sync_ts"] = _parsed.strftime("%Y.%m.%d %H:%M")
                except Exception:
                    st.session_state["_last_sync_ts"] = None
            else:
                st.session_state["_last_sync_ts"] = None
        _sync_display = st.session_state["_last_sync_ts"]
        _sync_line = (
            f'<br><span style="opacity:0.7;">Legutóbbi szinkronizálás: {_sync_display}</span>'
            if _sync_display else ""
        )

        st.markdown(
            f'<div class="sb-status-block" style="padding:0 1.5rem 0.75rem;font-size:0.6rem;'
            f'color:rgba(179,184,219,0.5);display:flex;align-items:center;gap:0.4rem;">'
            f'<span style="width:7px;height:7px;border-radius:50%;'
            f'background:{_dot_color};display:inline-block;"></span>'
            f'{_status_label}{_sync_line}</div>',
            unsafe_allow_html=True,
        )

        # ── Navigation items ─────────────────────────────────────────────
        _pages = [
            ("dashboard", "layout-dashboard", "Dashboard"),
            ("analytics", "chart-column",     "Analitika"),
        ]
        for page_id, icon_name, label in _pages:
            is_active = st.session_state.page == page_id
            style = NAV_ACTIVE_STYLE if is_active else NAV_INACTIVE_STYLE
            icon_c = "#FCFCFD" if is_active else "rgba(179,184,219,0.6)"
            chevron = (
                f'<span class="sb-label" style="margin-left:auto;opacity:0.7;">'
                f'{svg("chevron-right", 16, "#FCFCFD")}</span>'
                if is_active else ""
            )
            st.markdown(
                f'<div style="padding:0 0.75rem;">'
                f'<div class="sb-nav-row" style="{style}">'
                f'{svg(icon_name, 18, icon_c)}'
                f'<span class="sb-label">{label}</span>'
                f'{chevron}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            if st.button(
                "\u200b", key=f"nav_{page_id}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.page = page_id
                st.rerun()

        # ── Bottom: Settings + User profile (fixed to bottom) ────────────
        _sb_w = SIDEBAR_COLLAPSED_WIDTH if collapsed else SIDEBAR_WIDTH
        st.markdown(
            f'<div class="sb-bottom-block" style="position:fixed;bottom:0;width:{_sb_w};'
            f'background:#363F72;padding:0 0.75rem 1rem;z-index:20;">'
            f'<div class="sb-settings-row" style="{NAV_INACTIVE_STYLE}cursor:pointer;">'
            f'{svg("settings", 18, "rgba(179,184,219,0.6)")}'
            f'<span class="sb-label">Beállítások</span>'
            '</div>'
            '<div class="sb-profile-row" style="display:flex;align-items:center;gap:0.75rem;'
            'padding:0.75rem 0.75rem 0.25rem;border-top:1px solid #293056;'
            'margin-top:0.75rem;">'
            '<div style="width:32px;height:32px;border-radius:50%;'
            'background:rgba(78,91,166,0.2);'
            'display:flex;align-items:center;justify-content:center;'
            'color:#4E5BA6;font-size:0.54rem;font-weight:700;'
            "font-family:'Space Grotesk',sans-serif;flex-shrink:0;\">SS</div>"
            '<div class="sb-profile-details" style="min-width:0;">'
            '<div style="font-size:0.63rem;font-weight:500;color:#D5D9EB;'
            'line-height:1.2;white-space:nowrap;overflow:hidden;'
            'text-overflow:ellipsis;">SamanSport</div>'
            '<div style="font-size:0.53rem;color:rgba(179,184,219,0.4);">Adminisztrátor</div>'
            '</div>'
            '<div class="sb-logout-btn" style="margin-left:auto;flex-shrink:0;cursor:pointer;'
            'color:rgba(179,184,219,0.4);">'
            + svg("log-out", 16, "rgba(179,184,219,0.4)") +
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

    # ── Quick date range pill buttons ────────────────────────────────────
    _ranges = {
        "Ma":             (_today, _today),
        "7 nap":          (_today - timedelta(days=7), _today),
        "30 nap":         (_today - timedelta(days=30), _today),
        "Idén":           (_today.replace(month=1, day=1), _today),
        "Tavaly":         (_today.replace(year=_today.year - 1, month=1, day=1),
                           _today.replace(year=_today.year - 1, month=12, day=31)),
    }

    def _set_range(start, end):
        st.session_state["start_date"] = start
        st.session_state["end_date"] = end

    pill_cols = st.columns([1] * len(_ranges) + [max(1, 8 - len(_ranges))])
    for col, (label, (r_start, r_end)) in zip(pill_cols, _ranges.items()):
        with col:
            st.button(
                label, key=f"qr_{label}", use_container_width=True,
                on_click=_set_range, args=(r_start, r_end),
            )

    # ── Date pickers ──────────────────────────────────────────────────────
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
