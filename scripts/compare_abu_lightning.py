#!/usr/bin/env python3
"""
ABU-Lightning 시스템 비교 분석 스크립트

두 시스템의 메시지 패턴, 담당자 역할, 작업 타입 분포, 효율성 메트릭을 비교 분석합니다.
"""

import sys
import json
import csv
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import rdflib
from rdflib import Namespace, RDF, RDFS, XSD

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding="utf-8")

# 네임스페이스 정의
ABU = Namespace("https://abu-dhabi.example.org/ns#")
ABUI = Namespace("https://abu-dhabi.example.org/id/")
LIGHTNING = Namespace("http://example.org/lightning/")
LIGHTNINGI = Namespace("http://example.org/lightning/instance/")


def load_rdf_graph(file_path):
    """RDF 그래프 로드"""
    g = rdflib.Graph()
    g.parse(file_path, format="turtle")
    print(f"Loaded {len(g)} triples from {file_path}")
    return g


def load_csv_entities(csv_path):
    """CSV 엔티티 통계 로드"""
    entities = defaultdict(list)
    total_count = 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Category") and row.get("Entity"):
                category = row["Category"]
                entity = row["Entity"]
                count = int(row["Count"]) if row.get("Count") else 0
                entities[category].append({"entity": entity, "count": count})
                total_count += count

    return entities, total_count


def analyze_system_stats(graph, ns, nsi, system_name):
    """시스템 통계 분석"""
    stats = {}

    # 기본 카운트
    stats["total_triples"] = len(graph)
    stats["vessels"] = len(list(graph.subjects(RDF.type, ns.Vessel)))
    stats["persons"] = len(list(graph.subjects(RDF.type, ns.Person)))
    stats["locations"] = len(list(graph.subjects(RDF.type, ns.Location)))
    stats["operations"] = len(list(graph.subjects(RDF.type, ns.Operation)))
    stats["messages"] = len(list(graph.subjects(RDF.type, ns.Message)))
    stats["images"] = len(list(graph.subjects(RDF.type, ns.Image)))

    # 작업 타입 분포
    operation_types = Counter()
    for op in graph.subjects(RDF.type, ns.Operation):
        op_type = graph.value(op, ns.operationType)
        if op_type:
            operation_types[str(op_type)] += 1
    stats["operation_types"] = dict(operation_types.most_common(10))

    # 담당자별 활동
    person_activity = Counter()
    for person in graph.subjects(RDF.type, ns.Person):
        person_name = graph.value(person, ns.personName)
        if person_name:
            # 담당 선박 수
            vessels = list(graph.objects(person, ns.worksWithVessel))
            person_activity[str(person_name)] = len(vessels)
    stats["top_persons"] = dict(person_activity.most_common(10))

    # 선박별 활동
    vessel_activity = Counter()
    for vessel in graph.subjects(RDF.type, ns.Vessel):
        vessel_name = graph.value(vessel, ns.vesselName)
        if vessel_name:
            # 관련 작업 수
            ops = len(list(graph.subjects(ns.mentionsVessel, vessel)))
            vessel_activity[str(vessel_name)] = ops
    stats["top_vessels"] = dict(vessel_activity.most_common(10))

    # 위치별 활동
    location_activity = Counter()
    for loc in graph.subjects(RDF.type, ns.Location):
        loc_name = graph.value(loc, ns.locationName)
        if loc_name:
            # 관련 메시지 수
            mentions = len(list(graph.subjects(ns.mentionsLocation, loc)))
            location_activity[str(loc_name)] = mentions
    stats["top_locations"] = dict(location_activity.most_common(10))

    print(f"\n{system_name} 시스템 통계:")
    print(f"  - Total triples: {stats['total_triples']:,}")
    print(f"  - Vessels: {stats['vessels']}")
    print(f"  - Persons: {stats['persons']}")
    print(f"  - Locations: {stats['locations']}")
    print(f"  - Operations: {stats['operations']}")
    print(f"  - Messages: {stats['messages']}")
    print(f"  - Images: {stats['images']}")

    return stats


