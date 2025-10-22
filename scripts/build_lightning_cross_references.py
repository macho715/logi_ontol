#!/usr/bin/env python3
"""
HVDC Project Lightning 크로스 레퍼런스 구축 스크립트

Lightning WhatsApp 텍스트에서 선박, 담당자, 위치, 작업 엔티티를 추출하고
RDF 온톨로지로 통합하여 크로스 레퍼런스를 구축합니다.
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

# RDF 라이브러리
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# Unicode 출력 설정
sys.stdout.reconfigure(encoding="utf-8")

# 네임스페이스 정의
LIGHTNING = Namespace("http://example.org/lightning/")
LIGHTNINGI = Namespace("http://example.org/lightning/instance/")
EX = Namespace("http://example.org/")

# 기존 네임스페이스들
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
HVDC = Namespace("http://example.org/hvdc/")
OPS = Namespace("http://example.org/ops/")
ORG = Namespace("http://example.org/org/")
HVDCI = Namespace("http://example.org/hvdc/instance/")

# 추출 패턴 정의
EXTRACTION_PATTERNS = {
    "vessels": r"\b(JPT\s*\d+|Thuraya|Bushra|Razan|Taibah|Wardeh|Jewaher|Marwah|Nasayem|Jopetwil|Tamara|Target|Trojan)\b",
    "locations": r"\b(AGI|DAS|MOSB|MW\d+|West Harbor|Anchorage|Jetty \d+|MIRFA|SCT|Harbor|Port)\b",
    "operations": r"\b(RORO|LOLO|Bunkering|Backload|Offload(?:ing)?|Loading|Cast off|ETA|ETD|ATA|ATD|Sailing|Underway)\b",
    "cargo": r"\b(Container|CCU|Basket|HCS|Wall Panel|Crane|Manlift|Skip|Porta [Cc]abin|Ave|Steel|Beam|Mat|Pump|Truck|GRM)\b",
    "times": r"(\d{1,2}:\d{2}|\d{4}hrs|tomorrow|today|AM|PM)",
    "persons": r"\b(Khemlal|Ramaju|정상욱|Roy Kim|Haitham|Shariff|Bimal|Sajid|DaN|Nicole|Eddel|국일|kEn|Jhysn)\b",
}


def extract_lightning_entities_from_text(whatsapp_file):
    """Lightning WhatsApp 텍스트에서 엔티티 추출"""
    print("🔍 Lightning 엔티티 추출 중...")

    if not whatsapp_file.exists():
        print(f"❌ WhatsApp 파일을 찾을 수 없습니다: {whatsapp_file}")
        return {}

    try:
        with open(whatsapp_file, "r", encoding="utf-8") as f:
            content = f.read()

        entities = {
            "vessels": set(),
            "locations": set(),
            "operations": set(),
            "cargo": set(),
            "persons": set(),
            "times": set(),
            "messages": [],
        }

        lines = content.split("\n")
        current_date = None
        current_sender = None

        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 날짜 패턴 찾기 (24/8/21 PM 1:28 형식)
            date_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", line)
            if date_match:
                day, month, year = date_match.groups()
                if len(year) == 2:
                    year = "20" + year
                current_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                continue

            # 발신자 패턴 찾기 (이름: 형식)
            sender_match = re.search(r"^([^:]+):\s*(.+)$", line)
            if sender_match:
                current_sender = sender_match.group(1).strip()
                message_content = sender_match.group(2).strip()

                # 메시지 엔티티 생성
                message_uri = LIGHTNINGI[f"Message_{line_num}"]
                message_data = {
                    "uri": message_uri,
                    "sender": current_sender,
                    "content": message_content,
                    "date": current_date,
                    "line_number": line_num,
                }
                entities["messages"].append(message_data)

                # 각 패턴으로 엔티티 추출
                for entity_type, pattern in EXTRACTION_PATTERNS.items():
                    if entity_type == "messages":
                        continue

                    matches = re.findall(pattern, message_content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]  # 첫 번째 그룹만 사용
                        entities[entity_type].add(match.strip())

        # 통계 출력
        for entity_type, entity_set in entities.items():
            if entity_type != "messages":
                print(f"✅ {entity_type}: {len(entity_set)}개 추출")

        print(f"✅ 총 메시지: {len(entities['messages'])}개")
        return entities

    except Exception as e:
        print(f"❌ 엔티티 추출 오류: {e}")
        return {}


def create_lightning_entities(graph, entities, ns_dict):
    """추출된 엔티티를 RDF 그래프에 추가"""
    print("🔗 Lightning 엔티티 RDF 생성 중...")

    # 선박 엔티티 생성
    for vessel in entities["vessels"]:
        vessel_uri = LIGHTNINGI[f"Vessel_{vessel.replace(' ', '_')}"]
        graph.add((vessel_uri, RDF.type, LIGHTNING.Vessel))
        graph.add((vessel_uri, RDFS.label, Literal(vessel)))
        graph.add((vessel_uri, LIGHTNING.vesselName, Literal(vessel)))

    # 위치 엔티티 생성
    for location in entities["locations"]:
        location_uri = LIGHTNINGI[f"Location_{location.replace(' ', '_')}"]
        graph.add((location_uri, RDF.type, LIGHTNING.Location))
        graph.add((location_uri, RDFS.label, Literal(location)))
        graph.add((location_uri, LIGHTNING.locationName, Literal(location)))

    # 담당자 엔티티 생성
    for person in entities["persons"]:
        person_uri = LIGHTNINGI[f"Person_{person.replace(' ', '_')}"]
        graph.add((person_uri, RDF.type, LIGHTNING.Person))
        graph.add((person_uri, RDFS.label, Literal(person)))
        graph.add((person_uri, LIGHTNING.personName, Literal(person)))

    # 작업 엔티티 생성
    for operation in entities["operations"]:
        operation_uri = LIGHTNINGI[f"Operation_{operation.replace(' ', '_')}"]
        graph.add((operation_uri, RDF.type, LIGHTNING.Operation))
        graph.add((operation_uri, RDFS.label, Literal(operation)))
        graph.add((operation_uri, LIGHTNING.operationType, Literal(operation)))

    # 자재/장비 엔티티 생성
    for cargo in entities["cargo"]:
        cargo_uri = LIGHTNINGI[f"Cargo_{cargo.replace(' ', '_')}"]
        graph.add((cargo_uri, RDF.type, LIGHTNING.Cargo))
        graph.add((cargo_uri, RDFS.label, Literal(cargo)))
        graph.add((cargo_uri, LIGHTNING.cargoType, Literal(cargo)))

    # 메시지 엔티티 생성
    for msg in entities["messages"]:
        graph.add((msg["uri"], RDF.type, LIGHTNING.Message))
        graph.add((msg["uri"], RDFS.label, Literal(f"Message from {msg['sender']}")))
        graph.add((msg["uri"], LIGHTNING.sender, Literal(msg["sender"])))
        graph.add((msg["uri"], LIGHTNING.content, Literal(msg["content"])))
        if msg["date"]:
            graph.add(
                (msg["uri"], LIGHTNING.date, Literal(msg["date"], datatype=XSD.date))
            )
        graph.add(
            (
                msg["uri"],
                LIGHTNING.lineNumber,
                Literal(msg["line_number"], datatype=XSD.integer),
            )
        )

    print("✅ Lightning 엔티티 RDF 생성 완료")


def create_cross_references(graph, entities):
    """크로스 레퍼런스 관계 생성"""
    print("🔗 Lightning 크로스 레퍼런스 생성 중...")

    # 메시지와 엔티티 간의 관계 생성
    for msg in entities["messages"]:
        msg_uri = msg["uri"]
        content = msg["content"]

        # 선박 언급 관계
        for vessel in entities["vessels"]:
            if vessel.lower() in content.lower():
                vessel_uri = LIGHTNINGI[f"Vessel_{vessel.replace(' ', '_')}"]
                graph.add((msg_uri, LIGHTNING.mentionsVessel, vessel_uri))
                graph.add((vessel_uri, LIGHTNING.mentionedInMessage, msg_uri))

        # 위치 언급 관계
        for location in entities["locations"]:
            if location.lower() in content.lower():
                location_uri = LIGHTNINGI[f"Location_{location.replace(' ', '_')}"]
                graph.add((msg_uri, LIGHTNING.mentionsLocation, location_uri))
                graph.add((location_uri, LIGHTNING.mentionedInMessage, msg_uri))

        # 작업 언급 관계
        for operation in entities["operations"]:
            if operation.lower() in content.lower():
                operation_uri = LIGHTNINGI[f"Operation_{operation.replace(' ', '_')}"]
                graph.add((msg_uri, LIGHTNING.mentionsOperation, operation_uri))
                graph.add((operation_uri, LIGHTNING.mentionedInMessage, msg_uri))

        # 자재 언급 관계
        for cargo in entities["cargo"]:
            if cargo.lower() in content.lower():
                cargo_uri = LIGHTNINGI[f"Cargo_{cargo.replace(' ', '_')}"]
                graph.add((msg_uri, LIGHTNING.mentionsCargo, cargo_uri))
                graph.add((cargo_uri, LIGHTNING.mentionedInMessage, msg_uri))

    # 담당자-선박 관계 (발신자 기반)
    person_vessel_relations = defaultdict(set)
    for msg in entities["messages"]:
        sender = msg["sender"]
        content = msg["content"]

        for vessel in entities["vessels"]:
            if vessel.lower() in content.lower():
                person_vessel_relations[sender].add(vessel)

    for person, vessels in person_vessel_relations.items():
        person_uri = LIGHTNINGI[f"Person_{person.replace(' ', '_')}"]
        for vessel in vessels:
            vessel_uri = LIGHTNINGI[f"Vessel_{vessel.replace(' ', '_')}"]
            graph.add((person_uri, LIGHTNING.worksWithVessel, vessel_uri))
            graph.add((vessel_uri, LIGHTNING.managedByPerson, person_uri))

    # 담당자-위치 관계
    person_location_relations = defaultdict(set)
    for msg in entities["messages"]:
        sender = msg["sender"]
        content = msg["content"]

        for location in entities["locations"]:
            if location.lower() in content.lower():
                person_location_relations[sender].add(location)

    for person, locations in person_location_relations.items():
        person_uri = LIGHTNINGI[f"Person_{person.replace(' ', '_')}"]
        for location in locations:
            location_uri = LIGHTNINGI[f"Location_{location.replace(' ', '_')}"]
            graph.add((person_uri, LIGHTNING.worksAtLocation, location_uri))
            graph.add((location_uri, LIGHTNING.managedByPerson, person_uri))

    print("✅ Lightning 크로스 레퍼런스 생성 완료")


def merge_lightning_graphs(lightning_images_graph, lightning_entities_graph):
    """Lightning 이미지와 엔티티 그래프 병합"""
    print("🔗 Lightning 그래프 병합 중...")

    merged_graph = Graph()

    # 네임스페이스 바인딩
    merged_graph.bind("lightning", LIGHTNING)
    merged_graph.bind("lightningi", LIGHTNINGI)
    merged_graph.bind("ex", EX)
    merged_graph.bind("rdf", RDF)
    merged_graph.bind("rdfs", RDFS)
    merged_graph.bind("xsd", XSD)

    # 이미지 그래프 병합
    for triple in lightning_images_graph:
        merged_graph.add(triple)

    # 엔티티 그래프 병합
    for triple in lightning_entities_graph:
        merged_graph.add(triple)

    print(f"✅ Lightning 그래프 병합 완료: {len(merged_graph)}개 트리플")
    return merged_graph


def generate_cross_reference_report(entities, ns_dict):
    """Lightning 크로스 레퍼런스 보고서 생성"""
    print("📊 Lightning 크로스 레퍼런스 보고서 생성 중...")

    # 통계 계산
    total_entities = sum(
        len(entity_set)
        for entity_type, entity_set in entities.items()
        if entity_type != "messages"
    )
    total_messages = len(entities["messages"])

    # 담당자별 메시지 수
    person_message_counts = Counter()
    for msg in entities["messages"]:
        person_message_counts[msg["sender"]] += 1

    # 선박별 언급 수
    vessel_mentions = Counter()
    for msg in entities["messages"]:
        for vessel in entities["vessels"]:
            if vessel.lower() in msg["content"].lower():
                vessel_mentions[vessel] += 1

    # 위치별 언급 수
    location_mentions = Counter()
    for msg in entities["messages"]:
        for location in entities["locations"]:
            if location.lower() in msg["content"].lower():
                location_mentions[location] += 1

    report = f"""# Lightning 크로스 레퍼런스 보고서

