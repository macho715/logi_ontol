# HVDC Logistics & Ontology System

**통합 물류 온톨로지 시스템 for HVDC Project**
(Samsung C&T + ADNOC·DSV Partnership)

> **⚠️ 중요**: 메인 구현 패키지는 **[`logiontology/`](logiontology/)** 폴더입니다!
> - **전체 구현 코드**: `logiontology/src/`
> - **설정 파일**: `logiontology/configs/`
> - **온톨로지 정의**: `logiontology/configs/ontology/`
> - **MCP 서버**: `hvdc_mcp_server_v35/`
> - **문서 인덱스**: [docs/README.md](docs/README.md)

---

## 개요

HVDC 프로젝트의 물류 데이터를 온톨로지 기반으로 관리하고 분석하는 Full Stack MVP 시스템입니다.

**주요 기능**:
- 온톨로지 기반 데이터 모델 (OWL/TTL)
- Excel → RDF 변환
- Neo4j 그래프 DB 통합
- FastAPI REST API (8 endpoints)
- Docker 전체 스택 배포

---

## 프로젝트 상태

### logiontology v2.0.0 (메인 프로젝트)
**Status**: Backend Core 완료 (72%)

**완료된 구성요소** (15/25 tasks):
- ✅ 온톨로지 스키마 (7 classes, 11 properties)
- ✅ Excel → RDF 변환기
- ✅ Neo4j 통합 (store + loader + config)
- ✅ FastAPI Backend (8 endpoints)
- ✅ CLI (7 commands)
- ✅ Docker 배포
- ✅ 문서화 (7 docs)
- ✅ 테스트 (90%+ coverage)

**다음 단계** (Phase 2):
- API 실제 구현 (Neo4j 쿼리 연결)
- AI Insights Service
- PDF Report Generator
- React Frontend

**자세한 내용**: [Master Plan](plan.md) | [Work Log](docs/project_reports/HVDC_WORK_LOG.md) | [전체 문서](PROJECT_COMPLETE_DOCUMENTATION.md)

---

## 빠른 시작

### 전제 조건
- Python 3.13+
- Docker 20+
- Git

### 5분 시작 가이드

```bash
# 1. 프로젝트로 이동
cd logiontology

# 2. 의존성 설치
pip install -e ".[dev,api,graph]"

# 3. Neo4j 시작
docker run -d --name hvdc-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/hvdc_password \
  neo4j:5.14

# 4. 데이터 변환 (샘플 Excel 파일)
logiontology ingest-excel data/sample.xlsx

# 5. Neo4j 로드
export NEO4J_PASSWORD=hvdc_password
logiontology setup-neo4j
logiontology load-neo4j output/sample.ttl

# 6. API 서버 시작
logiontology serve-api --reload
```

**API Docs**: http://localhost:8000/docs
**Neo4j Browser**: http://localhost:7474

### Docker Compose (전체 스택)

```bash
cd logiontology
docker-compose up -d
```

**자세한 가이드**: [Quick Start](docs/guides/QUICK_START.md)

---

## 프로젝트 구조

```
logi_ontol/
├── 📄 README.md                     # 프로젝트 개요
├── 📄 plan.md                       # Master Plan v2.0.0
├── 📄 PROJECT_COMPLETE_DOCUMENTATION.md  # v3.5 완전 문서
├── 📄 requirements.txt              # 전체 의존성
│
├── 📁 logiontology/                 # ⭐ 메인 패키지 (v2.0.0 + Flow Code v3.5)
│   ├── src/                         # 소스 코드
│   │   ├── ingest/                  # Excel → RDF + Flow Code v3.5
│   │   ├── ontology/                # 온톨로지 로더, validator
│   │   ├── graph/                   # Neo4j integration
│   │   ├── api/                     # FastAPI endpoints
│   │   ├── export/                  # TTL → JSON
│   │   └── cli.py                   # CLI commands
│   ├── configs/                     # 설정 + 온톨로지 TTL
│   ├── tests/                       # 테스트 (90%+)
│   └── docs/                        # 기술 문서
│
├── 📁 hvdc_mcp_server_v35/          # ⭐ MCP 서버 (v3.5)
│   ├── mcp_server/                  # SPARQL API
│   ├── tests/                       # 서버 테스트
│   └── README.md                    # MCP 가이드
│
├── 📁 extended/                     # 확장 온톨로지 (15개)
├── 📁 ontology/                     # 온톨로지 참조
│   ├── HVDC.MD                      # v3.0 정의
│   ├── core/                        # 핵심 문서 (8개)
│   ├── extended/                    # 확장 문서
│   └── ontology_data_hub/           # 온톨로지 데이터 허브
│       └── 01_ontology/
│           └── consolidated/        # 통합 온톨로지 (5개)
│
├── 📁 docs/                         # ⭐ 통합 문서
│   ├── folder_analysis/             # 📊 폴더별 상세 분석 (17개 보고서)
│   ├── flow_code_v35/               # Flow Code v3.5 (4개)
│   ├── mcp_integration/             # MCP 통합 (3개)
│   ├── project_reports/             # 프로젝트 보고서 (7개)
│   ├── guides/                      # 가이드
│   ├── architecture/                # 아키텍처
│   └── README.md                    # ⭐ 문서 인덱스
│
├── 📁 data/                         # 데이터
│   ├── source/                      # 원본 Excel (2개)
│   ├── reports/                     # 리포트 (2개)
│   └── backups/                     # 백업
│
├── 📁 output/                       # 출력
│   ├── hvdc_status_v35.ttl          # ⭐ 최신 (9,904 triples)
│   ├── validation/                  # SPARQL 검증
│   ├── gpt_cache/                   # GPT 캐시
│   └── final/                       # 최종 출력
│
├── 📁 scripts/                      # 스크립트
│   ├── setup/                       # 설정 스크립트 (3개)
│   ├── utils/                       # 유틸리티 (1개)
│   └── stage3_report/               # Stage 3 리포트
│
├── 📁 tests/                        # 루트 테스트 (4개)
├── 📁 queries/                      # SPARQL 쿼리
├── 📁 reports/                      # 분석 보고서 (55개)
│
├── 📁 archive/                      # ⭐ 레거시 아카이브
│   ├── legacy/                      # 이전 패키지 (4개)
│   └── output_history/              # 이전 출력
│
└── (프로젝트별: ABU, JPT71, HVDC Project Lightning)
```

