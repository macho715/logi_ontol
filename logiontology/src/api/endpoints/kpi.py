"""KPI dashboard API endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from src.analytics.kpi_calculator import FlowKPICalculator, FlowKPIs
from src.core.flow_models import LogisticsFlow

logger = logging.getLogger(__name__)

router = APIRouter()


class KPIResponse(BaseModel):
    """KPI response model."""
    total_flows: int
    direct_delivery_rate: float
    mosb_pass_rate: float
    avg_wh_hops: float
    flow_distribution: List[dict]


@router.get("/", response_model=KPIResponse)
async def get_kpis():
    """
    Get real-time KPI metrics.

    Returns:
        KPI dashboard data
    """
    try:
        # TODO: Load flows from Neo4j
        # For now, return sample data
        flows: List[LogisticsFlow] = []

        calc = FlowKPICalculator()
        kpis: FlowKPIs = calc.calculate(flows)

        # Convert to response format
        return KPIResponse(
            total_flows=kpis.total_flows,
            direct_delivery_rate=kpis.direct_delivery_rate,
            mosb_pass_rate=kpis.mosb_pass_rate,
            avg_wh_hops=kpis.avg_wh_hops,
            flow_distribution=[
                {"code": 0, "count": kpis.pre_arrival_count},
                {"code": 1, "count": kpis.direct_delivery_count},
                {"code": 2, "count": kpis.wh_once_count},
                {"code": 3, "count": kpis.wh_mosb_count},
                {"code": 4, "count": kpis.wh_wh_mosb_count},
            ]
        )

    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow-distribution")
async def get_flow_distribution():
    """Get flow code distribution."""
    # TODO: Query Neo4j for actual distribution
    return {
        "distribution": [
            {"flow_code": 0, "count": 0, "label": "Pre-Arrival"},
            {"flow_code": 1, "count": 0, "label": "Direct"},
            {"flow_code": 2, "count": 0, "label": "WH Once"},
            {"flow_code": 3, "count": 0, "label": "WH + MOSB"},
            {"flow_code": 4, "count": 0, "label": "WH Double + MOSB"},
        ]
    }


