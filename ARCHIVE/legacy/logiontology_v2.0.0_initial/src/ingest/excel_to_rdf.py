"""Excel to RDF converter for HVDC data."""

import pandas as pd
from pathlib import Path
from rdflib import Graph, Literal, Namespace, URIRef, RDF, XSD
from typing import Optional
import logging

from src.core.flow_models import FlowCode
from src.integration.site_normalizer import SiteNormalizer

logger = logging.getLogger(__name__)

HVDC = Namespace("https://hvdc-project.com/ontology#")


class ExcelToRDFConverter:
    """Convert Excel logistics data to RDF format."""

    def __init__(self):
        """Initialize converter with graph and normalizer."""
        self.graph = Graph()
        self.graph.bind("hvdc", HVDC)
        self.normalizer = SiteNormalizer()
        self._cargo_counter = 0

    def convert(self, excel_path: Path, output_path: Path) -> Graph:
        """
        Convert Excel file to RDF TTL format.

        Args:
            excel_path: Path to input Excel file
            output_path: Path to output TTL file

        Returns:
            RDF Graph
        """
        logger.info(f"Converting Excel file: {excel_path}")

        # Read Excel
        df = pd.read_excel(excel_path)
        logger.info(f"Loaded {len(df)} rows from Excel")

        # Convert each row
        for idx, row in df.iterrows():
            self._convert_row(row, idx)

        # Serialize to TTL
        self.graph.serialize(destination=output_path, format="turtle")
        logger.info(f"RDF graph saved to: {output_path}")

        return self.graph

    def _convert_row(self, row: pd.Series, idx: int):
        """Convert single Excel row to RDF triples."""
        # Generate cargo IRI
        hvdc_code = row.get('HVDC_CODE') or row.get('hvdc_code') or f"AUTO-{idx:04d}"
        cargo_iri = HVDC[f"cargo-{hvdc_code}"]

        # Add cargo type
        self.graph.add((cargo_iri, RDF.type, HVDC.Cargo))

        # Add HVDC code
        self.graph.add((cargo_iri, HVDC.hasHVDCCode, Literal(hvdc_code, datatype=XSD.string)))

        # Add weight if available
        weight = row.get('WEIGHT') or row.get('weight')
        if weight and pd.notna(weight):
            self.graph.add((cargo_iri, HVDC.weight, Literal(float(weight), datatype=XSD.decimal)))

        # Add warehouse relationship
        warehouse = row.get('WAREHOUSE') or row.get('warehouse')
        if warehouse and pd.notna(warehouse):
            wh_code = self.normalizer.normalize_code(str(warehouse))
            if wh_code:
                wh_iri = HVDC[wh_code.lower().replace('_', '-')]
                self.graph.add((cargo_iri, HVDC.storedAt, wh_iri))

                # Ensure warehouse exists as instance
                self.graph.add((wh_iri, RDF.type, HVDC.Warehouse))
                self.graph.add((wh_iri, HVDC.warehouseName, Literal(wh_code, datatype=XSD.string)))

        # Add site relationship
        site = row.get('SITE') or row.get('site') or row.get('DESTINATION')
        if site and pd.notna(site):
            site_code = self.normalizer.normalize_code(str(site))
            if site_code:
                site_iri = HVDC[site_code.lower()]
                self.graph.add((cargo_iri, HVDC.destinedTo, site_iri))

                # Ensure site exists as instance
                self.graph.add((site_iri, RDF.type, HVDC.Site))
                self.graph.add((site_iri, HVDC.siteName, Literal(site_code, datatype=XSD.string)))

        # Add port if available
        port = row.get('PORT') or row.get('port')
        if port and pd.notna(port):
            port_code = self.normalizer.normalize_code(str(port))
            if port_code:
                port_iri = HVDC[port_code.lower().replace('_', '-')]
                self.graph.add((cargo_iri, HVDC.fromPort, port_iri))

                # Ensure port exists
                self.graph.add((port_iri, RDF.type, HVDC.Port))
                self.graph.add((port_iri, HVDC.portName, Literal(port_code, datatype=XSD.string)))

        # Calculate and add flow code
        flow_code = self._calculate_flow_code(row)
        if flow_code is not None:
            flow_code_iri = HVDC[f"flow-code-{flow_code}"]
            self.graph.add((cargo_iri, HVDC.hasFlowCode, flow_code_iri))

    def _calculate_flow_code(self, row: pd.Series) -> Optional[int]:
        """Calculate flow code based on row data."""
        # Check if flow code is explicitly provided
        explicit_code = row.get('FLOW_CODE') or row.get('flow_code')
        if explicit_code and pd.notna(explicit_code):
            return int(explicit_code)

        # Otherwise, infer from data
        wh_handling = row.get('WH_HANDLING') or row.get('wh_handling') or 0
        offshore_flag = row.get('OFFSHORE') or row.get('offshore_flag') or False
        is_pre_arrival = row.get('PRE_ARRIVAL') or row.get('is_pre_arrival') or False

        if is_pre_arrival:
            return 0

        # Calculate: 1 + wh_handling + offshore_flag
        code = 1 + int(wh_handling) + (1 if offshore_flag else 0)

        # Clip to [1, 4]
        return max(1, min(4, code))


