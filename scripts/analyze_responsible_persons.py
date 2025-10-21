#!/usr/bin/env python3
"""
ABU 담당자 분석 스크립트
RDF에서 담당자 정보를 추출하고 분석하여 통계를 생성합니다.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
from collections import Counter, defaultdict

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


def setup_namespaces() -> Dict[str, Namespace]:
    """네임스페이스 설정"""
    return {
        "abu": Namespace("https://abu-dhabi.example.org/ns#"),
        "abui": Namespace("https://abu-dhabi.example.org/id/"),
        "xsd": XSD,
        "rdf": RDF,
        "rdfs": RDFS,
    }


def extract_responsible_persons(
    g: Graph, ns_dict: Dict[str, Namespace]
) -> Dict[str, Any]:
    """담당자 정보 추출 및 분석"""
    print("[INFO] 담당자 정보 추출 중...")

    # 담당자별 통계
    person_stats = defaultdict(
        lambda: {
            "shipments": 0,
            "containers": 0,
            "deliveries": 0,
            "vessels": [],
            "locations": [],
            "keywords": [],
            "timestamps": [],
        }
    )

    # Shipment 분석
    print("[INFO] Shipment 담당자 분석 중...")
    for s, p, o in g.triples((None, RDF.type, ns_dict["abu"]["AbuDhabiShipment"])):
        # 담당자 추출
        for _, _, person in g.triples((s, ns_dict["abu"]["responsiblePerson"], None)):
            person_name = str(person)
            person_stats[person_name]["shipments"] += 1

            # 선박명 추출
            for _, _, ship_name in g.triples((s, ns_dict["abu"]["shipName"], None)):
                if str(ship_name) not in person_stats[person_name]["vessels"]:
                    person_stats[person_name]["vessels"].append(str(ship_name))

            # 위치 추출
            for _, _, location in g.triples(
                (s, ns_dict["abu"]["currentLocation"], None)
            ):
                if str(location) not in person_stats[person_name]["locations"]:
                    person_stats[person_name]["locations"].append(str(location))

            # 타임스탬프 추출
            for _, _, timestamp in g.triples((s, ns_dict["abu"]["timestamp"], None)):
                person_stats[person_name]["timestamps"].append(str(timestamp))

    # Container 분석
    print("[INFO] Container 담당자 분석 중...")
    for s, p, o in g.triples((None, RDF.type, ns_dict["abu"]["AbuDhabiContainer"])):
        for _, _, person in g.triples((s, ns_dict["abu"]["responsiblePerson"], None)):
            person_name = str(person)
            person_stats[person_name]["containers"] += 1

            # 타임스탬프 추출
            for _, _, timestamp in g.triples((s, ns_dict["abu"]["timestamp"], None)):
                person_stats[person_name]["timestamps"].append(str(timestamp))

    # Delivery 분석
    print("[INFO] Delivery 담당자 분석 중...")
    for s, p, o in g.triples((None, RDF.type, ns_dict["abu"]["AbuDhabiDelivery"])):
        for _, _, person in g.triples((s, ns_dict["abu"]["responsiblePerson"], None)):
            person_name = str(person)
            person_stats[person_name]["deliveries"] += 1

            # 타임스탬프 추출
            for _, _, timestamp in g.triples((s, ns_dict["abu"]["timestamp"], None)):
                person_stats[person_name]["timestamps"].append(str(timestamp))

    return dict(person_stats)


def analyze_time_patterns(person_stats: Dict[str, Any]) -> Dict[str, Any]:
    """시간대별 활동 패턴 분석"""
    print("[INFO] 시간대별 활동 패턴 분석 중...")

    time_analysis = {}

    for person, stats in person_stats.items():
        if not stats["timestamps"]:
            continue

        # 시간대별 활동 빈도
        hour_counts = Counter()
        for timestamp in stats["timestamps"]:
            try:
                # ISO 형식에서 시간 추출
                if "T" in timestamp:
                    hour = timestamp.split("T")[1].split(":")[0]
                    hour_counts[hour] += 1
            except:
                continue

        time_analysis[person] = {
            "total_activities": len(stats["timestamps"]),
            "hourly_distribution": dict(hour_counts.most_common()),
            "peak_hour": hour_counts.most_common(1)[0][0] if hour_counts else None,
            "activity_span": len(hour_counts),
        }

    return time_analysis


def generate_person_summary(
    person_stats: Dict[str, Any], time_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """담당자 요약 통계 생성"""
    print("[INFO] 담당자 요약 통계 생성 중...")

    # System 제외 실제 담당자만 필터링
    actual_persons = {k: v for k, v in person_stats.items() if k != "System"}

    summary = {
        "total_persons": len(actual_persons),
        "total_entities": sum(
            v["shipments"] + v["containers"] + v["deliveries"]
            for v in actual_persons.values()
        ),
        "person_details": {},
    }

    for person, stats in actual_persons.items():
        time_info = time_analysis.get(person, {})

        summary["person_details"][person] = {
            "shipments": stats["shipments"],
            "containers": stats["containers"],
            "deliveries": stats["deliveries"],
            "total_entities": stats["shipments"]
            + stats["containers"]
            + stats["deliveries"],
            "vessels": list(stats["vessels"]),
            "locations": list(stats["locations"]),
            "top_vessels": list(stats["vessels"])[:5],  # 상위 5개
            "top_locations": list(stats["locations"])[:5],  # 상위 5개
            "peak_hour": time_info.get("peak_hour"),
            "activity_span": time_info.get("activity_span", 0),
            "total_activities": time_info.get("total_activities", 0),
        }

    # 상위 담당자 정렬 (총 엔티티 수 기준)
    sorted_persons = sorted(
        actual_persons.items(),
        key=lambda x: x[1]["shipments"] + x[1]["containers"] + x[1]["deliveries"],
        reverse=True,
    )

    summary["top_persons"] = [
        {
            "person": person,
            "total_entities": stats["shipments"]
            + stats["containers"]
            + stats["deliveries"],
            "shipments": stats["shipments"],
            "containers": stats["containers"],
            "deliveries": stats["deliveries"],
        }
        for person, stats in sorted_persons[:10]
    ]

    return summary


def save_analysis_results(analysis: Dict[str, Any], output_file: str):
    """분석 결과를 JSON 파일로 저장"""
    Path("reports").mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 분석 결과 저장: {output_file}")


def main():
    """메인 함수"""
    print("=" * 60)
    print("ABU 담당자 분석 스크립트")
    print("=" * 60)

    # 파일 경로 설정
    rdf_file = "output/abu_logistics_data.ttl"
    output_file = "reports/abu_responsible_persons_analysis.json"

    # 1. RDF 데이터 로드
    print("\n1. RDF 데이터 로드")
    g = load_rdf_data(rdf_file)
    if g is None:
        return

    ns_dict = setup_namespaces()

    # 2. 담당자 정보 추출
    print("\n2. 담당자 정보 추출")
    person_stats = extract_responsible_persons(g, ns_dict)

    # 3. 시간대별 패턴 분석
    print("\n3. 시간대별 패턴 분석")
    time_analysis = analyze_time_patterns(person_stats)

    # 4. 요약 통계 생성
    print("\n4. 요약 통계 생성")
    summary = generate_person_summary(person_stats, time_analysis)

    # 5. 결과 저장
    print("\n5. 결과 저장")
    analysis_results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "rdf_file": rdf_file,
            "total_triples": len(g),
        },
        "summary": summary,
        "detailed_stats": person_stats,
        "time_analysis": time_analysis,
    }

    save_analysis_results(analysis_results, output_file)

    # 6. 결과 출력
    print("\n[SUCCESS] 담당자 분석 완료")
    print(f"  - 총 담당자: {summary['total_persons']}명")
    print(f"  - 총 엔티티: {summary['total_entities']}개")
    print(f"  - 출력 파일: {output_file}")

    print("\n상위 담당자 (총 엔티티 수 기준):")
    for i, person in enumerate(summary["top_persons"][:5], 1):
        print(
            f"  {i}. {person['person']}: {person['total_entities']}개 "
            f"(선박 {person['shipments']}, 컨테이너 {person['containers']}, 배송 {person['deliveries']})"
        )

    return analysis_results


if __name__ == "__main__":
    main()