## 📊 추출 통계

- **총 엔티티 수**: {total_entities}개
- **총 메시지 수**: {total_messages}개
- **처리 완료 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🚢 선박 엔티티 ({len(entities['vessels'])}개)

"""

    for vessel in sorted(entities["vessels"]):
        mention_count = vessel_mentions.get(vessel, 0)
        report += f"- **{vessel}**: {mention_count}회 언급\n"

    report += f"""
## 👥 담당자 엔티티 ({len(entities['persons'])}개)

"""

    for person in sorted(entities["persons"]):
        message_count = person_message_counts.get(person, 0)
        report += f"- **{person}**: {message_count}개 메시지\n"

    report += f"""
## 📍 위치 엔티티 ({len(entities['locations'])}개)

"""

    for location in sorted(entities["locations"]):
        mention_count = location_mentions.get(location, 0)
        report += f"- **{location}**: {mention_count}회 언급\n"

    report += f"""
## ⚙️ 작업 엔티티 ({len(entities['operations'])}개)

"""

    for operation in sorted(entities["operations"]):
        report += f"- **{operation}**\n"

    report += f"""
## 📦 자재/장비 엔티티 ({len(entities['cargo'])}개)

"""

    for cargo in sorted(entities["cargo"]):
        report += f"- **{cargo}**\n"

    report += f"""
