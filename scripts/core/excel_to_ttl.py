#!/usr/bin/env python3
"""
Excel to TTL Converter - CLI Script
Excel 파일을 이벤트 기반 TTL (Turtle) 형식으로 변환

Usage:
    python scripts/core/excel_to_ttl.py --input data.xlsx --output result.ttl
    python scripts/core/excel_to_ttl.py --input data.xlsx --output result.ttl --schema ontology/schema.ttl --flow-version 3.5
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
import logging

# 프로젝트 루트를 PYTHONPATH에 추가
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD, BNode
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings

warnings.filterwarnings("ignore")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 네임스페이스 정의
HVDC = Namespace("http://samsung.com/project-logistics#")

# 기본 창고/사이트 컬럼 (HVDC 프로젝트 표준)
DEFAULT_WAREHOUSE_KEYS = [
    "DSV Indoor", "DSV Outdoor", "DSV MZD", "DSV MZP", "DSV Al Markaz",
    "JDN MZD", "JDN Waterfront",
    "MOSB",
    "AAA Storage", "Hauler DG Storage", "DHL WH", "Hauler Indoor",
    "Shifting", "ZENER (WH)", "Vijay Tanks"
]
DEFAULT_SITE_KEYS = ["SHU", "MIR", "DAS", "AGI"]


# ============================================================================
# Core Functions
# ============================================================================

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
    if not flow or flow not in ["0", "1", "2", "3", "4", "5"]:
        stats["skipped"] = True
        return stats

    # Flow 0: Pre Arrival → 이벤트 없음
    if flow == "0":
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

    # FLOW 3: Port → MOSB → Site (MOSB 경유)
    elif flow == "3":
        # MOSB 컬럼 찾기
        mosb_cols = [col for col in wh_cols + site_cols if 'MOSB' in col.upper()]

        # Inbound: MOSB 날짜
        if mosb_cols:
            mosb_date = _pick_min_date_from_cols(row, mosb_cols)
            if mosb_date:
                mosb_name = _get_location_name(row, mosb_cols, mosb_date)
                if mosb_name:
                    inbound_event = BNode()
                    g.add((case_uri, HVDC.hasInboundEvent, inbound_event))
                    g.add((inbound_event, RDF.type, HVDC.StockEvent))
                    g.add((inbound_event, HVDC.hasEventDate,
                           Literal(mosb_date.date(), datatype=XSD.date)))
                    g.add((inbound_event, HVDC.hasLocationAtEvent,
                           Literal(mosb_name, datatype=XSD.string)))
                    g.add((inbound_event, HVDC.hasQuantity,
                           Literal(float(quantity), datatype=XSD.decimal)))
                    stats["inbound_count"] = 1

        # Outbound: Site 최종 날짜
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

    # FLOW 4: Port → WH → MOSB → Site (창고+MOSB 경유)
    elif flow == "4":
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

        # Outbound: Site 최종 날짜
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

    # FLOW 5: Mixed/Incomplete (혼합 케이스)
    elif flow == "5":
        # 혼합 케이스: 제한적 이벤트 생성
        stats["skipped"] = True

    return stats


def convert_excel_to_ttl(excel_path: str, output_path: str,
                         warehouse_cols: List[str],
                         site_cols: List[str],
                         schema_path: Optional[str] = None,
                         flow_version: str = "3.5") -> Dict:
    """
    Excel을 이벤트 기반 TTL로 변환

    Args:
        excel_path: Excel 파일 경로
        output_path: 출력 TTL 파일 경로
        warehouse_cols: 창고 컬럼 리스트
        site_cols: 사이트 컬럼 리스트
        schema_path: 온톨로지 스키마 TTL 경로 (선택)
        flow_version: Flow Code 버전 ("3.5" 기본값)

    Returns:
        dict: 변환 통계
    """
    logger.info(f"Loading Excel file: {excel_path}")

    # 1) Excel 로드
    try:
        df = pd.read_excel(excel_path)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        logger.error(f"Excel load failed: {e}")
        return {}

    # 1.5) Flow Code v3.5 계산 (옵션)
    if flow_version == "3.5":
        logger.info("Calculating Flow Code v3.5...")
        try:
            # flow_code_calculator 모듈 import
            sys.path.insert(0, str(ROOT / "logiontology" / "src" / "ingest"))
            from flow_code_calculator import calculate_flow_code_v35

            df = calculate_flow_code_v35(df, warehouse_cols, site_cols)
            logger.info("Flow Code v3.5 applied")
            flow_dist = df['FLOW_CODE'].value_counts().sort_index().to_dict()
            logger.info(f"Flow Code distribution: {flow_dist}")

            # AGI/DAS 강제 승급 통계
            override_count = df['FLOW_OVERRIDE_REASON'].notna().sum()
            if override_count > 0:
                logger.info(f"AGI/DAS forced upgrade: {override_count} cases")
        except Exception as e:
            logger.warning(f"Flow Code v3.5 calculation failed: {e}")
            logger.warning("Continuing with existing FLOW_CODE column...")
            import traceback
            traceback.print_exc()

    # 2) 창고/사이트 컬럼 식별 (정규화 후 컬럼명 사용)
    df_columns_lower = {col.lower(): col for col in df.columns}

    wh_cols = []
    for wh_key in warehouse_cols:
        wh_key_lower = wh_key.lower()
        # 정확한 매칭 우선
        if wh_key_lower in df_columns_lower:
            col_orig = df_columns_lower[wh_key_lower]
            if df[col_orig].notna().sum() > 0:
                wh_cols.append(col_orig)
        else:
            # 부분 매칭 시도
            for col_lower, col_orig in df_columns_lower.items():
                if wh_key_lower in col_lower and df[col_orig].notna().sum() > 0:
                    wh_cols.append(col_orig)
                    break

    site_cols_actual = []
    for site_key in site_cols:
        site_key_lower = site_key.lower()
        # 정확한 매칭만
        if site_key_lower in df_columns_lower:
            col_orig = df_columns_lower[site_key_lower]
            if df[col_orig].notna().sum() > 0:
                site_cols_actual.append(col_orig)

    logger.info(f"Warehouse columns found: {len(wh_cols)}")
    logger.info(f"Site columns found: {len(site_cols_actual)}")

    # 3) RDF 그래프 생성
    g = Graph()
    g.bind("hvdc", HVDC)

    # 4) 스키마 로드 (선택)
    if schema_path and Path(schema_path).exists():
        g.parse(schema_path, format="turtle")
        logger.info(f"Schema loaded: {schema_path}")

    # 5) 변환 통계
    stats = {
        "total_rows": len(df),
        "cases_created": 0,
        "inbound_events": 0,
        "outbound_events": 0,
        "skipped_no_flow": 0,
    }

    # 6) 각 행을 Case로 변환 + 이벤트 주입
    logger.info("Starting RDF conversion...")
    for idx, row in df.iterrows():
        case_uri = HVDC[f"Case_{idx+1:05d}"]
        g.add((case_uri, RDF.type, HVDC.Case))

        # 기본 속성
        if pd.notna(row.get("FLOW_CODE")):
            g.add((case_uri, HVDC.hasFlowCode,
                   Literal(str(row["FLOW_CODE"]), datatype=XSD.string)))

        # v3.5 추가 속성
        if pd.notna(row.get("FLOW_CODE_ORIG")):
            g.add((case_uri, HVDC.hasFlowCodeOriginal,
                   Literal(int(row["FLOW_CODE_ORIG"]), datatype=XSD.integer)))

        if pd.notna(row.get("FLOW_OVERRIDE_REASON")):
            g.add((case_uri, HVDC.hasFlowOverrideReason,
                   Literal(str(row["FLOW_OVERRIDE_REASON"]), datatype=XSD.string)))

        if pd.notna(row.get("FLOW_DESCRIPTION")):
            g.add((case_uri, HVDC.hasFlowDescription,
                   Literal(str(row["FLOW_DESCRIPTION"]), datatype=XSD.string)))

        if pd.notna(row.get("Final_Location")):
            g.add((case_uri, HVDC.hasFinalLocation,
                   Literal(str(row["Final_Location"]), datatype=XSD.string)))

        if pd.notna(row.get("HVDC CODE")):
            g.add((case_uri, HVDC.hasHvdcCode,
                   Literal(str(row["HVDC CODE"]), datatype=XSD.string)))

        if pd.notna(row.get("VENDOR")):
            g.add((case_uri, HVDC.hasVendor,
                   Literal(str(row["VENDOR"]), datatype=XSD.string)))

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
        event_stats = inject_events_to_case(g, case_uri, row, wh_cols, site_cols_actual)

        stats["cases_created"] += 1
        stats["inbound_events"] += event_stats["inbound_count"]
        stats["outbound_events"] += event_stats["outbound_count"]
        if event_stats["skipped"]:
            stats["skipped_no_flow"] += 1

        # 진행 상황 출력 (1000행마다)
        if (idx + 1) % 1000 == 0:
            logger.info(f"Progress: {idx+1}/{len(df)} rows")

    # 7) TTL 저장
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    g.serialize(destination=output_path, format="turtle")
    logger.info(f"TTL saved: {output_path}")

    return stats


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Excel to TTL Converter - Convert Excel data to event-based RDF/TTL format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 기본 변환 (Flow Code v3.5 자동 계산)
  python scripts/core/excel_to_ttl.py \\
      --input data/HVDC_STATUS.xlsx \\
      --output output/hvdc_status_v35.ttl

  # 스키마 포함 변환
  python scripts/core/excel_to_ttl.py \\
      --input data/HVDC_STATUS.xlsx \\
      --output output/hvdc_status_v35.ttl \\
      --schema logiontology/configs/ontology/hvdc_event_schema.ttl

  # 커스텀 컬럼 지정
  python scripts/core/excel_to_ttl.py \\
      --input data.xlsx \\
      --output result.ttl \\
      --warehouses "WH1,WH2,MOSB" \\
      --sites "SHU,MIR"
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input Excel file path'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output TTL file path'
    )
    parser.add_argument(
        '--schema', '-s',
        help='Ontology schema TTL file path (optional)'
    )
    parser.add_argument(
        '--warehouses',
        help='Comma-separated warehouse column names (default: HVDC standard)'
    )
    parser.add_argument(
        '--sites',
        help='Comma-separated site column names (default: SHU,MIR,DAS,AGI)'
    )
    parser.add_argument(
        '--flow-version',
        default='3.5',
        choices=['3.4', '3.5'],
        help='Flow Code version (default: 3.5)'
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
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # 창고/사이트 컬럼 파싱
    warehouse_cols = DEFAULT_WAREHOUSE_KEYS
    if args.warehouses:
        warehouse_cols = [w.strip() for w in args.warehouses.split(',')]

    site_cols = DEFAULT_SITE_KEYS
    if args.sites:
        site_cols = [s.strip() for s in args.sites.split(',')]

    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Flow Code version: {args.flow_version}")

    # 변환 실행
    try:
        stats = convert_excel_to_ttl(
            str(input_path),
            args.output,
            warehouse_cols,
            site_cols,
            args.schema,
            args.flow_version
        )
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 결과 출력
    print("\n" + "="*60)
    print("Conversion Statistics")
    print("="*60)
    print(f"  Total rows:      {stats.get('total_rows', 0):5d}")
    print(f"  Cases created:   {stats.get('cases_created', 0):5d}")
    print(f"  Inbound events:  {stats.get('inbound_events', 0):5d}")
    print(f"  Outbound events: {stats.get('outbound_events', 0):5d}")
    print(f"  Skipped (no FLOW): {stats.get('skipped_no_flow', 0):5d}")
    print("="*60 + "\n")

    logger.info("Conversion complete!")


if __name__ == "__main__":
    main()

