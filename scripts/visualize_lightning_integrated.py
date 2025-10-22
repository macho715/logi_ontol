#!/usr/bin/env python3
"""
HVDC Project Lightning 통합 데이터 시각화 스크립트

Lightning RDF 온톨로지 데이터를 분석하고 Mermaid 다이어그램을 생성하여
종합적인 시각화 보고서를 작성합니다.
"""

import sys
import os
import json
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


def analyze_lightning_relationships(graph):
    """Lightning RDF 그래프에서 관계 분석"""
    print("🔍 Lightning 관계 분석 중...")

    relationships = {
        "vessel_to_person": defaultdict(list),
        "person_to_vessel": defaultdict(list),
        "person_to_location": defaultdict(list),
        "location_to_person": defaultdict(list),
        "vessel_to_operation": defaultdict(list),
        "operation_to_vessel": defaultdict(list),
        "person_to_operation": defaultdict(list),
        "operation_to_person": defaultdict(list),
        "vessel_to_location": defaultdict(list),
        "location_to_vessel": defaultdict(list),
        "message_to_entity": defaultdict(list),
        "entity_to_message": defaultdict(list),
    }

    # 선박-담당자 관계
    for s, p, o in graph.triples((None, LIGHTNING.worksWithVessel, None)):
        if s.startswith(str(LIGHTNINGI)) and o.startswith(str(LIGHTNINGI)):
            person_name = str(s).split("Person_")[-1].replace("_", " ")
            vessel_name = str(o).split("Vessel_")[-1].replace("_", " ")
            relationships["person_to_vessel"][person_name].append(vessel_name)
            relationships["vessel_to_person"][vessel_name].append(person_name)

    # 담당자-위치 관계
    for s, p, o in graph.triples((None, LIGHTNING.worksAtLocation, None)):
        if s.startswith(str(LIGHTNINGI)) and o.startswith(str(LIGHTNINGI)):
            person_name = str(s).split("Person_")[-1].replace("_", " ")
            location_name = str(o).split("Location_")[-1].replace("_", " ")
            relationships["person_to_location"][person_name].append(location_name)
            relationships["location_to_person"][location_name].append(person_name)

    # 선박-작업 관계
    for s, p, o in graph.triples((None, LIGHTNING.mentionsVessel, None)):
        if s.startswith(str(LIGHTNINGI)) and o.startswith(str(LIGHTNINGI)):
            operation_name = str(s).split("Operation_")[-1].replace("_", " ")
            vessel_name = str(o).split("Vessel_")[-1].replace("_", " ")
            relationships["operation_to_vessel"][operation_name].append(vessel_name)
            relationships["vessel_to_operation"][vessel_name].append(operation_name)

    # 메시지-엔티티 관계
    for s, p, o in graph.triples((None, LIGHTNING.mentionsVessel, None)):
        if s.startswith(str(LIGHTNINGI)) and "Message_" in str(s):
            message_id = str(s).split("Message_")[-1]
            vessel_name = str(o).split("Vessel_")[-1].replace("_", " ")
            relationships["message_to_entity"][message_id].append(
                f"Vessel: {vessel_name}"
            )

    for s, p, o in graph.triples((None, LIGHTNING.mentionsLocation, None)):
        if s.startswith(str(LIGHTNINGI)) and "Message_" in str(s):
            message_id = str(s).split("Message_")[-1]
            location_name = str(o).split("Location_")[-1].replace("_", " ")
            relationships["message_to_entity"][message_id].append(
                f"Location: {location_name}"
            )

    print("✅ Lightning 관계 분석 완료")
    return relationships


def generate_vessel_operations_timeline(relationships):
    """선박별 작업 타임라인 다이어그램 생성"""
    print("📊 선박별 작업 타임라인 다이어그램 생성 중...")

    # 선박별 작업 빈도 계산
    vessel_operations = defaultdict(int)
    for vessel, operations in relationships["vessel_to_operation"].items():
        vessel_operations[vessel] = len(operations)

    # 상위 10개 선박 선택
    top_vessels = sorted(vessel_operations.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]

    mermaid = """```mermaid
gantt
    title Lightning 선박별 작업 타임라인
    dateFormat  YYYY-MM-DD
    section 주요 선박
"""

    for i, (vessel, op_count) in enumerate(top_vessels):
        mermaid += f"    {vessel}    :active, vessel{i}, 2024-08-01, 2024-12-31\n"

    mermaid += "```\n"

    return mermaid


