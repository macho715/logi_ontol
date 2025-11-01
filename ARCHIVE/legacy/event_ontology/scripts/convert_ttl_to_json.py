#!/usr/bin/env python3
"""
TTL to JSON Flat Converter
TTL 파일을 GPT용 평탄화 JSON으로 변환
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from rdflib import Graph, Namespace

HVDC = Namespace("http://samsung.com/project-logistics#")


def flatten_ttl_to_json(ttl_path: str, output_path: str) -> Dict:
    """
    TTL을 GPT용 평탄화 JSON으로 변환

    변환 규칙:
    1. Case 단위로 레코드 생성
    2. Inbound/Outbound 이벤트를 필드로 펼침
    3. 중첩 구조 제거 (flat structure)

    Args:
        ttl_path: TTL 파일 경로
        output_path: JSON 출력 경로

    Returns:
        dict: 변환 통계
    """
    print(f"Loading TTL file: {ttl_path}")

    g = Graph()
    g.parse(ttl_path, format="turtle")

    print(f"SUCCESS: Loaded {len(g)} triples")

    # SPARQL: Case 기본 정보 + 이벤트 조인
    query = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?case ?hvdcCode ?flowCode ?vendor ?grossWeight ?netWeight ?cbm
           ?inboundDate ?inboundLocation ?inboundQty
           ?outboundDate ?outboundLocation ?outboundQty
    WHERE {
        ?case a hvdc:Case .

        OPTIONAL { ?case hvdc:hasHvdcCode ?hvdcCode }
        OPTIONAL { ?case hvdc:hasFlowCode ?flowCode }
        OPTIONAL { ?case hvdc:hasVendor ?vendor }
        OPTIONAL { ?case hvdc:hasGrossWeight ?grossWeight }
        OPTIONAL { ?case hvdc:hasNetWeight ?netWeight }
        OPTIONAL { ?case hvdc:hasCBM ?cbm }

        OPTIONAL {
            ?case hvdc:hasInboundEvent ?inEvent .
            ?inEvent hvdc:hasEventDate ?inboundDate ;
                     hvdc:hasLocationAtEvent ?inboundLocation ;
                     hvdc:hasQuantity ?inboundQty .
        }

        OPTIONAL {
            ?case hvdc:hasOutboundEvent ?outEvent .
            ?outEvent hvdc:hasEventDate ?outboundDate ;
                      hvdc:hasLocationAtEvent ?outboundLocation ;
                      hvdc:hasQuantity ?outboundQty .
        }
    }
    ORDER BY ?case
    """

    print("\nExecuting SPARQL query...")
    results = g.query(query)

    # 레코드 변환
    records = []
    for row in results:
        record = {
            "case_id": str(row.case).split("/")[-1] if row.case else None,
            "hvdc_code": str(row.hvdcCode) if row.hvdcCode else None,
            "flow_code": str(row.flowCode) if row.flowCode else None,
            "vendor": str(row.vendor) if row.vendor else None,
            "gross_weight": float(row.grossWeight) if row.grossWeight else None,
            "net_weight": float(row.netWeight) if row.netWeight else None,
            "cbm": float(row.cbm) if row.cbm else None,
        }

        # Inbound event
        if row.inboundDate:
            record["inbound"] = {
                "date": str(row.inboundDate),
                "location": str(row.inboundLocation),
                "quantity": float(row.inboundQty) if row.inboundQty else None
            }
        else:
            record["inbound"] = None

        # Outbound event
        if row.outboundDate:
            record["outbound"] = {
                "date": str(row.outboundDate),
                "location": str(row.outboundLocation),
                "quantity": float(row.outboundQty) if row.outboundQty else None
            }
        else:
            record["outbound"] = None

        records.append(record)

    print(f"SUCCESS: Converted {len(records)} cases to JSON")

    # JSON 저장
    output = {
        "metadata": {
            "source_ttl": ttl_path,
            "total_cases": len(records),
            "generated_at": datetime.now().isoformat()
        },
        "cases": records
    }

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"SUCCESS: JSON saved: {output_path}")

    return {
        "total_cases": len(records),
        "output_file": output_path
    }


