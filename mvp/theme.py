"""
Visual constants for SamanSport ERP Dashboard.

Color palette, SVG icon library, sidebar navigation styles,
Plotly layout defaults, Hungarian number formatting, and global CSS.
"""

import streamlit as st

# ── Color palette ─────────────────────────────────────────────────────────────
C = {
    "blue":   "#2563eb",
    "teal":   "#2563eb",
    "indigo": "#4f46e5",
    "green":  "#10b981",
    "red":    "#ef4444",
    "orange": "#f59e0b",
    "purple": "#8b5cf6",
    "slate":  "#64748b",
    "coral":  "#e74c3c",
    "charcoal": "#1c1c2e",
    "sidebar_bg": "#1c1c2e",
    "sidebar_text": "#a0a3b1",
    "sidebar_active_bg": "rgba(231,76,60,0.15)",
}

# ── Sidebar width ─────────────────────────────────────────────────────────────
SIDEBAR_WIDTH = "15rem"

# ── Loader icons ──────────────────────────────────────────────────────────────
LOADER_ICONS = ["📦", "🗂️", "📊", "🏷️", "🔄"]

# ── SVG Icon Library ──────────────────────────────────────────────────────────
ICONS = {
    "grid":         '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
    "layout-dashboard": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "chart-column": '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "bar-chart":    '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>',
    "file-text":    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    "dollar-sign":  '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "package":      '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "tag":          '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
    "receipt":      '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1-2-1z"/><line x1="16" y1="8" x2="8" y2="8"/><line x1="16" y1="12" x2="8" y2="12"/>',
    "trending-up":  '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "warehouse":    '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "download":     '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "refresh-cw":   '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
    "activity":     '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "layers":       '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "info":         '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "database":     '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    "users":        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "calendar":     '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "filter":       '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "arrow-up-right":'<line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/>',
    "chevron-left":  '<polyline points="15 18 9 12 15 6"/>',
    "chevron-right": '<polyline points="9 18 15 12 9 6"/>',
    "settings":     '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    "log-out":      '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
    "user":         '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
}


def svg(name: str, size: int = 16, color: str = "currentColor") -> str:
    p = ICONS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{p}</svg>'
    )


# ── Sidebar navigation styles ────────────────────────────────────────────────
NAV_ACTIVE_STYLE = (
    "display:flex;align-items:center;gap:0.6rem;"
    "padding:0.4rem 0.65rem;border-radius:0.5rem;"
    "font-size:0.66rem;font-weight:500;font-family:'DM Sans',sans-serif;"
    "background:#e07a5f;color:#f9f7f4;"
    "box-shadow:0 4px 6px -1px rgba(0,0,0,0.1),0 2px 4px -2px rgba(0,0,0,0.1);"
    "height:2.1rem;box-sizing:border-box;"
)
NAV_INACTIVE_STYLE = (
    "display:flex;align-items:center;gap:0.6rem;"
    "padding:0.4rem 0.65rem;border-radius:0.5rem;"
    "font-size:0.66rem;font-weight:500;font-family:'DM Sans',sans-serif;"
    "background:transparent;color:rgba(224,217,209,0.6);"
    "height:2.1rem;box-sizing:border-box;"
)

# ── Plotly shared defaults ────────────────────────────────────────────────────
FONT_FAMILY = "Inter"

PLOTLY_BASE_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="#fafafa",
    font=dict(color="#374151", size=11, family=FONT_FAMILY),
    separators=", ",          # Hungarian: comma decimal, space thousands
    hovermode="x unified",
    showlegend=True,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        font=dict(size=13, family=FONT_FAMILY, color="#374151"),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(
        gridcolor="#f0f0f0", linecolor="#e5e7eb",
        tickfont=dict(color="#9ca3af", size=11), tickangle=-30,
    ),
    yaxis=dict(
        gridcolor="#f0f0f0", linecolor="#e5e7eb",
        tickfont=dict(color="#9ca3af", size=11), zeroline=False,
        separatethousands=True,
    ),
)

PLOTLY_NO_MODEBAR = {"displayModeBar": False}

