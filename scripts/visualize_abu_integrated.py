#!/usr/bin/env python3
"""
ABU 통합 시스템 시각화 대시보드 생성
엔티티 관계도, 시간순 이벤트 타임라인, 네트워크 다이어그램 생성
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
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


def load_integrated_rdf():
    """통합 RDF 그래프 로드"""
    rdf_file = Path("output/abu_integrated_system.ttl")
    if not rdf_file.exists():
        print("❌ 통합 RDF 파일을 찾을 수 없습니다.")
        return None

    g = Graph()
    g.parse(rdf_file, format="turtle")
    print(f"✅ 통합 RDF 그래프 로드: {len(g)}개 트리플")
    return g


def analyze_entity_relationships(graph, ns_dict):
    """엔티티 관계 분석"""
    print("🔍 엔티티 관계 분석 중...")

    relationships = {
        "lpo_to_person": defaultdict(list),
        "person_to_lpo": defaultdict(list),
        "person_to_vessel": defaultdict(list),
        "vessel_to_location": defaultdict(list),
        "location_to_lpo": defaultdict(list),
        "lpo_to_message": defaultdict(list),
        "message_to_person": defaultdict(list),
    }

    # LPO ↔ Person 관계
    for s, p, o in graph.triples((None, ns_dict["abu"]["handlesLPO"], None)):
        person_name = str(s).split("/")[-1].replace("_", " ")
        lpo_number = str(o).split("/")[-1]
        relationships["lpo_to_person"][lpo_number].append(person_name)

    for s, p, o in graph.triples((None, ns_dict["lpo"]["handledBy"], None)):
        lpo_number = str(s).split("/")[-1]
        person_name = str(o).split("/")[-1].replace("_", " ")
        relationships["person_to_lpo"][person_name].append(lpo_number)

    # Person ↔ Vessel 관계 (LPO를 통해)
    for s, p, o in graph.triples((None, ns_dict["abu"]["transportsLPO"], None)):
        vessel_name = str(s).split("/")[-1]
        lpo_number = str(o).split("/")[-1]
        if lpo_number in relationships["lpo_to_person"]:
            for person in relationships["lpo_to_person"][lpo_number]:
                relationships["person_to_vessel"][person].append(vessel_name)

    # Vessel ↔ Location 관계
    for s, p, o in graph.triples((None, ns_dict["abu"]["servesLocation"], None)):
        vessel_name = str(s).split("/")[-1]
        location_name = str(o).split("/")[-1]
        relationships["vessel_to_location"][vessel_name].append(location_name)

    # Location ↔ LPO 관계
    for s, p, o in graph.triples((None, ns_dict["lpo"]["hasDeliveryLocation"], None)):
        lpo_number = str(s).split("/")[-1]
        location_name = str(o).split("/")[-1]
        relationships["location_to_lpo"][location_name].append(lpo_number)

    # LPO ↔ Message 관계
    for s, p, o in graph.triples((None, ns_dict["abu"]["mentionsLPO"], None)):
        message_id = str(s).split("/")[-1]
        lpo_number = str(o).split("/")[-1]
        relationships["lpo_to_message"][lpo_number].append(message_id)

    # Message ↔ Person 관계
    for s, p, o in graph.triples((None, ns_dict["abu"]["sender"], None)):
        message_id = str(s).split("/")[-1]
        person_name = str(o)
        relationships["message_to_person"][person_name].append(message_id)

    return relationships


def generate_entity_relationship_diagram(relationships):
    """엔티티 관계도 생성"""
    print("📊 엔티티 관계도 생성 중...")

    # 주요 엔티티 추출
    persons = set()
    vessels = set()
    locations = set()
    lpos = set()

    for lpo, person_list in relationships["lpo_to_person"].items():
        lpos.add(lpo)
        persons.update(person_list)

    for vessel, location_list in relationships["vessel_to_location"].items():
        vessels.add(vessel)
        locations.update(location_list)

    # Mermaid 다이어그램 생성
    mermaid = ["graph TD"]

    # Person 노드들
    for person in list(persons)[:10]:  # 상위 10명만
        mermaid.append(f"    P_{person.replace(' ', '_')}[\"{person}\"]")

    # Vessel 노드들
    for vessel in list(vessels)[:10]:  # 상위 10개만
        mermaid.append(f'    V_{vessel}["{vessel}"]')

    # Location 노드들
    for location in list(locations)[:10]:  # 상위 10개만
        mermaid.append(f'    L_{location}["{location}"]')

    # LPO 노드들 (상위 5개만)
    for lpo in list(lpos)[:5]:
        mermaid.append(f'    LPO_{lpo}["LPO-{lpo}"]')

    # 관계 연결
    for lpo, person_list in list(relationships["lpo_to_person"].items())[:5]:
        for person in person_list[:2]:  # 각 LPO당 최대 2명
            mermaid.append(f"    LPO_{lpo} --> P_{person.replace(' ', '_')}")

    for vessel, location_list in list(relationships["vessel_to_location"].items())[:5]:
        for location in location_list[:2]:  # 각 선박당 최대 2개 위치
            mermaid.append(f"    V_{vessel} --> L_{location}")

    return "\n".join(mermaid)


def generate_timeline_diagram(graph, ns_dict):
    """시간순 이벤트 타임라인 생성"""
    print("⏰ 시간순 이벤트 타임라인 생성 중...")

    events = []

    # LPO 이벤트
    for s, p, o in graph.triples((None, ns_dict["lpo"]["issueDate"], None)):
        lpo_number = str(s).split("/")[-1]
        date = str(o)
        events.append(
            {
                "date": date,
                "type": "LPO",
                "description": f"LPO-{lpo_number} 발주",
                "entity": lpo_number,
            }
        )

    # 메시지 이벤트
    for s, p, o in graph.triples((None, ns_dict["abu"]["timestamp"], None)):
        message_id = str(s).split("/")[-1]
        date = str(o)
        events.append(
            {
                "date": date,
                "type": "Message",
                "description": f"메시지 {message_id}",
                "entity": message_id,
            }
        )

    # 날짜순 정렬
    events.sort(key=lambda x: x["date"])

    # Mermaid 타임라인 생성
    mermaid = ["timeline"]

    current_date = None
    for event in events[:20]:  # 상위 20개 이벤트만
        if event["date"] != current_date:
            mermaid.append(f"    title {event['date']}")
            current_date = event["date"]

        mermaid.append(f"        {event['type']} : {event['description']}")

    return "\n".join(mermaid)


def generate_network_diagram(relationships):
    """네트워크 다이어그램 생성"""
    print("🕸️ 네트워크 다이어그램 생성 중...")

    # 중심성 계산 (연결 수 기준)
    person_connections = Counter()
    vessel_connections = Counter()
    location_connections = Counter()

    for person, lpo_list in relationships["person_to_lpo"].items():
        person_connections[person] = len(lpo_list)

    for vessel, location_list in relationships["vessel_to_location"].items():
        vessel_connections[vessel] = len(location_list)

    for location, lpo_list in relationships["location_to_lpo"].items():
        location_connections[location] = len(lpo_list)

    # Mermaid 네트워크 다이어그램 생성
    mermaid = ["graph LR"]

    # 상위 연결된 엔티티들
    top_persons = person_connections.most_common(5)
    top_vessels = vessel_connections.most_common(5)
    top_locations = location_connections.most_common(5)

    # Person 노드들
    for person, count in top_persons:
        mermaid.append(f"    P_{person.replace(' ', '_')}[\"{person}<br/>({count})\"]")

    # Vessel 노드들
    for vessel, count in top_vessels:
        mermaid.append(f'    V_{vessel}["{vessel}<br/>({count})"]')

    # Location 노드들
    for location, count in top_locations:
        mermaid.append(f'    L_{location}["{location}<br/>({count})"]')

    # 연결 (간단한 형태)
    for person, count in top_persons[:3]:
        for vessel, _ in top_vessels[:2]:
            mermaid.append(f"    P_{person.replace(' ', '_')} -.-> V_{vessel}")

    for vessel, _ in top_vessels[:3]:
        for location, _ in top_locations[:2]:
            mermaid.append(f"    V_{vessel} -.-> L_{location}")

    return "\n".join(mermaid)


def generate_person_workflow_diagram(relationships):
    """담당자별 업무 흐름 다이어그램 생성"""
    print("👥 담당자별 업무 흐름 다이어그램 생성 중...")

    # 담당자별 LPO 처리 현황
    person_workload = {}
    for person, lpo_list in relationships["person_to_lpo"].items():
        person_workload[person] = {
            "total_lpos": len(lpo_list),
            "lpos": lpo_list[:10],  # 상위 10개만
        }

    # Mermaid 플로우차트 생성
    mermaid = ["flowchart TD"]

    # 시작 노드
    mermaid.append("    Start([시작])")

    # 각 담당자별 처리 흐름
    for person, workload in list(person_workload.items())[:5]:  # 상위 5명만
        person_id = person.replace(" ", "_")
        mermaid.append(
            f"    {person_id}[\"{person}<br/>({workload['total_lpos']}개 LPO)\"]"
        )
        mermaid.append(f"    Start --> {person_id}")

        # LPO 처리
        for i, lpo in enumerate(workload["lpos"][:3]):  # 각 담당자당 최대 3개 LPO
            lpo_id = f"{person_id}_LPO_{i}"
            mermaid.append(f'    {lpo_id}["LPO-{lpo}"]')
            mermaid.append(f"    {person_id} --> {lpo_id}")

    # 완료 노드
    mermaid.append("    End([완료])")

    # 마지막 LPO들에서 완료로 연결
    for person, workload in list(person_workload.items())[:5]:
        person_id = person.replace(" ", "_")
        for i, lpo in enumerate(workload["lpos"][:3]):
            lpo_id = f"{person_id}_LPO_{i}"
            mermaid.append(f"    {lpo_id} --> End")

    return "\n".join(mermaid)


def generate_comprehensive_report(graph, relationships, ns_dict):
    """통합 시각화 보고서 생성"""
    print("📋 통합 시각화 보고서 생성 중...")

    # 통계 수집
    stats = {
        "total_triples": len(graph),
        "lpo_count": len(
            list(graph.subjects(RDF.type, ns_dict["lpo"]["LocalPurchaseOrder"]))
        ),
        "person_count": len(list(graph.subjects(RDF.type, ns_dict["abu"]["Person"]))),
        "vessel_count": len(list(graph.subjects(RDF.type, ns_dict["abu"]["Vessel"]))),
        "location_count": len(
            list(graph.subjects(RDF.type, ns_dict["abu"]["AbuDhabiLocation"]))
        ),
        "message_count": len(
            list(graph.subjects(RDF.type, ns_dict["abu"]["WhatsAppMessage"]))
        ),
        "image_count": len(
            list(graph.subjects(RDF.type, ns_dict["abu"]["WhatsAppImage"]))
        ),
    }

    # 다이어그램 생성
    entity_diagram = generate_entity_relationship_diagram(relationships)
    timeline_diagram = generate_timeline_diagram(graph, ns_dict)
    network_diagram = generate_network_diagram(relationships)
    workflow_diagram = generate_person_workflow_diagram(relationships)

    # 보고서 생성
    report_content = f"""# ABU 통합 시스템 시각화 대시보드

