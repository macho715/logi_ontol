# HVDC Logistics & Ontology System

**통합 물류 온톨로지 시스템 for HVDC Project**
(Samsung C&T + ADNOC·DSV Partnership)

> **⚠️ 중요**: 이 문서를 읽기 전에 **[`ontology/logiontology/`](ontology/logiontology/)** 폴더를 먼저 확인하세요!
> - **전체 구현 코드**: `ontology/logiontology/src/`
> - **설정 파일**: `ontology/logiontology/configs/`
> - **온톨로지 정의**: `ontology/logiontology/configs/ontology/hvdc_ontology.ttl`
> - **문서**: `ontology/logiontology/README.md`, `ontology/logiontology/CHANGELOG.md`

---

## 개요

HVDC 프로젝트의 물류 데이터를 온톨로지 기반으로 관리하고 분석하는 Full Stack MVP 시스템입니다.

**주요 기능**:
- Protégé 기반 온톨로지 (OWL/TTL)
- Excel → RDF 변환
- Neo4j 그래프 DB 통합
- FastAPI REST API (8 endpoints)
- Docker 전체 스택 배포

---

## 프로젝트 상태

### logiontology v2.0.0 (메인 프로젝트)
**Status**: Backend Core 완료 (72%)

**완료된 구성요소** (15/25 tasks):
- ✅ Protégé 온톨로지 (7 classes, 11 properties)
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

**자세한 내용**: [Master Plan](plan.md) | [Work Log](HVDC_WORK_LOG.md)

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
├── plan.md                       # Master plan
├── README.md                     # 이 파일
├── HVDC_WORK_LOG.md             # 상세 작업 로그
│
├── logiontology/                 # ⭐ 메인 프로젝트 (v2.0.0)
│   ├── src/                      # 소스 코드
│   │   ├── ontology/             # Protégé loader, validator
│   │   ├── ingest/               # Excel → RDF converter
│   │   ├── graph/                # Neo4j integration
│   │   ├── api/                  # FastAPI endpoints
│   │   ├── core/                 # Flow models
│   │   ├── analytics/            # KPI calculator
│   │   ├── mapping/              # RDF mapper
│   │   └── cli.py                # CLI commands
│   ├── tests/                    # 테스트 (90%+ coverage)
│   ├── configs/                  # 설정 파일
│   ├── docs/                     # 기술 문서
│   ├── docker-compose.yml        # Docker 배포
│   ├── Dockerfile                # Backend image
│   ├── pyproject.toml            # v2.0.0
│   ├── README_FULL_STACK.md      # 전체 가이드
│   └── IMPLEMENTATION_SUMMARY.md # 구현 요약
│
├── ontology/                     # 온톨로지 정의
│   ├── HVDC.MD                   # HVDC v3.0 정의
│   ├── core/                     # 핵심 온톨로지 (15 files)
│   └── extended/                 # 확장 온톨로지 (7 files)
│
├── docs/                         # 프로젝트 문서
│   ├── guides/                   # 가이드 (3 files)
│   │   ├── QUICK_START.md        # 빠른 시작
│   │   ├── API_REFERENCE.md      # API 레퍼런스
│   │   └── TROUBLESHOOTING.md    # 문제 해결
│   ├── architecture/             # 아키텍처 (4 files)
│   ├── ontology/                 # 온톨로지 분석
│   └── README.md                 # 문서 인덱스
│
├── data/                         # 입력 데이터
│   ├── HVDC_입고로직_종합리포트.xlsx
│   └── backups/                  # 백업 파일
│
├── output/                       # 출력 결과
│   ├── rdf/                      # RDF/TTL 파일
│   ├── visualizations/           # HTML 시각화
│   ├── integration/              # JSON 통합 데이터
│   ├── final/                    # 최종 출력
│   └── versions/                 # 버전 관리
│
├── reports/                      # 분석 보고서
├── scripts/                      # 처리 스크립트
│   └── build_unified_network_v12_hvdc.py (최신)
│
├── ABU/                          # Abu Dhabi 데이터
├── JPT71/                        # Jopetwil 71 선박 데이터
├── HVDC Project Lightning/       # Lightning 서브시스템
└── archive/                      # 아카이브
```

---

## 주요 기능

### 1. Protégé 온톨로지
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
- [Master Plan](plan.md) - 전체 프로젝트 계획
- [Work Log](HVDC_WORK_LOG.md) - 상세 작업 로그 (v2.0.0)
- [Quick Start Guide](docs/guides/QUICK_START.md) - 5분 빠른 시작
- [API Reference](docs/guides/API_REFERENCE.md) - API 레퍼런스
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md) - 문제 해결
- [Documentation Index](docs/README.md) - 문서 인덱스

### logiontology 문서
- [README_FULL_STACK.md](logiontology/README_FULL_STACK.md) - 전체 시스템 가이드
- [IMPLEMENTATION_SUMMARY.md](logiontology/IMPLEMENTATION_SUMMARY.md) - 구현 요약
- [logiontology/docs/](logiontology/docs/) - 기술 문서 7개

### 온톨로지 문서
- [HVDC.MD](ontology/HVDC.MD) - HVDC v3.0 정의
- [core/](ontology/core/) - 핵심 온톨로지 (15개 파일)
- [extended/](ontology/extended/) - 확장 온톨로지 (7개 파일)

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
- Protégé 온톨로지
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
**최종 업데이트**: 2025-10-26

---

## 관련 링크

- [Master Plan](plan.md) - 전체 프로젝트 계획
- [Work Log](HVDC_WORK_LOG.md) - 상세 작업 로그
- [Quick Start](docs/guides/QUICK_START.md) - 5분 시작 가이드
- [API Reference](docs/guides/API_REFERENCE.md) - API 문서
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md) - 문제 해결
- [Documentation](docs/README.md) - 문서 인덱스
- [Full Stack Guide](logiontology/README_FULL_STACK.md) - 완전한 가이드

---

**개발**: HVDC Project Team
**프로젝트**: Samsung C&T Logistics & ADNOC·DSV Partnership
**최종 업데이트**: 2025-10-26
