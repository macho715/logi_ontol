> **⚠️ 중요**: 이 문서를 읽기 전에 **`../logiontology/`** 폴더를 먼저 확인하세요!
> - **전체 구현 코드**: `../logiontology/src/`
> - **설정 파일**: `../logiontology/configs/`
> - **온톨로지 정의**: `../logiontology/configs/ontology/hvdc_ontology.ttl`
> - **문서**: `../logiontology/README.md`, `../logiontology/CHANGELOG.md`

---

---
title: "HVDC Warehouse Logistics Ontology - Unified Framework"
type: "ontology-design"
domain: "warehouse-logistics"
sub-domains: ["warehouse-management", "inventory-tracking", "flow-control"]
version: "unified-2.0"
date: "2025-10-25"
tags: ["warehouse", "mosb", "stock", "flow-code", "transport-event", "hvdc", "logistics"]
standards: ["RDF", "OWL", "SHACL", "SPARQL", "JSON-LD", "Turtle", "XSD"]
status: "active"
source: "HVDC Warehouse Logistics Node Ontology v2.0"
verified_facts: "Warehouse operations, Flow Code system, Stock tracking"
---

# hvdc-warehouse-ops · 1_CORE-03

아래는 __HVDC 프로젝트 창고 물류 시스템(UAE 창고 네트워크)__를 __온톨로지 관점__으로 정의한 "작동 가능한 설계서"입니다.
핵심은 __Warehouse(창고)·Site(현장)·OffshoreBase(MOSB)__ 를 하나의 그래프(KG)로 엮고, __Flow Code(0~4)·재고 추적·위험물 관리·용량 제어__ 같은 제약을 **Constraints**로 운영하는 것입니다.

__1) Visual — Ontology Stack (요약표)__

| __Layer__                         | __표준/근거__                                    | __범위__                                       | __HVDC 창고 업무 매핑(예)__                                        |
| --------------------------------- | ------------------------------------------------ | ---------------------------------------------- | ------------------------------------------------------------- |
| __Upper__                         | __IOF/BFO Supply Chain Ontology__, __ISO 15926__ | 상위 개념(행위자/행위/자산/이벤트)·플랜트 라이프사이클 | 창고(Indoor/Outdoor)·이벤트(Transport/Stock)·상태(Flow Code) 프레임 |
| __Reference Data (Warehouse)__    | __UN/LOCODE__, __ISO 3166__                      | 창고·지역 코드 표준화                          | DSV Al Markaz, DSV Indoor, MOSB, Site 좌표             |
| __Inventory Management__          | __ISO 9001__, __ISO 14001__                      | 재고 관리, 품질 관리 시스템                   | StockSnapshot, TransportEvent, Case/Item 추적                |
| __Flow Control__                  | __HVDC Flow Code System__                        | 물류 흐름 코드(0~4) 표준화                   | Port→WH→MOSB→Site 경로 추적, WH Handling Count 관리                   |
| __Dangerous Cargo__               | __IMDG Code__, __IATA DGR__                      | 위험물 보관·운송 규정                         | DangerousCargoWarehouse, 특수 보관 조건, HSE 절차                           |
| __Data Validation__               | __SHACL__, __SPARQL__                            | 데이터 검증·질의 언어                         | Flow Code 검증, 재고 정확성, PKG Accuracy ≥99%            |
| __Integration__                   | __JSON-LD__, __RDF/XML__                         | 데이터 교환·통합 표준                         | Excel→RDF 매핑, API 연동, 실시간 동기화            |

Hint: MOSB는 **OffshoreBase**이면서 동시에 **특수 창고성 노드**로, ADNOC L&S 운영 Yard(20,000㎡)에서 해상화물 집하·적재를 담당합니다.

__2) Domain Ontology — 클래스/관계(창고 단위 재정의)__

__핵심 클래스 (Classes)__

- __Node__(Warehouse/Site/OffshoreBase)
- __Warehouse__(IndoorWarehouse/OutdoorWarehouse/DangerousCargoWarehouse)
- __Site__(AGI/DAS/MIR/SHU)
- __OffshoreBase__(MOSB)
- __TransportEvent__(노드 간 이동 및 상태 변경 이벤트)
- __StockSnapshot__(특정 시점 노드의 수량·중량·CBM 스냅샷)
- __Case__(패키지 단위 식별 개체)
- __Item__(개별 아이템 단위)
- __Invoice__(InvoiceLineItem/ChargeSummary)
- __Location__(UN/LOCODE, Warehouse Name, Storage Type)
- __FlowCode__(0~4 물류 흐름 코드)
- __KPI__(PKG_Accuracy/Flow_Code_Coverage/WH_Handling_Count/Data_Quality)

__대표 관계 (Object Properties)__

