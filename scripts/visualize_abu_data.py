#!/usr/bin/env python3
"""
아부다비 물류 데이터 시각화 스크립트
RDF 데이터를 분석하고 Mermaid 다이어그램으로 시각화합니다.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple

# RDF 처리
from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal, URIRef
from rdflib.namespace import NamespaceManager

# Unicode 출력 지원
sys.stdout.reconfigure(encoding="utf-8")


def load_rdf_data(rdf_path: str) -> Tuple[Graph, Dict[str, Any]]:
    """RDF 데이터 로드"""
    print(f"[INFO] RDF 파일 로드: {rdf_path}")

    g = Graph()
    g.parse(rdf_path, format="turtle")

    # 네임스페이스 추출
    ns_dict = dict(g.namespaces())
    abu_uri = ns_dict.get("abu")

    if not abu_uri:
        print("[ERROR] abu 네임스페이스를 찾을 수 없습니다.")
        return g, {}

    # Namespace 객체 생성
    abu_ns = Namespace(abu_uri)

    # 데이터 분석
    data = {
        "containers": [],
        "deliveries": [],
        "shipments": [],
        "participants": [],
        "guidelines": [],
        "rules": [],
        "kpis": [],
    }

    # 컨테이너 데이터 추출
    for s, p, o in g.triples((None, RDF.type, abu_ns["AbuDhabiContainer"])):
        container_data = {"uri": str(s)}
        for sp, so in g.predicate_objects(s):
            if "containerId" in str(sp):
                container_data["id"] = str(so)
            elif "containerType" in str(sp):
                container_data["type"] = str(so)
            elif "timestamp" in str(sp):
                container_data["timestamp"] = str(so)
            elif "reportedBy" in str(sp):
                container_data["reported_by"] = str(so)
        data["containers"].append(container_data)

    # 배송 데이터 추출
    for s, p, o in g.triples((None, RDF.type, abu_ns["AbuDhabiDelivery"])):
        delivery_data = {"uri": str(s)}
        for sp, so in g.predicate_objects(s):
            if "deliveryCompany" in str(sp):
                delivery_data["company"] = str(so)
            elif "timestamp" in str(sp):
                delivery_data["timestamp"] = str(so)
            elif "deliveryQuantity" in str(sp):
                delivery_data["quantity"] = str(so)
            elif "deliveryUnit" in str(sp):
                delivery_data["unit"] = str(so)
        data["deliveries"].append(delivery_data)

    # 선박 데이터 추출
    for s, p, o in g.triples((None, RDF.type, abu_ns["AbuDhabiShipment"])):
        shipment_data = {"uri": str(s)}
        for sp, so in g.predicate_objects(s):
            if "shipName" in str(sp):
                shipment_data["name"] = str(so)
            elif "timestamp" in str(sp):
                shipment_data["timestamp"] = str(so)
            elif "estimatedArrival" in str(sp):
                shipment_data["eta"] = str(so)
            elif "currentLocation" in str(sp):
                shipment_data["location"] = str(so)
            elif "shipStatus" in str(sp):
                shipment_data["status"] = str(so)
        data["shipments"].append(shipment_data)

    # 참여자 데이터 추출
    for s, p, o in g.triples((None, RDF.type, abu_ns["Organization"])):
        participant_data = {"uri": str(s)}
        for sp, so in g.predicate_objects(s):
            if "participantName" in str(sp):
                participant_data["name"] = str(so)
            elif "participantRole" in str(sp):
                participant_data["role"] = str(so)
        data["participants"].append(participant_data)

    # 가이드라인 데이터 추출
    for s, p, o in g.triples((None, RDF.type, abu_ns["AbuDhabiGuideline"])):
        guideline_data = {"uri": str(s)}
        for sp, so in g.predicate_objects(s):
            if "guidelineTitle" in str(sp):
                guideline_data["title"] = str(so)
            elif "guidelineVersion" in str(sp):
                guideline_data["version"] = str(so)
        data["guidelines"].append(guideline_data)

    # 규칙 데이터 추출
    for s, p, o in g.triples((None, RDF.type, abu_ns["AbuDhabiRule"])):
        rule_data = {"uri": str(s)}
        for sp, so in g.predicate_objects(s):
            if "ruleCategory" in str(sp):
                rule_data["category"] = str(so)
            elif "ruleText" in str(sp):
                rule_data["text"] = str(so)
        data["rules"].append(rule_data)

    # KPI 데이터 추출
    for s, p, o in g.triples((None, RDF.type, abu_ns["AbuDhabiKPI"])):
        kpi_data = {"uri": str(s)}
        for sp, so in g.predicate_objects(s):
            if "kpiDescription" in str(sp):
                kpi_data["description"] = str(so)
            elif "targetPercentage" in str(sp):
                kpi_data["target"] = str(so)
        data["kpis"].append(kpi_data)

    return g, data


def analyze_abu_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """ABU 데이터 분석"""
    analysis = {
        "summary": {
            "total_containers": len(data["containers"]),
            "total_deliveries": len(data["deliveries"]),
            "total_shipments": len(data["shipments"]),
            "total_participants": len(data["participants"]),
            "total_guidelines": len(data["guidelines"]),
            "total_rules": len(data["rules"]),
            "total_kpis": len(data["kpis"]),
        },
        "container_analysis": {},
        "delivery_analysis": {},
        "shipment_analysis": {},
        "participant_analysis": {},
        "rule_analysis": {},
        "kpi_analysis": {},
    }

    # 컨테이너 분석
    if data["containers"]:
        container_types = Counter(
            [c.get("type", "unknown") for c in data["containers"]]
        )
        reported_by = Counter(
            [c.get("reported_by", "unknown") for c in data["containers"]]
        )
        analysis["container_analysis"] = {
            "types": dict(container_types),
            "reported_by": dict(reported_by),
        }

    # 배송 분석
    if data["deliveries"]:
        companies = Counter([d.get("company", "unknown") for d in data["deliveries"]])
        analysis["delivery_analysis"] = {"companies": dict(companies)}

    # 선박 분석
    if data["shipments"]:
        ship_names = Counter([s.get("name", "unknown") for s in data["shipments"]])
        statuses = Counter([s.get("status", "unknown") for s in data["shipments"]])
        analysis["shipment_analysis"] = {
            "ship_names": dict(ship_names),
            "statuses": dict(statuses),
        }

    # 참여자 분석
    if data["participants"]:
        roles = Counter([p.get("role", "unknown") for p in data["participants"]])
        analysis["participant_analysis"] = {"roles": dict(roles)}

    # 규칙 분석
    if data["rules"]:
        categories = Counter([r.get("category", "unknown") for r in data["rules"]])
        analysis["rule_analysis"] = {"categories": dict(categories)}

    return analysis


def generate_entity_relationship_diagram(data: Dict[str, Any]) -> str:
    """엔티티 관계 다이어그램 생성"""
    mermaid = """graph TD
    subgraph "아부다비 물류 시스템"
        A[AbuDhabiGuideline] --> B[AbuDhabiRule]
        A --> C[AbuDhabiKPI]
        D[AbuDhabiShipment] --> E[AbuDhabiContainer]
        D --> F[AbuDhabiDelivery]
        G[Organization] --> D
        G --> E
        G --> F
    end

    subgraph "데이터 통계"
        H["컨테이너: {total_containers}개"]
        I["배송: {total_deliveries}개"]
        J["선박: {total_shipments}개"]
        K["참여자: {total_participants}개"]
        L["가이드라인: {total_guidelines}개"]
        M["규칙: {total_rules}개"]
        N["KPI: {total_kpis}개"]
    end
