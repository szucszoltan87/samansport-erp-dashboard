"""Tests for tharanis_client.py — Supabase read paths.

Three scenarios per function:
  1. Cache hit:       Supabase returns data → DataFrame with correct columns
  2. Empty result:    Supabase returns [] → empty DataFrame, no crash
  3. Connection error: Supabase throws → function returns None (graceful)

We mock _get_supabase and _supabase_select_all to isolate the Supabase
layer from the real network. _is_stale and _trigger_sync_background are
also patched to prevent side effects.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# Module path prefix for patching
_M = "tharanis_client"


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _enable_supabase():
    """Ensure _USE_SUPABASE is True so the Supabase path is taken."""
    with patch(f"{_M}._USE_SUPABASE", True):
        yield


@pytest.fixture()
def mock_sb():
    """Return a mock Supabase client and patch _get_supabase to return it."""
    client = MagicMock()
    with patch(f"{_M}._get_supabase", return_value=client):
        yield client


@pytest.fixture(autouse=True)
def _no_sync():
    """Prevent freshness checks and background sync triggers."""
    with patch(f"{_M}._is_stale", return_value=False), \
         patch(f"{_M}._trigger_sync_background"):
        yield


# ── Sales ────────────────────────────────────────────────────────────────────

SALES_COLUMNS = ["kelt", "Cikkszám", "Mennyiség", "Nettó ár",
                 "Bruttó ár", "Nettó érték", "Bruttó érték"]


class TestSupabaseGetSales:
    def test_cache_hit(self, mock_sb):
        rows = [
            {"fulfillment_date": "2025-06-15", "sku": "NIKE-42",
             "quantity": 2, "net_price": 25000, "vat_pct": 27,
             "gross_price": 31750, "net_value": 50000, "gross_value": 63500},
            {"fulfillment_date": "2025-06-16", "sku": "ADIDAS-44",
             "quantity": 1, "net_price": 35000, "vat_pct": 27,
             "gross_price": 44450, "net_value": 35000, "gross_value": 44450},
        ]
        with patch(f"{_M}._supabase_select_all", return_value=rows):
            from tharanis_client import _supabase_get_sales
            df = _supabase_get_sales("2025.06.01", "2025.06.30")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == SALES_COLUMNS
        assert df["Cikkszám"].tolist() == ["NIKE-42", "ADIDAS-44"]
        assert pd.api.types.is_datetime64_any_dtype(df["kelt"])

    def test_empty_result(self, mock_sb):
        with patch(f"{_M}._supabase_select_all", return_value=[]):
            from tharanis_client import _supabase_get_sales
            df = _supabase_get_sales("2025.06.01", "2025.06.30")

        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert list(df.columns) == SALES_COLUMNS

    def test_connection_error(self, mock_sb):
        with patch(f"{_M}._supabase_select_all", side_effect=Exception("connection refused")):
            from tharanis_client import _supabase_get_sales
            result = _supabase_get_sales("2025.06.01", "2025.06.30")

        assert result is None

    def test_sku_filter_passed(self, mock_sb):
        """Verify that a cikkszam filter adds an eq filter tuple."""
        with patch(f"{_M}._supabase_select_all", return_value=[]) as mock_select:
            from tharanis_client import _supabase_get_sales
            _supabase_get_sales("2025.06.01", "2025.06.30", cikkszam="NIKE-42")

        _args, _kwargs = mock_select.call_args
        filters = _args[3]  # 4th positional arg is the filters list
        eq_filters = [f for f in filters if f[0] == "eq"]
        assert any(args == ("sku", "NIKE-42") for _, args in eq_filters)


# ── Inventory ────────────────────────────────────────────────────────────────

INVENTORY_COLUMNS = ["Cikkszám", "Készlet",
                     "Raktár 1", "Raktár 2", "Raktár 3",
                     "Raktár 4", "Raktár 5", "Raktár 6"]


class TestSupabaseGetInventory:
    def test_cache_hit(self, mock_sb):
        rows = [
            {"sku": "NIKE-42", "total_available": 45,
             "warehouse_1": 20, "warehouse_2": 15, "warehouse_3": 10,
             "warehouse_4": 0, "warehouse_5": 0, "warehouse_6": 0},
        ]
        with patch(f"{_M}._supabase_select_all", return_value=rows):
            from tharanis_client import _supabase_get_inventory
            df = _supabase_get_inventory()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert set(INVENTORY_COLUMNS).issubset(set(df.columns))
        assert df["Cikkszám"].iloc[0] == "NIKE-42"
        assert df["Készlet"].iloc[0] == 45

    def test_empty_result(self, mock_sb):
        with patch(f"{_M}._supabase_select_all", return_value=[]):
            from tharanis_client import _supabase_get_inventory
            df = _supabase_get_inventory()

        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert list(df.columns) == INVENTORY_COLUMNS

    def test_connection_error(self, mock_sb):
        with patch(f"{_M}._supabase_select_all", side_effect=Exception("timeout")):
            from tharanis_client import _supabase_get_inventory
            result = _supabase_get_inventory()

        assert result is None


# ── Movements ────────────────────────────────────────────────────────────────

MOVEMENTS_COLUMNS = ["kelt", "Cikkszám", "Irány", "Mozgástípus", "Mennyiség"]


class TestSupabaseGetMovements:
    def test_cache_hit(self, mock_sb):
        rows = [
            {"movement_date": "2025-06-10", "sku": "NIKE-42",
             "direction": "I", "movement_type": "Beszállítás", "quantity": 50},
            {"movement_date": "2025-06-15", "sku": "NIKE-42",
             "direction": "O", "movement_type": "Értékesítés", "quantity": 2},
        ]
        with patch(f"{_M}._supabase_select_all", return_value=rows):
            from tharanis_client import _supabase_get_movements
            df = _supabase_get_movements("2025.06.01", "2025.06.30")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == MOVEMENTS_COLUMNS
        assert df["Irány"].tolist() == ["I", "O"]
        assert pd.api.types.is_datetime64_any_dtype(df["kelt"])

    def test_empty_result(self, mock_sb):
        with patch(f"{_M}._supabase_select_all", return_value=[]):
            from tharanis_client import _supabase_get_movements
            df = _supabase_get_movements("2025.06.01", "2025.06.30")

        assert isinstance(df, pd.DataFrame)
        assert df.empty
        assert list(df.columns) == MOVEMENTS_COLUMNS

    def test_connection_error(self, mock_sb):
        with patch(f"{_M}._supabase_select_all", side_effect=Exception("DNS failure")):
            from tharanis_client import _supabase_get_movements
            result = _supabase_get_movements("2025.06.01", "2025.06.30")

        assert result is None


# ── check_connection ─────────────────────────────────────────────────────────


class TestCheckConnection:
    def test_supabase_healthy(self, mock_sb):
        mock_sb.table.return_value.select.return_value.limit.return_value \
            .execute.return_value = MagicMock(data=[{"entity": "sales"}])

        from tharanis_client import check_connection
        result = check_connection()

        assert result["ok"] is True
        assert result["mode"] == "Supabase"

    def test_supabase_error(self, mock_sb):
        mock_sb.table.return_value.select.return_value.limit.return_value \
            .execute.side_effect = Exception("connection refused")

        from tharanis_client import check_connection
        result = check_connection()

        assert result["ok"] is False
        assert "hiba" in result["detail"].lower() or "connection" in result["detail"].lower()

    def test_soap_fallback_when_no_supabase(self):
        with patch(f"{_M}._USE_SUPABASE", False):
            from tharanis_client import check_connection
            result = check_connection()

        assert result["ok"] is True
        assert result["mode"] == "SOAP"


# ── Public API with Supabase path ────────────────────────────────────────────


class TestGetSalesPublic:
    """Test the public get_sales() routes through Supabase when available."""

    def test_returns_supabase_data(self, mock_sb):
        fake_df = pd.DataFrame({
            "kelt": pd.to_datetime(["2025-06-15"]),
            "Cikkszám": ["NIKE-42"],
            "Mennyiség": [2],
            "Nettó ár": [25000],
            "Bruttó ár": [31750],
            "Nettó érték": [50000],
            "Bruttó érték": [63500],
        })
        with patch(f"{_M}._supabase_get_sales", return_value=fake_df):
            from tharanis_client import get_sales
            df = get_sales("2025.06.01", "2025.06.30")

        assert len(df) == 1
        assert df["Cikkszám"].iloc[0] == "NIKE-42"

    def test_supabase_returns_none_falls_back(self, mock_sb):
        """When _supabase_get_sales returns None, SOAP fallback is attempted."""
        with patch(f"{_M}._supabase_get_sales", return_value=None), \
             patch(f"{_M}._cache_is_fresh", return_value=False), \
             patch(f"{_M}._load_cache", return_value=None), \
             patch(f"{_M}._post_soap", side_effect=Exception("no SOAP server")):
            from tharanis_client import get_sales
            df = get_sales("2025.06.01", "2025.06.30")

        # Should return empty DataFrame from the SOAP error handler
        assert isinstance(df, pd.DataFrame)
        assert df.empty


class TestGetInventoryPublic:
    def test_returns_supabase_data(self, mock_sb):
        fake_df = pd.DataFrame({
            "Cikkszám": ["NIKE-42"], "Készlet": [45],
            "Raktár 1": [20], "Raktár 2": [15], "Raktár 3": [10],
            "Raktár 4": [0], "Raktár 5": [0], "Raktár 6": [0],
        })
        with patch(f"{_M}._supabase_get_inventory", return_value=fake_df):
            from tharanis_client import get_inventory
            df = get_inventory()

        assert len(df) == 1


class TestGetMovementsPublic:
    def test_returns_supabase_data(self, mock_sb):
        fake_df = pd.DataFrame({
            "kelt": pd.to_datetime(["2025-06-10"]),
            "Cikkszám": ["NIKE-42"], "Irány": ["I"],
            "Mozgástípus": ["Beszállítás"], "Mennyiség": [50],
        })
        with patch(f"{_M}._supabase_get_movements", return_value=fake_df):
            from tharanis_client import get_stock_movements
            df = get_stock_movements("2025.06.01", "2025.06.30")

        assert len(df) == 1
        assert df["Irány"].iloc[0] == "I"