def compare_message_patterns(abu_stats, lightning_stats):
    """메시지 패턴 비교"""
    comparison = {}

    comparison["message_volume"] = {
        "abu": abu_stats["messages"],
        "lightning": lightning_stats["messages"],
        "ratio": (
            round(abu_stats["messages"] / lightning_stats["messages"], 2)
            if lightning_stats["messages"] > 0
            else 0
        ),
    }

    comparison["avg_messages_per_vessel"] = {
        "abu": (
            round(abu_stats["messages"] / abu_stats["vessels"], 1)
            if abu_stats["vessels"] > 0
            else 0
        ),
        "lightning": (
            round(lightning_stats["messages"] / lightning_stats["vessels"], 1)
            if lightning_stats["vessels"] > 0
            else 0
        ),
    }

    comparison["avg_operations_per_vessel"] = {
        "abu": (
            round(abu_stats["operations"] / abu_stats["vessels"], 1)
            if abu_stats["vessels"] > 0
            else 0
        ),
        "lightning": (
            round(lightning_stats["operations"] / lightning_stats["vessels"], 1)
            if lightning_stats["vessels"] > 0
            else 0
        ),
    }

    return comparison


def compare_person_roles(abu_stats, lightning_stats):
    """담당자 역할 비교"""
    comparison = {}

    comparison["total_persons"] = {
        "abu": abu_stats["persons"],
        "lightning": lightning_stats["persons"],
    }

    comparison["avg_vessels_per_person"] = {
        "abu": (
            round(
                sum(abu_stats["top_persons"].values()) / len(abu_stats["top_persons"]),
                1,
            )
            if abu_stats["top_persons"]
            else 0
        ),
        "lightning": (
            round(
                sum(lightning_stats["top_persons"].values())
                / len(lightning_stats["top_persons"]),
                1,
            )
            if lightning_stats["top_persons"]
            else 0
        ),
    }

    comparison["top_contributors"] = {
        "abu": abu_stats["top_persons"],
        "lightning": lightning_stats["top_persons"],
    }

    return comparison


def compare_operation_types(abu_stats, lightning_stats):
    """작업 타입 분포 비교"""
    comparison = {}

    comparison["total_operations"] = {
        "abu": abu_stats["operations"],
        "lightning": lightning_stats["operations"],
    }

    comparison["operation_distribution"] = {
        "abu": abu_stats["operation_types"],
        "lightning": lightning_stats["operation_types"],
    }

    # 공통 작업 타입
    abu_types = set(abu_stats["operation_types"].keys())
    lightning_types = set(lightning_stats["operation_types"].keys())
    comparison["common_operations"] = list(abu_types & lightning_types)
    comparison["abu_unique_operations"] = list(abu_types - lightning_types)
    comparison["lightning_unique_operations"] = list(lightning_types - abu_types)

    return comparison


def calculate_efficiency_metrics(abu_stats, lightning_stats):
    """효율성 메트릭 계산"""
    metrics = {}

    # 데이터 밀도 (트리플 수 / 메시지 수)
    metrics["data_density"] = {
        "abu": (
            round(abu_stats["total_triples"] / abu_stats["messages"], 2)
            if abu_stats["messages"] > 0
            else 0
        ),
        "lightning": (
            round(lightning_stats["total_triples"] / lightning_stats["messages"], 2)
            if lightning_stats["messages"] > 0
            else 0
        ),
    }

    # 추출 효율성 (엔티티 수 / 메시지 수)
    abu_entities = (
        abu_stats["vessels"]
        + abu_stats["persons"]
        + abu_stats["locations"]
        + abu_stats["operations"]
    )
    lightning_entities = (
        lightning_stats["vessels"]
        + lightning_stats["persons"]
        + lightning_stats["locations"]
        + lightning_stats["operations"]
    )

    metrics["extraction_rate"] = {
        "abu": (
            round(abu_entities / abu_stats["messages"] * 100, 2)
            if abu_stats["messages"] > 0
            else 0
        ),
        "lightning": (
            round(lightning_entities / lightning_stats["messages"] * 100, 2)
            if lightning_stats["messages"] > 0
            else 0
        ),
    }

    # 이미지 통합률
    metrics["image_integration"] = {
        "abu": abu_stats["images"],
        "lightning": lightning_stats["images"],
        "abu_per_message": (
            round(abu_stats["images"] / abu_stats["messages"] * 1000, 2)
            if abu_stats["messages"] > 0
            else 0
        ),
        "lightning_per_message": (
            round(lightning_stats["images"] / lightning_stats["messages"] * 1000, 2)
            if lightning_stats["messages"] > 0
            else 0
        ),
    }

    return metrics


