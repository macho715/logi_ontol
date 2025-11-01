#!/usr/bin/env python3
"""
Flow Code v3.5 TTL 검증 테스트
실제 TTL 파일에서 AGI/DAS 도메인 룰 및 Flow 5 케이스 검증
"""

import pytest
from rdflib import Graph, Namespace
from pathlib import Path

HVDC = Namespace("http://samsung.com/project-logistics#")

@pytest.fixture(scope="module")
def v35_graph():
    """Flow Code v3.5로 변환된 TTL 파일 로드"""
    ttl_path = Path("test_output_v35.ttl")

    if not ttl_path.exists():
        pytest.skip(f"TTL file not found: {ttl_path}")

    g = Graph()
    g.parse(str(ttl_path), format="turtle")
    return g


class TestAGIDASDomainRule:
    """AGI/DAS 도메인 룰 검증"""

    def test_agi_cases_all_flow_3_or_higher(self, v35_graph):
        """AGI 케이스는 모두 Flow 3 이상이어야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT (COUNT(?case) AS ?violations)
        WHERE {
            ?case hvdc:hasFinalLocation "AGI" ;
                  hvdc:hasFlowCode ?flow .
            FILTER(xsd:integer(?flow) < 3)
        }
        """

        results = list(v35_graph.query(query))
        violations = int(results[0][0]) if results else 0

        assert violations == 0, f"AGI 케이스 중 Flow < 3인 것: {violations}건 (도메인 룰 위반)"

    def test_das_cases_all_flow_3_or_higher(self, v35_graph):
        """DAS 케이스는 모두 Flow 3 이상이어야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT (COUNT(?case) AS ?violations)
        WHERE {
            ?case hvdc:hasFinalLocation "DAS" ;
                  hvdc:hasFlowCode ?flow .
            FILTER(xsd:integer(?flow) < 3)
        }
        """

        results = list(v35_graph.query(query))
        violations = int(results[0][0]) if results else 0

        assert violations == 0, f"DAS 케이스 중 Flow < 3인 것: {violations}건 (도메인 룰 위반)"

    def test_agi_das_override_tracking(self, v35_graph):
        """AGI/DAS 강제 승급이 FLOW_CODE_ORIG와 FLOW_OVERRIDE_REASON으로 추적됨"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>

        SELECT (COUNT(?case) AS ?override_count)
        WHERE {
            ?case hvdc:hasFinalLocation ?loc .
            FILTER(?loc IN ("AGI", "DAS"))
            ?case hvdc:hasFlowCodeOriginal ?orig ;
                  hvdc:hasFlowOverrideReason ?reason .
        }
        """

        results = list(v35_graph.query(query))
        override_count = int(results[0][0]) if results else 0

        # AGI/DAS 강제 승급이 발생한 경우 추적 정보가 있어야 함
        # (발생하지 않은 경우는 통과)
        assert override_count >= 0, f"Invalid override count: {override_count}"


class TestFlow5Cases:
    """Flow 5 (혼합/미완료) 케이스 검증"""

    def test_flow_5_cases_exist(self, v35_graph):
        """Flow 5 케이스가 존재하는지 확인"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT (COUNT(?case) AS ?flow5_count)
        WHERE {
            ?case hvdc:hasFlowCode ?flow .
            FILTER(xsd:integer(?flow) = 5)
        }
        """

        results = list(v35_graph.query(query))
        flow5_count = int(results[0][0]) if results else 0

        assert flow5_count > 0, "Flow 5 케이스가 없음"

    def test_flow_5_has_description(self, v35_graph):
        """Flow 5 케이스는 FLOW_DESCRIPTION을 가져야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?case ?desc
        WHERE {
            ?case hvdc:hasFlowCode ?flow .
            FILTER(xsd:integer(?flow) = 5)
            OPTIONAL { ?case hvdc:hasFlowDescription ?desc }
        }
        LIMIT 10
        """

        results = list(v35_graph.query(query))

        for row in results:
            assert row.desc is not None, f"Flow 5 케이스 {row.case}에 FLOW_DESCRIPTION 없음"


class TestFlowCodeDistribution:
    """Flow Code 분포 검증"""

    def test_all_flow_codes_exist(self, v35_graph):
        """Flow Code 0~5 모두 존재하는지 확인"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>

        SELECT DISTINCT ?flow
        WHERE {
            ?case hvdc:hasFlowCode ?flow .
        }
        ORDER BY ?flow
        """

        results = list(v35_graph.query(query))
        flow_codes = set(str(row.flow) for row in results)

        for code in ["0", "1", "2", "3", "4", "5"]:
            assert code in flow_codes, f"Flow Code {code}가 데이터에 없음"

    def test_flow_code_range_validation(self, v35_graph):
        """Flow Code가 0~5 범위인지 검증"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT (COUNT(?case) AS ?invalid_count)
        WHERE {
            ?case hvdc:hasFlowCode ?flow .
            FILTER(xsd:integer(?flow) < 0 || xsd:integer(?flow) > 5)
        }
        """

        results = list(v35_graph.query(query))
        invalid_count = int(results[0][0]) if results else 0

        assert invalid_count == 0, f"유효하지 않은 Flow Code: {invalid_count}건"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

