# SamanSport — MVP → Production Roadmap

**Goal**: Take the existing Streamlit MVP (with Supabase backend & Tharanis SOAP integration) to a fully functioning, production-grade app ready to present to Tharanis.

**How to use this file**: Copy this into your repo root. Tick boxes `[x]` as you complete each step. Use the Claude Code prompts as starting points — paste or adapt them in your VS Code terminal.

---

## Legend

- ⬜ = Not started
- 🔧 = In progress
- ✅ = Done
- 🧠 = Claude Code prompt tip included
- ⚠️ = Blocker / dependency

---

## Phase 0 — Project Setup & Orientation (Day 1)

*Get Claude Code fully loaded with project context so every subsequent prompt is accurate.*

### 0.1 Repository & Environment

- [ ✅ ] **0.1.1** Clone the repo into your VS Code workspace
- [ ✅ ] **0.1.2** Verify Python 3.12+ is active (`python --version`)
- [ ✅ ] **0.1.3** Create/activate a virtual environment (`python -m venv .venv && source .venv/bin/activate`)
- [ ✅ ] **0.1.4** Install dependencies (`pip install -r requirements.txt`) — if no requirements.txt exists, generate one from the current imports
- [ ✅ ] **0.1.5** Verify `.env` file exists with all required keys: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, SOAP credentials
- [ ✅ ] **0.1.6** Run the app locally (`streamlit run mvp/app.py`) and confirm the Dashboard loads with real data
- [ ✅ ] **0.1.7** Confirm Supabase project is accessible (check tables via Supabase dashboard or `psql`)
- [✅  ] **0.1.8** Confirm Edge Functions are deployed and responding (hit `check-freshness` endpoint manually)

> 🧠 **Claude Code setup prompt**:
> *"Read every file in the `mvp/` directory and the `supabase/` directory. Summarize the architecture, list all environment variables used, and identify any hardcoded values that should be moved to config. Also read BACKEND_ARCHITECTURE.md for context."*

### 0.2 Create a CLAUDE.md Context File

- [ ✅ ] **0.2.1** Create a `CLAUDE.md` file in the repo root that Claude Code will auto-read on every session. Include:
  - Project name, purpose, client name (SamanSport)
  - Tech stack summary (Streamlit, Supabase, Deno Edge Functions, Tharanis SOAP V3)
  - File structure overview
  - Key architectural decisions (stale-while-revalidate, atomic locks, entity TTLs)
  - Hungarian UI language requirement
  - Naming conventions (e.g., `snake_case` for Python, `camelCase` for TypeScript)
  - Links to Tharanis API docs and Supabase project
  - Current known issues / tech debt

> 🧠 **Claude Code prompt**:
> *"Based on BACKEND_ARCHITECTURE.md, and the codebase, generate a comprehensive CLAUDE.md context file that future Claude Code sessions can use to understand this project instantly. Include architecture, conventions, known issues, and key decisions."*

---

## Phase 1 — Code Quality & Technical Debt (Days 2–4)

*Clean up the MVP code so it's maintainable, testable, and ready for new features.*

### 1.1 Code Structure & Organization

- [ ] **1.1.1** Create a proper Python package structure:
  ```
  samansport/
    __init__.py
    config.py          # All env vars, constants, settings
    models.py           # Pydantic models or dataclasses for Sales, Inventory, Movement, Product
    tharanis_client.py  # Supabase reads + SOAP fallback (existing, refactored)
    cache.py            # 3-tier cache logic extracted from app.py
    charts.py           # All Plotly chart-building functions
    utils.py            # Date helpers, Hungarian formatting, currency formatting
    pages/
      __init__.py
      dashboard.py      # Dashboard page logic
      analytics.py      # Analytics page logic (Ertekesites + Mozgastortenet tabs)
  app.py                # Streamlit entry point — thin, just imports pages
  ```
