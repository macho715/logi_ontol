#!/usr/bin/env python3
"""
아부다비 물류 데이터 RDF 변환 스크립트
가이드라인과 WhatsApp 대화 데이터를 RDF로 변환합니다.
"""

import sys
import json
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import re

# RDF 처리
from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal, URIRef
from rdflib.namespace import NamespaceManager

# Unicode 출력 지원
sys.stdout.reconfigure(encoding="utf-8")


def convert_whatsapp_timestamp(timestamp_str: str) -> str:
    """Convert WhatsApp timestamp (YY/MM/DD HH:MM) to ISO format"""
    try:
        # Parse WhatsApp format: YY/MM/DD HH:MM
        dt = datetime.strptime(timestamp_str, "%y/%m/%d %H:%M")
        # Convert to ISO format
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        # If parsing fails, return the original string
        return timestamp_str


def setup_namespaces(rules: Dict[str, Any]) -> Dict[str, Namespace]:
    """네임스페이스 설정"""
    ns_dict = {}
    for prefix, uri in rules["namespaces"].items():
        ns_dict[prefix] = Namespace(uri)
    return ns_dict


def create_guideline_uri(version: str, ns_dict: Dict[str, Namespace]) -> URIRef:
    """가이드라인 URI 생성"""
    safe_version = re.sub(r"[^\w\-]", "_", version)
    uri_id = f"Guideline/{safe_version}_{datetime.now().strftime('%Y%m%d')}"
    return URIRef(f"{ns_dict['abui']}{uri_id}")


def create_shipment_uri(
    ship_name: str, timestamp: str, ns_dict: Dict[str, Namespace]
) -> URIRef:
    """선박 URI 생성"""
    safe_name = re.sub(r"[^\w\-]", "_", ship_name)
    safe_timestamp = re.sub(r"[^\w\-]", "_", timestamp)
    uri_id = f"Shipment/{safe_name}_{safe_timestamp}"
    return URIRef(f"{ns_dict['abui']}{uri_id}")


def create_container_uri(container_id: str, ns_dict: Dict[str, Namespace]) -> URIRef:
    """컨테이너 URI 생성"""
    safe_id = re.sub(r"[^\w\-]", "_", container_id)
    uri_id = f"Container/{safe_id}"
    return URIRef(f"{ns_dict['abui']}{uri_id}")


def create_delivery_uri(
    company: str, timestamp: str, ns_dict: Dict[str, Namespace]
) -> URIRef:
    """배송 URI 생성"""
    # Handle None values
    safe_company = re.sub(r"[^\w\-]", "_", company or "Unknown")
    safe_timestamp = re.sub(r"[^\w\-]", "_", timestamp or "Unknown")
    uri_id = f"Delivery/{safe_company}_{safe_timestamp}"
    return URIRef(f"{ns_dict['abui']}{uri_id}")


def create_participant_uri(name: str, ns_dict: Dict[str, Namespace]) -> URIRef:
    """참여자 URI 생성"""
    safe_name = re.sub(r"[^\w\-]", "_", name)
    uri_id = f"Participant/{safe_name}"
    return URIRef(f"{ns_dict['abui']}{uri_id}")


