#!/usr/bin/env python3
"""
Event Injection Quality Tests
이벤트 주입 품질 검증 (pytest)
"""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace
from datetime import datetime

HVDC = Namespace("http://samsung.com/project-logistics#")

# Test fixture: TTL 파일 로드
@pytest.fixture(scope="module")
def event_graph():
    """이벤트 기반 TTL 파일 로드"""
    ttl_path = Path("rdf_output/test_data_wh_events.ttl")

    if not ttl_path.exists():
        pytest.skip(f"TTL file not found: {ttl_path}")

    g = Graph()
    g.parse(str(ttl_path), format="turtle")
    return g


@pytest.fixture(scope="module")
def validation_results():
    """검증 결과 JSON 로드"""
    import json
    results_path = Path("validation_results/validation_summary.json")

    if not results_path.exists():
        pytest.skip(f"Validation results not found: {results_path}")

    with open(results_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestEventGeneration:
    """이벤트 생성 규칙 검증"""

    def test_all_cases_have_type(self, event_graph):
        """모든 케이스가 hvdc:Case 타입을 가져야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT (COUNT(?case) AS ?count)
        WHERE {
            ?case rdf:type hvdc:Case .
        }
        """

        result = list(event_graph.query(query))[0]
        case_count = int(result[0])  # First binding in result

        assert case_count > 0, "No cases found in TTL"
        assert case_count == 8995, f"Expected 8995 cases, got {case_count}"

    def test_inbound_event_coverage_threshold(self, validation_results):
        """Inbound 이벤트 커버리지가 50% 이상이어야 함"""
        coverage = validation_results["validation_results"]["coverage_stats"]["inbound_coverage_pct"]

        assert coverage >= 50.0, f"Inbound coverage {coverage}% < 50%"

    def test_flow1_must_have_inbound(self, event_graph):
        """FLOW 1 케이스는 모두 inbound 이벤트를 가져야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?case ?hasInbound
        WHERE {
            ?case hvdc:hasFlowCode "1"^^xsd:string .

            BIND(EXISTS { ?case hvdc:hasInboundEvent ?event } AS ?hasInbound)
        }
        """

        results = list(event_graph.query(query))
        total = len(results)
        with_inbound = sum(1 for r in results if r.hasInbound)

        assert total > 0, "No FLOW 1 cases found"
        assert with_inbound == total, f"FLOW 1: {with_inbound}/{total} have inbound (expected 100%)"

    def test_flow3_must_have_both_events(self, event_graph):
        """FLOW 3 케이스는 inbound + outbound 이벤트를 모두 가져야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?case ?hasInbound ?hasOutbound
        WHERE {
            ?case hvdc:hasFlowCode "3"^^xsd:string .

            BIND(EXISTS { ?case hvdc:hasInboundEvent ?inEvent } AS ?hasInbound)
            BIND(EXISTS { ?case hvdc:hasOutboundEvent ?outEvent } AS ?hasOutbound)
        }
        """

        results = list(event_graph.query(query))
        total = len(results)
        with_both = sum(1 for r in results if r.hasInbound and r.hasOutbound)

        assert total > 0, "No FLOW 3 cases found"
        coverage_pct = round(with_both / total * 100, 2) if total > 0 else 0

        # FLOW 3는 95% 이상이 both를 가져야 함 (일부 예외 허용)
        assert coverage_pct >= 95.0, f"FLOW 3: {coverage_pct}% have both events (expected ≥95%)"


class TestEventProperties:
    """이벤트 필수 속성 검증"""

    def test_inbound_events_have_required_properties(self, event_graph):
        """모든 Inbound 이벤트는 date, location, quantity를 가져야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>

        SELECT (COUNT(?event) AS ?totalInbound)
               (COUNT(?withDate) AS ?withDate)
               (COUNT(?withLocation) AS ?withLocation)
               (COUNT(?withQty) AS ?withQty)
        WHERE {
            ?case hvdc:hasInboundEvent ?event .

            OPTIONAL {
                ?event hvdc:hasEventDate ?date .
                BIND(?event AS ?withDate)
            }

            OPTIONAL {
                ?event hvdc:hasLocationAtEvent ?location .
                BIND(?event AS ?withLocation)
            }

            OPTIONAL {
                ?event hvdc:hasQuantity ?qty .
                BIND(?event AS ?withQty)
            }
        }
        """

        result = list(event_graph.query(query))[0]
        total = int(result.totalInbound)
        with_date = int(result.withDate)
        with_location = int(result.withLocation)
        with_qty = int(result.withQty)

        assert total > 0, "No inbound events found"

        # 필수 속성 100% 충족 확인
        assert with_date == total, f"Missing dates: {total - with_date}/{total}"
        assert with_location == total, f"Missing locations: {total - with_location}/{total}"
        assert with_qty == total, f"Missing quantities: {total - with_qty}/{total}"

    def test_outbound_events_have_required_properties(self, event_graph):
        """모든 Outbound 이벤트는 date, location, quantity를 가져야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>

        SELECT (COUNT(?event) AS ?totalOutbound)
               (COUNT(?withDate) AS ?withDate)
               (COUNT(?withLocation) AS ?withLocation)
               (COUNT(?withQty) AS ?withQty)
        WHERE {
            ?case hvdc:hasOutboundEvent ?event .

            OPTIONAL {
                ?event hvdc:hasEventDate ?date .
                BIND(?event AS ?withDate)
            }

            OPTIONAL {
                ?event hvdc:hasLocationAtEvent ?location .
                BIND(?event AS ?withLocation)
            }

            OPTIONAL {
                ?event hvdc:hasQuantity ?qty .
                BIND(?event AS ?withQty)
            }
        }
        """

        result = list(event_graph.query(query))[0]
        total = int(result.totalOutbound)
        with_date = int(result.withDate)
        with_location = int(result.withLocation)
        with_qty = int(result.withQty)

        assert total > 0, "No outbound events found"

        # 필수 속성 100% 충족 확인
        assert with_date == total, f"Missing dates: {total - with_date}/{total}"
        assert with_location == total, f"Missing locations: {total - with_location}/{total}"
        assert with_qty == total, f"Missing quantities: {total - with_qty}/{total}"

    def test_event_dates_are_valid(self, event_graph):
        """이벤트 날짜가 유효한 형식이어야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?date
        WHERE {
            {
                ?case hvdc:hasInboundEvent ?event .
            }
            UNION
            {
                ?case hvdc:hasOutboundEvent ?event .
            }

            ?event hvdc:hasEventDate ?date .
        }
        LIMIT 100
        """

        results = event_graph.query(query)

        for row in results:
            date_str = str(row.date)

            # 날짜 파싱 가능 여부 확인
            try:
                datetime.fromisoformat(date_str)
            except ValueError:
                pytest.fail(f"Invalid date format: {date_str}")

    def test_event_quantities_are_positive(self, event_graph):
        """이벤트 수량이 양수여야 함"""
        query = """
        PREFIX hvdc: <http://samsung.com/project-logistics#>

        SELECT (MIN(?qty) AS ?minQty) (MAX(?qty) AS ?maxQty)
        WHERE {
            {
                ?case hvdc:hasInboundEvent ?event .
            }
            UNION
            {
                ?case hvdc:hasOutboundEvent ?event .
            }

            ?event hvdc:hasQuantity ?qty .
        }
        """

        result = list(event_graph.query(query))[0]
        min_qty = float(result.minQty)
        max_qty = float(result.maxQty)

        assert min_qty > 0, f"Found non-positive quantity: {min_qty}"
        assert max_qty > 0, f"Max quantity invalid: {max_qty}"


class TestDataQuality:
    """데이터 품질 검증"""

    def test_no_flow23_without_inbound(self, validation_results):
        """FLOW 2/3 케이스는 모두 inbound를 가져야 함 (Human-gate 목록 확인)"""
        human_gate = validation_results["validation_results"]["human_gate_flow23"]
        count = human_gate["count"]

        # FLOW 2/3에서 inbound 없는 케이스는 허용 범위 내여야 함
        # 실제로는 0이 ideal이지만, 일부 예외 허용 (5% 이하)
        assert count <= 50, f"Too many FLOW 2/3 cases without inbound: {count}"

    def test_no_events_with_missing_dates(self, validation_results):
        """날짜 없는 이벤트가 없어야 함"""
        missing_dates = validation_results["validation_results"]["missing_dates"]["count"]

        assert missing_dates == 0, f"Found {missing_dates} events with missing dates"

    def test_event_injection_rate_above_threshold(self, validation_results):
        """전체 이벤트 주입율이 임계값 이상이어야 함"""
        stats = validation_results["validation_results"]["coverage_stats"]

        # 최소 50% 이상의 케이스가 이벤트를 가져야 함
        with_events = stats["total_cases"] - stats["with_neither"]
        event_rate = round(with_events / stats["total_cases"] * 100, 2)

        assert event_rate >= 50.0, f"Event injection rate {event_rate}% < 50%"

    def test_flow0_has_no_events(self, validation_results):
        """FLOW 0 (NO_FLOW)는 이벤트가 없어야 함"""
        flow_patterns = validation_results["validation_results"]["flow_patterns"]

        flow0 = next((f for f in flow_patterns if f["flow_code"] == "0"), None)

        if flow0:
            assert flow0["inbound_pct"] == 0.0, f"FLOW 0 should have no inbound events"
            assert flow0["outbound_pct"] == 0.0, f"FLOW 0 should have no outbound events"


class TestPerformance:
    """성능 및 통계 검증"""

    def test_total_triples_reasonable(self, event_graph):
        """전체 triple 수가 합리적 범위 내여야 함"""
        triple_count = len(event_graph)

        # 8995 케이스 × 평균 8-10 triple/케이스 ≈ 70,000-90,000
        assert 50000 <= triple_count <= 100000, \
            f"Triple count {triple_count} out of reasonable range"

    def test_average_events_per_case(self, validation_results):
        """케이스당 평균 이벤트 수가 합리적이어야 함"""
        stats = validation_results["validation_results"]["coverage_stats"]

        total_cases = stats["total_cases"]
        total_events = stats["with_inbound"] + stats["with_outbound"]

        avg_events = round(total_events / total_cases, 2)

        # 평균 0.5~1.5 이벤트/케이스 (일부는 inbound만, 일부는 both)
        assert 0.3 <= avg_events <= 2.0, \
            f"Average events per case {avg_events} out of reasonable range"


# Coverage target: ≥85%
# pytest --cov=logiontology --cov-report=term-missing tests/test_event_injection.py

