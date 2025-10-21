#!/usr/bin/env python3
"""
WhatsApp 이미지 메타데이터를 기존 ABU RDF 그래프에 통합
"""

import sys
import json
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


def load_existing_rdf():
    """기존 ABU RDF 그래프 로드"""
    rdf_file = Path("output/abu_logistics_data.ttl")
    if not rdf_file.exists():
        print("❌ 기존 ABU RDF 파일을 찾을 수 없습니다.")
        return None

    g = Graph()
    g.parse(rdf_file, format="turtle")
    print(f"✅ 기존 RDF 그래프 로드: {len(g)}개 트리플")
    return g


def load_image_analysis():
    """이미지 분석 데이터 로드"""
    analysis_file = Path("reports/whatsapp_images_analysis.json")
    if not analysis_file.exists():
        print("❌ 이미지 분석 파일을 찾을 수 없습니다.")
        return None

    with open(analysis_file, "r", encoding="utf-8") as f:
        return json.load(f)


def create_image_uri(filename, ns_dict):
    """이미지 URI 생성"""
    # IMG-20251019-WA0028.jpg -> WhatsAppImage/20251019-WA0028
    clean_name = filename.replace("IMG-", "").replace(".jpg", "")
    return ns_dict["hvdci"][f"WhatsAppImage/{clean_name}"]


def extract_date_from_filename(filename):
    """파일명에서 날짜 추출"""
    try:
        if filename.startswith("IMG-") and "-WA" in filename:
            date_part = filename.split("-")[1]  # 20251019
            if len(date_part) == 8:
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                return f"{year}-{month}-{day}"
    except:
        pass
    return None


def integrate_images_to_rdf(graph, image_data, ns_dict):
    """이미지 데이터를 RDF 그래프에 통합"""
    print("🖼️ WhatsApp 이미지를 RDF에 통합 중...")

    integrated_count = 0

    for img in image_data:
        filename = img["filename"]
        image_uri = create_image_uri(filename, ns_dict)

        # 이미지 엔티티 생성
        graph.add((image_uri, RDF.type, ns_dict["abu"]["WhatsAppImage"]))
        graph.add((image_uri, ns_dict["abu"]["fileName"], Literal(filename)))
        graph.add(
            (
                image_uri,
                ns_dict["abu"]["fileSize"],
                Literal(img["file_size"], datatype=XSD.integer),
            )
        )

        # 날짜 정보 추가
        extracted_date = extract_date_from_filename(filename)
        if extracted_date:
            graph.add(
                (
                    image_uri,
                    ns_dict["abu"]["captureDate"],
                    Literal(extracted_date, datatype=XSD.date),
                )
            )

        # 생성/수정 시간 추가
        created_time = img["created_date"]
        graph.add(
            (
                image_uri,
                ns_dict["abu"]["createdAt"],
                Literal(created_time, datatype=XSD.dateTime),
            )
        )

        # 파일 경로 추가
        graph.add((image_uri, ns_dict["abu"]["filePath"], Literal(img["file_path"])))

        # 이미지 타입 추가
        graph.add((image_uri, ns_dict["abu"]["imageType"], Literal("WhatsApp_Image")))

        integrated_count += 1

    print(f"✅ {integrated_count}개 이미지가 RDF에 통합되었습니다.")
    return graph


def create_image_message_links(graph, ns_dict):
    """이미지와 메시지 간 연결 생성 (추정)"""
    print("🔗 이미지-메시지 연결 생성 중...")

    # 기존 메시지 엔티티 찾기
    message_uris = list(graph.subjects(RDF.type, ns_dict["abu"]["WhatsAppMessage"]))
    image_uris = list(graph.subjects(RDF.type, ns_dict["abu"]["WhatsAppImage"]))

    print(f"  - 기존 메시지: {len(message_uris)}개")
    print(f"  - 이미지: {len(image_uris)}개")

    # 간단한 연결 로직: 날짜 기반 매칭
    links_created = 0
    for image_uri in image_uris:
        # 이미지의 날짜 정보 가져오기
        image_dates = list(graph.objects(image_uri, ns_dict["abu"]["captureDate"]))
        if not image_dates:
            continue

        image_date = str(image_dates[0])

        # 같은 날짜의 메시지 찾기
        for message_uri in message_uris:
            message_dates = list(
                graph.objects(message_uri, ns_dict["abu"]["timestamp"])
            )
            if not message_dates:
                continue

            message_date = str(message_dates[0])
            if image_date in message_date or message_date in image_date:
                # 연결 생성
                graph.add((message_uri, ns_dict["abu"]["hasAttachment"], image_uri))
                links_created += 1
                break

    print(f"✅ {links_created}개의 이미지-메시지 연결이 생성되었습니다.")
    return graph


