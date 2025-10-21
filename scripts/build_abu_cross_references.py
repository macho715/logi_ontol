#!/usr/bin/env python3
"""
ABU 데이터 간 크로스 레퍼런스 매핑 구축
LPO ↔ 메시지 ↔ 담당자 ↔ 선박 ↔ 위치 간 연결 생성
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding="utf-8")


def setup_namespaces():
    """RDF 네임스페이스 설정"""
    namespaces = {
        "hvdc": Namespace("https://hvdc.example.org/ns#"),
        "hvdci": Namespace("https://hvdc.example.org/id/"),
        "lpo": Namespace("https://hvdc.example.org/ns/lpo#"),
        "org": Namespace("http://www.w3.org/ns/org#"),
        "abu": Namespace("https://abu-dhabi.example.org/ns#"),
        "rdf": RDF,
        "rdfs": RDFS,
        "xsd": XSD,
    }
    return namespaces


def load_abu_rdf():
    """기존 ABU RDF 그래프 로드"""
    rdf_file = Path("output/abu_with_images.ttl")
    if not rdf_file.exists():
        print("❌ ABU RDF 파일을 찾을 수 없습니다.")
        return None

    g = Graph()
    g.parse(rdf_file, format="turtle")
    print(f"✅ ABU RDF 그래프 로드: {len(g)}개 트리플")
    return g


def load_lpo_rdf():
    """LPO RDF 그래프 로드"""
    rdf_file = Path("output/abu_lpo_data.ttl")
    if not rdf_file.exists():
        print("❌ LPO RDF 파일을 찾을 수 없습니다.")
        return None

    g = Graph()
    g.parse(rdf_file, format="turtle")
    print(f"✅ LPO RDF 그래프 로드: {len(g)}개 트리플")
    return g


def load_whatsapp_text():
    """WhatsApp 텍스트 대화 로드"""
    whatsapp_file = Path("ABU/‎Abu Dhabi Logistics님과의 WhatsApp 대화.txt")
    if not whatsapp_file.exists():
        print("❌ WhatsApp 텍스트 파일을 찾을 수 없습니다.")
        return None

    with open(whatsapp_file, "r", encoding="utf-8") as f:
        return f.read()


def extract_lpo_mentions_from_text(text):
    """텍스트에서 LPO 언급 추출"""
    lpo_mentions = []
    lpo_pattern = r"LPO-(\d+)"

    lines = text.split("\n")
    current_date = None
    current_sender = None

    for i, line in enumerate(lines):
        # 날짜 추출 (시간 포함)
        date_match = re.match(r"(\d{2}/\d{1,2}/\d{1,2}) [AP]M \d{1,2}:\d{2}", line)
        if date_match:
            current_date = date_match.group(1)
            # 발신자도 같은 라인에서 추출
            sender_match = re.search(r" - ([^:]+):", line)
            if sender_match:
                current_sender = sender_match.group(1)
            continue

        # LPO 언급 찾기 (발신자 정보가 있는 경우)
        lpo_matches = re.findall(lpo_pattern, line)
        if lpo_matches and current_date and current_sender:
            for lpo_num in lpo_matches:
                lpo_mentions.append(
                    {
                        "lpo_number": f"LPO-{lpo_num}",
                        "date": current_date,
                        "sender": current_sender,
                        "context": line.strip(),
                    }
                )

    return lpo_mentions


def create_cross_references(abu_graph, lpo_graph, lpo_mentions, ns_dict):
    """크로스 레퍼런스 생성"""
    print("🔗 크로스 레퍼런스 매핑 생성 중...")

    # LPO ↔ 메시지 연결
    lpo_message_links = 0
    for mention in lpo_mentions:
        lpo_number = mention["lpo_number"]
        sender = mention["sender"]
        date = mention["date"]

        # LPO URI 찾기
        lpo_uri = None
        for s, p, o in lpo_graph.triples(
            (None, ns_dict["lpo"]["lpoNumber"], Literal(lpo_number))
        ):
            lpo_uri = s
            break

        if lpo_uri:
            # 메시지 URI 생성 (간단한 형태)
            message_id = f"{date}_{sender}_{lpo_number}".replace("/", "_").replace(
                " ", "_"
            )
            message_uri = ns_dict["hvdci"][f"WhatsAppMessage/{message_id}"]

            # 메시지 엔티티 생성
            abu_graph.add((message_uri, RDF.type, ns_dict["abu"]["WhatsAppMessage"]))
            abu_graph.add((message_uri, ns_dict["abu"]["sender"], Literal(sender)))
            abu_graph.add((message_uri, ns_dict["abu"]["timestamp"], Literal(date)))
            abu_graph.add(
                (message_uri, ns_dict["abu"]["content"], Literal(mention["context"]))
            )

            # LPO ↔ 메시지 연결
            abu_graph.add((message_uri, ns_dict["abu"]["mentionsLPO"], lpo_uri))
            abu_graph.add((lpo_uri, ns_dict["lpo"]["mentionedInMessage"], message_uri))

            lpo_message_links += 1

    print(f"✅ {lpo_message_links}개의 LPO-메시지 연결 생성")

    # 담당자 ↔ LPO 연결
    person_lpo_links = 0
    person_lpo_map = {}

    for mention in lpo_mentions:
        sender = mention["sender"]
        lpo_number = mention["lpo_number"]

        if sender not in person_lpo_map:
            person_lpo_map[sender] = set()
        person_lpo_map[sender].add(lpo_number)

    for person, lpo_numbers in person_lpo_map.items():
        # 담당자 URI 생성
        person_uri = ns_dict["hvdci"][f"Person/{person.replace(' ', '_')}"]
        abu_graph.add((person_uri, RDF.type, ns_dict["abu"]["Person"]))
        abu_graph.add((person_uri, ns_dict["abu"]["name"], Literal(person)))

        # 담당자 ↔ LPO 연결
        for lpo_number in lpo_numbers:
            lpo_uri = None
            for s, p, o in lpo_graph.triples(
                (None, ns_dict["lpo"]["lpoNumber"], Literal(lpo_number))
            ):
                lpo_uri = s
                break

            if lpo_uri:
                abu_graph.add((person_uri, ns_dict["abu"]["handlesLPO"], lpo_uri))
                abu_graph.add((lpo_uri, ns_dict["lpo"]["handledBy"], person_uri))
                person_lpo_links += 1

    print(f"✅ {person_lpo_links}개의 담당자-LPO 연결 생성")

    # 위치 ↔ LPO ↔ 선박 연결
    location_shipment_links = 0

    # LPO에서 위치 정보 추출
    for s, p, o in lpo_graph.triples((None, ns_dict["lpo"]["deliveryLocation"], None)):
        location = str(o)
        lpo_uri = s

        # 위치 URI 생성
        location_uri = ns_dict["hvdci"][f"Location/{location}"]
        abu_graph.add((location_uri, RDF.type, ns_dict["abu"]["AbuDhabiLocation"]))
        abu_graph.add((location_uri, ns_dict["abu"]["locationName"], Literal(location)))

        # 위치 ↔ LPO 연결
        abu_graph.add((lpo_uri, ns_dict["lpo"]["hasDeliveryLocation"], location_uri))
        abu_graph.add((location_uri, ns_dict["abu"]["receivesLPO"], lpo_uri))

        # 선박 정보 추출 (간단한 매핑)
        vessel_mapping = {
            "AGI": ["JPT62", "JPT71", "Thuraya"],
            "DAS": ["Thuraya", "Bushra", "Tamarah"],
            "MOSB": ["JPT62", "JPT71", "Thuraya"],
            "MW4": ["JPT71"],
        }

        if location in vessel_mapping:
            for vessel_name in vessel_mapping[location]:
                vessel_uri = ns_dict["hvdci"][f"Vessel/{vessel_name}"]
                abu_graph.add((vessel_uri, RDF.type, ns_dict["abu"]["Vessel"]))
                abu_graph.add(
                    (vessel_uri, ns_dict["abu"]["vesselName"], Literal(vessel_name))
                )

                # 선박 ↔ 위치 연결
                abu_graph.add(
                    (vessel_uri, ns_dict["abu"]["servesLocation"], location_uri)
                )
                abu_graph.add(
                    (location_uri, ns_dict["abu"]["servedByVessel"], vessel_uri)
                )

                # 선박 ↔ LPO 연결
                abu_graph.add((vessel_uri, ns_dict["abu"]["transportsLPO"], lpo_uri))
                abu_graph.add((lpo_uri, ns_dict["lpo"]["transportedBy"], vessel_uri))

                location_shipment_links += 1

    print(f"✅ {location_shipment_links}개의 위치-선박-LPO 연결 생성")

    return abu_graph


def merge_graphs(abu_graph, lpo_graph):
    """두 RDF 그래프 병합"""
    print("🔄 RDF 그래프 병합 중...")

    # LPO 그래프의 모든 트리플을 ABU 그래프에 추가
    for s, p, o in lpo_graph:
        abu_graph.add((s, p, o))

    print(f"✅ 그래프 병합 완료: {len(abu_graph)}개 트리플")
    return abu_graph


def save_integrated_rdf(graph, output_file):
    """통합된 RDF 그래프 저장"""
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(graph.serialize(format="turtle"))

    return output_path


def generate_cross_reference_report(graph, lpo_mentions, output_file, ns_dict):
    """크로스 레퍼런스 보고서 생성"""
    report = {
        "integration_timestamp": datetime.now().isoformat(),
        "cross_reference_statistics": {
            "total_triples": len(graph),
            "lpo_mentions": len(lpo_mentions),
            "unique_senders": len(set(m["sender"] for m in lpo_mentions)),
            "unique_lpos": len(set(m["lpo_number"] for m in lpo_mentions)),
            "lpo_entities": len(
                list(graph.subjects(RDF.type, ns_dict["lpo"]["LocalPurchaseOrder"]))
            ),
            "message_entities": len(
                list(graph.subjects(RDF.type, ns_dict["abu"]["WhatsAppMessage"]))
            ),
            "person_entities": len(
                list(graph.subjects(RDF.type, ns_dict["abu"]["Person"]))
            ),
            "vessel_entities": len(
                list(graph.subjects(RDF.type, ns_dict["abu"]["Vessel"]))
            ),
            "location_entities": len(
                list(graph.subjects(RDF.type, ns_dict["abu"]["AbuDhabiLocation"]))
            ),
        },
        "integration_summary": {"output_file": str(output_file), "status": "SUCCESS"},
    }

    # 보고서 저장
    report_file = Path("reports/abu_cross_references_report.md")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# ABU 크로스 레퍼런스 통합 보고서\n\n")
        f.write(f"**통합 시간**: {report['integration_timestamp']}\n\n")
        f.write(f"## 크로스 레퍼런스 통계\n")
        f.write(
            f"- 총 RDF 트리플: {report['cross_reference_statistics']['total_triples']}개\n"
        )
        f.write(
            f"- LPO 언급: {report['cross_reference_statistics']['lpo_mentions']}개\n"
        )
        f.write(
            f"- 고유 발신자: {report['cross_reference_statistics']['unique_senders']}명\n"
        )
        f.write(
            f"- 고유 LPO: {report['cross_reference_statistics']['unique_lpos']}개\n"
        )
        f.write(
            f"- LPO 엔티티: {report['cross_reference_statistics']['lpo_entities']}개\n"
        )
        f.write(
            f"- 메시지 엔티티: {report['cross_reference_statistics']['message_entities']}개\n"
        )
        f.write(
            f"- 담당자 엔티티: {report['cross_reference_statistics']['person_entities']}개\n"
        )
        f.write(
            f"- 선박 엔티티: {report['cross_reference_statistics']['vessel_entities']}개\n"
        )
        f.write(
            f"- 위치 엔티티: {report['cross_reference_statistics']['location_entities']}개\n\n"
        )
        f.write(f"## 출력 파일\n")
        f.write(f"- 통합 RDF: {output_file}\n\n")
        f.write(f"## 상태: {report['integration_summary']['status']}\n")

    return report


def main():
    """메인 실행 함수"""
    print("🔄 ABU 크로스 레퍼런스 매핑 구축 시작...")

    # 네임스페이스 설정
    ns_dict = setup_namespaces()

    # 기존 RDF 그래프들 로드
    print("📊 RDF 그래프들 로드 중...")
    abu_graph = load_abu_rdf()
    if not abu_graph:
        return

    lpo_graph = load_lpo_rdf()
    if not lpo_graph:
        return

    # WhatsApp 텍스트 로드
    print("💬 WhatsApp 텍스트 로드 중...")
    whatsapp_text = load_whatsapp_text()
    if not whatsapp_text:
        return

    # LPO 언급 추출
    print("🔍 LPO 언급 추출 중...")
    lpo_mentions = extract_lpo_mentions_from_text(whatsapp_text)
    print(f"✅ {len(lpo_mentions)}개의 LPO 언급을 추출했습니다.")

    # 크로스 레퍼런스 생성
    abu_graph = create_cross_references(abu_graph, lpo_graph, lpo_mentions, ns_dict)

    # 그래프 병합
    abu_graph = merge_graphs(abu_graph, lpo_graph)

    # 통합된 RDF 저장
    output_file = Path("output/abu_integrated_system.ttl")
    print(f"💾 통합 RDF 저장 중: {output_file}")
    saved_path = save_integrated_rdf(abu_graph, output_file)

    # 통합 보고서 생성
    print("📋 통합 보고서 생성 중...")
    report = generate_cross_reference_report(
        abu_graph, lpo_mentions, saved_path, ns_dict
    )

    print(f"✅ ABU 크로스 레퍼런스 통합 완료!")
    print(f"  - 출력 파일: {saved_path}")
    print(f"  - 총 트리플: {len(abu_graph)}개")
    print(f"  - LPO 언급: {len(lpo_mentions)}개")
    print(f"  - 보고서: reports/abu_cross_references_report.md")


if __name__ == "__main__":
    main()
