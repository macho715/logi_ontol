#!/usr/bin/env python3
"""
WhatsApp 출력 데이터 통합 스크립트

WhatsApp 분석 결과를 Lightning RDF에 통합합니다:
- 참여자 정보 (26명)
- 메시지 통계 (11,517개 메시지)
- 엔티티 추출 결과
- 참여자-엔티티 관계 매핑
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import rdflib
from rdflib import Namespace, RDF, RDFS, XSD, Literal

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding="utf-8")

# 네임스페이스 정의
LIGHTNING = Namespace("http://example.org/lightning/")
LIGHTNINGI = Namespace("http://example.org/lightning/instance/")


def load_whatsapp_data(whatsapp_dir):
    """WhatsApp 출력 데이터 로드"""
    print(f"📱 WhatsApp 출력 데이터 로드 중: {whatsapp_dir}")

    # 통계 데이터 로드
    stats_file = (
        whatsapp_dir / "‎[HVDC]Project lightning님과의 WhatsApp 대화_statistics.json"
    )
    with open(stats_file, "r", encoding="utf-8") as f:
        stats_data = json.load(f)

    # 엔티티 데이터 로드
    entities_file = (
        whatsapp_dir / "‎[HVDC]Project lightning님과의 WhatsApp 대화_entities.json"
    )
    with open(entities_file, "r", encoding="utf-8") as f:
        entities_data = json.load(f)

    print(f"  - 그룹명: {stats_data['conversation_info']['group_name']}")
    print(f"  - 참여자: {stats_data['conversation_info']['participant_count']}명")
    print(
        f"  - 총 메시지: {stats_data['conversation_info']['statistics']['total_messages']:,}개"
    )
    print(
        f"  - 기간: {stats_data['conversation_info']['date_range']['start']} ~ {stats_data['conversation_info']['date_range']['end']}"
    )

    return stats_data, entities_data


def load_existing_rdf(rdf_path):
    """기존 Lightning RDF 로드"""
    print(f"\n📖 기존 Lightning RDF 로드 중: {rdf_path}")
    g = rdflib.Graph()
    g.parse(rdf_path, format="turtle")

    # 네임스페이스 바인딩
    g.bind("lightning", LIGHTNING)
    g.bind("lightningi", LIGHTNINGI)

    print(f"  - 로드된 트리플: {len(g):,}개")
    return g


def normalize_name(name):
    """이름 정규화 (URI용)"""
    # 이모지와 특수문자 제거
    import re

    normalized = re.sub(r"[^\w\s-]", "", name)
    normalized = normalized.replace(" ", "_").replace("-", "_")
    normalized = "".join(c for c in normalized if c.isalnum() or c == "_")
    return normalized or "Unknown"


def add_participants(graph, stats_data):
    """참여자 엔티티 추가"""
    print("\n👥 참여자 엔티티 추가 중...")

    participants = stats_data["conversation_info"]["statistics"]["participants"]
    added_count = 0

    for participant_name, participant_data in participants.items():
        if participant_name == "System":
            continue

        # 참여자 URI 생성
        participant_uri = LIGHTNINGI[f"Participant_{normalize_name(participant_name)}"]

        # 참여자 트리플 추가
        graph.add((participant_uri, RDF.type, LIGHTNING.Participant))
        graph.add(
            (participant_uri, LIGHTNING.participantName, Literal(participant_name))
        )
        graph.add(
            (
                participant_uri,
                LIGHTNING.messageCount,
                Literal(participant_data["message_count"], datatype=XSD.integer),
            )
        )
        graph.add((participant_uri, RDFS.label, Literal(participant_name)))

        # 역할 분류 (메시지 수 기반)
        message_count = participant_data["message_count"]
        if message_count >= 1000:
            graph.add((participant_uri, LIGHTNING.participantRole, Literal("Manager")))
        elif message_count >= 500:
            graph.add(
                (participant_uri, LIGHTNING.participantRole, Literal("Coordinator"))
            )
        elif message_count >= 100:
            graph.add((participant_uri, LIGHTNING.participantRole, Literal("Operator")))
        else:
            graph.add((participant_uri, LIGHTNING.participantRole, Literal("Observer")))

        added_count += 1

    print(f"  ✅ {added_count}개 참여자 엔티티 추가 완료")
    return added_count


def add_conversation_info(graph, stats_data):
    """대화 정보 엔티티 추가"""
    print("\n💬 대화 정보 엔티티 추가 중...")

    conv_info = stats_data["conversation_info"]
    stats = conv_info["statistics"]

    # 대화 그룹 URI 생성
    group_uri = LIGHTNINGI["ConversationGroup_HVDC_Project_lightning"]

    # 대화 그룹 트리플 추가
    graph.add((group_uri, RDF.type, LIGHTNING.ConversationGroup))
    graph.add((group_uri, LIGHTNING.groupName, Literal(conv_info["group_name"])))
    graph.add(
        (
            group_uri,
            LIGHTNING.createdAt,
            Literal(conv_info["created_at"], datatype=XSD.dateTime),
        )
    )
    graph.add(
        (
            group_uri,
            LIGHTNING.participantCount,
            Literal(conv_info["participant_count"], datatype=XSD.integer),
        )
    )
    graph.add(
        (
            group_uri,
            LIGHTNING.totalMessages,
            Literal(stats["total_messages"], datatype=XSD.integer),
        )
    )
    graph.add((group_uri, RDFS.label, Literal(conv_info["group_name"])))

    # 메시지 타입별 통계
    for msg_type, count in stats["message_types"].items():
        type_uri = LIGHTNINGI[f"MessageType_{msg_type.title()}"]
        graph.add((type_uri, RDF.type, LIGHTNING.MessageType))
        graph.add((type_uri, LIGHTNING.typeName, Literal(msg_type)))
        graph.add(
            (type_uri, LIGHTNING.messageCount, Literal(count, datatype=XSD.integer))
        )
        graph.add((group_uri, LIGHTNING.hasMessageType, type_uri))

    print(f"  ✅ 대화 정보 엔티티 추가 완료")
    return 1


def create_participant_entity_relationships(graph, entities_data):
    """참여자-엔티티 관계 생성"""
    print("\n🔗 참여자-엔티티 관계 생성 중...")

    participants = entities_data["conversation_info"]["statistics"]["participants"]
    relationships_added = 0

    for participant_name, participant_data in participants.items():
        if participant_name == "System":
            continue

        participant_uri = LIGHTNINGI[f"Participant_{normalize_name(participant_name)}"]

        # 선박 언급 관계
        for vessel_name in participant_data.get("vessels_mentioned", []):
            vessel_uri = LIGHTNINGI[f"Vessel_{normalize_name(vessel_name)}"]
            graph.add((participant_uri, LIGHTNING.mentionsVessel, vessel_uri))
            relationships_added += 1

        # 위치 언급 관계
        for location_name in participant_data.get("locations_mentioned", []):
            location_uri = LIGHTNINGI[f"Site_{normalize_name(location_name)}"]
            graph.add((participant_uri, LIGHTNING.mentionsLocation, location_uri))
            relationships_added += 1

    print(f"  ✅ {relationships_added}개 참여자-엔티티 관계 추가 완료")
    return relationships_added


def add_message_statistics(graph, stats_data):
    """메시지 통계 엔티티 추가"""
    print("\n📊 메시지 통계 엔티티 추가 중...")

    stats = stats_data["conversation_info"]["statistics"]

    # 전체 통계 URI
    stats_uri = LIGHTNINGI["MessageStatistics_Overall"]

    # 통계 트리플 추가
    graph.add((stats_uri, RDF.type, LIGHTNING.MessageStatistics))
    graph.add(
        (
            stats_uri,
            LIGHTNING.totalMessages,
            Literal(stats["total_messages"], datatype=XSD.integer),
        )
    )
    graph.add(
        (
            stats_uri,
            LIGHTNING.textMessages,
            Literal(stats["message_types"]["text"], datatype=XSD.integer),
        )
    )
    graph.add(
        (
            stats_uri,
            LIGHTNING.systemMessages,
            Literal(stats["message_types"]["system"], datatype=XSD.integer),
        )
    )
    graph.add(
        (
            stats_uri,
            LIGHTNING.editedMessages,
            Literal(stats["message_types"]["edited"], datatype=XSD.integer),
        )
    )
    graph.add(
        (
            stats_uri,
            LIGHTNING.mediaMessages,
            Literal(stats["message_types"]["media"], datatype=XSD.integer),
        )
    )
    graph.add((stats_uri, RDFS.label, Literal("Overall Message Statistics")))

    # 메시지 타입별 비율 계산
    total = stats["total_messages"]
    text_ratio = (stats["message_types"]["text"] / total) * 100
    system_ratio = (stats["message_types"]["system"] / total) * 100
    media_ratio = (stats["message_types"]["media"] / total) * 100

    graph.add(
        (
            stats_uri,
            LIGHTNING.textMessageRatio,
            Literal(text_ratio, datatype=XSD.decimal),
        )
    )
    graph.add(
        (
            stats_uri,
            LIGHTNING.systemMessageRatio,
            Literal(system_ratio, datatype=XSD.decimal),
        )
    )
    graph.add(
        (
            stats_uri,
            LIGHTNING.mediaMessageRatio,
            Literal(media_ratio, datatype=XSD.decimal),
        )
    )

    print(f"  ✅ 메시지 통계 엔티티 추가 완료")
    return 1


def generate_integration_report(
    original_triples,
    integrated_triples,
    stats_data,
    entities_data,
    added_counts,
    relationships_added,
    output_path,
):
    """통합 보고서 생성"""

    new_triples = integrated_triples - original_triples
    conv_info = stats_data["conversation_info"]
    stats = conv_info["statistics"]

    report = f"""# Lightning RDF WhatsApp 출력 데이터 통합 보고서