def save_integrated_rdf(graph, output_file):
    """통합된 RDF 그래프 저장"""
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(graph.serialize(format="turtle"))

    return output_path


def generate_integration_report(graph, image_count, output_file, ns_dict):
    """통합 보고서 생성"""
    report = {
        "integration_timestamp": datetime.now().isoformat(),
        "rdf_statistics": {
            "total_triples": len(graph),
            "image_entities": len(
                list(graph.subjects(RDF.type, ns_dict["abu"]["WhatsAppImage"]))
            ),
            "message_entities": len(
                list(graph.subjects(RDF.type, ns_dict["abu"]["WhatsAppMessage"]))
            ),
            "lpo_entities": len(
                list(graph.subjects(RDF.type, ns_dict["lpo"]["LocalPurchaseOrder"]))
            ),
            "shipment_entities": len(
                list(graph.subjects(RDF.type, ns_dict["abu"]["AbuDhabiShipment"]))
            ),
        },
        "integration_summary": {
            "images_integrated": image_count,
            "output_file": str(output_file),
            "status": "SUCCESS",
        },
    }

    # 보고서 저장
    report_file = Path("reports/whatsapp_images_integration_report.md")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# WhatsApp 이미지 RDF 통합 보고서\n\n")
        f.write(f"**통합 시간**: {report['integration_timestamp']}\n\n")
        f.write(f"## 통합 결과\n")
        f.write(f"- 통합된 이미지: {image_count}개\n")
        f.write(f"- 총 RDF 트리플: {report['rdf_statistics']['total_triples']}개\n")
        f.write(f"- 이미지 엔티티: {report['rdf_statistics']['image_entities']}개\n")
        f.write(f"- 메시지 엔티티: {report['rdf_statistics']['message_entities']}개\n")
        f.write(f"- LPO 엔티티: {report['rdf_statistics']['lpo_entities']}개\n")
        f.write(f"- 선박 엔티티: {report['rdf_statistics']['shipment_entities']}개\n\n")
        f.write(f"## 출력 파일\n")
        f.write(f"- 통합 RDF: {output_file}\n\n")
        f.write(f"## 상태: {report['integration_summary']['status']}\n")

    return report


def main():
    """메인 실행 함수"""
    print("🔄 WhatsApp 이미지를 ABU RDF에 통합 시작...")

    # 네임스페이스 설정
    ns_dict = setup_namespaces()

    # 기존 RDF 그래프 로드
    print("📊 기존 ABU RDF 그래프 로드 중...")
    graph = load_existing_rdf()
    if not graph:
        return

    # 이미지 분석 데이터 로드
    print("🖼️ 이미지 분석 데이터 로드 중...")
    image_analysis = load_image_analysis()
    if not image_analysis:
        return

    image_data = image_analysis["image_list"]
    print(f"✅ {len(image_data)}개의 이미지 데이터를 로드했습니다.")

    # 이미지 통합
    graph = integrate_images_to_rdf(graph, image_data, ns_dict)

    # 이미지-메시지 연결 생성
    graph = create_image_message_links(graph, ns_dict)

    # 통합된 RDF 저장
    output_file = Path("output/abu_with_images.ttl")
    print(f"💾 통합 RDF 저장 중: {output_file}")
    saved_path = save_integrated_rdf(graph, output_file)

    # 통합 보고서 생성
    print("📋 통합 보고서 생성 중...")
    report = generate_integration_report(graph, len(image_data), saved_path, ns_dict)

    print(f"✅ WhatsApp 이미지 통합 완료!")
    print(f"  - 출력 파일: {saved_path}")
    print(f"  - 총 트리플: {len(graph)}개")
    print(f"  - 통합된 이미지: {len(image_data)}개")
    print(f"  - 보고서: reports/whatsapp_images_integration_report.md")


if __name__ == "__main__":
    main()
