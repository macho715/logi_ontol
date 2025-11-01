# HVDC Full Stack MVP - Master Plan

**Version**: 2.0.0
**Status**: Backend Core Complete (72%)
**Updated**: 2025-10-31

> **⚠️ 중요**: 이 문서를 읽기 전에 **[`logiontology/`](logiontology/)** 폴더를 먼저 확인하세요!
> - **전체 구현 코드**: `logiontology/src/`
> - **설정 파일**: `logiontology/configs/`
> - **온톨로지 정의**: `logiontology/configs/ontology/`
> - **MCP 서버**: `hvdc_mcp_server_v35/`
> - **문서 인덱스**: [docs/README.md](docs/README.md)

---

## Executive Summary

**프로젝트**: HVDC Logistics & Ontology System
- logiontology v2.0.0 (메인 프로젝트)
- 통합 물류 네트워크 (ABU + JPT71 + Lightning)
- Samsung C&T + ADNOC·DSV Partnership

**현재 상태**:
- ✅ Backend Core 완료 (15/25 tasks)
- 🔄 다음 단계: API 실제 구현 + React Frontend
- 🎯 목표: Full Stack MVP 완성

---

## 프로젝트 구조

### 메인 프로젝트
**logiontology/** (v2.0.0 Backend Core)
- 온톨로지 스키마 (OWL/TTL)
- Excel → RDF 변환기
- Neo4j 그래프 DB 통합
- FastAPI REST API (8 endpoints)
- Docker 배포 환경

### 외부 데이터 소스
- **ABU/** - Abu Dhabi Logistics (WhatsApp + 473 entities)
- **JPT71/** - Jopetwil 71 Vessel Operations (PDF 20+ + Images 400+)
- **HVDC Project Lightning/** - Lightning Subsystem

### 지원 폴더
- **ontology/** - 온톨로지 정의 (core + extended)
- **data/** - 입력 데이터 (Excel)
- **output/** - RDF 출력 + 시각화
- **reports/** - 분석 보고서
- **scripts/** - 처리 스크립트
- **docs/** - 문서

---

## Phase 1: Backend Core (✅ 완료 - 72%)

### 1.1 온톨로지 스키마 (✅ 완료)
- [x] **hvdc_ontology.ttl** - 7 classes, 11 properties, 샘플 인스턴스
  - Classes: Cargo, Site, Warehouse, Port, FlowCode, BillOfLading, Project
  - Object Properties: storedAt, destinedTo, hasFlowCode, relatesToBL, fromPort
  - Datatype Properties: hasHVDCCode, weight, flowCodeValue, siteName, portName
- [x] **Ontology Loader** - OWL/TTL 파일 로더
  - Extract classes, properties, hierarchy
  - Get ontology metadata
- [x] **SHACL Validator** - 데이터 검증
  - Flow Code 범위 (0-4)
  - Weight 양수
  - 필수 속성 검증

### 1.2 데이터 수집 (✅ 완료)
- [x] **Excel → RDF Converter** (`src/ingest/excel_to_rdf.py`)
  - 지원 컬럼: HVDC_CODE, WEIGHT, WAREHOUSE, SITE, PORT, FLOW_CODE
  - Site/Warehouse 정규화 (SiteNormalizer)
  - Flow Code 자동 계산
- [x] **Batch Processor** (`src/ingest/batch_processor.py`)
  - 디렉토리 단위 처리
  - SHACL 검증 옵션
  - 에러 핸들링 및 로깅

### 1.3 그래프 DB (✅ 완료)
- [x] **Neo4j Config** (`configs/neo4j_config.yaml`)
  - Connection settings
  - Indexes: flow_code, hvdc_code, site_name, warehouse_name, port_name
  - Constraints: cargo hvdc_code unique
- [x] **Neo4j Store** (`src/graph/neo4j_store.py`)
  - Neo4j driver connection
  - RDF → Neo4j 매핑 (Node + Relationship)
  - Cypher query execution
- [x] **Neo4j Loader** (`src/graph/loader.py`)
  - TTL → Neo4j 로드
  - Batch directory loading
  - Database setup automation

### 1.4 REST API (✅ 완료)
- [x] **FastAPI Main App** (`src/api/main.py`)
  - 8 endpoints (flows, kpi, sparql, cypher)
  - CORS middleware
  - Health check
- [x] **KPI Endpoint** (`src/api/endpoints/kpi.py`)
  - FlowKPICalculator 통합
  - 실시간 KPI 대시보드
  - Flow 분포 분석
- [x] **SPARQL Endpoint** (`src/api/endpoints/sparql.py`)
  - RDFLib 그래프 쿼리
  - 샘플 쿼리 3개
- [x] **Cypher Endpoint** (`src/api/endpoints/cypher.py`)
  - Neo4j Cypher 쿼리
  - 샘플 쿼리 4개

### 1.5 배포 (✅ 완료)
- [x] **Docker Compose** (`docker-compose.yml`)
  - Neo4j 5.14 (health check)
  - Backend (FastAPI)
  - Frontend (placeholder)
  - Network configuration
- [x] **Dockerfile** (production-ready)
  - Python 3.13-slim
  - WeasyPrint 시스템 의존성
  - Optimized for production

### 1.6 CLI 확장 (✅ 완료)
7개 명령어:
- [x] `ingest-excel` - Excel → RDF 변환
- [x] `load-neo4j` - TTL → Neo4j 로드
- [x] `setup-neo4j` - 인덱스/제약조건 생성
- [x] `serve-api` - FastAPI 서버 시작
- [x] `batch-ingest` - 배치 처리
- [x] `run` - 기존 파이프라인 (레거시)
- [x] `make-id` - 결정적 ID 생성

### 1.7 문서화 (✅ 완료)
- [x] **README_FULL_STACK.md** - 전체 시스템 가이드
- [x] **IMPLEMENTATION_SUMMARY.md** - 구현 요약
- [x] **HVDC_WORK_LOG.md** - 상세 작업 로그 (1002 lines)
- [x] **logiontology/docs/** - 기술 문서 7개
  - ARCHITECTURE.md, FLOW_CODE_GUIDE.md, WORK_LOG_2025_10_26.md 등
- [x] **API Tests** - 7개 테스트 (pytest)

### 1.8 테스트 (✅ 완료)
- [x] Unit Tests - 26개 (기존)
  - test_flow_code.py (17 tests)
  - test_kpi_calculator.py (9 tests)
- [x] API Tests - 7개 (신규)
  - test_main.py (5 tests)
  - test_kpi_endpoint.py (2 tests)
- [x] Validation Tests - 10개 (SHACL)
- [x] **Coverage**: 90%+

---

## Phase 2A: 핵심 기능 완성 (🔄 계획 중 - 10-12시간)

### 2.1 실전 데이터 테스트 (2시간)
- [ ] 샘플 Excel 생성 (10-20행)
  - 실제 HVDC 데이터 구조
  - 모든 컬럼 포함
  - Flow Code 0-4 케이스 전부
- [ ] 전체 파이프라인 실행
  - Excel → RDF 변환
  - SHACL 검증
  - Neo4j 로드
  - API 쿼리
- [ ] 결과 검증
  - Neo4j 그래프 확인
  - API 응답 확인
  - KPI 계산 확인

### 2.2 API 실제 구현 (3시간)
- [ ] `/api/flows` 구현
  - Neo4j Cypher 쿼리 연결
  - Pagination (limit, offset)
  - 실제 데이터 반환
- [ ] `/api/flows/{id}` 구현
  - 특정 flow 조회
  - 관련 데이터 (warehouse, site, port) 조인
- [ ] `/api/search` 구현
  - 검색 필터 (hvdc_code, site, warehouse, flow_code)
  - Full-text search 옵션
- [ ] 에러 처리
  - 404 Not Found
  - 400 Bad Request
  - 500 Internal Server Error

### 2.3 통합 테스트 (3시간)
- [ ] E2E 테스트 작성
  - Excel → RDF → Neo4j → API 전체 플로우
  - Edge cases 처리
  - 성능 측정
- [ ] CI/CD 파이프라인 초기 구축
  - GitHub Actions 또는 GitLab CI
  - 자동 테스트 실행
  - Docker 이미지 빌드

### 2.4 문서화 업데이트 (2시간)
- [ ] API 사용 예시
  - cURL 예제
  - Python requests 예제
  - JavaScript fetch 예제
- [ ] 트러블슈팅 가이드
  - 일반적인 문제
  - 플랫폼별 주의사항
- [ ] Best Practices
  - 데이터 모델링
  - 성능 최적화

---

## Phase 2B: 확장 기능 (⏳ 대기 - 15-20시간)

### 2.5 AI Insights Service (4시간)
- [ ] Claude API 통합 (`src/ai/insights_service.py`)
  - 프롬프트 템플릿
  - 리스크 분석
  - 예측 모델
- [ ] `/api/insights` endpoint
  - Flow 리스크 분석
  - 최적화 제안
- [ ] Config (`configs/ai_config.yaml`)

### 2.6 PDF Report Generator (5시간)
- [ ] PDF 생성기 (`src/reports/pdf_generator.py`)
  - Jinja2 템플릿
  - WeasyPrint 통합
- [ ] Chart 생성 (`src/reports/chart_generator.py`)
  - Matplotlib 차트
  - Flow 분포, KPI 트렌드
- [ ] `/api/reports/pdf` endpoint
  - 커스터마이징 옵션

### 2.7 React Frontend (8시간)
- [ ] CRA 프로젝트 생성
  - TypeScript 설정
  - ESLint + Prettier
- [ ] 컴포넌트 3개
  - SearchFlow (검색 인터페이스)
  - KPIDashboard (KPI 시각화)
  - ReportViewer (PDF 뷰어)
- [ ] API 연동
  - Axios 설정
  - React Query 사용
- [ ] Dockerfile (`frontend/Dockerfile`)

---

## Phase 3: Production Ready (⏳ 대기 - 10-15시간)

### 3.1 Security (3시간)
- [ ] JWT 인증
  - 사용자 로그인
  - Token refresh
- [ ] HTTPS 설정
  - SSL 인증서
  - Nginx 리버스 프록시
- [ ] Rate Limiting
  - API 호출 제한
  - DDoS 방어

### 3.2 Performance (4시간)
- [ ] Redis Caching
  - KPI 결과 캐싱
  - 쿼리 결과 캐싱
- [ ] Query Optimization
  - Neo4j 쿼리 튜닝
  - 인덱스 최적화
- [ ] Load Testing
  - Locust 또는 k6
  - 성능 벤치마크

### 3.3 DevOps (5시간)
- [ ] CI/CD Pipeline
  - 자동 테스트
  - Docker 이미지 빌드
  - 자동 배포
- [ ] Kubernetes Manifests
  - Deployment, Service, Ingress
  - ConfigMap, Secret
- [ ] Monitoring/Logging
  - Prometheus + Grafana
  - ELK Stack (Elasticsearch, Logstash, Kibana)

---

## 빠른 시작

### 로컬 개발

```bash
# 1. 의존성 설치
cd logiontology
pip install -e ".[dev,api,graph]"

# 2. Neo4j 시작 (Docker)
docker run -d \
  --name hvdc-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/hvdc_password \
  neo4j:5.14

# 3. 샘플 데이터 준비
# data/sample.xlsx 생성

# 4. Excel → RDF 변환
logiontology ingest-excel data/sample.xlsx --out output/sample.ttl

# 5. Neo4j 설정
export NEO4J_PASSWORD=hvdc_password
logiontology setup-neo4j

# 6. RDF → Neo4j 로드
logiontology load-neo4j output/sample.ttl

# 7. API 서버 시작
logiontology serve-api --reload

# 8. API 테스트
curl http://localhost:8000/
curl http://localhost:8000/api/kpi/
open http://localhost:8000/docs
```

### Docker 전체 스택

```bash
# 1. 환경 변수 설정
echo "AI_API_KEY=your_key" > .env

# 2. 전체 스택 시작
docker-compose up -d

# 3. 서비스 확인
docker-compose ps

# 4. 서비스 접속
open http://localhost:7474  # Neo4j Browser
open http://localhost:8000/docs  # API Docs

# 5. 정지
docker-compose down
```

---

## 관련 문서

### 프로젝트 문서
- [HVDC_WORK_LOG.md](docs/project_reports/HVDC_WORK_LOG.md) - 상세 작업 로그 (v2.0.0)
- [IMPLEMENTATION_SUMMARY.md](docs/project_reports/IMPLEMENTATION_SUMMARY.md) - 구현 요약
- [CHANGELOG.md](docs/project_reports/CHANGELOG.md) - 변경 이력
- [문서 전체 인덱스](docs/README.md) - 모든 문서 링크

### 기술 문서
- [ARCHITECTURE.md](logiontology/docs/ARCHITECTURE.md) - 아키텍처 설계
- [FLOW_CODE_GUIDE.md](logiontology/docs/FLOW_CODE_GUIDE.md) - Flow Code 시스템
- [FLOW_CODE_IMPLEMENTATION_REPORT.md](logiontology/docs/FLOW_CODE_IMPLEMENTATION_REPORT.md) - 구현 보고서

### 온톨로지 및 아키텍처
- [HVDC.MD](ontology/HVDC.MD) - HVDC 온톨로지 정의
- [ontology/core/](ontology/core/) - 핵심 온톨로지 (8개 파일)
- [extended/](ontology/extended/) - 확장 온톨로지 (15개 파일)

### Flow Code v3.5 문서
- [FLOW_CODE_V35_MASTER_DOCUMENTATION.md](docs/flow_code_v35/FLOW_CODE_V35_MASTER_DOCUMENTATION.md) - 마스터 문서
- [FLOW_CODE_V35_ALGORITHM.md](docs/flow_code_v35/FLOW_CODE_V35_ALGORITHM.md) - 알고리즘 사양

### MCP Server 문서
- [MCP_SERVER_INTEGRATION_FINAL_REPORT.md](docs/mcp_integration/MCP_SERVER_INTEGRATION_FINAL_REPORT.md) - 통합 최종 보고서
- [MCP_FLOW_CODE_V35_INTEGRATION.md](docs/mcp_integration/MCP_FLOW_CODE_V35_INTEGRATION.md) - 통합 가이드

### 레거시 아카이브
- [아카이브 폴더](archive/legacy/) - 과거 패키지 (logiontology_v2.0.0, mcp_v1.0, mcp_v2.0, event_ontology)

---

## 성능 목표

### Current (v2.0.0)
- API Response: < 2s
- Test Coverage: 90%+
- Success Rate: 95%+
- Confidence: ≥ 0.97

### Target (v3.0.0)
- API Response: < 500ms
- Test Coverage: 95%+
- Success Rate: 98%+
- Uptime: 99.9%

---

## 프로젝트 통계

### 코드베이스
- Python 코드: ~3,500 lines
- 온톨로지 (TTL): 195 lines
- Config (YAML): 17 lines
- Docker: 90 lines
- 문서 (Markdown): 600+ lines
- 테스트: 160+ lines

### 파일
- 신규 파일: 27개
- 수정 파일: 2개
- 총 파일: 29개

### 의존성
- Python: 3.13+
- Neo4j: 5.14+
- FastAPI: 0.104+
- Node.js: 20+ (Frontend)
- Docker: 20+

---

## 라이선스 및 기여

**프로젝트**: HVDC Logistics & Ontology System
**소유자**: Samsung C&T Logistics (ADNOC·DSV Partnership)
**버전**: 2.0.0
**최종 업데이트**: 2025-10-31

기여 및 문의: 프로젝트 관리자에게 연락하세요.