- TransportEvent → hasLocation → Node (이벤트 발생 위치)
- Case → transportedBy → TransportEvent (케이스 이동 이벤트)
- StockSnapshot → capturedAt → Node (재고 스냅샷 위치)
- TransportEvent → hasLogisticsFlowCode → FlowCode (물류 흐름 코드)
- Warehouse → handles → DangerousCargo (위험물 처리)
- Site → receivesFrom → Warehouse (현장 수령)
- OffshoreBase → consolidates → Warehouse (MOSB 집하)
- TransportEvent → hasWHHandling → Integer (창고 경유 횟수)
- Case → hasHVDCCode → String (HVDC 식별 코드)
- Invoice → refersTo → TransportEvent (송장 연계)

__데이터 속성 (Data Properties)__

- hasCase, hasRecordId, hasHVDCCode, hasDate, hasOperationMonth, hasStartDate, hasFinishDate, hasLocation, hasWarehouseName, hasStorageType, hasQuantity, hasPackageCount, hasWeight, hasCBM, hasAmount, hasRateUSD, hasTotalUSD, hasCategory, hasVendor, hasTransactionType, hasLogisticsFlowCode, hasWHHandling, hasStackStatus, hasDHLWarehouse.

__3) Use-case별 제약(Constraints) = 운영 가드레일__

__3.1 Warehouse Capacity Management__

- __Rule-1__: Warehouse.storageCapacity > CurrentUtilization. 초과 시 *overflow 창고* 확보 또는 *입고 스케줄 조정*.
- __Rule-2__: IndoorWarehouse → 온도·습도 제어 필수. 미준수 시 *자재 손상 리스크 알림*.
- __Rule-3__: DangerousCargoWarehouse → IMDG Code 준수. 위험물 분류별 분리 보관 필수.

__3.2 Stock Tracking & Accuracy__

- __Rule-4__: 모든 TransportEvent는 hasCase + hasDate + hasLocation + hasLogisticsFlowCode 필수. 미충족 시 *이벤트 생성 차단*.
- __Rule-5__: StockSnapshot → hasQuantity + hasWeight + hasCBM 필수. 음수 값 금지.
- __Rule-6__: PKG Accuracy ≥ 99% = 시스템 PKG / 실제수입PKG. 미달 시 *재고 실사* 필수.

__3.3 Flow Code Validation__

- __Rule-7__: hasLogisticsFlowCode ∈ {0,1,2,3,4}. 비표준 값(예: 6) 감지 시 *자동 정규화* 또는 *데이터 검증 실패*.
- __Rule-8__: hasWHHandling = 경유 창고 횟수(0~3). Flow Code와 일치 필수.
  - Flow Code 0: WH Handling = 0 (Pre Arrival)
  - Flow Code 1: WH Handling = 0 (Direct Port→Site)
  - Flow Code 2: WH Handling = 1 (Port→WH→Site)
  - Flow Code 3: WH Handling = 1~2 (Port→WH→MOSB→Site)
  - Flow Code 4: WH Handling = 2~3 (Port→WH→WH→MOSB→Site)

__3.4 Dangerous Cargo Handling__

- __Rule-9__: 위험물 → DangerousCargoWarehouse 필수. 일반 창고 보관 금지.
- __Rule-10__: IMDG Class별 분리 보관. 호환성 없는 위험물 동시 보관 금지.
- __Rule-11__: 위험물 TransportEvent → 특수 HSE 절차 + PTW 필수.

__4) 최소 예시(표현) — JSON-LD (요지)__

```json
{
  "@context": {
    "hvdc": "http://samsung.com/project-logistics#",
    "hasCase": "hvdc:hasCase",
    "hasDate": {"@id": "hvdc:hasDate", "@type": "xsd:dateTime"},
    "hasLocation": {"@id": "hvdc:hasLocation", "@type": "@id"},
    "hasLogisticsFlowCode": {"@id": "hvdc:hasLogisticsFlowCode", "@type": "xsd:integer"}
  },
  "@type": "hvdc:TransportEvent",
  "id": "EVT_208221_1",
  "hasCase": "HE-208221",
  "hasDate": "2025-05-13T08:00:00",
  "hasLocation": {
    "@type": "hvdc:IndoorWarehouse",
    "name": "DSV Indoor",
    "storageType": "Indoor"
  },
  "hasQuantity": 2,
  "hasWeight": 694.00,
  "hasCBM": 12.50,
  "hasLogisticsFlowCode": 3,
  "hasWHHandling": 1,
  "hasHVDCCode": "HE-208221"
}
```

__5) 선택지(3) — 구축 옵션 (pro/con/$·risk·time)__

1. __RDF-first (표준 우선, 완전한 온톨로지)__

- __Pro__: RDF/OWL/SHACL 완전 지원, 표준 호환성 최고, 복잡한 추론 가능.
- __Con__: 학습 곡선 가파름, Excel 사용자 접근성↓.
- __$__: 중간~높음. __Risk__: 기술 복잡성. __Time__: 12–16주 완전 구현.

2. __Hybrid (RDF+Excel 동시)__ ← *추천*

- __Pro__: RDF 온톨로지 + Excel 친화적 인터페이스, 점진적 마이그레이션 가능.
- __Con__: 두 시스템 동기화 복잡성.
- __$__: 중간. __Risk__: 데이터 일관성 관리. __Time__: 8–12주 POC→Rollout.

