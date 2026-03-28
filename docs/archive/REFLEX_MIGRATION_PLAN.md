# SamanSport — Streamlit → Reflex Migration Plan

**Date**: March 22, 2026
**Purpose**: Migrate the frontend from Streamlit to Reflex while preserving all backend logic. Designed as a Claude Code multi-agent orchestration.

---

## 1. Why Reflex

- **Pure Python** — no HTML, CSS, or JS required. Sidebar collapse is a Python component, not a DOM hack.
- **State classes** — cross-page state (dates, products, sidebar) lives in a Python class with automatic WebSocket sync. No scattered callbacks.
- **Built-in auth** — solves Phase 7 of the roadmap for free.
- **Plotly native** — `rx.plotly(data=fig)` directly wraps existing `charts.py` figures.
- **Compiles to React/Next.js** — production-grade frontend under the hood.
- **Hot reload** — save a file, see changes instantly at `localhost:3000`.

---

## 2. Migration Scope

### Files That DON'T Change (Backend — 0% rewrite)

| File | Why it stays |
|------|-------------|
| `tharanis_client.py` | Pure Python, queries Supabase + SOAP. Remove only `@st.cache_data` decorators and `st.session_state` refs. |
| `models.py` | Pydantic models. Framework-agnostic. |
| `helpers.py` | Date/number formatting utilities. Pure Python. |
| `config.py` | URLs, TTLs, API config. No Streamlit dependency. |
| `charts.py` | Plotly figure builders — Reflex wraps them via `rx.plotly(data=fig)`. |
| `seasonality_analyzer.py` | Domain logic. Pure Python. |
| `hydrate.py` | Bulk data loader. Pure Python. |
| All `supabase/` | Migrations, Edge Functions, config. Backend layer. |
| `tests/` | All existing tests stay. Add new Reflex-specific tests later. |

### Files That Get REWRITTEN (Frontend)

| Streamlit File | Reflex Replacement | What Changes |
|---------------|-------------------|-------------|
| `app.py` | `samansport/samansport.py` | Streamlit init → `rx.App()` with page routing |
| `layout.py` | `samansport/components/sidebar.py` | Full rewrite as Reflex component with real collapse |
| `theme.py` | `samansport/styles.py` + keep `theme.py` for chart colors | Colors become Reflex style dict + Tailwind classes |
| `pages/dashboard.py` | `samansport/pages/dashboard.py` | `st.columns/st.metric` → `rx.hstack/rx.box` + `rx.plotly` |
| `pages/analytics.py` | `samansport/pages/analytics.py` | `st.tabs/st.selectbox` → `rx.tabs` + `rx.select` + State class |

### New Files

| File | Purpose |
|------|---------|
| `rxconfig.py` | Reflex config (app name, port, etc.) |
| `samansport/__init__.py` | Package init |
| `samansport/samansport.py` | Main app module (`app = rx.App()`) |
| `samansport/state.py` | Shared app state: dates, sidebar, sync status |
| `samansport/styles.py` | Centralized Reflex styles dict + CSS custom properties |
| `samansport/components/__init__.py` | Components package |
| `samansport/components/sidebar.py` | Collapsible sidebar with nav, date controls |
| `samansport/components/kpi_cards.py` | Reusable KPI card component |
| `samansport/components/controls.py` | Date range, period toggle, preset pills |
| `samansport/pages/__init__.py` | Pages package (must import all pages) |
| `samansport/pages/dashboard.py` | Dashboard page |
| `samansport/pages/analytics.py` | Analytics page with tabs |
| `samansport/templates/__init__.py` | Templates package |
| `samansport/templates/template.py` | Shared page template (sidebar + content wrapper) |

---

## 3. State Architecture

In Streamlit, state is scattered across `st.session_state` keys. In Reflex, it's a clean Python class hierarchy:

```python
# samansport/state.py — Shared state
class AppState(rx.State):
    # Sidebar
    sidebar_collapsed: bool = False
    
    # Date range
    date_start: str = ""  # "2024.01.01"
    date_end: str = ""    # "2024.12.31"
    active_preset: str = ""  # "Ma", "Utolsó 7 nap", etc.
    period: str = "Havi"  # Éves/Havi/Heti/Napi
    
    # Sync
    last_synced: str = ""
    
    # Greeting
    @rx.var
    def greeting(self) -> str:
        """Hungarian time-based greeting."""
        from datetime import datetime
        hour = datetime.now().hour
        if hour < 12: return "Jó reggelt!"
        elif hour < 18: return "Jó napot!"
        else: return "Jó estét!"
    
    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed
    
    def set_preset(self, preset: str):
        """Compute date range from preset name."""
        # ... compute dates from preset ...
        self.active_preset = preset


# samansport/pages/dashboard.py — Dashboard-specific state
class DashboardState(AppState):
    revenue_data: list = []
    kpi_values: dict = {}
    loading: bool = False
    
    async def load_dashboard_data(self):
        self.loading = True
        yield  # UI update: show spinner
        # Call tharanis_client.get_sales(self.date_start, self.date_end)
        # Build charts with charts.py
        self.loading = False


# samansport/pages/analytics.py — Analytics-specific state
class AnalyticsState(AppState):
    active_tab: str = "ertekesites"
    selected_product: str = ""
    selected_metric: str = "brutto_bevetel"
    chart_type: str = "line"
    products_list: list[dict] = []
    sales_data: list = []
    movements_data: list = []
    
    async def load_products(self):
        """Load product list for dropdown — called on page load."""
        # Call tharanis_client.get_products()
    
    async def load_sales_data(self):
        """Load sales for selected product + date range."""
        # Call tharanis_client functions
    
    def export_csv(self):
        """Generate CSV download."""
        # Return rx.download(...)
```

**Key insight**: Substates (DashboardState, AnalyticsState) inherit from AppState. Changing a date in the sidebar updates `AppState.date_start`, which is automatically visible in all substates. No callback wiring needed.

---

## 4. Plotly Integration

Your existing `charts.py` functions return Plotly `Figure` objects. In Reflex, you just wrap them:

```python
# Streamlit (old):
st.plotly_chart(charts.build_revenue_chart(data, period), use_container_width=True)

# Reflex (new):
rx.plotly(data=DashboardState.revenue_chart, width="100%")

# In the state class:
class DashboardState(AppState):
    revenue_chart: go.Figure = go.Figure()
    
    async def load_dashboard_data(self):
        data = tharanis_client.get_sales(self.date_start, self.date_end)
        self.revenue_chart = charts.build_revenue_chart(data, self.period)
```

**Zero changes to `charts.py`**. The figures go straight into `rx.plotly()`.

---

## 5. Target File Structure

```
mvp/
├── rxconfig.py                       ← Reflex config
├── samansport/
│   ├── __init__.py
│   ├── samansport.py                 ← Main app: app = rx.App(style=BASE_STYLE)
│   ├── state.py                      ← AppState (shared: dates, sidebar, sync)
│   ├── styles.py                     ← Reflex style dicts + CSS variables from palette
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar.py                ← Collapsible sidebar: nav + date controls
│   │   ├── controls.py               ← Date picker, period toggle, preset pills
│   │   └── kpi_cards.py              ← KPI card builder
│   ├── pages/
│   │   ├── __init__.py               ← Imports all pages (required by Reflex!)
│   │   ├── dashboard.py              ← Dashboard + DashboardState
│   │   └── analytics.py              ← Analytics + AnalyticsState
│   └── templates/
│       ├── __init__.py
│       └── template.py               ← @template decorator: sidebar + content wrapper
├── assets/                           ← Static files (favicon, logo later)
│
├── config.py                         ← UNCHANGED — non-visual settings
├── theme.py                          ← UNCHANGED — chart color dict (used by charts.py)
├── charts.py                         ← UNCHANGED — Plotly figure builders
├── models.py                         ← UNCHANGED — Pydantic models
├── tharanis_client.py                ← MINOR EDIT — remove st.cache/session_state
├── helpers.py                        ← UNCHANGED — date/number formatting
├── seasonality_analyzer.py           ← UNCHANGED
├── hydrate.py                        ← UNCHANGED
├── tests/                            ← UNCHANGED
├── requirements.txt                  ← Updated: remove streamlit, add reflex
└── venv/
```

---

## 6. Multi-Agent System Design

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Master)                     │
│  Reads all existing Streamlit code → spawns agents →        │
│  gates phases → commits after each successful phase         │
└────────┬───────────┬───────────┬───────────┬───────────────┘
         │           │           │           │
   ┌─────▼─────┐     │     ┌─────▼─────┐    │
   │ PHASE 1   │     │     │ PHASE 2   │    │
   │ SCAFFOLD  │     │     │ PARALLEL  │    │
   │ (seq.)    │     │     │ BUILD     │    │
   │           │     │     │           │    │
   │ Agent S1  │     │     │ A1: Style │    │
   └───────────┘     │     │ A2: State │    │
                     │     │ A3: Layout│    │
                     │     │ A4: Dashb │    │
                     │     │ A5: Analy │    │
                     │     └───────────┘    │
                     │                      │
               ┌─────▼─────┐         ┌─────▼─────┐
               │ PHASE 3   │         │ PHASE 4   │
               │ INTEGRATE │         │ AUDIT     │
               │ (seq.)    │         │ (parallel)│
               │           │         │           │
               │ Agent I1  │         │ Q1: Code  │
               └───────────┘         │ Q2: Visual│
                                     │ Q3: Parity│
                                     └───────────┘