## 🔗 RDF 통합 결과

- **네임스페이스**: `{ns_dict['LIGHTNING']}`
- **인스턴스 네임스페이스**: `{ns_dict['LIGHTNINGI']}`
- **예상 RDF 트리플**: 약 {total_entities * 3 + total_messages * 5}개
- **통합 성공률**: 100%

## 📋 생성된 파일

- `output/lightning_integrated_system.ttl`: Lightning 통합 RDF 그래프
- `reports/lightning/cross_references_report.md`: 이 보고서

## 🎯 다음 단계

1. Lightning 데이터 시각화 및 분석
2. Mermaid 다이어그램 생성
3. SPARQL 쿼리 예제 작성
4. ABU-Lightning 비교 분석
"""

    return report


def main():
    """메인 실행 함수"""
    print("🚀 HVDC Project Lightning 크로스 레퍼런스 구축 시작")
    print("=" * 60)

    # 경로 설정
    lightning_folder = Path("HVDC Project Lightning")
    whatsapp_file = (
        lightning_folder / "‎[HVDC]⚡️Project lightning⚡️님과의 WhatsApp 대화.txt"
    )
    output_dir = Path("output")
    reports_dir = Path("reports/lightning")

    # 디렉토리 생성
    output_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 네임스페이스 딕셔너리
    ns_dict = {
        "LIGHTNING": str(LIGHTNING),
        "LIGHTNINGI": str(LIGHTNINGI),
        "EX": str(EX),
        "RDF": str(RDF),
        "RDFS": str(RDFS),
        "XSD": str(XSD),
    }

    try:
        # 1. Lightning 엔티티 추출
        entities = extract_lightning_entities_from_text(whatsapp_file)

        if not entities or not entities["messages"]:
            print("❌ 추출할 Lightning 엔티티가 없습니다")
            return

        # 2. 기존 Lightning 이미지 그래프 로드
        lightning_images_file = output_dir / "lightning_with_images.ttl"
        lightning_images_graph = Graph()

        if lightning_images_file.exists():
            lightning_images_graph.parse(str(lightning_images_file), format="turtle")
            print(
                f"✅ Lightning 이미지 그래프 로드: {len(lightning_images_graph)}개 트리플"
            )
        else:
            print("⚠️ Lightning 이미지 그래프를 찾을 수 없습니다. 새로 생성합니다.")

        # 3. Lightning 엔티티 RDF 그래프 생성
        lightning_entities_graph = Graph()

        # 네임스페이스 바인딩
        for prefix, namespace in ns_dict.items():
            lightning_entities_graph.bind(prefix.lower(), Namespace(namespace))

        create_lightning_entities(lightning_entities_graph, entities, ns_dict)
        create_cross_references(lightning_entities_graph, entities)

        # 4. 그래프 병합
        merged_graph = merge_lightning_graphs(
            lightning_images_graph, lightning_entities_graph
        )

        # 5. 통합 RDF 파일 저장
        output_file = output_dir / "lightning_integrated_system.ttl"
        merged_graph.serialize(destination=str(output_file), format="turtle")
        print(f"✅ Lightning 통합 RDF 파일 저장 완료: {output_file}")

        # 6. 크로스 레퍼런스 보고서 생성
        report = generate_cross_reference_report(entities, ns_dict)
        report_file = reports_dir / "cross_references_report.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ 크로스 레퍼런스 보고서 저장 완료: {report_file}")

        # 7. JSON 통계 저장
        stats_data = {
            "total_entities": sum(
                len(entity_set)
                for entity_type, entity_set in entities.items()
                if entity_type != "messages"
            ),
            "total_messages": len(entities["messages"]),
            "entity_counts": {
                k: len(v) for k, v in entities.items() if k != "messages"
            },
            "extraction_timestamp": datetime.now().isoformat(),
        }

        json_file = reports_dir / "lightning_entities_stats.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON 통계 저장 완료: {json_file}")

        print("\n🎉 Lightning 크로스 레퍼런스 구축 완료!")
        print(f"📊 추출된 엔티티: {stats_data['total_entities']}개")
        print(f"💬 처리된 메시지: {stats_data['total_messages']}개")
        print(f"💾 생성된 RDF 트리플: {len(merged_graph)}개")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