3. __Excel-first (현장 우선)__

- __Pro__: 기존 Excel 워크플로우 유지, 즉시 적용 가능.
- __Con__: 온톨로지 표준 준수 제한, 확장성 제약.
- __$__: 낮음. __Risk__: 기술 부채 누적. __Time__: 4–6주.

__6) Roadmap (P→Pi→B→O→S + KPI)__

- __P(Plan)__: 스코프 확정(창고: 7개, 이벤트: TransportEvent/StockSnapshot, 속성: 20개). __KPI__: 클래스 정의 완전성 ≥ 100%.
- __Pi(Pilot)__: __DSV Indoor + MOSB__ 2창고 대상 __Flow Code 검증__ 적용. __KPI__: PKG Accuracy ↑ 99%, Flow Code 오류 ↓ 90%.
- __B(Build)__: __SHACL 검증__ + __SPARQL 질의__ + __Excel→RDF 매핑__ 추가. __KPI__: 데이터 품질 오류 ↓ 95%, 질의 응답시간 ≤ 2초.
- __O(Operate)__: 실시간 재고 추적, 자동 알림, KPI 대시보드. __KPI__: 실시간 동기화 지연 ≤ 5분.
- __S(Scale)__: 7창고→글로벌 재사용, __RDF Web Vocabulary__로 공개 스키마 매핑. __KPI__: 타 프로젝트 적용 공수 ↓ 50%.

__7) Data·Sim·BI (운영 숫자 관점)__

- __Stock Clock__: StockSnapshot = (Node, DateTime, Quantity, Weight, CBM) → 노드별 __재고 시계__ 운영.
- __Flow Code Distribution__: FlowCode_t = Count(TransportEvent) by FlowCode(0~4) → 경로 효율성 분석.
- __WH Handling Efficiency__: 평균 경유 창고 횟수 추적, 최적화 기회 식별.
- __PKG Accuracy Rate__: 시스템 PKG / 실제 PKG × 100% → 99% 이상 유지.
- __Dangerous Cargo Compliance__: IMDG Code 준수율, HSE 절차 이행률 모니터링.

__8) Automation (RPA·LLM·Sheets·TG) — Slash Cmd 예시__

- __/warehouse-master --fast stock-audit__ → 7개 창고별 __재고 정확성__ 검증→PKG Accuracy 리포트.
- __/warehouse-master predict --AEDonly flow-efficiency__ → Flow Code 분포 분석 + 최적화 제안.
- __/switch_mode LATTICE RHYTHM__ → 창고 용량 알림 + Flow Code 검증 교차검증.
- __/visualize_data --type=warehouse <stock.csv>__ → 창고별 재고 현황 시각화.
- __/flow-code validate --strict__ → Flow Code(0~4) + WH Handling 일치성 검증.
- __/dangerous-cargo check --compliance__ → IMDG Code 준수 상태 일괄 체크.

__9) QA — Gap/Recheck 리스트__

- __RDF 스키마 정합성__: Turtle 문법, OWL 클래스 정의, SHACL 규칙 검증.
- __Flow Code 매핑__: 0~4 코드 정의, WH Handling 계산 로직, 비표준 값 처리.
- __Excel 매핑 규칙__: field_mappings 정확성, 데이터 타입 변환, NULL 값 처리.
- __SPARQL 질의__: 문법 검증, 성능 최적화, 결과 정확성.
- __JSON-LD 컨텍스트__: 네임스페이스 정의, 타입 매핑, 호환성 확인.

__10) Fail-safe "중단" 테이블 (ZERO 전략)__

| __트리거(중단)__                           | __ZERO 액션__                              | __재개 조건__                         |
| ------------------------------------------ | ------------------------------------------ | ------------------------------------- |
| Flow Code 비표준 값(>4) 감지               | 이벤트 생성 중단, 데이터 정규화 요청       | Flow Code 0~4 범위 내 정규화 완료     |
| PKG Accuracy < 99%                        | 재고 실사 강제 실행, 시스템 PKG 재계산     | PKG Accuracy ≥ 99% 달성               |
| 위험물 일반 창고 보관 감지                 | 즉시 격리, DangerousCargoWarehouse 이송   | IMDG Code 준수 창고로 이송 완료       |
| WH Handling ≠ Flow Code 일치              | 이벤트 검증 실패, 경로 재검토              | WH Handling과 Flow Code 일치 확인     |
| StockSnapshot 음수 값                     | 재고 조정 중단, 원인 분석 요청             | 양수 값으로 수정 완료                 |
| SHACL 검증 실패                           | 데이터 입력 중단, 스키마 위반 수정 요청    | SHACL 규칙 통과                       |
| Excel→RDF 매핑 오류                       | 변환 중단, 매핑 규칙 재검토                | 매핑 규칙 수정 완료                   |
| SPARQL 질의 타임아웃(>30초)               | 질의 중단, 인덱스 최적화 요청              | 질의 응답시간 ≤ 30초 달성             |

