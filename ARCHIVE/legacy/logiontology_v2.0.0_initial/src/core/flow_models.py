"""
HVDC Flow Code Models v1.0
Flow Code (0-4) classification system with mode-specific attributes
"""

from enum import IntEnum
from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
import numpy as np


class FlowCode(IntEnum):
    """Flow Code enumeration (0-4)"""
    PRE_ARRIVAL = 0  # Documents only, no physical movement
    DIRECT = 1  # Port → Site (direct delivery)
    WH_ONCE = 2  # Port → WH → Site (warehouse once)
    WH_MOSB = 3  # Port → WH → MOSB → Site (offshore via MOSB)
    WH_DOUBLE_MOSB = 4  # Port → WH → WH → MOSB → Site (multiple WH hops)


class TransportMode(str):
    """Transport mode constants"""
    CONTAINER = "container"
    BULK = "bulk"
    LAND = "land"
    LCT = "lct"


class LogisticsFlow(BaseModel):
    """Base logistics flow with Flow Code 0-4"""
    model_config = ConfigDict(extra="forbid", use_enum_values=False)

    flow_id: str = Field(..., description="Unique flow identifier")
    flow_code: FlowCode = Field(..., description="Flow code 0-4")
    wh_handling: int = Field(..., ge=0, description="Number of WH hops")
    offshore_flag: bool = Field(..., description="True if MOSB involved")
    is_pre_arrival: bool = Field(False, description="True if pre-arrival state")
    flow_description: str = Field("", description="Human-readable flow path")
    transport_mode: str = Field(..., description="Transport mode: container|bulk|land|lct")

    @field_validator("flow_code", mode="before")
    @classmethod
    def validate_flow_code_range(cls, v: int | FlowCode) -> FlowCode:
        """Ensure FlowCode is in [0, 4]"""
        if isinstance(v, FlowCode):
            return v
        code_int = int(np.clip(v, 0, 4))
        return FlowCode(code_int)

    @classmethod
    def calculate_flow_code(
        cls,
        wh_hops: int,
        offshore: bool,
        pre_arrival: bool = False
    ) -> FlowCode:
        """
        Calculate flow code based on business rules:
        - PreArrival: FlowCode = 0
        - Else: FlowCode = min(1 + wh_hops + (1 if offshore else 0), 4)

        Args:
            wh_hops: Number of warehouse hops (0, 1, 2, ...)
            offshore: True if flow passes through MOSB
            pre_arrival: True if documents-only state

        Returns:
            FlowCode (0-4)
        """
        if pre_arrival:
            return FlowCode.PRE_ARRIVAL

        code = 1 + wh_hops + (1 if offshore else 0)
        code_clipped = int(np.clip(code, 1, 4))
        return FlowCode(code_clipped)

    def validate_consistency(self) -> bool:
        """
        Validate FlowCode consistency with wh_handling and offshore_flag

        Returns:
            True if consistent, False otherwise
        """
        if self.is_pre_arrival:
            return self.flow_code == FlowCode.PRE_ARRIVAL

        expected = self.calculate_flow_code(
            self.wh_handling,
            self.offshore_flag,
            self.is_pre_arrival
        )
        return self.flow_code == expected


class ContainerFlow(LogisticsFlow):
    """Container flow with CY/gate-specific attributes"""
    transport_mode: Literal["container"] = "container"

    # Container-specific attributes
    gate_appt_win_min: int | None = Field(
        None,
        ge=0,
        le=1440,
        description="Gate appointment window (0-1440 minutes)"
    )
    cy_in_out_lag_hr: float | None = Field(
        None,
        ge=0,
        description="Container yard in/out lag (hours)"
    )
    unload_rate_tph: float | None = Field(
        None,
        gt=0,
        description="Unload rate (tons per hour)"
    )


class BulkFlow(LogisticsFlow):
    """Bulk cargo flow with spillage risk tracking"""
    transport_mode: Literal["bulk"] = "bulk"

    # Bulk-specific attributes
    unload_rate_tph: float | None = Field(
        None,
        gt=0,
        description="Unload rate (tons per hour)"
    )
    spillage_risk_pct: float | None = Field(
        None,
        ge=0,
        le=100,
        description="Spillage risk percentage (0-100)"
    )


class LandFlow(LogisticsFlow):
    """Land transport flow (truck/convoy) with DOT permit requirements"""
    transport_mode: Literal["land"] = "land"

    # Land transport-specific attributes
    convoy_period_min: int | None = Field(
        None,
        ge=0,
        description="Convoy escort period (minutes)"
    )
    dot_permit_lead_days: int | None = Field(
        None,
        ge=0,
        description="DOT permit lead time (days)"
    )


class LCTFlow(LogisticsFlow):
    """LCT/barge offshore transport with ramp cycle and LOLO operations"""
    transport_mode: Literal["lct"] = "lct"

    # LCT-specific attributes
    ramp_cycle_min: int | None = Field(
        None,
        gt=0,
        description="Ramp loading/unloading cycle (minutes)"
    )
    stowage_util_pct: float | None = Field(
        None,
        ge=0,
        le=100,
        description="Stowage space utilization (0-100%)"
    )
    lolo_slots: int | None = Field(
        None,
        ge=0,
        description="Number of LOLO (Lift-On/Lift-Off) slots"
    )
    voyage_time_hours: float | None = Field(
        None,
        gt=0,
        description="Voyage time from MOSB to offshore site (hours)"
    )


# Flow Code description mapping
FLOW_CODE_DESCRIPTIONS = {
    FlowCode.PRE_ARRIVAL: "Pre-Arrival (Documents only)",
    FlowCode.DIRECT: "Direct Delivery (Port → Site)",
    FlowCode.WH_ONCE: "Warehouse Once (Port → WH → Site)",
    FlowCode.WH_MOSB: "WH + MOSB (Port → WH → MOSB → Site)",
    FlowCode.WH_DOUBLE_MOSB: "WH Double + MOSB (Port → WH → WH → MOSB → Site)",
}


def get_flow_description(flow_code: FlowCode) -> str:
    """Get human-readable description for a flow code"""
    return FLOW_CODE_DESCRIPTIONS.get(flow_code, f"Unknown FlowCode: {flow_code}")

