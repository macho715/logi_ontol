#!/usr/bin/env python3
"""
Flow Code v3.5 Calculator - CLI Script
이벤트 기반 관측값으로 Flow Code 0~5 계산 + AGI/DAS 도메인 룰 적용

Usage:
    python scripts/core/flow_code_calc.py --input data.xlsx --output result.csv
    python scripts/core/flow_code_calc.py --input data.xlsx --output result.json --format json
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
from typing import List, Optional
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Core Functions (from logiontology/src/ingest/flow_code_calculator.py)
# ============================================================================

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    컬럼명 정규화: 개행 문자 제거, 공백 정리

    'DSV\n Indoor' → 'DSV Indoor'
    """
    df = df.copy()
    # 개행 문자 제거 → 공백 정규화 (연속 공백을 1개로)
    df.columns = df.columns.str.replace('\n', ' ')
    df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
    return df


def extract_final_location(row: pd.Series, site_cols: List[str]) -> Optional[str]:
    """
    Site 컬럼에서 최종 위치 추출

    Logic:
        1. Site 컬럼들 중 날짜가 있는 것 필터링
        2. 가장 최근 날짜를 가진 컬럼명 반환
        3. 날짜가 없으면 None

    Example:
        SHU=2024-01-10, MIR=NaN, DAS=2024-01-15, AGI=NaN
        → Final_Location = "DAS"
    """
    dates_dict = {}
    for col in site_cols:
        val = row.get(col)
        if pd.notna(val):
            try:
                date_val = pd.to_datetime(val, errors='coerce')
                if pd.notna(date_val):
                    dates_dict[col] = date_val
            except:
                pass

    if dates_dict:
        # 최근 날짜 기준 정렬
        latest_site = max(dates_dict, key=dates_dict.get)
        return latest_site
    return None


def is_pre_arrival(row: pd.Series, all_date_cols: List[str], has_ata_col: bool = False) -> bool:
    """
    Pre Arrival 판별

    Conditions:
        1. ATA (실제 도착일) 컬럼이 NaN
        2. 또는 모든 창고/사이트 컬럼이 NaN
    """
    # Option 1: ATA 컬럼 확인
    if has_ata_col:
        ata = row.get('ATA')
        if pd.isna(ata):
            return True
        # ATA가 있고 날짜 컬럼이 있으면 Pre Arrival 아님
        if all_date_cols:
            has_any_date = any(pd.notna(row.get(col)) for col in all_date_cols)
            if has_any_date:
                return False

    # Option 2: 모든 날짜 컬럼 확인
    if all_date_cols:
        has_any_date = any(pd.notna(row.get(col)) for col in all_date_cols)
        return not has_any_date

    # 기본값: False
    return False


