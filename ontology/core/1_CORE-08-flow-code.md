> **⚠️ 중요**: 이 문서를 읽기 전에 **`../logiontology/`** 폴더를 먼저 확인하세요!
> - **전체 구현 코드**: `../logiontology/src/`
> - **설정 파일**: `../logiontology/configs/`
> - **온톨로지 정의**: `../logiontology/configs/ontology/hvdc_ontology.ttl`
> - **문서**: `../logiontology/README.md`, `../logiontology/CHANGELOG.md`

---

---
title: "HVDC Flow Code Algorithm Ontology"
type: "ontology-design"
domain: "flow-code-logistics"
sub-domains: ["warehouse-routing", "logistics-flow", "path-optimization"]
version: "unified-3.4"
date: "2025-10-26"
tags: ["ontology", "flow-code", "warehouse", "routing", "algorithm", "hvdc"]
standards: ["Python-Algorithm", "Pandas", "NumPy"]
status: "active"
source: "hvdc_excel_reporter_final_sqm_rev.py"
---

# hvdc-flow-code-algorithm · 1_CORE-08

## Executive Summary

Flow Code Algorithm Ontology는 HVDC 프로젝트의 복잡한 물류 흐름을 정량화하는 핵심 시스템입니다. 5단계 Flow Code(0-4)를 통해 창고 경유 패턴, 직송 비율, MOSB 해상운송 활용도 등 핵심 KPI를 산출하며, 물류 최적화와 비용 효율성 분석의 기반이 됩니다.

## Visual Ontology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Flow Code Algorithm                     │
├─────────────────────────────────────────────────────────────┤
│  Part 1: Ontology System  │  Part 2: Implementation  │  Part 3: Integration  │
├─────────────────────────────────────────────────────────────┤
│  • FlowCode Classes       │  • Calculation Logic    │  • Warehouse vs MOSB │
│  • Flow Path Relations    │  • Bug Fixes (v3.4)     │  • KPI Applications   │
│  • Constraint Rules       │  • Data Preprocessing    │  • Cross-references   │
└─────────────────────────────────────────────────────────────┘
```

## Part 1: Flow Code Ontology System

### Domain Ontology

#### Core Classes

```turtle
# Flow Code Ontology Classes
hvdc:FlowCode a owl:Class ;
    rdfs:label "Flow Code" ;
    rdfs:comment "물류 흐름 패턴을 나타내는 코드 (0-4)" .

hvdc:LogisticsFlow a owl:Class ;
    rdfs:label "Logistics Flow" ;
    rdfs:comment "물류 흐름 경로" .

hvdc:WarehouseHop a owl:Class ;
    rdfs:label "Warehouse Hop" ;
    rdfs:comment "창고 경유 단계" .

hvdc:OffshoreTransport a owl:Class ;
    rdfs:label "Offshore Transport" ;
    rdfs:comment "MOSB 해상운송" .

hvdc:PreArrival a owl:Class ;
    rdfs:label "Pre Arrival" ;
    rdfs:comment "선적 전 단계" .
```

#### Data Properties

```turtle
# Flow Code Properties
hvdc:hasFlowCode a owl:DatatypeProperty ;
    rdfs:label "has flow code" ;
    rdfs:comment "물류 흐름 코드 값" ;
    rdfs:domain hvdc:LogisticsFlow ;
    rdfs:range xsd:integer .

hvdc:hasWHHandling a owl:DatatypeProperty ;
    rdfs:label "has warehouse handling count" ;
    rdfs:comment "창고 처리 횟수" ;
    rdfs:domain hvdc:LogisticsFlow ;
    rdfs:range xsd:integer .

hvdc:hasOffshoreFlag a owl:DatatypeProperty ;
    rdfs:label "has offshore flag" ;
    rdfs:comment "MOSB 해상운송 여부" ;
    rdfs:domain hvdc:LogisticsFlow ;
    rdfs:range xsd:boolean .

hvdc:hasFlowDescription a owl:DatatypeProperty ;
    rdfs:label "has flow description" ;
    rdfs:comment "물류 흐름 설명" ;
    rdfs:domain hvdc:LogisticsFlow ;
    rdfs:range xsd:string .
