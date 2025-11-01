# HVDC Event-Based Ontology - 완료 패키지

**날짜**: 2025-10-30
**버전**: 1.0
**상태**: ✅ 완료

## 패키지 내용

이 패키지는 HVDC 물류 데이터를 이벤트 기반 온톨로지로 변환하는 완전한 시스템입니다.

### 디렉토리 구조

```
hvdc_final_package/
├── ontology_schemas/              온톨로지 스키마
│   ├── hvdc_event_schema.ttl     이벤트 온톨로지 (OWL + SHACL)
│   └── hvdc_nodes.ttl             HVDC 물류 노드 정의
├── conversion_scripts/            변환 스크립트
│   ├── excel_to_ttl_with_events.py    Excel → TTL 변환기
│   ├── ttl_to_json_flat.py            TTL → JSON 변환기
│   └── convert_data_wh_to_ttl.py      통합 CLI 스크립트
├── validation/                    검증 도구
│   ├── validate_events_with_sparql.py  SPARQL 검증 스크립트
│   └── event_validation.sparql         10개 검증 쿼리
├── test_results/                  테스트 결과
│   ├── test_event_injection.py         pytest 테스트 (14개)
│   └── *.json                          검증 결과 파일들
├── sample_outputs/                샘플 출력
│   ├── test_data_wh_events.ttl        샘플 TTL (8,995 케이스)
│   ├── test_data_wh_flat.json         샘플 평탄화 JSON
│   └── *.json                          사전집계 뷰 (3개)
├── IMPLEMENTATION_SUMMARY.md      구현 요약 문서
└── README.md                      이 파일
```

## 주요 파일 설명

### 1. 온톨로지 스키마
- **hvdc_event_schema.ttl**: 이벤트 기반 온톨로지 (Case, StockEvent, Warehouse, Site, Hub)
- **hvdc_nodes.ttl**: HVDC 6개 물류 노드 정의

### 2. 변환 스크립트
- **excel_to_ttl_with_events.py**: Excel → TTL 변환 (FLOW 기반 이벤트 주입)
- **ttl_to_json_flat.py**: TTL → JSON 변환 (GPT용 평탄화)
- **convert_data_wh_to_ttl.py**: 통합 CLI 스크립트

### 3. 검증 도구
- **validate_events_with_sparql.py**: SPARQL 검증 스크립트
- **event_validation.sparql**: 10개 검증 쿼리 (월별/Vendor별 집계)

### 4. 테스트
- **test_event_injection.py**: pytest 테스트 (14개, 모두 통과)
- 검증 결과 JSON 파일들

### 5. 샘플 출력
- **hvdc_data.ttl**: 8,995 케이스 TTL (GPT 업로드용)
- **hvdc_data_flat.json**: GPT용 평탄화 JSON
- 사전집계 뷰: 월별 창고, Vendor별, FLOW별 분포

## 사용 방법

### Excel → TTL 변환
```bash
python conversion_scripts/convert_data_wh_to_ttl.py \
  --input DATA_WH.xlsx \
  --output-ttl output.ttl \
  --schema ontology_schemas/hvdc_event_schema.ttl
```

### TTL → JSON 변환
```bash
python conversion_scripts/ttl_to_json_flat.py \
  output.ttl \
  output.json \
  views_dir
```

### SPARQL 검증
```bash
python validation/validate_events_with_sparql.py \
  --ttl output.ttl \
  --output validation_results
```

### pytest 실행
```bash
pytest test_results/test_event_injection.py -v
```

## 통계 (샘플 실행 결과)

- **총 케이스**: 8,995
- **Inbound 이벤트**: 5,012 (55.72%)
- **Outbound 이벤트**: 2,381 (26.47%)
- **Human-gate 이슈**: 0건
- **pytest**: 14/14 통과 (100%)

## FLOW 코드 규칙

| FLOW | 설명 | Inbound | Outbound |
|------|------|---------|----------|
| 0 | NO_FLOW | ❌ | ❌ |
| 1 | 직송 (Site 직접) | Site 최소 날짜 | ❌ |
| 2 | 창고 경유 | 창고 최소 날짜 | Site 최소 날짜 |
| 3 | 복합 (창고+사이트) | 창고/Site 최소 날짜 | Final_Location_Date |

## 의존성

```
pandas>=2.0.0
rdflib>=7.0.0
openpyxl>=3.1.0
pytest>=7.0.0
```

## 문서

상세 내용은 `IMPLEMENTATION_SUMMARY.md`를 참고하세요.

## GPT Copilot 설정

### GPT에 업로드할 파일
1. **필수**: `sample_outputs/hvdc_data.ttl` (TTL 메인 데이터)
2. **선택**: `sample_outputs/hvdc_data_flat.json` (빠른 조회용)
3. **선택**: 사전집계 JSON 파일들 (월별/벤더별 통계)

### GPT 프롬프트
`GPT_PROMPT.md` 파일을 GPT Builder의 "Instructions"에 복사하세요.

**설정 가이드**:
1. GPT Builder 열기
2. "Instructions"에 `GPT_PROMPT.md` 내용 붙여넣기
3. "Knowledge"에 `hvdc_data.ttl` 업로드
4. 테스트: "TTL 기반 HVDC 화물 조회 시스템 준비 완료" 응답 확인

## MCP TTL Server (NEW!)

실시간 SPARQL 쿼리 서버로 GPT Custom Action 연동 가능.

### 서버 실행

```bash
cd hvdc_final_package
python -m uvicorn mcp_server.mcp_ttl_server:app --reload --host 0.0.0.0 --port 8000
```

### API 테스트

```bash
# Health check
curl http://localhost:8000/health

# Case lookup
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "case_lookup", "params": {"case_id": "Case_00045"}}'

# Commands list
curl http://localhost:8000/commands
```

### GPT Custom Action

1. 서버 실행 후 `http://localhost:8000/openapi.json` 다운로드
2. GPT Builder > Actions > Import from OpenAPI
3. 테스트: "Lookup Case_00045 from HVDC TTL data"

상세 가이드: `mcp_server/MCP_SERVER_README.md`

## 라이선스

Internal Samsung Project - Confidential

---

**패키지 상태**: ✅ PRODUCTION READY
**품질 검증**: ✅ 14/14 테스트 통과
**데이터 품질**: ✅ 0건 Human-gate 이슈
**GPT 준비**: ✅ 프롬프트 및 데이터 포함
**MCP 서버**: ✅ FastAPI + SPARQL 실시간 조회