def calculate_flow_code_v35(
    df: pd.DataFrame,
    warehouse_columns: List[str],
    site_columns: List[str]
) -> pd.DataFrame:
    """
    Flow Code v3.5 계산

    Args:
        df: 입력 DataFrame
        warehouse_columns: 창고 컬럼 리스트 (MOSB 포함)
        site_columns: 사이트 컬럼 리스트

    Returns:
        DataFrame with added columns:
        - FLOW_CODE (0~5)
        - FLOW_DESCRIPTION
        - FLOW_CODE_ORIG (오버라이드 전 원본)
        - FLOW_OVERRIDE_REASON (오버라이드 사유)
        - Final_Location (자동 추출)
        - is_pre_arrival (Pre Arrival 여부)

    Algorithm:
        1. 필드 검증 및 전처리
        2. 관측값 계산 (is_pre_arrival, wh_cnt, has_mosb, has_site)
        3. 기본 Flow Code 계산 (0~4)
        4. AGI/DAS 도메인 오버라이드
        5. 혼합 케이스 처리 (Flow 5)
        6. 최종 반영 및 검증
    """
    df = df.copy()

    # Step 1: 컬럼명 정규화
    df = normalize_column_names(df)

    # 실제 컬럼 찾기 (정규화 후 - 대소문자 구분 없이)
    df_columns_lower = {col.lower(): col for col in df.columns}

    WH_COLS = []
    MOSB_COLS = []
    for wh_key in warehouse_columns:
        wh_key_lower = wh_key.lower().strip()
        # 정확한 매칭 우선, 없으면 부분 매칭
        if wh_key_lower in df_columns_lower:
            col_orig = df_columns_lower[wh_key_lower]
        else:
            # 부분 매칭 시도
            col_orig = None
            for col_lower, col in df_columns_lower.items():
                if wh_key_lower in col_lower:
                    col_orig = col
                    break

        if col_orig:
            if wh_key_lower == 'mosb':
                MOSB_COLS.append(col_orig)
            else:
                WH_COLS.append(col_orig)

    SITE_COLS = []
    for site_key in site_columns:
        site_key_lower = site_key.lower().strip()
        # 정확한 매칭만
        if site_key_lower in df_columns_lower:
            SITE_COLS.append(df_columns_lower[site_key_lower])

    logger.info(f"Found columns: WH={len(WH_COLS)}, MOSB={len(MOSB_COLS)}, SITE={len(SITE_COLS)}")

    # Step 2: Final_Location 추출 (새 컬럼 생성 - 기존 값이 없을 때만)
    if 'Final_Location' not in df.columns:
        df['Final_Location'] = df.apply(
            lambda row: extract_final_location(row, SITE_COLS),
            axis=1
        )
    else:
        logger.info("Final_Location 컬럼이 이미 존재 - 자동 추출 건너뜀")

    # Step 3: Pre Arrival 판별
    all_date_cols = WH_COLS + MOSB_COLS + SITE_COLS
    has_ata_col = 'ATA' in df.columns
    df['is_pre_arrival'] = df.apply(
        lambda row: is_pre_arrival(row, all_date_cols, has_ata_col),
        axis=1
    )

    # Step 4: 관측값 계산
    # 4.1 데이터 정규화 (0, "" → NaN)
    for col in WH_COLS + MOSB_COLS:
        if col in df.columns:
            df[col] = df[col].replace({0: np.nan, "": np.nan})

    # 4.2 창고 개수 계산
    wh_cnt = df[WH_COLS].notna().sum(axis=1) if WH_COLS else pd.Series(0, index=df.index)

    # 4.3 MOSB 존재 여부
    has_mosb = df[MOSB_COLS].notna().any(axis=1) if MOSB_COLS else pd.Series(False, index=df.index)

    # 4.4 Site 존재 여부
    has_site = df[SITE_COLS].notna().any(axis=1) if SITE_COLS else pd.Series(True, index=df.index)

    # Step 5: 기본 Flow Code 계산 (0~4)
    flow = pd.Series(0, index=df.index, dtype="int64")
    flow_desc = pd.Series("", index=df.index, dtype="object")

    # Flow 0: Pre Arrival
    flow[df['is_pre_arrival']] = 0
    flow_desc[df['is_pre_arrival']] = "Flow 0: Pre Arrival"

    # 나머지 Flow 계산 (Pre Arrival 아님)
    not_pre = ~df['is_pre_arrival']

    # Flow 1: Port → Site (WH=0, MOSB=0)
    mask_1 = not_pre & (wh_cnt == 0) & (~has_mosb)
    flow[mask_1] = 1
    flow_desc[mask_1] = "Flow 1: Port → Site"

    # Flow 2: Port → WH → Site (WH≥1, MOSB=0)
    mask_2 = not_pre & (wh_cnt >= 1) & (~has_mosb)
    flow[mask_2] = 2
    flow_desc[mask_2] = "Flow 2: Port → WH → Site"

    # Flow 3: Port → MOSB → Site (WH=0, MOSB=1)
    mask_3 = not_pre & (wh_cnt == 0) & has_mosb
    flow[mask_3] = 3
    flow_desc[mask_3] = "Flow 3: Port → MOSB → Site"

    # Flow 4: Port → WH → MOSB → Site (WH≥1, MOSB=1)
    mask_4 = not_pre & (wh_cnt >= 1) & has_mosb
    flow[mask_4] = 4
    flow_desc[mask_4] = "Flow 4: Port → WH → MOSB → Site"

    # Step 6: AGI/DAS 도메인 오버라이드
    df["FLOW_CODE_ORIG"] = flow.copy()
    df["FLOW_OVERRIDE_REASON"] = np.nan

    # Final_Location 컬럼 찾기 (이미 Step 2에서 생성했거나 입력 데이터에 존재)
    final_col = 'Final_Location'

    if final_col in df.columns:
        final_location = df[final_col].astype(str).str.upper()
        is_agi_das = final_location.isin(["AGI", "DAS"])

        # AGI/DAS가 0/1/2인 경우 강제 3 승급
        need_force = is_agi_das & flow.isin([0, 1, 2])
        flow[need_force] = 3
        flow_desc[need_force] = "Flow 3: Port → MOSB → Site (AGI/DAS forced)"
        df["FLOW_OVERRIDE_REASON"] = df["FLOW_OVERRIDE_REASON"].astype(object)
        df.loc[need_force, "FLOW_OVERRIDE_REASON"] = "AGI/DAS requires MOSB leg"

        if need_force.sum() > 0:
            logger.info(f" AGI/DAS 강제 승급: {need_force.sum()}건 (0/1/2 → 3)")
    else:
        logger.warning("Final_Location 컬럼을 찾을 수 없음 - AGI/DAS 강제 승급 불가")

    # Step 7: 혼합 케이스 처리 (Flow 5)
    # 조건 1: MOSB 있으나 Site 없음
    cond_mosb_no_site = has_mosb & (~has_site)

    # 조건 2: WH 2개 이상 + MOSB 없음
    cond_weird_wh = (wh_cnt >= 2) & (~has_mosb) & (~df['is_pre_arrival'])

    need_5 = cond_mosb_no_site | cond_weird_wh
    flow[need_5] = 5
    flow_desc[need_5] = "Flow 5: Mixed / Waiting / Incomplete leg"

    # Step 8: 최종 반영
    df["FLOW_CODE"] = flow.astype("int64")
    df["FLOW_DESCRIPTION"] = flow_desc

    # 검증 및 로깅
    dist = df["FLOW_CODE"].value_counts().sort_index()
    logger.info(f"[FlowCode v3.5] 분포: {dict(dist)}")
    logger.info(f" Pre Arrival: {df['is_pre_arrival'].sum()}건")
    logger.info(" Flow Code 재계산 완료 (v3.5: 0~5 확장)")

    # 범위 검증
    invalid_codes = df[~df["FLOW_CODE"].isin([0, 1, 2, 3, 4, 5])]
    if len(invalid_codes) > 0:
        logger.error(f"⚠️ 잘못된 Flow Code 발견: {invalid_codes['FLOW_CODE'].unique()}")

    return df