__11) 운영에 바로 쓰는 SHACL(요지)__

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix hvdc: <http://samsung.com/project-logistics#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# TransportEvent 검증 (핵심 4요소)
hvdc:TransportEventShape a sh:NodeShape ;
  sh:targetClass hvdc:TransportEvent ;
  sh:property [
    sh:path hvdc:hasCase ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
    sh:message "Case ID is required"
  ] ;
  sh:property [
    sh:path hvdc:hasDate ;
    sh:datatype xsd:dateTime ;
    sh:minCount 1 ;
    sh:message "Event date is required"
  ] ;
  sh:property [
    sh:path hvdc:hasLocation ;
    sh:class hvdc:Node ;
    sh:minCount 1 ;
    sh:message "Location must be a valid Node"
  ] ;
  sh:property [
    sh:path hvdc:hasLogisticsFlowCode ;
    sh:datatype xsd:integer ;
    sh:minInclusive 0 ;
    sh:maxInclusive 4 ;
    sh:minCount 1 ;
    sh:message "Flow Code must be 0-4"
  ] .

# Flow Code와 WH Handling 일치성 검증
hvdc:FlowCodeConsistencyShape a sh:NodeShape ;
  sh:targetClass hvdc:TransportEvent ;
  sh:sparql [
    sh:message "WH Handling count must match Flow Code" ;
    sh:select """
      SELECT $this
      WHERE {
        $this hvdc:hasLogisticsFlowCode ?flow .
        $this hvdc:hasWHHandling ?wh .
        FILTER (
          (?flow = 0 && ?wh != 0) ||
          (?flow = 1 && ?wh != 0) ||
          (?flow = 2 && ?wh != 1) ||
          (?flow = 3 && (?wh < 1 || ?wh > 2)) ||
          (?flow = 4 && (?wh < 2 || ?wh > 3))
        )
      }
    """
  ] .

# 위험물 창고 검증
hvdc:DangerousCargoShape a sh:NodeShape ;
  sh:targetClass hvdc:TransportEvent ;
  sh:sparql [
    sh:message "Dangerous cargo must be stored in DangerousCargoWarehouse" ;
    sh:select """
      SELECT $this
      WHERE {
        $this hvdc:hasCategory ?category .
        $this hvdc:hasLocation ?location .
        FILTER (CONTAINS(LCASE(?category), "dangerous") ||
                CONTAINS(LCASE(?category), "hazardous"))
        FILTER NOT EXISTS { ?location a hvdc:DangerousCargoWarehouse }
      }
    """
  ] .

# 재고 정확성 검증
hvdc:StockAccuracyShape a sh:NodeShape ;
  sh:targetClass hvdc:StockSnapshot ;
  sh:property [
    sh:path hvdc:hasQuantity ;
    sh:datatype xsd:integer ;
    sh:minInclusive 0 ;
    sh:message "Quantity cannot be negative"
  ] ;
  sh:property [
    sh:path hvdc:hasWeight ;
    sh:datatype xsd:decimal ;
    sh:minInclusive 0.0 ;
    sh:message "Weight cannot be negative"
  ] ;
  sh:property [
    sh:path hvdc:hasCBM ;
    sh:datatype xsd:decimal ;
    sh:minInclusive 0.0 ;
    sh:message "CBM cannot be negative"
  ] .
```

__12) GitHub·재사용__

- 리포지토리 __macho715/hvdc-warehouse-ontology__에 __/models (TTL/JSON-LD)__, __/rules (SHACL)__, __/queries (SPARQL)__, __/mappings (Excel→RDF)__ 디렉토리 구조 권장.
- Flow Code 시스템은 __/mappings/flow-code-rules.json__으로 관리.
- 창고 인스턴스는 __/data/warehouse-instances.ttl__로 버전 관리.

__13) Assumptions & Sources__

- __가정:__ Flow Code 0~4는 HVDC 프로젝트 내부 표준. PKG Accuracy 99%는 운영 품질 기준. 위험물은 IMDG Code 분류 기준 따름. Excel 원본은 ETL 전용 폴더에서만 사용.
- __표준/근거:__ RDF/OWL 2.0, SHACL 1.1, SPARQL 1.1, JSON-LD 1.1, XSD 1.1, IMDG Code, IATA DGR, ISO 9001/14001, HVDC Warehouse Logistics Node Ontology v2.0.

__14) 다음 액션(짧게)__

- __/warehouse-master --fast stock-audit__ 로 7개 창고 대상 __재고 정확성__ 일괄 점검,
- __/flow-code validate --strict__ 로 __Flow Code + WH Handling__ 일치성 검증,
- __/visualize_data --type=warehouse <stock.csv>__ 로 __창고별 재고 현황__ 시각화.

원하시면, 위 스택으로 __Flow Code 검증__과 __위험물 관리__부터 SHACL/룰팩을 묶어 드리겠습니다.

---

# Part 2: Technical Implementation

## 개요

HVDC 창고 물류 시스템의 **기술적 구현**을 RDF/OWL/SHACL/SPARQL 표준으로 정의합니다.

__🔶 1. Turtle Schema (완전한 온톨로지 정의)__

```turtle
@prefix hvdc: <http://samsung.com/project-logistics#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .

# 클래스 정의
hvdc:Node a owl:Class ; rdfs:label "Logistics Node"@en .
hvdc:Warehouse a owl:Class ; rdfs:subClassOf hvdc:Node ; rdfs:label "Warehouse"@en .
hvdc:IndoorWarehouse a owl:Class ; rdfs:subClassOf hvdc:Warehouse ; rdfs:label "Indoor Warehouse"@en .
hvdc:OutdoorWarehouse a owl:Class ; rdfs:subClassOf hvdc:Warehouse ; rdfs:label "Outdoor Warehouse"@en .
hvdc:DangerousCargoWarehouse a owl:Class ; rdfs:subClassOf hvdc:Warehouse ; rdfs:label "Dangerous Cargo Warehouse"@en .

hvdc:Site a owl:Class ; rdfs:subClassOf hvdc:Node ; rdfs:label "Project Site"@en .
hvdc:OffshoreBase a owl:Class ; rdfs:subClassOf hvdc:Warehouse ; rdfs:label "Offshore Base"@en .

hvdc:TransportEvent a owl:Class ; rdfs:label "Transport Event"@en .
hvdc:StockSnapshot a owl:Class ; rdfs:label "Stock Snapshot"@en .
hvdc:Case a owl:Class ; rdfs:label "Case"@en .
hvdc:Item a owl:Class ; rdfs:label "Item"@en .
hvdc:Invoice a owl:Class ; rdfs:label "Invoice"@en .
hvdc:InvoiceLineItem a owl:Class ; rdfs:label "Invoice Line Item"@en .

# 데이터 속성 정의
hvdc:hasCase a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Case ID"@en .
hvdc:hasRecordId a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Record ID"@en .
hvdc:hasHVDCCode a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has HVDC Code"@en .
hvdc:hasDate a owl:DatatypeProperty ; rdfs:range xsd:dateTime ; rdfs:label "has Date"@en .
hvdc:hasOperationMonth a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Operation Month"@en .
hvdc:hasStartDate a owl:DatatypeProperty ; rdfs:range xsd:dateTime ; rdfs:label "has Start Date"@en .
hvdc:hasFinishDate a owl:DatatypeProperty ; rdfs:range xsd:dateTime ; rdfs:label "has Finish Date"@en .

hvdc:hasLocation a owl:ObjectProperty ; rdfs:range hvdc:Node ; rdfs:label "has Location"@en .
hvdc:hasWarehouseName a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Warehouse Name"@en .
hvdc:hasStorageType a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Storage Type"@en .

hvdc:hasQuantity a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "has Quantity"@en .
hvdc:hasPackageCount a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "has Package Count"@en .
hvdc:hasWeight a owl:DatatypeProperty ; rdfs:range xsd:decimal ; rdfs:label "has Weight"@en .
hvdc:hasCBM a owl:DatatypeProperty ; rdfs:range xsd:decimal ; rdfs:label "has CBM"@en .

hvdc:hasAmount a owl:DatatypeProperty ; rdfs:range xsd:decimal ; rdfs:label "has Amount"@en .
hvdc:hasRateUSD a owl:DatatypeProperty ; rdfs:range xsd:decimal ; rdfs:label "has Rate USD"@en .
hvdc:hasTotalUSD a owl:DatatypeProperty ; rdfs:range xsd:decimal ; rdfs:label "has Total USD"@en .

hvdc:hasCategory a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Category"@en .
hvdc:hasVendor a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Vendor"@en .
hvdc:hasTransactionType a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Transaction Type"@en .
hvdc:hasLogisticsFlowCode a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "has Logistics Flow Code"@en .
hvdc:hasWHHandling a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "has Warehouse Handling Count"@en .
hvdc:hasStackStatus a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "has Stack Status"@en .
hvdc:hasDHLWarehouse a owl:DatatypeProperty ; rdfs:range xsd:boolean ; rdfs:label "has DHL Warehouse"@en .