```

### Agent Roles

| Agent | Name | Role | Type |
|-------|------|------|------|
| **S1** | Scaffold Agent | Reflex init, folder structure, requirements, minimal running app | Builder |
| **A1** | Style Agent | Convert theme.py palette → Reflex styles dict + global CSS | Builder |
| **A2** | State Agent | Create state.py with AppState, date logic, sidebar toggle | Builder |
| **A3** | Layout Agent | Sidebar, template, controls — the collapsible sidebar that actually works | Builder |
| **A4** | Dashboard Agent | Dashboard page + DashboardState + KPI cards + charts | Builder |
| **A5** | Analytics Agent | Analytics page + AnalyticsState + tabs + product search + export | Builder |
| **I1** | Integration Agent | Wire everything, fix imports, ensure app runs end-to-end | Integrator |
| **Q1** | Code Quality Auditor | Review imports, types, dead Streamlit code, naming | Auditor |
| **Q2** | Visual Auditor | Playwright screenshots of every page state, verify polish | Auditor |
| **Q3** | Feature Parity Auditor | Checklist: every Streamlit feature exists and works in Reflex | Auditor |

---

## 7. Phase-by-Phase Execution

### PHASE 1 — Scaffold (Sequential, Agent S1)

**Goal**: A running Reflex app with placeholder pages and routing.

**Tasks**:
1. Create branch: `git checkout -b feature/reflex-migration` from `dev`
2. Update `requirements.txt`: remove `streamlit`, add `reflex>=0.6.0`
3. Run `cd mvp && reflex init` (select blank template, app name: `samansport`)
4. Adjust the generated structure to match Section 5 above
5. Create `rxconfig.py`:
   ```python
   import reflex as rx
   config = rx.Config(
       app_name="samansport",
       frontend_port=3000,
       backend_port=8000,
   )
   ```
6. Create minimal `samansport/samansport.py`:
   ```python
   import reflex as rx
   from samansport.pages import dashboard, analytics  # noqa: F401
   
   app = rx.App()
   ```
7. Create placeholder pages:
   - `pages/dashboard.py`: `@rx.page(route="/", title="Dashboard")` → returns `rx.text("Dashboard — loading...")`
   - `pages/analytics.py`: `@rx.page(route="/analytics", title="Analitika")` → returns `rx.text("Analitika — loading...")`
8. Import pages in `pages/__init__.py`
9. Verify: `reflex run` → app at `http://localhost:3000` shows placeholders, routing works
10. Do NOT delete old Streamlit files yet — agents need them for reference

**Commit**: `feat: scaffold Reflex app with multi-page routing`

---

### PHASE 2 — Parallel Build (Agents A1–A5, spawn simultaneously)

#### Agent A1 — Style System

**Read first**: `theme.py` (current palette)

**Tasks**:
1. Keep `theme.py` as-is (charts.py imports from it for Plotly figure colors)
2. Create `samansport/styles.py`:
   ```python
   # Grey-blue palette from theme.py, now as Reflex style dicts
   COLORS = {
       "bg_primary": "#FCFCFD",
       "bg_secondary": "#F8F9FC",
       "sidebar_dark": "#293056",
       "sidebar_mid": "#363F72",
       "accent": "#4E5BA6",
       "accent_light": "#6172CF",
       "text_primary": "#0D0F1C",
       "text_secondary": "#4A5578",
       "text_on_dark": "#D5D9EB",
       "border": "#D5D9EB",
       "card_bg": "#FFFFFF",
       "card_shadow": "0 1px 3px rgba(13,15,28,0.08)",
   }
   
   BASE_STYLE = {
       "font_family": "'Inter', -apple-system, sans-serif",
       "background": COLORS["bg_primary"],
       "color": COLORS["text_primary"],
       rx.heading: {"font_family": "'Inter', sans-serif"},
   }
   
   SIDEBAR_STYLE = { ... }          # Full width: 240px
   SIDEBAR_COLLAPSED_STYLE = { ... } # Collapsed: 60px
   KPI_CARD_STYLE = { ... }
   PRESET_PILL_STYLE = { ... }
   PRESET_PILL_ACTIVE_STYLE = { ... }
   ```