- [ ] **1.1.2** Extract all Plotly chart-building code from `app.py` into `charts.py`
- [ ] **1.1.3** Extract all caching logic into `cache.py`
- [ ] **1.1.4** Extract config/constants (API URLs, TTLs, color palette, date formats) into `config.py`
- [ ] **1.1.5** Move each page's rendering logic into its own module under `pages/`
- [ ] **1.1.6** Ensure `app.py` is under 100 lines — it should only set up the Streamlit app shell and route to pages

> 🧠 **Claude Code prompt**:
> *"Refactor mvp/app.py into a clean package structure. Extract chart-building functions into charts.py, caching logic into cache.py, config into config.py, and each page into pages/dashboard.py and pages/analytics.py. Keep app.py as a thin entry point under 100 lines. Preserve all existing functionality — don't change behavior, only structure."*

> 💡 **Agenting tip**: This is a big refactor. Break it into sub-prompts:
> 1. First: "Extract all configuration constants from app.py into config.py"
> 2. Then: "Extract all Plotly chart functions from app.py into charts.py, import them back"
> 3. Then: "Extract dashboard page rendering into pages/dashboard.py"
> 4. Then: "Extract analytics page rendering into pages/analytics.py"
> 5. Finally: "Slim down app.py to only import and route to pages"
> Run the app after each step to confirm nothing broke.

### 1.2 Type Safety & Data Models

- [ ] **1.2.1** Create Pydantic models (or dataclasses) for: `SalesInvoiceLine`, `InventorySnapshot`, `WarehouseMovement`, `Product`, `SyncStatus`
- [ ] **1.2.2** Add type hints to every function in `tharanis_client.py`
- [ ] **1.2.3** Add type hints to all chart-building functions
- [ ] **1.2.4** Run `mypy` or `pyright` and fix any type errors

> 🧠 **Claude Code prompt**:
> *"Create Pydantic models in models.py matching the Supabase schema from BACKEND_ARCHITECTURE.md. Add full type hints to tharanis_client.py and charts.py. Then run mypy and fix any issues."*

### 1.3 Error Handling & Resilience

- [ ] **1.3.1** Add try/except blocks around all Supabase queries in `tharanis_client.py` with meaningful error messages
- [ ] **1.3.2** Add try/except around all SOAP fallback calls with timeout handling (10s default)
- [ ] **1.3.3** Add a user-facing error banner in Streamlit when data fetch fails (not a raw Python traceback)
- [ ] **1.3.4** Handle empty data gracefully — show "Nincs adat a megadott időszakra" (No data for the given period) instead of crashing
- [ ] **1.3.5** Add connection health check on app startup — verify Supabase is reachable, show status in sidebar
- [ ] **1.3.6** Handle edge case: what happens when Edge Function sync fails mid-way? Ensure partial data doesn't corrupt the cache

> 🧠 **Claude Code prompt**:
> *"Audit tharanis_client.py for unhandled exceptions. Wrap all Supabase calls and SOAP calls in try/except with user-friendly error messages. Add a connection health check function. Handle empty DataFrames in charts.py (show placeholder message, not crash)."*

### 1.4 Requirements & Dependency Management

- [ ] **1.4.1** Generate `requirements.txt` with pinned versions (`pip freeze > requirements.txt`)
- [ ] **1.4.2** Add a `pyproject.toml` or `setup.py` if you want a proper installable package
- [ ] **1.4.3** Document the Node.js / Deno requirements for Edge Functions in a `supabase/README.md`

---

## Phase 2 — Testing (Days 4–6)

*Build a test suite so you can refactor and add features with confidence.*

### 2.1 Unit Tests

- [ ] **2.1.1** Set up `pytest` and create `tests/` directory structure:
  ```
  tests/
    __init__.py
    conftest.py           # Shared fixtures (mock Supabase client, sample DataFrames)
    test_tharanis_client.py
    test_cache.py
    test_charts.py
    test_utils.py
    test_models.py
  ```
