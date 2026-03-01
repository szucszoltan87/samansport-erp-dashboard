# UI Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restyle SamanSport ERP app to match PulseERP reference with dark charcoal sidebar, coral accent, greeting header, and inline date picker.

**Architecture:** Single-file refactor of `mvp/app.py` — update CSS styles, restructure sidebar, move date picker to main content header area, add user profile/settings to sidebar bottom.

**Tech Stack:** Streamlit, Plotly, custom HTML/CSS (all existing)

---

### Task 1: Update Color Constants and Add New Icons

**Files:**
- Modify: `mvp/app.py:506-515` (C dictionary)
- Modify: `mvp/app.py:32-54` (add settings/logout icons)

**Step 1: Update color constants**

Change `C` dict at line 506 to add coral accent:
```python
C = {
    "blue":   "#2563eb",
    "teal":   "#2563eb",
    "indigo": "#4f46e5",
    "green":  "#10b981",
    "red":    "#ef4444",
    "orange": "#f59e0b",
    "purple": "#8b5cf6",
    "slate":  "#64748b",
    "coral":  "#e74c3c",        # NEW: sidebar active accent
    "sidebar_bg": "#1c1c2e",    # NEW: dark charcoal sidebar
    "sidebar_text": "#a0a3b1",  # NEW: muted sidebar text
    "sidebar_active_bg": "rgba(231,76,60,0.15)",  # NEW: coral tinted bg
}
```

**Step 2: Add missing SVG icons**

Add to `_ICONS` dict:
```python
"settings":     '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
"log-out":      '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
"user":         '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
```

**Step 3: Commit**
```bash
git add mvp/app.py
git commit -m "feat: add coral accent colors and new sidebar icons"
```

---

### Task 2: Rewrite Sidebar CSS for Dark Charcoal Theme

**Files:**
- Modify: `mvp/app.py:80-166` (sidebar CSS section)

**Step 1: Replace sidebar CSS**

Replace lines 80-166 with dark charcoal sidebar styles:

```css
/* ── Sidebar – dark charcoal ── */
[data-testid="stSidebar"] > div:first-child {
    background: #1c1c2e;
    padding: 0;
    border-right: none;
}
[data-testid="stSidebarUserContent"] {
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div > div:first-child {
    padding-top: 0 !important;
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p { color: #a0a3b1; }

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label {
    color: #6b7085 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.11em !important;
    font-weight: 700 !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] .stDateInput label p,
[data-testid="stSidebar"] .stSelectbox label p {
    font-size: inherit !important;
    font-weight: inherit !important;
    color: inherit !important;
    text-transform: inherit !important;
    letter-spacing: inherit !important;
}
[data-testid="stSidebar"] .stDateInput input {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(255,255,255,0.1) !important;
    color: #e2e4ea !important;
    border-radius: 8px !important;
    font-size: 0.72rem !important;
}

/* ── Sidebar nav buttons – dark ── */
[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #a0a3b1 !important;
    text-align: left !important;
    width: 100% !important;
    padding: 0.5rem 0.75rem !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    transition: background 0.15s, color 0.15s !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] div.stButton > button:hover {
    background: rgba(255,255,255,0.06) !important;
    color: #ffffff !important;
    border: none !important;
}
/* Active nav – coral accent */
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: rgba(231,76,60,0.15) !important;
    color: #e74c3c !important;
    font-weight: 600 !important;
    border: none !important;
}
/* Secondary nav buttons */
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #a0a3b1 !important;
    border: none !important;
    margin-top: 0.1rem !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.06) !important;
    color: #ffffff !important;
    border: none !important;
}
[data-testid="stSidebar"] .stSuccess {
    background: rgba(16,185,129,0.1) !important;
    color: #10b981 !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
    border-radius: 8px !important;
    font-size: 0.72rem !important;
    padding: 0.3rem 0.65rem !important;
}
```

**Step 2: Commit**
```bash
git add mvp/app.py
git commit -m "feat: dark charcoal sidebar CSS theme"
```

---

### Task 3: Rewrite Sidebar Layout (Brand, Nav, Settings, User Profile)

**Files:**
- Modify: `mvp/app.py:778-862` (render_sidebar function)

**Step 1: Rewrite render_sidebar()**

Replace the entire `render_sidebar()` function. Key changes:
- Dark-themed brand header with coral/white logo
- Navigation with just Dashboard + Analitika
- Settings button near bottom
- User profile (initials avatar, name, role, logout) at very bottom
- REMOVE date picker and refresh button from sidebar (moved to main area in Task 4)
- Return nothing (date picker will be handled elsewhere)

