# JPT71 Gantt Chart PNG Export Guide

## 📸 생성된 파일들

### HTML 파일
- **경로**: `c:\logi_ontol\reports\analysis\JPT71_gantt_timeline.html`
- **용도**: 브라우저에서 직접 열어서 확인
- **특징**: 다크 테마, 인터랙티브 툴팁

### PNG 이미지
- **경로**: `c:\logi_ontol\reports\analysis\image\JPT71_NETWORK_VISUALIZATION\JPT71_gantt_chart.png`
- **용도**: 문서 삽입, 프레젠테이션, 보고서
- **해상도**: 1920x1080 (고품질)

## 🖥️ 브라우저에서 확인하기

### 방법 1: 파일 탐색기
1. `c:\logi_ontol\reports\analysis\` 폴더 열기
2. `JPT71_gantt_timeline.html` 더블클릭
3. 기본 브라우저에서 열림

### 방법 2: 명령어
```cmd
start c:\logi_ontol\reports\analysis\JPT71_gantt_timeline.html
```

## 📷 PNG 스크린샷 다시 생성하기

### 자동 생성 (권장)
```cmd
cd c:\logi_ontol
python scripts\screenshot_gantt.py
```

### 수동 생성
1. HTML 파일을 브라우저에서 열기
2. F12 (개발자 도구) → Device Toolbar
3. 해상도 1920x1080 설정
4. 전체 페이지 스크린샷 (Ctrl+Shift+S)
5. PNG로 저장

## 🎨 스타일 특징

### 다크 테마
- **배경**: #282828 (어두운 회색)
- **텍스트**: #ffffff (흰색)
- **그리드**: #606060 (연한 회색)

### 간트 막대
- **Underway**: #3a663a (진한 녹색)
- **Active Operations**: #5cb85c (밝은 녹색)
- **현재 시간**: #ff0000 (빨간색)

### 3개 운항 경로
1. **AGI 운항**: 00:00-21:00
2. **MW4 운항**: 00:00-10:00
3. **MOSB 운항**: 06:00-22:00

## 🔧 문제 해결

### HTML이 제대로 열리지 않는 경우
```cmd
# 파일 경로 확인
dir c:\logi_ontol\reports\analysis\JPT71_gantt_timeline.html

# 브라우저 강제 실행
start chrome c:\logi_ontol\reports\analysis\JPT71_gantt_timeline.html
```

### PNG 생성 실패 시
```cmd
# Playwright 재설치
pip install playwright
playwright install

# 스크립트 재실행
python scripts\screenshot_gantt.py
```

## 📊 파일 크기 및 품질

| 파일 | 크기 | 품질 | 용도 |
|------|------|------|------|
| HTML | ~15KB | 무제한 | 브라우저 확인 |
| PNG | ~500KB | 1920x1080 | 문서 삽입 |

## 🎯 사용 예시

### PowerPoint 삽입
1. PNG 파일을 PowerPoint에 드래그
2. 크기 조정하여 슬라이드에 맞게 조정
3. 텍스트 설명 추가

### Word 문서 삽입
1. Word에서 "삽입" → "그림"
2. PNG 파일 선택
3. 캡션 추가: "그림 1. JPT71 운항 스케줄"

### 이메일 첨부
1. PNG 파일을 이메일에 첨부
2. 제목: "JPT71 운항 스케줄 분석 결과"
3. 본문에 간단한 설명 추가

---

**생성일**: 2025-10-25
**도구**: MACHO-GPT v3.4-mini
**스크립트**: `scripts\screenshot_gantt.py`
