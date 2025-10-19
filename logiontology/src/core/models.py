from __future__ import annotations
from typing import Any, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class TransportEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str
    shipment_id: str
    event_type: Literal["LOAD","UNLOAD","DEPART","ARRIVE","DELAY","CANCEL","CUSTOMS","SCAN"]
    occurred_at: datetime
    location: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)

class StockSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot_id: str
    sku_id: str
    location_id: str
    on_hand: int = 0
    allocated: int = 0
    available: int = 0
    at: datetime

class DeadStock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deadstock_id: str
    sku_id: str
    location_id: str
    quantity: int
    days_stagnant: int
    reason: str | None = None
