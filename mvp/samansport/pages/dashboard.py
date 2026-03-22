"""Dashboard page — KPIs, period toggle, and Plotly charts."""

import reflex as rx
import plotly.graph_objects as go
import sys
import os

# Add mvp/ to path so we can import backend modules (tharanis_client, helpers, etc.)
_mvp_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _mvp_dir not in sys.path:
    sys.path.insert(0, _mvp_dir)

from samansport.state import AppState
from samansport.components.kpi_cards import kpi_card, kpi_grid
from samansport.styles import COLORS
from samansport.templates.template import template


# ---------------------------------------------------------------------------
# Helpers (inline to avoid importing Streamlit-dependent modules at import time)
# ---------------------------------------------------------------------------

def _hu_thousands(n, decimals=0):
    """Hungarian number formatting: space as thousands sep, comma as decimal."""
    if decimals > 0:
        formatted = f"{n:,.{decimals}f}"
    else:
        formatted = f"{n:,.0f}"
    return formatted.replace(",", " ").replace(".", ",")


def _period_key(series, period: str):
    """Convert a datetime Series to period strings."""
    import pandas as pd  # noqa: local import

    if period == "Éves":
        return series.dt.to_period("Y").astype(str)
    if period == "Havi":
        return series.dt.strftime("%Y-%m")
    if period == "Heti":
        return series.dt.to_period("W").astype(str)
    return series.dt.strftime("%Y-%m-%d")


def _find_sku_col(df):
    for c in ("Cikkszám", "cikkszam", "SKU", "sku"):
        if c in df.columns:
            return c
    return None


def _find_name_col(df):
    for c in ("Cikknév", "cikknev", "Megnevezés"):
        if c in df.columns:
            return c
    return None


# ---------------------------------------------------------------------------
# Dashboard state
# ---------------------------------------------------------------------------