**주요 변경사항** (2025-10-31):
- `ontology/logiontology/` → `archive/legacy/` (레거시 v2.0.0)
- `logiontology/` 최신 버전 (Flow Code v3.5 통합)
- 문서 통합 (`docs/flow_code_v35/`, `docs/mcp_integration/`, `docs/project_reports/`)
- 데이터 구조화 (`data/source/`, `data/reports/`)
- 스크립트 정리 (`scripts/setup/`, `scripts/utils/`)
- 출력 통합 (`output/validation/`, `output/gpt_cache/`)

**최근 정리** (2025-11-01):
- 루트 레벨 중복 폴더 제거: `core/`, `core_consolidated/` 삭제
- 완료 보고서 아카이브: 5개 → `archive/completion_reports/`
- 정식 경로만 참조: `ontology/core/`, `ontology_data_hub/01_ontology/consolidated/`

**폴더 분석 보고서 추가** (2025-11-01):
- 전체 프로젝트 폴더 구조 상세 분석 완료
- 17개 개별 보고서 + 마스터 인덱스 생성
- 위치: `docs/folder_analysis/`
- 포함 내용:
  - 핵심 프로젝트 (4개): logiontology, hvdc_mcp_server_v35, ontology, ontology_data_hub
  - 데이터/출력 (3개): data, output, queries
  - 문서/보고서 (3개): docs, reports, extended
  - 외부 프로젝트 (2개): ABU, HVDC Project Lightning
  - 개발 도구 (2개): scripts, tests
  - 아카이브/시스템 (2개): archive, 시스템폴더
- 각 보고서: 개요, 통계, 주요 파일, 하위 구조, 연관성, 권장사항

**Flow Code v3.5 전체 문서 통합** (2025-11-01):
- 9개 CONSOLIDATED 문서 전체에 Flow Code v3.5 통합 완료
- 총 329회 Flow Code 언급 (이전 3회 → 100배 증가)
- AGI/DAS 강제 규칙 (Flow ≥3) 전체 문서 반영
- 위치: `Logi ontol core doc/`
- 통합 문서:
  1. CONSOLIDATED-01 (Core Framework) - 11회
  2. CONSOLIDATED-02 (Warehouse & Flow) - 85회 (완전 통합)
  3. CONSOLIDATED-03 (Document OCR) - 34회 (OCR 추출 필드)
  4. CONSOLIDATED-04 (Barge/Bulk) - 27회 (LCT Flow 3/4)
  5. CONSOLIDATED-05 (Invoice/Cost) - 8회 (Flow Code 비용 구조)
  6. CONSOLIDATED-06 (Material Handling) - 23회 (Phase A/B)
  7. CONSOLIDATED-07 (Port Operations) - 43회 (Flow Code 시작점)
  8. CONSOLIDATED-08 (Communication) - 7회
  9. CONSOLIDATED-09 (Operations) - 36회 (KPI 메트릭)
- 주요 특징:
  - Flow Code 0~5 정의 (Pre Arrival, Direct, WH, MOSB, Full, Mixed)
  - AGI/DAS 도메인 룰: 오프쇼어 사이트 MOSB 레그 필수
  - 도메인별 Flow Code 패턴: Material, Barge, Port, Document, Cost
  - RDF/OWL 속성 9개, SHACL 제약 4개
  - SPARQL 쿼리 20+ 제공
