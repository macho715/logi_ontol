# Flow Code v3.5 통합 문서

**작성일**: 2025-01-25
**프로젝트**: HVDC Logistics Ontology - Flow Code v3.5 통합
**버전**: v3.5
**상태**: ✅ **완료**

---

## 📋 목차

1. [개요](#개요)
2. [변경사항 요약](#변경사항-요약)
3. [온톨로지 통합](#온톨로지-통합)
4. [구현 파일 위치](#구현-파일-위치)
5. [테스트](#테스트)
6. [검증 결과](#검증-결과)
7. [사용법](#사용법)

---

## 개요

Flow Code v3.5는 HVDC 프로젝트의 물류 흐름을 0~5 범위로 분류하는 알고리즘으로, v3.4 대비 다음과 같이 확장되었습니다:

- **Flow Code 범위**: 0~4 → **0~5**
- **계산 방식**: 산술 계산 + clip → **관측 기반 규칙 적용**
- **AGI/DAS 처리**: 없음 → **도메인 룰 강제 적용**
- **혼합 케이스**: 없음 → **Flow 5로 명시적 분류**
- **원본 값 보존**: 없음 → **FLOW_CODE_ORIG 컬럼**
- **오버라이드 추적**: 없음 → **FLOW_OVERRIDE_REASON 컬럼**

---

## 변경사항 요약

### Flow Code 정의 (v3.5)

| Flow Code | 설명 | 패턴 | 주요 변경점 |
|-----------|------|------|-------------|
| **0** | Pre Arrival | - | v3.4과 동일 |
| **1** | Port → Site | 직접 배송 | v3.4과 동일 |
| **2** | Port → WH → Site | 창고 경유 | WH≥1 (v3.4에서는 WH=1) |
| **3** | Port → MOSB → Site | MOSB 경유 | **AGI/DAS 필수** 추가 |
| **4** | Port → WH → MOSB → Site | 창고+MOSB 경유 | v3.4과 동일 |
| **5** | Mixed/Waiting/Incomplete | 혼합/미완료 | **신규 추가** |

### 주요 알고리즘 흐름

```
[입력 데이터]
    ↓
[1단계] 필드 검증 및 전처리
    ↓
[2단계] 관측값 계산 (WH 개수, MOSB 존재, Site 존재)
    ↓
[3단계] 기본 Flow Code 계산 (0~4)
    ↓
[4단계] AGI/DAS 도메인 오버라이드 (0/1/2 → 3) ⭐
    ↓
[5단계] 혼합 케이스 처리 (→ 5) ⭐
    ↓
[6단계] 검증 및 최종 반영
    ↓
[출력] FLOW_CODE, FLOW_DESCRIPTION, FLOW_CODE_ORIG, FLOW_OVERRIDE_REASON
```

---

## 온톨로지 통합

### 1. Core 온톨로지 문서

#### `core/1_CORE-08-flow-code.md`
- **버전**: unified-3.4 → **unified-3.5**
- **날짜**: 2025-10-26 → **2025-10-31**
- **태그**: `agi-das`, `offshore` 추가

**주요 업데이트**:
- Flow Code 범위: 0~5
- AGI/DAS 도메인 룰 SHACL 제약 추가
- v3.5 알고리즘 업그레이드 섹션 추가
- JSON-LD 예제 3개 (일반, AGI 강제 승급, 혼합 케이스)
- AGI/DAS Domain Rule Validation SPARQL 추가

#### `core_consolidated/CONSOLIDATED-02-warehouse-flow.md`
- **버전**: consolidated-1.0 → **consolidated-1.0-v3.5**
- **날짜**: 2025-10-26 → **2025-10-31**
- **태그**: `agi-das` 추가
- **source_files**: `FLOW_CODE_V35_ALGORITHM.md` 추가

**주요 업데이트**:
- Flow Control Layer: Flow Code(0~5) v3.5로 업데이트
- FlowCode 클래스: 0~5로 업데이트
- Rule-7: hasLogisticsFlowCode ∈ {0,1,2,3,4,5}
- Rule-8A: AGI/DAS 도메인 룰 추가
- Rule-8B: Flow Code 5 조건 추가
- SHACL 검증: minInclusive 0, maxInclusive 5
- Fail-safe 테이블: Flow Code > 5로 업데이트

### 2. 온톨로지 스키마 파일

#### `logiontology/configs/ontology/hvdc_event_schema.ttl`

**신규 속성 추가**:
```turtle
hvdc:hasFlowCodeOriginal a owl:DatatypeProperty ;
    rdfs:domain hvdc:Case ;
    rdfs:range xsd:integer ;
    rdfs:comment "도메인 룰 적용 전 원본 Flow Code (v3.5 추적용)"@ko .

hvdc:hasFlowOverrideReason a owl:DatatypeProperty ;
    rdfs:domain hvdc:Case ;
    rdfs:range xsd:string ;
    rdfs:comment "Flow Code 오버라이드 사유 (예: AGI/DAS requires MOSB leg)"@ko .

hvdc:hasFlowDescription a owl:DatatypeProperty ;
    rdfs:domain hvdc:Case ;
    rdfs:range xsd:string ;
    rdfs:comment "Flow Code 패턴 설명 (예: Flow 3: Port → MOSB → Site)"@ko .

hvdc:hasFinalLocation a owl:DatatypeProperty ;
    rdfs:domain hvdc:Case ;
    rdfs:range xsd:string ;
    rdfs:comment "최종 위치 (자동 추출된 값)"@ko .
```

**기존 속성 업데이트**:
```turtle
hvdc:hasFlowCode a owl:DatatypeProperty ;
    rdfs:range xsd:string ;
    rdfs:comment "물류 흐름 코드 (0=Pre Arrival, 1=직송, 2=창고경유, 3=MOSB경유, 4=창고+MOSB, 5=혼합/미완료)"@ko .
```

---

## 구현 파일 위치

### 알고리즘 구현

#### `logiontology/src/ingest/flow_code_calculator.py` (신규)
- `normalize_column_names()`: 컬럼명 정규화
- `extract_final_location()`: Site 컬럼에서 최종 위치 추출
- `is_pre_arrival()`: ATA 또는 날짜 컬럼 기반 Pre Arrival 판별
- `calculate_flow_code_v35()`: 관측값 → Flow Code 0~5 + AGI/DAS 오버라이드

#### `logiontology/src/ingest/excel_to_ttl_with_events.py` (수정)
- `flow_version` 파라미터 추가 (기본값: "3.5")
- Flow Code v3.5 계산 자동 실행
- 이벤트 주입 로직 확장 (Flow 0, 4, 5 지원)
- TTL 속성 추가 (FLOW_CODE_ORIG, FLOW_OVERRIDE_REASON, FLOW_DESCRIPTION, Final_Location)

#### `scripts/convert_data_wh_to_ttl.py` (수정)
- `--flow-version` CLI 옵션 추가 (예정)

### 검증 파일

#### `tests/test_flow_code_v35.py` (신규)
단위 테스트: 12개
- 컬럼명 정규화
- Final_Location 추출
- Pre Arrival 판별
- Flow 0~5 계산
- AGI/DAS 강제 승급

#### `tests/test_flow_code_v35_validation.py` (신규)
TTL 검증 테스트: 7개
- AGI/DAS 도메인 룰 검증
- Flow 5 혼합 케이스 검증
- Flow Code 분포 검증

---

## 테스트

### 실행 방법

```bash
# 단위 테스트
python -m pytest tests/test_flow_code_v35.py -v

# TTL 검증 테스트
python -m pytest tests/test_flow_code_v35_validation.py -v

# 전체 Flow Code 관련 테스트
python -m pytest tests/ -k "flow_code" -v
```

### 테스트 결과

```
test_flow_code_v35.py: 12 passed in 0.73s
test_flow_code_v35_validation.py: 7 passed in 0.86s

Total: 19 passed
```

---

## 검증 결과

### 실제 데이터 변환

**Excel 파일**: `HVDC STATUS(20250815) (1).xlsx`
- **총 행**: 755
- **컬럼**: 80개

**Flow Code 분포**:
```
Flow 0 (Pre Arrival):    71건 (9.4%)
Flow 1 (Port → Site):   255건 (33.8%)
Flow 2 (Port → WH → Site): 152건 (20.1%)
Flow 3 (Port → MOSB → Site): 131건 (17.4%)
Flow 4 (Port → WH → MOSB → Site): 65건 (8.6%)
Flow 5 (Mixed/Incomplete): 81건 (10.7%)
```

**이벤트 생성**:
- Inbound 이벤트: 573건
- Outbound 이벤트: 245건
- 스킵된 케이스: 152건

**AGI/DAS 강제 승급**:
- 총 승급: 31건
- 사유: "AGI/DAS requires MOSB leg"
- 검증: AGI/DAS 케이스 중 Flow < 3인 것 0건 ✅

### SPARQL 검증

AGI/DAS 도메인 룰 준수:
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (COUNT(?case) AS ?violations)
WHERE {
    ?case hvdc:hasFinalLocation ?loc .
    FILTER(?loc IN ("AGI", "DAS"))
    ?case hvdc:hasFlowCode ?flow .
    FILTER(xsd:integer(?flow) < 3)
}
```

**결과**: violations = 0 ✅

---

## 사용법

### Python 코드에서 사용

```python
from logiontology.src.ingest.flow_code_calculator import calculate_flow_code_v35

# DataFrame 준비
warehouse_columns = [
    "DSV Indoor", "DSV Outdoor", "DSV MZD", "JDN MZD", "JDN Waterfront",
    "MOSB", "AAA Storage", "Hauler DG Storage", "DHL WH", "DSV Al Markaz",
    "DSV MZP", "Hauler Indoor", "ZENER (WH)", "Vijay Tanks"
]
site_columns = ["SHU", "MIR", "DAS", "AGI"]

# Flow Code v3.5 계산
df = calculate_flow_code_v35(df, warehouse_columns, site_columns)

# 결과 확인
print(df[['FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_CODE_ORIG', 'FLOW_OVERRIDE_REASON', 'Final_Location']].head())
```

### Excel to TTL 변환

```python
from logiontology.src.ingest.excel_to_ttl_with_events import convert_data_wh_to_ttl_with_events

# TTL 변환 (Flow v3.5)
result = convert_data_wh_to_ttl_with_events(
    excel_path='HVDC STATUS(20250815) (1).xlsx',
    output_path='output/hvdc_status_v35.ttl',
    flow_version='3.5'
)

# 통계 확인
print(result)
```

### SPARQL 쿼리 예제

```sparql
# Flow Code 분포 분석 (v3.5)
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
    ?flowCode
    ?description
    (COUNT(?case) AS ?count)
WHERE {
    ?case hvdc:hasFlowCode ?flowCodeStr .
    BIND(xsd:integer(?flowCodeStr) AS ?flowCode)
    ?case hvdc:hasFlowDescription ?description .
}
GROUP BY ?flowCode ?description
ORDER BY ?flowCode
```

### AGI/DAS 강제 승급 케이스 추적

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT
    ?case
    ?flowCode
    ?flowCodeOrig
    ?overrideReason
    ?finalLocation
WHERE {
    ?case hvdc:hasFlowCode ?flowCode ;
          hvdc:hasFlowCodeOriginal ?flowCodeOrig ;
          hvdc:hasFlowOverrideReason ?overrideReason ;
          hvdc:hasFinalLocation ?finalLocation .
}
```

---

## 관련 문서

### 구현 문서
- **알고리즘 상세**: `FLOW_CODE_V35_ALGORITHM.md`
- **구현 완료**: `FLOW_CODE_V35_IMPLEMENTATION_COMPLETE.md`
- **통합 문서**: `FLOW_CODE_V35_INTEGRATION.md` (이 문서)

### 온톨로지 문서
- **Core**: `core/1_CORE-08-flow-code.md`
- **Consolidated**: `core_consolidated/CONSOLIDATED-02-warehouse-flow.md`

### 계획 문서
- **변환 계획**: `\data-wh-excel-to-ttl-conversion.plan.md`

---

## 다음 단계

### 선택적 작업

1. **CLI 옵션 업데이트**
   - `scripts/convert_data_wh_to_ttl.py`에 `--flow-version` 옵션 추가

2. **MCP 서버 연동**
   - `hvdc_mcp_server`에서 새 속성 지원 확인
   - SPARQL 쿼리 업데이트

3. **문서 보강**
   - 사용 예제 추가
   - FAQ 섹션 추가
   - Troubleshooting 가이드 작성

---

## 체크리스트

- [x] Flow Code v3.5 알고리즘 구현
- [x] 온톨로지 스키마 확장
- [x] Excel to TTL 변환 통합
- [x] 단위 테스트 작성 (12개)
- [x] TTL 검증 테스트 작성 (7개)
- [x] Core 온톨로지 문서 업데이트
- [x] Consolidated 온톨로지 문서 업데이트
- [x] 실제 데이터 변환 검증
- [x] AGI/DAS 도메인 룰 SPARQL 검증
- [x] 통합 문서 작성
- [ ] CLI 옵션 업데이트 (선택)
- [ ] MCP 서버 연동 테스트 (선택)

---

## 마이그레이션 가이드

### v3.4 → v3.5 전환

1. **스키마 업데이트**: `hvdc_event_schema.ttl` 로드
2. **코드 업데이트**: `flow_code_calculator.py` import
3. **변환 실행**: `flow_version='3.5'` 지정
4. **검증**: SPARQL로 AGI/DAS 룰 및 Flow 5 케이스 확인

### 호환성

- **하위 호환**: v3.4 데이터도 v3.5로 재처리 가능
- **상위 호환**: v3.5에서 v3.4로 다운그레이드 시 Flow 5 → Flow 4 처리

---

## 문제 해결

### 일반적인 문제

**문제**: Flow Code > 5 발생
**해결**: 스키마 업데이트 확인, 범위 검증 로직 확인

**문제**: AGI/DAS 강제 승급 작동 안 함
**해결**: Final_Location 컬럼 존재 여부 확인, 자동 추출 로직 확인

**문제**: 테스트 실패
**해결**: pytest 실행 시 `-v` 옵션 사용하여 상세 로그 확인

---

## 결론

Flow Code v3.5 알고리즘을 HVDC 이벤트 기반 온톨로지 시스템에 성공적으로 통합했습니다. 실제 Excel 데이터 변환, AGI/DAS 도메인 룰 적용, 혼합 케이스 분류, 이벤트 주입 등 모든 기능이 정상 작동하며, 온톨로지 문서와 스키마도 v3.5로 업데이트되었습니다.

**통계**:
- 총 케이스: 755
- Flow Code 분포: 균형잡힌 분포 (9%~34%)
- 이벤트 생성: 818건
- 테스트 통과: 19/19 (100%)
- AGI/DAS 검증: 완료 (위반 0건)

**상태**: 프로덕션 사용 준비 완료 ✅

