#!/usr/bin/env python3
"""
키워드-엔티티 연결 스크립트
WhatsApp 메시지에서 추출한 Shipment/Container/Delivery와 태그 사전의 키워드를 매칭하여 연결
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
from collections import defaultdict

# RDF 처리
from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal, URIRef
from rdflib.namespace import NamespaceManager

# Unicode 출력 지원
sys.stdout.reconfigure(encoding="utf-8")


def load_rdf_data(rdf_file: str) -> Graph:
    """RDF 파일 로드"""
    g = Graph()
    if Path(rdf_file).exists():
        g.parse(rdf_file, format="turtle")
        print(f"[INFO] RDF 파일 로드: {rdf_file}")
    else:
        print(f"[ERROR] RDF 파일을 찾을 수 없습니다: {rdf_file}")
        return None
    return g


def load_tag_dictionary(tags_file: str) -> Dict[str, Any]:
    """태그 사전 로드"""
    with open(tags_file, "r", encoding="utf-8") as f:
        tags_data = json.load(f)
    print(f"[INFO] 태그 사전 로드: {tags_file}")
    return tags_data


def setup_namespaces() -> Dict[str, Namespace]:
    """네임스페이스 설정"""
    return {
        "abu": Namespace("https://abu-dhabi.example.org/ns#"),
        "abui": Namespace("https://abu-dhabi.example.org/id/"),
        "xsd": XSD,
        "rdf": RDF,
        "rdfs": RDFS,
    }


def find_matching_keywords(message: str, tags_data: Dict[str, Any]) -> List[str]:
    """메시지에서 매칭되는 키워드 찾기"""
    matched_keywords = []

    for category, entities in tags_data["categories"].items():
        for key, data in entities.items():
            # 정규식으로 매칭 시도
            try:
                pattern = data["regex"]
                if re.search(pattern, message, re.IGNORECASE):
                    matched_keywords.append(
                        {
                            "category": category,
                            "key": key,
                            "synonyms": data["synonyms"],
                            "priority": data["priority"],
                        }
                    )
            except re.error:
                # 정규식 오류 시 동의어로 매칭 시도
                for synonym in data["synonyms"]:
                    if re.search(rf"\b{re.escape(synonym)}\b", message, re.IGNORECASE):
                        matched_keywords.append(
                            {
                                "category": category,
                                "key": key,
                                "synonyms": data["synonyms"],
                                "priority": data["priority"],
                            }
                        )
                        break

    return matched_keywords


def link_shipments_to_keywords(
    g: Graph, ns_dict: Dict[str, Namespace], tags_data: Dict[str, Any]
) -> int:
    """Shipment 엔티티를 키워드와 연결"""
    print("[INFO] Shipment-키워드 연결 중...")

    linked_count = 0

    for s, p, o in g.triples((None, RDF.type, ns_dict["abu"]["AbuDhabiShipment"])):
        # 메시지 내용 추출
        message_literals = []
        for _, _, message in g.triples((s, ns_dict["abu"]["messageContent"], None)):
            message_literals.append(str(message))

        # 메시지가 없으면 다른 속성들에서 키워드 추출
        if not message_literals:
            # 선박명, 위치, 상태 등에서 키워드 추출
            entity_text = ""
            for _, _, ship_name in g.triples((s, ns_dict["abu"]["shipName"], None)):
                entity_text += f" {str(ship_name)}"
            for _, _, location in g.triples(
                (s, ns_dict["abu"]["currentLocation"], None)
            ):
                entity_text += f" {str(location)}"
            for _, _, status in g.triples((s, ns_dict["abu"]["shipStatus"], None)):
                entity_text += f" {str(status)}"
            message_literals = [entity_text]

        # 각 메시지에서 키워드 매칭
        all_matched_keywords = []
        for message in message_literals:
            matched = find_matching_keywords(message, tags_data)
            all_matched_keywords.extend(matched)

        # 중복 제거 (key 기준)
        unique_keywords = {}
        for kw in all_matched_keywords:
            key = kw["key"]
            if (
                key not in unique_keywords
                or kw["priority"] > unique_keywords[key]["priority"]
            ):
                unique_keywords[key] = kw

        # 매칭된 키워드를 RDF에 추가
        for kw in unique_keywords.values():
            # 키워드 엔티티 URI 생성
            keyword_uri = URIRef(f"{ns_dict['abui']}{kw['category']}Entity/{kw['key']}")

            # Shipment와 키워드 연결
            g.add((s, ns_dict["abu"]["relatedKeyword"], keyword_uri))
            linked_count += 1

    return linked_count


def link_containers_to_keywords(
    g: Graph, ns_dict: Dict[str, Namespace], tags_data: Dict[str, Any]
) -> int:
    """Container 엔티티를 키워드와 연결"""
    print("[INFO] Container-키워드 연결 중...")

    linked_count = 0

    for s, p, o in g.triples((None, RDF.type, ns_dict["abu"]["AbuDhabiContainer"])):
        # 컨테이너 ID와 타입에서 키워드 추출
        entity_text = ""
        for _, _, container_id in g.triples((s, ns_dict["abu"]["containerId"], None)):
            entity_text += f" {str(container_id)}"
        for _, _, container_type in g.triples(
            (s, ns_dict["abu"]["containerType"], None)
        ):
            entity_text += f" {str(container_type)}"

        # 메시지 내용도 확인
        for _, _, message in g.triples((s, ns_dict["abu"]["messageContent"], None)):
            entity_text += f" {str(message)}"

        # 키워드 매칭
        matched_keywords = find_matching_keywords(entity_text, tags_data)

        # 중복 제거
        unique_keywords = {}
        for kw in matched_keywords:
            key = kw["key"]
            if (
                key not in unique_keywords
                or kw["priority"] > unique_keywords[key]["priority"]
            ):
                unique_keywords[key] = kw

        # 매칭된 키워드를 RDF에 추가
        for kw in unique_keywords.values():
            keyword_uri = URIRef(f"{ns_dict['abui']}{kw['category']}Entity/{kw['key']}")
            g.add((s, ns_dict["abu"]["relatedKeyword"], keyword_uri))
            linked_count += 1

    return linked_count


def link_deliveries_to_keywords(
    g: Graph, ns_dict: Dict[str, Namespace], tags_data: Dict[str, Any]
) -> int:
    """Delivery 엔티티를 키워드와 연결"""
    print("[INFO] Delivery-키워드 연결 중...")

    linked_count = 0

    for s, p, o in g.triples((None, RDF.type, ns_dict["abu"]["AbuDhabiDelivery"])):
        # 배송 정보에서 키워드 추출
        entity_text = ""
        for _, _, company in g.triples((s, ns_dict["abu"]["deliveryCompany"], None)):
            entity_text += f" {str(company)}"
        for _, _, unit in g.triples((s, ns_dict["abu"]["deliveryUnit"], None)):
            entity_text += f" {str(unit)}"
        for _, _, date_info in g.triples((s, ns_dict["abu"]["deliveryDateInfo"], None)):
            entity_text += f" {str(date_info)}"

        # 메시지 내용도 확인
        for _, _, message in g.triples((s, ns_dict["abu"]["messageContent"], None)):
            entity_text += f" {str(message)}"

        # 키워드 매칭
        matched_keywords = find_matching_keywords(entity_text, tags_data)

        # 중복 제거
        unique_keywords = {}
        for kw in matched_keywords:
            key = kw["key"]
            if (
                key not in unique_keywords
                or kw["priority"] > unique_keywords[key]["priority"]
            ):
                unique_keywords[key] = kw

        # 매칭된 키워드를 RDF에 추가
        for kw in unique_keywords.values():
            keyword_uri = URIRef(f"{ns_dict['abui']}{kw['category']}Entity/{kw['key']}")
            g.add((s, ns_dict["abu"]["relatedKeyword"], keyword_uri))
            linked_count += 1

    return linked_count


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
    print("키워드-엔티티 연결 스크립트")
    print("=" * 60)

    # 파일 경로 설정
    rdf_file = "output/abu_logistics_data.ttl"
    tags_file = "ABU/abu_dhabi_logistics_tag_dict_v1.json"
    output_file = "output/abu_logistics_data.ttl"

    # 1. RDF 데이터 로드
    print("\n1. RDF 데이터 로드")
    g = load_rdf_data(rdf_file)
    if g is None:
        return

    # 2. 태그 사전 로드
    print("\n2. 태그 사전 로드")
    tags_data = load_tag_dictionary(tags_file)

    # 3. 네임스페이스 설정
    ns_dict = setup_namespaces()

    # 4. 엔티티-키워드 연결
    print("\n3. 엔티티-키워드 연결")
    shipment_links = link_shipments_to_keywords(g, ns_dict, tags_data)
    container_links = link_containers_to_keywords(g, ns_dict, tags_data)
    delivery_links = link_deliveries_to_keywords(g, ns_dict, tags_data)

    # 5. RDF 파일 저장
    print("\n4. RDF 파일 저장")
    save_rdf_graph(g, output_file)

    # 6. 결과 요약
    print("\n[SUCCESS] 키워드-엔티티 연결 완료")
    print(f"  - Shipment 연결: {shipment_links}개")
    print(f"  - Container 연결: {container_links}개")
    print(f"  - Delivery 연결: {delivery_links}개")
    print(f"  - 총 연결 수: {shipment_links + container_links + delivery_links}개")
    print(f"  - 총 트리플 수: {len(g)}개")
    print(f"  - 출력 파일: {output_file}")

    return {
        "shipment_links": shipment_links,
        "container_links": container_links,
        "delivery_links": delivery_links,
        "total_links": shipment_links + container_links + delivery_links,
        "total_triples": len(g),
    }


if __name__ == "__main__":
    main()
