"""
SHACL validation tests for HVDC Flow Code
"""

import pytest
from pathlib import Path
from rdflib import Graph
from pyshacl import validate
from src.mapping.flow_rdf_mapper import FlowRDFMapper
from src.core.flow_models import (
    ContainerFlow,
    BulkFlow,
    LCTFlow,
    FlowCode
)


class TestSHACLFlowCodeRange:
    """Test SHACL validates FlowCode range [0,4]"""

    def test_valid_flow_code_range(self):
        """Test SHACL accepts FlowCode in range [0,4]"""
        mapper = FlowRDFMapper()

        # Add flows with all valid codes (0-4)
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
            LCTFlow(
                flow_id="LCT002",
                flow_code=FlowCode.WH_DOUBLE_MOSB,
                wh_handling=2,
                offshore_flag=True
            ),
        ]

        for flow in flows:
            mapper.add_flow(flow)

        data_graph = mapper.get_graph()
        shapes_path = Path("logiontology/configs/shapes/FlowCode.shape.ttl")

        if not shapes_path.exists():
            pytest.skip("SHACL shapes file not found")

        conforms, results_graph, results_text = validate(
            data_graph=data_graph,
            shacl_graph=str(shapes_path),
            inference='rdfs',
            abort_on_first=False
        )

        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestSHACLPreArrivalConstraint:
    """Test SHACL enforces PreArrival→FlowCode=0"""

    def test_valid_pre_arrival(self):
        """Test SHACL accepts PreArrival with FlowCode=0"""
        mapper = FlowRDFMapper()

        flow = ContainerFlow(
            flow_id="PRE001",
            flow_code=FlowCode.PRE_ARRIVAL,
            wh_handling=0,
            offshore_flag=False,
            is_pre_arrival=True
        )
        mapper.add_flow(flow)

        data_graph = mapper.get_graph()
        shapes_path = Path("logiontology/configs/shapes/FlowCode.shape.ttl")

        if not shapes_path.exists():
            pytest.skip("SHACL shapes file not found")

        conforms, _, results_text = validate(
            data_graph=data_graph,
            shacl_graph=str(shapes_path),
            inference='rdfs'
        )

        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestSHACLContainerAttributes:
    """Test SHACL validates Container-specific attributes"""

    def test_valid_container_attributes(self):
        """Test SHACL accepts valid container attributes"""
        mapper = FlowRDFMapper()

        flow = ContainerFlow(
            flow_id="CT001",
            flow_code=FlowCode.DIRECT,
            wh_handling=0,
            offshore_flag=False,
            gate_appt_win_min=120,  # Valid: 0-1440
            cy_in_out_lag_hr=2.5,  # Valid: >= 0
            unload_rate_tph=25.0  # Valid: > 0
        )
        mapper.add_flow(flow)

        data_graph = mapper.get_graph()
        shapes_path = Path("logiontology/configs/shapes/FlowCode.shape.ttl")

        if not shapes_path.exists():
            pytest.skip("SHACL shapes file not found")

        conforms, _, results_text = validate(
            data_graph=data_graph,
            shacl_graph=str(shapes_path),
            inference='rdfs'
        )

        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestSHACLLCTAttributes:
    """Test SHACL validates LCT-specific attributes"""

    def test_valid_lct_attributes(self):
        """Test SHACL accepts valid LCT attributes"""
        mapper = FlowRDFMapper()

        flow = LCTFlow(
            flow_id="LCT001",
            flow_code=FlowCode.WH_MOSB,
            wh_handling=1,
            offshore_flag=True,
            ramp_cycle_min=45,  # Valid: > 0
            stowage_util_pct=85.5,  # Valid: 0-100
            lolo_slots=12,  # Valid: >= 0
            voyage_time_hours=10.5  # Valid: > 0
        )
        mapper.add_flow(flow)

        data_graph = mapper.get_graph()
        shapes_path = Path("logiontology/configs/shapes/FlowCode.shape.ttl")

        if not shapes_path.exists():
            pytest.skip("SHACL shapes file not found")

        conforms, _, results_text = validate(
            data_graph=data_graph,
            shacl_graph=str(shapes_path),
            inference='rdfs'
        )

        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestSHACLBulkAttributes:
    """Test SHACL validates Bulk-specific attributes"""

    def test_valid_bulk_attributes(self):
        """Test SHACL accepts valid bulk attributes"""
        mapper = FlowRDFMapper()

        flow = BulkFlow(
            flow_id="BLK001",
            flow_code=FlowCode.WH_ONCE,
            wh_handling=1,
            offshore_flag=False,
            unload_rate_tph=50.0,  # Valid: > 0
            spillage_risk_pct=15.5  # Valid: 0-100
        )
        mapper.add_flow(flow)

        data_graph = mapper.get_graph()
        shapes_path = Path("logiontology/configs/shapes/FlowCode.shape.ttl")

        if not shapes_path.exists():
            pytest.skip("SHACL shapes file not found")

        conforms, _, results_text = validate(
            data_graph=data_graph,
            shacl_graph=str(shapes_path),
            inference='rdfs'
        )

        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestSHACLConsistencyRule:
    """Test SHACL FlowCode consistency rule"""

    def test_consistent_flows_pass(self):
        """Test SHACL accepts consistent flows"""
        mapper = FlowRDFMapper()

        # All consistent flows
        flows = [
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,  # 1
                wh_handling=0,
                offshore_flag=False
            ),
            LCTFlow(
                flow_id="LCT001",
                flow_code=FlowCode.WH_MOSB,  # 3 = 1+1+1
                wh_handling=1,
                offshore_flag=True
            ),
        ]

        for flow in flows:
            mapper.add_flow(flow)

        data_graph = mapper.get_graph()
        shapes_path = Path("logiontology/configs/shapes/FlowCode.shape.ttl")

        if not shapes_path.exists():
            pytest.skip("SHACL shapes file not found")

        conforms, _, results_text = validate(
            data_graph=data_graph,
            shacl_graph=str(shapes_path),
            inference='rdfs',
            abort_on_first=False
        )

        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestSHACLFullValidation:
    """Test complete SHACL validation with mixed scenarios"""

    def test_full_validation_suite(self):
        """Test comprehensive SHACL validation"""
        mapper = FlowRDFMapper()

        # Add diverse flow types
        flows = [
            # Pre-arrival
            ContainerFlow(
                flow_id="PRE001",
                flow_code=FlowCode.PRE_ARRIVAL,
                wh_handling=0,
                offshore_flag=False,
                is_pre_arrival=True
            ),
            # Container direct
            ContainerFlow(
                flow_id="CT001",
                flow_code=FlowCode.DIRECT,
                wh_handling=0,
                offshore_flag=False,
                gate_appt_win_min=120,
                cy_in_out_lag_hr=2.0,
                unload_rate_tph=30.0
            ),
            # Bulk with WH
            BulkFlow(
                flow_id="BLK001",
                flow_code=FlowCode.WH_ONCE,
                wh_handling=1,
                offshore_flag=False,
                unload_rate_tph=45.0,
                spillage_risk_pct=20.0
            ),
            # LCT offshore
            LCTFlow(
                flow_id="LCT001",
                flow_code=FlowCode.WH_MOSB,
                wh_handling=1,
                offshore_flag=True,
                ramp_cycle_min=40,
                stowage_util_pct=80.0,
                lolo_slots=10,
                voyage_time_hours=12.0
            ),
        ]

        for flow in flows:
            mapper.add_flow(flow)

        data_graph = mapper.get_graph()
        shapes_path = Path("logiontology/configs/shapes/FlowCode.shape.ttl")

        if not shapes_path.exists():
            pytest.skip("SHACL shapes file not found")

        conforms, results_graph, results_text = validate(
            data_graph=data_graph,
            shacl_graph=str(shapes_path),
            inference='rdfs',
            abort_on_first=False
        )

        assert conforms, f"SHACL validation failed:\n{results_text}"

