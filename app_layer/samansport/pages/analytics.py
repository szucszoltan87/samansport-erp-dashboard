"""Analytics page — Sales, Warehouse Movements, and Inventory Monitor analysis."""

import reflex as rx
import plotly.graph_objects as go
import pandas as pd
import sys
import os
import csv
import io
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from samansport.state import AppState
from samansport.styles import COLORS
from samansport.templates.template import template


# ── Helpers (inlined to avoid importing Streamlit-era modules) ───────────────

def _hu_thousands(n: float | int, decimals: int = 0) -> str:
    if decimals > 0:
        formatted = f"{n:,.{decimals}f}"
    else:
        formatted = f"{n:,.0f}"
    return formatted.replace(",", " ").replace(".", ",")


def _period_key(series: pd.Series, period: str) -> pd.Series:
    if period == "Éves":
        return series.dt.to_period("Y").astype(str)
    if period == "Havi":
        return series.dt.strftime("%Y-%m")
    if period == "Heti":
        return series.dt.to_period("W").astype(str)
    return series.dt.strftime("%Y-%m-%d")


def _find_sku_col(df: pd.DataFrame):
    for c in ["Cikkszám", "cikkszam", "SKU", "sku"]:
        if c in df.columns:
            return c
    return None


def _find_name_col(df: pd.DataFrame):
    for c in ["Cikknév", "cikknev", "Megnevezés"]:
        if c in df.columns:
            return c
    return None


PERIOD_OPTIONS = ["Éves", "Havi", "Heti", "Napi"]
METRIC_KEYS = [
    "Bruttó forgalom",
    "Nettó forgalom",
    "Mennyiség",
    "Átl. bruttó ár",
    "Átl. nettó ár",
    "Tranzakciók",
]
METRIC_CFG = {
    "Bruttó forgalom": ("Bruttó érték", "sum", "HUF"),
    "Nettó forgalom": ("Nettó érték", "sum", "HUF"),
    "Mennyiség": ("Mennyiség", "sum", "db"),
    "Átl. bruttó ár": ("Bruttó ár", "mean", "HUF"),
    "Átl. nettó ár": ("Nettó ár", "mean", "HUF"),
    "Tranzakciók": ("Mennyiség", "count", "db"),
}


