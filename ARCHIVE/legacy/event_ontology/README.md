# HVDC Event-Based Ontology System

**Version**: 1.0
**Date**: 2025-10-30
**Status**: Production Ready

## Overview

이 프로젝트는 HVDC 물류 데이터(Excel)를 이벤트 기반 RDF/OWL 온톨로지로 변환하고, GPT용 평탄화 JSON을 생성하는 완전한 파이프라인입니다.

### 주요 기능

- **Excel → TTL 변환**: 이벤트 기반 온톨로지로 자동 변환
- **FLOW 기반 이벤트 주입**: 물류 흐름(FLOW 1/2/3)에 따라 Inbound/Outbound 이벤트 자동 생성
- **TTL → JSON 변환**: GPT 질의를 위한 평탄화 JSON 생성
- **SPARQL 검증**: 데이터 품질 자동 검증
- **pytest 테스트**: 14개 자동화 테스트로 품질 보증

## Quick Start

### 1. 설치

```bash
pip install pandas rdflib openpyxl pytest
```

### 2. Excel → TTL 변환

```bash
python scripts/convert.py \
  --input path/to/DATA_WH.xlsx \
  --output output/rdf/events.ttl \
  --schema config/ontology/hvdc_event_schema.ttl
```

### 3. TTL → JSON 변환 (GPT용)

```bash
python scripts/convert_ttl_to_json.py \
  output/rdf/events.ttl \
  output/json/events.json \
  output/json/views
```

### 4. 검증 실행

```bash
python scripts/validate.py \
  --ttl output/rdf/events.ttl \
  --output output/validation
```

### 5. 테스트 실행

```bash
pytest tests/ -v
```

## Project Structure

```
hvdc_event_ontology_project/
├── README.md                  # 이 파일
├── requirements.txt           # Python 의존성
├── config/
│   └── ontology/
│       ├── hvdc_event_schema.ttl  # 이벤트 온톨로지 스키마
│       └── hvdc_nodes.ttl         # HVDC 노드 정의
├── scripts/
│   ├── convert.py            # Excel → TTL CLI
│   ├── convert_ttl_to_json.py # TTL → JSON CLI
│   └── validate.py           # SPARQL 검증 CLI
├── queries/
│   └── validation.sparql     # 10개 검증 쿼리
├── tests/
│   └── test_validators.py    # pytest 테스트 (14개)
├── examples/                 # 샘플 데이터
├── docs/                     # 상세 문서
└── output/                   # 출력 디렉토리
    ├── rdf/
    ├── json/
    └── validation/
```

## FLOW Code Rules

| FLOW | 설명 | Inbound | Outbound |
|------|------|---------|----------|
| 0 | NO_FLOW | ❌ | ❌ |
| 1 | 직송 (Site 직접) | Site 최소 날짜 | ❌ |
| 2 | 창고 경유 | 창고 최소 날짜 | Site 최소 날짜 |
| 3 | 복합 (창고+사이트) | 창고/Site 최소 날짜 | Final_Location_Date |

## Events

각 Case는 다음 이벤트를 가질 수 있습니다:

### Inbound Event
- `hasEventDate`: 입고 날짜
- `hasLocationAtEvent`: 입고 위치 (창고/사이트)
- `hasQuantity`: 수량

### Outbound Event
- `hasEventDate`: 출고 날짜
- `hasLocationAtEvent`: 출고 위치
- `hasQuantity`: 수량

## Statistics (Sample Run)

- **Total Cases**: 8,995
- **Inbound Events**: 5,012 (55.72%)
- **Outbound Events**: 2,381 (26.47%)
- **Human-gate Issues**: 0

## Test Results

```
✅ 14/14 tests passed
   - Event generation (4 tests)
   - Event properties (5 tests)
   - Data quality (4 tests)
   - Performance (2 tests)
```

## Documentation

- [USER_GUIDE.md](docs/USER_GUIDE.md) - 상세 사용법
- [IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) - 구현 요약
- [validation.sparql](queries/validation.sparql) - SPARQL 쿼리 모음

## License

Internal Samsung Project

## Contact

HVDC Logistics Team