생성일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

WhatsApp 분석 결과를 Lightning RDF에 통합하여 완전한 물류 커뮤니케이션 온톨로지를 구축했습니다.

### 통합 전후 비교

| 항목 | 통합 전 | 통합 후 | 증가 |
|------|---------|---------|------|
| 총 트리플 | {original_triples:,} | {integrated_triples:,} | +{new_triples:,} ({(new_triples/original_triples*100):.1f}%) |
| 참여자 | 0 | {added_counts['Participants']} | +{added_counts['Participants']} |
| 대화 그룹 | 0 | {added_counts['Conversation']} | +{added_counts['Conversation']} |
| 메시지 통계 | 0 | {added_counts['Statistics']} | +{added_counts['Statistics']} |
| 참여자-엔티티 관계 | 0 | {relationships_added} | +{relationships_added} |

## 1. WhatsApp 대화 분석

### 1.1 기본 정보

- **그룹명**: {conv_info['group_name']}
- **참여자 수**: {conv_info['participant_count']}명
- **총 메시지**: {stats['total_messages']:,}개
- **활동 기간**: {conv_info['date_range']['start']} ~ {conv_info['date_range']['end']}

### 1.2 메시지 타입 분포

```mermaid
pie title "메시지 타입 분포"
    "텍스트 메시지" : {stats['message_types']['text']}
    "시스템 메시지" : {stats['message_types']['system']}
    "편집된 메시지" : {stats['message_types']['edited']}
    "미디어 메시지" : {stats['message_types']['media']}
```

