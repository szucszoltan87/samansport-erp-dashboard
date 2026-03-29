"""Shared pytest fixtures with realistic sample data matching Pydantic models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pandas as pd
import pytest

from models import (
    InventorySnapshot,
    Product,
    SalesInvoiceLine,
    WarehouseMovement,
)


# ── Pydantic model instances ────────────────────────────────────────────────


@pytest.fixture()
def sample_sales_rows() -> list[SalesInvoiceLine]:
    """Three realistic sales invoice lines."""
    return [
        SalesInvoiceLine(
            id=1,
            fulfillment_date=date(2025, 6, 15),
            sku="NIKE-AIR-MAX-42",
            quantity=Decimal("2.0000"),
            net_price=Decimal("25000.0000"),
            vat_pct=Decimal("27.00"),
            gross_price=Decimal("31750.0000"),
            net_value=Decimal("50000.00"),
            gross_value=Decimal("63500.00"),
            is_storno=False,
            synced_at=datetime(2025, 6, 15, 10, 0, 0),
        ),
        SalesInvoiceLine(
            id=2,
            fulfillment_date=date(2025, 6, 16),
            sku="ADIDAS-UB-44",
            quantity=Decimal("1.0000"),
            net_price=Decimal("35000.0000"),
            vat_pct=Decimal("27.00"),
            gross_price=Decimal("44450.0000"),
            net_value=Decimal("35000.00"),
            gross_value=Decimal("44450.00"),
            is_storno=False,
            synced_at=datetime(2025, 6, 16, 8, 30, 0),
        ),
        SalesInvoiceLine(
            id=3,
            fulfillment_date=date(2025, 6, 16),
            sku="NIKE-AIR-MAX-42",
            quantity=Decimal("-1.0000"),
            net_price=Decimal("25000.0000"),
            vat_pct=Decimal("27.00"),
            gross_price=Decimal("31750.0000"),
            net_value=Decimal("-25000.00"),
            gross_value=Decimal("-31750.00"),
            is_storno=True,
            synced_at=datetime(2025, 6, 16, 9, 0, 0),
        ),
    ]


@pytest.fixture()
def sample_inventory_rows() -> list[InventorySnapshot]:
    """Inventory across multiple warehouses."""
    return [
        InventorySnapshot(
            id=1,
            sku="NIKE-AIR-MAX-42",
            total_available=Decimal("45.00"),
            warehouse_1=Decimal("20.00"),
            warehouse_2=Decimal("15.00"),
            warehouse_3=Decimal("10.00"),
            synced_at=datetime(2025, 6, 15, 12, 0, 0),
        ),
        InventorySnapshot(
            id=2,
            sku="ADIDAS-UB-44",
            total_available=Decimal("12.00"),
            warehouse_1=Decimal("8.00"),
            warehouse_2=Decimal("4.00"),
            synced_at=datetime(2025, 6, 15, 12, 0, 0),
        ),
        InventorySnapshot(
            id=3,
            sku="PUMA-RS-X-40",
            total_available=Decimal("0.00"),
            synced_at=datetime(2025, 6, 15, 12, 0, 0),
        ),
    ]


@pytest.fixture()
def sample_movement_rows() -> list[WarehouseMovement]:
    """Inbound and outbound warehouse movements."""
    return [
        WarehouseMovement(
            id=1,
            movement_date=date(2025, 6, 10),
            sku="NIKE-AIR-MAX-42",
            direction="I",
            movement_type="Beszállítás",
            quantity=Decimal("50.0000"),
            synced_at=datetime(2025, 6, 10, 14, 0, 0),
        ),
        WarehouseMovement(
            id=2,
            movement_date=date(2025, 6, 15),
            sku="NIKE-AIR-MAX-42",
            direction="O",
            movement_type="Értékesítés",
            quantity=Decimal("2.0000"),
            synced_at=datetime(2025, 6, 15, 10, 5, 0),
        ),
        WarehouseMovement(
            id=3,
            movement_date=date(2025, 6, 14),
            sku="ADIDAS-UB-44",
            direction="I",
            movement_type="Beszállítás",
            quantity=Decimal("20.0000"),
            synced_at=datetime(2025, 6, 14, 9, 0, 0),
        ),
    ]


@pytest.fixture()
def sample_product_rows() -> list[Product]:
    """Product master data."""
    return [
        Product(
            id=1,
            sku="NIKE-AIR-MAX-42",
            name="Nike Air Max 90 - 42-es",
            category="Sportcipő",
            manufacturer="Nike",
            unit="pár",
            active=True,
            synced_at=datetime(2025, 6, 1, 0, 0, 0),
        ),
        Product(
            id=2,
            sku="ADIDAS-UB-44",
            name="Adidas Ultraboost 22 - 44-es",
            category="Sportcipő",
            manufacturer="Adidas",
            unit="pár",
            active=True,
            synced_at=datetime(2025, 6, 1, 0, 0, 0),
        ),
        Product(
            id=3,
            sku="PUMA-RS-X-40",
            name="Puma RS-X - 40-es",
            category="Sportcipő",
            manufacturer="Puma",
            unit="pár",
            active=False,
            synced_at=datetime(2025, 5, 1, 0, 0, 0),
        ),
    ]


# ── DataFrame fixtures ──────────────────────────────────────────────────────


@pytest.fixture()
def sales_df(sample_sales_rows: list[SalesInvoiceLine]) -> pd.DataFrame:
    """Sales data as a DataFrame (mirrors Supabase query result)."""
    return pd.DataFrame([r.model_dump() for r in sample_sales_rows])


@pytest.fixture()
def inventory_df(sample_inventory_rows: list[InventorySnapshot]) -> pd.DataFrame:
    """Inventory data as a DataFrame."""
    return pd.DataFrame([r.model_dump() for r in sample_inventory_rows])


@pytest.fixture()
def movements_df(sample_movement_rows: list[WarehouseMovement]) -> pd.DataFrame:
    """Warehouse movements as a DataFrame."""
    return pd.DataFrame([r.model_dump() for r in sample_movement_rows])


@pytest.fixture()
def products_df(sample_product_rows: list[Product]) -> pd.DataFrame:
    """Product master data as a DataFrame."""
    return pd.DataFrame([r.model_dump() for r in sample_product_rows])


# ── Supabase mock ───────────────────────────────────────────────────────────


@pytest.fixture()
def mock_supabase() -> MagicMock:
    """Mock Supabase client with chained query builder pattern.

    Usage in tests::

        mock_supabase.table("sales_invoice_lines").select("*").execute.return_value = ...
    """
    client = MagicMock()

    # Supabase queries are chained: client.table(...).select(...).eq(...).execute()
    # MagicMock handles arbitrary chaining by default — each attribute/call
    # returns a new MagicMock.  We just need .execute() to return a response-
    # shaped object at the end of any chain.
    response = MagicMock()
    response.data = []
    response.count = 0

    # Make .execute() at any chain depth return the response mock.
    # Tests override .data / .count per-scenario.
    def _make_chain_terminal(mock: MagicMock) -> None:
        mock.execute.return_value = response
        # Common query-builder methods should keep the chain going.
        for method in ("select", "insert", "upsert", "update", "delete",
                       "eq", "neq", "gt", "gte", "lt", "lte",
                       "in_", "order", "limit", "range", "single"):
            chained = getattr(mock, method).return_value
            chained.execute.return_value = response
            # Support two levels of chaining (e.g. .select().eq().execute())
            for m2 in ("eq", "neq", "gt", "gte", "lt", "lte",
                       "in_", "order", "limit", "range", "single"):
                getattr(chained, m2).return_value.execute.return_value = response

    table_mock = client.table.return_value
    _make_chain_terminal(table_mock)

    # Expose the response mock so tests can set `.data` easily.
    client._response = response

    return client