```python
def render_sidebar():
    with st.sidebar:
        # ── Brand header ──
        st.markdown("""
        <div style="padding:1rem 1rem 0.75rem;margin-top:0;">
            <div style="display:flex;align-items:center;gap:0.55rem;">
                <div style="width:28px;height:28px;background:#e74c3c;border-radius:7px;
                            display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                    <svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24'
                         fill='none' stroke='white' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>
                        <polyline points='23 6 13.5 15.5 8.5 10.5 1 18'/>
                        <polyline points='17 6 23 6 23 12'/>
                    </svg>
                </div>
                <div>
                    <div style="font-size:0.88rem;font-weight:800;color:#ffffff;letter-spacing:-0.02em;line-height:1.2;">SamanSport</div>
                    <div style="font-size:0.55rem;color:#6b7085;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;">ERP Analytics</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigation label ──
        st.markdown(
            '<div style="padding:0.5rem 1rem 0.15rem;font-size:0.68rem;font-weight:700;'
            'color:#6b7085;text-transform:uppercase;letter-spacing:0.11em;">Navigáció</div>',
            unsafe_allow_html=True,
        )

        pages = [
            ("dashboard", "grid",      "Dashboard"),
            ("analytics", "bar-chart", "Analitika"),
        ]
        for page_id, icon_name, label in pages:
            is_active = st.session_state.page == page_id
            icon_color = "#e74c3c" if is_active else "#6b7085"
            if st.button(
                f"  {label}", key=f"nav_{page_id}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.page = page_id
                st.rerun()

        # ── Spacer to push Settings + Profile to bottom ──
        st.markdown('<div style="flex:1;min-height:40vh;"></div>', unsafe_allow_html=True)

        # ── Settings ──
        st.markdown(
            '<div style="height:1px;background:rgba(255,255,255,0.06);margin:0.5rem 0;"></div>',
            unsafe_allow_html=True,
        )
        if st.button("  Beállítások", key="nav_settings", type="secondary", use_container_width=True):
            pass  # placeholder for future settings page

        # ── User profile ──
        st.markdown("""
        <div style="padding:0.75rem 1rem;display:flex;align-items:center;gap:0.6rem;
                    border-top:1px solid rgba(255,255,255,0.06);margin-top:0.5rem;">
            <div style="width:32px;height:32px;border-radius:50%;background:#e74c3c;
                        display:flex;align-items:center;justify-content:center;
                        color:white;font-size:0.7rem;font-weight:700;flex-shrink:0;">SS</div>
            <div style="flex:1;min-width:0;">
                <div style="font-size:0.78rem;font-weight:600;color:#e2e4ea;line-height:1.2;">SamanSport</div>
                <div style="font-size:0.6rem;color:#6b7085;">Admin</div>
            </div>
            <div style="cursor:pointer;opacity:0.5;">
                """ + svg("log-out", 14, "#a0a3b1") + """
            </div>
        </div>
        """, unsafe_allow_html=True)
```

**Step 2: Commit**
```bash
git add mvp/app.py
git commit -m "feat: dark sidebar with brand, nav, settings, user profile"
```

---

### Task 4: Add Greeting Header and Inline Date Picker to Main Content

**Files:**
- Modify: `mvp/app.py` — add new `render_header()` function before `render_dashboard()`
- Modify: `mvp/app.py:1277-1331` (main function)

**Step 1: Add header CSS**

Add these CSS rules to the global CSS block (before `</style>`):

```css
/* ── Top header bar ── */
.top-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
}
.greeting-text {
    font-size: 1.5rem;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.03em;
}
.greeting-sub {
    font-size: 0.875rem;
    color: #6b7280;
    margin-top: 0.15rem;
}
.header-date {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding-top: 0.5rem;
}
```

**Step 2: Add render_header() function**

Add after the helper functions, before `render_dashboard()`:

```python
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

    # Hungarian month names
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

    # ── Inline date range picker row ──
    _default_start = _today.replace(year=_today.year - 1)
    dc1, dc2, dc3 = st.columns([2, 2, 1])
    with dc1:
        start_date = st.date_input(
            "Kezdő dátum", key="start_date",
            value=_default_start, max_value=_today,
        )
    with dc2:
        end_date = st.date_input(
            "Záró dátum", key="end_date",
            value=_today, max_value=_today,
        )
    with dc3:
        st.markdown('<div style="height:1.6rem;"></div>', unsafe_allow_html=True)
        refresh_clicked = st.button(
            "🔄  Frissítés", key="force_refresh_btn",
            use_container_width=True, type="secondary",
        )

    return start_date, end_date, refresh_clicked
```