# 객체 속성 정의
hvdc:transportedBy a owl:ObjectProperty ; rdfs:domain hvdc:Case ; rdfs:range hvdc:TransportEvent ; rdfs:label "transported by"@en .
hvdc:capturedAt a owl:ObjectProperty ; rdfs:domain hvdc:StockSnapshot ; rdfs:range hvdc:Node ; rdfs:label "captured at"@en .
hvdc:refersTo a owl:ObjectProperty ; rdfs:domain hvdc:Invoice ; rdfs:range hvdc:TransportEvent ; rdfs:label "refers to"@en .
hvdc:handles a owl:ObjectProperty ; rdfs:domain hvdc:Warehouse ; rdfs:range hvdc:Item ; rdfs:label "handles"@en .
hvdc:receivesFrom a owl:ObjectProperty ; rdfs:domain hvdc:Site ; rdfs:range hvdc:Warehouse ; rdfs:label "receives from"@en .
hvdc:consolidates a owl:ObjectProperty ; rdfs:domain hvdc:OffshoreBase ; rdfs:range hvdc:Warehouse ; rdfs:label "consolidates"@en .
```

__🔶 2. 표준 노드 인스턴스 (v2 목록)__

```turtle
# 창고 인스턴스
hvdc:DSV_Al_Markaz a hvdc:IndoorWarehouse ; rdfs:label "DSV Al Markaz" ; hvdc:hasStorageType "Indoor" .
hvdc:DSV_Indoor a hvdc:IndoorWarehouse ; rdfs:label "DSV Indoor" ; hvdc:hasStorageType "Indoor" .
hvdc:DSV_Outdoor a hvdc:OutdoorWarehouse ; rdfs:label "DSV Outdoor" ; hvdc:hasStorageType "Outdoor" .
hvdc:DSV_MZP a hvdc:OutdoorWarehouse ; rdfs:label "DSV MZP" ; hvdc:hasStorageType "Outdoor" .
hvdc:AAA_Storage a hvdc:DangerousCargoWarehouse ; rdfs:label "AAA Storage" ; hvdc:hasStorageType "Dangerous" .
hvdc:Hauler_Indoor a hvdc:IndoorWarehouse ; rdfs:label "Hauler Indoor" ; hvdc:hasStorageType "Indoor" .
hvdc:DHL_Warehouse a hvdc:IndoorWarehouse ; rdfs:label "DHL Warehouse" ; hvdc:hasStorageType "Transit" .

# MOSB (OffshoreBase)
hvdc:MOSB_Base a hvdc:OffshoreBase ; rdfs:label "MOSB" ; hvdc:hasStorageType "Offshore" .

# 현장 인스턴스
hvdc:AGI_Site a hvdc:Site ; rdfs:label "AGI" .
hvdc:DAS_Site a hvdc:Site ; rdfs:label "DAS" .
hvdc:MIR_Site a hvdc:Site ; rdfs:label "MIR" .
hvdc:SHU_Site a hvdc:Site ; rdfs:label "SHU" .
```

__🔶 3. 예시 인스턴스 & 이벤트__

```turtle
# 케이스 인스턴스
hvdc:CASE_208221 a hvdc:Case ; hvdc:hasHVDCCode "HE-208221" .

# TransportEvent 시퀀스
hvdc:EVT_208221_1 a hvdc:TransportEvent ;
  hvdc:hasCase "HE-208221" ;
  hvdc:hasDate "2025-05-13T08:00:00"^^xsd:dateTime ;
  hvdc:hasLocation hvdc:DSV_Indoor ;
  hvdc:hasQuantity 2 ;
  hvdc:hasWeight 694.00 ;
  hvdc:hasCBM 12.50 ;
  hvdc:hasLogisticsFlowCode 3 ;
  hvdc:hasWHHandling 1 .

hvdc:EVT_208221_2 a hvdc:TransportEvent ;
  hvdc:hasCase "HE-208221" ;
  hvdc:hasDate "2025-05-15T10:00:00"^^xsd:dateTime ;
  hvdc:hasLocation hvdc:MOSB_Base ;
  hvdc:hasLogisticsFlowCode 3 ;
  hvdc:hasWHHandling 2 .

hvdc:EVT_208221_3 a hvdc:TransportEvent ;
  hvdc:hasCase "HE-208221" ;
  hvdc:hasDate "2025-05-18T16:00:00"^^xsd:dateTime ;
  hvdc:hasLocation hvdc:DAS_Site ;
  hvdc:hasLogisticsFlowCode 3 ;
  hvdc:hasWHHandling 2 .

# StockSnapshot
hvdc:STOCK_DSV_20250513 a hvdc:StockSnapshot ;
  hvdc:capturedAt hvdc:DSV_Indoor ;
  hvdc:hasDate "2025-05-13T23:59:59"^^xsd:dateTime ;
  hvdc:hasQuantity 150 ;
  hvdc:hasWeight 25000.50 ;
  hvdc:hasCBM 450.75 .
```

__🔶 4. SPARQL 질의(운영 예시)__

**(A) 월별·창고별 수량/금액 요약**
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?month ?warehouse (SUM(?amount) AS ?totalAmount) (SUM(?qty) AS ?totalQty)
WHERE {
  ?e a hvdc:TransportEvent ; hvdc:hasLocation ?warehouse ; hvdc:hasDate ?date .
  OPTIONAL { ?e hvdc:hasAmount ?amount }
  OPTIONAL { ?e hvdc:hasQuantity ?qty }
  BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
}
GROUP BY ?month ?warehouse
ORDER BY ?month ?warehouse
```