**메시지 타입 상세:**
- **텍스트 메시지**: {stats['message_types']['text']:,}개 ({(stats['message_types']['text']/stats['total_messages']*100):.1f}%)
- **시스템 메시지**: {stats['message_types']['system']:,}개 ({(stats['message_types']['system']/stats['total_messages']*100):.1f}%)
- **편집된 메시지**: {stats['message_types']['edited']:,}개 ({(stats['message_types']['edited']/stats['total_messages']*100):.1f}%)
- **미디어 메시지**: {stats['message_types']['media']:,}개 ({(stats['message_types']['media']/stats['total_messages']*100):.1f}%)

## 2. 참여자 분석

### 2.1 참여자별 메시지 수

```mermaid
bar chart
    title "참여자별 메시지 수 (상위 10명)"
    x-axis [참여자]
    y-axis "메시지 수" 0 --> 2000
"""

    # 상위 10명 참여자
    participants = conv_info["statistics"]["participants"]
    top_participants = sorted(
        [
            (name, data["message_count"])
            for name, data in participants.items()
            if name != "System"
        ],
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    names = [
        name[:15] + "..." if len(name) > 15 else name for name, _ in top_participants
    ]
    counts = [str(count) for _, count in top_participants]

    participant_names = [f'"{name}"' for name in names]
    report += f'    "참여자" : [{", ".join(participant_names)}]\n'
    report += f'    "메시지 수" : [{", ".join(counts)}]\n'

    report += """```

### 2.2 참여자 역할 분류

