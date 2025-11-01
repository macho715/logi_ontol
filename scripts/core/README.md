# Core CLI Scripts for HVDC Logistics Ontology

**독립 실행 가능한 핵심 기능 스크립트 모음**

이 디렉토리에는 HVDC 프로젝트의 핵심 기능을 독립적으로 실행할 수 있는 CLI 스크립트가 포함되어 있습니다. 모든 스크립트는 프로젝트 루트에서 실행하도록 설계되었습니다.

## 📁 스크립트 목록

### 1. `flow_code_calc.py` - Flow Code v3.5 계산기

**기능**: Excel 파일에서 Flow Code 0~5를 자동 계산하고 CSV/JSON으로 출력

**주요 기능**:
- ✅ Flow Code 0~5 자동 계산
- ✅ AGI/DAS 도메인 룰 적용
- ✅ Pre Arrival 판별
- ✅ Final_Location 자동 추출
- ✅ Override 추적 (FLOW_CODE_ORIG, FLOW_OVERRIDE_REASON)
- ✅ 컬럼명 자동 정규화

**사용법**:
```bash
# CSV 출력 (기본)
python scripts/core/flow_code_calc.py \
    --input data/HVDC_STATUS.xlsx \
    --output output/flow_codes.csv

# JSON 출력
python scripts/core/flow_code_calc.py \
    --input data/HVDC_STATUS.xlsx \
    --output output/flow_codes.json \
    --format json

# 통계만 출력 (파일 저장 안 함)
python scripts/core/flow_code_calc.py \
    --input data/HVDC_STATUS.xlsx \
    --stats-only
```

**옵션**:
- `--input, -i`: 입력 Excel 파일 경로 (필수)
- `--output, -o`: 출력 파일 경로 (CSV or JSON)
- `--format, -f`: 출력 형식 (`csv` or `json`, 기본값: csv)
- `--warehouses`: 창고 컬럼 이름 (쉼표로 구분)
- `--sites`: 사이트 컬럼 이름 (쉼표로 구분)
- `--stats-only`: 통계만 출력, 파일 저장 안 함
- `--verbose, -v`: 상세 출력

---

### 2. `excel_to_ttl.py` - Excel to TTL 변환기

**기능**: Excel 파일을 이벤트 기반 RDF/TTL 형식으로 변환

**주요 기능**:
- ✅ Excel → RDF/TTL 변환 (이벤트 기반)
- ✅ Flow Code v3.5 자동 통합
- ✅ StockEvent 주입 (Inbound/Outbound)
- ✅ HVDC 온톨로지 스키마 준수
- ✅ 창고/사이트 자동 매핑

**사용법**:
```bash
# 기본 변환 (Flow Code v3.5 자동 계산)
python scripts/core/excel_to_ttl.py \
    --input data/HVDC_STATUS.xlsx \
    --output output/hvdc_status_v35.ttl

# 스키마 포함 변환
python scripts/core/excel_to_ttl.py \
    --input data/HVDC_STATUS.xlsx \
    --output output/hvdc_status_v35.ttl \
    --schema logiontology/configs/ontology/hvdc_event_schema.ttl

# 커스텀 컬럼 지정
python scripts/core/excel_to_ttl.py \
    --input data.xlsx \
    --output result.ttl \
    --warehouses "WH1,WH2,MOSB" \
    --sites "SHU,MIR"
```

**옵션**:
- `--input, -i`: 입력 Excel 파일 경로 (필수)
- `--output, -o`: 출력 TTL 파일 경로 (필수)
- `--schema, -s`: 온톨로지 스키마 TTL 파일 경로 (선택)
- `--warehouses`: 창고 컬럼 이름 (쉼표로 구분)
- `--sites`: 사이트 컬럼 이름 (쉼표로 구분)
- `--flow-version`: Flow Code 버전 (`3.4` or `3.5`, 기본값: 3.5)
- `--verbose, -v`: 상세 출력

---

### 3. `validate_schema.py` - TTL 스키마 검증기

**기능**: TTL 파일을 SHACL 스키마로 검증