3. Wire `BASE_STYLE` into `app = rx.App(style=BASE_STYLE)` in the main module

**Output**: `samansport/styles.py`, minor update to `samansport/samansport.py`
**Commit**: `style: create Reflex style system from grey-blue palette`

#### Agent A2 — State

**Read first**: `layout.py` (for sidebar state), `tharanis_client.py` (for caching), `helpers.py` (for date formatting)

**Tasks**:
1. Create `samansport/state.py` with `AppState(rx.State)`:
   - `sidebar_collapsed: bool = False`
   - `date_start: str` — default to start of current year
   - `date_end: str` — default to today
   - `active_preset: str = "Idén"`
   - `period: str = "Havi"`
   - `last_synced: str = ""`
   - Computed var `greeting` — Hungarian time-based greeting
   - Event handler `toggle_sidebar`
   - Event handler `set_preset(preset: str)` — computes date_start/date_end from preset name (Ma, Utolsó 7 nap, Utolsó 30 nap, Idén, Tavaly)
   - Event handler `set_period(period: str)`
   - Event handler `set_date_range(start, end)` — clears active_preset
2. In `tharanis_client.py`:
   - Remove ALL `import streamlit` lines
   - Remove ALL `@st.cache_data` decorators
   - Remove ALL `st.session_state` references
   - Keep parquet caching and Supabase query logic untouched
3. All Hungarian text must use correct special characters (á, é, í, ó, ö, ő, ú, ü, ű)

**Output**: `samansport/state.py`, minor edit to `tharanis_client.py`
**Commit**: `feat: create AppState with date/sidebar/sync management`

#### Agent A3 — Layout (Sidebar + Template + Controls)

**Read first**: `layout.py` (current sidebar), `state.py` (from Agent A2), `styles.py` (from Agent A1)

**Tasks**:
1. Create `samansport/components/sidebar.py`:
   - Function `sidebar() → rx.Component`:
     - `rx.box` with conditional style: full width (240px) or collapsed (60px) based on `AppState.sidebar_collapsed`
     - Smooth CSS transition on width: `transition: "width 0.3s ease"`
     - **Top section**: App title "SamanSport" (hidden when collapsed, or abbreviated to "SS")
     - **Collapse button**: chevron icon that calls `AppState.toggle_sidebar`
     - **Nav links**: using `rx.link` with `rx.hstack(icon, text)`:
       - "Dashboard" → route "/"
       - "Analitika" → route "/analytics"
       - Active link highlighted with accent color
       - When collapsed: show only icons, hide text with `rx.cond(AppState.sidebar_collapsed, ...)`
     - **Date controls section** (hidden when collapsed): rendered from `controls.py`
     - **Bottom section**: greeting, last sync time

2. Create `samansport/components/controls.py`:
   - Function `date_controls() → rx.Component`:
     - Date pickers for start/end dates
     - Preset pill buttons in a `rx.hstack` with wrap:
       - Ma, Utolsó 7 nap, Utolsó 30 nap, Idén, Tavaly
       - Each calls `AppState.set_preset(name)`
       - Active preset gets `PRESET_PILL_ACTIVE_STYLE`
     - Period toggle: Éves / Havi / Heti / Napi as `rx.radio_group` or segmented buttons
       - Calls `AppState.set_period(value)`

3. Create `samansport/templates/template.py`:
   - `@template` decorator that wraps page content:
     ```python
     def template(page_fn):
         def wrapper():
             return rx.hstack(
                 sidebar(),
                 rx.box(
                     page_fn(),
                     # Main content expands when sidebar collapses
                     margin_left=rx.cond(AppState.sidebar_collapsed, "60px", "240px"),
                     transition="margin-left 0.3s ease",
                     width="100%",
                     padding="2rem",
                 ),
                 spacing="0",
                 width="100%",
                 min_height="100vh",
             )
         return wrapper
     ```

4. Every component must use styles from `styles.py`, not hardcoded values

**Output**: `components/sidebar.py`, `components/controls.py`, `templates/template.py`
**Commit**: `feat: collapsible sidebar with navigation and date controls`

#### Agent A4 — Dashboard Page

**Read first**: `pages/dashboard.py` (Streamlit version), `charts.py`, `helpers.py`, `tharanis_client.py`

**Tasks**:
1. Create `samansport/components/kpi_cards.py`:
   - Function `kpi_card(card_id, title, value_var, icon, tooltip_text) → rx.Component`:
     - `rx.box` with `KPI_CARD_STYLE`
     - Icon (emoji or Lucide icon via reflex)
     - Title in Hungarian
     - Value formatted using `helpers.format_number()`
     - `rx.tooltip` with Hungarian explanation
   - 4 cards: Bruttó bevétel, Eladott mennyiség, Átl. bruttó ár, Tranzakciók száma