```

#### Object Properties

```turtle
# Flow Path Relations
hvdc:hasWarehouseHop a owl:ObjectProperty ;
    rdfs:label "has warehouse hop" ;
    rdfs:comment "창고 경유 관계" ;
    rdfs:domain hvdc:LogisticsFlow ;
    rdfs:range hvdc:WarehouseHop .

hvdc:hasOffshoreTransport a owl:ObjectProperty ;
    rdfs:label "has offshore transport" ;
    rdfs:comment "해상운송 관계" ;
    rdfs:domain hvdc:LogisticsFlow ;
    rdfs:range hvdc:OffshoreTransport .

hvdc:isPreArrival a owl:ObjectProperty ;
    rdfs:label "is pre arrival" ;
    rdfs:comment "선적 전 단계 여부" ;
    rdfs:domain hvdc:LogisticsFlow ;
    rdfs:range hvdc:PreArrival .
```

### Use-case별 제약

#### Rule-20: Flow Code Range Constraint
```turtle
hvdc:FlowCodeRangeShape a sh:NodeShape ;
    sh:targetClass hvdc:LogisticsFlow ;
    sh:property [
        sh:path hvdc:hasFlowCode ;
        sh:minInclusive 0 ;
        sh:maxInclusive 4 ;
        sh:message "Flow Code는 0-4 범위 내에 있어야 함"
    ] .
```

#### Rule-21: Flow Code Calculation Consistency
```turtle
hvdc:FlowCodeConsistencyShape a sh:NodeShape ;
    sh:targetClass hvdc:LogisticsFlow ;
    sh:property [
        sh:path hvdc:hasFlowCode ;
        sh:equals [
            sh:sparql """
                SELECT ?flowCode WHERE {
                    ?flow hvdc:hasWHHandling ?whCount .
                    ?flow hvdc:hasOffshoreFlag ?offshore .
                    BIND(IF(?offshore = true, 1, 0) + ?whCount + 1 AS ?calculated) .
                    BIND(IF(?calculated > 4, 4, ?calculated) AS ?flowCode) .
                }
            """
        ] ;
        sh:message "Flow Code 계산이 일관성 있어야 함"
    ] .
```

#### Rule-22: Pre Arrival Flow Code Constraint
```turtle
hvdc:PreArrivalFlowCodeShape a sh:NodeShape ;
    sh:targetClass hvdc:LogisticsFlow ;
    sh:property [
        sh:path hvdc:isPreArrival ;
        sh:hasValue true ;
        sh:property [
            sh:path hvdc:hasFlowCode ;
            sh:hasValue 0 ;
            sh:message "Pre Arrival은 Flow Code 0이어야 함"
        ]
    ] .
```

## Part 2: Algorithm Implementation

### Flow Code 정의 (Lines 308-315)

```python
self.flow_codes = {
    0: "Pre Arrival",
    1: "Port → Site",
    2: "Port → WH → Site",
    3: "Port → WH → MOSB → Site",
    4: "Port → WH → WH → MOSB → Site",
}
```

**5가지 물류 흐름 패턴:**
- **Code 0**: 선적 전 단계 (Pre Arrival)
- **Code 1**: 항구에서 현장 직송 (창고 경유 없음)
- **Code 2**: 항구 → 창고 1개 → 현장
- **Code 3**: 항구 → 창고 → MOSB(해상운송) → 현장
- **Code 4**: 항구 → 창고 2개 이상 → MOSB → 현장

---

### Flow Code 계산 알고리즘 (`_override_flow_code()` - Lines 563-622)

#### 입력 데이터 전처리 (Lines 568-584)

```python
# 창고 컬럼 분류 (MOSB 제외)
WH_COLS = [w for w in self.warehouse_columns if w != "MOSB"]
MOSB_COLS = [w for w in self.warehouse_columns if w == "MOSB"]

# 0값과 빈 문자열을 NaN으로 치환 (notna() 오류 방지)
for col in WH_COLS + MOSB_COLS:
    if col in self.combined_data.columns:
        self.combined_data[col] = self.combined_data[col].replace({0: np.nan, "": np.nan})
```

**목적**: 데이터 품질 보장 및 일관성 있는 null 값 처리

#### Pre Arrival 판별 (Lines 586-594)

```python
# 명시적 Pre Arrival 판별
status_col = "Status_Location"
if status_col in self.combined_data.columns:
    is_pre_arrival = self.combined_data[status_col].str.contains(
        "Pre Arrival", case=False, na=False
    )
