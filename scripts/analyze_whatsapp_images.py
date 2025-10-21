#!/usr/bin/env python3
"""
ABU WhatsApp 이미지에서 LPO 관련 정보 추출 및 분석
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

# UTF-8 인코딩 설정
sys.stdout.reconfigure(encoding="utf-8")

def analyze_image_metadata(image_folder):
    """WhatsApp 이미지 메타데이터 분석"""
    image_data = []
    
    image_path = Path(image_folder)
    if not image_path.exists():
        print(f"❌ 이미지 폴더를 찾을 수 없습니다: {image_folder}")
        return image_data
    
    # 이미지 파일 목록 가져오기
    image_files = list(image_path.glob("*.jpg"))
    print(f"📸 {len(image_files)}개의 WhatsApp 이미지를 발견했습니다.")
    
    for img_file in image_files:
        # 파일명에서 날짜 정보 추출
        filename = img_file.name
        date_info = extract_date_from_filename(filename)
        
        # 파일 크기 및 메타데이터 수집
        file_stats = img_file.stat()
        
        image_info = {
            'filename': filename,
            'file_path': str(img_file),
            'file_size': file_stats.st_size,
            'created_date': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'modified_date': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'extracted_date': date_info,
            'file_type': 'WhatsApp_Image'
        }
        
        image_data.append(image_info)
    
    return image_data

def extract_date_from_filename(filename):
    """파일명에서 날짜 정보 추출"""
    # IMG-20251019-WA0028.jpg 형식에서 날짜 추출
    try:
        if filename.startswith('IMG-') and '-WA' in filename:
            # IMG-20251019-WA0028.jpg -> 2025-10-19
            date_part = filename.split('-')[1]  # 20251019
            if len(date_part) == 8:
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                return f"{year}-{month}-{day}"
    except:
        pass
    
    return None

def categorize_images_by_date(image_data):
    """이미지를 날짜별로 분류"""
    date_groups = defaultdict(list)
    
    for img in image_data:
        date = img.get('extracted_date', 'Unknown')
        date_groups[date].append(img)
    
    return dict(date_groups)

def analyze_image_patterns(image_data):
    """이미지 패턴 분석"""
    patterns = {
        'total_images': len(image_data),
        'date_range': {},
        'file_size_distribution': {},
        'daily_activity': defaultdict(int),
        'file_naming_patterns': defaultdict(int)
    }
    
    if not image_data:
        return patterns
    
    # 날짜 범위 계산
    dates = [img['extracted_date'] for img in image_data if img['extracted_date']]
    if dates:
        patterns['date_range'] = {
            'earliest': min(dates),
            'latest': max(dates)
        }
    
    # 파일 크기 분포
    size_ranges = {
        'small': 0,    # < 100KB
        'medium': 0,   # 100KB - 500KB
        'large': 0     # > 500KB
    }
    
    for img in image_data:
        size_kb = img['file_size'] / 1024
        if size_kb < 100:
            size_ranges['small'] += 1
        elif size_kb < 500:
            size_ranges['medium'] += 1
        else:
            size_ranges['large'] += 1
    
    patterns['file_size_distribution'] = size_ranges
    
    # 일별 활동량
    for img in image_data:
        date = img.get('extracted_date', 'Unknown')
        patterns['daily_activity'][date] += 1
    
    # 파일명 패턴 분석
    for img in image_data:
        filename = img['filename']
        if filename.startswith('IMG-'):
            patterns['file_naming_patterns']['IMG-prefix'] += 1
        if '-WA' in filename:
            patterns['file_naming_patterns']['WhatsApp-format'] += 1
    
    return patterns

def generate_image_analysis_report(image_data, patterns, date_groups):
    """이미지 분석 보고서 생성"""
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'summary': {
            'total_images': patterns['total_images'],
            'date_range': patterns['date_range'],
            'file_size_distribution': patterns['file_size_distribution'],
            'most_active_dates': dict(Counter(patterns['daily_activity']).most_common(5))
        },
        'detailed_analysis': {
            'images_by_date': {date: len(images) for date, images in date_groups.items()},
            'file_naming_patterns': dict(patterns['file_naming_patterns']),
            'daily_activity': dict(patterns['daily_activity'])
        },
        'image_list': image_data,
        'recommendations': generate_recommendations(patterns, date_groups)
    }
    
    return report

def generate_recommendations(patterns, date_groups):
    """분석 결과 기반 권장사항 생성"""
    recommendations = []
    
    # 이미지 수 기반 권장사항
    total_images = patterns['total_images']
    if total_images > 100:
        recommendations.append("대량의 이미지가 발견되었습니다. OCR 처리를 통한 LPO 정보 추출을 권장합니다.")
    elif total_images > 50:
        recommendations.append("중간 규모의 이미지가 발견되었습니다. 샘플링 기반 분석을 고려하세요.")
    else:
        recommendations.append("소규모 이미지 세트입니다. 전체 이미지 분석이 가능합니다.")
    
    # 날짜 분포 기반 권장사항
    if patterns['date_range']:
        date_range = patterns['date_range']
        if date_range['earliest'] != date_range['latest']:
            recommendations.append(f"이미지가 {date_range['earliest']}부터 {date_range['latest']}까지 분포되어 있습니다. 시간순 분석이 가능합니다.")
    
    # 파일 크기 기반 권장사항
    size_dist = patterns['file_size_distribution']
    if size_dist['large'] > size_dist['small'] + size_dist['medium']:
        recommendations.append("대용량 이미지가 많습니다. 고해상도 문서나 스크린샷일 가능성이 높습니다.")
    
    # LPO 관련 권장사항
    recommendations.extend([
        "이미지에서 LPO 번호, 공급업체명, 금액, 날짜 등의 텍스트 정보를 추출할 수 있습니다.",
        "WhatsApp 이미지는 주로 LPO 문서, 견적서, 승인서 등의 스크린샷일 가능성이 높습니다.",
        "OCR 기술을 활용하여 이미지에서 구조화된 LPO 데이터를 추출하는 것을 권장합니다."
    ])
    
    return recommendations

def main():
    """메인 실행 함수"""
    print("📸 ABU WhatsApp 이미지 분석 시작...")
    
    # 이미지 폴더 경로 설정
    image_folder = Path("ABU/WHATSAPP")
    
    if not image_folder.exists():
        print(f"❌ 이미지 폴더를 찾을 수 없습니다: {image_folder}")
        return
    
    # 이미지 메타데이터 분석
    print("📊 이미지 메타데이터 분석 중...")
    image_data = analyze_image_metadata(image_folder)
    
    if not image_data:
        print("❌ 분석할 이미지가 없습니다.")
        return
    
    # 이미지 패턴 분석
    print("🔍 이미지 패턴 분석 중...")
    patterns = analyze_image_patterns(image_data)
    
    # 날짜별 분류
    print("📅 날짜별 분류 중...")
    date_groups = categorize_images_by_date(image_data)
    
    # 분석 보고서 생성
    print("📋 분석 보고서 생성 중...")
    report = generate_image_analysis_report(image_data, patterns, date_groups)
    
    # 결과 저장
    output_file = Path("reports/whatsapp_images_analysis.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 분석 결과가 저장되었습니다: {output_file}")
    
    # 요약 출력
    print("\n📊 WhatsApp 이미지 분석 요약:")
    print(f"  - 총 이미지: {patterns['total_images']}개")
    print(f"  - 날짜 범위: {patterns['date_range'].get('earliest', 'N/A')} ~ {patterns['date_range'].get('latest', 'N/A')}")
    print(f"  - 파일 크기 분포: {patterns['file_size_distribution']}")
    print(f"  - 가장 활발한 날짜: {dict(Counter(patterns['daily_activity']).most_common(3))}")
    
    # 권장사항 출력
    print("\n💡 권장사항:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    return report

if __name__ == "__main__":
    main()
