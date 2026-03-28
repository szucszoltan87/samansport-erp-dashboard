"""Tests for pure helper functions in helpers.py."""

from datetime import date

import pandas as pd
import pytest

from helpers import find_name_col, find_sku_col, load_warn, period_key


# ── period_key ───────────────────────────────────────────────────────────────


class TestPeriodKey:
    @pytest.fixture()
    def date_series(self) -> pd.Series:
        return pd.to_datetime(pd.Series([
            "2025-01-05", "2025-01-15", "2025-02-10", "2025-03-20",
        ]))

    def test_monthly(self, date_series):
        result = period_key(date_series, "Havi")
        assert list(result) == ["2025.01", "2025.01", "2025.02", "2025.03"]

    def test_weekly(self, date_series):
        result = period_key(date_series, "Heti")
        # Weekly periods — just verify they are non-empty strings with '/'
        assert all(isinstance(v, str) and "/" in v for v in result)

    def test_daily(self, date_series):
        result = period_key(date_series, "Napi")
        assert list(result) == ["2025.01.05", "2025.01.15", "2025.02.10", "2025.03.20"]

    def test_yearly(self, date_series):
        result = period_key(date_series, "Éves")
        assert list(result) == ["2025", "2025", "2025", "2025"]

    def test_daily_is_default(self, date_series):
        """Any unrecognized period string falls through to daily format."""
        result = period_key(date_series, "Egyéb")
        assert list(result) == ["2025.01.05", "2025.01.15", "2025.02.10", "2025.03.20"]

    def test_empty_series(self):
        result = period_key(pd.Series(dtype="datetime64[ns]"), "Havi")
        assert len(result) == 0

    def test_single_date(self):
        s = pd.to_datetime(pd.Series(["2025-06-15"]))
        result = period_key(s, "Havi")
        assert list(result) == ["2025.06"]


# ── find_sku_col ─────────────────────────────────────────────────────────────


class TestFindSkuCol:
    def test_hungarian_cikkszam(self):
        df = pd.DataFrame({"Cikkszám": ["A"], "Mennyiség": [1]})
        assert find_sku_col(df) == "Cikkszám"

    def test_lowercase_cikkszam(self):
        df = pd.DataFrame({"cikkszam": ["A"]})
        assert find_sku_col(df) == "cikkszam"

    def test_uppercase_sku(self):
        df = pd.DataFrame({"SKU": ["A"]})
        assert find_sku_col(df) == "SKU"

    def test_lowercase_sku(self):
        df = pd.DataFrame({"sku": ["A"]})
        assert find_sku_col(df) == "sku"

    def test_priority_order(self):
        """Cikkszám should be preferred over SKU when both exist."""
        df = pd.DataFrame({"SKU": ["A"], "Cikkszám": ["B"]})
        assert find_sku_col(df) == "Cikkszám"

    def test_no_match(self):
        df = pd.DataFrame({"product_code": ["A"]})
        assert find_sku_col(df) is None

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        assert find_sku_col(df) is None


# ── find_name_col ────────────────────────────────────────────────────────────


class TestFindNameCol:
    def test_cikknev(self):
        df = pd.DataFrame({"Cikknév": ["Nike"]})
        assert find_name_col(df) == "Cikknév"

    def test_lowercase_cikknev(self):
        df = pd.DataFrame({"cikknev": ["Nike"]})
        assert find_name_col(df) == "cikknev"

    def test_megnevezes(self):
        df = pd.DataFrame({"Megnevezés": ["Nike"]})
        assert find_name_col(df) == "Megnevezés"

    def test_priority_order(self):
        df = pd.DataFrame({"Megnevezés": ["A"], "Cikknév": ["B"]})
        assert find_name_col(df) == "Cikknév"

    def test_no_match(self):
        df = pd.DataFrame({"product_name": ["Nike"]})
        assert find_name_col(df) is None

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        assert find_name_col(df) is None


# ── load_warn ────────────────────────────────────────────────────────────────


class TestLoadWarn:
    def test_short_period_default_message(self):
        result = load_warn(date(2025, 1, 1), date(2025, 6, 1))
        assert "első betöltése" in result

    def test_exactly_two_years_triggers_warning(self):
        """730 days > 365*2, so this triggers the 2-year warning."""
        result = load_warn(date(2023, 1, 1), date(2025, 1, 1))
        assert "2 évnél" in result

    def test_over_two_years_warning(self):
        result = load_warn(date(2022, 6, 1), date(2025, 1, 1))
        assert result != ""
        assert "2 évnél" in result

    def test_over_three_years_longer_warning(self):
        result = load_warn(date(2020, 1, 1), date(2025, 1, 1))
        assert result != ""
        assert "kávé" in result or "☕" in result

    def test_same_day(self):
        result = load_warn(date(2025, 1, 1), date(2025, 1, 1))
        assert "első betöltése" in result

    def test_one_day(self):
        result = load_warn(date(2025, 1, 1), date(2025, 1, 2))
        assert "első betöltése" in result