class AnalyticsState(AppState):
    """Analytics page state."""

    # Tab selection
    active_tab: str = "Értékesítés"

    # Sales controls
    selected_metric: str = "Bruttó forgalom"
    selected_period: str = "Havi"
    chart_type: str = "Oszlop"

    # Product selection
    product_options: list[str] = ["— Összes termék —"]
    selected_product: str = "— Összes termék —"

    # Plotly chart figures (Reflex serialises go.Figure natively)
    sales_chart: go.Figure = go.Figure()
    movements_chart_data: go.Figure = go.Figure()

    # Summary metrics
    summary_quantity: str = "0 db"
    summary_gross: str = "0 HUF"
    summary_net: str = "0 HUF"
    summary_avg_price: str = "0 HUF"
    summary_periods: str = "0"

    # Movements summary
    mov_incoming: str = "0 db"
    mov_outgoing: str = "0 db"
    mov_net: str = "0 db"
    mov_types: str = "0"

    # Data table (list of lists for rx.data_table)
    table_data: list[list] = []
    table_columns: list[str] = []
    mov_table_data: list[dict] = []

    # CSV download
    csv_data: str = ""
    csv_filename: str = ""
    mov_csv_data: str = ""
    mov_csv_filename: str = ""

    # Loading states
    is_loading_sales: bool = False
    is_loading_movements: bool = False
    has_sales_data: bool = False
    has_movements_data: bool = False

    # Private (non-serialized) storage for DataFrames
    _sales_df: pd.DataFrame = pd.DataFrame()

    def set_tab(self, tab: str):
        self.active_tab = tab

    def set_metric(self, metric: str):
        self.selected_metric = metric
        if self.has_sales_data:
            self._rebuild_sales_chart()

    def set_analytics_period(self, period: str):
        self.selected_period = period
        if self.has_sales_data:
            self._rebuild_sales_chart()

    def set_chart_type(self, chart_type: str):
        self.chart_type = chart_type
        if self.has_sales_data:
            self._rebuild_sales_chart()

    def set_product(self, product: str):
        self.selected_product = product
        if self.has_sales_data:
            self._apply_product_filter()

    async def load_sales_data(self):
        """Load sales data from the API."""
        self.is_loading_sales = True
        yield

        try:
            import tharanis_client as api

            start = (
                self.date_start
                or date.today().replace(year=date.today().year - 1).isoformat()
            ).replace("-", ".")
            end = (self.date_end or date.today().isoformat()).replace("-", ".")

            df = api.get_sales(start, end, None)
            if df is None or df.empty:
                self.has_sales_data = False
                self.is_loading_sales = False
                return

            # Store df reference for rebuilding (underscore-prefixed = private)
            self._sales_df = df

            # Build product options
            sc = _find_sku_col(df)
            nc = _find_name_col(df)
            opts = ["— Összes termék —"]
            if sc:
                products = (
                    df[[sc] + ([nc] if nc else [])]
                    .drop_duplicates(subset=[sc])
                    .sort_values(nc if nc else sc)
                )
                for _, row in products.iterrows():
                    label = (
                        f"{row[sc]}  –  {row[nc]}"
                        if nc and pd.notna(row.get(nc))
                        else str(row[sc])
                    )
                    opts.append(label)
            self.product_options = opts

            self.has_sales_data = True

            # Build chart, summary, table for current product filter
            self._apply_product_filter()
        except Exception as e:
            print(f"Sales load error: {e}")
            self.has_sales_data = False
        finally:
            self.is_loading_sales = False

    def _get_filtered_df(self) -> pd.DataFrame:
        """Return sales df filtered by selected product."""
        df = self._sales_df
        if df is None or df.empty:
            return df
        if self.selected_product == "— Összes termék —":
            return df
        # Extract SKU from "SKU  –  Name" label
        sku = self.selected_product.split("  –  ")[0].strip()
        sc = _find_sku_col(df)
        if sc:
            filtered = df[df[sc] == sku]
            return filtered if not filtered.empty else df
        return df

    def _apply_product_filter(self):
        """Re-filter data, rebuild chart, summary and table for selected product."""
        df = self._get_filtered_df()
        if df is None or df.empty:
            return

        # Update summary metrics for filtered data
        self.summary_quantity = f"{_hu_thousands(df['Mennyiség'].sum())} db"
        self.summary_gross = f"{_hu_thousands(df['Bruttó érték'].sum())} HUF"
        self.summary_net = f"{_hu_thousands(df['Nettó érték'].sum())} HUF"
        self.summary_avg_price = f"{_hu_thousands(df['Bruttó ár'].mean())} HUF"

        # Rebuild chart
        self._rebuild_sales_chart()

        # Rebuild table
        table_df = df.copy()
        table_df["kelt"] = table_df["kelt"].dt.strftime("%Y.%m.%d")
        sc = _find_sku_col(table_df)
        nc = _find_name_col(table_df)
        # Build display table with selected columns
        cols = ["kelt"]
        if sc:
            cols.append(sc)
        if nc:
            cols.append(nc)
        cols += ["Mennyiség", "Bruttó érték", "Nettó érték"]
        available = [c for c in cols if c in table_df.columns]
        self.table_columns = available
        self.table_data = table_df[available].head(1000).values.tolist()

        # Update CSV
        start = (self.date_start or "").replace("-", ".")
        end = (self.date_end or "").replace("-", ".")
        sku_part = "osszes"
        if self.selected_product != "— Összes termék —":
            sku_part = self.selected_product.split("  –  ")[0].strip().replace("/", "-")
        self.csv_data = table_df[available].to_csv(index=False)
        self.csv_filename = f"samansport_ertekesites_{sku_part}_{start}_{end}.csv"

    def _rebuild_sales_chart(self):
        """Rebuild the sales chart based on current metric/period/chart_type."""
        import plotly.graph_objects as go

        df = self._get_filtered_df()
        if df is None or df.empty:
            return

        col_name, agg_fn, unit = METRIC_CFG[self.selected_metric]
        df2 = df.copy()
        df2["Periódus"] = _period_key(df2["kelt"], self.selected_period)
        grouped = (
            df2.groupby("Periódus")[col_name]
            .agg(agg_fn)
            .reset_index()
            .sort_values("Periódus")
        )

        self.summary_periods = str(grouped["Periódus"].nunique())

        fig = go.Figure()
        if self.chart_type == "Oszlop":
            fig.add_trace(
                go.Bar(
                    x=grouped["Periódus"].tolist(),
                    y=grouped[col_name].tolist(),
                    marker_color=COLORS["accent"],
                    name=self.selected_metric,
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=grouped["Periódus"].tolist(),
                    y=grouped[col_name].tolist(),
                    mode="lines+markers",
                    name=self.selected_metric,
                    line=dict(color=COLORS["accent"], width=2.5),
                    fill="tozeroy",
                    fillcolor="rgba(78,91,166,0.07)",
                )
            )
        fig.update_layout(
            height=380,
            autosize=True,
            paper_bgcolor="white",
            plot_bgcolor=COLORS["25"],
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(color=COLORS["charcoal"], size=13, family="Inter"),
            xaxis=dict(gridcolor=COLORS["100"], type="category"),
            yaxis=dict(
                gridcolor=COLORS["100"],
                separatethousands=True,
                title=f"{self.selected_metric} ({unit})",
            ),
            showlegend=False,
        )
        self.sales_chart = fig

    async def load_movements_data(self):
        """Load warehouse movements data from the API."""
        self.is_loading_movements = True
        yield

        try:
            import tharanis_client as api
            import plotly.graph_objects as go

            start = (
                self.date_start
                or date.today().replace(year=date.today().year - 1).isoformat()
            ).replace("-", ".")
            end = (self.date_end or date.today().isoformat()).replace("-", ".")

            mdf = api.get_stock_movements(start, end, None)
            if mdf is None or mdf.empty:
                self.has_movements_data = False
                self.is_loading_movements = False
                return

            # Summary
            total_be = mdf[mdf["Irány"] == "B"]["Mennyiség"].sum()
            total_ki = mdf[mdf["Irány"] == "K"]["Mennyiség"].sum()
            net = total_be - total_ki
            self.mov_incoming = f"{_hu_thousands(total_be)} db"
            self.mov_outgoing = f"{_hu_thousands(total_ki)} db"
            self.mov_net = f"{'+'if net > 0 else ''}{_hu_thousands(net)} db"
            self.mov_types = str(mdf["Mozgástípus"].nunique())

            # Chart
            mdf2 = mdf.copy()
            mdf2["Periódus"] = _period_key(mdf2["kelt"], self.selected_period)
            be_map = (
                mdf2[mdf2["Irány"] == "B"]
                .groupby("Periódus")["Mennyiség"]
                .sum()
                .to_dict()
            )
            ki_map = (
                mdf2[mdf2["Irány"] == "K"]
                .groupby("Periódus")["Mennyiség"]
                .sum()
                .to_dict()
            )
            all_p = sorted(set(be_map) | set(ki_map))
            be_v = [be_map.get(p, 0) for p in all_p]
            ki_v = [ki_map.get(p, 0) for p in all_p]

            fig = go.Figure()
            fig.add_trace(
                go.Bar(x=all_p, y=be_v, name="Beérkező", marker_color=COLORS["accent"])
            )
            fig.add_trace(
                go.Bar(x=all_p, y=ki_v, name="Kiadó", marker_color=COLORS["charcoal"])
            )
            fig.update_layout(
                barmode="group",
                height=380,
                autosize=True,
                paper_bgcolor="white",
                plot_bgcolor=COLORS["25"],
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(color=COLORS["charcoal"], size=13, family="Inter"),
                xaxis=dict(gridcolor=COLORS["100"], type="category"),
                yaxis=dict(gridcolor=COLORS["100"], separatethousands=True),
            )
            self.movements_chart_data = fig

            # Table
            show_m = mdf.copy()
            show_m["kelt"] = show_m["kelt"].dt.strftime("%Y.%m.%d")
            self.mov_table_data = show_m.head(1000).to_dict("records")

            # CSV
            self.mov_csv_data = show_m.to_csv(index=False)
            self.mov_csv_filename = f"samansport_mozgas_osszes_{start}_{end}.csv"

            self.has_movements_data = True
        except Exception as e:
            print(f"Movements load error: {e}")
            self.has_movements_data = False
        finally:
            self.is_loading_movements = False


