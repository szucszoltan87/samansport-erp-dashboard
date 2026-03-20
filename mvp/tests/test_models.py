"""Tests for Pydantic models — valid data, invalid data, defaults, coercion."""

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from models import (
    EntityConfig,
    InventorySnapshot,
    Product,
    SalesInvoiceLine,
    SyncMetadata,
    WarehouseMovement,
)


# ── SalesInvoiceLine ─────────────────────────────────────────────────────────


class TestSalesInvoiceLine:
    def test_valid_minimal(self):
        row = SalesInvoiceLine(
            fulfillment_date=date(2025, 3, 1),
            sku="ABC-123",
            quantity=Decimal("1"),
            net_price=Decimal("1000"),
            gross_price=Decimal("1270"),
            net_value=Decimal("1000"),
            gross_value=Decimal("1270"),
        )
        assert row.sku == "ABC-123"
        assert row.vat_pct == Decimal("27.0")  # default
        assert row.is_storno is False
        assert row.id is None

    def test_valid_full(self, sample_sales_rows):
        row = sample_sales_rows[0]
        assert row.fulfillment_date == date(2025, 6, 15)
        assert row.quantity == Decimal("2.0000")

    def test_missing_required_sku(self):
        with pytest.raises(ValidationError) as exc_info:
            SalesInvoiceLine(
                fulfillment_date=date(2025, 1, 1),
                quantity=Decimal("1"),
                net_price=Decimal("100"),
                gross_price=Decimal("127"),
                net_value=Decimal("100"),
                gross_value=Decimal("127"),
            )
        assert "sku" in str(exc_info.value)

    def test_missing_required_fulfillment_date(self):
        with pytest.raises(ValidationError) as exc_info:
            SalesInvoiceLine(
                sku="X",
                quantity=Decimal("1"),
                net_price=Decimal("100"),
                gross_price=Decimal("127"),
                net_value=Decimal("100"),
                gross_value=Decimal("127"),
            )
        assert "fulfillment_date" in str(exc_info.value)

    def test_wrong_type_quantity(self):
        with pytest.raises(ValidationError):
            SalesInvoiceLine(
                fulfillment_date=date(2025, 1, 1),
                sku="X",
                quantity="not-a-number",
                net_price=Decimal("100"),
                gross_price=Decimal("127"),
                net_value=Decimal("100"),
                gross_value=Decimal("127"),
            )

    def test_date_coercion_from_string(self):
        row = SalesInvoiceLine(
            fulfillment_date="2025-06-15",
            sku="X",
            quantity=Decimal("1"),
            net_price=Decimal("100"),
            gross_price=Decimal("127"),
            net_value=Decimal("100"),
            gross_value=Decimal("127"),
        )
        assert row.fulfillment_date == date(2025, 6, 15)

    def test_storno_row(self, sample_sales_rows):
        storno = sample_sales_rows[2]
        assert storno.is_storno is True
        assert storno.quantity < 0


# ── InventorySnapshot ────────────────────────────────────────────────────────


class TestInventorySnapshot:
    def test_valid_minimal(self):
        row = InventorySnapshot(sku="SKU-1", total_available=Decimal("10"))
        assert row.warehouse_1 == Decimal("0")  # default
        assert row.warehouse_6 == Decimal("0")

    def test_valid_full(self, sample_inventory_rows):
        row = sample_inventory_rows[0]
        assert row.sku == "NIKE-AIR-MAX-42"
        assert row.warehouse_1 == Decimal("20.00")

    def test_missing_sku(self):
        with pytest.raises(ValidationError) as exc_info:
            InventorySnapshot(total_available=Decimal("5"))
        assert "sku" in str(exc_info.value)

    def test_missing_total_available(self):
        with pytest.raises(ValidationError) as exc_info:
            InventorySnapshot(sku="X")
        assert "total_available" in str(exc_info.value)

    def test_wrong_type_total_available(self):
        with pytest.raises(ValidationError):
            InventorySnapshot(sku="X", total_available="abc")

    def test_zero_stock(self, sample_inventory_rows):
        zero = sample_inventory_rows[2]
        assert zero.total_available == Decimal("0.00")