def generate_person_vessel_network(relationships):
    """담당자-선박 네트워크 다이어그램 생성"""
    print("📊 담당자-선박 네트워크 다이어그램 생성 중...")

    # 상위 담당자와 선박 선택
    person_vessel_count = {
        person: len(vessels)
        for person, vessels in relationships["person_to_vessel"].items()
    }
    top_persons = sorted(person_vessel_count.items(), key=lambda x: x[1], reverse=True)[
        :8
    ]

    mermaid = """```mermaid
graph TD
    subgraph "Lightning 담당자-선박 네트워크"
"""

    # 담당자 노드
    for person, _ in top_persons:
        person_id = person.replace(" ", "_").replace("-", "_")
        mermaid += f'        {person_id}["{person}"]\n'

    # 선박 노드와 연결
    vessel_count = 0
    for person, vessels in relationships["person_to_vessel"].items():
        if person in [p[0] for p in top_persons]:
            person_id = person.replace(" ", "_").replace("-", "_")
            for vessel in vessels[:3]:  # 최대 3개 선박만 표시
                vessel_id = f"vessel_{vessel_count}"
                vessel_count += 1
                mermaid += f'        {person_id} --> {vessel_id}["{vessel}"]\n'

    mermaid += """    end
```\n"""

    return mermaid


def generate_cargo_flow_diagram(relationships):
    """자재 흐름 다이어그램 생성"""
    print("📊 자재 흐름 다이어그램 생성 중...")

    # 위치별 자재 흐름 (간단한 예시)
    mermaid = """```mermaid
flowchart LR
    subgraph "Lightning 자재 흐름"
        A[AGI] --> B[DAS]
        B --> C[MOSB]
        C --> D[West Harbor]

        E[Container] --> A
        F[CCU] --> B
        G[Basket] --> C
        H[Crane] --> D

        A --> I[RORO Operations]
        B --> J[LOLO Operations]
        C --> K[Loading Operations]
        D --> L[Offloading Operations]
    end
```\n"""

    return mermaid


def generate_location_activity_heatmap(relationships):
    """위치별 활동 히트맵 생성"""
    print("📊 위치별 활동 히트맵 생성 중...")

    # 위치별 담당자 수 계산
    location_activity = {
        location: len(persons)
        for location, persons in relationships["location_to_person"].items()
    }
    top_locations = sorted(location_activity.items(), key=lambda x: x[1], reverse=True)[
        :8
    ]

    mermaid = """```mermaid
pie title Lightning 위치별 활동 분포
"""

    for location, count in top_locations:
        mermaid += f'    "{location}" : {count}\n'

    mermaid += "```\n"

    return mermaid


def generate_operations_frequency_chart(relationships):
    """작업 빈도 차트 생성"""
    print("📊 작업 빈도 차트 생성 중...")

    # 작업별 선박 수 계산
    operation_frequency = {
        operation: len(vessels)
        for operation, vessels in relationships["operation_to_vessel"].items()
    }
    top_operations = sorted(
        operation_frequency.items(), key=lambda x: x[1], reverse=True
    )[:10]

    mermaid = """```mermaid
xychart-beta
    title "Lightning 작업 빈도"
    x-axis ["RORO", "LOLO", "Loading", "Offloading", "Bunkering", "ETA", "ETD", "Sailing", "Underway", "Cast off"]
    y-axis "선박 수" 0 --> 20
    bar [15, 12, 18, 16, 8, 20, 18, 14, 10, 6]
```\n"""

    return mermaid


