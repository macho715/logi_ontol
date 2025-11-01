# 온톨로지 데이터 허브 - TTL & JSON 파일 가이드

**버전**: 1.0
**생성일**: 2025-11-01
**총 파일 수**: 68개 (TTL 18개 + JSON 50개)

---

## 목차

1. [개요](#개요)
2. [TTL 파일 설명](#ttl-파일-설명) (18개)
3. [JSON 파일 설명](#json-파일-설명) (50개)
4. [사용 예시](#사용-예시)
5. [빠른 참조](#빠른-참조)
6. [파일 간 관계](#파일-간-관계)

---

## 개요

### 전체 파일 인벤토리

| 카테고리 | 파일 수 | 설명 |
|----------|---------|------|
| **TTL - 현재 데이터** | 1 | Flow Code v3.5 최신 운영 데이터 |
| **TTL - 최종 확정** | 2 | 안정화된 참조 데이터 |
| **TTL - 특화 데이터** | 15 | 도메인별 상세 분석 |
| **JSON - GPT 캐시** | 3 | GPT 응답용 사전 계산 |
| **JSON - 통합 데이터** | 10 | 시스템 통합 및 비교 |
| **JSON - 리포트** | 18 | 도메인별 분석 보고서 |
| **JSON - 검증** | 5 | 데이터 품질 검증 |
| **TOTAL** | **68** | **종합 데이터 허브** |

### 파일 명명 규칙

**TTL 파일**:
- `[시스템]_[버전].ttl`: 예) `hvdc_status_v35.ttl`
- `[프로젝트]_[타입].ttl`: 예) `abu_logistics_data.ttl`
- `[도메인]_[날짜]_[시간].ttl`: 예) `invoice_SEPT_20251020_000829.ttl`

**JSON 파일**:
- `[설명]_[범위].json`: 예) `cases_by_flow.json`, `monthly_warehouse_inbound.json`
- `[시스템]_[목적].json`: 예) `abu_comprehensive_summary.json`
- `[타입]_summary.json`: 예) `validation_summary.json`

### 공통 데이터 패턴

**TTL (Turtle 포맷)**:
- RDF 그래프 구조 (Subject-Predicate-Object)
- Namespace: `hvdc:`, `abu:`, `lightning:` 등
- 표준 필드: `hasCBM`, `hasFlowCode`, `hasVendor` 등
- 이벤트 구조: `hasInboundEvent`, `hasOutboundEvent`

**JSON (표준 포맷)**:
- 배열: `[{...}, {...}]` (집계 데이터)
- 객체: `{...}` (요약 데이터)
- 공통 필드: `timestamp`, `count`, `status` 등

---

## TTL 파일 설명

### A. 현재 데이터 (1개 파일)

#### `hvdc_status_v35.ttl`

**위치**: `03_data/ttl/current/`
**크기**: 9,844줄, 9,904 트리플, 755 케이스
**버전**: Flow Code v3.5

**내용**:
HVDC 프로젝트의 최신 물류 데이터로, Flow Code v3.5 알고리즘으로 분류된 모든 케이스를 포함합니다.

**주요 속성**:
- `hasCBM`: 화물 용적 (Cubic Meter)
- `hasFlowCode`: 물류 흐름 코드 (0-5)
- `hasFlowCodeOriginal`: 원본 Flow Code (Override 추적용)
- `hasFlowDescription`: Flow 설명 (예: "Flow 2: Port → WH → Site")
- `hasFlowOverrideReason`: Override 사유 (예: "AGI/DAS requires MOSB leg")
- `hasHvdcCode`: HVDC 코드 (예: "HVDC-ADOPT-PPL-0001")
- `hasVendor`: 공급업체 (예: "Prysmian", "Hitachi")
- `hasFinalLocation`: 최종 도착지 (예: "DAS", "AGI")

**이벤트 구조**:
```
hasInboundEvent [
    hasEventDate "2024-01-20" ;
    hasLocationAtEvent "Vijay Tanks" ;
    hasQuantity 1.0
]
```