**주요 기능**:
- ✅ SHACL 기반 데이터 검증
- ✅ Flow Code 범위 검증 (0~5)
- ✅ 필수 속성 검증
- ✅ Case/Event 통계
- ✅ JSON 결과 출력

**사용법**:
```bash
# 기본 검증 (SHACL 없이)
python scripts/core/validate_schema.py \
    --ttl output/hvdc_status_v35.ttl

# SHACL 스키마 포함 검증
python scripts/core/validate_schema.py \
    --ttl output/hvdc_status_v35.ttl \
    --schema logiontology/configs/ontology/hvdc_event_schema.ttl

# JSON 출력
python scripts/core/validate_schema.py \
    --ttl output/hvdc_status_v35.ttl \
    --output validation_result.json
```

**옵션**:
- `--ttl, -t`: 검증할 TTL 파일 경로 (필수)
- `--schema, -s`: SHACL 스키마 파일 경로 (선택)
- `--output, -o`: 결과를 저장할 JSON 파일 경로 (선택)
- `--verbose, -v`: 상세 출력

**Exit Code**:
- `0`: 검증 통과 (conforms=true)
- `1`: 검증 실패 (conforms=false or error)

---

### 4. `ttl_to_json.py` - TTL to JSON 변환기

**기능**: TTL 파일을 GPT용 평탄화 JSON으로 변환

**주요 기능**:
- ✅ TTL → JSON 평탄화 (GPT 친화적)
- ✅ 월별 집계 (월별 창고 입고)
- ✅ Vendor별 분석
- ✅ Flow Code 분포
- ✅ 사전 집계 뷰 생성

**사용법**:
```bash
# 기본 변환 (TTL → JSON)
python scripts/core/ttl_to_json.py \
    --input output/hvdc_status_v35.ttl \
    --output output/hvdc_flat.json

# 사전 집계 뷰 포함
python scripts/core/ttl_to_json.py \
    --input output/hvdc_status_v35.ttl \
    --output output/hvdc_flat.json \
    --views output/views/

# 뷰 생성만 (flat JSON 건너뛰기)
python scripts/core/ttl_to_json.py \
    --input output/hvdc_status_v35.ttl \
    --views-only output/views/
```

**옵션**:
- `--input, -i`: 입력 TTL 파일 경로 (필수)
- `--output, -o`: 출력 JSON 파일 경로 (flat 형식)
- `--views`: 사전 집계 뷰 출력 디렉토리 (선택)
- `--views-only`: 뷰만 생성 (flat JSON 건너뛰기)
- `--verbose, -v`: 상세 출력

**생성되는 뷰**:
- `monthly_warehouse_inbound.json` - 월별 창고 입고 집계
- `vendor_summary.json` - Vendor별 월별 입고
- `cases_by_flow.json` - Flow Code별 케이스 분포

---

### 5. `neo4j_loader.py` - Neo4j 로더

**기능**: TTL 파일을 Neo4j 그래프 데이터베이스에 로드

**주요 기능**:
- ✅ TTL → Neo4j 변환
- ✅ Case 노드 생성
- ✅ 환경변수 지원
- ✅ 커스텀 데이터베이스 지원

**사용법**:
```bash
# 기본 로드 (로컬 Neo4j)
python scripts/core/neo4j_loader.py \
    --ttl output/hvdc_status_v35.ttl \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password password

# 환경변수 사용
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
python scripts/core/neo4j_loader.py \
    --ttl output/hvdc_status_v35.ttl

# 커스텀 데이터베이스
python scripts/core/neo4j_loader.py \
    --ttl output/hvdc_status_v35.ttl \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password password \
    --database hvdc
```

**옵션**:
- `--ttl, -t`: 로드할 TTL 파일 경로 (필수)
- `--uri`: Neo4j URI (기본값: `bolt://localhost:7687` or `$NEO4J_URI`)
- `--user`: Neo4j 사용자 (기본값: `neo4j` or `$NEO4J_USER`)
- `--password`: Neo4j 비밀번호 (필수, 또는 `$NEO4J_PASSWORD`)
- `--database`: Neo4j 데이터베이스 이름 (기본값: `neo4j`)
- `--verbose, -v`: 상세 출력