**(B) Flow Code 분포(wh handling 기반)**
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?flow (COUNT(?e) AS ?cnt)
WHERE {
  ?e a hvdc:TransportEvent ; hvdc:hasLogisticsFlowCode ?flow .
}
GROUP BY ?flow ORDER BY ?flow
```

**(C) 위험물 창고 사용 현황**
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?warehouse ?category (COUNT(?e) AS ?eventCount)
WHERE {
  ?e a hvdc:TransportEvent ;
     hvdc:hasLocation ?warehouse ;
     hvdc:hasCategory ?category .
  ?warehouse a hvdc:DangerousCargoWarehouse .
  FILTER (CONTAINS(LCASE(?category), "dangerous") ||
          CONTAINS(LCASE(?category), "hazardous"))
}
GROUP BY ?warehouse ?category
ORDER BY ?warehouse ?category
```

**(D) PKG Accuracy 계산**
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?warehouse
       (COUNT(?e) AS ?systemPKG)
       (SUM(?qty) AS ?totalQuantity)
       ((COUNT(?e) * 1.0 / SUM(?qty)) * 100 AS ?pkgAccuracy)
WHERE {
  ?e a hvdc:TransportEvent ;
     hvdc:hasLocation ?warehouse ;
     hvdc:hasQuantity ?qty .
}
GROUP BY ?warehouse
HAVING (?pkgAccuracy >= 99.0)
```

__🔶 5. JSON-LD 컨텍스트(완전한 정의)__

```json
{
  "@context": {
    "hvdc": "http://samsung.com/project-logistics#",
    "hasCase": "hvdc:hasCase",
    "hasRecordId": "hvdc:hasRecordId",
    "hasHVDCCode": "hvdc:hasHVDCCode",
    "hasDate": {"@id": "hvdc:hasDate", "@type": "xsd:dateTime"},
    "hasOperationMonth": "hvdc:hasOperationMonth",
    "hasStartDate": {"@id": "hvdc:hasStartDate", "@type": "xsd:dateTime"},
    "hasFinishDate": {"@id": "hvdc:hasFinishDate", "@type": "xsd:dateTime"},
    "hasLocation": {"@id": "hvdc:hasLocation", "@type": "@id"},
    "hasWarehouseName": "hvdc:hasWarehouseName",
    "hasStorageType": "hvdc:hasStorageType",
    "hasQuantity": {"@id": "hvdc:hasQuantity", "@type": "xsd:integer"},
    "hasPackageCount": {"@id": "hvdc:hasPackageCount", "@type": "xsd:integer"},
    "hasWeight": {"@id": "hvdc:hasWeight", "@type": "xsd:decimal"},
    "hasCBM": {"@id": "hvdc:hasCBM", "@type": "xsd:decimal"},
    "hasAmount": {"@id": "hvdc:hasAmount", "@type": "xsd:decimal"},
    "hasRateUSD": {"@id": "hvdc:hasRateUSD", "@type": "xsd:decimal"},
    "hasTotalUSD": {"@id": "hvdc:hasTotalUSD", "@type": "xsd:decimal"},
    "hasCategory": "hvdc:hasCategory",
    "hasVendor": "hvdc:hasVendor",
    "hasTransactionType": "hvdc:hasTransactionType",
    "hasLogisticsFlowCode": {"@id": "hvdc:hasLogisticsFlowCode", "@type": "xsd:integer"},
    "hasWHHandling": {"@id": "hvdc:hasWHHandling", "@type": "xsd:integer"},
    "hasStackStatus": "hvdc:hasStackStatus",
    "hasDHLWarehouse": {"@id": "hvdc:hasDHLWarehouse", "@type": "xsd:boolean"},
    "transportedBy": {"@id": "hvdc:transportedBy", "@type": "@id"},
    "capturedAt": {"@id": "hvdc:capturedAt", "@type": "@id"},
    "refersTo": {"@id": "hvdc:refersTo", "@type": "@id"},
    "handles": {"@id": "hvdc:handles", "@type": "@id"},
    "receivesFrom": {"@id": "hvdc:receivesFrom", "@type": "@id"},
    "consolidates": {"@id": "hvdc:consolidates", "@type": "@id"}
  }
}
```

---

# Part 3: Operational Details

## 개요

HVDC 창고 물류 시스템의 **운영 세부사항**을 정의합니다.

__🔶 1. 표준 노드 인스턴스 목록 (v2 완전 목록)__

### 1.1 창고(Warehouse) - 7개
- **DSV Al Markaz** (Indoor) - 주요 실내 창고
- **DSV Indoor** (Indoor) - 실내 보관 전용
- **DSV Outdoor** (Outdoor) - 야외 보관
- **DSV MZP** (Outdoor) - 야외 보관
- **AAA Storage** (Dangerous 가능/보관 전용) - 위험물 전용
- **Hauler Indoor** (Indoor) - 실내 보관
- **DHL Warehouse** (Indoor/Transit) - 통과 창고

### 1.2 현장(Site) - 4개
- **AGI** (Al Ghallan Island)
- **DAS** (DAS Island)
- **MIR** (Mirfa Site)
- **SHU** (Shuweihat Site)

### 1.3 해상기지(OffshoreBase) - 1개
- **MOSB** (Mussafah Offshore Supply Base) - 중앙 집하 허브

__🔶 2. 물류 흐름 코드(Logistics Flow Code) 상세__

**정의**(0~4 고정):
- **0**: Pre Arrival — Planning → Port (계획 단계)
- **1**: Direct Port→Site — Port → Site (직접 운송)
- **2**: Port→WH→Site — Port → Warehouse → Site (1회 창고 경유)
- **3**: Port→WH→MOSB→Site — Port → Warehouse → MOSB → Site (2회 창고 경유)
- **4**: Port→WH→WH→MOSB→Site — Port → Warehouse → Warehouse → MOSB → Site (3회 창고 경유)

**규칙**
- 비표준 값(예: 6)은 정규화하여 3으로 매핑 가능(데이터 복구 단계에서 적용)
- `hvdc:hasWHHandling`(정수)는 경유 창고 횟수(0~3)를 표현
- Flow Code와 WH Handling Count는 일치해야 함

__🔶 3. 매핑 규칙 상세 (Excel → RDF)__

### 3.1 필드 매핑
```json
{
  "field_mappings": {
    "Case_No": "hvdc:hasCase",
    "Date": "hvdc:hasDate",
    "Location": "hvdc:hasLocation",
    "Qty": "hvdc:hasQuantity",
    "Amount": "hvdc:hasAmount",
    "Stack_Status": "hvdc:hasStackStatus",
    "DHL Warehouse": "hvdc:hasDHLWarehouse",
    "Flow_Code": "hvdc:hasLogisticsFlowCode",
    "WH_Handling": "hvdc:hasWHHandling"
  }
}
```

### 3.2 정규화 규칙
- `NULL PKG` → `1` (기본 패키지 수)
- `Flow Code 6` → `3` (비표준 값 정규화)
- 벤더/날짜 표준화 (ISO 8601 형식)
- 전각 공백 → 반각 공백 변환

### 3.3 분류 코드
```json
{
  "warehouse_codes": {
    "DSV Al Markaz": "hvdc:DSV_Al_Markaz",
    "DSV Indoor": "hvdc:DSV_Indoor",
    "DSV Outdoor": "hvdc:DSV_Outdoor",
    "DSV MZP": "hvdc:DSV_MZP",
    "AAA Storage": "hvdc:AAA_Storage",
    "Hauler Indoor": "hvdc:Hauler_Indoor",
    "DHL Warehouse": "hvdc:DHL_Warehouse",
    "MOSB": "hvdc:MOSB_Base"
  },
  "site_codes": {
    "AGI": "hvdc:AGI_Site",
    "DAS": "hvdc:DAS_Site",
    "MIR": "hvdc:MIR_Site",
    "SHU": "hvdc:SHU_Site"
  }
}
```

__🔶 4. 운영 가이드__

### 4.1 Zero-Edit 원본 보존
- Excel 원본은 ETL 전용 폴더에서만 사용
- 수동 편집 금지
- 버전 관리 필수

### 4.2 매핑 버전 잠금
- `hvdc_integrated_mapping_rules_v*.json` 불일치 시 빌드 중단
- 매핑 규칙 변경 시 전체 시스템 재검증

### 4.3 이슈 핸들러
- MOSB·날짜 포맷 변동 감지 시 진단 스크립트 재실행
- Flow Code 비표준 값 감지 시 자동 정규화 또는 오류 보고
- PKG Accuracy < 99% 시 재고 실사 자동 트리거

__🔶 5. 데이터 품질 기준__

### 5.1 KPI & 거버넌스
- **PKG Accuracy ≥ 99%** = 시스템 PKG / 실제수입PKG
- **Flow Code Coverage** = {0..4} 전체 출현
- **WH Handling 합리성** = 경유 창고 횟수(0~3) 분포 정상성 모니터
- **데이터 품질** = 헤더 탐지/전각 공백/날짜 파싱 오류 0건 기준으로 CI 실패 설정

### 5.2 검증 기준
- SHACL 규칙 100% 통과
- SPARQL 질의 응답시간 ≤ 30초
- JSON-LD 변환 정확성 100%
- Excel→RDF 매핑 정확성 ≥ 99.5%

### 5.3 모니터링 지표
- 실시간 재고 동기화 지연 ≤ 5분
- Flow Code 검증 성공률 ≥ 99.9%
- 위험물 창고 규정 준수율 100%
- 시스템 가용성 ≥ 99.5%

---

## 🔶 6. 버전 관리

- **v2.0 (2025-10-25)**: 창고·현장·MOSB 노드 정규화, Flow Code(0~4) 고정, SHACL/질의 포함.
- **v2.1 (2025-10-25)**: 01-core 포맷 적용, 기술 구현 상세화, 운영 가이드 추가.

---

🔧 **추천 명령어:**
`/warehouse-master stock-audit` [7개 창고 재고 정확성 일괄 점검 - PKG Accuracy 검증]
`/flow-code validate --strict` [Flow Code + WH Handling 일치성 검증 - 데이터 품질 보장]
`/visualize_data --type=warehouse stock` [창고별 재고 현황 시각화 - 실시간 모니터링]
`/dangerous-cargo check --compliance` [위험물 IMDG Code 준수 상태 검증 - 안전 관리]
