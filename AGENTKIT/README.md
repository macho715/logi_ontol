# HVDC AgentKit Data Package

**프로젝트**: HVDC Logistics & Ontology System
**버전**: v1.0
**작성일**: 2025-11-01
**상태**: 프로덕션

---

## 📋 개요

AgentKit은 HVDC 프로젝트의 물류 데이터를 AI Agent가 쉽게 이해하고 처리할 수 있도록 준비된 **표준 데이터 패키지**입니다. AGENTKIT.MD 사양에 따라 실제 프로젝트 데이터를 기반으로 생성되었습니다.

---

## 📦 포함된 파일 (6개)

### 1. hvdc_schema_events_8997_sample.csv
**용도**: 이벤트 기반 화물 케이스 샘플 데이터

**컬럼**:
- `Case_No`: 케이스 고유 번호 (예: HVDC-00001)
- `Vendor`: 벤더 (SCT, DSV, ALS)
- `Event_Type`: 이벤트 유형 (Inbound/Outbound)
- `Flow_Code`: Flow Code 0~5
- `Warehouse_Code`: 창고 코드 (DSV_Indoor, MOSB 등)
- `Final_Location`: 최종 목적지 (MIR, SHU, DAS, AGI)
- `Status_Location_Date`: 상태 위치 날짜
- `Final_Location_Date`: 최종 도착 날짜
- `Weight_ton`: 중량 (톤)
- `Qty`: 수량 (Pkg)
- `Container_No`: 컨테이너 번호

**데이터 소스**: HVDC STATUS(20250815) (1).xlsx (755 cases)

---

### 2. hvdc_ontology_core_no-hasLocation.ttl
**용도**: TTL 온톨로지 스키마 샘플

**네임스페이스**: `http://samsung.com/project-logistics#`

**주요 클래스 & 속성**:
- `hvdc:Case` - 화물 케이스
- `hvdc:hasHvdcCode` - HVDC 코드
- `hvdc:hasVendor` - 벤더
- `hvdc:hasFinalLocation` - 최종 위치
- `hvdc:hasFinalLocationDate` - 최종 도착일
- `hvdc:hasFlowCode` - Flow Code 0~5
- `hvdc:hasFlowDescription` - Flow 패턴 설명
- `hvdc:hasFlowCodeOriginal` - 원본 Flow Code (오버라이드 전)
- `hvdc:hasFlowOverrideReason` - 오버라이드 사유

**특징**: `hasLocation` 제거, `hasFinalLocation`만 사용 (단순화)

---

### 3. flow_code_v3.5_rules.md
**용도**: Flow Code v3.5 규칙 및 통계 요약

**내용**:
- Flow Code 0~5 정의 및 경로
- 실제 분포 (755 cases):
  - Flow 0: 71 (9.4%)
  - Flow 1: 255 (33.8%)
  - Flow 2: 152 (20.1%)
  - Flow 3: 131 (17.4%)
  - Flow 4: 65 (8.6%)
  - Flow 5: 81 (10.7%)
- AGI/DAS 도메인 룰 (31건 자동 승급)
- 검증 규칙 및 계산 로직

---

### 4. validation_report_sample.txt
**용도**: 실제 검증 결과 보고서

**주요 내용**:
- Flow Code v3.5 검증: PASS ✅
- AGI/DAS 준수율: 100% ✅
- 이벤트 커버리지: 55.72% Inbound, 26.47% Outbound
- Flow별 패턴 분석 (8,995 cases)
- 데이터 품질 이슈 (12건 Final_Location 누락 등)

**데이터 소스**: `output/validation/validation_summary.json`

---

### 5. stock_audit_sample.csv
**용도**: Site별 입출고 통계

**컬럼**:
- `Final_Location`: 최종 위치 (DAS, AGI, MIR, SHU)
- `Event_Type`: 이벤트 유형 (Inbound/Outbound)
- `Count`: 건수
- `First_Date`: 첫 날짜
- `Last_Date`: 마지막 날짜