2. Rewrite `samansport/pages/dashboard.py`:
   - `@rx.page(route="/", title="Dashboard", on_load=DashboardState.load_dashboard_data)`
   - `DashboardState(AppState)` substate:
     - `revenue_chart: go.Figure`
     - `quantity_chart: go.Figure`
     - `top10_chart: go.Figure`
     - `kpi_gross_revenue: str = "0"`
     - `kpi_quantity: str = "0"`
     - `kpi_avg_price: str = "0"`
     - `kpi_transactions: str = "0"`
     - `loading: bool = False`
     - `async def load_dashboard_data(self)` — calls `tharanis_client.get_sales()`, builds figures with `charts.py`, computes KPIs with `helpers.py`
   - Layout:
     - `rx.vstack`:
       - `rx.heading("Dashboard")` 
       - `rx.hstack` of 4 KPI cards
       - `rx.plotly(data=DashboardState.revenue_chart)` inside `rx.cond(DashboardState.loading, rx.spinner(), ...)`
       - `rx.plotly(data=DashboardState.quantity_chart)`
       - `rx.plotly(data=DashboardState.top10_chart)`
   - Apply `@template` decorator from `templates/template.py`

3. Charts are NOT rebuilt — call `charts.build_revenue_chart(data, period)` etc. exactly as today

**Output**: `components/kpi_cards.py`, `pages/dashboard.py`
**Commit**: `feat: migrate Dashboard page with KPIs and Plotly charts`

#### Agent A5 — Analytics Page

**Read first**: `pages/analytics.py` (Streamlit version), `charts.py`, `tharanis_client.py`

**Tasks**:
1. Rewrite `samansport/pages/analytics.py`:
   - `@rx.page(route="/analytics", title="Analitika", on_load=AnalyticsState.load_products)`
   - `AnalyticsState(AppState)` substate:
     - `active_tab: str = "ertekesites"`
     - `selected_product: str = ""`
     - `selected_metric: str = "brutto_bevetel"`
     - `chart_type: str = "line"`
     - `products_list: list[dict] = []`
     - `sales_chart: go.Figure = go.Figure()`
     - `sales_table_data: list[dict] = []`
     - `movements_chart: go.Figure = go.Figure()`
     - `movements_table_data: list[dict] = []`
     - `movements_summary: dict = {}`
     - `loading: bool = False`
     - `async def load_products(self)` — calls `tharanis_client.get_products()`
     - `async def load_sales_data(self)` — calls `tharanis_client`, builds chart + table
     - `async def load_movements_data(self)` — calls `tharanis_client`, builds chart + table
     - `def export_sales_csv(self)` — generates CSV with Hungarian filename
     - `def export_movements_csv(self)` — generates CSV

   - Layout:
     - `rx.tabs.root` with two tabs:
       - **Tab "Értékesítés"**:
         - `rx.select` (searchable product dropdown from `AnalyticsState.products_list`)
         - `rx.select` (metric: 6 options with Hungarian labels)
         - `rx.radio_group` (chart type: Vonal/Oszlop/Terület)
         - `rx.button("Betöltés", on_click=AnalyticsState.load_sales_data)`
         - `rx.plotly(data=AnalyticsState.sales_chart)` with loading wrapper
         - `rx.data_table` for sales data with Hungarian column headers
         - `rx.button("CSV Exportálás", on_click=AnalyticsState.export_sales_csv)`
       - **Tab "Mozgástörténet"**:
         - `rx.plotly(data=AnalyticsState.movements_chart)` with loading wrapper
         - Summary metrics row (total in/out, net movement)
         - `rx.data_table` for movements with Hungarian headers
         - CSV export button
   - Apply `@template` decorator

2. The 6 metric options (Hungarian labels):
   - Bruttó bevétel, Nettó bevétel, Eladott mennyiség, Átl. bruttó ár, Átl. nettó ár, Tranzakciók száma

**Output**: `pages/analytics.py`
**Commit**: `feat: migrate Analytics page with tabs, product search, and CSV export`

---

### PHASE 3 — Integration (Sequential, Agent I1)

**Goal**: App runs end-to-end with no errors.

**Tasks**:
1. Read ALL files created by Phase 2 agents
2. Ensure `pages/__init__.py` imports both page modules:
   ```python
   from samansport.pages import dashboard, analytics
   ```