- 관련 문서: `docs/flow_code_v35/`, `CORE_DOCUMENTATION_MASTER.md`

---

## 주요 기능

### 1. 온톨로지 스키마
- **파일**: `logiontology/configs/ontology/hvdc_ontology.ttl`
- **클래스**: Cargo, Site, Warehouse, Port, FlowCode, BillOfLading, Project (7개)
- **속성**: 11개 (5 Object Properties + 6 Datatype Properties)
- **샘플**: 15개 인스턴스 (sites, warehouses, ports, flow codes)

### 2. Excel → RDF 변환
- **지원 컬럼**: HVDC_CODE, WEIGHT, WAREHOUSE, SITE, PORT, FLOW_CODE
- **자동 처리**: Site/Warehouse 정규화, Flow Code 계산
- **배치 처리**: 디렉토리 단위 변환
- **검증**: SHACL 자동 검증

### 3. Neo4j 그래프 DB
- **RDF → Neo4j 매핑**: 자동 변환 (Node + Relationship)
- **인덱스**: flow_code, hvdc_code, site_name, warehouse_name, port_name
- **제약조건**: cargo hvdc_code unique
- **쿼리**: Cypher 및 SPARQL 지원

### 4. FastAPI REST API
**8개 엔드포인트**:
1. `GET /` - API 정보
2. `GET /health` - 헬스 체크
3. `GET /api/flows` - 플로우 목록 (pagination)
4. `GET /api/flows/{id}` - 플로우 상세
5. `GET /api/search` - 플로우 검색
6. `GET /api/kpi/` - KPI 대시보드
7. `POST /api/sparql/` - SPARQL 쿼리
8. `POST /api/cypher/` - Cypher 쿼리

**API Docs**: http://localhost:8000/docs (Swagger UI)

### 5. CLI (7개 명령어)
```bash
logiontology ingest-excel FILE.xlsx    # Excel → RDF
logiontology load-neo4j FILE.ttl       # RDF → Neo4j
logiontology setup-neo4j               # 인덱스/제약조건 설정
logiontology serve-api --reload        # API 서버 시작
logiontology batch-ingest DIR/         # 배치 처리
logiontology run                       # 레거시 파이프라인
logiontology make-id                   # ID 생성
```

### 6. Docker 배포
**3개 서비스**:
- **neo4j**: Neo4j 5.14 (ports: 7474, 7687)
- **backend**: FastAPI (port: 8000)
- **frontend**: React (port: 3000, placeholder)

```bash
docker-compose up -d
```

---

## 외부 데이터 소스

### ABU/ (Abu Dhabi Logistics)
- WhatsApp 데이터 통합: 67,499개 메시지
- RDF 그래프: 23,331개 트리플
- 실시간 운영 대시보드

### JPT71/ (Jopetwil 71 Vessel Operations)
- PDF 문서 20+, 이미지 400+
- 선박 운항 데이터 분석
- 네트워크 시각화

### HVDC Project Lightning/
- WhatsApp 데이터: 11,517개 메시지
- RDF 그래프: 67,000+ 트리플
- CSV 엔티티: 331개

---

## 문서

### 핵심 문서
- **[README.md](README.md)** - 프로젝트 개요 (이 문서)
- **[plan.md](plan.md)** - Master Plan v2.0.0
- **[PROJECT_COMPLETE_DOCUMENTATION.md](PROJECT_COMPLETE_DOCUMENTATION.md)** - v3.5 완전 문서
- **[docs/README.md](docs/README.md)** - 문서 전체 인덱스 ⭐

### Flow Code v3.5 & MCP 문서
- **[Flow Code v3.5 문서](docs/flow_code_v35/)** (4개)
  - 알고리즘, 구현, 통합, 마스터 문서
- **[MCP 통합 문서](docs/mcp_integration/)** (3개)
  - MCP 서버 v3.5, 통합 가이드, 최종 보고서

### 프로젝트 보고서
- **[프로젝트 보고서](docs/project_reports/)** (7개)
  - Work Log, Changelog, 구현 요약 등

### 온톨로지 참조
- [HVDC.MD](ontology/HVDC.MD) - HVDC v3.0 정의
- [ontology/core/](ontology/core/) - 핵심 온톨로지 문서 (8개)
- [ontology_data_hub/01_ontology/consolidated/](ontology_data_hub/01_ontology/consolidated/) - 통합 온톨로지 (5개)
- [extended/](extended/) - 확장 온톨로지 (15개)

