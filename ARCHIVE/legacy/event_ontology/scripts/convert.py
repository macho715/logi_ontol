#!/usr/bin/env python3
"""
HVDC Excel to TTL Converter with Event Injection
Excel 파일을 이벤트 기반 TTL 형식으로 변환하는 스크립트
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD, BNode
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings

warnings.filterwarnings("ignore")

# 네임스페이스 정의
HVDC = Namespace("http://samsung.com/project-logistics#")

# 창고/사이트 컬럼 매핑 (import pandas as pd.py 기준)
WAREHOUSE_KEYS = [
    "dhl_wh", "dsv_indoor", "dsv_al_markaz", "aaa_storage",
    "dsv_outdoor", "dsv_mzp", "mosb", "hauler_indoor", "jdn_mzd", "shifting"
]
SITE_KEYS = ["mir", "shu", "das", "agi"]


def _pick_min_date_from_cols(row: pd.Series, cols: List[str]) -> Optional[datetime]:
    """컬럼 리스트에서 최소 날짜 추출"""
    dates = []
    for col in cols:
        val = row.get(col)
        if pd.notna(val):
            try:
                date_val = pd.to_datetime(val, errors="coerce")
                if pd.notna(date_val):
                    dates.append(date_val)
            except Exception:
                pass
    return min(dates) if dates else None


def _get_location_name(row: pd.Series, cols: List[str], target_date: datetime) -> Optional[str]:
    """날짜에 해당하는 위치명 추출"""
    for col in cols:
        val = row.get(col)
        if pd.notna(val):
            try:
                date_val = pd.to_datetime(val, errors="coerce")
                if pd.notna(date_val) and date_val == target_date:
                    return col  # 컬럼명이 위치명
            except Exception:
                pass
    return None


def inject_events_to_case(g: Graph, case_uri, row: pd.Series,
                          wh_cols: List[str], site_cols: List[str]) -> Dict:
    """
    FLOW_CODE 기반 이벤트 주입

    Args:
        g: RDF Graph
        case_uri: Case URI
        row: DataFrame 행
        wh_cols: 창고 컬럼 리스트
        site_cols: 사이트 컬럼 리스트

    Returns:
        dict: {"inbound_count": int, "outbound_count": int, "skipped": bool}
    """
    flow = str(row.get("FLOW_CODE", "")).strip()
    stats = {"inbound_count": 0, "outbound_count": 0, "skipped": False}

    # FLOW_CODE 없으면 건너뜀
    if not flow or flow not in ["1", "2", "3"]:
        stats["skipped"] = True
        return stats

    # 수량 (Pkg 없으면 1.00)
    quantity = row.get("Pkg", 1.0)
    if pd.isna(quantity):
        quantity = 1.0

    # FLOW 1: 직송 (Site 입고만)
    if flow == "1":
        site_min_date = _pick_min_date_from_cols(row, site_cols)
        if site_min_date:
            site_name = _get_location_name(row, site_cols, site_min_date)
            if site_name:
                inbound_event = BNode()
                g.add((case_uri, HVDC.hasInboundEvent, inbound_event))
                g.add((inbound_event, RDF.type, HVDC.StockEvent))
                g.add((inbound_event, HVDC.hasEventDate,
                       Literal(site_min_date.date(), datatype=XSD.date)))
                g.add((inbound_event, HVDC.hasLocationAtEvent,
                       Literal(site_name, datatype=XSD.string)))
                g.add((inbound_event, HVDC.hasQuantity,
                       Literal(float(quantity), datatype=XSD.decimal)))
                stats["inbound_count"] = 1

    # FLOW 2: 창고 경유
    elif flow == "2":
        # Inbound: 창고 최소 날짜
        wh_min_date = _pick_min_date_from_cols(row, wh_cols)
        if wh_min_date:
            wh_name = _get_location_name(row, wh_cols, wh_min_date)
            if wh_name:
                inbound_event = BNode()
                g.add((case_uri, HVDC.hasInboundEvent, inbound_event))
                g.add((inbound_event, RDF.type, HVDC.StockEvent))
                g.add((inbound_event, HVDC.hasEventDate,
                       Literal(wh_min_date.date(), datatype=XSD.date)))
                g.add((inbound_event, HVDC.hasLocationAtEvent,
                       Literal(wh_name, datatype=XSD.string)))
                g.add((inbound_event, HVDC.hasQuantity,
                       Literal(float(quantity), datatype=XSD.decimal)))
                stats["inbound_count"] = 1

        # Outbound: 사이트 최소 날짜
        site_min_date = _pick_min_date_from_cols(row, site_cols)
        if site_min_date:
            site_name = _get_location_name(row, site_cols, site_min_date)
            if site_name:
                outbound_event = BNode()
                g.add((case_uri, HVDC.hasOutboundEvent, outbound_event))
                g.add((outbound_event, RDF.type, HVDC.StockEvent))
                g.add((outbound_event, HVDC.hasEventDate,
                       Literal(site_min_date.date(), datatype=XSD.date)))
                g.add((outbound_event, HVDC.hasLocationAtEvent,
                       Literal(site_name, datatype=XSD.string)))
                g.add((outbound_event, HVDC.hasQuantity,
                       Literal(float(quantity), datatype=XSD.decimal)))
                stats["outbound_count"] = 1

    # FLOW 3: 복합 (창고+사이트 혼합)
    elif flow == "3":
        all_cols = wh_cols + site_cols
        min_date = _pick_min_date_from_cols(row, all_cols)
        if min_date:
            first_loc = _get_location_name(row, all_cols, min_date)
            if first_loc:
                inbound_event = BNode()
                g.add((case_uri, HVDC.hasInboundEvent, inbound_event))
                g.add((inbound_event, RDF.type, HVDC.StockEvent))
                g.add((inbound_event, HVDC.hasEventDate,
                       Literal(min_date.date(), datatype=XSD.date)))
                g.add((inbound_event, HVDC.hasLocationAtEvent,
                       Literal(first_loc, datatype=XSD.string)))
                g.add((inbound_event, HVDC.hasQuantity,
                       Literal(float(quantity), datatype=XSD.decimal)))
                stats["inbound_count"] = 1

        # Outbound: Final_Location_Date 사용
        final_date = row.get("Final_Location_Date")
        final_loc = row.get("Final_Location") or row.get("Status_Location")
        if pd.notna(final_date):
            try:
                final_date_val = pd.to_datetime(final_date, errors="coerce")
                if pd.notna(final_date_val) and pd.notna(final_loc):
                    outbound_event = BNode()
                    g.add((case_uri, HVDC.hasOutboundEvent, outbound_event))
                    g.add((outbound_event, RDF.type, HVDC.StockEvent))
                    g.add((outbound_event, HVDC.hasEventDate,
                           Literal(final_date_val.date(), datatype=XSD.date)))
                    g.add((outbound_event, HVDC.hasLocationAtEvent,
                           Literal(str(final_loc), datatype=XSD.string)))
                    g.add((outbound_event, HVDC.hasQuantity,
                           Literal(float(quantity), datatype=XSD.decimal)))
                    stats["outbound_count"] = 1
            except Exception:
                pass

    return stats


def convert_data_wh_to_ttl_with_events(excel_path: str, output_path: str,
                                        schema_path: Optional[str] = None) -> Dict:
    """
    DATA WH.xlsx를 이벤트 기반 TTL로 변환

    Args:
        excel_path: Excel 파일 경로
        output_path: 출력 TTL 파일 경로
        schema_path: 온톨로지 스키마 TTL 경로 (선택)

    Returns:
        dict: 변환 통계
    """
    print(f"Loading Excel file: {excel_path}")

    # 1) Excel 로드
    try:
        df = pd.read_excel(excel_path)
        print(f"SUCCESS: Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"ERROR: Excel load failed: {e}")
        return {}

    # 2) 창고/사이트 컬럼 식별 (대소문자 구분 없이)
    df_columns_lower = {col.lower(): col for col in df.columns}

    wh_cols = []
    for wh_key in WAREHOUSE_KEYS:
        for col_lower, col_orig in df_columns_lower.items():
            if wh_key in col_lower and df[col_orig].notna().sum() > 0:
                wh_cols.append(col_orig)
                break

    site_cols = []
    for site_key in SITE_KEYS:
        for col_lower, col_orig in df_columns_lower.items():
            if site_key in col_lower and df[col_orig].notna().sum() > 0:
                site_cols.append(col_orig)
                break

    print(f"   - Warehouse columns: {len(wh_cols)}")
    print(f"   - Site columns: {len(site_cols)}")

    # 3) RDF 그래프 생성
    g = Graph()
    g.bind("hvdc", HVDC)

    # 4) 스키마 로드 (선택)
    if schema_path and Path(schema_path).exists():
        g.parse(schema_path, format="turtle")
        print(f"Schema loaded: {schema_path}")

    # 5) 변환 통계
    stats = {
        "total_rows": len(df),
        "cases_created": 0,
        "inbound_events": 0,
        "outbound_events": 0,
        "skipped_no_flow": 0,
        "skipped_no_date": 0
    }

    # 6) 각 행을 Case로 변환 + 이벤트 주입
    print("\nStarting RDF conversion...")
    for idx, row in df.iterrows():
        case_uri = HVDC[f"Case_{idx+1:05d}"]
        g.add((case_uri, RDF.type, HVDC.Case))

        # 기본 속성
        if pd.notna(row.get("FLOW_CODE")):
            g.add((case_uri, HVDC.hasFlowCode,
                   Literal(str(row["FLOW_CODE"]), datatype=XSD.string)))

        if pd.notna(row.get("HVDC CODE")):
            g.add((case_uri, HVDC.hasHvdcCode,
                   Literal(str(row["HVDC CODE"]), datatype=XSD.string)))

        if pd.notna(row.get("Vendor")):
            g.add((case_uri, HVDC.hasVendor,
                   Literal(str(row["Vendor"]), datatype=XSD.string)))

        # 물리적 속성
        if pd.notna(row.get("G.W(KG)")):
            try:
                g.add((case_uri, HVDC.hasGrossWeight,
                       Literal(float(row["G.W(KG)"]), datatype=XSD.decimal)))
            except Exception:
                pass

        if pd.notna(row.get("N.W(kgs)")):
            try:
                g.add((case_uri, HVDC.hasNetWeight,
                       Literal(float(row["N.W(kgs)"]), datatype=XSD.decimal)))
            except Exception:
                pass

        if pd.notna(row.get("CBM")):
            try:
                g.add((case_uri, HVDC.hasCBM,
                       Literal(float(row["CBM"]), datatype=XSD.decimal)))
            except Exception:
                pass

        # 이벤트 주입
        event_stats = inject_events_to_case(g, case_uri, row, wh_cols, site_cols)

        stats["cases_created"] += 1
        stats["inbound_events"] += event_stats["inbound_count"]
        stats["outbound_events"] += event_stats["outbound_count"]
        if event_stats["skipped"]:
            stats["skipped_no_flow"] += 1

        # 진행 상황 출력 (1000행마다)
        if (idx + 1) % 1000 == 0:
            print(f"   Progress: {idx+1}/{len(df)} rows")

    # 7) TTL 저장
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    g.serialize(destination=output_path, format="turtle")
    print(f"\nSUCCESS: TTL saved: {output_path}")

    return stats


if __name__ == "__main__":
    import argparse
    import sys
    import io

    # Windows console encoding fix
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="Convert Excel to Event-Based TTL",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--input", required=True, help="Path to input Excel file")
    parser.add_argument("--output", required=True, help="Path to output TTL file")
    parser.add_argument("--schema", default="config/ontology/hvdc_event_schema.ttl",
                       help="Path to ontology schema TTL file")
    parser.add_argument("--report", help="Path to output report JSON file")

    args = parser.parse_args()

    # 기본 스키마 경로를 상대 경로로 조정
    if args.schema == "config/ontology/hvdc_event_schema.ttl":
        schema_path = str(Path(__file__).parent.parent / args.schema)
    else:
        schema_path = args.schema

    stats = convert_data_wh_to_ttl_with_events(args.input, args.output, schema_path)

    print("\n" + "=" * 80)
    print("Conversion Summary")
    print("=" * 80)
    print(f"TTL Output: {args.output}")
    print(f"Statistics:")
    print(f"   - Total rows: {stats.get('total_rows', 0)}")
    print(f"   - Cases created: {stats.get('cases_created', 0)}")
    print(f"   - Inbound events: {stats.get('inbound_events', 0)}")
    print(f"   - Outbound events: {stats.get('outbound_events', 0)}")
    print(f"   - No FLOW_CODE: {stats.get('skipped_no_flow', 0)}")

    # 리포트 생성 (선택)
    if args.report:
        import json
        from datetime import datetime

        report_data = {
            "source_file": args.input,
            "output_ttl": args.output,
            "conversion_date": datetime.now().isoformat(),
            "statistics": stats
        }

        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved: {args.report}")