# ── Hungarian number formatting ──────────────────────────────────────────────

def hu_thousands(n: float | int, decimals: int = 0) -> str:
    """Format a number with space as thousands separator (Hungarian convention).

    >>> hu_thousands(1234567)
    '1 234 567'
    >>> hu_thousands(1234567.5, 1)
    '1 234 567,5'
    """
    if decimals > 0:
        formatted = f"{n:,.{decimals}f}"
    else:
        formatted = f"{n:,.0f}"
    return formatted.replace(",", " ").replace(".", ",")


# ── Global CSS injection ─────────────────────────────────────────────────────

def inject_css() -> None:
    _sb_w = SIDEBAR_WIDTH
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

* {{ font-family: 'Inter', sans-serif !important; }}

/* ── Layout ── */
.main .block-container {{ padding: 1.5rem 1rem 1.5rem 1.75rem; max-width: 100%; }}
.main {{ background-color: #f8fafc; }}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ── Sidebar frame ── */
section[data-testid="stSidebar"] {{
    width: {_sb_w} !important;
    min-width: {_sb_w} !important;
    max-width: {_sb_w} !important;
}}
section[data-testid="stSidebar"] > div {{
    background: #221e1b !important;
    padding: 0 !important;
    border-right: none !important;
    width: {_sb_w} !important;
    overflow: hidden !important;
    height: 100vh !important;
}}
/* Hide EVERY native sidebar chrome button */
section[data-testid="stSidebar"] [data-testid*="Collapse"],
section[data-testid="stSidebar"] [data-testid*="collapse"],
[data-testid="collapsedControl"],
[data-testid*="baseButton-header"],
section[data-testid="stSidebar"] > div > button {{
    display: none !important;
}}
[data-testid="stSidebarUserContent"] {{
    padding: 0 !important;
    height: 100% !important;
}}

/* ── Sidebar: zero gaps between elements ── */
[data-testid="stSidebar"] .element-container {{ margin: 0 !important; }}
[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {{ gap: 0 !important; }}
[data-testid="stSidebar"] .stMarkdown {{ margin: 0 !important; }}
[data-testid="stSidebar"] .stMarkdown p {{ margin: 0 !important; }}

/* ── Sidebar nav buttons: transparent, overlaid on HTML nav rows ── */
[data-testid="stSidebar"] div.stButton {{
    margin-top: -2.1rem !important;
    margin-bottom: 0 !important;
    padding: 0 0.75rem !important;
    position: relative;
    z-index: 10;
}}
[data-testid="stSidebar"] div.stButton > button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: transparent !important;
    text-align: left !important;
    width: 100% !important;
    height: 2.1rem !important;
    padding: 0 !important;
    border-radius: 0.5rem !important;
    font-size: 0 !important;
    min-height: 0 !important;
    cursor: pointer !important;
}}
/* Hover on inactive nav: invisible button stays transparent, HTML row changes */
[data-testid="stSidebar"] div.stButton > button:hover {{
    background: transparent !important;
    border: none !important;
}}
/* When hovering inactive button, style the preceding HTML row: background + white text + white icon */
[data-testid="stSidebar"] .element-container:has(+ .element-container div.stButton > button:not([kind="primary"]):hover) div[style*="transparent"] {{
    background: #322c29 !important;
    color: #ffffff !important;
}}
[data-testid="stSidebar"] .element-container:has(+ .element-container div.stButton > button:not([kind="primary"]):hover) div[style*="transparent"] svg {{
    stroke: #ffffff !important;
}}
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
    background: transparent !important;
    border: none !important;
}}
[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {{
    background: transparent !important;
    border: none !important;
}}

/* ── KPI cards ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
    margin-bottom: 0.625rem;
}}
.kpi-card {{
    background: white;
    border-radius: 10px;
    padding: 0.65rem 0.85rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}}
.kpi-left {{ flex: 1; min-width: 0; }}
.kpi-label {{
    font-size: 0.55rem;
    font-weight: 500;
    color: #6b7280;
    margin-bottom: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.kpi-value {{
    font-size: 0.92rem;
    font-weight: 800;
    color: #111827;
    line-height: 1.1;
    letter-spacing: -0.03em;
}}
.kpi-sub {{
    font-size: 0.52rem;
    font-weight: 500;
    color: #9ca3af;
    margin-top: 0.2rem;
}}
.kpi-icon-box {{
    width: 30px;
    height: 30px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-left: 0.5rem;
}}

/* ── Section card ── */
.section-card {{
    background: white;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    padding: 1.25rem 1.25rem 0.75rem;
    margin-bottom: 1rem;
}}
.section-title {{
    font-size: 0.72rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.15rem;
}}
.section-sub {{
    font-size: 0.58rem;
    color: #9ca3af;
    margin-bottom: 0.75rem;
}}

/* ── Page header ── */
.page-hdr {{ margin-bottom: 1.25rem; }}
.page-hdr-title {{
    font-size: 1.12rem;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.03em;
}}
.page-hdr-sub {{
    font-size: 0.65rem;
    color: #6b7280;
    margin-top: 0.2rem;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: #f3f4f6;
    border-radius: 8px;
    padding: 0.2rem;
    gap: 0.1rem;
    border-bottom: none !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 6px;
    padding: 0.3rem 0.9rem;
    font-size: 0.65rem;
    font-weight: 500;
    color: #6b7280;
    background: transparent;
    border: none;
}}
.stTabs [aria-selected="true"] {{
    background: white !important;
    color: #111827 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1rem; }}

/* ── st.metric ── */
[data-testid="stMetricValue"] {{
    font-size: 0.76rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.51rem !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 600 !important;
}}

/* ── Radio controls ── */
.stRadio > label {{
    font-size: 0.53rem !important;
    font-weight: 600 !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}}
.stRadio [data-testid="stMarkdownContainer"] p {{
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
}}
div[role="radiogroup"] {{ gap: 0.15rem !important; }}

/* ── Selectbox ── */
.stSelectbox div[data-baseweb="select"] > div {{
    background: #f9fafb !important;
    border-color: #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.66rem !important;
    color: #111827 !important;
}}
.stSelectbox > label {{
    font-size: 0.53rem !important;
    font-weight: 600 !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}}

/* ── Empty state ── */
.empty-state {{
    text-align: center;
    padding: 3rem 1.5rem;
    background: white;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
}}
.empty-icon {{ margin: 0 auto 0.75rem; display: flex; justify-content: center; }}
.empty-title {{ font-size: 0.76rem; font-weight: 700; color: #374151; }}
.empty-sub {{ font-size: 0.65rem; color: #9ca3af; margin-top: 0.35rem; line-height: 1.5; }}

/* ── Badges ── */
.badge {{
    display: inline-flex;
    align-items: center;
    padding: 0.12rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.54rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    white-space: nowrap;
}}
.badge-red    {{ background: #fee2e2; color: #b91c1c; }}
.badge-orange {{ background: #fff7ed; color: #c2410c; }}
.badge-yellow {{ background: #fef9c3; color: #854d0e; }}
.badge-green  {{ background: #f0fdf4; color: #166534; }}
.badge-gray   {{ background: #f3f4f6; color: #6b7280; }}
.badge-blue   {{ background: #eff6ff; color: #1d4ed8; }}

/* ── Risk table ── */
.risk-table {{ width: 100%; border-collapse: collapse; font-size: 0.65rem; }}
.risk-table th {{
    text-align: left;
    padding: 0.4rem 0.65rem;
    font-size: 0.53rem;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    border-bottom: 1px solid #f1f5f9;
}}
.risk-table td {{
    padding: 0.5rem 0.65rem;
    border-bottom: 1px solid #f9fafb;
    color: #374151;
    vertical-align: middle;
}}
.risk-table tr:last-child td {{ border-bottom: none; }}
.risk-table tr:hover td {{ background: #f9fafb; }}

/* ── Selectbox dropdown ── */
[data-baseweb="menu"] {{
    min-width: min(720px, 90vw) !important;
    overflow-x: auto !important;
}}
[data-baseweb="menu"] [role="option"] {{
    white-space: nowrap !important;
}}

/* ── Main area primary button ── */
.main div.stButton > button[kind="primary"] {{
    background: #e74c3c !important;
    border-color: #e74c3c !important;
    color: white !important;
    padding: 0.25rem 0.8rem !important;
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    min-height: 0 !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(231,76,60,0.25) !important;
}}
.main div.stButton > button[kind="primary"]:hover {{
    background: #c0392b !important;
    border-color: #c0392b !important;
}}

/* ── Misc ── */
.hline {{ height: 1px; background: #f1f5f9; margin: 1rem 0; }}
.stDownloadButton > button {{
    background: #f9fafb !important;
    border: 1px solid #e5e7eb !important;
    color: #374151 !important;
    border-radius: 8px !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
}}
.stDownloadButton > button:hover {{
    background: #f3f4f6 !important;
    border-color: #d1d5db !important;
}}

/* ── Info banner ── */
.info-banner {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.65rem 0.85rem;
    background: rgba(231,76,60,0.06);
    border: 1px solid rgba(231,76,60,0.15);
    border-radius: 8px;
    font-size: 0.65rem;
    color: #e74c3c;
    margin-bottom: 0.85rem;
}}

/* ── Loading overlay ── */
@keyframes spinRing {{
    0%   {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}
@keyframes dashGrow {{
    0%   {{ stroke-dasharray: 1 150; stroke-dashoffset: 0; }}
    50%  {{ stroke-dasharray: 90 150; stroke-dashoffset: -35; }}
    100% {{ stroke-dasharray: 90 150; stroke-dashoffset: -125; }}
}}
.load-overlay {{
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: rgba(248, 250, 252, 0.97);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.85rem;
}}
.load-spinner-wrap {{
    position: relative;
    width: 60px;
    height: 60px;
}}
.load-ring-svg  {{ animation: spinRing 2s linear infinite; }}
.load-ring-arc  {{ animation: dashGrow 1.5s ease-in-out infinite; }}
.load-icon-center {{
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1.2rem;
    line-height: 1;
}}
.load-title {{
    font-size: 0.72rem;
    font-weight: 600;
    color: #e74c3c;
    text-align: center;
    letter-spacing: -0.01em;
}}
.load-warn {{
    font-size: 0.63rem;
    color: #374151;
    text-align: center;
    max-width: 340px;
    line-height: 1.5;
    padding: 0.55rem 0.9rem;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}}

/* ── Top header bar ── */
.top-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.35rem;
}}
.greeting-text {{
    font-size: 0.97rem;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.03em;
}}
.greeting-sub {{
    font-size: 0.63rem;
    color: #6b7280;
    margin-top: 0.1rem;
}}
.header-date {{
    font-size: 0.65rem;
    color: #6b7280;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.35rem;
    padding-top: 0.35rem;
}}

/* ── Main area date inputs ── */
.main .stDateInput input {{
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.63rem !important;
    color: #111827 !important;
    padding: 0.25rem 0.5rem !important;
}}
.main .stDateInput label {{
    font-size: 0.53rem !important;
    font-weight: 600 !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}}

/* ── Refresh icon button (no background, matches date input height) ── */
.refresh-icon-spacer {{
    height: 1.6rem;
}}
.main div.stButton:has(button[key="force_refresh_btn"]) > button,
.main div.stButton:has(button[key="force_refresh_btn"]) > button:focus,
.main div.stButton:has(button[key="force_refresh_btn"]) > button:active {{
    background: none !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    padding: 0.25rem 0.5rem !important;
    min-height: 0 !important;
    height: auto !important;
    width: auto !important;
    font-size: 1rem !important;
    line-height: 1 !important;
    color: #9ca3af !important;
    cursor: pointer !important;
    border-radius: 6px !important;
    transition: color 0.15s !important;
}}
.main div.stButton:has(button[key="force_refresh_btn"]) > button:hover {{
    color: #e74c3c !important;
    background: none !important;
    background-color: transparent !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    font-size: 0.65rem !important;
}}
</style>
""", unsafe_allow_html=True)