# ---------------------------------------------------------------------------
# Inventory Monitor State
# ---------------------------------------------------------------------------
class InventoryMonitorState(AppState):
    """State for the Készlet Monitor tab."""

    lookback_years: int = 2
    lead_time: int = 3
    service_level: float = 0.95
    monitor_data: list[dict] = []
    monitor_loading: bool = False
    has_monitor_data: bool = False
    monitor_csv_data: str = ""
    monitor_csv_filename: str = ""
    methodology_modal: str = ""

    def open_methodology(self, key: str):
        self.methodology_modal = key

    def close_methodology(self, _open: bool = False):
        if not _open:
            self.methodology_modal = ""

    @rx.var
    def total_monitored(self) -> int:
        return len(self.monitor_data)

    @rx.var
    def needs_reorder(self) -> int:
        return len([r for r in self.monitor_data if r.get("status") == "RENDELJ"])

    @rx.var
    def is_ok(self) -> int:
        return len([r for r in self.monitor_data if r.get("status") == "OK"])

    @rx.var
    def rop_col_label(self) -> str:
        return f"ROP ({self.lead_time}h)"

    @rx.var
    def lead_time_label(self) -> str:
        return f"{self.lead_time} hónapos"

    @rx.var
    def rop_example_text(self) -> list[str]:
        """Build dynamic ROP example lines from SKU 4633 live data."""
        r = next((d for d in self.monitor_data if d.get("cikkszam") == "4633"), None)
        if not r:
            return [
                "Példa — Boxzsák, Saman Spirit, 150×40 cm (cikkszám: 4633)",
                "Nincs adat a kiválasztott szűrőkkel.",
            ]
        lt = self.lead_time
        f1 = r.get("forecast_m1", 0)
        f2 = r.get("forecast_m2", 0)
        f3 = r.get("forecast_m3", 0)
        ip = r.get("inventory_position", 0)
        rop_key = f"rop_{lt}m"
        rop_val = r.get(rop_key, 0)
        jav_key = f"javasolt_{lt}m"
        jav_val = r.get(jav_key, 0)
        z_map = {0.90: "1,28", 0.95: "1,65", 0.99: "2,33"}
        z_label = z_map.get(self.service_level, "1,65")
        if lt == 1:
            mu_parts = f"H+1 = {_fmt_num(f1)}"
            mu_val = f1
        elif lt == 2:
            mu_parts = f"H+1 = {_fmt_num(f1)}, H+2 = {_fmt_num(f2)}"
            mu_val = f1 + f2
        else:
            mu_parts = f"H+1 = {_fmt_num(f1)}, H+2 = {_fmt_num(f2)}, H+3 = {_fmt_num(f3)}"
            mu_val = f1 + f2 + f3
        name = r.get("cikknev", "Boxzsák, Saman Spirit, 150×40 cm")
        return [
            f"Példa — {name} (cikkszám: 4633)",
            f"Előrejelzett kereslet: {mu_parts}",
            f"{lt} hónapos átfutási időre (z = {z_label}):",
            f"• Várható kereslet: μ({lt}) = {_fmt_num(mu_val, decimals=1)}",
            f"• ROP({lt}) = {_fmt_num(rop_val, decimals=1)}",
            f"• Jelenlegi készlet (IP): {_fmt_num(ip)} db",
            f"• Javasolt = max(0, {_fmt_num(rop_val, decimals=1)} − {_fmt_num(ip)}) = {_fmt_num(jav_val)} db",
        ]

    @rx.var
    def monitor_table_data(self) -> list[list]:
        """Build table rows from monitor_data, formatted for display."""
        rows = []
        lt = self.lead_time
        for r in self.monitor_data:
            stab = r.get("stability", "")
            rop_key = f"rop_{lt}m"
            rop_val = r.get(rop_key, 0)
            jav = (
                f"{_fmt_num(r.get('javasolt_1m', 0))} / "
                f"{_fmt_num(r.get('javasolt_2m', 0))} / "
                f"{_fmt_num(r.get('javasolt_3m', 0))}"
            )
            rows.append([
                r.get("rank", 0),
                r.get("cikkszam", ""),
                r.get("cikknev", ""),
                stab,
                _fmt_num(r.get("month_sold_qty", 0)),
                _fmt_num(r.get("month_remaining_qty", 0)),
                _fmt_num(r.get("forecast_m1", 0)),
                _fmt_num(r.get("forecast_m2", 0)),
                _fmt_num(r.get("forecast_m3", 0)),
                _fmt_num(r.get("on_inventory", 0)),
                _fmt_num(r.get("inventory_position", 0)),
                _fmt_num(rop_val),
                jav,
                r.get("status", ""),
            ])
        return rows

    async def load_monitor_data(self):
        self.monitor_loading = True
        yield
        try:
            import tharanis_client as api
            data = api.get_inventory_monitor(
                lookback_years=self.lookback_years,
                top_n=100,
                lead_time=self.lead_time,
                service_level=self.service_level,
            )
            self.monitor_data = data
            self.has_monitor_data = len(data) > 0
            self._build_csv()
        except Exception as e:
            print(f"Inventory monitor load error: {e}")
            self.has_monitor_data = False
        finally:
            self.monitor_loading = False

    def set_lookback(self, years: str):
        self.lookback_years = int(years)
        return self.load_monitor_data()

    def set_lead_time(self, months: str):
        self.lead_time = int(months)
        return self.load_monitor_data()

    def set_service_level(self, level: str):
        self.service_level = float(level)
        return self.load_monitor_data()

    def _build_csv(self):
        if not self.monitor_data:
            self.monitor_csv_data = ""
            return
        buf = io.StringIO()
        cols = [
            "#", "Cikkszám", "Terméknév", "Stabilitás",
            "Havi eladás", "Havi hátra",
            "H+1", "H+2", "H+3",
            "Készlet", "IP",
            "ROP 1h", "ROP 2h", "ROP 3h",
            "Javasolt 1h", "Javasolt 2h", "Javasolt 3h",
            "Státusz",
        ]
        writer = csv.writer(buf)
        writer.writerow(cols)
        for r in self.monitor_data:
            writer.writerow([
                r.get("rank"), r.get("cikkszam"), r.get("cikknev"),
                r.get("stability"),
                r.get("month_sold_qty"), r.get("month_remaining_qty"),
                r.get("forecast_m1"), r.get("forecast_m2"),
                r.get("forecast_m3"),
                r.get("on_inventory"), r.get("inventory_position"),
                r.get("rop_1m"), r.get("rop_2m"), r.get("rop_3m"),
                r.get("javasolt_1m"), r.get("javasolt_2m"), r.get("javasolt_3m"),
                r.get("status"),
            ])
        self.monitor_csv_data = buf.getvalue()
        today = date.today().isoformat()
        self.monitor_csv_filename = f"samansport_keszlet_riport_{today}.csv"


def _fmt_num(val, decimals: int | None = None) -> str:
    """Format number with space as thousands separator, Hungarian style."""
    try:
        n = float(val)
        if decimals is not None:
            return f"{n:,.{decimals}f}".replace(",", " ").replace(".", ",")
        if n == int(n):
            return f"{int(n):,}".replace(",", " ")
        return f"{n:,.1f}".replace(",", " ")
    except (ValueError, TypeError):
        return str(val)