---

## 🔄 일반적인 워크플로우

### 완전한 변환 파이프라인

```bash
# 1. Excel에서 Flow Code 계산 (검증용)
python scripts/core/flow_code_calc.py \
    --input data/HVDC_STATUS.xlsx \
    --output output/flow_codes.csv

# 2. Excel → TTL 변환 (Flow Code v3.5 포함)
python scripts/core/excel_to_ttl.py \
    --input data/HVDC_STATUS.xlsx \
    --output output/hvdc_status_v35.ttl \
    --schema logiontology/configs/ontology/hvdc_event_schema.ttl

# 3. TTL 검증
python scripts/core/validate_schema.py \
    --ttl output/hvdc_status_v35.ttl \
    --schema logiontology/configs/ontology/hvdc_event_schema.ttl

# 4. TTL → JSON 변환 (GPT용)
python scripts/core/ttl_to_json.py \
    --input output/hvdc_status_v35.ttl \
    --output output/hvdc_flat.json \
    --views output/views/

# 5. (선택) Neo4j 로드
python scripts/core/neo4j_loader.py \
    --ttl output/hvdc_status_v35.ttl \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password password
```

---

## 📋 요구사항

### Python 패키지
```bash
pip install -r requirements.txt
```

**필수 패키지**:
- `pandas` - Excel 처리
- `rdflib` - RDF/TTL 처리
- `pyshacl` - SHACL 검증 (선택)
- `neo4j` - Neo4j 연동 (선택)

### 데이터 요구사항

**Excel 파일 구조**:
- 창고 컬럼: `DSV Indoor`, `DSV Outdoor`, `MOSB`, etc.
- 사이트 컬럼: `SHU`, `MIR`, `DAS`, `AGI`
- 메타데이터: `HVDC CODE`, `VENDOR`, `G.W(KG)`, `CBM`, etc.

---

## 🔍 트러블슈팅

### 1. 컬럼 매칭 실패
**문제**: `Found columns: WH=0, SITE=0`

**해결**:
```bash
# 커스텀 컬럼 지정
python scripts/core/flow_code_calc.py \
    --input data.xlsx \
    --warehouses "창고1,창고2,MOSB" \
    --sites "사이트1,사이트2"
```

### 2. Flow Code 계산 오류
**문제**: `FLOW_CODE` 값이 0~5 범위를 벗어남

**해결**:
- Excel 파일의 날짜 컬럼 형식 확인 (YYYY-MM-DD)
- `ATA` 컬럼 존재 여부 확인
- `--verbose` 옵션으로 상세 로그 확인

### 3. TTL 파싱 오류
**문제**: `Failed to parse TTL`

**해결**:
- TTL 파일 인코딩 확인 (UTF-8)
- 파일 크기 확인 (메모리 부족)
- RDFLib 버전 확인 (`pip install --upgrade rdflib`)

### 4. Neo4j 연결 실패
**문제**: `Failed to connect to Neo4j`

**해결**:
- Neo4j 서버 실행 확인
- URI 형식 확인 (`bolt://` prefix)
- 방화벽/포트 확인 (기본 포트: 7687)

---

## 📚 추가 문서

- [Flow Code v3.5 Algorithm](../../docs/flow_code_v35/FLOW_CODE_V35_ALGORITHM.md)
- [Master Documentation](../../docs/flow_code_v35/FLOW_CODE_V35_MASTER_DOCUMENTATION.md)
- [MCP Integration](../../docs/mcp_integration/MCP_FLOW_CODE_V35_INTEGRATION.md)
- [Project Documentation](../../PROJECT_COMPLETE_DOCUMENTATION.md)

---

## 🔗 관련 링크

- **프로젝트 루트**: `../../`
- **원본 소스**: `../../logiontology/src/`
- **테스트**: `../../tests/`
- **출력 데이터**: `../../output/`

---

**Last Updated**: 2025-10-31
**Version**: 1.0
**Author**: MACHO-GPT v3.4-mini + Flow Code v3.5

