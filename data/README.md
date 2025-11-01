# HVDC Logistics Data

**프로젝트**: HVDC Logistics & Ontology System
**데이터 버전**: v3.5
**최종 업데이트**: 2025-10-31

---

## 📁 폴더 구조

```
data/
├── source/          # 원본 소스 데이터
├── reports/         # 리포트 및 처리된 데이터
└── backups/         # 백업 데이터
```

---

## 📄 Source Data (원본 데이터)

**위치**: `data/source/`

### 1. DATA_WH.xlsx
- **설명**: 초기 HVDC 데이터 (Warehouse 중심)
- **크기**: ~755 cases
- **용도**: 초기 시스템 개발 및 테스트
- **컬럼**: HVDC_CODE, WAREHOUSE (multiple), SITE (MIR, SHU, DAS, AGI), Status_Location
- **처리**: Excel → TTL 변환 (logiontology/src/ingest/)

### 2. HVDC_STATUS_20250815.xlsx
- **설명**: 최신 HVDC 상태 데이터 (2025-08-15)
- **원본 파일명**: `HVDC STATUS(20250815) (1).xlsx`
- **크기**: ~755 cases
- **용도**: Flow Code v3.5 알고리즘 적용
- **특징**:
  - Flow Code 0~5 분류
  - AGI/DAS 도메인 룰 적용
  - 이벤트 기반 모델링 (Inbound/Outbound)
- **처리**: `logiontology/src/ingest/excel_to_ttl_with_events.py`
- **출력**: `output/hvdc_status_v35.ttl` (9,904 triples, 818 events)

---

## 📊 Reports (리포트 데이터)

**위치**: `data/reports/`

### 1. HVDC_입고로직_종합리포트_20251019_v3.0.xlsx
- **설명**: HVDC 입고 로직 종합 리포트
- **날짜**: 2025-10-19
- **버전**: v3.0 (corrected)
- **용도**: 입고 프로세스 분석 및 검증
- **내용**:
  - 입고 패턴 분석
  - Warehouse 경유 통계
  - MOSB 레그 분석
  - Flow 분포 리포트

### 2. invoice_sept2025.xlsm
- **설명**: 2025년 9월 인보이스 데이터
- **형식**: Excel Macro-Enabled Workbook
- **용도**: 비용 분석 및 청구서 관리
- **처리**: Invoice OCR 및 분석 (계획 중)

---

## 💾 Backups (백업)

**위치**: `data/backups/`

### HVDC_STATUS_20250427.xlsm
- **설명**: 2025-04-27 HVDC 상태 백업
- **형식**: Excel Macro-Enabled Workbook
- **용도**: 이전 버전 데이터 참조 및 비교

---

## 🔄 데이터 변환 프로세스

### Excel → TTL 변환

**스크립트**: `logiontology/src/ingest/excel_to_ttl_with_events.py`

**프로세스**:
1. Excel 파일 읽기 (pandas)
2. 컬럼 정규화 (normalize_column_names)
3. Flow Code 계산 (flow_code_calculator.py)
   - 관측값 계산 (wh_cnt, has_mosb, has_site)
   - 기본 Flow Code (0~4)
   - AGI/DAS 도메인 오버라이드
   - 혼합 케이스 처리 (Flow 5)
4. 이벤트 주입 (inject_events_to_case)
   - Inbound/Outbound StockEvent 생성
   - 날짜, 위치, 수량 정보 추가
5. RDF 트리플 생성 (hvdc: namespace)
6. TTL 파일 저장

**입력**:
```
data/source/HVDC_STATUS_20250815.xlsx
```

**출력**:
```
output/hvdc_status_v35.ttl
  - 755 cases (hvdc:Case)
  - 9,904 triples
  - 818 events (hvdc:StockEvent)
```

### Flow Code v3.5 분류

| Flow Code | 설명 | 패턴 | 비율 (예상) |
|-----------|------|------|-------------|
| 0 | Pre Arrival | - | ~23% |
| 1 | Port → Site | 직접 배송 | ~49% |
| 2 | Port → WH → Site | 창고 경유 | ~50% |
| 3 | Port → MOSB → Site | MOSB 경유 (AGI/DAS 필수) | ~6% |
| 4 | Port → WH → MOSB → Site | 창고+MOSB 경유 | ~7% |
| 5 | Mixed/Waiting/Incomplete | 혼합/미완료 | ~5% |

---

## 🛠️ 데이터 사용 가이드

### 1. 새 Excel 데이터 추가

```bash
# 1. Excel 파일을 data/source/에 복사
cp "new_data.xlsx" data/source/

# 2. TTL 변환
cd logiontology
logiontology ingest-excel ../data/source/new_data.xlsx

# 3. 출력 확인
ls ../output/
```

### 2. 기존 데이터 재처리

```bash
# Flow Code v3.5 재계산
cd logiontology
python src/ingest/excel_to_ttl_with_events.py \
  --input ../data/source/HVDC_STATUS_20250815.xlsx \
  --output ../output/hvdc_status_v35_reprocessed.ttl
```

### 3. 데이터 검증

```bash
# SPARQL 검증 쿼리 실행
cd logiontology
logiontology validate-events ../output/hvdc_status_v35.ttl
```

---

## 📐 데이터 스키마

### Excel 컬럼 (주요)

- **HVDC_CODE**: 화물 고유 코드
- **Status_Location**: 현재 위치 및 상태
- **Warehouse 컬럼**: DHL WH, DSV Indoor, DSV Outdoor, MOSB, etc.
- **Site 컬럼**: MIR, SHU, DAS, AGI
- **Final_Location**: 최종 목적지
- **ATA/ATD**: Actual Time of Arrival/Departure

### TTL 클래스 (RDF)

- **hvdc:Case**: 개별 화물 케이스
- **hvdc:StockEvent**: 입출고 이벤트
- **hvdc:Warehouse**: 창고 시설
- **hvdc:Site**: 현장 위치
- **hvdc:Hub**: 물류 허브 (MOSB)

---

## 🔗 관련 문서

- **Flow Code v3.5 알고리즘**: [docs/flow_code_v35/FLOW_CODE_V35_ALGORITHM.md](../docs/flow_code_v35/FLOW_CODE_V35_ALGORITHM.md)
- **구현 완료 보고서**: [docs/flow_code_v35/FLOW_CODE_V35_IMPLEMENTATION_COMPLETE.md](../docs/flow_code_v35/FLOW_CODE_V35_IMPLEMENTATION_COMPLETE.md)
- **Excel → TTL 변환기**: [logiontology/src/ingest/](../logiontology/src/ingest/)
- **출력 데이터**: [output/](../output/)

---

**데이터 버전**: v3.5
**작성일**: 2025-10-31
**작성자**: HVDC Project Team

