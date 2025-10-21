#!/usr/bin/env python3
"""
ABU 태그 사전 RDF 변환 스크립트
abu_dhabi_logistics_tag_dict_v1.json을 RDF로 변환하여 기존 abu_logistics_data.ttl에 통합
"""

import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re

# RDF 처리
from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal, URIRef
from rdflib.namespace import NamespaceManager

# Unicode 출력 지원
sys.stdout.reconfigure(encoding="utf-8")


def load_existing_rdf(rdf_file: str) -> Graph:
    """기존 RDF 파일 로드"""
    g = Graph()
    if Path(rdf_file).exists():
        g.parse(rdf_file, format="turtle")
        print(f"[INFO] 기존 RDF 파일 로드: {rdf_file}")
    else:
        print(f"[INFO] 새 RDF 그래프 생성")
    return g


def setup_namespaces() -> Dict[str, Namespace]:
    """네임스페이스 설정"""
    return {
        "abu": Namespace("https://abu-dhabi.example.org/ns#"),
        "abui": Namespace("https://abu-dhabi.example.org/id/"),
        "xsd": XSD,
        "rdf": RDF,
        "rdfs": RDFS,
    }


def create_entity_uri(category: str, key: str, ns_dict: Dict[str, Namespace]) -> URIRef:
    """엔티티 URI 생성"""
    safe_key = re.sub(r"[^\w\-]", "_", key)
    uri_id = f"{category}Entity/{safe_key}"
    return URIRef(f"{ns_dict['abui']}{uri_id}")


def convert_tags_to_rdf(
    tags_data: Dict[str, Any], g: Graph, ns_dict: Dict[str, Namespace]
) -> List[URIRef]:
    """태그 사전을 RDF로 변환"""
    print("[INFO] 태그 사전 RDF 변환 중...")

    created_uris = []
    category_mapping = {
        "VESSEL": "VesselEntity",
        "LOCATION": "LocationEntity",
        "DOC_APPROVAL": "DocumentType",
        "EQUIPMENT_OPERATION": "EquipmentType",
        "RISK_QUALITY": "RiskFactor",
        "STATUS_ACTION": "StatusType",
    }

    for category, entities in tags_data["categories"].items():
        print(f"[INFO] {category} 카테고리 처리 중... ({len(entities)}개 엔티티)")

        for key, data in entities.items():
            # 엔티티 URI 생성
            entity_uri = create_entity_uri(category, key, ns_dict)

            # 엔티티 타입 설정
            entity_type = category_mapping.get(category, "Entity")
            g.add((entity_uri, RDF.type, ns_dict["abu"][entity_type]))

            # 기본 속성들
            g.add((entity_uri, ns_dict["abu"]["entityKey"], Literal(key)))
            g.add((entity_uri, ns_dict["abu"]["category"], Literal(category)))
            g.add(
                (
                    entity_uri,
                    ns_dict["abu"]["priority"],
                    Literal(data["priority"], datatype=XSD.integer),
                )
            )

            # 동의어들
            for synonym in data["synonyms"]:
                g.add((entity_uri, ns_dict["abu"]["synonym"], Literal(synonym)))

            # 정규식 패턴
            g.add((entity_uri, ns_dict["abu"]["regexPattern"], Literal(data["regex"])))

            # 카테고리별 추가 속성
            if category == "VESSEL":
                g.add((entity_uri, ns_dict["abu"]["vesselKey"], Literal(key)))
            elif category == "LOCATION":
                g.add((entity_uri, ns_dict["abu"]["locationKey"], Literal(key)))
            elif category == "DOC_APPROVAL":
                g.add((entity_uri, ns_dict["abu"]["documentKey"], Literal(key)))
            elif category == "EQUIPMENT_OPERATION":
                g.add((entity_uri, ns_dict["abu"]["equipmentKey"], Literal(key)))
            elif category == "RISK_QUALITY":
                g.add((entity_uri, ns_dict["abu"]["riskKey"], Literal(key)))
            elif category == "STATUS_ACTION":
                g.add((entity_uri, ns_dict["abu"]["statusKey"], Literal(key)))

            created_uris.append(entity_uri)

    return created_uris


def save_rdf_graph(g: Graph, output_file: str):
    """RDF 그래프를 파일로 저장"""
    # 네임스페이스 바인딩
    g.bind("abu", "https://abu-dhabi.example.org/ns#")
    g.bind("abui", "https://abu-dhabi.example.org/id/")
    g.bind("xsd", XSD)

    # TTL 형식으로 저장
    g.serialize(destination=output_file, format="turtle", encoding="utf-8")
    print(f"[SUCCESS] RDF 파일 저장: {output_file}")


def main():
    """메인 함수"""
    print("=" * 60)
    print("ABU 태그 사전 RDF 변환 스크립트")
    print("=" * 60)

    # 파일 경로 설정
    tags_file = "ABU/abu_dhabi_logistics_tag_dict_v1.json"
    existing_rdf = "output/abu_logistics_data.ttl"
    output_file = "output/abu_logistics_data.ttl"

    # 1. 태그 사전 로드
    print("\n1. 태그 사전 로드")
    if not Path(tags_file).exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {tags_file}")
        return

    with open(tags_file, "r", encoding="utf-8") as f:
        tags_data = json.load(f)

    print(f"[SUCCESS] 태그 사전 로드 완료")
    print(f"  - 버전: {tags_data['version']}")
    print(f"  - 소스: {tags_data['source']}")
    print(f"  - 생성일: {tags_data['generated_at']}")

    # 2. 기존 RDF 로드
    print("\n2. 기존 RDF 로드")
    g = load_existing_rdf(existing_rdf)
    ns_dict = setup_namespaces()

    # 3. 태그 사전 RDF 변환
    print("\n3. 태그 사전 RDF 변환")
    created_uris = convert_tags_to_rdf(tags_data, g, ns_dict)

    # 4. RDF 파일 저장
    print("\n4. RDF 파일 저장")
    Path("output").mkdir(exist_ok=True)
    save_rdf_graph(g, output_file)

    # 5. 결과 요약
    print("\n[SUCCESS] 태그 사전 RDF 변환 완료")
    print(f"  - 생성된 엔티티: {len(created_uris)}개")
    print(f"  - 총 트리플 수: {len(g)}개")
    print(f"  - 출력 파일: {output_file}")

    # 카테고리별 통계
    category_stats = {}
    for uri in created_uris:
        # URI에서 카테고리 추출
        uri_str = str(uri)
        if "VesselEntity" in uri_str:
            category_stats["VESSEL"] = category_stats.get("VESSEL", 0) + 1
        elif "LocationEntity" in uri_str:
            category_stats["LOCATION"] = category_stats.get("LOCATION", 0) + 1
        elif "DocumentType" in uri_str:
            category_stats["DOC_APPROVAL"] = category_stats.get("DOC_APPROVAL", 0) + 1
        elif "EquipmentType" in uri_str:
            category_stats["EQUIPMENT_OPERATION"] = (
                category_stats.get("EQUIPMENT_OPERATION", 0) + 1
            )
        elif "RiskFactor" in uri_str:
            category_stats["RISK_QUALITY"] = category_stats.get("RISK_QUALITY", 0) + 1
        elif "StatusType" in uri_str:
            category_stats["STATUS_ACTION"] = category_stats.get("STATUS_ACTION", 0) + 1

    print("\n카테고리별 엔티티 수:")
    for category, count in category_stats.items():
        print(f"  - {category}: {count}개")

    return created_uris


if __name__ == "__main__":
    main()