# ============================================================================
# CLI Interface
# ============================================================================

# 기본 창고/사이트 컬럼 (HVDC 프로젝트 표준)
DEFAULT_WAREHOUSE_COLS = [
    "DSV Indoor", "DSV Outdoor", "DSV MZD", "DSV MZP", "DSV Al Markaz",
    "JDN MZD", "JDN Waterfront",
    "MOSB",
    "AAA Storage", "Hauler DG Storage", "DHL WH", "Hauler Indoor",
    "Shifting", "ZENER (WH)", "Vijay Tanks"
]

DEFAULT_SITE_COLS = ["SHU", "MIR", "DAS", "AGI"]


def main():
    parser = argparse.ArgumentParser(
        description="Flow Code v3.5 Calculator - Calculate logistics flow codes from Excel data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CSV 출력 (기본)
  python scripts/core/flow_code_calc.py --input data/HVDC_STATUS.xlsx --output output/flow_codes.csv

  # JSON 출력
  python scripts/core/flow_code_calc.py --input data/HVDC_STATUS.xlsx --output output/flow_codes.json --format json

  # 커스텀 창고 컬럼 지정
  python scripts/core/flow_code_calc.py --input data.xlsx --output result.csv --warehouses "WH1,WH2,MOSB"

  # 통계만 출력 (파일 저장 안 함)
  python scripts/core/flow_code_calc.py --input data.xlsx --stats-only
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input Excel file path (e.g., data/HVDC_STATUS.xlsx)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (CSV or JSON)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['csv', 'json'],
        default='csv',
        help='Output format (default: csv)'
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
        '--sheet',
        default=0,
        help='Excel sheet name or index (default: 0 = first sheet)'
    )
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Print statistics only, do not save file'
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
        logger.error(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    # 창고/사이트 컬럼 파싱
    warehouse_cols = DEFAULT_WAREHOUSE_COLS
    if args.warehouses:
        warehouse_cols = [w.strip() for w in args.warehouses.split(',')]

    site_cols = DEFAULT_SITE_COLS
    if args.sites:
        site_cols = [s.strip() for s in args.sites.split(',')]

    logger.info(f"📂 Loading: {input_path}")
    logger.info(f"   Warehouse columns: {len(warehouse_cols)} configured")
    logger.info(f"   Site columns: {site_cols}")

    # Excel 로드
    try:
        if isinstance(args.sheet, int) or args.sheet.isdigit():
            sheet = int(args.sheet)
        else:
            sheet = args.sheet
        df = pd.read_excel(input_path, sheet_name=sheet)
        logger.info(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        logger.error(f"❌ Failed to load Excel: {e}")
        sys.exit(1)

    # Flow Code 계산
    try:
        logger.info("🔄 Calculating Flow Code v3.5...")
        df_result = calculate_flow_code_v35(df, warehouse_cols, site_cols)
        logger.info("✅ Calculation complete")
    except Exception as e:
        logger.error(f"❌ Flow Code calculation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 통계 출력
    print("\n" + "="*60)
    print("📊 Flow Code v3.5 Distribution")
    print("="*60)
    dist = df_result['FLOW_CODE'].value_counts().sort_index()
    for code, count in dist.items():
        pct = count / len(df_result) * 100
        desc = df_result[df_result['FLOW_CODE'] == code]['FLOW_DESCRIPTION'].iloc[0]
        print(f"  Flow {code}: {count:5d} cases ({pct:5.1f}%)  {desc}")

    print(f"\n  Pre Arrival: {df_result['is_pre_arrival'].sum()} cases")

    override_count = df_result['FLOW_OVERRIDE_REASON'].notna().sum()
    if override_count > 0:
        print(f"  Overrides:   {override_count} cases (AGI/DAS forced)")

    print("="*60 + "\n")

    # 파일 저장
    if not args.stats_only:
        if not args.output:
            logger.error("❌ --output required (or use --stats-only)")
            sys.exit(1)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if args.format == 'json':
                # JSON 출력 (레코드 형식)
                result_json = df_result.to_dict(orient='records')
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result_json, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"✅ Saved to: {output_path} (JSON format)")
            else:
                # CSV 출력
                df_result.to_csv(output_path, index=False, encoding='utf-8-sig')
                logger.info(f"✅ Saved to: {output_path} (CSV format)")
        except Exception as e:
            logger.error(f"❌ Failed to save output: {e}")
            sys.exit(1)

    logger.info("🎉 Flow Code calculation complete!")


if __name__ == "__main__":
    main()