def process_guideline_data(
    guideline_data: Dict[str, Any], g: Graph, ns_dict: Dict[str, Namespace]
) -> URIRef:
    """가이드라인 데이터 처리"""
    print("[INFO] 가이드라인 데이터 처리 중...")

    # 가이드라인 URI 생성
    version = guideline_data.get("executive_summary", {}).get("version", "v2.1")
    guideline_uri = create_guideline_uri(version, ns_dict)

    # 가이드라인 타입 설정
    g.add((guideline_uri, RDF.type, ns_dict["abu"]["AbuDhabiGuideline"]))

    # Executive Summary 처리
    exec_summary = guideline_data.get("executive_summary", {})
    if exec_summary.get("version"):
        g.add(
            (guideline_uri, ns_dict["abu"]["version"], Literal(exec_summary["version"]))
        )

    # Group Profile 처리
    group_profile = guideline_data.get("group_profile", {})
    if group_profile.get("purpose_scope"):
        g.add(
            (
                guideline_uri,
                ns_dict["abu"]["purposeScope"],
                Literal(group_profile["purpose_scope"]),
            )
        )
    if group_profile.get("activity_period"):
        g.add(
            (
                guideline_uri,
                ns_dict["abu"]["activityPeriod"],
                Literal(group_profile["activity_period"]),
            )
        )
    if group_profile.get("traffic_level"):
        g.add(
            (
                guideline_uri,
                ns_dict["abu"]["trafficLevel"],
                Literal(group_profile["traffic_level"]),
            )
        )

    # 참여자 처리
    for participant in group_profile.get("top_participants", []):
        participant_uri = create_participant_uri(participant["name"], ns_dict)
        g.add((participant_uri, RDF.type, ns_dict["org"]["Organization"]))
        g.add((participant_uri, ns_dict["org"]["name"], Literal(participant["name"])))
        g.add(
            (
                participant_uri,
                ns_dict["abu"]["messageCount"],
                Literal(participant["message_count"], datatype=XSD.integer),
            )
        )
        g.add((guideline_uri, ns_dict["abu"]["hasParticipant"], participant_uri))

    # Pain Points 처리
    for i, pain_point in enumerate(guideline_data.get("pain_points", [])):
        pain_point_uri = URIRef(f"{ns_dict['abui']}PainPoint/{i+1}")
        g.add((pain_point_uri, RDF.type, ns_dict["abu"]["PainPoint"]))
        g.add((pain_point_uri, ns_dict["abu"]["description"], Literal(pain_point)))
        g.add((guideline_uri, ns_dict["abu"]["hasPainPoint"], pain_point_uri))

    # Tailored Rules 처리
    rule_count = 0
    for rule in guideline_data.get("tailored_rules", []):
        rule_count += 1
        rule_uri = URIRef(f"{ns_dict['abui']}Rule/{rule_count}")
        g.add((rule_uri, RDF.type, ns_dict["abu"]["AbuDhabiRule"]))
        g.add((rule_uri, ns_dict["abu"]["ruleCategory"], Literal(rule["category"])))
        g.add((rule_uri, ns_dict["abu"]["ruleText"], Literal(rule["rule"])))
        g.add((guideline_uri, ns_dict["abu"]["hasRule"], rule_uri))

    # KPIs 처리
    kpi_count = 0
    for kpi in guideline_data.get("kpis", []):
        kpi_count += 1
        kpi_uri = URIRef(f"{ns_dict['abui']}KPI/{kpi_count}")
        g.add((kpi_uri, RDF.type, ns_dict["abu"]["AbuDhabiKPI"]))
        g.add((kpi_uri, ns_dict["abu"]["kpiDescription"], Literal(kpi["description"])))
        if kpi.get("target_percentage"):
            g.add(
                (
                    kpi_uri,
                    ns_dict["abu"]["targetPercentage"],
                    Literal(kpi["target_percentage"], datatype=XSD.decimal),
                )
            )
        g.add((guideline_uri, ns_dict["abu"]["hasKPI"], kpi_uri))

    return guideline_uri