else:
    is_pre_arrival = pd.Series(False, index=self.combined_data.index)
```

**로직**: `Status_Location` 컬럼에서 "Pre Arrival" 문자열 포함 여부로 선적 전 단계 감지

#### 핵심 계산 로직 (Lines 596-609)

```python
# 창고 Hop 수 계산
wh_cnt = self.combined_data[WH_COLS].notna().sum(axis=1)

# Offshore 계산 (MOSB 통과 여부)
offshore = self.combined_data[MOSB_COLS].notna().any(axis=1).astype(int)

# Flow Code 계산 (Off-by-One 버그 수정)
base_step = 1  # Port → Site 기본 1스텝
flow_raw = wh_cnt + offshore + base_step  # 1~5 범위

# Pre Arrival은 무조건 0, 나머지는 1~4로 클립
self.combined_data["FLOW_CODE"] = np.where(
    is_pre_arrival,
    0,  # Pre Arrival은 Code 0
    np.clip(flow_raw, 1, 4),  # 나머지는 1~4
)
```

**계산 공식:**
```
FLOW_CODE = {
    0                           if "Pre Arrival" in Status_Location
    clip(wh_count + offshore + 1, 1, 4)  otherwise
}

where:
- wh_count = 창고 컬럼(MOSB 제외)에서 날짜가 있는 개수
- offshore = MOSB 컬럼에 날짜가 있으면 1, 없으면 0
- base_step = 1 (Port → Site 기본값)
```

**예시:**
- 창고 0개 + offshore 0 + 1 = **1** (Port → Site 직송)
- 창고 1개 + offshore 0 + 1 = **2** (Port → WH → Site)
- 창고 1개 + offshore 1 + 1 = **3** (Port → WH → MOSB → Site)
- 창고 2개 + offshore 1 + 1 = **4** (Port → WH → WH → MOSB → Site)
- 창고 3개 이상이어도 **4**로 클립 (최대값 제한)

#### 설명 매핑 및 검증 (Lines 611-620)

```python
# 설명 매핑
self.combined_data["FLOW_DESCRIPTION"] = self.combined_data["FLOW_CODE"].map(
    self.flow_codes
)

# 디버깅 정보 출력
flow_distribution = self.combined_data["FLOW_CODE"].value_counts().sort_index()
logger.info(f" Flow Code 분포: {dict(flow_distribution)}")
logger.info(f" Pre Arrival 정확 판별: {is_pre_arrival.sum()}건")
```

---

### v3.4-corrected 버그 수정 내역 (Line 565)

**수정 전 문제:**
- Off-by-One 버그: Flow Code가 실제보다 1 낮게 계산됨
- Pre Arrival 정확 판별 실패

**수정 후:**
- `base_step = 1` 명시적 추가로 Port → Site 기본값 보장
- `Status_Location` 기반 Pre Arrival 정확 판별
- `np.clip(flow_raw, 1, 4)` 범위 제한으로 안정성 강화

## Part 3: Operational Integration

### 창고 vs MOSB 구분 로직

**창고 컬럼 (Lines 216-227):**
```python
self.warehouse_columns = [
    "DHL WH", "DSV Indoor", "DSV Al Markaz", "Hauler Indoor",
    "DSV Outdoor", "DSV MZP", "HAULER", "JDN MZD",
    "MOSB", "AAA Storage"
]
```

**MOSB 특별 처리:**
- MOSB는 창고이지만 **offshore 해상운송** 특성으로 별도 카운트
- `wh_cnt`에서는 제외, `offshore` 변수로 독립 계산
- MOSB 통과 시 Flow Code +1 증가 효과

### Flow Code 활용 사례

#### 직접 배송 계산 (Lines 1099-1137)

```python
def calculate_direct_delivery(self, df: pd.DataFrame) -> Dict:
    """직접 배송 계산 (Port → Site)"""
    for idx, row in df.iterrows():
        # Flow Code가 1인 경우 (Port → Site)
        if row.get("FLOW_CODE") == 1:
            # 현장으로 직접 이동한 항목들
```

#### Flow 분석 시트 (Lines 1937-1957)

```python
def create_flow_analysis_sheet(self, stats: Dict) -> pd.DataFrame:
    """Flow Code 분석 시트 생성"""
    flow_summary = df.groupby("FLOW_CODE").size().reset_index(name="Count")
    flow_summary["FLOW_DESCRIPTION"] = flow_summary["FLOW_CODE"].map(
        self.calculator.flow_codes
    )
