#!/usr/bin/env python3
"""
SPARQL Event Validation Script
이벤트 기반 TTL 데이터 품질 검증
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime
from rdflib import Graph

# Windows console encoding fix
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def run_sparql_validation(ttl_path: str, output_dir: str) -> dict:
    """
    SPARQL 쿼리로 이벤트 데이터 검증

    Args:
        ttl_path: TTL 파일 경로
        output_dir: 검증 결과 출력 디렉토리

    Returns:
        dict: 검증 통계
    """
    print("=" * 80)
    print("SPARQL Event Validation")
    print("=" * 80)

    print(f"\nLoading TTL: {ttl_path}")
    g = Graph()
    g.parse(ttl_path, format="turtle")
    print(f"SUCCESS: Loaded {len(g)} triples")

    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(parents=True, exist_ok=True)

    results = {}

    # Query 4: FLOW 2/3 without Inbound (Human-gate)
    print("\n" + "=" * 80)
    print("Query 4: FLOW 2/3 Cases without Inbound Events (Human-gate)")
    print("=" * 80)

    query_4 = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?case ?flowCode ?hvdcCode
    WHERE {
        ?case a hvdc:Case ;
              hvdc:hasFlowCode ?flowCode .

        OPTIONAL { ?case hvdc:hasHvdcCode ?hvdcCode }

        FILTER(?flowCode IN ("2", "3"))

        FILTER NOT EXISTS {
            ?case hvdc:hasInboundEvent ?inEvent .
        }
    }
    ORDER BY ?flowCode ?case
    """

    q4_results = g.query(query_4)
    q4_data = [
        {
            "case_id": str(row.case).split("/")[-1],
            "flow_code": str(row.flowCode),
            "hvdc_code": str(row.hvdcCode) if row.hvdcCode else None
        }
        for row in q4_results
    ]

    print(f"FOUND: {len(q4_data)} cases requiring manual verification")

    q4_file = output_dir_obj / "human_gate_flow23_no_inbound.json"
    with open(q4_file, 'w', encoding='utf-8') as f:
        json.dump(q4_data, f, indent=2, ensure_ascii=False)

    results["human_gate_flow23"] = {
        "count": len(q4_data),
        "file": str(q4_file)
    }

    # Query 5: Missing Event Dates (Human-gate)
    print("\n" + "=" * 80)
    print("Query 5: Events with Missing Dates (Human-gate)")
    print("=" * 80)

    query_5 = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?case ?event ?eventType
    WHERE {
        ?case a hvdc:Case .

        {
            ?case hvdc:hasInboundEvent ?event .
            BIND("inbound" AS ?eventType)
            FILTER NOT EXISTS {
                ?event hvdc:hasEventDate ?date .
            }
        }
        UNION
        {
            ?case hvdc:hasOutboundEvent ?event .
            BIND("outbound" AS ?eventType)
            FILTER NOT EXISTS {
                ?event hvdc:hasEventDate ?date .
            }
        }
    }
    ORDER BY ?case ?eventType
    """

    q5_results = g.query(query_5)
    q5_data = [
        {
            "case_id": str(row.case).split("/")[-1],
            "event_type": str(row.eventType),
            "event_uri": str(row.event)
        }
        for row in q5_results
    ]

    print(f"FOUND: {len(q5_data)} events with missing dates")

    q5_file = output_dir_obj / "human_gate_missing_dates.json"
    with open(q5_file, 'w', encoding='utf-8') as f:
        json.dump(q5_data, f, indent=2, ensure_ascii=False)

    results["missing_dates"] = {
        "count": len(q5_data),
        "file": str(q5_file)
    }

    # Query 6: Event Coverage Statistics
    print("\n" + "=" * 80)
    print("Query 6: Event Coverage Statistics")
    print("=" * 80)

    query_6 = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?case ?hasInbound ?hasOutbound
    WHERE {
        ?case a hvdc:Case .

        BIND(EXISTS { ?case hvdc:hasInboundEvent ?in } AS ?hasInbound)
        BIND(EXISTS { ?case hvdc:hasOutboundEvent ?out } AS ?hasOutbound)
    }
    """

    q6_results = list(g.query(query_6))

    total_cases = len(q6_results)
    with_inbound = sum(1 for r in q6_results if r.hasInbound)
    with_outbound = sum(1 for r in q6_results if r.hasOutbound)
    with_both = sum(1 for r in q6_results if r.hasInbound and r.hasOutbound)
    with_neither = sum(1 for r in q6_results if not r.hasInbound and not r.hasOutbound)

    coverage_stats = {
        "total_cases": total_cases,
        "with_inbound": with_inbound,
        "with_outbound": with_outbound,
        "with_both": with_both,
        "with_neither": with_neither,
        "inbound_coverage_pct": round(with_inbound / total_cases * 100, 2) if total_cases > 0 else 0,
        "outbound_coverage_pct": round(with_outbound / total_cases * 100, 2) if total_cases > 0 else 0
    }

    print(f"Total cases: {total_cases}")
    print(f"With inbound: {with_inbound} ({coverage_stats['inbound_coverage_pct']}%)")
    print(f"With outbound: {with_outbound} ({coverage_stats['outbound_coverage_pct']}%)")
    print(f"With both: {with_both}")
    print(f"With neither: {with_neither}")

    coverage_file = output_dir_obj / "event_coverage_stats.json"
    with open(coverage_file, 'w', encoding='utf-8') as f:
        json.dump(coverage_stats, f, indent=2, ensure_ascii=False)

    results["coverage_stats"] = coverage_stats

    # Query 9: FLOW-wise Event Pattern Validation
    print("\n" + "=" * 80)
    print("Query 9: FLOW-wise Event Pattern Validation")
    print("=" * 80)

    query_9 = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?flowCode ?case ?hasInbound ?hasOutbound
    WHERE {
        ?case a hvdc:Case ;
              hvdc:hasFlowCode ?flowCode .

        BIND(EXISTS { ?case hvdc:hasInboundEvent ?in } AS ?hasInbound)
        BIND(EXISTS { ?case hvdc:hasOutboundEvent ?out } AS ?hasOutbound)
    }
    """

    q9_results = list(g.query(query_9))

    from collections import defaultdict
    flow_stats = defaultdict(lambda: {"total": 0, "with_inbound": 0, "with_outbound": 0})

    for row in q9_results:
        flow = str(row.flowCode)
        flow_stats[flow]["total"] += 1
        if row.hasInbound:
            flow_stats[flow]["with_inbound"] += 1
        if row.hasOutbound:
            flow_stats[flow]["with_outbound"] += 1

    flow_validation = [
        {
            "flow_code": flow,
            "total_cases": data["total"],
            "with_inbound": data["with_inbound"],
            "with_outbound": data["with_outbound"],
            "inbound_pct": round(data["with_inbound"] / data["total"] * 100, 2) if data["total"] > 0 else 0,
            "outbound_pct": round(data["with_outbound"] / data["total"] * 100, 2) if data["total"] > 0 else 0
        }
        for flow, data in sorted(flow_stats.items())
    ]

    for item in flow_validation:
        print(f"FLOW {item['flow_code']}: {item['total_cases']} cases, "
              f"inbound={item['inbound_pct']}%, outbound={item['outbound_pct']}%")

    flow_file = output_dir_obj / "flow_event_patterns.json"
    with open(flow_file, 'w', encoding='utf-8') as f:
        json.dump(flow_validation, f, indent=2, ensure_ascii=False)

    results["flow_patterns"] = flow_validation

    # Summary Report
    print("\n" + "=" * 80)
    print("Validation Summary")
    print("=" * 80)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "source_ttl": ttl_path,
        "total_triples": len(g),
        "validation_results": results
    }

    summary_file = output_dir_obj / "validation_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nValidation complete. Results saved to: {output_dir}")
    print(f"Summary: {summary_file}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SPARQL Event Validation")
    parser.add_argument("--ttl", required=True, help="Path to TTL file")
    parser.add_argument("--output", default="validation_results", help="Output directory")

    args = parser.parse_args()

    results = run_sparql_validation(args.ttl, args.output)

    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print(f"1. Review Human-gate lists: {args.output}/human_gate_*.json")
    print("2. Verify FLOW patterns match expected rules")
    print("3. Address missing dates if any")
    print("4. Run pytest for automated quality checks")