class DashboardState(AppState):
    """Dashboard-specific state with KPIs and chart data."""

    # KPI display strings
    kpi_revenue: str = "0"
    kpi_quantity: str = "0"
    kpi_avg_price: str = "0"
    kpi_transactions: str = "0"
    kpi_revenue_sub: str = ""
    kpi_quantity_sub: str = ""
    kpi_avg_price_sub: str = ""
    kpi_transactions_sub: str = ""

    # Plotly chart figures (Reflex serialises go.Figure natively for rx.plotly)
    revenue_chart: go.Figure = go.Figure()
    quantity_chart: go.Figure = go.Figure()
    top10_chart: go.Figure = go.Figure()

    is_loading: bool = False
    has_data: bool = False

    # Private storage for the raw DataFrame so period changes can rebuild charts
    _raw_sales_df: object = None  # pd.DataFrame stored as object to avoid serialisation

    def set_period(self, period: str):
        """Override parent to rebuild charts when dashboard period changes."""
        self.period = period
        if self._raw_sales_df is not None:
            self._rebuild_charts(self._raw_sales_df)

    async def load_dashboard_data(self):
        """Fetch sales data and compute KPIs + charts."""
        self.is_loading = True
        yield

        try:
            import pandas as pd
            import plotly.graph_objects as go
            import tharanis_client as api

            # Determine date range
            from datetime import date, timedelta

            if not self.date_start or not self.date_end:
                today = date.today()
                start = (today - timedelta(days=30)).isoformat()
                end = today.isoformat()
            else:
                start = self.date_start
                end = self.date_end

            start_fmt = start.replace("-", ".")
            end_fmt = end.replace("-", ".")

            df = api.get_sales(start_fmt, end_fmt, None)
            if df is None or df.empty:
                self.has_data = False
                self.is_loading = False
                return

            # ── KPIs ─────────────────────────────────────────────────
            self.kpi_revenue = f"{_hu_thousands(df['Bruttó érték'].sum())} HUF"
            self.kpi_quantity = f"{_hu_thousands(df['Mennyiség'].sum())} db"
            self.kpi_avg_price = f"{_hu_thousands(df['Bruttó ár'].mean())} HUF"
            self.kpi_transactions = _hu_thousands(len(df))

            self.kpi_revenue_sub = (
                f"{df['kelt'].dt.to_period('M').nunique()} aktív hónap"
            )
            self.kpi_quantity_sub = (
                f"Nettó: {_hu_thousands(df['Nettó érték'].sum())} HUF"
            )
            self.kpi_avg_price_sub = (
                f"Átl. nettó: {_hu_thousands(df['Nettó ár'].mean())} HUF"
            )
            self.kpi_transactions_sub = f"{df['kelt'].dt.year.nunique()} aktív év"

            # Store raw df for period-change rebuilds
            self._raw_sales_df = df

            # Build charts from data
            self._rebuild_charts(df)

            self.has_data = True
        except Exception as e:
            print(f"Dashboard load error: {e}")
            import traceback

            traceback.print_exc()
            self.has_data = False
        finally:
            self.is_loading = False

    def _rebuild_charts(self, df):
        """(Re)build revenue, quantity, and top-10 charts from *df*."""
        import pandas as pd
        import plotly.graph_objects as go

        # ── Revenue trend (area) ─────────────────────────────────
        df2 = df.copy()
        df2["Periódus"] = _period_key(df2["kelt"], self.period)
        monthly = (
            df2.groupby("Periódus")["Bruttó érték"]
            .sum()
            .reset_index()
            .sort_values("Periódus")
        )

        fig_rev = go.Figure()
        fig_rev.add_trace(
            go.Scatter(
                x=monthly["Periódus"].tolist(),
                y=monthly["Bruttó érték"].tolist(),
                mode="lines",
                name="Bruttó forgalom",
                line=dict(color=COLORS["accent"], width=2.5),
                fill="tozeroy",
                fillcolor="rgba(78,91,166,0.08)",
            )
        )
        fig_rev.update_layout(
            height=260,
            autosize=True,
            paper_bgcolor="white",
            plot_bgcolor=COLORS["25"],
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(color=COLORS["charcoal"], size=11, family="Inter"),
            xaxis=dict(gridcolor=COLORS["100"], type="category"),
            yaxis=dict(gridcolor=COLORS["100"], separatethousands=True),
            showlegend=False,
        )
        self.revenue_chart = fig_rev

        # ── Quantity bar chart ───────────────────────────────────
        mq = (
            df2.groupby("Periódus")["Mennyiség"]
            .sum()
            .reset_index()
            .sort_values("Periódus")
        )
        fig_qty = go.Figure(
            go.Bar(
                x=mq["Periódus"].tolist(),
                y=mq["Mennyiség"].tolist(),
                marker=dict(color=COLORS["charcoal"], opacity=0.8),
            )
        )
        fig_qty.update_layout(
            height=230,
            autosize=True,
            paper_bgcolor="white",
            plot_bgcolor=COLORS["25"],
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(color=COLORS["charcoal"], size=11, family="Inter"),
            xaxis=dict(gridcolor=COLORS["100"], type="category"),
            yaxis=dict(gridcolor=COLORS["100"], separatethousands=True),
            showlegend=False,
        )
        self.quantity_chart = fig_qty

        # ── Top 10 products (horizontal bar) ─────────────────────
        sc = _find_sku_col(df)
        if sc:
            grp = (
                df.groupby(sc)["Bruttó érték"]
                .sum()
                .nlargest(10)
                .reset_index()
            )
            grp.columns = ["Cikkszám", "Forgalom"]
            nc = _find_name_col(df)
            if nc:
                names = (
                    df[[sc, nc]]
                    .drop_duplicates()
                    .rename(columns={sc: "Cikkszám", nc: "Cikknév"})
                )
                grp = grp.merge(names, on="Cikkszám", how="left")
            # Fallback: load product names from CSV master if not in data
            if "Cikknév" not in grp.columns or grp["Cikknév"].isna().all():
                try:
                    from helpers import load_product_master
                    pm = load_product_master()
                    if not pm.empty:
                        grp = grp.drop(columns=["Cikknév"], errors="ignore")
                        grp = grp.merge(
                            pm[["Cikkszám", "Cikknév"]].drop_duplicates(subset=["Cikkszám"]),
                            on="Cikkszám", how="left",
                        )
                except Exception:
                    pass
            grp["Label"] = grp.apply(
                lambda r: (
                    f"{r['Cikknév'][:30]} ({r['Cikkszám']})"
                    if pd.notna(r.get("Cikknév"))
                    else str(r["Cikkszám"])
                ),
                axis=1,
            )

            grp = grp.sort_values("Forgalom").reset_index(drop=True)

            fig_top = go.Figure(
                go.Bar(
                    x=grp["Forgalom"].tolist(),
                    y=grp["Label"].tolist(),
                    orientation="h",
                    marker=dict(color=COLORS["accent"], opacity=0.85),
                )
            )
            fig_top.update_layout(
                height=max(400, len(grp) * 42),
                autosize=True,
                paper_bgcolor="white",
                plot_bgcolor=COLORS["25"],
                margin=dict(l=0, r=0, t=0, b=30),
                font=dict(color=COLORS["charcoal"], size=11, family="Inter"),
                yaxis=dict(type="category", automargin=True),
                xaxis=dict(separatethousands=True, automargin=True),
                showlegend=False,
            )
            self.top10_chart = fig_top


