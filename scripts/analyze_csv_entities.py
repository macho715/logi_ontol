#!/usr/bin/env python3
"""
CSV 엔티티 분석 스크립트
"""

import sys
import csv
from collections import defaultdict

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding="utf-8")

def analyze_csv_entities(csv_path):
    """CSV 엔티티 분석"""
    categories = defaultdict(int)
    category_details = defaultdict(list)
    total_entities = 0
    total_mentions = 0
    
    print(f"📊 CSV 엔티티 분석: {csv_path}")
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Category") and row.get("Entity"):
                category = row["Category"]
                entity = row["Entity"]
                count = int(row["Count"]) if row.get("Count") else 0
                
                categories[category] += 1
                category_details[category].append({
                    "entity": entity,
                    "count": count
                })
                total_entities += 1
                total_mentions += count
    
    print(f"\n총 엔티티: {total_entities}개")
    print(f"총 언급: {total_mentions:,}회")
    print()
    
    for category, count in sorted(categories.items()):
        mentions = sum(e["count"] for e in category_details[category])
        print(f"  - {category}: {count}개 엔티티, {mentions:,}회 언급")
    
    return categories, category_details, total_entities, total_mentions

if __name__ == "__main__":
    csv_path = "HVDC Project Lightning/Logistics_Entities__Summary_.csv"
    analyze_csv_entities(csv_path)