```

#### Flow Traceability Dashboard (Lines 1739-1885)

**KPI 계산에 활용:**
- MOSB 통과율 (MOSB Pass Rate)
- 직송 비율 (Direct Flow Rate) - Flow Code 1 비율
- 창고 평균 체류 일수 (Avg WH Dwell Days)

### 알고리즘 강점

1. **명확한 물류 패턴 분류**: 5단계로 모든 물류 흐름 커버
2. **견고한 예외 처리**: null 값, 빈 문자열 사전 정규화
3. **정확한 Pre Arrival 판별**: Status_Location 기반 검증
4. **Off-by-One 버그 수정**: v3.4에서 완전히 해결
5. **범위 제한**: np.clip으로 1-4 범위 보장
6. **추적 가능성**: 분포 로그 및 검증 메커니즘 내장

### 제한사항 및 가정

1. **최대 Flow Code 4**: 창고 3개 이상 경유 시에도 4로 클립
2. **MOSB 특수성**: 창고이지만 offshore로 별도 처리
3. **Status_Location 의존**: Pre Arrival 판별이 이 컬럼에 의존
4. **날짜 기반 판단**: 창고 컬럼에 날짜가 있으면 경유로 간주

## JSON-LD Example

```json
{
  "@context": {
    "hvdc": "https://hvdc-project.com/ontology/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "hvdc:flow-example-001",
  "@type": "hvdc:LogisticsFlow",
  "hvdc:hasFlowCode": 2,
  "hvdc:hasWHHandling": 1,
  "hvdc:hasOffshoreFlag": false,
  "hvdc:hasFlowDescription": "Port → WH → Site",
  "hvdc:hasWarehouseHop": {
    "@type": "hvdc:WarehouseHop",
    "hvdc:warehouseName": "DSV Indoor"
  }
}
```

## SPARQL Queries

### Flow Code 분포 분석
```sparql
PREFIX hvdc: <https://hvdc-project.com/ontology/>

SELECT ?flowCode ?description (COUNT(?flow) AS ?count)
WHERE {
    ?flow hvdc:hasFlowCode ?flowCode .
    ?flow hvdc:hasFlowDescription ?description .
}
GROUP BY ?flowCode ?description
ORDER BY ?flowCode
```

### MOSB 통과율 계산
```sparql
PREFIX hvdc: <https://hvdc-project.com/ontology/>

SELECT
    (COUNT(?offshoreFlow) AS ?offshoreCount)
    (COUNT(?totalFlow) AS ?totalCount)
    ((COUNT(?offshoreFlow) * 100.0 / COUNT(?totalFlow)) AS ?mosbPassRate)
WHERE {
    ?totalFlow a hvdc:LogisticsFlow .
    OPTIONAL {
        ?offshoreFlow hvdc:hasOffshoreFlag true .
    }
}
```

## Semantic KPI Layer

### Flow Code Distribution
- **Direct Flow Rate**: Flow Code 1 비율 (직송 효율성)
- **Warehouse Utilization**: Flow Code 2-4 비율 (창고 활용도)
- **MOSB Pass Rate**: Offshore Transport 비율 (해상운송 활용도)
- **Pre Arrival Ratio**: Flow Code 0 비율 (선적 전 단계 비율)

### Performance Metrics
- **Average Flow Complexity**: 평균 Flow Code 값
- **Flow Code Variance**: Flow Code 분산 (물류 패턴 다양성)
- **Optimization Potential**: Flow Code 4 → 1 전환 가능성

## 추천 명령어

- `/flow-code analyze --distribution` [Flow Code 분포 분석]
- `/flow-code validate --strict` [Flow Code 일관성 검증]
- `/flow-code optimize --target=1` [직송 최적화 분석]
- `/mosb-pass-rate calculate` [MOSB 통과율 계산]
- `/warehouse-efficiency analyze` [창고 효율성 분석]

이 Flow Code 알고리즘은 HVDC 프로젝트의 복잡한 물류 흐름을 정량화하여 창고 경유 패턴, 직송 비율, MOSB 해상운송 활용도 등 핵심 KPI 산출의 기반이 됩니다.