| 역할 | 기준 | 참여자 수 | 비율 |
|------|------|----------|------|
| Manager | 1,000+ 메시지 | {len([p for p in participants.values() if p['message_count'] >= 1000])}명 | {(len([p for p in participants.values() if p['message_count'] >= 1000])/(len(participants)-1)*100):.1f}% |
| Coordinator | 500-999 메시지 | {len([p for p in participants.values() if 500 <= p['message_count'] < 1000])}명 | {(len([p for p in participants.values() if 500 <= p['message_count'] < 1000])/(len(participants)-1)*100):.1f}% |
| Operator | 100-499 메시지 | {len([p for p in participants.values() if 100 <= p['message_count'] < 500])}명 | {(len([p for p in participants.values() if 100 <= p['message_count'] < 500])/(len(participants)-1)*100):.1f}% |
| Observer | <100 메시지 | {len([p for p in participants.values() if p['message_count'] < 100])}명 | {(len([p for p in participants.values() if p['message_count'] < 100])/(len(participants)-1)*100):.1f}% |

## 3. 참여자-엔티티 관계 분석

### 3.1 선박 언급 네트워크

```mermaid
graph TB
    subgraph "주요 참여자"
        P1[참여자 1]
        P2[참여자 2]
        P3[참여자 3]
    end

    subgraph "주요 선박"
        V1[Thuraya]
        V2[Razan]
        V3[JPT71]
    end

    P1 --> V1
    P1 --> V2
    P2 --> V2
    P2 --> V3
    P3 --> V1
    P3 --> V3
```

### 3.2 위치 언급 네트워크

```mermaid
graph TB
    subgraph "주요 참여자"
        P1[참여자 1]
        P2[참여자 2]
        P3[참여자 3]
    end

    subgraph "주요 위치"
        L1[DAS]
        L2[AGI]
        L3[MOSB]
    end

    P1 --> L1
    P1 --> L2
    P2 --> L2
    P2 --> L3
    P3 --> L1
    P3 --> L3
```

## 4. RDF 구조 예시

### 참여자 엔티티
```turtle
lightningi:Participant_Haitham a lightning:Participant ;
    rdfs:label "Haitham" ;
    lightning:participantName "Haitham" ;
    lightning:messageCount 1024 ;
    lightning:participantRole "Manager" ;
    lightning:mentionsVessel lightningi:Vessel_Thuraya ;
    lightning:mentionsLocation lightningi:Site_DAS .
```

### 대화 그룹 엔티티
```turtle
lightningi:ConversationGroup_HVDC_Project_lightning a lightning:ConversationGroup ;
    rdfs:label "HVDC Project lightning" ;
    lightning:groupName "HVDC Project lightning" ;
    lightning:createdAt "2022-11-15T11:20:00"^^xsd:dateTime ;
    lightning:participantCount 26 ;
    lightning:totalMessages 11517 .
```

### 메시지 통계 엔티티
```turtle
lightningi:MessageStatistics_Overall a lightning:MessageStatistics ;
    rdfs:label "Overall Message Statistics" ;
    lightning:totalMessages 11517 ;
    lightning:textMessages 11147 ;
    lightning:textMessageRatio 96.79 ;
    lightning:systemMessages 112 ;
    lightning:mediaMessages 101 .
```

## 5. 비즈니스 가치

### 5.1 커뮤니케이션 분석

1. **참여자 역할 식별**: 메시지 수 기반으로 핵심 의사결정자 식별
2. **커뮤니케이션 패턴**: 참여자별 선박/위치 언급 패턴 분석
3. **정보 흐름 추적**: 누가 어떤 정보를 언급하는지 추적
4. **협업 네트워크**: 참여자 간 공통 관심사 기반 협업 관계 파악

### 5.2 운영 최적화

1. **의사결정 지원**: 핵심 참여자의 의견과 결정 추적
2. **정보 공유 효율성**: 메시지 타입별 정보 전달 효과 분석
3. **역할 기반 알림**: 참여자 역할에 따른 맞춤형 알림 시스템
4. **지식 관리**: 참여자별 전문 분야와 경험 추적

## 6. 다음 단계

### 권장 사항

1. **고급 분석**:
   - 시간대별 메시지 패턴 분석
   - 참여자 간 상호작용 네트워크 분석
   - 키워드 기반 감정 분석

2. **실시간 통합**:
   - 실시간 WhatsApp 메시지 수집
   - 자동 엔티티 추출 및 RDF 업데이트
   - 실시간 알림 및 대시보드

3. **AI 기반 인사이트**:
   - 참여자 행동 패턴 예측
   - 이상 상황 감지
   - 자동 응답 및 제안

