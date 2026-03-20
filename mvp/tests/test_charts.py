"""Tests for chart builder functions in charts.py.

Each chart function calls st.plotly_chart internally, so we patch it and
inspect the Figure object that was passed. For empty DataFrames we verify
the placeholder annotation ("Nincs adat") is rendered.
"""

from unittest.mock import patch

import pandas as pd
import plotly.graph_objects as go
import pytest

# Patch st.plotly_chart globally for all chart calls — charts.py renders
# directly via st.plotly_chart, so we intercept the Figure there.
_ST_CHART = "charts.st.plotly_chart"
_ST_MARKDOWN = "charts.st.markdown"


def _last_figure(mock_plotly_chart) -> go.Figure:
    """Extract the Figure from the most recent st.plotly_chart call."""
    assert mock_plotly_chart.called, "st.plotly_chart was never called"
    return mock_plotly_chart.call_args[0][0]


def _has_nincs_adat(fig: go.Figure) -> bool:
    """Check whether figure has a 'Nincs adat' annotation (placeholder)."""
    return any(
        getattr(a, "text", "") == "Nincs adat"
        for a in fig.layout.annotations
    )


# ── revenue_trend_chart ──────────────────────────────────────────────────────


class TestRevenueTrendChart:
    @pytest.fixture()
    def monthly_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            "Periódus": ["2025-01", "2025-02", "2025-03"],
            "Bruttó érték": [500_000, 750_000, 620_000],
        })

    @patch(_ST_CHART)
    def test_with_data(self, mock_chart, monthly_df):
        from charts import revenue_trend_chart
        revenue_trend_chart(monthly_df)
        fig = _last_figure(mock_chart)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "scatter"

    @patch(_ST_CHART)
    def test_empty_df_shows_placeholder(self, mock_chart):
        from charts import revenue_trend_chart
        revenue_trend_chart(pd.DataFrame())
        fig = _last_figure(mock_chart)
        assert _has_nincs_adat(fig)


# ── quantity_bar_chart ───────────────────────────────────────────────────────


class TestQuantityBarChart:
    @pytest.fixture()
    def qty_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            "Periódus": ["2025-01", "2025-02"],
            "Mennyiség": [120, 95],
        })

    @patch(_ST_CHART)
    def test_with_data(self, mock_chart, qty_df):
        from charts import quantity_bar_chart
        quantity_bar_chart(qty_df)
        fig = _last_figure(mock_chart)
        assert isinstance(fig, go.Figure)
        assert fig.data[0].type == "bar"

    @patch(_ST_CHART)
    def test_empty_df_shows_placeholder(self, mock_chart):
        from charts import quantity_bar_chart
        quantity_bar_chart(pd.DataFrame())
        fig = _last_figure(mock_chart)
        assert _has_nincs_adat(fig)


# ── top10_products_chart ─────────────────────────────────────────────────────


class TestTop10ProductsChart:
    @pytest.fixture()
    def top10_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            "Label": ["Nike Air Max", "Adidas UB", "Puma RS-X"],
            "Forgalom": [1_500_000, 900_000, 400_000],
            "Pct": [53.6, 32.1, 14.3],
        })

    @patch(_ST_CHART)
    def test_with_data(self, mock_chart, top10_df):
        from charts import top10_products_chart
        top10_products_chart(top10_df)
        fig = _last_figure(mock_chart)
        assert isinstance(fig, go.Figure)
        assert fig.data[0].type == "bar"
        assert fig.data[0].orientation == "h"

    @patch(_ST_CHART)
    def test_empty_df_shows_placeholder(self, mock_chart):
        from charts import top10_products_chart
        top10_products_chart(pd.DataFrame())
        fig = _last_figure(mock_chart)
        assert _has_nincs_adat(fig)


# ── metric_chart ─────────────────────────────────────────────────────────────


class TestMetricChart:
    @pytest.fixture()
    def metric_df(self) -> pd.DataFrame:
        return pd.DataFrame({
            "Periódus": ["2025-01", "2025-02", "2025-03"],
            "Bruttó érték": [500_000, 750_000, 620_000],
        })

    @patch(_ST_CHART)
    def test_bar_chart_type(self, mock_chart, metric_df):
        from charts import metric_chart
        metric_chart(metric_df, "Bruttó érték", "Bruttó forgalom", "HUF",
                     "Bruttó forgalom (HUF)", "Oszlop")
        fig = _last_figure(mock_chart)
        assert fig.data[0].type == "bar"

    @patch(_ST_CHART)
    def test_line_chart_type(self, mock_chart, metric_df):
        from charts import metric_chart
        metric_chart(metric_df, "Bruttó érték", "Bruttó forgalom", "HUF",
                     "Bruttó forgalom (HUF)", "Vonal")
        fig = _last_figure(mock_chart)
        assert fig.data[0].type == "scatter"

    @patch(_ST_CHART)
    def test_empty_df_shows_placeholder(self, mock_chart):
        from charts import metric_chart
        metric_chart(pd.DataFrame(), "x", "m", "u", "y", "Oszlop")
        fig = _last_figure(mock_chart)
        assert _has_nincs_adat(fig)


# ── movements_chart ──────────────────────────────────────────────────────────


class TestMovementsChart:
    def _periods(self):
        return ["2025-01", "2025-02", "2025-03"]

    def _be(self):
        return [50, 30, 45]

    def _ki(self):
        return [20, 25, 40]

    @patch(_ST_CHART)
    def test_bar_chart_type(self, mock_chart):
        from charts import movements_chart
        movements_chart(self._periods(), self._be(), self._ki(), "Oszlop")
        fig = _last_figure(mock_chart)
        assert len(fig.data) == 2
        assert fig.data[0].type == "bar"
        assert fig.data[1].type == "bar"

    @patch(_ST_CHART)
    def test_line_chart_type(self, mock_chart):
        from charts import movements_chart
        movements_chart(self._periods(), self._be(), self._ki(), "Vonal")
        fig = _last_figure(mock_chart)
        assert len(fig.data) == 2
        assert fig.data[0].type == "scatter"
        assert fig.data[1].type == "scatter"

    @patch(_ST_CHART)
    def test_empty_lists_show_placeholder(self, mock_chart):
        from charts import movements_chart
        movements_chart([], [], [], "Oszlop")
        fig = _last_figure(mock_chart)
        assert _has_nincs_adat(fig)

    @patch(_ST_CHART)
    def test_trace_names(self, mock_chart):
        from charts import movements_chart
        movements_chart(self._periods(), self._be(), self._ki(), "Oszlop")
        fig = _last_figure(mock_chart)
        assert fig.data[0].name == "Beérkező"
        assert fig.data[1].name == "Kiadó"


# ── hbar_chart ───────────────────────────────────────────────────────────────


class TestHbarChart:
    @patch(_ST_CHART)
    def test_with_data(self, mock_chart):
        from charts import hbar_chart
        hbar_chart(["A", "B"], [100, 200], "#ff0000")
        fig = _last_figure(mock_chart)
        assert fig.data[0].type == "bar"
        assert fig.data[0].orientation == "h"

    @patch(_ST_CHART)
    def test_custom_height(self, mock_chart):
        from charts import hbar_chart
        hbar_chart(["A"], [50], "#000", height=500)
        fig = _last_figure(mock_chart)
        assert fig.layout.height == 500
