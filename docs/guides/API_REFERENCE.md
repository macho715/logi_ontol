# HVDC Full Stack MVP - API Reference

**Version**: 2.0.0
**Base URL**: `http://localhost:8000`
**Protocol**: HTTP/HTTPS

---

## 개요

HVDC Logistics API는 RESTful 방식으로 설계된 8개의 엔드포인트를 제공합니다.

**인증**: 현재 버전(v2.0.0)에서는 인증이 필요하지 않습니다. (Phase 3에서 JWT 추가 예정)

**응답 형식**: JSON

**CORS**: 활성화 (개발 환경)

---

## Endpoints

### 1. Root Endpoint

**GET /**

프로젝트 정보 및 API 버전 확인

**Request**:
```bash
curl http://localhost:8000/
```

**Response** (200 OK):
```json
{
  "message": "Welcome to HVDC Logistics Ontology API v2.0.0",
  "version": "2.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

### 2. Health Check

**GET /health**

시스템 상태 확인 (모니터링용)

**Request**:
```bash
curl http://localhost:8000/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-10-26T12:34:56.789Z"
}
```

---

### 3. List Flows

**GET /api/flows**

모든 물류 플로우 목록 조회

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit     | int  | No       | 100     | 결과 개수 제한 |
| offset    | int  | No       | 0       | 결과 시작 위치 |

**Request**:
```bash
curl "http://localhost:8000/api/flows?limit=10&offset=0"
```

**Response** (200 OK):
```json
{
  "total": 45,
  "limit": 10,
  "offset": 0,
  "flows": [
    {
      "flow_id": "flow-001",
      "hvdc_code": "HVDC-ADOPT-SCT-0001",
      "flow_code": 2,
      "warehouse": "DSV INDOOR",
      "site": "MIR",
      "port": "ZAYED",
      "weight": 25.5
    },
    ...
  ]
}
```

---

### 4. Get Flow Details

**GET /api/flows/{flow_id}**

특정 플로우의 상세 정보 조회

**Path Parameters**:
| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| flow_id   | string | Yes      | Flow 고유 ID |

**Request**:
```bash
curl http://localhost:8000/api/flows/flow-001
```

**Response** (200 OK):
```json
{
  "flow_id": "flow-001",
  "hvdc_code": "HVDC-ADOPT-SCT-0001",
  "flow_code": 2,
  "flow_description": "WH Once (Port → WH → Site)",
  "warehouse": {
    "name": "DSV INDOOR",
    "location": "Mussafah"
  },
  "site": {
    "name": "MIR",
    "type": "Land Site"
  },
  "port": {
    "name": "ZAYED",
    "customs_code": "ADNOC 47150"
  },
  "weight": 25.5,
  "offshore_flag": false,
  "wh_handling_count": 1
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Flow not found"
}
```

---

### 5. Search Flows

**GET /api/search**

플로우 검색 (다양한 필터)

**Query Parameters**:
| Parameter    | Type   | Required | Description |
|--------------|--------|----------|-------------|
| hvdc_code    | string | No       | HVDC 코드 검색 |
| site         | string | No       | 목적지 사이트 |
| warehouse    | string | No       | 창고명 |
| flow_code    | int    | No       | Flow Code (0-4) |
| min_weight   | float  | No       | 최소 무게 |
| max_weight   | float  | No       | 최대 무게 |

**Request**:
```bash
curl "http://localhost:8000/api/search?site=MIR&flow_code=2"
```

**Response** (200 OK):
```json
{
  "query": {
    "site": "MIR",
    "flow_code": 2
  },
  "count": 12,
  "results": [
    {
      "flow_id": "flow-001",
      "hvdc_code": "HVDC-ADOPT-SCT-0001",
      "flow_code": 2,
      ...
    },
    ...
  ]
}
```

---

### 6. KPI Dashboard

**GET /api/kpi/**

실시간 KPI 대시보드 데이터

**Request**:
```bash
curl http://localhost:8000/api/kpi/
```

**Response** (200 OK):
```json
{
  "total_flows": 45,
  "direct_delivery_rate": 22.2,
  "mosb_pass_rate": 33.3,
  "avg_wh_hops": 1.4,
  "flow_distribution": {
    "PRE_ARRIVAL": 2,
    "DIRECT": 10,
    "WH_ONCE": 18,
    "WH_MOSB": 12,
    "WH_DOUBLE_MOSB": 3
  },
  "mode_distribution": {
    "Container": 25,
    "Bulk": 12,
    "Land": 5,
    "LCT": 3
  }
}
```

**KPI 설명**:
- `direct_delivery_rate`: Direct delivery (Flow Code 1) 비율 (%)
- `mosb_pass_rate`: MOSB 경유 플로우 비율 (%)
- `avg_wh_hops`: 평균 창고 경유 횟수

---

### 7. SPARQL Query

**POST /api/sparql/**

SPARQL 쿼리 실행 (RDF 그래프 대상)

**Request Body**:
```json
{
  "query": "SELECT ?cargo ?code WHERE { ?cargo hvdc:hasHVDCCode ?code } LIMIT 10"
}
```

**Request**:
```bash
curl -X POST http://localhost:8000/api/sparql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT ?cargo ?code WHERE { ?cargo hvdc:hasHVDCCode ?code } LIMIT 10"}'
```

**Response** (200 OK):
```json
{
  "query": "SELECT ?cargo ?code WHERE ...",
  "results": [
    {
      "cargo": "https://hvdc.example.org/id/Cargo/cargo-001",
      "code": "HVDC-ADOPT-SCT-0001"
    },
    ...
  ],
  "count": 10
}
```

**샘플 쿼리**:
```sparql
# 1. Get all cargo
SELECT ?cargo ?code ?weight
WHERE {
  ?cargo a hvdc:Cargo ;
         hvdc:hasHVDCCode ?code ;
         hvdc:weight ?weight .
}
LIMIT 10

# 2. Get cargo by site
SELECT ?cargo ?code ?site
WHERE {
  ?cargo hvdc:hasHVDCCode ?code ;
         hvdc:destinedTo ?siteIRI .
  ?siteIRI hvdc:siteName ?site .
  FILTER (?site = "MIR")
}

# 3. Flow code distribution
SELECT ?flowCodeValue (COUNT(?cargo) AS ?count)
WHERE {
  ?cargo hvdc:hasFlowCode ?flowCode .
  ?flowCode hvdc:flowCodeValue ?flowCodeValue .
}
GROUP BY ?flowCodeValue
ORDER BY ?flowCodeValue
```

---

### 8. Cypher Query

**POST /api/cypher/**

Cypher 쿼리 실행 (Neo4j 대상)

**Request Body**:
```json
{
  "query": "MATCH (c:Cargo) RETURN c.hvdc_code AS code LIMIT 10",
  "parameters": {}
}
```

**Request**:
```bash
curl -X POST http://localhost:8000/api/cypher/ \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (c:Cargo) RETURN c.hvdc_code AS code LIMIT 10"}'
```

**Response** (200 OK):
```json
{
  "query": "MATCH (c:Cargo) RETURN c.hvdc_code AS code LIMIT 10",
  "results": [
    {"code": "HVDC-ADOPT-SCT-0001"},
    {"code": "HVDC-ADOPT-SCT-0002"},
    ...
  ],
  "count": 10
}
```

**샘플 쿼리**:
```cypher
// 1. Get all cargo nodes
MATCH (c:Cargo)
RETURN c.hvdc_code AS code, c.weight AS weight
LIMIT 10

// 2. Get cargo with warehouse
MATCH (c:Cargo)-[:STOREDAT]->(w:Warehouse)
RETURN c.hvdc_code AS code, w.name AS warehouse
LIMIT 10

// 3. Flow path
MATCH path = (p:Port)-[:FROMPORT]-(c:Cargo)-[:STOREDAT]-(w:Warehouse)--(s:Site)
RETURN path
LIMIT 5

// 4. Count by flow code
MATCH (c:Cargo)-[:HASFLOWCODE]->(f:FlowCode)
RETURN f.flowCodeValue AS code, COUNT(c) AS count
ORDER BY code
```

---

## Error Responses

### 400 Bad Request
잘못된 요청 (파라미터 오류)

```json
{
  "detail": "Invalid parameter: limit must be positive integer"
}
```

### 404 Not Found
리소스를 찾을 수 없음

```json
{
  "detail": "Flow not found"
}
```

### 500 Internal Server Error
서버 내부 오류

```json
{
  "detail": "An unexpected error occurred"
}
```

---

## Rate Limiting

현재 버전(v2.0.0)에서는 Rate Limiting이 적용되지 않습니다.

**Phase 3에서 추가 예정**:
- 일반 요청: 100 requests/minute
- 쿼리 엔드포인트: 10 requests/minute

---

## Authentication

현재 버전(v2.0.0)에서는 인증이 필요하지 않습니다.

**Phase 3에서 추가 예정**:
- JWT 기반 인증
- API Key 인증 (선택적)

**예상 헤더**:
```
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
```

---

## Examples

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Get KPI
kpi_response = requests.get(f"{BASE_URL}/api/kpi/")
print(kpi_response.json())

# SPARQL Query
sparql_query = {
    "query": "SELECT ?cargo ?code WHERE { ?cargo hvdc:hasHVDCCode ?code } LIMIT 5"
}
sparql_response = requests.post(
    f"{BASE_URL}/api/sparql/",
    json=sparql_query
)
print(sparql_response.json())
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// Get KPI
fetch(`${BASE_URL}/api/kpi/`)
  .then(response => response.json())
  .then(data => console.log(data));

// Cypher Query
const cypherQuery = {
  query: "MATCH (c:Cargo) RETURN c.hvdc_code AS code LIMIT 5",
  parameters: {}
};

fetch(`${BASE_URL}/api/cypher/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(cypherQuery)
})
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## Interactive Documentation

**Swagger UI**: http://localhost:8000/docs
- 모든 엔드포인트 인터랙티브 테스트
- 요청/응답 스키마 확인

**ReDoc**: http://localhost:8000/redoc
- 읽기 친화적 API 문서
- 다운로드 가능

---

## Changelog

### v2.0.0 (2025-10-26)
- ✅ 8개 엔드포인트 구현
- ✅ Swagger UI/ReDoc 통합
- ⏳ 인증 미구현 (Phase 3 예정)
- ⏳ Rate limiting 미구현 (Phase 3 예정)

---

## Support

문제 발생 시:
1. [Troubleshooting Guide](TROUBLESHOOTING.md) 확인
2. [GitHub Issues](https://github.com/your-repo/issues) 생성
3. 프로젝트 관리자에게 문의

---

**마지막 업데이트**: 2025-10-26