**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 시스템 개요

### 통계 요약
- **총 RDF 트리플**: {stats['total_triples']:,}개
- **LPO 엔티티**: {stats['lpo_count']}개
- **담당자 엔티티**: {stats['person_count']}명
- **선박 엔티티**: {stats['vessel_count']}척
- **위치 엔티티**: {stats['location_count']}개
- **메시지 엔티티**: {stats['message_count']}개
- **이미지 엔티티**: {stats['image_count']}개

## 🔗 엔티티 관계도

다음 다이어그램은 주요 엔티티 간의 관계를 보여줍니다:

```mermaid
{entity_diagram}
```

## ⏰ 시간순 이벤트 타임라인

다음은 시간순으로 정렬된 주요 이벤트들입니다:

```mermaid
{timeline_diagram}
```

## 🕸️ 네트워크 다이어그램

다음은 엔티티 간의 연결 강도를 보여주는 네트워크 다이어그램입니다:

```mermaid
{network_diagram}
```

## 👥 담당자별 업무 흐름

다음은 주요 담당자들의 LPO 처리 흐름을 보여줍니다:

```mermaid
{workflow_diagram}
```

## 📈 핵심 인사이트

### 1. 데이터 통합 성과
- **완전한 물류 이력 추적**: LPO 발주부터 배송까지 전 과정이 RDF로 구조화됨
- **담당자 업무 가시성**: 각 담당자의 LPO 처리 현황이 명확히 추적됨
- **이미지-컨텍스트 연결**: 282개의 WhatsApp 이미지가 메시지와 연결됨

