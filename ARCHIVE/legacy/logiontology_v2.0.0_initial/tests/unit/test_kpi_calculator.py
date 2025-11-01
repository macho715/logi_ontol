"""
Unit tests for HVDC Flow KPI Calculator
"""

import pytest
from src.core.flow_models import (
    ContainerFlow,
    BulkFlow,
    LandFlow,
    LCTFlow,
    FlowCode
)
from src.analytics.kpi_calculator import FlowKPICalculator, FlowKPIs


class TestKPICalculation:
    """Test KPI calculation from flows"""

    def test_empty_flows(self):
        """Test KPI calculation with no flows"""
        calc = FlowKPICalculator()
        kpis = calc.calculate([])

        assert kpis.total_flows == 0
        assert kpis.direct_delivery_rate == 0.0
        assert kpis.mosb_pass_rate == 0.0
        assert kpis.avg_wh_hops == 0.0

    def test_single_direct_flow(self):
        """Test KPI with single direct delivery"""
        flows = [
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False
            )
        ]

        calc = FlowKPICalculator()
        kpis = calc.calculate(flows)

        assert kpis.total_flows == 1
        assert kpis.direct_delivery_rate == 100.0
        assert kpis.mosb_pass_rate == 0.0
        assert kpis.avg_wh_hops == 0.0
        assert kpis.flow_distribution == {1: 1}

    def test_mixed_flow_kpis(self):
        """Test KPI calculation with mixed flows"""
        flows = [
            # Direct delivery
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False
            ),
            # WH Once
            ContainerFlow(
                flow_id="CT002",
                flow_code=FlowCode.WH_ONCE,
                wh_handling=1,
                offshore_flag=False
            ),
            # WH + MOSB (LCT)
            LCTFlow(
                flow_id="LCT001",
                flow_code=FlowCode.WH_MOSB,
                wh_handling=1,
                offshore_flag=True
            ),
            # WH + MOSB (LCT)
            LCTFlow(
                flow_id="LCT002",
                flow_code=FlowCode.WH_MOSB,
                wh_handling=1,
                offshore_flag=True
            ),
        ]

        calc = FlowKPICalculator()
        kpis = calc.calculate(flows)

        assert kpis.total_flows == 4
        assert kpis.direct_delivery_rate == 25.0  # 1/4
        assert kpis.mosb_pass_rate == 50.0  # 2/4
        assert kpis.avg_wh_hops == 0.75  # (0+1+1+1)/4
        assert kpis.flow_distribution == {1: 1, 2: 1, 3: 2}
        assert kpis.mode_distribution == {"container": 2, "lct": 2}

    def test_pre_arrival_flows(self):
        """Test KPI with pre-arrival flows"""
        flows = [
            ContainerFlow(
                flow_id="PRE001",
                flow_code=FlowCode.PRE_ARRIVAL,
                wh_handling=0,
                offshore_flag=False,
                is_pre_arrival=True
            ),
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False
            ),
        ]

        calc = FlowKPICalculator()
        kpis = calc.calculate(flows)

        assert kpis.total_flows == 2
        assert kpis.pre_arrival_count == 1
        assert kpis.flow_distribution == {0: 1, 1: 1}


class TestKPIByMode:
    """Test KPI calculation grouped by transport mode"""

    def test_kpi_by_mode(self):
        """Test KPI calculation grouped by mode"""
        flows = [
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False
            ),
            ContainerFlow(
                flow_id="CT002",
                flow_code=FlowCode.WH_ONCE,
                wh_handling=1,
                offshore_flag=False
            ),
            LCTFlow(
                flow_id="LCT001",
                flow_code=FlowCode.WH_MOSB,
                wh_handling=1,
                offshore_flag=True
            ),
            BulkFlow(
                flow_id="BLK001",
                flow_code=FlowCode.WH_ONCE,
                wh_handling=1,
                offshore_flag=False
            ),
        ]

        calc = FlowKPICalculator()
        kpis_by_mode = calc.calculate_by_mode(flows)

        assert "container" in kpis_by_mode
        assert "lct" in kpis_by_mode
        assert "bulk" in kpis_by_mode

        # Container KPIs
        ct_kpis = kpis_by_mode["container"]
        assert ct_kpis.total_flows == 2
        assert ct_kpis.direct_delivery_rate == 50.0  # 1/2
        assert ct_kpis.mosb_pass_rate == 0.0

        # LCT KPIs
        lct_kpis = kpis_by_mode["lct"]
        assert lct_kpis.total_flows == 1
        assert lct_kpis.mosb_pass_rate == 100.0

        # Bulk KPIs
        blk_kpis = kpis_by_mode["bulk"]
        assert blk_kpis.total_flows == 1
        assert blk_kpis.avg_wh_hops == 1.0


class TestFlowConsistencyValidation:
    """Test flow consistency validation across multiple flows"""

    def test_all_consistent_flows(self):
        """Test validation with all consistent flows"""
        flows = [
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False
            ),
            LCTFlow(
                flow_id="LCT001",
                flow_code=FlowCode.WH_MOSB,
                wh_handling=1,
                offshore_flag=True
            ),
        ]

        calc = FlowKPICalculator()
        valid_count, errors = calc.validate_consistency(flows)

        assert valid_count == 2
        assert len(errors) == 0

    def test_inconsistent_flows(self):
        """Test validation with inconsistent flows"""
        flows = [
            # Consistent
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False
            ),
            # Inconsistent: FlowCode=2 but should be 1
            ContainerFlow(
                flow_id="CT002",
                flow_code=FlowCode.WH_ONCE,  # 2
                wh_handling=0,
                offshore_flag=False
            ),
            # Inconsistent: PreArrival but FlowCode=1
            ContainerFlow(
                flow_id="PRE001",
                flow_code=FlowCode.DIRECT,  # Should be 0
                wh_handling=0,
                offshore_flag=False,
                is_pre_arrival=True
            ),
        ]

        calc = FlowKPICalculator()
        valid_count, errors = calc.validate_consistency(flows)

        assert valid_count == 1
        assert len(errors) == 2
        assert "CT002" in errors[0]
        assert "PRE001" in errors[1]


class TestKPISummary:
    """Test KPI summary report generation"""

    def test_kpi_summary(self):
        """Test KPI summary report"""
        flows = [
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False
            ),
            LCTFlow(
                flow_id="LCT001",
                flow_code=FlowCode.WH_MOSB,
                wh_handling=1,
                offshore_flag=True
            ),
        ]

        calc = FlowKPICalculator()
        kpis = calc.calculate(flows)
        summary = kpis.summary()

        assert "Total Flows: 2" in summary
        assert "Direct Delivery Rate:" in summary
        assert "MOSB Pass Rate:" in summary
        assert "Flow Code Distribution:" in summary
        assert "Transport Mode Distribution:" in summary

    def test_kpi_to_dict(self):
        """Test KPI conversion to dictionary"""
        kpis = FlowKPIs(
            total_flows=10,
            pre_arrival_count=2,
            direct_delivery_rate=30.0,
            mosb_pass_rate=40.0,
            avg_wh_hops=1.2,
            flow_distribution={1: 3, 2: 4, 3: 3},
            mode_distribution={"container": 5, "lct": 5}
        )

        kpi_dict = kpis.to_dict()

        assert kpi_dict["total_flows"] == 10
        assert kpi_dict["direct_delivery_rate"] == 30.0
        assert kpi_dict["mosb_pass_rate"] == 40.0
        assert isinstance(kpi_dict["flow_distribution"], dict)