# ---------------------------------------------------------------------------
# Helper: metric card component
# ---------------------------------------------------------------------------
def _metric_card(label: str, value: rx.Var) -> rx.Component:
    return rx.box(
        rx.text(
            label,
            font_size="0.65rem",
            color=COLORS["muted"],
            font_weight="600",
            text_transform="uppercase",
            letter_spacing="0.03em",
        ),
        rx.text(value, font_weight="700", font_size="0.9rem", color=COLORS["charcoal"]),
        padding="0.75rem",
        background="white",
        border_radius="8px",
        border=f"1px solid {COLORS['100']}",
    )


# ---------------------------------------------------------------------------
# Helper: toggle button (highlighted when active)
# ---------------------------------------------------------------------------
def _toggle_btn(
    label: str,
    on_click,
    is_active: rx.Var,
    size: str = "1",
) -> rx.Component:
    return rx.button(
        label,
        on_click=on_click,
        variant=rx.cond(is_active, "solid", "outline"),
        color_scheme="indigo",
        size=size,
    )


# ---------------------------------------------------------------------------
# Sales tab
# ---------------------------------------------------------------------------
def _sales_tab() -> rx.Component:
    return rx.box(
        # Product selector
        rx.select(
            AnalyticsState.product_options,
            value=AnalyticsState.selected_product,
            on_change=AnalyticsState.set_product,
            width="100%",
            margin_bottom="1rem",
        ),
        # When no data loaded — show load button
        rx.cond(
            ~AnalyticsState.has_sales_data,
            rx.center(
                rx.vstack(
                    rx.button(
                        "Értékesítési adatok betöltése",
                        on_click=AnalyticsState.load_sales_data,
                        loading=AnalyticsState.is_loading_sales,
                        color_scheme="indigo",
                        size="3",
                    ),
                    rx.text(
                        "Kattintson a gombra az adatok betöltéséhez.",
                        color=COLORS["muted"],
                        font_size="0.8rem",
                    ),
                    align="center",
                    spacing="3",
                    padding="3rem",
                    background="white",
                    border_radius="10px",
                    border=f"1px solid {COLORS['100']}",
                ),
            ),
            # Data loaded — controls + chart + summary
            rx.box(
                # Controls row
                rx.hstack(
                    # Metric selector
                    rx.vstack(
                        rx.text(
                            "MUTATÓ",
                            font_size="0.7rem",
                            font_weight="600",
                            color=COLORS["muted"],
                            text_transform="uppercase",
                        ),
                        rx.select(
                            METRIC_KEYS,
                            value=AnalyticsState.selected_metric,
                            on_change=AnalyticsState.set_metric,
                        ),
                        flex="4",
                    ),
                    # Period selector
                    rx.vstack(
                        rx.text(
                            "PERIÓDUS",
                            font_size="0.7rem",
                            font_weight="600",
                            color=COLORS["muted"],
                            text_transform="uppercase",
                        ),
                        rx.hstack(
                            *[
                                _toggle_btn(
                                    p,
                                    AnalyticsState.set_analytics_period(p),
                                    AnalyticsState.selected_period == p,
                                )
                                for p in PERIOD_OPTIONS
                            ],
                            spacing="1",
                        ),
                        flex="2",
                    ),
                    # Chart type
                    rx.vstack(
                        rx.text(
                            "DIAGRAM",
                            font_size="0.7rem",
                            font_weight="600",
                            color=COLORS["muted"],
                            text_transform="uppercase",
                        ),
                        rx.hstack(
                            _toggle_btn(
                                "Oszlop",
                                AnalyticsState.set_chart_type("Oszlop"),
                                AnalyticsState.chart_type == "Oszlop",
                            ),
                            _toggle_btn(
                                "Vonal",
                                AnalyticsState.set_chart_type("Vonal"),
                                AnalyticsState.chart_type == "Vonal",
                            ),
                            spacing="1",
                        ),
                        flex="2",
                    ),
                    spacing="4",
                    width="100%",
                    margin_bottom="1rem",
                    align="end",
                ),
                # Chart
                rx.box(
                    rx.plotly(
                        data=AnalyticsState.sales_chart,
                        use_resize_handler=True,
                        style={"width": "100%"},
                    ),
                    background="white",
                    border_radius="10px",
                    padding="1rem",
                    border=f"1px solid {COLORS['100']}",
                    margin_bottom="1rem",
                    overflow="hidden",
                ),
                # Summary metrics row
                rx.grid(
                    _metric_card("ÖSSZES MENNYISÉG", AnalyticsState.summary_quantity),
                    _metric_card("BRUTTÓ FORGALOM", AnalyticsState.summary_gross),
                    _metric_card("NETTÓ FORGALOM", AnalyticsState.summary_net),
                    _metric_card("ÁTL. BRUTTÓ ÁR", AnalyticsState.summary_avg_price),
                    _metric_card("AKTÍV PERIÓDUSOK", AnalyticsState.summary_periods),
                    columns="5",
                    spacing="3",
                    width="100%",
                    margin_bottom="1rem",
                ),
                # Data table
                rx.cond(
                    AnalyticsState.table_data.length() > 0,
                    rx.box(
                        rx.text(
                            "Tranzakciók",
                            font_weight="700",
                            font_size="0.85rem",
                            margin_bottom="0.5rem",
                            color=COLORS["charcoal"],
                        ),
                        rx.data_table(
                            data=AnalyticsState.table_data,
                            columns=AnalyticsState.table_columns,
                            pagination=True,
                            search=True,
                            sort=True,
                        ),
                        background="white",
                        border_radius="10px",
                        padding="1rem",
                        border=f"1px solid {COLORS['100']}",
                        margin_bottom="1rem",
                        overflow="auto",
                    ),
                    rx.fragment(),
                ),
                # CSV download button
                rx.cond(
                    AnalyticsState.csv_data != "",
                    rx.button(
                        "CSV letöltése",
                        on_click=rx.download(
                            data=AnalyticsState.csv_data,
                            filename=AnalyticsState.csv_filename,
                        ),
                        variant="outline",
                        size="2",
                    ),
                    rx.fragment(),
                ),
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Movements tab
# ---------------------------------------------------------------------------
def _movements_tab() -> rx.Component:
    return rx.box(
        rx.cond(
            ~AnalyticsState.has_movements_data,
            rx.center(
                rx.vstack(
                    rx.button(
                        "Mozgástörténet betöltése",
                        on_click=AnalyticsState.load_movements_data,
                        loading=AnalyticsState.is_loading_movements,
                        color_scheme="indigo",
                        size="3",
                    ),
                    rx.text(
                        "Kattintson a gombra a mozgásadatok betöltéséhez.",
                        color=COLORS["muted"],
                        font_size="0.8rem",
                    ),
                    align="center",
                    spacing="3",
                    padding="3rem",
                    background="white",
                    border_radius="10px",
                    border=f"1px solid {COLORS['100']}",
                ),
            ),
            rx.box(
                # Movements chart
                rx.box(
                    rx.text(
                        "Raktári mozgások",
                        font_weight="700",
                        font_size="0.85rem",
                        margin_bottom="0.5rem",
                        color=COLORS["charcoal"],
                    ),
                    rx.plotly(
                        data=AnalyticsState.movements_chart_data,
                        use_resize_handler=True,
                        style={"width": "100%"},
                    ),
                    background="white",
                    border_radius="10px",
                    padding="1rem",
                    overflow="hidden",
                    border=f"1px solid {COLORS['100']}",
                    margin_bottom="1rem",
                ),
                # Summary metrics
                rx.grid(
                    _metric_card("ÖSSZES BEÉRKEZŐ", AnalyticsState.mov_incoming),
                    _metric_card("ÖSSZES KIADÓ", AnalyticsState.mov_outgoing),
                    _metric_card("NETTÓ MOZGÁS", AnalyticsState.mov_net),
                    _metric_card("MOZGÁSTÍPUSOK", AnalyticsState.mov_types),
                    columns="4",
                    spacing="3",
                    width="100%",
                    margin_bottom="1rem",
                ),
                # CSV download for movements
                rx.cond(
                    AnalyticsState.mov_csv_data != "",
                    rx.button(
                        "CSV letöltése",
                        on_click=rx.download(
                            data=AnalyticsState.mov_csv_data,
                            filename=AnalyticsState.mov_csv_filename,
                        ),
                        variant="outline",
                        size="2",
                    ),
                    rx.fragment(),
                ),
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Inventory Monitor tab
# ---------------------------------------------------------------------------
def _stability_badge(value: rx.Var) -> rx.Component:
    """Colored badge for stability classification."""
    return rx.cond(
        value == "stable",
        rx.badge("stabil", color_scheme="green", size="1"),
        rx.cond(
            value == "light_volatile",
            rx.badge("ingadozó", color_scheme="yellow", size="1"),
            rx.badge("volatilis", color_scheme="red", size="1"),
        ),
    )


def _status_badge(value: rx.Var) -> rx.Component:
    """Colored badge for order status."""
    return rx.cond(
        value == "RENDELJ",
        rx.badge("RENDELJ", color_scheme="red", size="1"),
        rx.badge("OK", color_scheme="green", size="1"),
    )


# ---------------------------------------------------------------------------
# Methodology: info icons & modals
# ---------------------------------------------------------------------------

def _info_icon(tooltip: str) -> rx.Component:
    """Small info icon with hover tooltip only (no click action)."""
    return rx.tooltip(
        rx.icon(
            tag="info",
            size=13,
            color=COLORS["muted"],
            cursor="help",
            flex_shrink="0",
        ),
        content=tooltip,
        side="top",
    )


def _info_icon_clickable(tooltip: str, modal_key: str) -> rx.Component:
    """Info icon with hover tooltip AND click-to-open modal."""
    return rx.tooltip(
        rx.icon(
            tag="info",
            size=13,
            color=COLORS["accent"],
            cursor="pointer",
            flex_shrink="0",
            on_click=InventoryMonitorState.open_methodology(modal_key),
        ),
        content=f"{tooltip} (kattints a részletekért)",
        side="top",
    )


def _col_header(
    label: str, tooltip: str, width: str, modal_key: str = "", use_min_width: bool = False,
) -> rx.Component:
    """Column header cell with label + info icon."""
    icon = (
        _info_icon_clickable(tooltip, modal_key)
        if modal_key
        else _info_icon(tooltip)
    )
    size_kwarg = {"min_width": width} if use_min_width else {"width": width}
    return rx.table.column_header_cell(
        rx.hstack(
            rx.text(label, white_space="nowrap"),
            icon,
            spacing="1",
            align="center",
        ),
        **size_kwarg,
    )


def _col_header_dynamic(label: rx.Var, tooltip: str, width: str, modal_key: str = "") -> rx.Component:
    """Column header cell with a dynamic (rx.Var) label + info icon."""
    icon = (
        _info_icon_clickable(tooltip, modal_key)
        if modal_key
        else _info_icon(tooltip)
    )
    return rx.table.column_header_cell(
        rx.hstack(
            rx.text(label, white_space="nowrap"),
            icon,
            spacing="1",
            align="center",
        ),
        width=width,
    )


def _methodology_modal_rop() -> rx.Component:
    """Modal content explaining the ROP calculation."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("ROP — Újrarendelési küszöb"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "A ROP (Reorder Point) az a készletszint, amelynél új rendelést kell feladni "
                        "ahhoz, hogy a kiszolgálási szint a célérték felett maradjon.",
                        font_size="0.85rem",
                    ),
                    rx.box(
                        rx.text("Képlet:", font_weight="600", font_size="0.85rem"),
                        rx.code(
                            "ROP(L) = μ(L) + z × σ(L)",
                            font_size="0.9rem",
                            padding="0.5rem",
                            width="100%",
                            display="block",
                        ),
                        rx.vstack(
                            rx.text("• μ(L) = várható összkereslet az L hónapos átfutási idő alatt", font_size="0.8rem"),
                            rx.text("• σ(L) = a kereslet szórása ugyanezen időszakra", font_size="0.8rem"),
                            rx.text("• z = biztonsági tényező (90% → 1,28 | 95% → 1,65 | 99% → 2,33)", font_size="0.8rem"),
                            spacing="1",
                        ),
                        padding="0.75rem",
                        background=COLORS["50"],
                        border_radius="8px",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.foreach(
                                InventoryMonitorState.rop_example_text,
                                lambda line: rx.text(line, font_size="0.8rem"),
                            ),
                            spacing="1",
                        ),
                        padding="0.75rem",
                        background=COLORS["50"],
                        border_radius="8px",
                        width="100%",
                    ),
                    spacing="3",
                ),
            ),
            rx.dialog.close(
                rx.button("Bezárás", variant="outline", size="2"),
                margin_top="1rem",
            ),
            max_width="520px",
        ),
        open=InventoryMonitorState.methodology_modal == "rop",
        on_open_change=InventoryMonitorState.close_methodology,
    )


def _methodology_modal_ip() -> rx.Component:
    """Modal content explaining IP (Inventory Position)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("IP — Készletpozíció (Inventory Position)"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "Az IP a valós rendelkezésre álló készletet mutatja, figyelembe véve "
                        "a nyitott rendeléseket és a vevői hátralékokat.",
                        font_size="0.85rem",
                    ),
                    rx.box(
                        rx.code(
                            "IP = Készlet + Rendelve − Hátralékos",
                            font_size="0.9rem",
                            padding="0.5rem",
                            width="100%",
                            display="block",
                        ),
                        padding="0.75rem",
                        background=COLORS["50"],
                        border_radius="8px",
                        width="100%",
                    ),
                    rx.text(
                        "Jelenleg a Rendelve és Hátralékos értékek minden terméknél 0, "
                        "ezért az IP megegyezik a raktárkészlettel. Ha ezek az értékek "
                        "változnak, az IP automatikusan frissül.",
                        font_size="0.85rem",
                        color=COLORS["text_secondary"],
                    ),
                    rx.text(
                        "A készletadatok a Bartók raktárból (központi raktár) származnak "
                        "— minden beszerzés ide érkezik, innen történik a többi raktár feltöltése.",
                        font_size="0.85rem",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="3",
                ),
            ),
            rx.dialog.close(
                rx.button("Bezárás", variant="outline", size="2"),
                margin_top="1rem",
            ),
            max_width="480px",
        ),
        open=InventoryMonitorState.methodology_modal == "ip",
        on_open_change=InventoryMonitorState.close_methodology,
    )


def _methodology_modal_stability() -> rx.Component:
    """Modal explaining stability classification."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Stabilitás — Kereslet besorolás"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "A stabilitási besorolás a variációs együtthatón (CV) alapul, "
                        "ami a havi eladások ingadozását méri.",
                        font_size="0.85rem",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.badge("stabil", color_scheme="green", size="1"),
                                rx.text("CV < 0,5 — kiszámítható kereslet", font_size="0.8rem"),
                                align="center", spacing="2",
                            ),
                            rx.hstack(
                                rx.badge("ingadozó", color_scheme="yellow", size="1"),
                                rx.text("CV 0,5–0,75 — mérsékelt ingadozás", font_size="0.8rem"),
                                align="center", spacing="2",
                            ),
                            rx.hstack(
                                rx.badge("volatilis", color_scheme="red", size="1"),
                                rx.text("CV > 0,75 — kiszámíthatatlan, magasabb biztonsági készlet szükséges", font_size="0.8rem"),
                                align="center", spacing="2",
                            ),
                            spacing="2",
                        ),
                        padding="0.75rem",
                        background=COLORS["50"],
                        border_radius="8px",
                        width="100%",
                    ),
                    spacing="3",
                ),
            ),
            rx.dialog.close(
                rx.button("Bezárás", variant="outline", size="2"),
                margin_top="1rem",
            ),
            max_width="480px",
        ),
        open=InventoryMonitorState.methodology_modal == "stability",
        on_open_change=InventoryMonitorState.close_methodology,
    )


def _methodology_modal_status() -> rx.Component:
    """Modal explaining RENDELJ / OK status logic."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Státusz — RENDELJ / OK"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "A státusz azt jelzi, hogy szükséges-e rendelést feladni a termékre "
                        "a kiválasztott átfutási idő alapján.",
                        font_size="0.85rem",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.badge("RENDELJ", color_scheme="red", size="1"),
                                rx.text(
                                    rx.text.span("Készlet (IP) < ROP "),
                                    rx.text.span(InventoryMonitorState.lead_time_label),
                                    rx.text.span(" átfutásra — rendelés szükséges"),
                                    font_size="0.8rem",
                                ),
                                align="center", spacing="2",
                            ),
                            rx.hstack(
                                rx.badge("OK", color_scheme="green", size="1"),
                                rx.text(
                                    rx.text.span("Készlet (IP) ≥ ROP "),
                                    rx.text.span(InventoryMonitorState.lead_time_label),
                                    rx.text.span(" átfutásra — nincs azonnali teendő"),
                                    font_size="0.8rem",
                                ),
                                align="center", spacing="2",
                            ),
                            spacing="2",
                        ),
                        padding="0.75rem",
                        background=COLORS["50"],
                        border_radius="8px",
                        width="100%",
                    ),
                    rx.text(
                        "Ha a kiválasztott átfutási időn belül a készlet a ROP alatt van, "
                        "a rendszer jelzi a rendelési igényt.",
                        font_size="0.85rem",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="3",
                ),
            ),
            rx.dialog.close(
                rx.button("Bezárás", variant="outline", size="2"),
                margin_top="1rem",
            ),
            max_width="480px",
        ),
        open=InventoryMonitorState.methodology_modal == "status",
        on_open_change=InventoryMonitorState.close_methodology,
    )