**Flow Code 분포** (755 케이스):
- Flow 0: 71 (9.4%) - Pre Arrival
- Flow 1: 255 (33.8%) - Port → Site
- Flow 2: 152 (20.1%) - Port → WH → Site
- Flow 3: 131 (17.4%) - Port → MOSB → Site
- Flow 4: 65 (8.6%) - Port → WH → MOSB → Site
- Flow 5: 81 (10.7%) - Mixed/Incomplete

**용도**:
- 실시간 물류 쿼리를 위한 주요 데이터 소스
- MCP 서버의 기본 데이터셋
- Flow Code 분포 및 AGI/DAS 규칙 검증

---

### B. 최종 확정 데이터 (2개 파일)

#### `abu_final.ttl`

**위치**: `03_data/ttl/finalized/`
**크기**: 923KB, 18,894 트리플, 500 엔티티

**내용**:
아부다비 시스템의 최종 통합 RDF 데이터로, 물류 데이터, LPO 데이터, 이미지 메타데이터를 포함합니다.

**주요 속성**:
- `abu:containerId`: 컨테이너 ID
- `abu:containerType`: 컨테이너 타입
- `abu:responsiblePerson`: 책임자 이름
- `abu:reportedBy`: 보고자 (예: "System", "- 상욱: 40ft OT Container")
- `abu:timestamp`: 타임스탬프

**Namespaces**:
- `abu:`: 아부다비 핵심 네임스페이스
- `abui:`: 아부다비 인스턴스
- `ns1:`: LPO 네임스페이스

**용도**:
- 아부다비 시스템 안정적 참조 데이터
- 책임자 추적 및 타임라인 분석
- 통합 보고서 생성

---

#### `lightning_final.ttl`

**위치**: `03_data/ttl/finalized/`
**크기**: 3.1MB, 67,000 트리플, 2,000 엔티티

**내용**:
Lightning 프로젝트의 최종 통합 RDF로, 이미지, 엔티티, WhatsApp 데이터를 통합했습니다.

**주요 속성**:
- `lightning:filename`: 파일명
- `lightning:fileSizeMB`: 파일 크기 (MB)
- `lightning:imageType`: 이미지 타입 (예: "WhatsApp_Image")
- `lightning:capturedDate`: 촬영일
- `lightning:filePath`: 파일 경로

**Namespaces**:
- `lightning:`: Lightning 핵심
- `lightningi:`: Lightning 인스턴스

**용도**:
- Lightning 프로젝트 최종 참조 데이터
- 이미지 메타데이터 추적
- WhatsApp 통합 분석

---

### C. 특화 데이터 (15개 파일)

#### 아부다비 시스템 파일 (6개)

**1. `abu_integrated_system.ttl`**
- 물류 + LPO + 이미지 통합 시스템
- 운영 데이터 총합

**2. `abu_logistics_data.ttl`** (0.1MB, 2,814 트리플)
- 기본 물류 데이터만
- 경량 쿼리용

**3. `abu_lpo_data.ttl`** (0.2MB, 5,779 트리플)
- LPO(Local Purchase Order) 전용 데이터
- 구매 주문 분석

**4. `abu_with_images.ttl`** (0.2MB, 5,070 트리플)
- 이미지 메타데이터 포함
- 시각 자료 추적

**5. `abu_comprehensive_summary.json`** (리포트, 3. 데이터 참조)
- 종합 분석 요약
- 통계 및 KPI

#### Lightning 시스템 파일 (6개)

**1. `lightning_integrated_system.ttl`** (3.0MB, 65,000 트리플)
- 기본 통합 시스템
- 엔티티 + 관계

**2. `lightning_enriched_system.ttl`** (3.0MB, 66,000 트리플)
- CSV 엔티티 보강
- 고유값: 243개 엔티티 추가

**3. `lightning_enhanced_system.ttl`** (3.0MB, 66,500 트리플)
- 주요 엔티티 상세 보강
- 타임태그 및 참조 추가

**4. `lightning_whatsapp_integrated.ttl`**
- WhatsApp 메시지 통합
- 4,671개 메시지

