"""
Unit tests for HVDC Flow Code models
"""

import pytest
from src.core.flow_models import (
    LogisticsFlow,
    FlowCode,
    ContainerFlow,
    BulkFlow,
    LandFlow,
    LCTFlow,
    get_flow_description
)


class TestFlowCodeCalculation:
    """Test Flow Code calculation logic"""

    def test_pre_arrival_code(self):
        """PreArrival should always be FlowCode.PRE_ARRIVAL (0)"""
        code = LogisticsFlow.calculate_flow_code(
            wh_hops=0,
            offshore=False,
            pre_arrival=True
        )
        assert code == FlowCode.PRE_ARRIVAL
        assert int(code) == 0

    def test_direct_delivery_code(self):
        """Direct delivery (Port→Site) should be FlowCode.DIRECT (1)"""
        code = LogisticsFlow.calculate_flow_code(
            wh_hops=0,
            offshore=False,
            pre_arrival=False
        )
        assert code == FlowCode.DIRECT
        assert int(code) == 1

    def test_wh_once_code(self):
        """Port→WH→Site should be FlowCode.WH_ONCE (2)"""
        code = LogisticsFlow.calculate_flow_code(
            wh_hops=1,
            offshore=False,
            pre_arrival=False
        )
        assert code == FlowCode.WH_ONCE
        assert int(code) == 2

    def test_wh_mosb_code(self):
        """Port→WH→MOSB→Site should be FlowCode.WH_MOSB (3)"""
        code = LogisticsFlow.calculate_flow_code(
            wh_hops=1,
            offshore=True,
            pre_arrival=False
        )
        assert code == FlowCode.WH_MOSB
        assert int(code) == 3

    def test_wh_double_mosb_code(self):
        """Port→WH→WH→MOSB→Site should be FlowCode.WH_DOUBLE_MOSB (4)"""
        code = LogisticsFlow.calculate_flow_code(
            wh_hops=2,
            offshore=True,
            pre_arrival=False
        )
        assert code == FlowCode.WH_DOUBLE_MOSB
        assert int(code) == 4

    def test_code_clipping_at_4(self):
        """FlowCode should be clipped to max 4"""
        # 1 + 5 + 1 = 7, should clip to 4
        code = LogisticsFlow.calculate_flow_code(
            wh_hops=5,
            offshore=True,
            pre_arrival=False
        )
        assert code == FlowCode.WH_DOUBLE_MOSB
        assert int(code) == 4

    def test_code_clipping_at_4_no_offshore(self):
        """FlowCode should be clipped to max 4 even without offshore"""
        # 1 + 10 + 0 = 11, should clip to 4
        code = LogisticsFlow.calculate_flow_code(
            wh_hops=10,
            offshore=False,
            pre_arrival=False
        )
        assert code == FlowCode.WH_DOUBLE_MOSB
        assert int(code) == 4


class TestContainerFlow:
    """Test Container flow with extended attributes"""

    def test_container_flow_creation(self):
        """Test creating a container flow"""
        flow = ContainerFlow(
            flow_id="CT001",
            flow_code=FlowCode.DIRECT,
            wh_handling=0,
            offshore_flag=False,
            gate_appt_win_min=120,
            cy_in_out_lag_hr=2.5,
            unload_rate_tph=25.0
        )

        assert flow.flow_id == "CT001"
        assert flow.flow_code == FlowCode.DIRECT
        assert flow.transport_mode == "container"
        assert flow.gate_appt_win_min == 120
        assert flow.cy_in_out_lag_hr == 2.5
        assert flow.unload_rate_tph == 25.0

    def test_container_flow_validation_gate_window(self):
        """Test gate appointment window validation (0-1440 min)"""
        # Valid
        flow = ContainerFlow(
            flow_id="CT002",
            flow_code=FlowCode.DIRECT,
            wh_handling=0,
            offshore_flag=False,
            gate_appt_win_min=1440  # 24 hours max
        )
        assert flow.gate_appt_win_min == 1440

        # Invalid - should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            ContainerFlow(
                flow_id="CT003",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False,
                gate_appt_win_min=1441  # Over 24 hours
            )