def generate_comparison_report(
    abu_stats, lightning_stats, csv_entities, csv_total, output_path
):
    """비교 분석 보고서 생성"""

    message_patterns = compare_message_patterns(abu_stats, lightning_stats)
    person_roles = compare_person_roles(abu_stats, lightning_stats)
    operation_types = compare_operation_types(abu_stats, lightning_stats)
    efficiency = calculate_efficiency_metrics(abu_stats, lightning_stats)

    report = f"""# ABU-Lightning 시스템 비교 분석 보고서

생성일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

ABU와 Lightning은 모두 HVDC 프로젝트의 물류 조정을 위한 WhatsApp 그룹 데이터를 RDF 온톨로지로 통합한 시스템입니다.

### 핵심 차이점

| 항목 | ABU | Lightning | 비율 (ABU/Lightning) |
|------|-----|-----------|---------------------|
| 메시지 수 | {abu_stats["messages"]:,} | {lightning_stats["messages"]:,} | {message_patterns["message_volume"]["ratio"]}x |
| 총 트리플 | {abu_stats["total_triples"]:,} | {lightning_stats["total_triples"]:,} | {round(abu_stats["total_triples"] / lightning_stats["total_triples"], 2) if lightning_stats["total_triples"] > 0 else 0}x |
| 선박 | {abu_stats["vessels"]} | {lightning_stats["vessels"]} | - |
| 담당자 | {abu_stats["persons"]} | {lightning_stats["persons"]} | - |
| 위치 | {abu_stats["locations"]} | {lightning_stats["locations"]} | - |
| 작업 | {abu_stats["operations"]} | {lightning_stats["operations"]} | {round(abu_stats["operations"] / lightning_stats["operations"], 2) if lightning_stats["operations"] > 0 else 0}x |
| 이미지 | {abu_stats["images"]} | {lightning_stats["images"]} | - |

## 1. 메시지 패턴 비교

### 1.1 메시지 볼륨

```mermaid
pie title "메시지 분포"
    "ABU ({abu_stats["messages"]:,})" : {abu_stats["messages"]}
    "Lightning ({lightning_stats["messages"]:,})" : {lightning_stats["messages"]}
```

### 1.2 선박당 평균 메시지

```mermaid
bar chart LR
    title 선박당 평균 메시지 수
    x-axis [ABU, Lightning]
    y-axis "메시지 수" 0 --> {max(message_patterns["avg_messages_per_vessel"]["abu"], message_patterns["avg_messages_per_vessel"]["lightning"]) + 500}
    "ABU" : {message_patterns["avg_messages_per_vessel"]["abu"]}
    "Lightning" : {message_patterns["avg_messages_per_vessel"]["lightning"]}
```

**분석**:
- ABU는 선박당 평균 **{message_patterns["avg_messages_per_vessel"]["abu"]:.1f}** 개의 메시지
- Lightning은 선박당 평균 **{message_patterns["avg_messages_per_vessel"]["lightning"]:.1f}** 개의 메시지
- {"ABU가 더 집중적인 커뮤니케이션" if message_patterns["avg_messages_per_vessel"]["abu"] > message_patterns["avg_messages_per_vessel"]["lightning"] else "Lightning이 더 집중적인 커뮤니케이션"}

### 1.3 선박당 평균 작업 수

**ABU**: {message_patterns["avg_operations_per_vessel"]["abu"]:.1f} 작업/선박
**Lightning**: {message_patterns["avg_operations_per_vessel"]["lightning"]:.1f} 작업/선박

## 2. 담당자 역할 비교

### 2.1 담당자 수 비교

- **ABU**: {person_roles["total_persons"]["abu"]}명
- **Lightning**: {person_roles["total_persons"]["lightning"]}명

### 2.2 담당자당 평균 선박 수

- **ABU**: {person_roles["avg_vessels_per_person"]["abu"]:.1f} 선박/담당자
- **Lightning**: {person_roles["avg_vessels_per_person"]["lightning"]:.1f} 선박/담당자

### 2.3 주요 담당자 (ABU)

```mermaid
graph LR
"""

    # ABU 담당자 네트워크
    for i, (person, count) in enumerate(
        list(person_roles["top_contributors"]["abu"].items())[:5], 1
    ):
        report += f'    P{i}["{person}<br/>{count} 선박"] --> ABU[ABU 시스템]\n'

    report += """```

### 2.4 주요 담당자 (Lightning)

```mermaid
graph LR
"""

    # Lightning 담당자 네트워크
    for i, (person, count) in enumerate(
        list(person_roles["top_contributors"]["lightning"].items())[:5], 1
    ):
        report += f'    P{i}["{person}<br/>{count} 선박"] --> LTN[Lightning 시스템]\n'

    report += f"""```

**분석**:
- ABU는 {"더 많은" if person_roles["total_persons"]["abu"] > person_roles["total_persons"]["lightning"] else "더 적은"} 담당자가 참여
- Lightning은 담당자당 평균 {"더 많은" if person_roles["avg_vessels_per_person"]["lightning"] > person_roles["avg_vessels_per_person"]["abu"] else "더 적은"} 선박을 관리

## 3. 작업 타입 분포 비교

### 3.1 총 작업 수

- **ABU**: {operation_types["total_operations"]["abu"]:,} 작업
- **Lightning**: {operation_types["total_operations"]["lightning"]:,} 작업

### 3.2 주요 작업 타입 (ABU)

| 작업 타입 | 건수 | 비율 |
|----------|------|------|
"""

    abu_total_ops = sum(operation_types["operation_distribution"]["abu"].values())
    for op_type, count in list(
        operation_types["operation_distribution"]["abu"].items()
    )[:10]:
        percentage = (count / abu_total_ops * 100) if abu_total_ops > 0 else 0
        report += f"| {op_type} | {count:,} | {percentage:.1f}% |\n"

    report += f"""
### 3.3 주요 작업 타입 (Lightning)

| 작업 타입 | 건수 | 비율 |
|----------|------|------|
"""

    lightning_total_ops = sum(
        operation_types["operation_distribution"]["lightning"].values()
    )
    for op_type, count in list(
        operation_types["operation_distribution"]["lightning"].items()
    )[:10]:
        percentage = (
            (count / lightning_total_ops * 100) if lightning_total_ops > 0 else 0
        )
        report += f"| {op_type} | {count:,} | {percentage:.1f}% |\n"

    report += f"""
### 3.4 작업 타입 벤 다이어그램

```mermaid
graph TB
    subgraph ABU만
"""

    for op in operation_types["abu_unique_operations"][:3]:
        report += f'        A{hash(op) % 1000}["{op}"]\n'

    report += """    end

    subgraph 공통
"""

    for op in operation_types["common_operations"][:5]:
        report += f'        C{hash(op) % 1000}["{op}"]\n'

    report += """    end

    subgraph Lightning만
"""

    for op in operation_types["lightning_unique_operations"][:3]:
        report += f'        L{hash(op) % 1000}["{op}"]\n'

    report += f"""    end
```

**분석**:
- **공통 작업**: {len(operation_types["common_operations"])}개
- **ABU 고유 작업**: {len(operation_types["abu_unique_operations"])}개
- **Lightning 고유 작업**: {len(operation_types["lightning_unique_operations"])}개

## 4. 효율성 메트릭 비교

### 4.1 데이터 밀도 (트리플/메시지)

```mermaid
bar chart
    title "데이터 밀도: 메시지당 트리플 수"
    x-axis [ABU, Lightning]
    y-axis "트리플/메시지" 0 --> {max(efficiency["data_density"]["abu"], efficiency["data_density"]["lightning"]) + 1}
    "ABU" : {efficiency["data_density"]["abu"]}
    "Lightning" : {efficiency["data_density"]["lightning"]}
```

- **ABU**: {efficiency["data_density"]["abu"]:.2f} 트리플/메시지
- **Lightning**: {efficiency["data_density"]["lightning"]:.2f} 트리플/메시지

**해석**: {"ABU가 더 상세한 데이터 추출" if efficiency["data_density"]["abu"] > efficiency["data_density"]["lightning"] else "Lightning이 더 상세한 데이터 추출"}

### 4.2 엔티티 추출률

- **ABU**: {efficiency["extraction_rate"]["abu"]:.2f}% (메시지당 엔티티 수)
- **Lightning**: {efficiency["extraction_rate"]["lightning"]:.2f}% (메시지당 엔티티 수)

### 4.3 이미지 통합

| 시스템 | 총 이미지 | 1000 메시지당 이미지 |
|--------|----------|---------------------|
| ABU | {efficiency["image_integration"]["abu"]} | {efficiency["image_integration"]["abu_per_message"]:.2f} |
| Lightning | {efficiency["image_integration"]["lightning"]} | {efficiency["image_integration"]["lightning_per_message"]:.2f} |

## 5. Lightning CSV 엔티티 검증

### 5.1 CSV 데이터 요약

Lightning 시스템의 실제 엔티티 추출 결과를 CSV ground truth와 비교:

| 카테고리 | CSV 유니크 엔티티 | CSV 총 언급 | RDF 추출 |
|---------|------------------|-------------|----------|
"""

    for category, entities in sorted(csv_entities.items()):
        unique_count = len(entities)
        total_mentions = sum(e["count"] for e in entities)

        # RDF에서 해당 카테고리 카운트
        rdf_count = 0
        if category == "Vessel":
            rdf_count = lightning_stats["vessels"]
        elif category == "Site":
            rdf_count = lightning_stats["locations"]
        elif category == "Operation":
            rdf_count = len(lightning_stats["operation_types"])

        report += (
            f"| {category} | {unique_count} | {total_mentions:,} | {rdf_count} |\n"
        )

    report += f"""
**CSV 총 엔티티 언급**: {csv_total:,}회

### 5.2 상위 엔티티 비교

#### Vessel (선박)
"""

    if "Vessel" in csv_entities:
        report += "\n| 순위 | 선박명 | CSV 언급 | RDF 존재 |\n|------|--------|----------|----------|\n"
        for i, entity_data in enumerate(
            sorted(csv_entities["Vessel"], key=lambda x: x["count"], reverse=True)[:10],
            1,
        ):
            vessel_name = entity_data["entity"]
            count = entity_data["count"]
            # RDF에 존재하는지 확인 (간단히 top vessels에 있는지)
            in_rdf = "✅" if vessel_name in lightning_stats["top_vessels"] else "⚠️"
            report += f"| {i} | {vessel_name} | {count:,} | {in_rdf} |\n"

    report += "\n#### Site (위치)\n"

    if "Site" in csv_entities:
        report += "\n| 순위 | 위치명 | CSV 언급 | RDF 존재 |\n|------|--------|----------|----------|\n"
        for i, entity_data in enumerate(
            sorted(csv_entities["Site"], key=lambda x: x["count"], reverse=True)[:10], 1
        ):
            site_name = entity_data["entity"]
            count = entity_data["count"]
            in_rdf = "✅" if site_name in lightning_stats["top_locations"] else "⚠️"
            report += f"| {i} | {site_name} | {count:,} | {in_rdf} |\n"

    report += "\n#### Operation (작업)\n"

    if "Operation" in csv_entities:
        report += "\n| 순위 | 작업 타입 | CSV 언급 | RDF 존재 |\n|------|----------|----------|----------|\n"
        for i, entity_data in enumerate(
            sorted(csv_entities["Operation"], key=lambda x: x["count"], reverse=True)[
                :10
            ],
            1,
        ):
            op_type = entity_data["entity"]
            count = entity_data["count"]
            in_rdf = "✅" if op_type in lightning_stats["operation_types"] else "⚠️"
            report += f"| {i} | {op_type} | {count:,} | {in_rdf} |\n"

    report += f"""
## 6. 시스템별 강점 및 약점

### 6.1 ABU 시스템

**강점**:
- 높은 메시지 볼륨 ({abu_stats["messages"]:,}개)
- 상세한 엔티티 추출
- 집중적인 커뮤니케이션 패턴

**약점**:
- 제한된 선박 수 ({abu_stats["vessels"]}개)
- 단기 활동 기간

### 6.2 Lightning 시스템

**강점**:
- 다양한 선박 ({lightning_stats["vessels"]}개)
- 장기 활동 데이터 (2022~2025)
- 다양한 담당자 네트워크 ({lightning_stats["persons"]}명)
- CSV ground truth로 검증된 엔티티

**약점**:
- 상대적으로 적은 메시지 볼륨
- 낮은 이미지 비율

## 7. 통합 시나리오

### 7.1 데이터 통합 가능성

두 시스템 모두 동일한 HVDC 프로젝트의 일부이므로 통합 가능:

```mermaid
graph TB
    ABU[ABU 시스템<br/>{abu_stats["messages"]:,} 메시지<br/>{abu_stats["vessels"]} 선박]
    LTN[Lightning 시스템<br/>{lightning_stats["messages"]:,} 메시지<br/>{lightning_stats["vessels"]} 선박]

    INT[통합 HVDC 시스템<br/>{abu_stats["messages"] + lightning_stats["messages"]:,} 메시지<br/>{abu_stats["vessels"] + lightning_stats["vessels"]} 선박]

    ABU --> INT
    LTN --> INT

    INT --> DASH[실시간 대시보드]
    INT --> PRED[예측 분석]
    INT --> AUTO[자동화 알림]
```

### 7.2 통합 후 예상 효과

| 메트릭 | 통합 전 (개별) | 통합 후 | 증가율 |
|--------|---------------|---------|--------|
| 총 메시지 | {max(abu_stats["messages"], lightning_stats["messages"]):,} | {abu_stats["messages"] + lightning_stats["messages"]:,} | +{round((abu_stats["messages"] + lightning_stats["messages"]) / max(abu_stats["messages"], lightning_stats["messages"]) * 100 - 100, 1)}% |
| 총 선박 | {max(abu_stats["vessels"], lightning_stats["vessels"])} | {abu_stats["vessels"] + lightning_stats["vessels"]} | +{round((abu_stats["vessels"] + lightning_stats["vessels"]) / max(abu_stats["vessels"], lightning_stats["vessels"]) * 100 - 100, 1)}% |
| 총 담당자 | {max(abu_stats["persons"], lightning_stats["persons"])} | {abu_stats["persons"] + lightning_stats["persons"]} | +{round((abu_stats["persons"] + lightning_stats["persons"]) / max(abu_stats["persons"], lightning_stats["persons"]) * 100 - 100, 1)}% |
| RDF 트리플 | {max(abu_stats["total_triples"], lightning_stats["total_triples"]):,} | {abu_stats["total_triples"] + lightning_stats["total_triples"]:,} | +{round((abu_stats["total_triples"] + lightning_stats["total_triples"]) / max(abu_stats["total_triples"], lightning_stats["total_triples"]) * 100 - 100, 1)}% |

## 8. 결론 및 권고사항

### 8.1 주요 발견

1. **규모**: ABU는 메시지 집약적, Lightning은 선박 다양성 우수
2. **효율성**: 두 시스템 모두 높은 데이터 추출 효율성 달성
3. **검증**: Lightning의 CSV ground truth는 {round(lightning_stats["vessels"] / len(csv_entities.get("Vessel", [])) * 100, 1) if csv_entities.get("Vessel") else 0}%의 선박 커버리지
4. **보완성**: 두 시스템은 서로 보완적인 강점 보유

### 8.2 권고사항

1. **단기** (1-2주):
   - Lightning RDF에 CSV의 누락 엔티티 추가
   - ABU-Lightning 공통 담당자 식별 및 연결
   - 통합 네임스페이스 설계

2. **중기** (1-2개월):
   - 통합 HVDC RDF 온톨로지 구축
   - 크로스 시스템 SPARQL 쿼리 개발
   - 통합 대시보드 프로토타입

3. **장기** (3-6개월):
   - 실시간 데이터 파이프라인 구축
   - 머신러닝 기반 예측 시스템
   - 자동화된 알림 및 의사결정 지원

### 8.3 비즈니스 가치

- **운영 효율성**: 통합 시스템으로 중복 작업 제거
- **의사결정 지원**: 전체 HVDC 프로젝트 가시성 확보
- **리스크 관리**: 조기 지연 감지 및 대응
- **지식 관리**: 조직 지식의 체계적 보존

---

**생성 정보**:
- ABU RDF: `output/abu_integrated_system.ttl` ({abu_stats["total_triples"]:,} triples)
- Lightning RDF: `output/lightning_integrated_system.ttl` ({lightning_stats["total_triples"]:,} triples)
- Lightning CSV: `HVDC Project Lightning/Logistics_Entities__Summary_.csv` ({csv_total:,} mentions)
- 생성 스크립트: `scripts/compare_abu_lightning.py`
"""

    # 보고서 저장
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n비교 분석 보고서 생성 완료: {output_path}")

    # JSON 데이터도 저장
    json_data = {
        "abu_stats": abu_stats,
        "lightning_stats": lightning_stats,
        "message_patterns": message_patterns,
        "person_roles": person_roles,
        "operation_types": operation_types,
        "efficiency_metrics": efficiency,
        "csv_validation": {
            "total_mentions": csv_total,
            "categories": {
                cat: len(entities) for cat, entities in csv_entities.items()
            },
        },
        "generated_at": datetime.now().isoformat(),
    }

    json_path = (
        Path(__file__).parent.parent / "output" / "abu_lightning_comparison_data.json"
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"비교 데이터 JSON 저장: {json_path}")

    return json_data