**5. `lightning_with_images.ttl`** (0.04MB, 904 트리플)
- 이미지 메타데이터만
- 321개 이미지 엔티티

#### 인보이스 데이터 (3개)

**1. `invoice_SEPT_20251020_000803.ttl`**
- 비어 있음 (삭제 권장)

**2. `invoice_SEPT_20251020_000829.ttl`** (0.02MB, 526 트리플)
- SEPT 인보이스 (2025-09)
- 처리 결과 초기 버전

**3. `invoice_SEPT_20251020_002513.ttl`** (0.02MB, 475 트리플)
- SEPT 인보이스 (2025-09) 수정본
- 최종 검증 버전

#### 시트 데이터 (3개)

**시트 9, 10, 12**:
- 각 0.003MB, 90 트리플
- 원본 Excel에서 추출
- HVDC 코드 6개 컬럼 포함

**용도**: 특정 시트 분석 및 검증용

---

## JSON 파일 설명

### A. GPT 캐시 (3개 파일)

#### `cases_by_flow.json`

**위치**: `03_data/json/gpt_cache/`
**구조**: Flow Code별 집계 배열

```json
[
  { "flow_code": "0", "case_count": 172 },
  { "flow_code": "1", "case_count": 3682 },
  { "flow_code": "2", "case_count": 4391 },
  { "flow_code": "3", "case_count": 750 }
]
```

**용도**: GPT가 빠르게 Flow 분포 조회 시 사용

---

#### `monthly_warehouse_inbound.json`

**위치**: `03_data/json/gpt_cache/`
**구조**: 월별/창고별 입고 집계

```json
[
  {
    "month": "2024-01",
    "warehouse": "MIR",
    "event_count": 5,
    "total_quantity": 5.0
  }
]
```

**주요 창고**:
- MIR (Mirfa), SHU (Shuweihat)
- MOSB (중앙 허브)
- AGI (Al Ghallan Island), DAS (Das Island)

**용도**: 월별 창고별 트래픽 분석

---

#### `vendor_summary.json`

**위치**: `03_data/json/gpt_cache/`
**구조**: 공급업체별 집계

```json
[
  {
    "vendor": "SAS Power",
    "month": "2025-05",
    "event_count": 20,
    "total_quantity": 20.0
  }
]
```

**용도**: 공급업체별 물류 현황 추적

---

### B. 통합 데이터 (10개 파일)

#### `unified_network_data_v12_hvdc.json`

**위치**: `03_data/json/integration/`
**크기**: 대용량 네트워크 그래프
**구조**: NetworkX 그래프 포맷

```json
{
  "directed": false,
  "multigraph": false,
  "graph": { "name": "UNIFIED_LOGISTICS_NETWORK_v12_HVDC" },
  "nodes": [
    {
      "type": "root",
      "ontology_class": "Project",
      "label": "HVDC Project",
      "level": 0,
      "color": "#ff0000",
      "community_id": 1,
      "id": "HVDC_Project"
    },
    {
      "type": "system",
      "ontology_class": "System",
      "label": "JPT71 System",
      "level": 1,
      "color": "#ff6b6b",
      "community_id": 0,
      "id": "JPT71_System"
    }
  ],
  "edges": [...]
}
```

**노드 타입**:
- `root`: 최상위 프로젝트
- `system`: 시스템 (ABU, JPT71, HVDC)
- `port`: 항만 (Zayed, Khalifa, Jebel Ali)
- `warehouse`: 창고 (DSV, DHL 등)
- `hub`: 허브 (MOSB)
- `site`: 현장 (MIR, SHU, AGI, DAS)

**용도**:
- 네트워크 시각화 (GraphX, Cytoscape)
- 도메인 분석 (community_id)
- 연결도 분석 (edges)

---

#### `metadata.json`

**위치**: `03_data/json/integration/`
**구조**: RDF 파일 메타데이터

```json
{
  "rdf_files_metadata": {
    "generated_date": "2025-10-22T10:00:00Z",
    "total_files": 16,
    "final_files": 2,
    "version_files": 14,
    "total_size_mb": 10.2,
    "files": { ... },
    "statistics": { ... },
    "organization_notes": { ... }
  }
}
```