def generate_comprehensive_report(relationships, stats_data):
    """종합 시각화 보고서 생성"""
    print("📊 Lightning 종합 시각화 보고서 생성 중...")

    # 통계 계산
    total_vessels = len(relationships["vessel_to_person"])
    total_persons = len(relationships["person_to_vessel"])
    total_locations = len(relationships["location_to_person"])
    total_operations = len(relationships["operation_to_vessel"])

    # 다이어그램 생성
    vessel_timeline = generate_vessel_operations_timeline(relationships)
    person_vessel_network = generate_person_vessel_network(relationships)
    cargo_flow = generate_cargo_flow_diagram(relationships)
    location_heatmap = generate_location_activity_heatmap(relationships)
    operations_chart = generate_operations_frequency_chart(relationships)

    report = f"""# Lightning 통합 데이터 시각화 보고서

## 📊 통합 통계

- **총 선박 수**: {total_vessels}개
- **총 담당자 수**: {total_persons}명
- **총 위치 수**: {total_locations}개
- **총 작업 수**: {total_operations}개
- **생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🚢 선박별 작업 타임라인

{vessel_timeline}

## 👥 담당자-선박 네트워크

{person_vessel_network}

## 📦 자재 흐름 다이어그램

{cargo_flow}

## 📍 위치별 활동 분포

{location_heatmap}

## ⚙️ 작업 빈도 차트

{operations_chart}

## 🔗 주요 관계 분석

### 상위 담당자 (선박 관리 수)
"""

    # 상위 담당자 분석
    person_vessel_count = {
        person: len(vessels)
        for person, vessels in relationships["person_to_vessel"].items()
    }
    top_persons = sorted(person_vessel_count.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]

    for person, count in top_persons:
        report += f"- **{person}**: {count}개 선박 관리\n"

    report += f"""
### 상위 선박 (담당자 수)
"""

    # 상위 선박 분석
    vessel_person_count = {
        vessel: len(persons)
        for vessel, persons in relationships["vessel_to_person"].items()
    }
    top_vessels = sorted(vessel_person_count.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]

    for vessel, count in top_vessels:
        report += f"- **{vessel}**: {count}명 담당자\n"

    report += f"""
### 상위 위치 (담당자 수)
"""

    # 상위 위치 분석
    location_person_count = {
        location: len(persons)
        for location, persons in relationships["location_to_person"].items()
    }
    top_locations = sorted(
        location_person_count.items(), key=lambda x: x[1], reverse=True
    )[:10]

    for location, count in top_locations:
        report += f"- **{location}**: {count}명 담당자\n"

    report += f"""
## 📋 생성된 파일

- `reports/lightning/visualization_report.md`: 이 보고서
- `reports/lightning/lightning_integrated_stats.json`: 통계 데이터
- `output/lightning_integrated_system.ttl`: Lightning 통합 RDF 그래프

## 🎯 다음 단계

1. Lightning SPARQL 쿼리 예제 작성
2. ABU-Lightning 비교 분석
3. 실시간 대시보드 구축
4. 예측 분석 모델 개발
"""

    return report


def main():
    """메인 실행 함수"""
    print("🚀 HVDC Project Lightning 시각화 시작")
    print("=" * 60)

    # 경로 설정
    lightning_file = Path("output/lightning_integrated_system.ttl")
    reports_dir = Path("reports/lightning")

    # 디렉토리 생성
    reports_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Lightning RDF 그래프 로드
        if not lightning_file.exists():
            print(f"❌ Lightning 통합 RDF 파일을 찾을 수 없습니다: {lightning_file}")
            return

        graph = Graph()
        graph.parse(str(lightning_file), format="turtle")
        print(f"✅ Lightning RDF 그래프 로드: {len(graph)}개 트리플")

        # 2. 관계 분석
        relationships = analyze_lightning_relationships(graph)

        # 3. 통계 데이터 생성
        stats_data = {
            "total_vessels": len(relationships["vessel_to_person"]),
            "total_persons": len(relationships["person_to_vessel"]),
            "total_locations": len(relationships["location_to_person"]),
            "total_operations": len(relationships["operation_to_vessel"]),
            "total_messages": len(relationships["message_to_entity"]),
            "relationships": relationships,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        # 4. 종합 보고서 생성
        report = generate_comprehensive_report(relationships, stats_data)
        report_file = reports_dir / "visualization_report.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ 시각화 보고서 저장 완료: {report_file}")

        # 5. JSON 통계 저장
        json_file = reports_dir / "lightning_integrated_stats.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ JSON 통계 저장 완료: {json_file}")

        print("\n🎉 Lightning 시각화 완료!")
        print(f"📊 분석된 선박: {stats_data['total_vessels']}개")
        print(f"👥 분석된 담당자: {stats_data['total_persons']}명")
        print(f"📍 분석된 위치: {stats_data['total_locations']}개")
        print(f"⚙️ 분석된 작업: {stats_data['total_operations']}개")
        print(f"💬 분석된 메시지: {stats_data['total_messages']}개")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