- [ ] **2.1.2** Write fixtures that create sample DataFrames matching the Supabase schema (sales, inventory, movements, products)
- [ ] **2.1.3** Test `tharanis_client.py`: mock Supabase responses, test cache-hit path, test stale-trigger path, test SOAP fallback path
- [ ] **2.1.4** Test `cache.py`: test session cache write/read, test TTL expiry logic, test Parquet disk cache
- [ ] **2.1.5** Test `charts.py`: each chart function returns a valid Plotly figure given sample data, and returns a placeholder on empty data
- [ ] **2.1.6** Test `utils.py`: date formatting, Hungarian number formatting, currency display
- [ ] **2.1.7** Test `models.py`: Pydantic validation accepts correct data, rejects bad data

> 🧠 **Claude Code prompt**:
> *"Create a pytest test suite for the samansport package. Start with conftest.py containing fixtures with realistic sample data matching our Supabase schema. Then write tests for tharanis_client.py (mock Supabase with unittest.mock.patch), charts.py (verify Plotly figure output), and utils.py. Aim for >80% coverage on the client and utils modules."*

### 2.2 Integration Tests

- [ ] **2.2.1** Write a test that calls Supabase (using a test/staging project or the real one with read-only queries) and verifies the response shape
- [ ] **2.2.2** Write a test that calls the `check-freshness` Edge Function and verifies the JSON response
- [ ] **2.2.3** Write a smoke test that starts Streamlit headlessly and verifies no crash on load

### 2.3 Edge Function Tests

- [ ] **2.3.1** Write Deno test files for `sync-entity` (mock the SOAP response, verify upsert logic)
- [ ] **2.3.2** Write tests for `xml-parser.ts` with sample Tharanis XML payloads
- [ ] **2.3.3** Write tests for `soap-client.ts` envelope construction

> 🧠 **Claude Code prompt**:
> *"Read supabase/functions/_shared/xml-parser.ts. Write Deno tests (using Deno.test) that verify XML parsing for each entity type: kimeno_szamla, keszlet, raktari_mozgas, cikk. Use realistic sample XML payloads based on the Tharanis API structure."*

---

## Phase 3 — Security Hardening (Days 6–8)

*Critical before any production deployment or Tharanis demo.*

### 3.1 Secrets Management