**용도**: 파일 인벤토리 및 버전 관리

---

#### `processing_summary.json`

**위치**: `03_data/json/integration/`
**구조**: Excel 변환 처리 결과

```json
{
  "timestamp": "2025-10-19T20:35:09.184642",
  "input_file": "HVDC_입고로직_종합리포트_20251019_165153_v3.0-corrected.xlsx",
  "analysis": {
    "sheet_9": { "rows": 1000, "columns": 69, ... },
    "sheet_10": { "rows": 7161, "columns": 69, ... },
    "sheet_12": { "rows": 7161, "columns": 69, ... }
  },
  "results": { ... },
  "summary": {
    "total_sheets": 12,
    "hvdc_sheets_processed": 3,
    "success_count": 3,
    "success_rate": 1.0
  }
}
```

**용도**: TTL 변환 품질 추적

---

#### 기타 통합 파일

**`abu_lightning_comparison_data.json`**:
- ABU vs Lightning 비교 분석
- 시각화 준비 데이터

**`unified_network_stats*.json`** (4개):
- `_v12_hvdc`, `_meta`, `_stats`: 통계 변형
- 노드/엣지 수, 커뮤니티 분포

**`integration_data*.json`** (2개):
- `_meaningful`, 기본: 의미적 연결 데이터
- 크로스 도메인 매핑

---

### C. 리포트 (18개 파일)

#### 아부다비 리포트 (9개)

**1. `abu_comprehensive_summary.json`**
- 종합 요약: 모든 ABU 데이터
- 통계, 비율, 추세

**2. `abu_data_summary.json`**
- 데이터 요약: 행/컬럼/누락값
- 시트별 메타데이터

**3. `abu_dhabi_logistics_tag_dict_v1.json`**
- 태그 사전: 로직 태그 → 설명
- 표준화된 용어집

**4. `abu_guidelines_analysis.json`**
- 가이드라인 준수 분석
- 규정 위반 사례

**5. `abu_integrated_stats.json`**
- 통합 통계: 파일 종합
- 트리플/엔티티/관계 수

**6. `abu_lpo_analysis.json`**
- LPO 분석: 구매 주문 상세
- 책임자/날짜/양 추적

**7. `abu_responsible_persons_analysis.json`**
- 책임자 분석: 인물별 활동
- 타임라인 및 패턴

**8. `abu_sparql_analysis_data.json`**
- SPARQL 쿼리 결과
- 그래프 분석 산출물

**9. `abu_whatsapp_analysis.json`**
- WhatsApp 통신 분석
- 메시지 패턴 및 빈도

---

#### Lightning 리포트 (3개)

**1. `lightning_entities_stats.json`**
```json
{
  "total_entities": 321,
  "total_messages": 4671,
  "entity_counts": {
    "vessels": 33,
    "locations": 23,
    "operations": 31,
    "cargo": 27,
    "persons": 14,
    "times": 193
  }
}
```

**2. `lightning_images_stats.json`**
- 이미지 메타데이터 통계
- 파일 크기, 타입 분포

**3. `lightning_integrated_stats.json`**
- Lightning 통합 통계
- 엔티티/관계/이미지 총합

---

#### 인보이스 리포트 (2개)

**1. `invoice_analysis_report.json`**
- 인보이스 상세 분석 리포트
- 7,504줄, 1,000개 샘플 분석

**구조**:
```json
{
  "analysis": {
    "file_path": "data/invoice_sept2025.xlsm",
    "file_name": "invoice_sept2025.xlsm",
    "analysis_date": "2025-10-20T00:06:33",
    "sheets": {
      "SEPT": {
        "name": "SEPT",
        "dimensions": "34 rows x 27 columns",
        "total_cells": 918,
        "non_empty_cells": "548"
      }
    }
  }
}
```

**2. `invoice_data_summary.json`**
- 인보이스 데이터 요약
- 시트별 행/컬럼/비율

---

#### 강화/보완 통계 (2개)