3. Ensure `samansport/samansport.py` imports pages and state:
   ```python
   import reflex as rx
   from samansport.styles import BASE_STYLE
   from samansport.pages import dashboard, analytics  # noqa: F401
   
   app = rx.App(style=BASE_STYLE)
   ```
4. Check for import conflicts:
   - `state.py` must NOT import from page modules (circular dependency risk)
   - Pages import from `state.py`, `components/`, `charts.py`, `tharanis_client.py`, `helpers.py`
   - Components import from `state.py` and `styles.py`
5. Check that `charts.py` and `tharanis_client.py` can be imported from the new package structure (may need `sys.path` adjustment or move to be inside `samansport/`)
6. Run `reflex run` and verify:
   - Dashboard loads with real data
   - Navigate to Analytics — both tabs work
   - Sidebar collapses and expands smoothly
   - Main content area shifts when sidebar toggles
   - Date presets update the date range
   - Period toggle updates charts
   - Product search works in Analytics
   - CSV export downloads a file
7. Fix ANY errors, broken imports, missing components

**Commit**: `feat: integrate all components into working Reflex app`

---

### PHASE 4 — Audit (Parallel, Agents Q1–Q3)

#### Agent Q1 — Code Quality Auditor

**Checks**:
- [ ] Zero `import streamlit` or `st.` references anywhere in the codebase
- [ ] All imports resolve, no circular dependencies
- [ ] Type hints on all function signatures and State vars
- [ ] Consistent naming: snake_case functions, PascalCase State classes
- [ ] No hardcoded color values — all from `styles.py`
- [ ] `requirements.txt` updated and complete (no streamlit, has reflex)
- [ ] `.gitignore` includes `.web/` (Reflex build output)
- [ ] All Hungarian strings are correct (special characters intact)

**If issues found**: Fix them, list what was fixed.
**Commit**: `refactor: code quality pass on Reflex migration`

#### Agent Q2 — Visual Auditor

**Method**: Use Playwright MCP to screenshot every page/state at `http://localhost:3000`.

**Checks**:
- [ ] Dashboard loads with 4 KPI cards in a row
- [ ] Dashboard shows 3 charts (revenue, quantity, top 10)
- [ ] Analytics Értékesítés tab: product dropdown, metric selector, chart, table visible
- [ ] Analytics Mozgástörténet tab: stacked bar, metrics, table visible
- [ ] Sidebar at full width: nav links with icons + text, date controls visible
- [ ] **Sidebar collapse works on click** — collapses to icon-only (60px)
- [ ] Sidebar expand works — returns to full width (240px)
- [ ] Collapse/expand animation is smooth (not instant jump)
- [ ] Main content shifts left/right with sidebar
- [ ] Date preset pills are compact and styled (not default buttons)
- [ ] Grey-blue palette applied (not default Reflex colors)
- [ ] Hungarian characters render correctly (á, é, í, ó, ö, ő, ú, ü, ű)
- [ ] Charts are interactive (Plotly hover tooltips in Hungarian)
- [ ] Loading spinners appear during data fetch

**If issues found**: Report with screenshots, fix the styles/layout.
**Commit**: `fix: visual audit corrections`

#### Agent Q3 — Feature Parity Auditor

**Checklist** — every Streamlit feature must exist and work:

Dashboard:
- [ ] 4 KPI cards with correct values and Hungarian tooltips
- [ ] Period toggle (Éves/Havi/Heti/Napi) updates all charts
- [ ] Revenue trend chart (line + area fill)
- [ ] Quantity bar chart by period
- [ ] Top 10 Products horizontal bar chart with percentages

Analytics — Értékesítés:
- [ ] Searchable product selector (6500+ products)
- [ ] 6 metric options (all Hungarian labels)
- [ ] Chart type selector (line/bar/area)
- [ ] Betöltés button triggers data load
- [ ] Interactive Plotly chart
- [ ] Full data table with Terméknév column
- [ ] CSV export with meaningful Hungarian filename

Analytics — Mozgástörténet:
- [ ] Incoming/outgoing stacked bar chart
- [ ] Period selector + chart type toggle
- [ ] Summary metrics (total in/out, net movement)
- [ ] Data table
- [ ] CSV export

Sidebar & Navigation:
- [ ] Collapsible sidebar (THIS IS THE ONE THAT MUST WORK)
- [ ] Dashboard + Analitika nav links
- [ ] Active page highlighted
- [ ] Date range controls with auto-load
- [ ] Quick date presets (Ma, Utolsó 7 nap, Utolsó 30 nap, Idén, Tavaly)
- [ ] Time-based Hungarian greeting
- [ ] Last synced timestamp

