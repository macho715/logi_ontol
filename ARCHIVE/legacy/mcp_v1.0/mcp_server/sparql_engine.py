"""
SPARQL Engine for querying hvdc_data.ttl using RDFLib
"""
import rdflib
from rdflib import Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SPARQLEngine:
    """RDFLib-based SPARQL query engine for HVDC logistics data"""

    def __init__(self, ttl_path: str):
        """
        Initialize SPARQL engine and load TTL file

        Args:
            ttl_path: Path to hvdc_data.ttl file
        """
        self.graph = rdflib.Graph()
        self.hvdc = Namespace("http://samsung.com/project-logistics#")
        self.graph.bind("hvdc", self.hvdc)

        try:
            logger.info(f"Loading TTL file: {ttl_path}")
            self.graph.parse(ttl_path, format='turtle')
            logger.info(f"Successfully loaded {len(self.graph)} triples")
        except Exception as e:
            logger.error(f"Failed to parse TTL file: {e}")
            raise ValueError(f"Failed to parse TTL file: {e}")

    def execute_query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        Execute raw SPARQL query and return results as list of dicts

        Args:
            sparql_query: SPARQL SELECT query

        Returns:
            List of result rows as dictionaries
        """
        try:
            results = self.graph.query(sparql_query)
            return [
                {str(var): self._convert_rdf_value(row[var])
                 for var in results.vars if row[var] is not None}
                for row in results
            ]
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            raise ValueError(f"SPARQL query failed: {e}")

    def _convert_rdf_value(self, value: Any) -> Any:
        """Convert RDF value to Python native type"""
        if isinstance(value, Literal):
            return value.toPython()
        elif isinstance(value, rdflib.URIRef):
            # Extract local name from URI (e.g., hvdc:Case_00045 -> Case_00045)
            return str(value).split('#')[-1] if '#' in str(value) else str(value)
        else:
            return str(value)

    def get_case_by_id(self, case_id: str) -> Dict[str, Any]:
        """
        Lookup case by ID

        Args:
            case_id: Case ID (e.g., "Case_00045" or "hvdc:Case_00045")

        Returns:
            Dictionary with case details including events
        """
        # Normalize case_id
        if not case_id.startswith("Case_"):
            case_id = f"Case_{case_id}"

        query = f"""
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?flow_code ?vendor ?cbm ?net_weight
               ?in_date ?in_location ?in_quantity
               ?out_date ?out_location ?out_quantity
        WHERE {{
            hvdc:{case_id} a hvdc:Case .

            OPTIONAL {{ hvdc:{case_id} hvdc:hasFlowCode ?flow_code }}
            OPTIONAL {{ hvdc:{case_id} hvdc:hasVendor ?vendor }}
            OPTIONAL {{ hvdc:{case_id} hvdc:hasCBM ?cbm }}
            OPTIONAL {{ hvdc:{case_id} hvdc:hasNetWeight ?net_weight }}

            OPTIONAL {{
                hvdc:{case_id} hvdc:hasInboundEvent ?in_event .
                ?in_event hvdc:hasEventDate ?in_date ;
                          hvdc:hasLocationAtEvent ?in_location ;
                          hvdc:hasQuantity ?in_quantity .
            }}

            OPTIONAL {{
                hvdc:{case_id} hvdc:hasOutboundEvent ?out_event .
                ?out_event hvdc:hasEventDate ?out_date ;
                           hvdc:hasLocationAtEvent ?out_location ;
                           hvdc:hasQuantity ?out_quantity .
            }}
        }}
        LIMIT 1
        """

        results = self.execute_query(query)
        if not results:
            raise ValueError(f"Case {case_id} not found in TTL")

        result = results[0]

        # Build response structure
        response = {
            "case_id": case_id,
            "flow_code": result.get("flow_code"),
            "vendor": result.get("vendor"),
            "cbm": result.get("cbm"),
            "net_weight": result.get("net_weight"),
        }

        # Add inbound event if exists
        if result.get("in_date"):
            response["inbound_event"] = {
                "date": str(result["in_date"]),
                "location": result.get("in_location"),
                "quantity": float(result.get("in_quantity", 1.0))
            }

        # Add outbound event if exists
        if result.get("out_date"):
            response["outbound_event"] = {
                "date": str(result["out_date"]),
                "location": result.get("out_location"),
                "quantity": float(result.get("out_quantity", 1.0))
            }

        return response

    def get_monthly_warehouse(self, year_month: str) -> List[Dict[str, Any]]:
        """
        Get monthly warehouse inbound/outbound summary

        Args:
            year_month: YYYY-MM format (e.g., "2024-03")

        Returns:
            List of warehouse aggregations
        """
        query = f"""
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?location (COUNT(?event) AS ?event_count) (SUM(?quantity) AS ?total_qty)
        WHERE {{
            {{
                ?case hvdc:hasInboundEvent ?event .
                ?event hvdc:hasEventDate ?date ;
                       hvdc:hasLocationAtEvent ?location ;
                       hvdc:hasQuantity ?quantity .
                FILTER(STRSTARTS(STR(?date), "{year_month}"))
            }} UNION {{
                ?case hvdc:hasOutboundEvent ?event .
                ?event hvdc:hasEventDate ?date ;
                       hvdc:hasLocationAtEvent ?location ;
                       hvdc:hasQuantity ?quantity .
                FILTER(STRSTARTS(STR(?date), "{year_month}"))
            }}
        }}
        GROUP BY ?location
        ORDER BY DESC(?event_count)
        """

        return self.execute_query(query)

    def get_vendor_summary(self, vendor: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get vendor summary (case count, inbound/outbound events)

        Args:
            vendor: Optional vendor name filter

        Returns:
            List of vendor aggregations
        """
        vendor_filter = f'FILTER(?vendor = "{vendor}"^^xsd:string)' if vendor else ''

        query = f"""
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?vendor (COUNT(DISTINCT ?case) AS ?case_count)
               (COUNT(DISTINCT ?in_event) AS ?inbound_count)
               (COUNT(DISTINCT ?out_event) AS ?outbound_count)
        WHERE {{
            ?case a hvdc:Case ;
                  hvdc:hasVendor ?vendor .
            {vendor_filter}

            OPTIONAL {{ ?case hvdc:hasInboundEvent ?in_event }}
            OPTIONAL {{ ?case hvdc:hasOutboundEvent ?out_event }}
        }}
        GROUP BY ?vendor
        ORDER BY DESC(?case_count)
        """

        return self.execute_query(query)

    def get_flow_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of cases by FLOW code"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?flow_code (COUNT(?case) AS ?count)
        WHERE {
            ?case a hvdc:Case ;
                  hvdc:hasFlowCode ?flow_code .
        }
        GROUP BY ?flow_code
        ORDER BY ?flow_code
        """

        return self.execute_query(query)

    def search_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Search cases by location (inbound or outbound)

        Args:
            location: Location name (e.g., "MOSB", "DAS", "DSV Indoor")

        Returns:
            List of cases with events at that location
        """
        query = f"""
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?case_id ?event_type ?date ?quantity
        WHERE {{
            ?case a hvdc:Case .
            BIND(STRAFTER(STR(?case), "#") AS ?case_id)

            {{
                ?case hvdc:hasInboundEvent ?event .
                BIND("inbound" AS ?event_type)
            }} UNION {{
                ?case hvdc:hasOutboundEvent ?event .
                BIND("outbound" AS ?event_type)
            }}

            ?event hvdc:hasLocationAtEvent "{location}"^^xsd:string ;
                   hvdc:hasEventDate ?date ;
                   hvdc:hasQuantity ?quantity .
        }}
        ORDER BY ?date
        """

        return self.execute_query(query)

    def search_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Search events by date range

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of events in date range
        """
        query = f"""
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?case_id ?event_type ?date ?location ?quantity
        WHERE {{
            ?case a hvdc:Case .
            BIND(STRAFTER(STR(?case), "#") AS ?case_id)

            {{
                ?case hvdc:hasInboundEvent ?event .
                BIND("inbound" AS ?event_type)
            }} UNION {{
                ?case hvdc:hasOutboundEvent ?event .
                BIND("outbound" AS ?event_type)
            }}

            ?event hvdc:hasEventDate ?date ;
                   hvdc:hasLocationAtEvent ?location ;
                   hvdc:hasQuantity ?quantity .

            FILTER(?date >= "{start_date}"^^xsd:date && ?date <= "{end_date}"^^xsd:date)
        }}
        ORDER BY ?date
        """

        return self.execute_query(query)

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics from TTL"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>

        SELECT (COUNT(DISTINCT ?case) AS ?total_cases)
               (COUNT(DISTINCT ?in_event) AS ?total_inbound)
               (COUNT(DISTINCT ?out_event) AS ?total_outbound)
        WHERE {
            ?case a hvdc:Case .
            OPTIONAL { ?case hvdc:hasInboundEvent ?in_event }
            OPTIONAL { ?case hvdc:hasOutboundEvent ?out_event }
        }
        """

        results = self.execute_query(query)
        return results[0] if results else {}


