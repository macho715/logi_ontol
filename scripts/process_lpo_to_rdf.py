#!/usr/bin/env python3
"""
ABU WhatsApp 대화에서 추출한 LPO 데이터를 RDF로 변환
"""

import sys
import json
import yaml
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


def load_mapping_rules():
    """LPO 매핑 규칙 로드"""
    rules_file = Path("logiontology/configs/lpo_mapping_rules.yaml")
    with open(rules_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_vendor_name(vendor_name):
    """공급업체 이름 정규화"""
    # 특수문자 제거 및 공백을 언더스코어로 변경
    normalized = re.sub(r"[^\w\s]", "", vendor_name)
    normalized = re.sub(r"\s+", "_", normalized.strip())
    return normalized


def normalize_location_name(location_name):
    """위치 이름 정규화"""
    if not location_name:
        return "Unknown_Location"
    return location_name.strip()


def convert_whatsapp_date(date_str):
    """WhatsApp 날짜 형식을 ISO 형식으로 변환"""
    if not date_str:
        return "1900-01-01"

    try:
        # 24/8/21 형식을 2024-08-21로 변환
        date_obj = datetime.strptime(date_str, "%y/%m/%d")
        return date_obj.strftime("%Y-%m-%d")
    except:
        return "1900-01-01"


def categorize_lpo_item(description):
    """LPO 항목 카테고리 분류"""
    category_keywords = {
        "Stationary": ["stationary", "office", "paper", "cup", "tissue"],
        "Electrical": ["elec", "wire", "cable", "electrical", "power"],
        "Construction": ["upvc", "steel", "conduit", "scaffolding", "kerb"],
        "Maintenance": ["maintenance", "filter", "grease", "chemical"],
        "Furniture": ["furniture", "bed", "cabinet", "shelving"],
        "Kitchen": ["kitchen", "dish", "pantry", "food"],
        "Safety": ["protective", "sling", "webbing", "rope"],
        "General": ["general", "consumable", "items"],
    }

    description_lower = description.lower()
    for category, keywords in category_keywords.items():
        if any(keyword in description_lower for keyword in keywords):
            return category
    return "Other"


def create_lpo_uri(lpo_number, ns_dict):
    """LPO URI 생성"""
    return ns_dict["hvdci"][f"LPO/{lpo_number}"]


def create_vendor_uri(vendor_name, ns_dict):
    """공급업체 URI 생성"""
    normalized_name = normalize_vendor_name(vendor_name)
    return ns_dict["hvdci"][f"Organization/{normalized_name}"]


def create_location_uri(location_name, ns_dict):
    """위치 URI 생성"""
    normalized_name = normalize_location_name(location_name)
    return ns_dict["hvdci"][f"Location/{normalized_name}"]


def process_lpo_data(lpo_data, mapping_rules, ns_dict):
    """LPO 데이터를 RDF로 변환"""
    g = Graph()

    # 네임스페이스 바인딩
    for prefix, namespace in ns_dict.items():
        g.bind(prefix, namespace)

    # 처리된 엔티티 추적
    processed_lpos = set()
    processed_vendors = set()
    processed_locations = set()

    for item in lpo_data:
        lpo_number = item["lpo_number"]

        # LPO 엔티티 생성 (중복 방지)
        if lpo_number not in processed_lpos:
            lpo_uri = create_lpo_uri(lpo_number, ns_dict)

            # LPO 타입 설정
            g.add((lpo_uri, RDF.type, ns_dict["lpo"]["LocalPurchaseOrder"]))

            # LPO 속성 추가
            g.add((lpo_uri, ns_dict["lpo"]["lpoNumber"], Literal(lpo_number)))
            g.add(
                (lpo_uri, ns_dict["lpo"]["description"], Literal(item["description"]))
            )
            g.add((lpo_uri, ns_dict["lpo"]["vendorName"], Literal(item["vendor"])))

            # 날짜 변환 및 추가
            iso_date = convert_whatsapp_date(item["date"])
            g.add(
                (
                    lpo_uri,
                    ns_dict["lpo"]["issueDate"],
                    Literal(iso_date, datatype=XSD.date),
                )
            )

            # 위치 추가
            if item["location"]:
                g.add(
                    (
                        lpo_uri,
                        ns_dict["lpo"]["deliveryLocation"],
                        Literal(item["location"]),
                    )
                )

            # 카테고리 분류 및 추가
            category = categorize_lpo_item(item["description"])
            g.add((lpo_uri, ns_dict["lpo"]["category"], Literal(category)))

            # 기본 상태 설정
            g.add((lpo_uri, ns_dict["lpo"]["status"], Literal("Issued")))
            g.add((lpo_uri, ns_dict["lpo"]["currency"], Literal("AED")))

            processed_lpos.add(lpo_number)

        # 공급업체 엔티티 생성 (중복 방지)
        vendor_name = item["vendor"]
        if vendor_name not in processed_vendors:
            vendor_uri = create_vendor_uri(vendor_name, ns_dict)

            g.add((vendor_uri, RDF.type, ns_dict["org"]["Organization"]))
            g.add((vendor_uri, ns_dict["org"]["name"], Literal(vendor_name)))
            g.add((vendor_uri, RDFS.label, Literal(vendor_name)))

            processed_vendors.add(vendor_name)

        # 위치 엔티티 생성 (중복 방지)
        location_name = item["location"]
        if location_name and location_name not in processed_locations:
            location_uri = create_location_uri(location_name, ns_dict)

            g.add((location_uri, RDF.type, ns_dict["abu"]["AbuDhabiLocation"]))
            g.add(
                (location_uri, ns_dict["abu"]["locationName"], Literal(location_name))
            )
            g.add((location_uri, RDFS.label, Literal(location_name)))

            processed_locations.add(location_name)

        # 관계 설정
        lpo_uri = create_lpo_uri(lpo_number, ns_dict)
        vendor_uri = create_vendor_uri(vendor_name, ns_dict)

        # LPO → Vendor 관계
        g.add((lpo_uri, ns_dict["lpo"]["hasVendor"], vendor_uri))

        # LPO → Location 관계
        if location_name:
            location_uri = create_location_uri(location_name, ns_dict)
            g.add((lpo_uri, ns_dict["lpo"]["hasDeliveryLocation"], location_uri))

    return g


def save_rdf_graph(graph, output_file):
    """RDF 그래프를 TTL 파일로 저장"""
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(graph.serialize(format="turtle"))

    return output_path


def generate_processing_report(lpo_data, graph, output_file):
    """처리 보고서 생성"""
    report = {
        "processing_timestamp": datetime.now().isoformat(),
        "input_statistics": {
            "total_lpo_entries": len(lpo_data),
            "unique_lpo_numbers": len(set(item["lpo_number"] for item in lpo_data)),
            "unique_vendors": len(set(item["vendor"] for item in lpo_data)),
            "unique_locations": len(
                set(item["location"] for item in lpo_data if item["location"])
            ),
        },
        "rdf_statistics": {
            "total_triples": len(graph),
            "lpo_entities": len(list(graph.subjects(RDF.type, None))),
            "namespaces_used": list(graph.namespaces()),
        },
        "output_file": str(output_file),
        "processing_status": "SUCCESS",
    }

    # 보고서 저장
    report_file = Path("reports/lpo_processing_report.md")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# LPO RDF 변환 보고서\n\n")
        f.write(f"**처리 시간**: {report['processing_timestamp']}\n\n")
        f.write(f"## 입력 데이터 통계\n")
        f.write(f"- 총 LPO 항목: {report['input_statistics']['total_lpo_entries']}개\n")
        f.write(
            f"- 고유 LPO 번호: {report['input_statistics']['unique_lpo_numbers']}개\n"
        )
        f.write(f"- 고유 공급업체: {report['input_statistics']['unique_vendors']}개\n")
        f.write(f"- 고유 위치: {report['input_statistics']['unique_locations']}개\n\n")
        f.write(f"## RDF 변환 결과\n")
        f.write(f"- 총 트리플: {report['rdf_statistics']['total_triples']}개\n")
        f.write(f"- LPO 엔티티: {report['rdf_statistics']['lpo_entities']}개\n")
        f.write(f"- 출력 파일: {report['output_file']}\n\n")
        f.write(f"## 처리 상태: {report['processing_status']}\n")

    return report


def main():
    """메인 실행 함수"""
    print("🔄 ABU LPO 데이터를 RDF로 변환 시작...")

    # 입력 파일 확인
    lpo_analysis_file = Path("reports/abu_lpo_analysis.json")
    if not lpo_analysis_file.exists():
        print(
            "❌ LPO 분석 파일을 찾을 수 없습니다. 먼저 analyze_lpo_data.py를 실행하세요."
        )
        return

    # LPO 데이터 로드
    print("📊 LPO 분석 데이터 로드 중...")
    with open(lpo_analysis_file, "r", encoding="utf-8") as f:
        analysis_data = json.load(f)

    lpo_data = analysis_data["lpo_list"]
    print(f"✅ {len(lpo_data)}개의 LPO 항목을 로드했습니다.")

    # 매핑 규칙 로드
    print("📋 매핑 규칙 로드 중...")
    mapping_rules = load_mapping_rules()

    # 네임스페이스 설정
    print("🔗 RDF 네임스페이스 설정 중...")
    ns_dict = setup_namespaces()

    # RDF 변환
    print("🔄 RDF 변환 중...")
    graph = process_lpo_data(lpo_data, mapping_rules, ns_dict)

    # 결과 저장
    output_file = Path("output/abu_lpo_data.ttl")
    print(f"💾 RDF 파일 저장 중: {output_file}")
    saved_path = save_rdf_graph(graph, output_file)

    # 처리 보고서 생성
    print("📋 처리 보고서 생성 중...")
    report = generate_processing_report(lpo_data, graph, saved_path)

    print(f"✅ LPO RDF 변환 완료!")
    print(f"  - 출력 파일: {saved_path}")
    print(f"  - 총 트리플: {len(graph)}개")
    print(f"  - LPO 엔티티: {len(list(graph.subjects(RDF.type, None)))}개")
    print(f"  - 보고서: reports/lpo_processing_report.md")


if __name__ == "__main__":
    main()
