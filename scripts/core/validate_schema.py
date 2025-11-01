#!/usr/bin/env python3
"""
TTL Schema Validator - CLI Script
TTL 파일을 SHACL 스키마로 검증

Usage:
    python scripts/core/validate_schema.py --ttl output/hvdc_status_v35.ttl
    python scripts/core/validate_schema.py --ttl output/hvdc_status_v35.ttl --schema logiontology/configs/ontology/hvdc_event_schema.ttl
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
import logging
import json

# 프로젝트 루트를 PYTHONPATH에 추가
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from rdflib import Graph, Namespace

# pyshacl은 선택적 의존성
try:
    from pyshacl import validate
    HAS_PYSHACL = True
except ImportError:
    HAS_PYSHACL = False

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 네임스페이스
HVDC = Namespace("http://samsung.com/project-logistics#")


def validate_ttl(ttl_path: str, schema_path: str = None) -> dict:
    """
    TTL 파일을 SHACL 스키마로 검증

    Args:
        ttl_path: TTL 파일 경로
        schema_path: SHACL 스키마 경로 (optional)

    Returns:
        dict: 검증 결과 {
            "conforms": bool,
            "violations": int,
            "validation_report": str
        }
    """
    logger.info(f"Loading TTL: {ttl_path}")

    # TTL 로드
    try:
        data_graph = Graph()
        data_graph.parse(ttl_path, format='turtle')
        logger.info(f"TTL loaded: {len(data_graph)} triples")
    except Exception as e:
        logger.error(f"Failed to load TTL: {e}")
        return {"conforms": False, "error": str(e)}

    # SHACL 스키마 로드 (optional)
    shacl_graph = None
    if schema_path:
        logger.info(f"Loading SHACL schema: {schema_path}")
        try:
            shacl_graph = Graph()
            shacl_graph.parse(schema_path, format='turtle')
            logger.info(f"SHACL schema loaded: {len(shacl_graph)} triples")
        except Exception as e:
            logger.warning(f"Failed to load SHACL schema: {e}")
            logger.warning("Continuing without SHACL validation...")

    # SHACL 검증
    if shacl_graph:
        if not HAS_PYSHACL:
            logger.warning("pyshacl not installed. Install with: pip install pyshacl")
            logger.warning("Falling back to basic validation...")
            return validate_basic(data_graph)

        logger.info("Running SHACL validation...")
        try:
            conforms, results_graph, results_text = validate(
                data_graph,
                shacl_graph=shacl_graph,
                inference='rdfs',
                abort_on_first=False
            )

            violations = len(list(results_graph.subjects()))

            return {
                "conforms": conforms,
                "violations": violations,
                "validation_report": results_text
            }
        except Exception as e:
            logger.error(f"SHACL validation failed: {e}")
            return {"conforms": False, "error": str(e)}
    else:
        # SHACL 없이 기본 검증
        logger.info("Running basic validation (no SHACL)...")
        result = validate_basic(data_graph)
        return result


def validate_basic(graph: Graph) -> dict:
    """
    기본 검증 (SHACL 없이)

    Args:
        graph: RDF Graph

    Returns:
        dict: 검증 결과
    """
    violations = []

    # 1. Case 개수 확인
    cases = list(graph.subjects(predicate=None, object=HVDC.Case))
    logger.info(f"Found {len(cases)} cases")

    if len(cases) == 0:
        violations.append("No hvdc:Case instances found")

    # 2. Flow Code 범위 확인 (0~5)
    flow_codes = []
    for case in cases:
        flow_code_obj = graph.value(subject=case, predicate=HVDC.hasFlowCode)
        if flow_code_obj:
            flow_code = str(flow_code_obj)
            if flow_code not in ['0', '1', '2', '3', '4', '5']:
                violations.append(f"Invalid FLOW_CODE: {flow_code} for {case}")
            flow_codes.append(flow_code)

    logger.info(f"Flow Code distribution: {dict((c, flow_codes.count(c)) for c in set(flow_codes))}")

    # 3. StockEvent 확인
    events = list(graph.subjects(predicate=None, object=HVDC.StockEvent))
    logger.info(f"Found {len(events)} stock events")

    # 4. 필수 속성 확인 (샘플링)
    missing_properties = []
    sample_size = min(10, len(cases))
    for case in list(cases)[:sample_size]:
        if not graph.value(subject=case, predicate=HVDC.hasFlowCode):
            missing_properties.append(f"{case} missing hasFlowCode")

    if missing_properties:
        violations.extend(missing_properties[:5])  # 최대 5개만 표시

    conforms = len(violations) == 0

    return {
        "conforms": conforms,
        "violations": len(violations),
        "validation_report": "\n".join(violations) if violations else "All checks passed",
        "stats": {
            "cases": len(cases),
            "events": len(events),
            "flow_code_distribution": dict((c, flow_codes.count(c)) for c in set(flow_codes))
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="TTL Schema Validator - Validate TTL files against SHACL schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 기본 검증 (SHACL 없이)
  python scripts/core/validate_schema.py --ttl output/hvdc_status_v35.ttl

  # SHACL 스키마 포함 검증
  python scripts/core/validate_schema.py \\
      --ttl output/hvdc_status_v35.ttl \\
      --schema logiontology/configs/ontology/hvdc_event_schema.ttl

  # JSON 출력
  python scripts/core/validate_schema.py \\
      --ttl output/hvdc_status_v35.ttl \\
      --output validation_result.json
        """
    )

    parser.add_argument(
        '--ttl', '-t',
        required=True,
        help='TTL file path to validate'
    )
    parser.add_argument(
        '--schema', '-s',
        help='SHACL schema file path (optional)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output JSON file path (optional)'
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
    ttl_path = Path(args.ttl)
    if not ttl_path.exists():
        logger.error(f"TTL file not found: {ttl_path}")
        sys.exit(1)

    schema_path = None
    if args.schema:
        schema_path = Path(args.schema)
        if not schema_path.exists():
            logger.warning(f"SHACL schema not found: {schema_path}")
            schema_path = None

    logger.info(f"Validating: {ttl_path}")

    # 검증 실행
    try:
        result = validate_ttl(str(ttl_path), str(schema_path) if schema_path else None)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 결과 출력
    print("\n" + "="*60)
    print("Validation Result")
    print("="*60)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    print(f"  Conforms:   {'PASS' if result['conforms'] else 'FAIL'}")
    print(f"  Violations: {result.get('violations', 0)}")

    if "stats" in result:
        print(f"\n  Cases:  {result['stats']['cases']}")
        print(f"  Events: {result['stats']['events']}")
        print(f"  Flow Code Distribution:")
        for code, count in sorted(result['stats']['flow_code_distribution'].items()):
            print(f"    Flow {code}: {count}")

    if result.get('validation_report'):
        print(f"\n  Validation Report:")
        print("  " + result['validation_report'].replace("\n", "\n  "))

    print("="*60 + "\n")

    # JSON 저장
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"Result saved: {output_path}")

    # Exit code
    sys.exit(0 if result['conforms'] else 1)


if __name__ == "__main__":
    main()