- [ ] **3.1.1** Audit `.env` for any secrets that shouldn't be there (e.g., service role key in frontend)
- [ ] **3.1.2** Ensure `.env` is in `.gitignore` (verify it's not committed in any historical commit)
- [ ] **3.1.3** Create `.env.example` with placeholder values and comments
- [ ] **3.1.4** Move SOAP credentials (username/password) to Supabase Vault or Edge Function secrets — never expose them to the frontend
- [ ] **3.1.5** Ensure the frontend only uses `SUPABASE_ANON_KEY` (not the service role key)
- [ ] **3.1.6** Add Supabase Row Level Security (RLS) policies on all entity tables — at minimum, read-only for the anon key

> 🧠 **Claude Code prompt**:
> *"Audit the entire codebase for security issues. Check: (1) Are SOAP credentials exposed to the frontend? (2) Is the Supabase service role key used anywhere in Python? (3) Is .env in .gitignore? (4) Are there any hardcoded API keys? Generate a security report with findings and fixes."*

### 3.2 Supabase RLS & Permissions

- [ ] **3.2.1** Write RLS policies: `anon` role gets SELECT-only on `sales_invoice_lines`, `inventory_snapshot`, `warehouse_movements`, `products`
- [ ] **3.2.2** Write RLS policy: `anon` role gets SELECT-only on `sync_metadata` (for freshness checks)
- [ ] **3.2.3** Write RLS policy: `service_role` (used by Edge Functions) gets full CRUD
- [ ] **3.2.4** Test: confirm the anon key cannot INSERT/UPDATE/DELETE
- [ ] **3.2.5** Create a new Supabase migration: `005_enable_rls.sql`

> 🧠 **Claude Code prompt**:
> *"Write a Supabase migration file 005_enable_rls.sql that enables Row Level Security on all entity tables (sales_invoice_lines, inventory_snapshot, warehouse_movements, products, sync_metadata, entity_config). Add policies: anon can SELECT only, service_role can do everything."*

### 3.3 Input Validation & Rate Limiting

- [ ] **3.3.1** Validate date range inputs in `tharanis_client.py` (no future dates, start ≤ end, max range 5 years)
- [ ] **3.3.2** Sanitize SKU inputs before passing to Supabase queries (prevent SQL injection via PostgREST)
- [ ] **3.3.3** Add rate limiting to Edge Functions (already have debounce, but add a hard 60 calls/min/IP limit)

---

## Phase 4 — Performance & Optimization (Days 8–10)

*Make the app feel snappy for the Tharanis demo.*

### 4.1 Frontend Performance

- [ ] **4.1.1** Profile the Streamlit app: which operations take >1s? Use `st.spinner` with Hungarian text for any slow operation
- [ ] **4.1.2** Use `@st.cache_data` (not the deprecated `@st.cache`) on all data-fetching functions with appropriate TTL
- [ ] **4.1.3** Lazy-load the Analytics page — don't fetch analytics data until the user navigates there
- [ ] **4.1.4** Optimize the product selector: use `@st.cache_data` for the 6,500+ product list, cache for 24h
- [ ] **4.1.5** Add loading skeletons or spinners for every chart that takes >200ms to render
- [ ] **4.1.6** Minimize Streamlit reruns: use `st.session_state` to avoid unnecessary recalculations on widget interactions

> 🧠 **Claude Code prompt**:
> *"Audit app.py and the page modules for Streamlit performance. Replace any deprecated @st.cache with @st.cache_data. Add st.spinner() around all data fetches. Ensure the product list is cached. Identify any session_state writes that trigger unnecessary reruns."*

### 4.2 Query Optimization

- [ ] **4.2.1** Review all Supabase queries: are they using the indexes? Add `EXPLAIN ANALYZE` for the 3 most common queries
- [ ] **4.2.2** Add composite indexes if missing (e.g., `(fulfillment_date, sku)` on sales)
- [ ] **4.2.3** For the Top 10 Products chart, consider a materialized view or pre-aggregation instead of computing client-side
- [ ] **4.2.4** Profile Edge Function cold starts — if >2s, consider warming strategies or reducing bundle size

### 4.3 Data Volume Handling

- [ ] **4.3.1** Test with the full historical dataset (2016–present): does the app still load in <3s?
- [ ] **4.3.2** Implement server-side pagination for the data tables (don't load 100k+ rows into the browser)
- [ ] **4.3.3** Add date range guards: warn the user if they select >1 year of data ("Ez sok adatot tölthet be...")

---

## Phase 5 — UI/UX Polish (Days 10–14)

*Make it look professional enough to demo to Tharanis.*

### 5.1 Visual Consistency

- [ ] **5.1.1** Audit the charcoal/orange theme: ensure every chart, table, button, and text follows the same color palette
- [ ] **5.1.2** Create a `theme.py` with all color constants, font sizes, and shared Plotly layout defaults
- [ ] **5.1.3** Ensure all charts have consistent axis formatting: Hungarian number format (space as thousands separator), proper date labels
- [ ] **5.1.4** Fix any CSS-injected styles that might break across browsers (test Chrome, Firefox, Safari)
- [ ] **5.1.5** Add a SamanSport logo to the sidebar (ask client for brand assets, or use a placeholder)
- [ ] **5.1.6** Ensure mobile-responsive behavior (Streamlit is mostly responsive, but test tables and charts)

> 🧠 **Claude Code prompt**:
> *"Create a theme.py file that centralizes all visual constants: color palette (charcoal #2D2D2D, orange #FF6B35, etc.), Plotly layout defaults, font sizes, number format (Hungarian locale with space separator). Then update all chart functions in charts.py to use these shared defaults."*

### 5.2 UX Improvements

- [ ] **5.2.1** Add breadcrumb or page title showing what the user is looking at (e.g., "Irányítópult / 2024.01.01 – 2024.12.31")
- [ ] **5.2.2** Add "last synced" timestamp in the sidebar (pulled from `sync_metadata`) with a manual refresh button
- [ ] **5.2.3** Add tooltips / info icons (`st.info` or `ℹ️`) next to KPI cards explaining what each metric means
- [ ] **5.2.4** Add keyboard shortcut or button to quickly switch between common date ranges (YTD, Last 30 days, Last quarter, Last year)
- [ ] **5.2.5** Improve empty state: when there's no data, show a friendly illustration or message, not a blank page
- [ ] **5.2.6** Make the CSV export filename meaningful: `samansport_ertekesites_2024-01-01_2024-12-31.csv`
- [ ] **5.2.7** Add a "Loading data for the first time, this may take a moment..." message for uncached date ranges

### 5.3 Accessibility & Hungarian Localization

- [ ] **5.3.1** Audit all user-facing text: ensure everything is in Hungarian (no stray English labels)
- [ ] **5.3.2** Use Hungarian date format everywhere: `2024.01.15` not `2024-01-15` or `01/15/2024`
- [ ] **5.3.3** Use Hungarian number format: `1 234 567 Ft` (space as thousands separator)
- [ ] **5.3.4** Ensure chart hover tooltips are in Hungarian
- [ ] **5.3.5** Test with Hungarian special characters (á, é, í, ó, ö, ő, ú, ü, ű) — no encoding issues

---

## Phase 6 — Deployment & Infrastructure (Days 14–17)

*Get the app accessible from the internet with proper monitoring.*

### 6.1 Deployment Strategy Decision

- [ ] **6.1.1** Decide on hosting platform. Options:
  - **Streamlit Cloud** (free, easiest, limited customization)
  - **Railway / Render** (simple, Docker-based, custom domain)
  - **VPS (Hetzner/DigitalOcean)** (full control, needs Docker setup)
  - **Client's infrastructure** (ask Tharanis/SamanSport)
- [ ] **6.1.2** Document the decision and reasoning

### 6.2 Dockerization

- [ ] **6.2.1** Create a `Dockerfile`:
  ```dockerfile
  FROM python:3.12-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  EXPOSE 8501
  HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
  CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
  ```
- [ ] **6.2.2** Create `.dockerignore` (exclude `.env`, `.git`, `__pycache__`, `tests/`, `.venv/`)
- [ ] **6.2.3** Build and test locally: `docker build -t samansport . && docker run -p 8501:8501 --env-file .env samansport`
- [ ] **6.2.4** Verify all features work in the Docker container

> 🧠 **Claude Code prompt**:
> *"Create a production Dockerfile for our Streamlit app. Use python:3.12-slim, install requirements, add a healthcheck endpoint, and configure Streamlit for production (disable dev features, set server.headless=true). Also create a .dockerignore."*

### 6.3 CI/CD Pipeline

- [ ] **6.3.1** Create `.github/workflows/ci.yml`:
  - Run `pytest` on every push/PR
  - Run `mypy` type checking
  - Run `ruff` or `flake8` linting
  - Build Docker image (don't push, just verify it builds)
- [ ] **6.3.2** Create `.github/workflows/deploy.yml`:
  - On merge to `main`, build and push Docker image
  - Deploy to your chosen platform
- [ ] **6.3.3** Add branch protection on `main` (require CI pass before merge)

> 🧠 **Claude Code prompt**:
> *"Create a GitHub Actions CI workflow (.github/workflows/ci.yml) that: (1) runs pytest, (2) runs mypy, (3) runs ruff linting, (4) builds the Docker image. Trigger on push to main and all PRs."*

### 6.4 Supabase Production Readiness

- [ ] **6.4.1** Review Supabase project settings: is it on the free tier? Consider upgrading for production (better performance, no pause after inactivity)
- [ ] **6.4.2** Enable Supabase database backups (point-in-time recovery)
- [ ] **6.4.3** Set up Supabase cron for `cron-refresh` Edge Function (every 5 minutes for stock, every 30 minutes for sales/movements)
- [ ] **6.4.4** Verify Edge Functions have proper error reporting (check Supabase logs dashboard)
- [ ] **6.4.5** Set up Supabase alerts for Edge Function failures

### 6.5 Domain & SSL

- [ ] **6.5.1** Register or decide on a domain (e.g., `analytics.samansport.hu` or `dashboard.samansport.hu`)
- [ ] **6.5.2** Configure DNS and SSL (most platforms handle SSL automatically)
- [ ] **6.5.3** Test HTTPS access end-to-end

---

## Phase 7 — Authentication & Multi-tenancy (Days 17–20)

*If Tharanis wants to offer this to multiple clients, or SamanSport wants user accounts.*

### 7.1 Authentication (if required)

- [ ] **7.1.1** Decide on auth strategy:
  - **Simple**: Single shared password (for demo/internal use)
  - **Supabase Auth**: Email/password or magic link (good for multi-user)
  - **SSO**: If Tharanis has an identity provider
- [ ] **7.1.2** Implement login page in Streamlit (use `streamlit-authenticator` package or Supabase Auth)
- [ ] **7.1.3** Add session management: redirect to login if not authenticated
- [ ] **7.1.4** Add logout functionality in the sidebar
- [ ] **7.1.5** Store user preferences (default date range, preferred metrics) in Supabase per user

### 7.2 Multi-tenancy (if Tharanis wants to resell)

- [ ] **7.2.1** Add a `tenant_id` column to all entity tables
- [ ] **7.2.2** Update Edge Functions to scope SOAP calls per tenant (different Tharanis credentials per company)
- [ ] **7.2.3** Update RLS policies to filter by tenant
- [ ] **7.2.4** Add tenant selector in the app (or auto-detect from auth context)

---

## Phase 8 — Documentation & Handover (Days 20–22)

*Essential for Tharanis introduction and long-term maintenance.*

### 8.1 Technical Documentation

- [ ] **8.1.1** Update `README.md` with:
  - Project overview and screenshots
  - Setup instructions (local dev, Docker, production)
  - Environment variables reference
  - Architecture diagram (can reuse from BACKEND_ARCHITECTURE.md)
- [ ] **8.1.2** Document the Supabase setup: how to replicate the database, deploy Edge Functions, run migrations
- [ ] **8.1.3** Document the hydration process: when to run it, how long it takes, what to expect
- [ ] **8.1.4** Create `CONTRIBUTING.md` with code style guide, PR process, testing requirements
- [ ] **8.1.5** Add inline docstrings to all public functions in the Python package

> 🧠 **Claude Code prompt**:
> *"Add comprehensive Google-style docstrings to every public function in the samansport package. Include parameter types, return types, and a brief description. Skip private/helper functions."*

### 8.2 User Documentation

- [ ] **8.2.1** Create a user guide (in Hungarian) explaining each dashboard feature — can be a simple PDF or in-app help
- [ ] **8.2.2** Document the KPI definitions (what counts as "gross revenue", how storno invoices are handled, etc.)
- [ ] **8.2.3** Create a FAQ: "Why is the data not up to date?", "What does the sync indicator mean?", etc.

### 8.3 Tharanis-Specific Documentation

- [ ] **8.3.1** Write a technical integration guide: which SOAP API methods are used, what data is extracted, how pagination works
- [ ] **8.3.2** Document the Tharanis API entities used: `kimeno_szamla`, `keszlet`, `raktari_mozgas`, `cikk`
- [ ] **8.3.3** Document any Tharanis API limitations discovered (rate limits, max page sizes, timeout behaviors)
- [ ] **8.3.4** Prepare a list of additional Tharanis API entities that could be integrated in future phases

---

## Phase 9 — Pre-Demo Testing & QA (Days 22–24)

*Final quality gate before the Tharanis demo.*

### 9.1 End-to-End Testing Checklist

- [ ] **9.1.1** Dashboard loads in <3 seconds with cached data
- [ ] **9.1.2** Dashboard loads correctly for: last 7 days, last month, last quarter, last year, custom range
- [ ] **9.1.3** KPI cards show correct values (cross-check with a manual Supabase query)
- [ ] **9.1.4** Revenue trend chart renders correctly for all period toggles (Annual/Monthly/Weekly/Daily)
- [ ] **9.1.5** Top 10 Products chart shows correct products and percentages
- [ ] **9.1.6** Analytics → Ertekesites tab: select a product, all 6 metrics render correctly
- [ ] **9.1.7** Analytics → Mozgastortenet tab: incoming/outgoing chart renders, summary metrics are correct
- [ ] **9.1.8** CSV export works and contains correct data with proper Hungarian column names
- [ ] **9.1.9** Date range changes trigger correct data reload
- [ ] **9.1.10** Product selector search works for partial SKU and partial product name
- [ ] **9.1.11** Stale data triggers background sync (watch the Supabase Edge Function logs)
- [ ] **9.1.12** App handles gracefully: no internet, Supabase down, Tharanis API down
- [ ] **9.1.13** No console errors or Python tracebacks visible to the user
- [ ] **9.1.14** All text is in Hungarian, no stray English

### 9.2 Performance Testing

- [ ] **9.2.1** Test with 3+ simultaneous browser tabs open (simulating concurrent users)
- [ ] **9.2.2** Test with a 5-year date range (2019–2024): does it load without crashing?
- [ ] **9.2.3** Measure: time to first meaningful paint, time to interactive chart, time for data table render
- [ ] **9.2.4** Verify debouncing: rapid date changes don't flood Edge Functions with sync requests

### 9.3 Browser Testing

- [ ] **9.3.1** Test on Chrome (primary)
- [ ] **9.3.2** Test on Firefox
- [ ] **9.3.3** Test on Safari (if Mac available)
- [ ] **9.3.4** Test on mobile (iOS Safari, Android Chrome) — even if not primary target, it shouldn't break

---

## Phase 10 — Tharanis Demo Preparation (Days 24–25)

*Prepare the actual demo presentation.*

### 10.1 Demo Script

- [ ] **10.1.1** Write a 15-minute demo script covering:
  1. Login / app launch (30s)
  2. Dashboard overview — KPIs, revenue trend, top products (3 min)
  3. Change date range — show how quickly data updates (1 min)
  4. Deep dive: Analytics → pick a specific product → show sales metrics (3 min)
  5. Warehouse movements for the same product (2 min)
  6. CSV export demo (1 min)
  7. Behind the scenes: explain architecture, caching, sync (3 min)
  8. Q&A (remaining time)
- [ ] **10.1.2** Prepare 3 "hero products" to demo (products with interesting sales patterns or seasonality)
- [ ] **10.1.3** Pre-cache all demo date ranges (load them once before the demo so everything is instant)
- [ ] **10.1.4** Prepare a backup plan: what if the internet is slow? Have screenshots or a screen recording ready

### 10.2 Demo Environment

- [ ] **10.2.1** Deploy to a stable URL that will work during the demo
- [ ] **10.2.2** Test the demo flow 3 times end-to-end on the actual deployment
- [ ] **10.2.3** Have the Supabase dashboard open in a background tab to show real-time sync if asked

### 10.3 Pitch Materials

- [ ] **10.3.1** Prepare a 1-page summary: what the app does, tech stack, value proposition for Tharanis clients
- [ ] **10.3.2** Prepare a roadmap slide: what's built now, what could be built next (predictive analytics, alerts, multi-tenant)
- [ ] **10.3.3** Prepare pricing/partnership talking points (if applicable)

---

## Appendix A — Claude Code Prompting Tips & Tricks

### General Best Practices

1. **Always reference specific files**: Instead of "fix the chart", say "In charts.py, the `build_revenue_chart()` function — fix the Y-axis to use Hungarian number formatting."

2. **One task per prompt**: Don't ask Claude Code to "refactor the app and add tests and fix the theme." Break it into 3 prompts.

3. **Show, don't tell**: Paste a sample of what you want the output to look like. "Make the CSV export header look like this: `Dátum;Terméknév;SKU;Mennyiség;Bruttó ár`"

4. **Ask for verification**: End prompts with "After making the change, run the app and confirm it still works" or "Run pytest and show me the results."

5. **Use the CLAUDE.md file**: Keep it updated. Claude Code reads it automatically and it dramatically improves context accuracy.

### Useful Meta-Prompts

| Situation | Prompt |
|-----------|--------|
| Before starting a new phase | *"Read the current codebase and tell me what you'd change before I start [Phase X]. Flag any risks."* |
| When stuck on a bug | *"Read the error traceback. Then read the relevant source file. Explain what's happening and propose 2 fixes."* |
| Code review | *"Review [file] for: security issues, performance problems, unused code, and style inconsistencies. Be specific."* |
| Refactoring safety | *"Before changing [file], write a test that captures the current behavior. Then make the change. Then run the test."* |
| Architecture decisions | *"I'm deciding between [A] and [B] for [problem]. Given our stack (Streamlit + Supabase + Tharanis SOAP), which is better? List trade-offs."* |

### Agenting Workflow Patterns

**Pattern 1: Test-Driven Changes**
```
1. "Write a failing test for [feature]"
2. "Now implement [feature] to make the test pass"
3. "Run all tests and confirm nothing else broke"
```

**Pattern 2: Incremental Refactoring**
```
1. "Extract [function] from [file_A] into [file_B] — don't change behavior"
2. "Run the app. Does it still work? Run tests."
3. "Now improve [function] in [file_B]"
```

**Pattern 3: Bug Fix Investigation**
```
1. "Read [error]. Trace the call chain from the error back to the root cause."
2. "Show me the relevant code sections."
3. "Fix the root cause, not just the symptom."
4. "Write a regression test so this bug can't come back."
```

**Pattern 3: Feature Development**
```
1. "Read the existing codebase for [related area]. Summarize how it works."
2. "Propose an implementation plan for [new feature] — just the plan, don't code yet."
3. [Review the plan, adjust if needed]
4. "Implement step 1 of the plan."
5. "Run the app and verify. Then implement step 2."
```

---

## Appendix B — Estimated Timeline

| Phase | Duration | What |
|-------|----------|------|
| 0 — Setup | 1 day | Repo, env, CLAUDE.md |
| 1 — Code Quality | 3 days | Refactor, types, error handling |
| 2 — Testing | 2 days | Unit + integration tests |
| 3 — Security | 2 days | Secrets, RLS, validation |
| 4 — Performance | 2 days | Query optimization, caching |
| 5 — UI/UX Polish | 4 days | Theme, localization, UX improvements |
| 6 — Deployment | 3 days | Docker, CI/CD, hosting |
| 7 — Auth (optional) | 3 days | Login, sessions, multi-tenant |
| 8 — Documentation | 2 days | Tech docs, user guide, Tharanis guide |
| 9 — QA | 2 days | Full test pass, browser testing |
| 10 — Demo Prep | 1 day | Script, materials, dry run |
| **Total** | **~25 working days** | **~5 weeks** |

> 💡 Phases 1–4 can partially overlap. Phase 7 (Auth) can be deferred post-demo if SamanSport doesn't need it yet. The critical path for a Tharanis demo is: 0 → 1 → 3 → 5 → 6 → 9 → 10.
