#!/usr/bin/env python3
"""
아부다비 물류 가이드라인 분석 스크립트
Guideline_Abu_Dhabi_Logistics.md 파일을 분석하여 구조화된 데이터를 추출합니다.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Unicode 출력 지원
sys.stdout.reconfigure(encoding="utf-8")


def extract_executive_summary(content: str) -> Dict[str, Any]:
    """Executive Summary 섹션 추출"""
    summary = {
        "version": "v2.1",
        "key_improvements": [],
        "safety_requirements": [],
        "port_policies": [],
        "vessel_stowage": [],
    }

    lines = content.split("\n")
    in_summary = False

    for line in lines:
        if "Executive Summary" in line:
            in_summary = True
            continue
        elif in_summary and line.startswith("##"):
            break
        elif in_summary and line.strip().startswith("-"):
            # 키워드 추출
            if "지연 리스크" in line:
                summary["key_improvements"].append(
                    "지연 리스크 관리 고도화 - 10·20·30 Rule 에스컬레이션"
                )
            elif "안전" in line:
                summary["safety_requirements"].append("HCS 균열 반송·증빙 의무화")
                summary["safety_requirements"].append(
                    "슬링/라싱 TPI·컬러코드 준수 강화"
                )
            elif "항만 정책" in line:
                summary["port_policies"].append("Al Jaber Only A-Frame")
                summary["port_policies"].append("예외 Dispensation 사전 승인")
            elif "선박/적재" in line:
                summary["vessel_stowage"].append("2-LCT Stowage")
                summary["vessel_stowage"].append("대체 LCT(Yeam/Taibah) 탄력 운용")

    return summary


def extract_group_profile(content: str) -> Dict[str, Any]:
    """Group Profile 섹션 추출"""
    profile = {
        "purpose_scope": "",
        "key_participants": [],
        "activity_period": "",
        "traffic_level": "",
        "top_participants": [],
    }

    lines = content.split("\n")
    in_profile = False
    in_table = False

    for i, line in enumerate(lines):
        if "Group Profile" in line:
            in_profile = True
            continue
        elif in_profile and line.startswith("##"):
            break
        elif in_profile and "목적/범위" in line:
            # 다음 줄에서 목적/범위 내용 추출
            if i + 1 < len(lines):
                parts = lines[i + 1].split("|")
                if len(parts) > 2:
                    profile["purpose_scope"] = parts[2].strip()
        elif in_profile and "주요 참여자" in line:
            # 다음 줄에서 참여자 추출
            if i + 1 < len(lines):
                parts = lines[i + 1].split("|")
                if len(parts) > 2:
                    participants = parts[2].strip()
                    profile["key_participants"] = [
                        p.strip() for p in participants.split(",")
                    ]
        elif in_profile and "활동기간" in line:
            if i + 1 < len(lines):
                parts = lines[i + 1].split("|")
                if len(parts) > 2:
                    profile["activity_period"] = parts[2].strip()
        elif in_profile and "트래픽" in line:
            if i + 1 < len(lines):
                parts = lines[i + 1].split("|")
                if len(parts) > 2:
                    profile["traffic_level"] = parts[2].strip()
        elif in_profile and "Top10 참여자" in line:
            in_table = True
            continue
        elif in_table and "|" in line and not line.startswith("|---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2 and parts[0] != "이름":
                profile["top_participants"].append(
                    {
                        "name": parts[0],
                        "message_count": int(parts[1]) if parts[1].isdigit() else 0,
                    }
                )

    return profile


def extract_patterns(content: str) -> Dict[str, Any]:
    """Observed Patterns 섹션 추출"""
    patterns = {
        "language_ratio": {},
        "peak_hours": [],
        "response_delay": {},
        "top_keywords": [],
    }

    lines = content.split("\n")
    in_patterns = False

    for line in lines:
        if "Observed Patterns" in line:
            in_patterns = True
            continue
        elif in_patterns and line.startswith("##"):
            break
        elif in_patterns and "언어 비율" in line:
            # KR 21% / EN 79% 형태에서 추출
            match = re.search(r"KR (\d+)% / EN (\d+)%", line)
            if match:
                patterns["language_ratio"] = {
                    "korean": int(match.group(1)),
                    "english": int(match.group(2)),
                }
        elif in_patterns and "피크 시간대" in line:
            # 09:00, 08:00, 10:00 형태에서 추출
            times = re.findall(r"\d{2}:\d{2}", line)
            patterns["peak_hours"] = times
        elif in_patterns and "평균 응답지연" in line:
            # 평균 16.7분 / 중앙값 2.0분 형태에서 추출
            avg_match = re.search(r"평균 ([\d.]+)분", line)
            median_match = re.search(r"중앙값 ([\d.]+)분", line)
            if avg_match and median_match:
                patterns["response_delay"] = {
                    "average": float(avg_match.group(1)),
                    "median": float(median_match.group(1)),
                }
        elif in_patterns and "Top10 키워드" in line:
            # 키워드 테이블 처리
            continue
        elif (
            in_patterns
            and "|" in line
            and not line.startswith("|---")
            and "키워드" not in line
        ):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3 and parts[0] != "키워드":
                patterns["top_keywords"].append(
                    {
                        "keyword": parts[0],
                        "count": int(parts[1]) if parts[1].isdigit() else 0,
                        "trend": parts[2],
                    }
                )

    return patterns


def extract_pain_points(content: str) -> List[str]:
    """Pain Points & Risks 섹션 추출"""
    pain_points = []

    lines = content.split("\n")
    in_pain_points = False

    for line in lines:
        if "Pain Points & Risks" in line:
            in_pain_points = True
            continue
        elif in_pain_points and line.startswith("##"):
            break
        elif in_pain_points and line.strip().startswith("-"):
            # 불릿 포인트에서 텍스트 추출
            point = line.strip()[1:].strip()
            if point:
                pain_points.append(point)

    return pain_points


def extract_tailored_rules(content: str) -> List[Dict[str, str]]:
    """Tailored Rules 섹션 추출"""
    rules = []

    lines = content.split("\n")
    in_rules = False

    for line in lines:
        if "Tailored Rules" in line:
            in_rules = True
            continue
        elif in_rules and line.startswith("##"):
            break
        elif in_rules and line.strip().startswith("-"):
            # 규칙 텍스트 추출
            rule_text = line.strip()[1:].strip()
            if rule_text:
                # 규칙 카테고리 분류
                category = "기타"
                if "Port policy" in rule_text or "항만 정책" in rule_text:
                    category = "항만 정책"
                elif "Forklift" in rule_text or "지연" in rule_text:
                    category = "지연 관리"
                elif "HCS" in rule_text or "안전" in rule_text:
                    category = "안전 관리"
                elif "라싱" in rule_text or "슬링" in rule_text:
                    category = "장비 관리"
                elif "Stowage" in rule_text or "적재" in rule_text:
                    category = "적재 계획"
                elif "증빙" in rule_text or "보고" in rule_text:
                    category = "문서 관리"
                elif "PII" in rule_text or "보안" in rule_text:
                    category = "보안 관리"
                elif "화이트보드" in rule_text:
                    category = "현장 관리"
                elif "선박" in rule_text or "자원" in rule_text:
                    category = "자원 관리"

                rules.append({"category": category, "rule": rule_text})

    return rules


def extract_kpis(content: str) -> List[Dict[str, Any]]:
    """KPI & 모니터링 섹션 추출"""
    kpis = []

    lines = content.split("\n")
    in_kpis = False

    for line in lines:
        if "KPI & 모니터링" in line:
            in_kpis = True
            continue
        elif in_kpis and line.startswith("##"):
            break
        elif in_kpis and line.strip().startswith("-"):
            # KPI 텍스트 추출
            kpi_text = line.strip()[1:].strip()
            if kpi_text:
                # KPI 메트릭 추출
                metric_match = re.search(r"(\d+)%", kpi_text)
                target = int(metric_match.group(1)) if metric_match else None

                kpis.append({"description": kpi_text, "target_percentage": target})

    return kpis


def analyze_abu_guidelines(file_path: str) -> Dict[str, Any]:
    """아부다비 물류 가이드라인 분석"""
    print(f"[INFO] 아부다비 물류 가이드라인 분석 중: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    analysis = {
        "metadata": {
            "file_name": Path(file_path).name,
            "analysis_date": datetime.now().isoformat(),
            "file_size": len(content),
        },
        "executive_summary": extract_executive_summary(content),
        "group_profile": extract_group_profile(content),
        "patterns": extract_patterns(content),
        "pain_points": extract_pain_points(content),
        "tailored_rules": extract_tailored_rules(content),
        "kpis": extract_kpis(content),
    }

    return analysis


def main():
    """메인 함수"""
    print("=" * 60)
    print("아부다비 물류 가이드라인 분석 스크립트")
    print("=" * 60)

    # 파일 경로 설정
    guideline_file = "ABU/Guideline_Abu_Dhabi_Logistics (3).md"

    if not Path(guideline_file).exists():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {guideline_file}")
        return

    # 가이드라인 분석
    print("\n1. 가이드라인 분석")
    analysis = analyze_abu_guidelines(guideline_file)

    # 결과 출력
    print(f"\n[SUCCESS] 분석 완료")
    print(
        f"  - Executive Summary: {len(analysis['executive_summary']['key_improvements'])}개 개선사항"
    )
    print(
        f"  - Group Profile: {len(analysis['group_profile']['top_participants'])}명 참여자"
    )
    print(f"  - Patterns: {len(analysis['patterns']['top_keywords'])}개 키워드")
    print(f"  - Pain Points: {len(analysis['pain_points'])}개 이슈")
    print(f"  - Tailored Rules: {len(analysis['tailored_rules'])}개 규칙")
    print(f"  - KPIs: {len(analysis['kpis'])}개 지표")

    # JSON 파일로 저장
    output_file = "reports/abu_guidelines_analysis.json"
    Path("reports").mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] 분석 결과 저장: {output_file}")

    return analysis


if __name__ == "__main__":
    main()
