#!/usr/bin/env python3
"""
DATA WH.xlsx → TTL + JSON Converter
Excel 파일을 HVDC 온톨로지 기반 TTL로 변환하고, GPT용 JSON으로도 평탄화
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from logiontology.src.ingest.excel_to_ttl_with_events import convert_data_wh_to_ttl_with_events
except ImportError:
    print("❌ 모듈 임포트 실패. logiontology 설치 확인 필요")
    sys.exit(1)


def main():
    # Windows console encoding fix
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="DATA WH.xlsx -> TTL + JSON Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 전체 파이프라인 실행 (Excel → TTL → JSON)
  python scripts/convert_data_wh_to_ttl.py \\
      --input "DATA WH.xlsx" \\
      --output-ttl "rdf_output/data_wh_events.ttl" \\
      --schema "logiontology/configs/ontology/hvdc_event_schema.ttl"

  # TTL만 생성 (JSON 건너뛰기)
  python scripts/convert_data_wh_to_ttl.py \\
      --input "DATA WH.xlsx" \\
      --skip-json
        """
    )

    parser.add_argument("--input", "-i", required=True,
                        help="Excel 파일 경로")
    parser.add_argument("--output-ttl", "-o",
                        default="rdf_output/data_wh_events.ttl",
                        help="출력 TTL 파일 경로")
    parser.add_argument("--schema", "-s",
                        help="온톨로지 스키마 TTL 경로 (선택)")
    parser.add_argument("--report", "-r",
                        help="변환 통계 JSON 리포트 경로 (선택)")
    parser.add_argument("--skip-json", action="store_true",
                        help="JSON 변환 건너뛰기 (아직 구현 안 됨)")

    args = parser.parse_args()

    print("=" * 80)
    print("DATA WH.xlsx -> TTL Converter (Event-Based)")
    print("=" * 80)

    # 입력 파일 존재 확인
    if not Path(args.input).exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    # 1) Excel -> TTL (Event injection)
    print("\n" + "=" * 80)
    print("Step 1: Excel -> TTL Conversion (Event Injection)")
    print("=" * 80)

    try:
        ttl_stats = convert_data_wh_to_ttl_with_events(
            excel_path=args.input,
            output_path=args.output_ttl,
            schema_path=args.schema
        )

        print(f"\nSUCCESS: TTL created")
        print(f"   - Cases: {ttl_stats.get('cases_created', 0)}")
        print(f"   - Inbound Events: {ttl_stats.get('inbound_events', 0)}")
        print(f"   - Outbound Events: {ttl_stats.get('outbound_events', 0)}")
        print(f"   - Output: {args.output_ttl}")

    except Exception as e:
        print(f"\nERROR: TTL conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 2) JSON conversion (TODO)
    if not args.skip_json:
        print("\n" + "=" * 80)
        print("Step 2: TTL -> JSON Flattening (TODO)")
        print("=" * 80)
        print("   JSON conversion not yet implemented.")
        print("   Next TODO: ttl_to_json_flat.py")

    # 3) Save report
    if args.report:
        report_data = {
            "source_file": args.input,
            "output_ttl": args.output_ttl,
            "conversion_date": datetime.now().isoformat(),
            "statistics": ttl_stats
        }

        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved: {args.report}")

    # 4) Final summary
    print("\n" + "=" * 80)
    print("Conversion Summary")
    print("=" * 80)
    print(f"TTL (Original): {args.output_ttl}")
    print(f"Statistics:")
    print(f"   - Total rows: {ttl_stats.get('total_rows', 0)}")
    print(f"   - Cases created: {ttl_stats.get('cases_created', 0)}")
    print(f"   - Inbound events: {ttl_stats.get('inbound_events', 0)}")
    print(f"   - Outbound events: {ttl_stats.get('outbound_events', 0)}")
    print(f"   - No FLOW_CODE: {ttl_stats.get('skipped_no_flow', 0)}")

    print("\nNext steps:")
    print(f"   1. Check TTL file: {args.output_ttl}")
    print("   2. Validate with SPARQL queries")
    print("   3. Convert to JSON for GPT (TODO)")


if __name__ == "__main__":
    main()