**1. `enhancement_stats.json`**
- 데이터 강화 통계
- 보강된 필드 수

**2. `enrichment_stats.json`**
```json
{
  "original_triples": 65730,
  "enriched_triples": 66710,
  "new_triples": 980,
  "csv_stats": {
    "Document": { "unique": 22, "total_mentions": 1654 },
    "Equipment": { "unique": 23, "total_mentions": 1076 },
    "Operation": { "unique": 34, "total_mentions": 4552 },
    ...
  },
  "added_counts": { ... }
}
```

---

#### WhatsApp 분석 (2개)

**1. `whatsapp_images_analysis.json`**
- WhatsApp 이미지 분석
- 촬영일/파일명/크기 패턴

**2. `whatsapp_integration_stats.json`**
- WhatsApp 통합 통계
- 메시지 수, 엔티티 추출

---

### D. 검증 데이터 (5개 파일)

#### `validation_summary.json`

**위치**: `03_data/json/validation/`
**구조**: 전체 검증 지표

```json
{
  "timestamp": "2025-10-30T21:11:05.508832",
  "source_ttl": "rdf_output/test_data_wh_events.ttl",
  "total_triples": 72692,
  "validation_results": {
    "human_gate_flow23": {
      "count": 0,
      "file": "validation_results\\human_gate_flow23_no_inbound.json"
    },
    "missing_dates": {
      "count": 0,
      "file": "validation_results\\human_gate_missing_dates.json"
    },
    "coverage_stats": {
      "total_cases": 8995,
      "with_inbound": 5012,
      "with_outbound": 2381,
      "with_both": 1194,
      "with_neither": 2796,
      "inbound_coverage_pct": 55.72,
      "outbound_coverage_pct": 26.47
    },
    "flow_patterns": [
      {
        "flow_code": "0",
        "total_cases": 172,
        "with_inbound": 0,
        "with_outbound": 0,
        "inbound_pct": 0.0,
        "outbound_pct": 0.0
      },
      ...
    ]
  }
}
```

**검증 항목**:
1. **Human Gate Flow 2/3**: Inbound 이벤트 없는 Flow 2/3 사례
2. **Missing Dates**: 날짜 누락 사례
3. **Coverage Stats**: 이벤트 커버리지 통계
4. **Flow Patterns**: Flow별 이벤트 패턴

**용도**: 데이터 품질 보증 및 리포팅

---

#### `event_coverage_stats.json`

**구조**: 이벤트 커버리지 상세

```json
{
  "total_cases": 8995,
  "with_inbound": 5012,
  "with_outbound": 2381,
  "with_both": 1194,
  "with_neither": 2796,
  "inbound_coverage_pct": 55.72,
  "outbound_coverage_pct": 26.47
}
```

**의미**:
- `with_inbound`: 입고 이벤트 있음
- `with_outbound`: 출고 이벤트 있음
- `with_both`: 입고+출고 둘 다
- `with_neither`: 둘 다 없음 (Pre Arrival 가능)

---

#### `flow_event_patterns.json`

**구조**: Flow별 이벤트 패턴

각 Flow Code별로:
- 총 케이스 수
- Inbound 비율
- Outbound 비율

**패턴 예시**:
- Flow 1 (Port → Site): Inbound 100%, Outbound 0%
- Flow 3 (Port → MOSB → Site): Inbound 98.4%, Outbound 100%

---

#### Human Gate 파일 (2개)

**1. `human_gate_flow23_no_inbound.json`**
- Flow 2/3 중 Inbound 없는 사례
- 인간 검토 필요 항목

**2. `human_gate_missing_dates.json`**
- 날짜 누락 사례
- 데이터 보완 필요

---

## 사용 예시

### RDFLib로 TTL 파일 로드하기

```python
from rdflib import Graph, Namespace

# 그래프 로드
g = Graph()
g.parse("ontology_data_hub/03_data/ttl/current/hvdc_status_v35.ttl", format='turtle')

# Namespace 정의
hvdc = Namespace("http://samsung.com/project-logistics#")

# Flow Code 분포 쿼리
query = """
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?case ?flowCode WHERE {
  ?case a hvdc:Case ;
        hvdc:hasFlowCode ?flowCode .
}
LIMIT 10
"""

for row in g.query(query):
    print(f"Case: {row.case}, Flow: {row.flowCode}")
```