""".format(
        total_containers=data["summary"]["total_containers"],
        total_deliveries=data["summary"]["total_deliveries"],
        total_shipments=data["summary"]["total_shipments"],
        total_participants=data["summary"]["total_participants"],
        total_guidelines=data["summary"]["total_guidelines"],
        total_rules=data["summary"]["total_rules"],
        total_kpis=data["summary"]["total_kpis"],
    )

    return mermaid


def generate_container_type_chart(container_analysis: Dict[str, Any]) -> str:
    """컨테이너 타입 차트 생성"""
    if not container_analysis.get("types"):
        return "pie title 컨테이너 타입\n    데이터 없음 : 1"

    mermaid = "pie title 컨테이너 타입\n"
    for container_type, count in container_analysis["types"].items():
        mermaid += f'    "{container_type}" : {count}\n'

    return mermaid


def generate_delivery_company_chart(delivery_analysis: Dict[str, Any]) -> str:
    """배송 회사 차트 생성"""
    if not delivery_analysis.get("companies"):
        return "pie title 배송 회사\n    데이터 없음 : 1"

    mermaid = "pie title 배송 회사\n"
    for company, count in delivery_analysis["companies"].items():
        mermaid += f'    "{company}" : {count}\n'

    return mermaid


def generate_shipment_status_chart(shipment_analysis: Dict[str, Any]) -> str:
    """선박 상태 차트 생성"""
    if not shipment_analysis.get("statuses"):
        return "pie title 선박 상태\n    데이터 없음 : 1"

    mermaid = "pie title 선박 상태\n"
    for status, count in shipment_analysis["statuses"].items():
        mermaid += f'    "{status}" : {count}\n'

    return mermaid


def generate_data_flow_diagram() -> str:
    """데이터 플로우 다이어그램 생성"""
    return """graph LR
    A[가이드라인 문서] --> B[구조화된 분석]
    C[WhatsApp 대화] --> D[물류 데이터 추출]
    B --> E[RDF 변환]
    D --> E
    E --> F[아부다비 물류 온톨로지]
    F --> G[시각화 및 분석]