class TestBulkFlow:
    """Test Bulk flow with spillage risk"""

    def test_bulk_flow_creation(self):
        """Test creating a bulk flow"""
        flow = BulkFlow(
            flow_id="BLK001",
            flow_code=FlowCode.WH_ONCE,
            wh_handling=1,
            offshore_flag=False,
            unload_rate_tph=50.0,
            spillage_risk_pct=15.5
        )

        assert flow.flow_id == "BLK001"
        assert flow.flow_code == FlowCode.WH_ONCE
        assert flow.transport_mode == "bulk"
        assert flow.unload_rate_tph == 50.0
        assert flow.spillage_risk_pct == 15.5


class TestLandFlow:
    """Test Land transport flow with DOT permit"""

    def test_land_flow_creation(self):
        """Test creating a land transport flow"""
        flow = LandFlow(
            flow_id="LAND001",
            flow_code=FlowCode.DIRECT,
            wh_handling=0,
            offshore_flag=False,
            convoy_period_min=180,
            dot_permit_lead_days=7
        )

        assert flow.flow_id == "LAND001"
        assert flow.flow_code == FlowCode.DIRECT
        assert flow.transport_mode == "land"
        assert flow.convoy_period_min == 180
        assert flow.dot_permit_lead_days == 7


class TestLCTFlow:
    """Test LCT/barge flow with offshore operations"""

    def test_lct_flow_creation(self):
        """Test creating an LCT flow"""
        flow = LCTFlow(
            flow_id="LCT001",
            flow_code=FlowCode.WH_MOSB,
            wh_handling=1,
            offshore_flag=True,
            ramp_cycle_min=45,
            stowage_util_pct=85.5,
            lolo_slots=12,
            voyage_time_hours=10.5
        )

        assert flow.flow_id == "LCT001"
        assert flow.flow_code == FlowCode.WH_MOSB
        assert flow.transport_mode == "lct"
        assert flow.ramp_cycle_min == 45
        assert flow.stowage_util_pct == 85.5
        assert flow.lolo_slots == 12
        assert flow.voyage_time_hours == 10.5


class TestFlowConsistency:
    """Test flow code consistency validation"""

    def test_consistent_direct_flow(self):
        """Test consistent direct delivery flow"""
        flow = ContainerFlow(
            flow_id="CT001",
            flow_code=FlowCode.DIRECT,
            wh_handling=0,
            offshore_flag=False
        )
        assert flow.validate_consistency() is True

    def test_consistent_wh_mosb_flow(self):
        """Test consistent WH+MOSB flow"""
        flow = LCTFlow(
            flow_id="LCT001",
            flow_code=FlowCode.WH_MOSB,
            wh_handling=1,
            offshore_flag=True
        )
        assert flow.validate_consistency() is True

    def test_inconsistent_flow_code(self):
        """Test inconsistent flow code detection"""
        # FlowCode=2 but wh=0, offshore=False → should be 1
        flow = ContainerFlow(
            flow_id="CT002",
            flow_code=FlowCode.WH_ONCE,  # 2
            wh_handling=0,
            offshore_flag=False
        )
        assert flow.validate_consistency() is False

    def test_pre_arrival_consistency(self):
        """Test PreArrival flows must have FlowCode=0"""
        flow = ContainerFlow(
            flow_id="PRE001",
            flow_code=FlowCode.PRE_ARRIVAL,
            wh_handling=0,
            offshore_flag=False,
            is_pre_arrival=True
        )
        assert flow.validate_consistency() is True

        # Inconsistent: PreArrival but FlowCode=1
        flow_bad = ContainerFlow(
            flow_id="PRE002",
            flow_code=FlowCode.DIRECT,  # Wrong!
            wh_handling=0,
            offshore_flag=False,
            is_pre_arrival=True
        )
        assert flow_bad.validate_consistency() is False


class TestFlowDescriptions:
    """Test flow description helpers"""

    def test_flow_description_retrieval(self):
        """Test getting human-readable descriptions"""
        assert "Pre-Arrival" in get_flow_description(FlowCode.PRE_ARRIVAL)
        assert "Direct Delivery" in get_flow_description(FlowCode.DIRECT)
        assert "Warehouse Once" in get_flow_description(FlowCode.WH_ONCE)
        assert "MOSB" in get_flow_description(FlowCode.WH_MOSB)
        assert "WH Double" in get_flow_description(FlowCode.WH_DOUBLE_MOSB)