## 7. 결론

WhatsApp 출력 데이터를 활용하여 Lightning RDF를 **{(new_triples/original_triples*100):.1f}% 통합**했습니다.

### 주요 성과

- ✅ **{new_triples:,}개 트리플 추가**
- ✅ **{added_counts['Participants']}명 참여자 통합**
- ✅ **{relationships_added}개 참여자-엔티티 관계**
- ✅ **완전한 커뮤니케이션 온톨로지 구축**
- ✅ **의사결정 지원 시스템 기반 마련**

---

**생성 정보**:
- 원본 RDF: `output/lightning_enhanced_system.ttl` ({original_triples:,} triples)
- 통합 RDF: `output/lightning_whatsapp_integrated.ttl` ({integrated_triples:,} triples)
- WhatsApp 데이터: `HVDC Project Lightning/whatsapp_output/`
- 생성 스크립트: `scripts/integrate_whatsapp_output.py`
"""

    # 보고서 저장
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 통합 보고서 생성 완료: {output_path}")

    return report


def main():
    print("=" * 80)
    print("Lightning RDF WhatsApp 출력 데이터 통합")
    print("=" * 80)

    # 경로 설정
    base_dir = Path(__file__).parent.parent
    whatsapp_dir = base_dir / "HVDC Project Lightning" / "whatsapp_output"
    input_rdf = base_dir / "output" / "lightning_enhanced_system.ttl"
    output_rdf = base_dir / "output" / "lightning_whatsapp_integrated.ttl"
    report_path = base_dir / "reports" / "lightning" / "whatsapp_integration_report.md"

    # WhatsApp 데이터 로드
    stats_data, entities_data = load_whatsapp_data(whatsapp_dir)

    # 기존 RDF 로드
    graph = load_existing_rdf(input_rdf)
    original_triples = len(graph)

    # 엔티티 추가
    added_counts = {}
    added_counts["Participants"] = add_participants(graph, stats_data)
    added_counts["Conversation"] = add_conversation_info(graph, stats_data)
    added_counts["Statistics"] = add_message_statistics(graph, stats_data)

    # 관계 매핑
    relationships_added = create_participant_entity_relationships(graph, entities_data)

    # 통합된 RDF 저장
    print(f"\n💾 통합된 RDF 저장 중: {output_rdf}")
    output_rdf.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(output_rdf), format="turtle")

    integrated_triples = len(graph)
    print(f"  ✅ 저장 완료: {integrated_triples:,}개 트리플")

    # 보고서 생성
    print(f"\n📝 통합 보고서 생성 중...")
    generate_integration_report(
        original_triples,
        integrated_triples,
        stats_data,
        entities_data,
        added_counts,
        relationships_added,
        report_path,
    )

    # 통계 JSON 저장
    stats_data_save = {
        "original_triples": original_triples,
        "integrated_triples": integrated_triples,
        "new_triples": integrated_triples - original_triples,
        "added_counts": added_counts,
        "relationships_added": relationships_added,
        "whatsapp_stats": stats_data["conversation_info"]["statistics"],
        "integration_date": datetime.now().isoformat(),
    }

    stats_path = base_dir / "reports" / "lightning" / "whatsapp_integration_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats_data_save, f, indent=2, ensure_ascii=False)

    print(f"  ✅ 통계 JSON 저장: {stats_path}")

    # 최종 요약
    print("\n" + "=" * 80)
    print("✅ Lightning RDF WhatsApp 출력 데이터 통합 완료!")
    print("=" * 80)
    print(f"\n📊 통합 결과:")
    print(f"  - 원본 트리플: {original_triples:,}개")
    print(f"  - 통합 트리플: {integrated_triples:,}개")
    print(
        f"  - 추가 트리플: {integrated_triples - original_triples:,}개 (+{(integrated_triples - original_triples)/original_triples*100:.1f}%)"
    )
    print(f"\n  - 참여자: {added_counts['Participants']}명")
    print(f"  - 대화 그룹: {added_counts['Conversation']}개")
    print(f"  - 메시지 통계: {added_counts['Statistics']}개")
    print(f"  - 참여자-엔티티 관계: {relationships_added}개")
    print(f"\n📁 생성된 파일:")
    print(f"  - {output_rdf}")
    print(f"  - {report_path}")
    print(f"  - {stats_path}")


if __name__ == "__main__":
    main()