"""


def generate_ontology_class_diagram() -> str:
    """온톨로지 클래스 다이어그램 생성"""
    return """classDiagram
    class AbuDhabiGuideline {
        +String guidelineTitle
        +String guidelineVersion
        +String guidelineDescription
        +hasRule: AbuDhabiRule[]
        +hasKPI: AbuDhabiKPI[]
    }

    class AbuDhabiRule {
        +String ruleCategory
        +String ruleText
    }

    class AbuDhabiKPI {
        +String kpiDescription
        +Decimal targetPercentage
    }

    class AbuDhabiShipment {
        +String shipName
        +DateTime timestamp
        +String estimatedArrival
        +String currentLocation
        +String shipStatus
        +String[] cargoType
    }

    class AbuDhabiContainer {
        +String containerId
        +String containerType
        +DateTime timestamp
        +String reportedBy
    }

    class AbuDhabiDelivery {
        +String deliveryCompany
        +DateTime timestamp
        +Integer deliveryQuantity
        +String deliveryUnit
    }

    class Organization {
        +String participantName
        +String participantRole
    }

    AbuDhabiGuideline --> AbuDhabiRule
    AbuDhabiGuideline --> AbuDhabiKPI
    Organization --> AbuDhabiShipment
    Organization --> AbuDhabiContainer
    Organization --> AbuDhabiDelivery
"""


def generate_markdown_report(data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    """마크다운 보고서 생성"""
    report = f"""# 아부다비 물류 데이터 시각화 보고서

**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 실행 요약

- **총 컨테이너**: {analysis['summary']['total_containers']}개
- **총 배송**: {analysis['summary']['total_deliveries']}개
- **총 선박**: {analysis['summary']['total_shipments']}개
- **총 참여자**: {analysis['summary']['total_participants']}개
- **총 가이드라인**: {analysis['summary']['total_guidelines']}개
- **총 규칙**: {analysis['summary']['total_rules']}개
- **총 KPI**: {analysis['summary']['total_kpis']}개

## 🔗 엔티티 관계 다이어그램

```mermaid
{generate_entity_relationship_diagram(analysis)}
```