def generate_precomputed_views(ttl_path: str, output_dir: str) -> Dict[str, str]:
    """
    GPT용 사전 집계 뷰 생성 (월별 창고, Vendor별 등)

    Args:
        ttl_path: TTL 파일 경로
        output_dir: 출력 디렉토리

    Returns:
        dict: 생성된 파일 목록 {view_name: file_path}
    """
    print(f"\nGenerating precomputed views from: {ttl_path}")

    g = Graph()
    g.parse(ttl_path, format="turtle")

    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(parents=True, exist_ok=True)

    views = {}

    # 1) 월별 창고 입고 집계
    print("  - Monthly warehouse inbound...")
    monthly_wh_query = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?date ?location ?qty
    WHERE {
        ?case hvdc:hasInboundEvent ?event .
        ?event hvdc:hasEventDate ?date ;
               hvdc:hasLocationAtEvent ?location ;
               hvdc:hasQuantity ?qty .
    }
    """

    results = g.query(monthly_wh_query)

    # Python으로 집계 처리
    from collections import defaultdict
    monthly_data = defaultdict(lambda: defaultdict(lambda: {"count": 0, "qty": 0.0}))

    for row in results:
        month = str(row.date)[:7]  # YYYY-MM
        location = str(row.location)
        qty = float(row.qty) if row.qty else 0.0

        monthly_data[month][location]["count"] += 1
        monthly_data[month][location]["qty"] += qty

    monthly_wh = [
        {
            "month": month,
            "warehouse": location,
            "event_count": data["count"],
            "total_quantity": data["qty"]
        }
        for month in sorted(monthly_data.keys())
        for location, data in sorted(monthly_data[month].items())
    ]

    monthly_wh_file = output_dir_obj / "monthly_warehouse_inbound.json"
    with open(monthly_wh_file, 'w', encoding='utf-8') as f:
        json.dump(monthly_wh, f, indent=2, ensure_ascii=False)
    views["monthly_warehouse"] = str(monthly_wh_file)
    print(f"    SUCCESS: {len(monthly_wh)} records")

    # 2) Vendor별 월별 입고
    print("  - Vendor monthly summary...")
    vendor_query = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?vendor ?date ?qty
    WHERE {
        ?case hvdc:hasVendor ?vendor ;
              hvdc:hasInboundEvent ?event .
        ?event hvdc:hasEventDate ?date ;
               hvdc:hasQuantity ?qty .
    }
    """

    results = g.query(vendor_query)

    # Python으로 집계 처리
    vendor_data = defaultdict(lambda: defaultdict(lambda: {"count": 0, "qty": 0.0}))

    for row in results:
        if not row.vendor:
            continue
        vendor = str(row.vendor)
        month = str(row.date)[:7]
        qty = float(row.qty) if row.qty else 0.0

        vendor_data[vendor][month]["count"] += 1
        vendor_data[vendor][month]["qty"] += qty

    vendor_summary = [
        {
            "vendor": vendor,
            "month": month,
            "event_count": data["count"],
            "total_quantity": data["qty"]
        }
        for vendor in sorted(vendor_data.keys())
        for month, data in sorted(vendor_data[vendor].items())
    ]

    vendor_file = output_dir_obj / "vendor_summary.json"
    with open(vendor_file, 'w', encoding='utf-8') as f:
        json.dump(vendor_summary, f, indent=2, ensure_ascii=False)
    views["vendor_summary"] = str(vendor_file)
    print(f"    SUCCESS: {len(vendor_summary)} records")

    # 3) FLOW 코드별 케이스 분포
    print("  - Flow code distribution...")
    flow_query = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?case ?flowCode
    WHERE {
        ?case a hvdc:Case .
        OPTIONAL { ?case hvdc:hasFlowCode ?flowCode }
    }
    """

    results = g.query(flow_query)

    # Python으로 집계 처리
    flow_counts = defaultdict(int)

    for row in results:
        flow = str(row.flowCode) if row.flowCode else "NO_FLOW"
        flow_counts[flow] += 1

    flow_dist = [
        {
            "flow_code": flow,
            "case_count": count
        }
        for flow, count in sorted(flow_counts.items())
    ]

    flow_file = output_dir_obj / "cases_by_flow.json"
    with open(flow_file, 'w', encoding='utf-8') as f:
        json.dump(flow_dist, f, indent=2, ensure_ascii=False)
    views["flow_distribution"] = str(flow_file)
    print(f"    SUCCESS: {len(flow_dist)} records")

    print(f"\nSUCCESS: Generated {len(views)} precomputed views")
    return views


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python ttl_to_json_flat.py <ttl_path> <output_path> [views_dir]")
        sys.exit(1)

    ttl_path = sys.argv[1]
    output_path = sys.argv[2]
    views_dir = sys.argv[3] if len(sys.argv) > 3 else None

    # TTL -> JSON
    stats = flatten_ttl_to_json(ttl_path, output_path)

    # Precomputed views
    if views_dir:
        views = generate_precomputed_views(ttl_path, views_dir)
        print(f"\nGenerated views:")
        for name, path in views.items():
            print(f"  - {name}: {path}")

