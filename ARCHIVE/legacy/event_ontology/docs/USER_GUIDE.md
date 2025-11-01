# User Guide

## HVDC Event-Based Ontology System

이 가이드는 HVDC Event-Based Ontology System을 사용하는 방법을 안내합니다.

## Installation

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### 1. Excel → TTL Conversion

Excel 파일을 이벤트 기반 TTL로 변환합니다.

```bash
python scripts/convert.py \
  --input path/to/DATA_WH.xlsx \
  --output output/rdf/events.ttl \
  --schema config/ontology/hvdc_event_schema.ttl
```

**Arguments:**
- `--input`: 입력 Excel 파일 경로
- `--output`: 출력 TTL 파일 경로
- `--schema`: 온톨로지 스키마 TTL 파일 경로 (선택)

**Output:**
- TTL 파일이 생성됩니다
- 콘솔에 변환 통계가 출력됩니다

### 2. TTL → JSON Conversion (GPT-Ready)

TTL 파일을 GPT용 평탄화 JSON으로 변환합니다.

```bash
python scripts/convert_ttl_to_json.py \
  output/rdf/events.ttl \
  output/json/events.json \
  output/json/views
```

**Arguments:**
- `ttl_path`: TTL 파일 경로
- `output_path`: 출력 JSON 파일 경로
- `views_dir`: 사전 집계 뷰 출력 디렉토리 (선택)

**Output:**
- `events.json`: Case 단위 평탄화 JSON
- `views/monthly_warehouse_inbound.json`: 월별 창고 입고
- `views/vendor_summary.json`: Vendor별 요약
- `views/cases_by_flow.json`: FLOW 코드별 분포

### 3. Validation

SPARQL 쿼리로 데이터 품질을 검증합니다.

```bash
python scripts/validate.py \
  --ttl output/rdf/events.ttl \
  --output output/validation
```

**Arguments:**
- `--ttl`: TTL 파일 경로
- `--output`: 검증 결과 출력 디렉토리

**Output:**
- `human_gate_flow23_no_inbound.json`: FLOW 2/3 without inbound 목록
- `human_gate_missing_dates.json`: 날짜 없는 이벤트 목록
- `event_coverage_stats.json`: 커버리지 통계
- `flow_event_patterns.json`: FLOW별 패턴 검증

### 4. Testing

pytest로 자동화된 품질 테스트를 실행합니다.

```bash
pytest tests/ -v
```

**Test Coverage:**
- 14 automated tests
- Event generation rules
- Event properties validation
- Data quality checks
- Performance metrics

## FLOW Code Rules

| FLOW | Description | Inbound | Outbound |
|------|-------------|---------|----------|
| 0 | NO_FLOW | ❌ | ❌ |
| 1 | Direct to Site | Site 최소 날짜 | ❌ |
| 2 | Warehouse via | Warehouse 최소 날짜 | Site 최소 날짜 |
| 3 | Complex (mixed) | Warehouse/Site 최소 날짜 | Final_Location_Date |

## Event Properties

### Inbound Event
- `hasEventDate`: 입고 날짜 (YYYY-MM-DD)
- `hasLocationAtEvent`: 입고 위치 (창고/사이트명)
- `hasQuantity`: 수량 (Pkg 기준, default 1.0)

### Outbound Event
- `hasEventDate`: 출고 날짜 (YYYY-MM-DD)
- `hasLocationAtEvent`: 출고 위치
- `hasQuantity`: 수량

## Troubleshooting

### Encoding Errors (Windows)

Windows 콘솔에서 인코딩 오류가 발생하면 UTF-8로 설정:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Excel Load Errors

- Excel 파일이 바이너리 형식인지 확인
- `openpyxl` 패키지 설치 확인
- Excel 파일이 열려있지 않은지 확인

### TTL Parse Errors

- 온톨로지 스키마 경로 확인
- `rdflib` 버전 확인 (7.0+)
- TTL 파일이 손상되지 않았는지 확인

### SPARQL Query Errors

- 네임스페이스 prefix 확인
- FLOW 코드가 string으로 저장되어 있는지 확인
- 날짜 형식이 xsd:date인지 확인

## Examples

프로젝트 루트의 `examples/` 디렉토리에 샘플 파일이 포함되어 있습니다:
- `sample_input.xlsx`: 샘플 Excel 파일
- `sample_output.ttl`: 샘플 TTL 출력

## Support

문제가 발생하면 다음을 확인하세요:
1. `README.md`의 Quick Start 섹션
2. `docs/IMPLEMENTATION_SUMMARY.md`의 기술 문서
3. `queries/validation.sparql`의 SPARQL 쿼리 예제

## License

Internal Samsung Project - Confidential