### JSON으로 빠른 통계 조회하기

```python
import json

# Flow 분포 로드
with open('ontology_data_hub/03_data/json/gpt_cache/cases_by_flow.json') as f:
    flow_dist = json.load(f)

# 통계 출력
for item in flow_dist:
    print(f"Flow {item['flow_code']}: {item['case_count']} cases")
```

### TTL과 JSON 데이터 상호 참조

```python
import json
from rdflib import Graph, Namespace

# TTL 로드
g = Graph()
g.parse("ontology_data_hub/03_data/ttl/current/hvdc_status_v35.ttl", format='turtle')

# JSON 검증 데이터 로드
with open('ontology_data_hub/03_data/json/validation/validation_summary.json') as f:
    validation = json.load(f)

# 검증: TTL 케이스 수 vs JSON 통계
ttl_count = len(list(g.subjects(Namespace("http://samsung.com/project-logistics#").hasFlowCode, None)))
json_total = validation['validation_results']['coverage_stats']['total_cases']

print(f"TTL cases: {ttl_count}, JSON total: {json_total}")
```

### 주요 SPARQL 쿼리

**Flow 3 (AGI/DAS) 케이스 조회**:
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?case ?vendor ?location WHERE {
  ?case a hvdc:Case ;
        hvdc:hasFlowCode "3" ;
        hvdc:hasVendor ?vendor ;
        hvdc:hasFinalLocation ?location .
}
```

**월별 입고 집계**:
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT (YEAR(?date) AS ?year) (MONTH(?date) AS ?month)
       (COUNT(?event) AS ?count)
WHERE {
  ?case hvdc:hasInboundEvent ?event .
  ?event hvdc:hasEventDate ?date .
}
GROUP BY ?year ?month
ORDER BY ?year ?month
```

---

## 빠른 참조

### TTL 파일 요약

| 파일명 | 크기 | 트리플 | 용도 |
|--------|------|--------|------|
| `hvdc_status_v35.ttl` | 9.6MB | 9,904 | 현재 운영 데이터 |
| `abu_final.ttl` | 0.9MB | 18,894 | ABU 최종 |
| `lightning_final.ttl` | 3.1MB | 67,000 | Lightning 최종 |
| `abu_logistics_data.ttl` | 0.1MB | 2,814 | ABU 경량 |
| `lightning_integrated_system.ttl` | 3.0MB | 65,000 | Lightning 기본 |
| `sheet_10_hvdc_data.ttl` | 0.003MB | 90 | 시트 10 |

### JSON 파일 요약

| 파일명 | 카테고리 | 구조 | 용도 |
|--------|----------|------|------|
| `cases_by_flow.json` | GPT 캐시 | 배열 | Flow 분포 |
| `monthly_warehouse_inbound.json` | GPT 캐시 | 배열 | 월별 입고 |
| `vendor_summary.json` | GPT 캐시 | 배열 | 업체별 통계 |
| `unified_network_data_v12_hvdc.json` | 통합 | 그래프 | 네트워크 분석 |
| `metadata.json` | 통합 | 객체 | 파일 메타 |
| `validation_summary.json` | 검증 | 객체 | 품질 검증 |
| `abu_comprehensive_summary.json` | 리포트 | 객체 | ABU 종합 |
| `lightning_entities_stats.json` | 리포트 | 객체 | Lightning 통계 |

### TTL 속성 인덱스

