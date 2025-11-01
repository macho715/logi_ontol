"""
HVDC Flow RDF Mapper v1.0
Maps Flow Code models to RDF/Turtle format
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, OWL
from pathlib import Path
from typing import List, Union
from ..core.flow_models import (
    LogisticsFlow,
    ContainerFlow,
    BulkFlow,
    LandFlow,
    LCTFlow,
    FlowCode
)

# Namespaces
HVDC = Namespace("https://hvdc.example.org/ns#")
HVDC_FLOW = Namespace("https://hvdc.example.org/flow#")
HVDCI = Namespace("https://hvdc.example.org/id/")


class FlowRDFMapper:
    """Map logistics flows to RDF graph"""

    def __init__(self):
        """Initialize RDF graph with namespaces"""
        self.g = Graph()
        self.g.bind("hvdc", HVDC)
        self.g.bind("hvdc-flow", HVDC_FLOW)
        self.g.bind("hvdci", HVDCI)
        self.g.bind("rdf", RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("xsd", XSD)
        self.g.bind("owl", OWL)

    def add_flow(self, flow: LogisticsFlow) -> URIRef:
        """
        Add a logistics flow to RDF graph

        Args:
            flow: LogisticsFlow instance

        Returns:
            URIRef of the flow
        """
        flow_uri = HVDCI[f"Flow/{flow.flow_id}"]

        # Determine flow class by type
        if isinstance(flow, ContainerFlow):
            self.g.add((flow_uri, RDF.type, HVDC_FLOW.ContainerFlow))
            self._add_container_attributes(flow_uri, flow)
        elif isinstance(flow, BulkFlow):
            self.g.add((flow_uri, RDF.type, HVDC_FLOW.BulkFlow))
            self._add_bulk_attributes(flow_uri, flow)
        elif isinstance(flow, LandFlow):
            self.g.add((flow_uri, RDF.type, HVDC_FLOW.LandFlow))
            self._add_land_attributes(flow_uri, flow)
        elif isinstance(flow, LCTFlow):
            self.g.add((flow_uri, RDF.type, HVDC_FLOW.LCTFlow))
            self._add_lct_attributes(flow_uri, flow)
        else:
            self.g.add((flow_uri, RDF.type, HVDC_FLOW.LogisticsFlow))

        # Add common properties
        self._add_common_properties(flow_uri, flow)

        return flow_uri

    def _add_common_properties(self, flow_uri: URIRef, flow: LogisticsFlow):
        """Add common flow properties"""
        self.g.add((
            flow_uri,
            HVDC_FLOW.hasFlowCode,
            Literal(int(flow.flow_code), datatype=XSD.integer)
        ))
        self.g.add((
            flow_uri,
            HVDC_FLOW.hasWHHandling,
            Literal(flow.wh_handling, datatype=XSD.integer)
        ))
        self.g.add((
            flow_uri,
            HVDC_FLOW.hasOffshoreFlag,
            Literal(flow.offshore_flag, datatype=XSD.boolean)
        ))
        self.g.add((
            flow_uri,
            HVDC_FLOW.isPreArrival,
            Literal(flow.is_pre_arrival, datatype=XSD.boolean)
        ))
        self.g.add((
            flow_uri,
            HVDC_FLOW.hasTransportMode,
            Literal(flow.transport_mode, datatype=XSD.string)
        ))

        if flow.flow_description:
            self.g.add((
                flow_uri,
                HVDC_FLOW.hasFlowDescription,
                Literal(flow.flow_description, datatype=XSD.string)
            ))

    def _add_container_attributes(self, flow_uri: URIRef, flow: ContainerFlow):
        """Add container-specific attributes"""
        if flow.gate_appt_win_min is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.gateApptWinMin,
                Literal(flow.gate_appt_win_min, datatype=XSD.integer)
            ))
        if flow.cy_in_out_lag_hr is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.CYInOutLagHr,
                Literal(flow.cy_in_out_lag_hr, datatype=XSD.decimal)
            ))
        if flow.unload_rate_tph is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.unloadRateTph,
                Literal(flow.unload_rate_tph, datatype=XSD.decimal)
            ))

    def _add_bulk_attributes(self, flow_uri: URIRef, flow: BulkFlow):
        """Add bulk-specific attributes"""
        if flow.unload_rate_tph is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.unloadRateTph,
                Literal(flow.unload_rate_tph, datatype=XSD.decimal)
            ))
        if flow.spillage_risk_pct is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.spillageRiskPct,
                Literal(flow.spillage_risk_pct, datatype=XSD.decimal)
            ))

    def _add_land_attributes(self, flow_uri: URIRef, flow: LandFlow):
        """Add land transport-specific attributes"""
        if flow.convoy_period_min is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.convoyPeriodMin,
                Literal(flow.convoy_period_min, datatype=XSD.integer)
            ))
        if flow.dot_permit_lead_days is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.DOTPermitLeadDays,
                Literal(flow.dot_permit_lead_days, datatype=XSD.integer)
            ))

    def _add_lct_attributes(self, flow_uri: URIRef, flow: LCTFlow):
        """Add LCT-specific attributes"""
        if flow.ramp_cycle_min is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.rampCycleMin,
                Literal(flow.ramp_cycle_min, datatype=XSD.integer)
            ))
        if flow.stowage_util_pct is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.stowageUtilPct,
                Literal(flow.stowage_util_pct, datatype=XSD.decimal)
            ))
        if flow.lolo_slots is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.LOLOslots,
                Literal(flow.lolo_slots, datatype=XSD.integer)
            ))
        if flow.voyage_time_hours is not None:
            self.g.add((
                flow_uri,
                HVDC_FLOW.voyageTimeHours,
                Literal(flow.voyage_time_hours, datatype=XSD.decimal)
            ))

    def add_flows(self, flows: List[LogisticsFlow]) -> List[URIRef]:
        """
        Add multiple flows to graph

        Args:
            flows: List of LogisticsFlow instances

        Returns:
            List of URIRefs
        """
        return [self.add_flow(flow) for flow in flows]

    def serialize(self, out_path: Union[str, Path], format: str = "turtle") -> Path:
        """
        Serialize graph to file

        Args:
            out_path: Output file path
            format: RDF format (turtle, xml, nt, n3)

        Returns:
            Path to output file
        """
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        self.g.serialize(out, format=format)
        return out

    def get_graph(self) -> Graph:
        """Get the RDF graph"""
        return self.g

    @classmethod
    def from_flows(cls, flows: List[LogisticsFlow]) -> "FlowRDFMapper":
        """
        Create mapper and add flows in one step

        Args:
            flows: List of LogisticsFlow instances

        Returns:
            FlowRDFMapper instance
        """
        mapper = cls()
        mapper.add_flows(flows)
        return mapper