def process_whatsapp_data(
    whatsapp_data: Dict[str, Any], g: Graph, ns_dict: Dict[str, Namespace]
) -> List[URIRef]:
    """WhatsApp 데이터 처리"""
    print("[INFO] WhatsApp 데이터 처리 중...")

    created_uris = []

    # 선박 데이터 처리
    for shipment in whatsapp_data.get("logistics_data", {}).get("shipments", []):
        shipment_uri = create_shipment_uri(
            shipment["ship_name"], shipment["timestamp"], ns_dict
        )
        g.add((shipment_uri, RDF.type, ns_dict["abu"]["AbuDhabiShipment"]))
        g.add(
            (shipment_uri, ns_dict["abu"]["shipName"], Literal(shipment["ship_name"]))
        )
        # Convert timestamp to ISO format
        iso_timestamp = convert_whatsapp_timestamp(shipment["timestamp"])
        g.add(
            (
                shipment_uri,
                ns_dict["abu"]["timestamp"],
                Literal(iso_timestamp, datatype=XSD.dateTime),
            )
        )

        if shipment.get("eta"):
            g.add(
                (
                    shipment_uri,
                    ns_dict["abu"]["estimatedArrival"],
                    Literal(shipment["eta"]),
                )
            )
        if shipment.get("location"):
            g.add(
                (
                    shipment_uri,
                    ns_dict["abu"]["currentLocation"],
                    Literal(shipment["location"]),
                )
            )
        if shipment.get("status"):
            g.add(
                (
                    shipment_uri,
                    ns_dict["abu"]["shipStatus"],
                    Literal(shipment["status"]),
                )
            )
        if shipment.get("cargo"):
            for cargo in shipment["cargo"]:
                g.add((shipment_uri, ns_dict["abu"]["cargoType"], Literal(cargo)))

        if shipment.get("responsible_person"):
            g.add(
                (
                    shipment_uri,
                    ns_dict["abu"]["responsiblePerson"],
                    Literal(shipment["responsible_person"]),
                )
            )

        created_uris.append(shipment_uri)

    # 컨테이너 데이터 처리
    for container in whatsapp_data.get("logistics_data", {}).get("containers", []):
        container_uri = create_container_uri(container["container_id"], ns_dict)
        g.add((container_uri, RDF.type, ns_dict["abu"]["AbuDhabiContainer"]))
        g.add(
            (
                container_uri,
                ns_dict["abu"]["containerId"],
                Literal(container["container_id"]),
            )
        )
        g.add(
            (container_uri, ns_dict["abu"]["containerType"], Literal(container["type"]))
        )
        # Convert timestamp to ISO format
        iso_timestamp = convert_whatsapp_timestamp(container["timestamp"])
        g.add(
            (
                container_uri,
                ns_dict["abu"]["timestamp"],
                Literal(iso_timestamp, datatype=XSD.dateTime),
            )
        )
        g.add(
            (container_uri, ns_dict["abu"]["reportedBy"], Literal(container["sender"]))
        )

        if container.get("responsible_person"):
            g.add(
                (
                    container_uri,
                    ns_dict["abu"]["responsiblePerson"],
                    Literal(container["responsible_person"]),
                )
            )

        created_uris.append(container_uri)

    # 배송 데이터 처리
    for delivery in whatsapp_data.get("logistics_data", {}).get("deliveries", []):
        delivery_uri = create_delivery_uri(
            delivery["company"], delivery["timestamp"], ns_dict
        )
        g.add((delivery_uri, RDF.type, ns_dict["abu"]["AbuDhabiDelivery"]))
        g.add(
            (
                delivery_uri,
                ns_dict["abu"]["deliveryCompany"],
                Literal(delivery["company"]),
            )
        )
        # Convert timestamp to ISO format
        iso_timestamp = convert_whatsapp_timestamp(delivery["timestamp"])
        g.add(
            (
                delivery_uri,
                ns_dict["abu"]["timestamp"],
                Literal(iso_timestamp, datatype=XSD.dateTime),
            )
        )

        if delivery.get("quantity"):
            g.add(
                (
                    delivery_uri,
                    ns_dict["abu"]["deliveryQuantity"],
                    Literal(int(delivery["quantity"]), datatype=XSD.integer),
                )
            )
        if delivery.get("unit"):
            g.add(
                (
                    delivery_uri,
                    ns_dict["abu"]["deliveryUnit"],
                    Literal(delivery["unit"]),
                )
            )
        if delivery.get("date_info"):
            g.add(
                (
                    delivery_uri,
                    ns_dict["abu"]["deliveryDateInfo"],
                    Literal(delivery["date_info"]),
                )
            )

        if delivery.get("responsible_person"):
            g.add(
                (
                    delivery_uri,
                    ns_dict["abu"]["responsiblePerson"],
                    Literal(delivery["responsible_person"]),
                )
            )

        created_uris.append(delivery_uri)

    return created_uris