def _methodology_modal_jav() -> rx.Component:
    """Modal explaining suggested order quantities."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Javasolt rendelési mennyiség"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "A javasolt rendelési mennyiség megmutatja, minimum hány darabot "
                        "érdemes rendelni az adott átfutási időhöz.",
                        font_size="0.85rem",
                    ),
                    rx.box(
                        rx.code(
                            "Javasolt = max(0, ROP(L) − IP)",
                            font_size="0.9rem",
                            padding="0.5rem",
                            width="100%",
                            display="block",
                        ),
                        rx.text(
                            "Ha a készlet (IP) a ROP felett van, nincs szükség rendelésre (0). "
                            "Ha alatta van, a különbség a minimális rendelési mennyiség.",
                            font_size="0.8rem",
                            margin_top="0.5rem",
                        ),
                        padding="0.75rem",
                        background=COLORS["50"],
                        border_radius="8px",
                        width="100%",
                    ),
                    rx.text(
                        "A három érték (1h / 2h / 3h) az 1, 2 és 3 hónapos átfutási "
                        "időhöz tartozó javasolt mennyiséget mutatja.",
                        font_size="0.85rem",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="3",
                ),
            ),
            rx.dialog.close(
                rx.button("Bezárás", variant="outline", size="2"),
                margin_top="1rem",
            ),
            max_width="480px",
        ),
        open=InventoryMonitorState.methodology_modal == "jav",
        on_open_change=InventoryMonitorState.close_methodology,
    )


def _methodology_modal_forecast() -> rx.Component:
    """Modal explaining the forecasting method — triggered from H+1/H+2/H+3 columns."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Előrejelzési módszer"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "Az előrejelzésekhez naiv (történelmi átlagokon alapuló) módszert alkalmazunk. "
                        "Az egyes hónapokra a korábbi évek azonos hónapjainak átlaga adja a becslést.",
                        font_size="0.85rem",
                    ),
                    rx.text(
                        "Megvizsgáltunk más statisztikai modelleket is (pl. exponenciális simítás, ARIMA), "
                        "és arra a következtetésre jutottunk, hogy az adatok jellegéből adódóan — magas "
                        "volatilitás, szezonális ingadozások, rendszertelen értékesítési minták — a naiv "
                        "előrejelzés nem teljesít rosszabbul, mint a bonyolultabb modellek.",
                        font_size="0.85rem",
                    ),
                    rx.text(
                        "Trendet mutató termékeknél javasolt továbbá statisztikai vizsgálatok elvégzése, "
                        "amelyek jobban kezelhetik a szisztematikus változásokat a keresletben.",
                        font_size="0.85rem",
                        color=COLORS["text_secondary"],
                    ),
                    rx.box(
                        rx.text("Megjegyzés:", font_weight="600", font_size="0.8rem"),
                        rx.text(
                            "A nulla eladású hónapok ki vannak zárva a szórásszámításból, "
                            "hogy ne torzítsák lefelé a volatilitás becslését.",
                            font_size="0.8rem",
                        ),
                        padding="0.75rem",
                        background=COLORS["50"],
                        border_radius="8px",
                        width="100%",
                    ),
                    spacing="3",
                ),
            ),
            rx.dialog.close(
                rx.button("Bezárás", variant="outline", size="2"),
                margin_top="1rem",
            ),
            max_width="480px",
        ),
        open=InventoryMonitorState.methodology_modal == "forecast",
        on_open_change=InventoryMonitorState.close_methodology,
    )


