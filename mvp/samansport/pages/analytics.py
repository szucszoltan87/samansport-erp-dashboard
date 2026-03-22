"""Analytics page — Sales and Warehouse Movements analysis."""

import reflex as rx
import plotly.graph_objects as go
import pandas as pd
import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from samansport.state import AppState
from samansport.styles import COLORS
from samansport.templates.template import template


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

    # Data table (list of dicts for rx.data_table)
    table_data: list[dict] = []
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

    async def load_sales_data(self):
        """Load sales data from the API."""
        self.is_loading_sales = True
        yield

        try:
            import tharanis_client as api
            from theme import hu_thousands
            from helpers import period_key, find_sku_col, find_name_col

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
            sc = find_sku_col(df)
            nc = find_name_col(df)
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

            # Summary metrics
            self.summary_quantity = f"{hu_thousands(df['Mennyiség'].sum())} db"
            self.summary_gross = f"{hu_thousands(df['Bruttó érték'].sum())} HUF"
            self.summary_net = f"{hu_thousands(df['Nettó érték'].sum())} HUF"
            self.summary_avg_price = f"{hu_thousands(df['Bruttó ár'].mean())} HUF"

            # Build chart
            self._rebuild_sales_chart()

            # Build table data (list of dicts for serialization)
            table_df = df.copy()
            table_df["kelt"] = table_df["kelt"].dt.strftime("%Y.%m.%d")
            self.table_data = table_df.head(1000).to_dict("records")

            # CSV
            csv_bytes = table_df.to_csv(index=False)
            self.csv_data = csv_bytes
            self.csv_filename = f"samansport_ertekesites_osszes_{start}_{end}.csv"

            self.has_sales_data = True
        except Exception as e:
            print(f"Sales load error: {e}")
            self.has_sales_data = False
        finally:
            self.is_loading_sales = False

    def _rebuild_sales_chart(self):
        """Rebuild the sales chart based on current metric/period/chart_type."""
        import plotly.graph_objects as go
        from helpers import period_key

        df = self._sales_df
        if df is None or df.empty:
            return

        col_name, agg_fn, unit = METRIC_CFG[self.selected_metric]
        df2 = df.copy()
        df2["Periódus"] = period_key(df2["kelt"], self.selected_period)
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
            paper_bgcolor="white",
            plot_bgcolor=COLORS["25"],
            margin=dict(l=0, r=0, t=10, b=0),
            font=dict(color=COLORS["charcoal"], size=11, family="Inter"),
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
            from theme import hu_thousands
            from helpers import period_key
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
            self.mov_incoming = f"{hu_thousands(total_be)} db"
            self.mov_outgoing = f"{hu_thousands(total_ki)} db"
            self.mov_net = f"{'+'if net > 0 else ''}{hu_thousands(net)} db"
            self.mov_types = str(mdf["Mozgástípus"].nunique())

            # Chart
            mdf2 = mdf.copy()
            mdf2["Periódus"] = period_key(mdf2["kelt"], self.selected_period)
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
                paper_bgcolor="white",
                plot_bgcolor=COLORS["25"],
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(color=COLORS["charcoal"], size=11, family="Inter"),
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
                    rx.plotly(data=AnalyticsState.sales_chart),
                    background="white",
                    border_radius="10px",
                    padding="1rem",
                    border=f"1px solid {COLORS['100']}",
                    margin_bottom="1rem",
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
                    rx.plotly(data=AnalyticsState.movements_chart_data),
                    background="white",
                    border_radius="10px",
                    padding="1rem",
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
        width="100%",
        padding="1.5rem",
    )
