from rdflib import Graph
from rdflib.namespace import XSD
from .config import TTL_PATH

class SPARQLEngine:
    def __init__(self):
        self.graph = Graph()
        self.graph.parse(TTL_PATH, format='turtle')

    def _execute_query(self, query: str):
        results = self.graph.query(query)
        output = []
        for row in results:
            row_dict = {}
            for var in results.vars:
                row_dict[str(var)] = str(row[var]) if row[var] is not None else None
            output.append(row_dict)
        return output

    def get_flow_code_distribution_v35(self) -> list:
        """Get distribution including Flow 0-5 with descriptions"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?flowCode ?description (COUNT(?case) AS ?count)
        WHERE {
            ?case a hvdc:Case ;
                  hvdc:hasFlowCode ?flowStr ;
                  hvdc:hasFlowDescription ?description .
            BIND(xsd:integer(?flowStr) AS ?flowCode)
        }
        GROUP BY ?flowCode ?description
        ORDER BY ?flowCode
        """
        return self._execute_query(query)

    def get_agi_das_compliance(self) -> dict:
        """Validate AGI/DAS domain rule compliance"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT
            (COUNT(?case) AS ?totalAgiDas)
            (COUNT(?compliant) AS ?compliantCount)
        WHERE {
            ?case hvdc:hasFinalLocation ?loc .
            FILTER(?loc IN ("AGI", "DAS"))
            OPTIONAL {
                ?case hvdc:hasFlowCode ?flow .
                FILTER(xsd:integer(?flow) >= 3)
                BIND(?case AS ?compliant)
            }
        }
        """
        results = self.graph.query(query)
        for row in results:
            total = int(row.totalAgiDas) if row.totalAgiDas else 0
            compliant = int(row.compliantCount) if row.compliantCount else 0
            return {
                'total_agi_das': total,
                'compliant_count': compliant,
                'compliance_rate': (compliant / total * 100) if total > 0 else 0
            }
        return {'total_agi_das': 0, 'compliant_count': 0, 'compliance_rate': 0}

    def get_override_cases(self) -> list:
        """Get all cases with flow code overrides"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        SELECT ?caseId ?flowCode ?flowCodeOrig ?reason ?finalLoc
        WHERE {
            ?case hvdc:hasFlowCodeOriginal ?flowCodeOrig ;
                  hvdc:hasFlowOverrideReason ?reason ;
                  hvdc:hasFlowCode ?flowCode ;
                  hvdc:hasFinalLocation ?finalLoc .
            BIND(STRAFTER(STR(?case), "Case_") AS ?caseId)
        }
        """
        return self._execute_query(query)

    def get_flow_5_analysis(self) -> list:
        """Analyze mixed/incomplete cases for Flow 5"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?caseId ?vendor ?hvdcCode ?description
        WHERE {
            ?case a hvdc:Case ;
                  hvdc:hasFlowCode "5" .
            OPTIONAL { ?case hvdc:hasVendor ?vendor . }
            OPTIONAL { ?case hvdc:hasHvdcCode ?hvdcCode . }
            OPTIONAL { ?case hvdc:hasFlowDescription ?description . }
            BIND(STRAFTER(STR(?case), "Case_") AS ?caseId)
        }
        ORDER BY ?caseId
        """
        return self._execute_query(query)

    def get_pre_arrival_status(self) -> list:
        """Get Flow 0 cases"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        SELECT ?caseId ?hvdcCode ?vendor
        WHERE {
            ?case a hvdc:Case ;
                  hvdc:hasFlowCode "0" .
            OPTIONAL { ?case hvdc:hasHvdcCode ?hvdcCode . }
            OPTIONAL { ?case hvdc:hasVendor ?vendor . }
            BIND(STRAFTER(STR(?case), "Case_") AS ?caseId)
        }
        ORDER BY ?caseId
        """
        return self._execute_query(query)

    def get_case(self, case_id: str) -> dict:
        """Updated case lookup using hvdc: namespace"""
        query = f"""
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        SELECT ?flowCode ?vendor ?hvdcCode ?cbm ?description
        WHERE {{
            ?case a hvdc:Case .
            FILTER(CONTAINS(STR(?case), "{case_id}"))
            OPTIONAL {{ ?case hvdc:hasFlowCode ?flowCode . }}
            OPTIONAL {{ ?case hvdc:hasVendor ?vendor . }}
            OPTIONAL {{ ?case hvdc:hasHvdcCode ?hvdcCode . }}
            OPTIONAL {{ ?case hvdc:hasCBM ?cbm . }}
            OPTIONAL {{ ?case hvdc:hasFlowDescription ?description . }}
        }}
        LIMIT 1
        """
        results = self._execute_query(query)
        if results:
            return results[0]
        return {}