def _methodology_modal_disclaimer() -> rx.Component:
    """Modal with a compact legal disclaimer."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Jogi nyilatkozat"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "Jelen monitor kizárólag tájékoztató és statisztikai elemzési célokat szolgál, "
                        "és nem minősül üzleti, pénzügyi vagy jogi tanácsadásnak.",
                        font_size="0.85rem",
                    ),
                    rx.text(
                        "Az elemzés történelmi adatokon alapul. Az előrejelzések, újrarendelési pontok és "
                        "javasolt mennyiségek statisztikai modellek kimenetei, amelyek természetüknél fogva "
                        "bizonytalanságot hordoznak magukban.",
                        font_size="0.85rem",
                    ),
                    rx.text(
                        "Az üzleti döntések meghozatala kizárólag a felhasználó felelőssége. "
                        "A készletgazdálkodást számos tényező befolyásolhatja, beleértve a beszállítói "
                        "megbízhatóságot, piaci változásokat, szabályozási környezetet és vis maior eseményeket.",
                        font_size="0.85rem",
                        color=COLORS["text_secondary"],
                    ),
                    spacing="3",
                ),
            ),
            rx.dialog.close(
                rx.button("Bezárás", variant="outline", size="2"),
                margin_top="1rem",
            ),
            max_width="480px",
        ),
        open=InventoryMonitorState.methodology_modal == "disclaimer",
        on_open_change=InventoryMonitorState.close_methodology,
    )


def _methodology_modals() -> rx.Component:
    """All methodology modals grouped together."""
    return rx.fragment(
        _methodology_modal_rop(),
        _methodology_modal_ip(),
        _methodology_modal_stability(),
        _methodology_modal_status(),
        _methodology_modal_jav(),
        _methodology_modal_forecast(),
        _methodology_modal_disclaimer(),
    )


def _monitor_kpi(label: str, value: rx.Var, color: str = COLORS["charcoal"]) -> rx.Component:
    return rx.box(
        rx.text(
            label,
            font_size="0.65rem",
            color=COLORS["muted"],
            font_weight="600",
            text_transform="uppercase",
            letter_spacing="0.03em",
        ),
        rx.text(value, font_weight="700", font_size="1.1rem", color=color),
        padding="0.75rem 1rem",
        background="white",
        border_radius="8px",
        border=f"1px solid {COLORS['100']}",
    )


def _monitor_table_row(row: rx.Var) -> rx.Component:
    """Render a single row of the inventory monitor table."""
    return rx.table.row(
        rx.table.cell(row[0], width="40px"),                           # rank
        rx.table.cell(row[1], width="70px", font_size="0.75rem"),      # cikkszam
        rx.table.cell(row[2], min_width="200px"),                      # cikknev
        rx.table.cell(_stability_badge(row[3]), width="75px"),         # stability
        rx.table.cell(row[4], width="55px", text_align="right"),       # month_sold
        rx.table.cell(row[5], width="60px", text_align="right"),       # month_remaining
        rx.table.cell(row[6], width="45px", text_align="right"),       # H+1
        rx.table.cell(row[7], width="45px", text_align="right"),       # H+2
        rx.table.cell(row[8], width="45px", text_align="right"),       # H+3
        rx.table.cell(row[9], width="60px", text_align="right", font_weight="600"),  # inventory
        rx.table.cell(row[10], width="50px", text_align="right"),      # IP
        rx.table.cell(row[11], width="50px", text_align="right"),      # ROP
        rx.table.cell(row[12], width="100px", text_align="right", font_size="0.75rem"),  # jav
        rx.table.cell(_status_badge(row[13]), width="70px"),           # status
    )


def _monitor_tab() -> rx.Component:
    return rx.box(
        rx.cond(
            ~InventoryMonitorState.has_monitor_data,
            # No data loaded — show controls + load button
            rx.vstack(
                # Controls
                _monitor_controls(),
                rx.center(
                    rx.vstack(
                        rx.button(
                            "Készlet monitor betöltése",
                            on_click=InventoryMonitorState.load_monitor_data,
                            loading=InventoryMonitorState.monitor_loading,
                            color_scheme="indigo",
                            size="3",
                        ),
                        rx.text(
                            "Kattintson a gombra a készletfigyelő adatok betöltéséhez.",
                            color=COLORS["muted"],
                            font_size="0.8rem",
                        ),
                        align="center",
                        spacing="3",
                        padding="3rem",
                        background="white",
                        border_radius="10px",
                        border=f"1px solid {COLORS['100']}",
                    ),
                ),
                width="100%",
                spacing="4",
            ),
            # Data loaded
            rx.vstack(
                # Controls row
                _monitor_controls(),
                # KPI summary row
                rx.grid(
                    _monitor_kpi(
                        "MONITOROZOTT",
                        InventoryMonitorState.total_monitored,
                    ),
                    _monitor_kpi(
                        "RENDELÉST IGÉNYEL",
                        InventoryMonitorState.needs_reorder,
                        color=COLORS["red"],
                    ),
                    _monitor_kpi(
                        "OK",
                        InventoryMonitorState.is_ok,
                        color=COLORS["green"],
                    ),
                    columns="3",
                    spacing="3",
                    width="100%",
                ),
                # Data table
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                _col_header("#", "Rangsor árbevétel alapján", "40px"),
                                _col_header("Cikksz.", "Cikkszám (SKU azonosító)", "70px"),
                                _col_header("Terméknév", "A termék megnevezése", "200px", use_min_width=True),
                                _col_header("Stab.", "Kereslet stabilitása (variációs együttható alapján)", "75px", modal_key="stability"),
                                _col_header("Havi el.", "Aktuális hónap eddigi eladásai", "55px"),
                                _col_header("Havi hátra", "Hónap végéig várható további eladások (előrejelzés − eddigi)", "70px"),
                                _col_header("H+1", "Következő hónap előrejelzése", "45px", modal_key="forecast"),
                                _col_header("H+2", "2 hónap múlva előrejelzés", "45px", modal_key="forecast"),
                                _col_header("H+3", "3 hónap múlva előrejelzés", "45px", modal_key="forecast"),
                                _col_header("Készlet", "Aktuális raktárkészlet (Bartók raktár)", "60px"),
                                _col_header("IP", "Készletpozíció: Készlet + Rendelve − Hátralékos", "50px", modal_key="ip"),
                                _col_header_dynamic(InventoryMonitorState.rop_col_label, "Újrarendelési küszöb az adott átfutási időre", "60px", modal_key="rop"),
                                _col_header("Jav 1h/2h/3h", "Javasolt rendelési mennyiség 1, 2, 3 hónapos átfutásra", "110px", modal_key="jav"),
                                _col_header("St.", "RENDELJ ha készlet < ROP (3 hó), egyébként OK", "70px", modal_key="status"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                InventoryMonitorState.monitor_table_data,
                                _monitor_table_row,
                            ),
                        ),
                        width="100%",
                        size="1",
                        variant="surface",
                    ),
                    background="white",
                    border_radius="10px",
                    padding="0.5rem",
                    border=f"1px solid {COLORS['100']}",
                    overflow_x="auto",
                    max_height="70vh",
                    overflow_y="auto",
                    font_size="0.8rem",
                ),
                # Bottom row: CSV export + disclaimer
                rx.hstack(
                    rx.cond(
                        InventoryMonitorState.monitor_csv_data != "",
                        rx.button(
                            "CSV Exportálás",
                            on_click=rx.download(
                                data=InventoryMonitorState.monitor_csv_data,
                                filename=InventoryMonitorState.monitor_csv_filename,
                            ),
                            variant="outline",
                            size="2",
                        ),
                        rx.fragment(),
                    ),
                    rx.spacer(),
                    rx.text(
                        "Jogi nyilatkozat",
                        font_size="0.75rem",
                        color=COLORS["muted"],
                        cursor="pointer",
                        text_decoration="underline",
                        _hover={"color": COLORS["accent"]},
                        on_click=InventoryMonitorState.open_methodology("disclaimer"),
                    ),
                    width="100%",
                    align="center",
                ),
                # Methodology modals (rendered but hidden until opened)
                _methodology_modals(),
                width="100%",
                spacing="4",
            ),
        ),
    )


def _monitor_controls() -> rx.Component:
    """Controls row for inventory monitor parameters."""
    return rx.hstack(
        # Lookback period
        rx.vstack(
            rx.text(
                "IDŐSZAK",
                font_size="0.7rem",
                font_weight="600",
                color=COLORS["muted"],
                text_transform="uppercase",
            ),
            rx.hstack(
                *[
                    _toggle_btn(
                        f"{y} év",
                        InventoryMonitorState.set_lookback(str(y)),
                        InventoryMonitorState.lookback_years == y,
                    )
                    for y in [1, 2, 3, 5]
                ],
                spacing="1",
            ),
        ),
        # Lead time
        rx.vstack(
            rx.text(
                "ÁTFUTÁSI IDŐ",
                font_size="0.7rem",
                font_weight="600",
                color=COLORS["muted"],
                text_transform="uppercase",
            ),
            rx.hstack(
                *[
                    _toggle_btn(
                        f"{m} hó",
                        InventoryMonitorState.set_lead_time(str(m)),
                        InventoryMonitorState.lead_time == m,
                    )
                    for m in [1, 2, 3]
                ],
                spacing="1",
            ),
        ),
        # Service level
        rx.vstack(
            rx.text(
                "KISZOLGÁLÁSI SZINT",
                font_size="0.7rem",
                font_weight="600",
                color=COLORS["muted"],
                text_transform="uppercase",
            ),
            rx.hstack(
                *[
                    _toggle_btn(
                        f"{int(sl * 100)}%",
                        InventoryMonitorState.set_service_level(str(sl)),
                        InventoryMonitorState.service_level == sl,
                    )
                    for sl in [0.90, 0.95, 0.99]
                ],
                spacing="1",
            ),
        ),
        spacing="6",
        width="100%",
        align="end",
    )


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
@rx.page(route="/analytics", title="Analitika | SamanSport")
@template(on_date_change=AnalyticsState.load_sales_data)
def analytics() -> rx.Component:
    return rx.box(
        # Tab selector
        rx.hstack(
            _toggle_btn(
                "Értékesítés",
                AnalyticsState.set_tab("Értékesítés"),
                AnalyticsState.active_tab == "Értékesítés",
                size="2",
            ),
            _toggle_btn(
                "Mozgástörténet",
                AnalyticsState.set_tab("Mozgástörténet"),
                AnalyticsState.active_tab == "Mozgástörténet",
                size="2",
            ),
            _toggle_btn(
                "Készlet Monitor",
                AnalyticsState.set_tab("Készlet Monitor"),
                AnalyticsState.active_tab == "Készlet Monitor",
                size="2",
            ),
            spacing="2",
            margin_bottom="1rem",
        ),
        # Sales tab content
        rx.cond(
            AnalyticsState.active_tab == "Értékesítés",
            _sales_tab(),
            rx.fragment(),
        ),
        # Movements tab content
        rx.cond(
            AnalyticsState.active_tab == "Mozgástörténet",
            _movements_tab(),
            rx.fragment(),
        ),
        # Inventory Monitor tab content
        rx.cond(
            AnalyticsState.active_tab == "Készlet Monitor",
            _monitor_tab(),
            rx.fragment(),
        ),
        width="100%",
        padding="1.5rem",
    )