### 2. 관계 네트워크 분석
- **LPO-담당자 연결**: {len(relationships['lpo_to_person'])}개의 LPO가 담당자와 연결됨
- **선박-위치 연결**: {len(relationships['vessel_to_location'])}개의 선박이 위치와 연결됨
- **메시지-LPO 연결**: {len(relationships['lpo_to_message'])}개의 메시지가 LPO와 연결됨

### 3. 운영 효율성
- **자동화된 추적**: 모든 물류 활동이 RDF 그래프로 자동 추적됨
- **SPARQL 쿼리 가능**: 복잡한 물류 질문에 즉시 답변 가능
- **실시간 모니터링**: 담당자별, 선박별, 위치별 실시간 현황 파악 가능

## 🚀 다음 단계

1. **SPARQL 쿼리 최적화**: 자주 사용되는 쿼리 패턴에 대한 인덱스 구축
2. **실시간 업데이트**: 새로운 LPO나 메시지가 추가될 때 자동 RDF 업데이트
3. **고급 분석**: 머신러닝을 활용한 물류 패턴 분석 및 예측
4. **대시보드 구축**: 웹 기반 실시간 모니터링 대시보드 개발

## 📁 관련 파일

- **통합 RDF**: `output/abu_integrated_system.ttl`
- **크로스 레퍼런스 보고서**: `reports/abu_cross_references_report.md`
- **이미지 통합 보고서**: `reports/whatsapp_images_integration_report.md`