# ---------------------------------------------------------------------------
# Chart card helper
# ---------------------------------------------------------------------------

def _chart_card(title: str, chart_data: rx.Var) -> rx.Component:
    """Wrap a Plotly chart in a styled card."""
    return rx.box(
        rx.text(
            title,
            font_weight="700",
            font_size="0.85rem",
            color=COLORS["text_dark"],
            margin_bottom="0.5rem",
        ),
        rx.plotly(
            data=chart_data,
            use_resize_handler=True,
            style={"width": "100%"},
        ),
        background="white",
        border_radius="10px",
        padding="1rem",
        border=f"1px solid {COLORS['100']}",
        margin_bottom="1rem",
        overflow="hidden",
    )


# ---------------------------------------------------------------------------
# Period toggle
# ---------------------------------------------------------------------------

def _period_toggle() -> rx.Component:
    """Radio-button-style period selector."""
    periods = ["Éves", "Havi", "Heti", "Napi"]
    buttons = []
    for p in periods:
        buttons.append(
            rx.button(
                p,
                on_click=DashboardState.set_period(p),
                variant=rx.cond(DashboardState.period == p, "solid", "outline"),
                color_scheme="iris",
                size="1",
                cursor="pointer",
            )
        )
    return rx.hstack(*buttons, spacing="2", margin_bottom="1rem")


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

@rx.page(route="/", title="Dashboard | SamanSport", on_load=[AppState.check_connection_and_sync, DashboardState.load_dashboard_data])
@template(on_date_change=DashboardState.load_dashboard_data)
def dashboard() -> rx.Component:
    return rx.box(
        # Loading overlay
        rx.cond(
            DashboardState.is_loading,
            rx.center(
                rx.hstack(
                    rx.spinner(size="3"),
                    rx.text("Adatok betöltése...", margin_left="0.5rem", color=COLORS["600"]),
                ),
                padding="2rem",
            ),
            rx.fragment(),
        ),
        # KPI row
        kpi_grid(
            kpi_card(
                "Bruttó forgalom",
                DashboardState.kpi_revenue,
                sub=DashboardState.kpi_revenue_sub,
                icon_name="dollar-sign",
                icon_bg=COLORS["blue_light"],
                icon_color=COLORS["accent"],
            ),
            kpi_card(
                "Értékesített mennyiség",
                DashboardState.kpi_quantity,
                sub=DashboardState.kpi_quantity_sub,
                icon_name="package",
                icon_bg=COLORS["green_light"],
                icon_color=COLORS["green"],
            ),
            kpi_card(
                "Átlagos bruttó ár",
                DashboardState.kpi_avg_price,
                sub=DashboardState.kpi_avg_price_sub,
                icon_name="tag",
                icon_bg=COLORS["amber_light"],
                icon_color=COLORS["amber"],
            ),
            kpi_card(
                "Tranzakciók",
                DashboardState.kpi_transactions,
                sub=DashboardState.kpi_transactions_sub,
                icon_name="receipt",
                icon_bg=COLORS["pink_light"],
                icon_color=COLORS["purple"],
            ),
        ),
        # Period toggle
        _period_toggle(),
        # Charts
        _chart_card("Bruttó forgalom", DashboardState.revenue_chart),
        _chart_card("Értékesített mennyiség", DashboardState.quantity_chart),
        _chart_card("Top 10 termék", DashboardState.top10_chart),
        # Empty state (shown when not loading and no data)
        rx.cond(
            ~DashboardState.has_data & ~DashboardState.is_loading,
            rx.center(
                rx.vstack(
                    rx.icon(tag="database", size=32, color=COLORS["300"]),
                    rx.text(
                        "Nincs betöltött adat",
                        font_weight="700",
                        font_size="1rem",
                        color=COLORS["text_body"],
                    ),
                    rx.text(
                        "Válasszon dátumtartományt az oldalsávban.",
                        color=COLORS["muted"],
                    ),
                    align="center",
                    padding="3rem",
                ),
            ),
            rx.fragment(),
        ),
        width="100%",
    )
