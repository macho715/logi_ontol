#!/usr/bin/env python3
"""
아부다비 WhatsApp 대화 분석 스크립트
WhatsApp 대화 내용에서 물류 관련 데이터를 추출하고 구조화합니다.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict

# Unicode 출력 지원
sys.stdout.reconfigure(encoding="utf-8")


def parse_whatsapp_message(line: str) -> Dict[str, Any]:
    """WhatsApp 메시지 파싱"""
    # 날짜/시간 패턴: 24/8/21 PM 1:28
    date_pattern = r"(\d{1,2}/\d{1,2}/\d{2,4})\s+(AM|PM)\s+(\d{1,2}:\d{2})"
    match = re.match(date_pattern, line)

    if not match:
        return None

    date_str, period, time_str = match.groups()
    # 시간을 24시간 형식으로 변환
    hour, minute = map(int, time_str.split(":"))
    if period == "PM" and hour != 12:
        hour += 12
    elif period == "AM" and hour == 12:
        hour = 0

    # 나머지 부분에서 발신자와 메시지 추출
    remaining = line[len(match.group(0)) :].strip()
    if " - " in remaining:
        sender, message = remaining.split(" - ", 1)
        sender = sender.strip()
        message = message.strip()
    else:
        sender = "System"
        message = remaining

    return {
        "date": date_str,
        "time": f"{hour:02d}:{minute:02d}",
        "sender": sender,
        "message": message,
        "timestamp": f"{date_str} {hour:02d}:{minute:02d}",
    }


def extract_responsible_person(message: str) -> str:
    """메시지에서 담당자 이름 추출 (예: '- Haitham:' -> 'Haitham')"""
    match = re.match(r"^-\s*([^:]+):", message)
    if match:
        return match.group(1).strip()
    return "System"


def extract_logistics_keywords(message: str) -> List[str]:
    """물류 관련 키워드 추출"""
    keywords = []

    # 선박 관련
    ship_patterns = [
        r"\b(JPt\d+|JPT\d+|Buahra|Thuraya|Tamarah|Yeam|Taibah)\b",
        r"\b(LCT|RORO|FB|A-Frame)\b",
        r"\b(casting off|underway|eta|arrived|departure)\b",
    ]

    # 화물 관련
    cargo_patterns = [
        r"\b(container|cntr|40ft|20ft|OT|ST|Flat rack)\b",
        r"\b(aggregate|food delivery|drinking water|skip bins)\b",
        r"\b(offloading|loading|delivery|collection)\b",
    ]

    # 위치 관련
    location_patterns = [
        r"\b(DAS|AGI|MOSB|MW4|AGU|Umm ALanbar|Musaffah)\b",
        r"\b(Al Jaber|Al Ain|buskeen)\b",
    ]

    # 장비 관련
    equipment_patterns = [
        r"\b(crane|forklift|FLIFT|sling|webbing|spreader)\b",
        r"\b(TPI|TUV|HCS|choker)\b",
    ]

    # 문서 관련
    document_patterns = [
        r"\b(BL|LPO|LOTO|exit pass|gatepass|EID|CICPA)\b",
        r"\b(dispensation|approval|document)\b",
    ]

    all_patterns = (
        ship_patterns
        + cargo_patterns
        + location_patterns
        + equipment_patterns
        + document_patterns
    )

    for pattern in all_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        keywords.extend(matches)

    return list(set(keywords))


def extract_shipment_data(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """선박 및 화물 데이터 추출"""
    shipments = []
    current_shipment = None

    for msg in messages:
        if not msg:
            continue

        message = msg["message"]
        keywords = extract_logistics_keywords(message)

        # 선박 이름이 포함된 메시지
        ship_match = re.search(
            r"\b(JPt\d+|JPT\d+|Buahra|Thuraya|Tamarah|Yeam|Taibah)\b",
            message,
            re.IGNORECASE,
        )
        if ship_match:
            ship_name = ship_match.group(1)

            # ETA 정보 추출
            eta_match = re.search(r"eta\s+([^.\n]+)", message, re.IGNORECASE)
            eta = eta_match.group(1).strip() if eta_match else None

            # 위치 정보 추출
            location_match = re.search(
                r"\b(DAS|AGI|MOSB|MW4|AGU|Umm ALanbar|Musaffah|Al Jaber|Al Ain|buskeen)\b",
                message,
                re.IGNORECASE,
            )
            location = location_match.group(1) if location_match else None

            # 화물 정보 추출
            cargo_info = []
            if "food delivery" in message.lower():
                cargo_info.append("Food Delivery")
            if "aggregate" in message.lower():
                cargo_info.append("Aggregate")
            if "drinking water" in message.lower():
                cargo_info.append("Drinking Water")
            if "skip bins" in message.lower():
                cargo_info.append("Skip Bins")

            shipment = {
                "ship_name": ship_name,
                "timestamp": msg["timestamp"],
                "sender": msg["sender"],
                "responsible_person": extract_responsible_person(message),
                "eta": eta,
                "location": location,
                "cargo": cargo_info,
                "status": (
                    "underway"
                    if "underway" in message.lower()
                    else "at anchor" if "anchor" in message.lower() else "unknown"
                ),
                "message": message,
            }

            shipments.append(shipment)

    return shipments


def extract_container_data(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """컨테이너 데이터 추출"""
    containers = []

    for msg in messages:
        if not msg:
            continue

        message = msg["message"]

        # 컨테이너 번호 패턴
        container_patterns = [
            r"\b(TR\s*\d+)\b",  # TR 3155 형태
            r"\b(\d+FT\s+OT\s+[A-Z]+\s+\d+)\b",  # 40FT OT ENSU 7000087 형태
            r"\b([A-Z]{4}\d{7})\b",  # 4글자+7숫자 형태
        ]

        for pattern in container_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                container = {
                    "container_id": match.strip(),
                    "timestamp": msg["timestamp"],
                    "sender": msg["sender"],
                    "responsible_person": extract_responsible_person(message),
                    "message": message,
                    "type": (
                        "40FT"
                        if "40FT" in match
                        else "20FT" if "20FT" in match else "unknown"
                    ),
                }
                containers.append(container)

    return containers


def extract_delivery_schedule(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """배송 일정 데이터 추출"""
    deliveries = []

    for msg in messages:
        if not msg:
            continue

        message = msg["message"]

        # 배송 관련 키워드가 포함된 메시지
        if any(
            keyword in message.lower()
            for keyword in ["delivery", "deliveries", "today", "tomorrow"]
        ):
            # 회사명 추출
            company_match = re.search(
                r"\b(Averda|Alphamed|Novatech|Granite)\b", message, re.IGNORECASE
            )
            company = company_match.group(1) if company_match else None

            # 수량 정보 추출
            quantity_match = re.search(
                r"(\d+)\s*(x|×)\s*(skips|trailers|bins)", message, re.IGNORECASE
            )
            quantity = quantity_match.group(1) if quantity_match else None
            unit = quantity_match.group(3) if quantity_match else None

            # 날짜 정보 추출
            date_info = (
                "today"
                if "today" in message.lower()
                else "tomorrow" if "tomorrow" in message.lower() else None
            )

            if company or quantity:
                delivery = {
                    "company": company,
                    "quantity": quantity,
                    "unit": unit,
                    "date_info": date_info,
                    "timestamp": msg["timestamp"],
                    "sender": msg["sender"],
                    "responsible_person": extract_responsible_person(message),
                    "message": message,
                }
                deliveries.append(delivery)

    return deliveries


def analyze_whatsapp_data(file_path: str) -> Dict[str, Any]:
    """WhatsApp 대화 데이터 분석"""
    print(f"[INFO] WhatsApp 대화 데이터 분석 중: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    messages = []

    # 메시지 파싱
    for line in lines:
        if line.strip():
            message = parse_whatsapp_message(line)
            if message:
                messages.append(message)

    print(f"[INFO] 총 {len(messages)}개 메시지 파싱 완료")

    # 발신자별 통계
    sender_stats = Counter(msg["sender"] for msg in messages if msg)

    # 시간대별 통계
    hour_stats = Counter(msg["time"][:2] for msg in messages if msg)

    # 물류 관련 키워드 추출
    all_keywords = []
    for msg in messages:
        if msg:
            keywords = extract_logistics_keywords(msg["message"])
            all_keywords.extend(keywords)

    keyword_stats = Counter(all_keywords)

    # 선박 및 화물 데이터 추출
    shipments = extract_shipment_data(messages)
    containers = extract_container_data(messages)
    deliveries = extract_delivery_schedule(messages)

    analysis = {
        "metadata": {
            "file_name": Path(file_path).name,
            "analysis_date": datetime.now().isoformat(),
            "total_messages": len(messages),
            "file_size": len(content),
        },
        "message_stats": {
            "total_messages": len(messages),
            "top_senders": dict(sender_stats.most_common(10)),
            "hourly_distribution": dict(hour_stats.most_common(24)),
        },
        "logistics_data": {
            "shipments": shipments,
            "containers": containers,
            "deliveries": deliveries,
            "top_keywords": dict(keyword_stats.most_common(20)),
        },
        "raw_messages": messages[:100],  # 처음 100개 메시지만 저장
    }

    return analysis


def main():
    """메인 함수"""
    print("=" * 60)
    print("아부다비 WhatsApp 대화 분석 스크립트")
    print("=" * 60)

    # 파일 경로 설정
    whatsapp_file = "ABU/‎Abu Dhabi Logistics님과의 WhatsApp 대화.txt"

    if not Path(whatsapp_file).exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {whatsapp_file}")
        return

    # WhatsApp 데이터 분석
    print("\n1. WhatsApp 대화 분석")
    analysis = analyze_whatsapp_data(whatsapp_file)

    # 결과 출력
    print(f"\n[SUCCESS] 분석 완료")
    print(f"  - 총 메시지: {analysis['message_stats']['total_messages']}개")
    print(f"  - 선박 데이터: {len(analysis['logistics_data']['shipments'])}개")
    print(f"  - 컨테이너 데이터: {len(analysis['logistics_data']['containers'])}개")
    print(f"  - 배송 일정: {len(analysis['logistics_data']['deliveries'])}개")
    print(f"  - 상위 키워드: {len(analysis['logistics_data']['top_keywords'])}개")

    # JSON 파일로 저장
    output_file = "reports/abu_whatsapp_analysis.json"
    Path("reports").mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] 분석 결과 저장: {output_file}")

    return analysis


if __name__ == "__main__":
    main()