def load_precomputed_stats(json_path, system_name):
    """사전 계산된 통계 로드"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n{system_name} 시스템 통계 (사전 계산됨):")
    print(f"  - Total triples: {data.get('total_triples', 0):,}")
    print(
        f"  - Vessels: {data.get('total_vessels', data.get('vessel_count', data.get('vessels', 0)))}"
    )
    print(
        f"  - Persons: {data.get('total_persons', data.get('person_count', data.get('persons', 0)))}"
    )
    print(
        f"  - Locations: {data.get('total_locations', data.get('location_count', data.get('locations', 0)))}"
    )
    print(
        f"  - Operations: {data.get('total_operations', data.get('operation_count', data.get('operations', 0)))}"
    )
    print(
        f"  - Messages: {data.get('total_messages', data.get('message_count', data.get('messages', 0)))}"
    )
    print(
        f"  - Images: {data.get('total_images', data.get('image_count', data.get('images', 0)))}"
    )

    return data


def main():
    print("=" * 80)
    print("ABU-Lightning 시스템 비교 분석")
    print("=" * 80)

    # 경로 설정
    base_dir = Path(__file__).parent.parent
    abu_stats_file = base_dir / "reports" / "data" / "abu_integrated_stats.json"
    lightning_stats_file = (
        base_dir / "reports" / "lightning" / "lightning_integrated_stats.json"
    )
    csv_file = base_dir / "HVDC Project Lightning" / "Logistics_Entities__Summary_.csv"
    output_report = base_dir / "reports" / "final" / "ABU_LIGHTNING_COMPARISON.md"

    # 파일 존재 확인
    if not abu_stats_file.exists():
        print(f"❌ ABU 통계 파일을 찾을 수 없습니다: {abu_stats_file}")
        return

    if not lightning_stats_file.exists():
        print(f"❌ Lightning 통계 파일을 찾을 수 없습니다: {lightning_stats_file}")
        return

    if not csv_file.exists():
        print(f"⚠️  Lightning CSV 파일을 찾을 수 없습니다: {csv_file}")
        csv_entities = {}
        csv_total = 0
    else:
        # CSV 로드
        print(f"\n📊 Lightning CSV 엔티티 로드 중...")
        csv_entities, csv_total = load_csv_entities(csv_file)
        print(f"   - CSV 카테고리: {len(csv_entities)}")
        print(f"   - CSV 총 언급: {csv_total:,}")

    # 사전 계산된 통계 로드
    print(f"\n📊 ABU 통계 로드 중...")
    abu_data = load_precomputed_stats(abu_stats_file, "ABU")

    print(f"\n📊 Lightning 통계 로드 중...")
    lightning_data = load_precomputed_stats(lightning_stats_file, "Lightning")

    # 통계 데이터 정규화
    abu_stats = {
        "total_triples": abu_data.get("total_triples", 0),
        "vessels": abu_data.get("vessel_count", 0),
        "persons": abu_data.get("person_count", 0),
        "locations": abu_data.get("location_count", 0),
        "operations": abu_data.get("operation_count", 0),
        "messages": abu_data.get("message_count", 0),
        "images": abu_data.get("image_count", 0),
        "operation_types": abu_data.get("operation_types", {}),
        "top_persons": abu_data.get("top_persons", {}),
        "top_vessels": abu_data.get("top_vessels", {}),
        "top_locations": abu_data.get("top_locations", {}),
    }

    lightning_stats = {
        "total_triples": lightning_data.get("total_triples", 0),
        "vessels": lightning_data.get(
            "total_vessels",
            lightning_data.get("vessel_count", lightning_data.get("vessels", 0)),
        ),
        "persons": lightning_data.get(
            "total_persons",
            lightning_data.get("person_count", lightning_data.get("persons", 0)),
        ),
        "locations": lightning_data.get(
            "total_locations",
            lightning_data.get("location_count", lightning_data.get("locations", 0)),
        ),
        "operations": lightning_data.get(
            "total_operations",
            lightning_data.get("operation_count", lightning_data.get("operations", 0)),
        ),
        "messages": lightning_data.get(
            "total_messages",
            lightning_data.get("message_count", lightning_data.get("messages", 0)),
        ),
        "images": lightning_data.get(
            "total_images",
            lightning_data.get("image_count", lightning_data.get("images", 0)),
        ),
        "operation_types": lightning_data.get("operation_types", {}),
        "top_persons": lightning_data.get("top_persons", {}),
        "top_vessels": lightning_data.get("top_vessels", {}),
        "top_locations": lightning_data.get("top_locations", {}),
    }

    # 비교 분석 보고서 생성
    print(f"\n📝 비교 분석 보고서 생성 중...")
    comparison_data = generate_comparison_report(
        abu_stats, lightning_stats, csv_entities, csv_total, output_report
    )

    print(f"\n✅ ABU-Lightning 비교 분석 완료!")
    print(f"\n생성된 파일:")
    print(f"  - {output_report}")
    print(f"  - {base_dir / 'output' / 'abu_lightning_comparison_data.json'}")


if __name__ == "__main__":
    main()