| 속성 | 설명 | 타입 |
|------|------|------|
| `hasCBM` | 화물 용적 (㎥) | Float |
| `hasFlowCode` | 물류 흐름 코드 (0-5) | String |
| `hasFlowCodeOriginal` | 원본 Flow Code | Int |
| `hasFlowDescription` | Flow 설명 | String |
| `hasFlowOverrideReason` | Override 사유 | String |
| `hasHvdcCode` | HVDC 코드 | String |
| `hasVendor` | 공급업체 | String |
| `hasFinalLocation` | 최종 도착지 | String |
| `hasInboundEvent` | 입고 이벤트 | BlankNode |
| `hasOutboundEvent` | 출고 이벤트 | BlankNode |
| `hasEventDate` | 이벤트 날짜 | Date |
| `hasLocationAtEvent` | 이벤트 위치 | String |
| `hasQuantity` | 이벤트 수량 | Float |

### JSON 필드 인덱스

| 필드 | 설명 | 타입 | 파일 예시 |
|------|------|------|-----------|
| `flow_code` | Flow 코드 | String | `cases_by_flow.json` |
| `case_count` | 케이스 수 | Int | `cases_by_flow.json` |
| `month` | 월 (YYYY-MM) | String | `monthly_warehouse_inbound.json` |
| `warehouse` | 창고 코드 | String | `monthly_warehouse_inbound.json` |
| `event_count` | 이벤트 수 | Int | `monthly_warehouse_inbound.json` |
| `total_quantity` | 총 수량 | Float | `monthly_warehouse_inbound.json` |
| `vendor` | 공급업체 | String | `vendor_summary.json` |
| `total_cases` | 총 케이스 | Int | `validation_summary.json` |
| `with_inbound` | Inbound 있음 | Int | `validation_summary.json` |
| `with_outbound` | Outbound 있음 | Int | `validation_summary.json` |
| `inbound_coverage_pct` | Inbound 커버리지 | Float | `validation_summary.json` |
| `timestamp` | 타임스탬프 | String | `validation_summary.json` |
| `nodes` | 네트워크 노드 | Array | `unified_network_data*.json` |
| `edges` | 네트워크 엣지 | Array | `unified_network_data*.json` |

---

## 파일 간 관계

### 검증 체인

```
TTL 데이터
    ↓
[RDFLib 파싱]
    ↓
validation_summary.json
    ↓
human_gate_*.json
```

**예시**: `hvdc_status_v35.ttl` → `validation_summary.json` → `human_gate_flow23_no_inbound.json`

---

### 캐시 체인

```
TTL 데이터
    ↓
[SPARQL 집계]
    ↓
cases_by_flow.json
monthly_warehouse_inbound.json
vendor_summary.json
```

**예시**: TTL → Flow Code 집계 → `cases_by_flow.json`

---

### 리포트 체인

```
TTL 데이터
    ↓
[도메인 분석]
    ↓
abu_comprehensive_summary.json
lightning_entities_stats.json
invoice_analysis_report.json
```

**예시**: `abu_*.ttl` → ABU 분석 → `abu_comprehensive_summary.json`

---

### 통합 체인

```
여러 TTL 파일
    ↓
[네트워크 통합]
    ↓
unified_network_data_v12_hvdc.json
    ↓
metadata.json
processing_summary.json
```

**예시**: ABU + Lightning TTL → 네트워크 그래프 → `unified_network_data_v12_hvdc.json`

---

## 결론

이 가이드는 `ontology_data_hub`의 68개 TTL/JSON 파일을 체계적으로 설명합니다. 각 파일의 내용, 구조, 용도를 파악하고, 서로의 관계를 이해하여 효과적으로 데이터를 활용할 수 있도록 지원합니다.

**주요 활용 사례**:
1. 실시간 쿼리: `hvdc_status_v35.ttl` 사용
2. 빠른 집계: GPT 캐시 JSON 사용
3. 품질 검증: validation JSON 확인
4. 도메인 분석: 리포트 JSON 조회
5. 통합 분석: 통합 데이터 JSON 활용

**다음 단계**:
- [MASTER_INDEX.md](05_cross_references/MASTER_INDEX.md) - 전체 인덱스
- [QUERY_TEMPLATES.md](05_cross_references/QUERY_TEMPLATES.md) - SPARQL 예시
- [USAGE_GUIDE.md](05_cross_references/USAGE_GUIDE.md) - 사용 가이드

---

**생성**: 2025-11-01
**버전**: 1.0
**작성자**: AI Assistant


