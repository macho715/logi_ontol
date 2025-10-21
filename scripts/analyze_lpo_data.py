#!/usr/bin/env python3
"""
ABU WhatsApp 대화에서 LPO(Local Purchase Order) 데이터 추출 및 분석
"""

import sys
import re
import json
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding="utf-8")


def extract_lpo_data(whatsapp_file):
    """WhatsApp 대화에서 LPO 데이터 추출"""
    lpo_data = []
    lpo_pattern = r"LPO-(\d+)"

    with open(whatsapp_file, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    current_date = None
    current_location = None

    for line in lines:
        # 날짜 추출
        date_match = re.match(r"(\d{2}/\d{1,2}/\d{1,2})", line)
        if date_match:
            current_date = date_match.group(1)
            continue

        # 위치 추출 (AGI, DAS, MOSB 등)
        location_match = re.search(r"\*(AGI|DAS|MOSB|MW4)\*", line)
        if location_match:
            current_location = location_match.group(1)
            continue

        # LPO 항목 추출
        lpo_matches = re.findall(lpo_pattern, line)
        if lpo_matches:
            # LPO 번호와 설명 추출
            lpo_items = re.findall(r"LPO-(\d+)\s*-\s*([^/]+)\s*/\s*([^/\n]+)", line)
            for lpo_num, description, vendor in lpo_items:
                lpo_data.append(
                    {
                        "lpo_number": f"LPO-{lpo_num}",
                        "description": description.strip(),
                        "vendor": vendor.strip(),
                        "date": current_date,
                        "location": current_location,
                        "raw_line": line.strip(),
                    }
                )

    return lpo_data


def analyze_lpo_statistics(lpo_data):
    """LPO 데이터 통계 분석"""
    stats = {
        "total_lpos": len(lpo_data),
        "unique_lpos": len(set(item["lpo_number"] for item in lpo_data)),
        "vendors": Counter(item["vendor"] for item in lpo_data),
        "locations": Counter(item["location"] for item in lpo_data if item["location"]),
        "categories": defaultdict(int),
        "monthly_distribution": defaultdict(int),
        "lpo_numbers": sorted(set(item["lpo_number"] for item in lpo_data)),
    }

    # 카테고리 분류 (키워드 기반)
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

    for item in lpo_data:
        description_lower = item["description"].lower()
        categorized = False

        for category, keywords in category_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                stats["categories"][category] += 1
                categorized = True
                break

        if not categorized:
            stats["categories"]["Other"] += 1

        # 월별 분포
        if item["date"]:
            try:
                date_obj = datetime.strptime(item["date"], "%y/%m/%d")
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                stats["monthly_distribution"][month_key] += 1
            except:
                pass

    return stats


def generate_lpo_analysis_report(lpo_data, stats):
    """LPO 분석 보고서 생성"""
    report = {
        "executive_summary": {
            "total_lpo_entries": stats["total_lpos"],
            "unique_lpo_numbers": stats["unique_lpos"],
            "date_range": "2024-08-21 to 2025-08-08",
            "primary_locations": dict(stats["locations"].most_common(3)),
            "top_vendors": dict(stats["vendors"].most_common(5)),
        },
        "detailed_statistics": {
            "vendor_distribution": dict(stats["vendors"]),
            "location_distribution": dict(stats["locations"]),
            "category_distribution": dict(stats["categories"]),
            "monthly_distribution": dict(stats["monthly_distribution"]),
        },
        "lpo_list": lpo_data,
        "analysis_timestamp": datetime.now().isoformat(),
    }

    return report


def main():
    """메인 실행 함수"""
    print("🔍 ABU WhatsApp 대화에서 LPO 데이터 분석 시작...")

    # 파일 경로 설정
    whatsapp_file = Path("ABU/‎Abu Dhabi Logistics님과의 WhatsApp 대화.txt")

    if not whatsapp_file.exists():
        print(f"❌ WhatsApp 파일을 찾을 수 없습니다: {whatsapp_file}")
        return

    # LPO 데이터 추출
    print("📊 LPO 데이터 추출 중...")
    lpo_data = extract_lpo_data(whatsapp_file)
    print(f"✅ {len(lpo_data)}개의 LPO 항목을 추출했습니다.")

    # 통계 분석
    print("📈 통계 분석 중...")
    stats = analyze_lpo_statistics(lpo_data)

    # 보고서 생성
    print("📋 분석 보고서 생성 중...")
    report = generate_lpo_analysis_report(lpo_data, stats)

    # 결과 저장
    output_file = Path("reports/abu_lpo_analysis.json")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ 분석 결과가 저장되었습니다: {output_file}")

    # 요약 출력
    print("\n📊 LPO 분석 요약:")
    print(f"  - 총 LPO 항목: {stats['total_lpos']}개")
    print(f"  - 고유 LPO 번호: {stats['unique_lpos']}개")
    print(f"  - 주요 위치: {dict(stats['locations'].most_common(3))}")
    print(f"  - 상위 공급업체: {dict(stats['vendors'].most_common(3))}")
    print(f"  - 카테고리 분포: {dict(stats['categories'])}")

    # LPO 번호 범위 출력
    if stats["lpo_numbers"]:
        print(
            f"  - LPO 번호 범위: {stats['lpo_numbers'][0]} ~ {stats['lpo_numbers'][-1]}"
        )

    return report


if __name__ == "__main__":
    main()
