"""Pydantic models matching the Supabase PostgreSQL schema."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ── Entity tables ─────────────────────────────────────────────────────────────


class SalesInvoiceLine(BaseModel):
    """Row in ``sales_invoice_lines`` (kimenő számla tételek)."""

    id: int | None = None
    fulfillment_date: date
    sku: str
    quantity: Decimal = Field(max_digits=12, decimal_places=4)
    net_price: Decimal = Field(max_digits=14, decimal_places=4)
    vat_pct: Decimal = Field(default=Decimal("27.0"), max_digits=5, decimal_places=2)
    gross_price: Decimal = Field(max_digits=14, decimal_places=4)
    net_value: Decimal = Field(max_digits=16, decimal_places=2)
    gross_value: Decimal = Field(max_digits=16, decimal_places=2)
    is_storno: bool = False
    raw_xml_hash: str | None = None
    synced_at: datetime | None = None


class InventorySnapshot(BaseModel):
    """Row in ``inventory_snapshot`` (készlet)."""

    id: int | None = None
    sku: str
    total_available: Decimal = Field(max_digits=12, decimal_places=2)
    warehouse_1: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    warehouse_2: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    warehouse_3: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    warehouse_4: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    warehouse_5: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    warehouse_6: Decimal = Field(default=Decimal("0"), max_digits=12, decimal_places=2)
    synced_at: datetime | None = None


class WarehouseMovement(BaseModel):
    """Row in ``warehouse_movements`` (raktári mozgás)."""

    id: int | None = None
    movement_date: date
    sku: str
    direction: str = Field(min_length=1, max_length=1)
    movement_type: str | None = None
    quantity: Decimal = Field(max_digits=12, decimal_places=4)
    raw_xml_hash: str | None = None
    synced_at: datetime | None = None


class Product(BaseModel):
    """Row in ``products`` (cikk)."""

    id: int | None = None
    sku: str
    name: str | None = None
    category: str | None = None
    manufacturer: str | None = None
    unit: str | None = None
    active: bool = True
    synced_at: datetime | None = None


# ── Sync / config tables ─────────────────────────────────────────────────────


class SyncMetadata(BaseModel):
    """Row in ``sync_metadata``."""

    id: int | None = None
    entity: str
    filter_hash: str
    filter_params: dict[str, object]
    last_synced_at: datetime | None = None
    sync_started_at: datetime | None = None
    sync_status: str = "idle"
    error_message: str | None = None
    ttl_seconds: int
    pages_fetched: int = 0
    records_synced: int = 0


class EntityConfig(BaseModel):
    """Row in ``entity_config``."""

    entity: str
    ttl_seconds: int
    page_size: int = 200
    enabled: bool = True
    description: str | None = None