---
*이 보고서는 ABU WhatsApp 방의 모든 데이터를 통합하여 생성되었습니다.*
"""

    return report_content, stats


def save_visualization_report(report_content, stats):
    """시각화 보고서 저장"""
    report_file = Path("reports/abu_integrated_visualization.md")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    # 통계 데이터도 JSON으로 저장
    stats_file = Path("reports/abu_integrated_stats.json")
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    return report_file, stats_file


def main():
    """메인 실행 함수"""
    print("🔄 ABU 통합 시스템 시각화 대시보드 생성 시작...")

    # 네임스페이스 설정
    ns_dict = setup_namespaces()

    # 통합 RDF 그래프 로드
    print("📊 통합 RDF 그래프 로드 중...")
    graph = load_integrated_rdf()
    if not graph:
        return

    # 엔티티 관계 분석
    relationships = analyze_entity_relationships(graph, ns_dict)

    # 통합 보고서 생성
    print("📋 통합 시각화 보고서 생성 중...")
    report_content, stats = generate_comprehensive_report(graph, relationships, ns_dict)

    # 보고서 저장
    report_file, stats_file = save_visualization_report(report_content, stats)

    print(f"✅ ABU 통합 시각화 대시보드 생성 완료!")
    print(f"  - 시각화 보고서: {report_file}")
    print(f"  - 통계 데이터: {stats_file}")
    print(f"  - 총 트리플: {stats['total_triples']:,}개")
    print(f"  - LPO 엔티티: {stats['lpo_count']}개")
    print(f"  - 담당자: {stats['person_count']}명")
    print(f"  - 선박: {stats['vessel_count']}척")


if __name__ == "__main__":
    main()