def main():
    """메인 함수"""
    print("=" * 60)
    print("아부다비 물류 데이터 RDF 변환 스크립트")
    print("=" * 60)

    # 파일 경로 설정
    guideline_analysis_file = "reports/abu_guidelines_analysis.json"
    whatsapp_analysis_file = "reports/abu_whatsapp_analysis.json"
    mapping_rules_file = "logiontology/configs/abu_mapping_rules.yaml"
    output_file = "output/abu_logistics_data.ttl"

    # 파일 존재 확인
    for file_path in [
        guideline_analysis_file,
        whatsapp_analysis_file,
        mapping_rules_file,
    ]:
        if not Path(file_path).exists():
            print(f"[ERROR] 파일을 찾을 수 없습니다: {file_path}")
            return

    # 매핑 규칙 로드
    print("\n1. 매핑 규칙 로드")
    with open(mapping_rules_file, "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)

    # 네임스페이스 설정
    ns_dict = setup_namespaces(rules)

    # RDF 그래프 생성
    g = Graph()
    for prefix, namespace in ns_dict.items():
        g.bind(prefix, namespace)

    # 가이드라인 데이터 로드
    print("\n2. 가이드라인 데이터 로드")
    with open(guideline_analysis_file, "r", encoding="utf-8") as f:
        guideline_data = json.load(f)

    # WhatsApp 데이터 로드
    print("\n3. WhatsApp 데이터 로드")
    with open(whatsapp_analysis_file, "r", encoding="utf-8") as f:
        whatsapp_data = json.load(f)

    # 가이드라인 데이터 처리
    print("\n4. 가이드라인 데이터 RDF 변환")
    guideline_uri = process_guideline_data(guideline_data, g, ns_dict)

    # WhatsApp 데이터 처리
    print("\n5. WhatsApp 데이터 RDF 변환")
    whatsapp_uris = process_whatsapp_data(whatsapp_data, g, ns_dict)

    # RDF 파일 저장
    print("\n6. RDF 파일 저장")
    Path("output").mkdir(exist_ok=True)
    g.serialize(output_file, format="turtle")

    # 결과 요약
    total_triples = len(list(g.triples((None, None, None))))
    print(f"\n[SUCCESS] RDF 변환 완료")
    print(f"  - 총 트리플 수: {total_triples}")
    print(f"  - 가이드라인 URI: {guideline_uri}")
    print(f"  - WhatsApp 엔티티: {len(whatsapp_uris)}개")
    print(f"  - 출력 파일: {output_file}")

    # 처리 보고서 생성
    report_file = (
        f"reports/abu_processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 아부다비 물류 데이터 RDF 변환 보고서\n\n")
        f.write(f"**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 처리 결과\n\n")
        f.write(f"- **총 트리플 수**: {total_triples}\n")
        f.write(f"- **가이드라인 엔티티**: 1개\n")
        f.write(f"- **WhatsApp 엔티티**: {len(whatsapp_uris)}개\n")
        f.write(f"- **출력 파일**: {output_file}\n\n")
        f.write(f"## 생성된 엔티티 유형\n\n")
        f.write(f"- AbuDhabiGuideline\n")
        f.write(f"- AbuDhabiShipment\n")
        f.write(f"- AbuDhabiContainer\n")
        f.write(f"- AbuDhabiDelivery\n")
        f.write(f"- Organization (참여자)\n")
        f.write(f"- AbuDhabiRule\n")
        f.write(f"- AbuDhabiKPI\n")

    print(f"[SUCCESS] 처리 보고서 저장: {report_file}")


if __name__ == "__main__":
    main()
