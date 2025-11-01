#!/usr/bin/env python3
"""
Neo4j Loader - CLI Script
TTL 파일을 Neo4j 그래프 데이터베이스에 로드

Usage:
    python scripts/core/neo4j_loader.py --ttl data.ttl --uri bolt://localhost:7687 --user neo4j --password password
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
import logging
import os

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


def load_ttl_to_neo4j(ttl_path: str, uri: str, user: str, password: str, database: str = "neo4j") -> dict:
    """
    TTL 파일을 Neo4j에 로드

    Args:
        ttl_path: TTL 파일 경로
        uri: Neo4j URI (e.g., bolt://localhost:7687)
        user: Neo4j 사용자
        password: Neo4j 비밀번호
        database: 데이터베이스 이름 (기본값: neo4j)

    Returns:
        dict: 로드 통계
    """
    logger.info(f"Loading TTL: {ttl_path}")

    # TTL 로드
    try:
        g = Graph()
        g.parse(ttl_path, format='turtle')
        logger.info(f"TTL loaded: {len(g)} triples")
    except Exception as e:
        logger.error(f"Failed to load TTL: {e}")
        return {"error": str(e)}

    # Neo4j 연결
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"Connected to Neo4j: {uri}")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        return {"error": str(e)}

    # Case 노드 생성
    logger.info("Creating Case nodes in Neo4j...")

    query = """
    PREFIX hvdc: <http://samsung.com/project-logistics#>

    SELECT ?case ?hvdcCode ?flowCode ?vendor ?grossWeight
    WHERE {
        ?case a hvdc:Case .
        OPTIONAL { ?case hvdc:hasHvdcCode ?hvdcCode }
        OPTIONAL { ?case hvdc:hasFlowCode ?flowCode }
        OPTIONAL { ?case hvdc:hasVendor ?vendor }
        OPTIONAL { ?case hvdc:hasGrossWeight ?grossWeight }
    }
    """

    results = g.query(query)

    stats = {"cases_created": 0, "events_created": 0}

    with driver.session(database=database) as session:
        # 기존 데이터 삭제 (optional)
        # session.run("MATCH (n) DETACH DELETE n")

        # Case 노드 생성
        for row in results:
            case_id = str(row.case).split("/")[-1]

            cypher = """
            MERGE (c:Case {id: $case_id})
            SET c.hvdc_code = $hvdc_code,
                c.flow_code = $flow_code,
                c.vendor = $vendor,
                c.gross_weight = $gross_weight
            """

            session.run(cypher, {
                "case_id": case_id,
                "hvdc_code": str(row.hvdcCode) if row.hvdcCode else None,
                "flow_code": str(row.flowCode) if row.flowCode else None,
                "vendor": str(row.vendor) if row.vendor else None,
                "gross_weight": float(row.grossWeight) if row.grossWeight else None
            })

            stats["cases_created"] += 1

            if stats["cases_created"] % 100 == 0:
                logger.info(f"  Progress: {stats['cases_created']} cases")

    driver.close()
    logger.info(f"Neo4j load complete: {stats['cases_created']} cases")

    return stats


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Neo4j Loader - Load TTL files into Neo4j graph database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 기본 로드 (로컬 Neo4j)
  python scripts/core/neo4j_loader.py \\
      --ttl output/hvdc_status_v35.ttl \\
      --uri bolt://localhost:7687 \\
      --user neo4j \\
      --password password

  # 환경변수 사용
  export NEO4J_URI=bolt://localhost:7687
  export NEO4J_USER=neo4j
  export NEO4J_PASSWORD=password
  python scripts/core/neo4j_loader.py --ttl output/hvdc_status_v35.ttl

  # 커스텀 데이터베이스
  python scripts/core/neo4j_loader.py \\
      --ttl output/hvdc_status_v35.ttl \\
      --uri bolt://localhost:7687 \\
      --user neo4j \\
      --password password \\
      --database hvdc
        """
    )

    parser.add_argument(
        '--ttl', '-t',
        required=True,
        help='TTL file path to load'
    )
    parser.add_argument(
        '--uri',
        default=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        help='Neo4j URI (default: bolt://localhost:7687 or $NEO4J_URI)'
    )
    parser.add_argument(
        '--user',
        default=os.getenv('NEO4J_USER', 'neo4j'),
        help='Neo4j username (default: neo4j or $NEO4J_USER)'
    )
    parser.add_argument(
        '--password',
        default=os.getenv('NEO4J_PASSWORD'),
        help='Neo4j password (required, or set $NEO4J_PASSWORD)'
    )
    parser.add_argument(
        '--database',
        default='neo4j',
        help='Neo4j database name (default: neo4j)'
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

    # 비밀번호 확인
    if not args.password:
        logger.error("Neo4j password required (--password or $NEO4J_PASSWORD)")
        sys.exit(1)

    logger.info(f"TTL: {ttl_path}")
    logger.info(f"Neo4j URI: {args.uri}")
    logger.info(f"Database: {args.database}")

    # 로드 실행
    try:
        stats = load_ttl_to_neo4j(
            str(ttl_path),
            args.uri,
            args.user,
            args.password,
            args.database
        )
    except Exception as e:
        logger.error(f"Load failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 결과 출력
    if "error" in stats:
        logger.error(f"Load failed: {stats['error']}")
        sys.exit(1)

    print("\n" + "="*60)
    print("Neo4j Load Complete")
    print("="*60)
    print(f"  Cases created: {stats['cases_created']}")
    print("="*60 + "\n")

    logger.info("Neo4j load complete!")


if __name__ == "__main__":
    main()

