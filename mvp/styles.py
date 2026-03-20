"""
Global CSS styles for SamanSport ERP Dashboard.
"""

import streamlit as st
from config import SIDEBAR_WIDTH


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