### 가이드 & 아키텍처
- [Quick Start](docs/guides/QUICK_START.md) - 5분 빠른 시작
- [API Reference](docs/guides/API_REFERENCE.md) - API 레퍼런스
- [Architecture](docs/architecture/) - 시스템 아키텍처

---

## 설치

```bash
# 1. 저장소 클론
git clone https://github.com/macho715/logi_ontol.git
cd logi_ontol

# 2. 가상환경 생성
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. logiontology 설치
cd logiontology
pip install -e ".[dev,api,graph]"
```

---

## 테스트

```bash
# 전체 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest --cov=src --cov-report=term-missing

# API 테스트만
pytest tests/api/ -v
```

**테스트 커버리지**: 90%+ (43개 테스트)

---

## 성능 목표

### 현재 (v2.0.0)
- API Response: < 2s
- Test Coverage: 90%+
- Success Rate: 95%+

### 목표 (v3.0.0)
- API Response: < 500ms
- Test Coverage: 95%+
- Success Rate: 98%+
- Uptime: 99.9%

---

## 기술 스택

### Backend
- Python 3.13
- FastAPI 0.104+
- uvicorn (ASGI server)
- Neo4j 5.14
- RDFLib (OWL/TTL)
- pyshacl (SHACL validation)
- pandas (Data processing)
- Pydantic (Data validation)

### DevOps
- Docker 20+
- Docker Compose
- pytest (Testing)
- ruff (Linting)
- black (Formatting)

### 추후 추가 예정 (Phase 2-3)
- React (Frontend)
- Redis (Caching)
- Jinja2 + WeasyPrint (PDF Reports)
- Claude API (AI Insights)
- Kubernetes (Orchestration)

---

## 로드맵

### Phase 1: Backend Core (✅ 완료 - 72%)
- 온톨로지 스키마
- Excel → RDF 변환
- Neo4j 통합
- FastAPI Backend
- Docker 배포
- 문서화

### Phase 2A: 핵심 기능 완성 (🔄 계획 - 10-12시간)
- Real data testing
- API 실제 구현
- Integration tests

### Phase 2B: 확장 기능 (⏳ 대기 - 15-20시간)
- AI Insights Service
- PDF Report Generator
- React Frontend

### Phase 3: Production (⏳ 대기 - 10-15시간)
- Security (JWT, HTTPS)
- Performance (Redis, Query optimization)
- DevOps (CI/CD, Kubernetes, Monitoring)

**예상 완성 시점**: 6주 (Full Stack MVP 완성)

---

## 기여

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 라이선스

**프로젝트**: HVDC Logistics & Ontology System
**소유자**: Samsung C&T Logistics (ADNOC·DSV Partnership)
**버전**: 2.0.0
**최종 업데이트**: 2025-10-31

---

## 관련 링크

### 📚 핵심 문서
- **[문서 전체 인덱스](docs/README.md)** - 모든 문서 한눈에 보기 ⭐
- [Master Plan](plan.md) - 전체 프로젝트 계획
- [PROJECT_COMPLETE_DOCUMENTATION](PROJECT_COMPLETE_DOCUMENTATION.md) - v3.5 완전 문서

### 🚀 시작하기
- [Quick Start](docs/guides/QUICK_START.md) - 5분 빠른 시작
- [logiontology README](logiontology/README.md) - 메인 패키지 가이드
- [MCP Server README](hvdc_mcp_server_v35/README.md) - MCP 서버 가이드

### 📊 보고서
- [Work Log](docs/project_reports/HVDC_WORK_LOG.md) - v2.0.0 작업 로그
- [Changelog](docs/project_reports/CHANGELOG.md) - 변경 이력
- [Implementation Summary](docs/project_reports/IMPLEMENTATION_SUMMARY.md) - 구현 요약

### 🔬 Flow Code v3.5
- [Algorithm](docs/flow_code_v35/FLOW_CODE_V35_ALGORITHM.md) - 알고리즘 상세
- [Master Documentation](docs/flow_code_v35/FLOW_CODE_V35_MASTER_DOCUMENTATION.md) - 마스터 문서

---

**개발**: HVDC Project Team
**프로젝트**: Samsung C&T Logistics & ADNOC·DSV Partnership
**버전**: v3.5 (Flow Code + MCP Integration)
**최종 업데이트**: 2025-10-31

---

## 📊 프로젝트 상태 요약

- ✅ **Backend Core**: 완료 (logiontology v2.0.0)
- ✅ **Flow Code v3.5**: 완료 (0~5 분류, AGI/DAS 룰)
- ✅ **MCP Server**: 완료 (hvdc_mcp_server_v35)
- ✅ **문서화**: 완료 (48개+ 문서)
- ✅ **테스트**: 29/29 통과 (100%)
- ✅ **데이터**: 755 cases, 9,904 triples, 818 events
- 📋 **Next**: Phase 2A (API 실제 구현)
