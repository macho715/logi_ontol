#!/usr/bin/env python3
"""
TTL to JSON Converter - CLI Script
TTL 파일을 GPT용 평탄화 JSON으로 변환

Usage:
    python scripts/core/ttl_to_json.py --input data.ttl --output result.json
    python scripts/core/ttl_to_json.py --input data.ttl --output result.json --views output/views/
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
import logging
import json
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

# 프로젝트 루트를 PYTHONPATH에 추가
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from rdflib import Graph, Namespace

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 네임스페이스
HVDC = Namespace("http://samsung.com/project-logistics#")


def flatten_ttl_to_json(ttl_path: str, output_path: str) -> Dict:
    """
    TTL을 GPT용 평탄화 JSON으로 변환

    변환 규칙:
    1. Case 단위로 레코드 생성
    2. Inbound/Outbound 이벤트를 필드로 펼침
    3. 중첩 구조 제거 (flat structure)
    4. Flow Code v3.5 속성 포함

    Args:
        ttl_path: TTL 파일 경로
        output_path: JSON 출력 경로

    Returns:
        dict: 변환 통계
    """
    logger.info(f"Loading TTL file: {ttl_path}")

    g = Graph()
    g.parse(ttl_path, format="turtle")

    logger.info(f"Loaded {len(g)} triples")

    # SPARQL: Case 기본 정보 + 이벤트 조인 (v3.5 확장)
    query = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?case ?hvdcCode ?flowCode ?flowCodeOrig ?flowOverrideReason ?flowDesc ?finalLocation
           ?vendor ?grossWeight ?netWeight ?cbm
           ?inboundDate ?inboundLocation ?inboundQty
           ?outboundDate ?outboundLocation ?outboundQty
    WHERE {
        ?case a hvdc:Case .

        OPTIONAL { ?case hvdc:hasHvdcCode ?hvdcCode }
        OPTIONAL { ?case hvdc:hasFlowCode ?flowCode }
        OPTIONAL { ?case hvdc:hasFlowCodeOriginal ?flowCodeOrig }
        OPTIONAL { ?case hvdc:hasFlowOverrideReason ?flowOverrideReason }
        OPTIONAL { ?case hvdc:hasFlowDescription ?flowDesc }
        OPTIONAL { ?case hvdc:hasFinalLocation ?finalLocation }
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

    logger.info("Executing SPARQL query...")
    results = g.query(query)

    # 레코드 변환
    records = []
    for row in results:
        record = {
            "case_id": str(row.case).split("/")[-1] if row.case else None,
            "hvdc_code": str(row.hvdcCode) if row.hvdcCode else None,
            "flow_code": str(row.flowCode) if row.flowCode else None,
            "flow_code_original": int(row.flowCodeOrig) if row.flowCodeOrig else None,
            "flow_override_reason": str(row.flowOverrideReason) if row.flowOverrideReason else None,
            "flow_description": str(row.flowDesc) if row.flowDesc else None,
            "final_location": str(row.finalLocation) if row.finalLocation else None,
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

    logger.info(f"Converted {len(records)} cases to JSON")

    # JSON 저장
    output = {
        "metadata": {
            "source_ttl": ttl_path,
            "total_cases": len(records),
            "generated_at": datetime.now().isoformat(),
            "flow_code_version": "3.5"
        },
        "cases": records
    }

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"JSON saved: {output_path}")

    return {
        "total_cases": len(records),
        "output_file": output_path
    }


def generate_precomputed_views(ttl_path: str, output_dir: str) -> Dict[str, str]:
    """
    GPT용 사전 집계 뷰 생성 (월별 창고, Vendor별, Flow 분포 등)

    Args:
        ttl_path: TTL 파일 경로
        output_dir: 출력 디렉토리

    Returns:
        dict: 생성된 파일 목록 {view_name: file_path}
    """
    logger.info(f"Generating precomputed views from: {ttl_path}")

    g = Graph()
    g.parse(ttl_path, format="turtle")

    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(parents=True, exist_ok=True)

    views = {}

    # 1) 월별 창고 입고 집계
    logger.info("  - Monthly warehouse inbound...")
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
    logger.info(f"    Created: {len(monthly_wh)} records")

    # 2) Vendor별 월별 입고
    logger.info("  - Vendor monthly summary...")
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
    logger.info(f"    Created: {len(vendor_summary)} records")

    # 3) FLOW 코드별 케이스 분포 (v3.5 확장)
    logger.info("  - Flow code distribution (v3.5)...")
    flow_query = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?case ?flowCode ?flowCodeOrig ?flowOverrideReason
    WHERE {
        ?case a hvdc:Case .
        OPTIONAL { ?case hvdc:hasFlowCode ?flowCode }
        OPTIONAL { ?case hvdc:hasFlowCodeOriginal ?flowCodeOrig }
        OPTIONAL { ?case hvdc:hasFlowOverrideReason ?flowOverrideReason }
    }
    """

    results = g.query(flow_query)

    # Python으로 집계 처리
    flow_counts = defaultdict(int)
    override_counts = defaultdict(int)

    for row in results:
        flow = str(row.flowCode) if row.flowCode else "NO_FLOW"
        flow_counts[flow] += 1

        if row.flowOverrideReason:
            override_counts[flow] += 1

    flow_dist = [
        {
            "flow_code": flow,
            "case_count": count,
            "override_count": override_counts.get(flow, 0)
        }
        for flow, count in sorted(flow_counts.items())
    ]

    flow_file = output_dir_obj / "cases_by_flow.json"
    with open(flow_file, 'w', encoding='utf-8') as f:
        json.dump(flow_dist, f, indent=2, ensure_ascii=False)
    views["flow_distribution"] = str(flow_file)
    logger.info(f"    Created: {len(flow_dist)} records")

    logger.info(f"Generated {len(views)} precomputed views")
    return views


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="TTL to JSON Converter - Convert TTL to GPT-friendly flat JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 기본 변환 (TTL → JSON)
  python scripts/core/ttl_to_json.py \\
      --input output/hvdc_status_v35.ttl \\
      --output output/hvdc_flat.json

  # 사전 집계 뷰 포함
  python scripts/core/ttl_to_json.py \\
      --input output/hvdc_status_v35.ttl \\
      --output output/hvdc_flat.json \\
      --views output/views/

  # 메타데이터만 (뷰 생성만)
  python scripts/core/ttl_to_json.py \\
      --input output/hvdc_status_v35.ttl \\
      --views-only output/views/
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input TTL file path'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file path (flat format)'
    )
    parser.add_argument(
        '--views',
        help='Output directory for precomputed views (optional)'
    )
    parser.add_argument(
        '--views-only',
        help='Generate only precomputed views (no flat JSON)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # 로깅 레벨 설정
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # 파일 확인
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"TTL file not found: {input_path}")
        sys.exit(1)

    logger.info(f"Input TTL: {input_path}")

    # 1) Flat JSON 변환
    if not args.views_only:
        if not args.output:
            logger.error("--output required (or use --views-only)")
            sys.exit(1)

        try:
            stats = flatten_ttl_to_json(str(input_path), args.output)
            logger.info(f"Flat JSON conversion complete: {stats['total_cases']} cases")
        except Exception as e:
            logger.error(f"Flat JSON conversion failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # 2) Precomputed views
    views_dir = args.views or args.views_only
    if views_dir:
        try:
            views = generate_precomputed_views(str(input_path), views_dir)
            logger.info("Precomputed views generated")
            print("\n" + "="*60)
            print("Generated Views:")
            print("="*60)
            for name, path in views.items():
                print(f"  {name:<20} -> {path}")
            print("="*60 + "\n")
        except Exception as e:
            logger.error(f"Precomputed views generation failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    logger.info("Conversion complete!")


if __name__ == "__main__":
    main()

