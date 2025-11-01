from __future__ import annotations
from typing import Final

# Canonical column names (snake_case). These are the contract names the system expects after ingest/normalize.
TRANSPORT_EVENT_COLS: Final[list[str]] = [
    "event_id","shipment_id","event_type","occurred_at","location"
]

STOCK_SNAPSHOT_COLS: Final[list[str]] = [
    "snapshot_id","sku_id","location_id","on_hand","allocated","available","at"
]

DEAD_STOCK_COLS: Final[list[str]] = [
    "deadstock_id","sku_id","location_id","quantity","days_stagnant","reason"
]

# Case-insensitive rename map examples (source→canonical). Extend per data source.
DEFAULT_RENAME_MAP: dict[str, str] = {
    "EventID": "event_id",
    "ShipmentID": "shipment_id",
    "Type": "event_type",
    "Time": "occurred_at",
    "Loc": "location",
    "SKU": "sku_id",
    "Site": "location_id",
    "OnHand": "on_hand",
    "Allocated": "allocated",
    "Available": "available",
    "Timestamp": "at",
}