**Step 3: Update main() function**

Rewrite `main()` to:
1. Call `render_sidebar()` (no return value now)
2. Call `render_header()` which returns `start_date, end_date, refresh_clicked`
3. Handle refresh click + auto-load logic using those values
4. Route to dashboard/analytics

```python
def main():
    load_product_master()
    render_sidebar()
    start_date, end_date, refresh_clicked = render_header()

    # ── Handle refresh click ──
    _today = datetime.now().date()
    if refresh_clicked:
        with st.spinner("Friss adatok letöltése az API-ból..."):
            _r_df = fetch_sales(None, start_date, end_date, force_refresh=True)
        if _r_df is not None:
            st.session_state.sales_df = _r_df
            st.session_state.last_query = {
                "cikkszam": None,
                "label": ALL_PRODUCTS_LABEL,
                "start": start_date,
                "end": end_date,
            }
            st.session_state.mozgas_df = None
            st.session_state.last_mozgas_query = {}
            st.rerun()

    # ── Auto-load / reload when dates change ──
    _last = st.session_state.last_query or {}
    _need_load = (
        st.session_state.sales_df is None
        or _last.get("start") != start_date
        or _last.get("end") != end_date
    )
    if _need_load:
        with funny_loader("Dashboard adatok betöltése...", _load_warn(start_date, end_date)):
            _df = fetch_sales(None, start_date, end_date)
        if _df is not None:
            st.session_state.sales_df = _df
            st.session_state.last_query = {
                "cikkszam": None,
                "label": ALL_PRODUCTS_LABEL,
                "start": start_date,
                "end": end_date,
            }
            st.session_state.mozgas_df = None
            st.session_state.last_mozgas_query = {}
            _sc = find_sku_col(_df)
            _nc = find_name_col(_df)
            if _sc:
                _prows = (
                    _df[[_sc] + ([_nc] if _nc else [])]
                    .drop_duplicates(subset=[_sc])
                    .dropna(subset=[_sc])
                    .sort_values(_nc if _nc else _sc)
                )
                _cache = {ALL_PRODUCTS_LABEL: None}
                for _, _r in _prows.iterrows():
                    _lbl = (
                        f"{_r[_sc]}  –  {_r[_nc]}"
                        if _nc and pd.notna(_r.get(_nc))
                        else str(_r[_sc])
                    )
                    _cache[_lbl] = _r[_sc]
                st.session_state["_prod_opts_cache"] = _cache

    page = st.session_state.page
    if page == "dashboard":
        render_dashboard()
    elif page == "analytics":
        render_analytics()
```

**Step 4: Commit**
```bash
git add mvp/app.py
git commit -m "feat: greeting header with inline date picker in main content"
```

---

### Task 5: Update Page Headers to Match New Style

**Files:**
- Modify: `mvp/app.py` — `render_dashboard()` and `render_analytics()` page_header calls

**Step 1: Remove redundant page_header from dashboard**

Since we now have the greeting header, the Dashboard page no longer needs its own `page_header()` call. Remove the `page_header(...)` call at the top of `render_dashboard()` and the Analytics page's `page_header("Analitika")`.

Replace with lighter section context — or simply remove them since the greeting header already establishes context.

**Step 2: Update date input CSS for main area**

Add to global CSS to style the main-area date inputs compactly:

```css
/* ── Main area date inputs – compact ── */
.main .stDateInput input {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    color: #111827 !important;
    padding: 0.3rem 0.6rem !important;
}
.main .stDateInput label {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}
```

**Step 3: Commit**
```bash
git add mvp/app.py
git commit -m "feat: clean up page headers for new layout"
```

---

### Task 6: Visual QA and Polish

**Files:**
- Modify: `mvp/app.py` (minor CSS tweaks)

**Step 1: Run the app and verify visually**

Run: `cd mvp && streamlit run app.py`

Check:
- [ ] Dark charcoal sidebar renders correctly
- [ ] Brand logo is coral with white icon
- [ ] Nav items show coral highlight for active page
- [ ] Settings button appears near bottom of sidebar
- [ ] User profile (SS initials, SamanSport, Admin) at very bottom
- [ ] Greeting header shows correct time-of-day greeting
- [ ] Date picker row appears inline below greeting
- [ ] Refresh button works
- [ ] Dashboard KPI cards, charts load correctly
- [ ] Analytics page functions normally
- [ ] Loading overlay still works

**Step 2: Fix any visual issues found**

Adjust padding, colors, or spacing as needed.

**Step 3: Final commit**
```bash
git add mvp/app.py
git commit -m "fix: polish UI redesign styling"
```