**통계**:
- DAS: 289 Inbound, 98 Outbound
- AGI: 142 Inbound, 67 Outbound
- MIR: 98 Inbound, 52 Outbound
- SHU: 44 Inbound, 28 Outbound

---

### 6. slash_commands_logi-master.md
**용도**: HVDC Logistics 명령어 참조 가이드

**카테고리**:
- LogiMaster 명령어 (`/logi-master invoice-audit` 등)
- Mode 전환 (`/switch_mode PRIME/ORACLE/LATTICE` 등)
- 데이터 시각화 (`/visualize_data --type=heatmap` 등)
- 검증 명령어 (`/validate-data compliance` 등)
- 고급 명령어 (RPA, 예측 분석 등)

---

## 🚀 사용 방법

### 1. AI Agent에게 데이터 제공
```markdown
**AgentKit 데이터 로드**:
- 위치: `data/agentkit/`
- 파일: 6개 (CSV 2개, TTL 1개, MD 2개, TXT 1개)
- 용도: HVDC 물류 데이터 분석 및 검증
```

### 2. Flow Code 검증
```bash
# AgentKit 데이터 기반 검증
/validate-data flow-code --source=data/agentkit/
```

### 3. 시각화
```bash
# Flow 분포 차트
/visualize_data --type=flowchart --data=agentkit/flow_code_v3.5_rules.md
```

### 4. 커스텀 쿼리
```python
import pandas as pd

# CSV 로드
events = pd.read_csv('data/agentkit/hvdc_schema_events_8997_sample.csv')
audit = pd.read_csv('data/agentkit/stock_audit_sample.csv')

# Flow Code 분포 분석
flow_dist = events.groupby('Flow_Code').size()
print(flow_dist)
```

---

## 📊 데이터 소스

### 원본 데이터
- **Excel**: `HVDC STATUS(20250815) (1).xlsx` (755 cases)
- **TTL**: `output/hvdc_status_v35.ttl` (9,904 triples, 818 events)
- **Validation**: `output/validation/validation_summary.json`

### 생성 스크립트
- **Excel → TTL**: `logiontology/src/ingest/excel_to_ttl_with_events.py`
- **Flow Code 계산**: `logiontology/src/ingest/flow_code_calculator.py`
- **검증**: `tests/test_flow_code_v35_validation.py`

---

## 🔗 관련 문서

- **AGENTKIT.MD**: 사양 정의 (루트 폴더)
- **Flow Code v3.5 알고리즘**: `docs/flow_code_v35/FLOW_CODE_V35_ALGORITHM.md`
- **구현 완료 보고서**: `docs/flow_code_v35/FLOW_CODE_V35_IMPLEMENTATION_COMPLETE.md`
- **MCP 서버**: `hvdc_mcp_server_v35/README.md`
- **온톨로지 스키마**: `logiontology/configs/ontology/hvdc_event_schema.ttl`

---

## ⚙️ 기술 스택

- **데이터 형식**: CSV, TTL (Turtle), Markdown, Plain Text
- **온톨로지**: OWL/RDF (네임스페이스: `hvdc:`)
- **검증**: SPARQL, SHACL
- **통합**: MACHO-GPT v3.4-mini, MCP Server v3.5

---

## 📝 버전 이력

### v1.0 (2025-11-01)
- ✅ 초기 릴리스
- ✅ 6개 파일 생성 (실제 데이터 기반)
- ✅ AGENTKIT.MD 사양 완전 준수
- ✅ Flow Code v3.5 통계 반영
- ✅ AGI/DAS 도메인 룰 검증 결과 포함

---

## 📧 문의

**프로젝트**: HVDC Logistics & Ontology System
**팀**: HVDC Project Team
**저장소**: https://github.com/macho715/logi_ontol.git

---

**작성일**: 2025-11-01
**상태**: 프로덕션
**다음 단계**: AI Agent 통합 테스트