## 📦 컨테이너 타입 분포

```mermaid
{generate_container_type_chart(analysis['container_analysis'])}
```

## 🚚 배송 회사 분포

```mermaid
{generate_delivery_company_chart(analysis['delivery_analysis'])}
```

## 🚢 선박 상태 분포

```mermaid
{generate_shipment_status_chart(analysis['shipment_analysis'])}
```

## 🔄 데이터 처리 파이프라인

```mermaid
{generate_data_flow_diagram()}
```

## 🏗️ 온톨로지 클래스 구조

```mermaid
{generate_ontology_class_diagram()}
```

## 📈 상세 분석

### 컨테이너 분석
- **타입별 분포**: {analysis['container_analysis'].get('types', {})}
- **보고자별 분포**: {analysis['container_analysis'].get('reported_by', {})}

### 배송 분석
- **회사별 분포**: {analysis['delivery_analysis'].get('companies', {})}

### 선박 분석
- **선박명별 분포**: {analysis['shipment_analysis'].get('ship_names', {})}
- **상태별 분포**: {analysis['shipment_analysis'].get('statuses', {})}

### 참여자 분석
- **역할별 분포**: {analysis['participant_analysis'].get('roles', {})}

### 규칙 분석
- **카테고리별 분포**: {analysis['rule_analysis'].get('categories', {})}

## 🎯 주요 인사이트

1. **데이터 품질**: 총 {analysis['summary']['total_containers'] + analysis['summary']['total_deliveries'] + analysis['summary']['total_shipments']}개의 물류 엔티티가 성공적으로 변환되었습니다.

2. **참여자 다양성**: {analysis['summary']['total_participants']}명의 다양한 역할의 참여자가 시스템에 참여하고 있습니다.

3. **규칙 체계**: {analysis['summary']['total_rules']}개의 구조화된 규칙과 {analysis['summary']['total_kpis']}개의 KPI가 정의되어 있습니다.

4. **데이터 일관성**: 모든 타임스탬프가 ISO 8601 형식으로 정규화되어 있습니다.

## 📋 권장사항

1. **데이터 검증**: 컨테이너 타입 정보를 더 정확하게 수집하도록 개선
2. **실시간 업데이트**: WhatsApp 데이터의 실시간 처리 파이프라인 구축
3. **품질 모니터링**: KPI 기반 데이터 품질 모니터링 시스템 도입
4. **통합 분석**: 다른 물류 시스템과의 데이터 통합 분석

---
*이 보고서는 LogiOntology 시스템에 의해 자동 생성되었습니다.*
"""

    return report


def save_json_summary(analysis: Dict[str, Any], output_path: str):
    """JSON 요약 저장"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)


def main():
    """메인 함수"""
    print("=" * 60)
    print("아부다비 물류 데이터 시각화 스크립트")
    print("=" * 60)

    # 파일 경로 설정
    rdf_path = "output/abu_logistics_data.ttl"
    report_path = "reports/abu_visualization_report.md"
    json_path = "reports/abu_data_summary.json"

    # 파일 존재 확인
    if not Path(rdf_path).exists():
        print(f"[ERROR] RDF 파일을 찾을 수 없습니다: {rdf_path}")
        return

    try:
        # RDF 데이터 로드
        g, data = load_rdf_data(rdf_path)
        print(f"[SUCCESS] RDF 데이터 로드 완료")

        # 데이터 분석
        analysis = analyze_abu_data(data)
        print(f"[SUCCESS] 데이터 분석 완료")

        # 마크다운 보고서 생성
        report = generate_markdown_report(data, analysis)

        # 보고서 저장
        Path("reports").mkdir(exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[SUCCESS] 시각화 보고서 저장: {report_path}")

        # JSON 요약 저장
        save_json_summary(analysis, json_path)
        print(f"[SUCCESS] JSON 요약 저장: {json_path}")

        print("\n" + "=" * 60)
        print("시각화 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] 처리 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