# ── WarehouseMovement ────────────────────────────────────────────────────────


class TestWarehouseMovement:
    def test_valid_inbound(self, sample_movement_rows):
        row = sample_movement_rows[0]
        assert row.direction == "I"
        assert row.movement_type == "Beszállítás"

    def test_valid_outbound(self, sample_movement_rows):
        row = sample_movement_rows[1]
        assert row.direction == "O"

    def test_missing_movement_date(self):
        with pytest.raises(ValidationError) as exc_info:
            WarehouseMovement(sku="X", direction="I", quantity=Decimal("1"))
        assert "movement_date" in str(exc_info.value)

    def test_direction_too_long(self):
        with pytest.raises(ValidationError):
            WarehouseMovement(
                movement_date=date(2025, 1, 1),
                sku="X",
                direction="IN",  # max_length=1
                quantity=Decimal("1"),
            )

    def test_direction_empty(self):
        with pytest.raises(ValidationError):
            WarehouseMovement(
                movement_date=date(2025, 1, 1),
                sku="X",
                direction="",  # min_length=1
                quantity=Decimal("1"),
            )

    def test_wrong_type_quantity(self):
        with pytest.raises(ValidationError):
            WarehouseMovement(
                movement_date=date(2025, 1, 1),
                sku="X",
                direction="I",
                quantity="lots",
            )


# ── Product ──────────────────────────────────────────────────────────────────


class TestProduct:
    def test_valid_minimal(self):
        p = Product(sku="SKU-1")
        assert p.active is True  # default
        assert p.name is None

    def test_valid_full(self, sample_product_rows):
        p = sample_product_rows[0]
        assert p.name == "Nike Air Max 90 - 42-es"
        assert p.manufacturer == "Nike"

    def test_missing_sku(self):
        with pytest.raises(ValidationError) as exc_info:
            Product()
        assert "sku" in str(exc_info.value)

    def test_inactive_product(self, sample_product_rows):
        p = sample_product_rows[2]
        assert p.active is False

    def test_wrong_type_active(self):
        with pytest.raises(ValidationError):
            Product(sku="X", active="maybe")


# ── SyncMetadata ─────────────────────────────────────────────────────────────


class TestSyncMetadata:
    def test_valid_minimal(self):
        m = SyncMetadata(
            entity="sales",
            filter_hash="abc123",
            filter_params={"start": "2025-01-01"},
            ttl_seconds=300,
        )
        assert m.sync_status == "idle"  # default
        assert m.pages_fetched == 0
        assert m.records_synced == 0

    def test_missing_entity(self):
        with pytest.raises(ValidationError) as exc_info:
            SyncMetadata(
                filter_hash="x",
                filter_params={},
                ttl_seconds=60,
            )
        assert "entity" in str(exc_info.value)

    def test_missing_ttl(self):
        with pytest.raises(ValidationError) as exc_info:
            SyncMetadata(entity="x", filter_hash="x", filter_params={})
        assert "ttl_seconds" in str(exc_info.value)

    def test_wrong_type_ttl(self):
        with pytest.raises(ValidationError):
            SyncMetadata(
                entity="x",
                filter_hash="x",
                filter_params={},
                ttl_seconds="five",
            )


# ── EntityConfig ─────────────────────────────────────────────────────────────


class TestEntityConfig:
    def test_valid_defaults(self):
        cfg = EntityConfig(entity="products", ttl_seconds=86400)
        assert cfg.page_size == 200
        assert cfg.enabled is True

    def test_missing_entity(self):
        with pytest.raises(ValidationError) as exc_info:
            EntityConfig(ttl_seconds=60)
        assert "entity" in str(exc_info.value)

    def test_wrong_type_page_size(self):
        with pytest.raises(ValidationError):
            EntityConfig(entity="x", ttl_seconds=60, page_size="big")