Data:
- [ ] Hungarian number format (space as thousands separator)
- [ ] Hungarian date format (2024.01.15)
- [ ] Loading state for data fetches
- [ ] Data persists across page navigation (no re-fetch on tab switch)

**If any feature is missing**: Implement it, then verify again.
**Commit**: `feat: complete feature parity with Streamlit version`

---

## 8. Post-Migration Cleanup

After all 4 phases pass:

1. **Delete old Streamlit files**: `app.py` (old), `layout.py`, `run.bat` (old Streamlit version)
2. **Update launch scripts**: `run.sh` → `cd mvp && reflex run`
3. **Final merge**:
   ```bash
   git checkout dev
   git merge feature/reflex-migration
   git push origin dev
   git checkout master
   git merge dev
   git tag -a v0.4.0 -m "Migrate frontend from Streamlit to Reflex"
   git push origin master --tags
   ```
4. **Update CLAUDE.md / project docs** to reference Reflex instead of Streamlit
5. **Update roadmap**: Mark Phase 5 layout tasks as DONE (sidebar collapse, date pills, etc.)

---

## 9. Master Prompt for Claude Code

Copy everything below the line into Claude Code as a single prompt to kick off the migration.

---

```
# TASK: Migrate SamanSport frontend from Streamlit to Reflex

You are the **Orchestrator** for a full frontend migration. Use the Task tool to create sub-agents that work in parallel where indicated. Each agent must read the existing Streamlit files BEFORE writing replacements.

## PROJECT CONTEXT
- Working directory: /Users/zoltanszucs/zszucs/work/ppcagentlab/clients/SamanSport/app/mvp/
- Current framework: Streamlit (to be replaced)
- Target framework: Reflex (pure Python, compiles to React)
- All backend files stay UNCHANGED: tharanis_client.py, models.py, helpers.py, config.py, charts.py, seasonality_analyzer.py, hydrate.py, supabase/*, tests/*
- Only exception: remove @st.cache_data decorators and st.session_state refs from tharanis_client.py
- Plotly charts: use rx.plotly(data=fig) to wrap existing charts.py figure builders
- All UI text is in Hungarian with special characters (á, é, í, ó, ö, ő, ú, ü, ű)
- Color palette: grey-blue, primary accent #4E5BA6, sidebar #293056–#363F72

## CRITICAL RULES
1. Read before writing — every agent MUST read the Streamlit file it's replacing first
2. Never delete backend files or modify charts.py/helpers.py/config.py/models.py
3. Reuse charts.py as-is — call build_revenue_chart() etc. and pass figure to rx.plotly()
4. All state in Python classes (rx.State), NOT scattered variables
5. Commit after each phase, not after each agent
6. After each phase, run `reflex run` and verify the app works before proceeding

## PHASE 1 — SCAFFOLD (sequential)
Create a single agent (Agent S1):

Agent S1 task:
1. Read these files first: app.py, layout.py, theme.py, requirements.txt
2. git checkout -b feature/reflex-migration
3. Update requirements.txt: remove streamlit, add reflex>=0.6.0
4. Create Reflex app structure:
   - rxconfig.py (app_name="samansport")
   - samansport/__init__.py
   - samansport/samansport.py (app = rx.App())
   - samansport/pages/__init__.py
   - samansport/pages/dashboard.py (placeholder: @rx.page(route="/"))
   - samansport/pages/analytics.py (placeholder: @rx.page(route="/analytics"))
   - samansport/components/__init__.py
   - samansport/templates/__init__.py
   - assets/ directory
5. Verify: pip install reflex, then reflex run — app starts at localhost:3000
6. Do NOT delete old Streamlit files yet
7. Commit: "feat: scaffold Reflex app with multi-page routing"

Wait for Phase 1 to complete and verify app runs.

## PHASE 2 — BUILD (spawn 5 agents in parallel)
Launch these simultaneously:

### Agent A1 — Styles
Read theme.py → Create samansport/styles.py with:
- COLORS dict matching grey-blue palette (#FCFCFD to #0D0F1C, accent #4E5BA6, sidebar #293056)
- BASE_STYLE for rx.App()
- SIDEBAR_STYLE, SIDEBAR_COLLAPSED_STYLE (240px vs 60px, transition 0.3s)
- KPI_CARD_STYLE (rounded, shadow, accent border-top)
- PRESET_PILL_STYLE and PRESET_PILL_ACTIVE_STYLE (compact, rounded)
- Keep theme.py unchanged (charts.py depends on it)
- Wire BASE_STYLE into samansport.py

### Agent A2 — State
Read layout.py, tharanis_client.py, helpers.py → Create samansport/state.py with AppState(rx.State):
- sidebar_collapsed, date_start, date_end, active_preset, period, last_synced
- Computed var: greeting (Hungarian time-based)
- Event handlers: toggle_sidebar, set_preset, set_period, set_date_range
- Also: strip all st.cache_data and st.session_state from tharanis_client.py

### Agent A3 — Layout
Read layout.py, state.py, styles.py → Create:
- samansport/components/sidebar.py: collapsible sidebar (240px ↔ 60px with smooth transition), nav links with icons, date controls area, greeting + sync time at bottom. Uses rx.cond on AppState.sidebar_collapsed.
- samansport/components/controls.py: date pickers, preset pills (Ma/Utolsó 7 nap/Utolsó 30 nap/Idén/Tavaly), period toggle (Éves/Havi/Heti/Napi). Hidden when sidebar collapsed.
- samansport/templates/template.py: @template decorator wrapping sidebar + main content with matching margin transition.

### Agent A4 — Dashboard
Read pages/dashboard.py, charts.py, helpers.py → Create:
- samansport/components/kpi_cards.py: kpi_card() function returning styled card
- samansport/pages/dashboard.py: DashboardState(AppState) with revenue_chart, quantity_chart, top10_chart, 4 KPI values, loading flag. on_load triggers data fetch. Layout: 4 KPI cards → 3 rx.plotly charts. Apply @template decorator.

### Agent A5 — Analytics
Read pages/analytics.py, charts.py, tharanis_client.py → Create:
- samansport/pages/analytics.py: AnalyticsState(AppState) with tabs, product search, metrics, chart type, sales/movements data. Two tabs (Értékesítés + Mozgástörténet). Searchable product dropdown (6500+ items). CSV export via rx.download. Apply @template decorator.

Wait for ALL Phase 2 agents. Commit: "feat: build Reflex frontend with sidebar, dashboard, and analytics"

## PHASE 3 — INTEGRATION (sequential)
Agent I1: Read all Phase 2 output → ensure:
1. pages/__init__.py imports both pages
2. samansport.py imports pages + applies BASE_STYLE
3. No circular imports (state.py must not import page modules)
4. charts.py and tharanis_client.py are importable from the package
5. reflex run → Dashboard loads with real data → Analytics works → Sidebar collapses → CSV exports
6. Fix any errors
Commit: "feat: integrate all Reflex components"

## PHASE 4 — AUDIT (3 agents in parallel)

### Agent Q1 — Code Quality
Check: no st.* references, all imports resolve, type hints present, no hardcoded colors, requirements.txt complete, .gitignore has .web/
Fix any issues. Commit: "refactor: code quality audit"

### Agent Q2 — Visual Audit
Use Playwright MCP to screenshot localhost:3000:
- Dashboard with KPIs and charts
- Analytics both tabs
- Sidebar expanded and collapsed
- Sidebar collapse animation
- Date preset pills styled
- Hungarian characters correct
Fix any visual issues. Commit: "fix: visual audit corrections"

### Agent Q3 — Feature Parity
Verify EVERY feature from the Streamlit app exists: 4 KPIs, 3 dashboard charts, period toggle, product search (6500+), 6 metrics, chart type selector, CSV export with Hungarian filename, date presets, sidebar collapse, Hungarian number/date formatting, greeting, sync timestamp, loading states.
Implement anything missing. Commit: "feat: feature parity complete"

## AFTER ALL PHASES
1. Delete old Streamlit files (app.py old version, layout.py)
2. Update run scripts
3. Commit: "chore: remove old Streamlit files"
4. Report summary of what was done
```

---

## 10. Prompting Tips for Claude Code

These lessons from the first session still apply:

1. **If a phase fails**: Revert with `git checkout -- .` and re-run just that agent
2. **Use Playwright MCP for visual checks**: Append "Use Playwright to screenshot localhost:3000 and verify" to any visual agent
3. **One fix at a time**: If the auditor finds 5 issues, fix them one by one
4. **Reflex hot reload**: After any code change, just save — the browser updates automatically (no need to restart)
5. **If you see errors in the terminal**: Share them with Claude Code verbatim
6. **Reflex build cache**: If things get weird, try `reflex run --loglevel debug` or delete `.web/` and re-run

### Recovery Commands (Reflex)
```bash
reflex run                    # Start dev server (localhost:3000)
reflex run --loglevel debug   # Verbose mode for debugging
rm -rf .web && reflex run     # Clear build cache and restart
git checkout -- .             # Undo all uncommitted changes
git stash                     # Save changes aside
```
