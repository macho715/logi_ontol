# logiontology

**HVDC Logistics Ontology System** - Full Stack MVP for ontology-based logistics data management

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-90%25+-brightgreen.svg)](https://github.com/yourusername/logiontology)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## Overview

logiontology는 HVDC 프로젝트를 위한 **물류 온톨로지 시스템**입니다. 온톨로지 기반 데이터 모델, Excel 데이터 수집, Neo4j 그래프 DB, FastAPI REST API를 통합한 Full Stack MVP입니다.

**현재 상태**: v2.0.0 Backend Core 완료 (72%)

---

## Features

### 1. Ontology Schema
- **OWL/TTL 온톨로지**: 7 classes, 11 properties
- **클래스**: Cargo, Site, Warehouse, Port, FlowCode, BillOfLading, Project
- **Loader**: OWL/TTL 파일 자동 로드 및 hierarchy 추출
- **Validator**: SHACL 기반 데이터 검증

### 2. Excel → RDF Conversion
- **지원 컬럼**: HVDC_CODE, WEIGHT, WAREHOUSE, SITE, PORT, FLOW_CODE
- **자동 처리**: Site/Warehouse 정규화, Flow Code 계산
- **배치 처리**: 디렉토리 단위 변환 및 SHACL 검증

### 3. Neo4j Graph Database
- **RDF → Neo4j 매핑**: 자동 변환 (Node + Relationship)
- **인덱스**: flow_code, hvdc_code, site_name, warehouse_name, port_name
- **쿼리**: Cypher 및 SPARQL 지원

### 4. FastAPI REST API
**8개 엔드포인트**:
- `GET /` - API 정보
- `GET /health` - 헬스 체크
- `GET /api/flows` - 플로우 목록 (pagination)
- `GET /api/flows/{id}` - 플로우 상세
- `GET /api/search` - 플로우 검색
- `GET /api/kpi/` - KPI 대시보드
- `POST /api/sparql/` - SPARQL 쿼리
- `POST /api/cypher/` - Cypher 쿼리

**API Docs**: http://localhost:8000/docs (Swagger UI)

### 5. Flow Code System v3.5
**통합 물류 플로우 분류** (0-5):
- **0**: Pre-Arrival (Documents only)
- **1**: Direct Delivery (Port → Site)
- **2**: WH (Port → WH → Site)
- **3**: MOSB (Port → WH → MOSB → Site)
- **4**: Full (Port → WH → WH → MOSB → Site)
- **5**: Mixed/Incomplete

**Features**:
- Pydantic models (Container/Bulk/Land/LCT)
- KPI Calculator (Direct Rate, MOSB Pass, Avg WH Hops)
- SHACL validation (3 core rules)
- Site normalizer (HVDC v3.0 codes)

### 6. CLI Commands
**7개 명령어**:
```bash
logiontology ingest-excel FILE.xlsx    # Excel → RDF
logiontology load-neo4j FILE.ttl       # RDF → Neo4j
logiontology setup-neo4j               # DB setup
logiontology serve-api --reload        # API server
logiontology batch-ingest DIR/         # Batch processing
logiontology run                       # Legacy pipeline
logiontology make-id                   # ID generation
```

### 7. Docker Deployment
**3개 서비스**:
- **Neo4j**: Neo4j 5.14 (ports: 7474, 7687)
- **Backend**: FastAPI (port: 8000)
- **Frontend**: React (port: 3000, placeholder)

```bash
docker-compose up -d
```

### 8. Testing & Quality
- **Test Coverage**: 90%+
- **Tests**: 16 total (13 unit + 3 API)
- **Linting**: ruff + black
- **Type Checking**: mypy

---

## Quick Start

### Prerequisites
- Python 3.13+
- Docker 20+
- Git

### Installation

```bash
# Clone repository
cd c:\logi_ontol\logiontology

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -e ".[dev,api,graph]"
```

### 5-Minute Start

```bash
# 1. Start Neo4j
docker run -d --name hvdc-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/hvdc_password \
  neo4j:5.14

# 2. Convert Excel → RDF (prepare sample.xlsx)
logiontology ingest-excel data/sample.xlsx

# 3. Load to Neo4j
export NEO4J_PASSWORD=hvdc_password  # Windows: set NEO4J_PASSWORD=hvdc_password
logiontology setup-neo4j
logiontology load-neo4j output/sample.ttl

# 4. Start API server
logiontology serve-api --reload
```

**Access**:
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474 (neo4j / hvdc_password)

### Docker Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## Project Structure

```
logiontology/
├── src/                      # Source code
│   ├── ontology/             # Ontology loader, validator
│   ├── ingest/               # Excel → RDF converter
│   ├── graph/                # Neo4j integration
│   ├── api/                  # FastAPI endpoints
│   ├── core/                 # Flow models, IDs
│   ├── analytics/            # KPI calculator
│   ├── mapping/              # RDF mapper
│   ├── integration/          # Site normalizer
│   ├── export/               # TTL to JSON
│   ├── rdfio/                # RDF I/O
│   ├── reasoning/            # Ontology reasoning
│   ├── pipeline/             # Main pipeline
│   ├── report/               # Report queries
│   ├── validation/           # Schema validator
│   └── cli.py                # CLI commands
├── tests/                    # Tests (90%+ coverage)
│   ├── unit/                 # Unit tests
│   ├── validation/           # SHACL tests
│   ├── api/                  # API tests
│   └── integration/          # Integration tests
├── configs/                  # Configuration files
│   ├── ontology/             # hvdc_ontology.ttl
│   ├── shapes/               # SHACL shapes
│   ├── sparql/               # SPARQL queries
│   └── neo4j_config.yaml     # Neo4j config
├── docs/                     # Documentation (9 files)
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Backend image
├── pyproject.toml            # v2.0.0
├── README.md                 # This file
├── plan.md                   # Development plan
├── CHANGELOG.md              # Version history
├── README_FULL_STACK.md      # Complete guide
└── IMPLEMENTATION_SUMMARY.md # Implementation details
```

---

## Usage Examples

### Python API

```python
from src.core.flow_models import ContainerFlow, FlowCode
from src.analytics.kpi_calculator import FlowKPICalculator

# Create flow
flow = ContainerFlow(
    flow_id="CT001",
    flow_code=FlowCode.DIRECT,
    wh_handling=0,
    offshore_flag=False,
    gate_appt_win_min=120
)

# Calculate KPIs
calc = FlowKPICalculator()
kpis = calc.calculate([flow])
print(f"Direct Delivery Rate: {kpis.direct_delivery_rate:.2f}%")
```

### CLI

```bash
# Convert Excel
logiontology ingest-excel data/shipments.xlsx --out output/flows.ttl

# Load to Neo4j
logiontology load-neo4j output/flows.ttl --uri bolt://localhost:7687

# Start API
logiontology serve-api --host 0.0.0.0 --port 8000 --reload

# Batch processing
logiontology batch-ingest data/ --output-dir output/ --pattern "*.xlsx"
```

### API

```bash
# Health check
curl http://localhost:8000/health

# Get KPIs
curl http://localhost:8000/api/kpi/

# SPARQL query
curl -X POST http://localhost:8000/api/sparql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT ?cargo ?code WHERE { ?cargo hvdc:hasHVDCCode ?code } LIMIT 10"}'

# Cypher query
curl -X POST http://localhost:8000/api/cypher/ \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (c:Cargo) RETURN c.hvdc_code LIMIT 10"}'
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest --cov=src --cov-report=term-missing

# Specific tests
pytest tests/api/ -v
pytest tests/unit/test_flow_code.py -v

# Linting
ruff check src/ tests/
black src/ tests/

# Type checking
mypy src/
```

---

## Documentation

### Core Docs
- [Development Plan](plan.md) - Roadmap & TDD guidelines
- [Changelog](CHANGELOG.md) - Version history
- [Full Stack Guide](README_FULL_STACK.md) - Complete system documentation
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Implementation details

### Technical Docs (docs/)
- `ARCHITECTURE.md` - System architecture
- `FLOW_CODE_GUIDE.md` - Flow Code system guide
- `FLOW_CODE_IMPLEMENTATION_REPORT.md` - Implementation report
- `WORK_LOG_2025_10_26.md` - Detailed work log (v2.0.0)

### External Links
- [Master Plan](../plan.md) - Overall HVDC project plan
- [Quick Start Guide](../docs/guides/QUICK_START.md) - 5-minute guide
- [API Reference](../docs/guides/API_REFERENCE.md) - API documentation
- [Troubleshooting](../docs/guides/TROUBLESHOOTING.md) - Common issues

---

## Performance Targets

### Current (v2.0.0)
- API Response: < 2s
- Test Coverage: 90%+ ✅
- Success Rate: 95%+ ✅

### Target (v3.0.0)
- API Response: < 500ms
- Test Coverage: 95%+
- Success Rate: 98%+
- Uptime: 99.9%

---

## Roadmap

### Phase 1: Backend Core (✅ Complete - 72%)
- Ontology schema
- Excel → RDF conversion
- Neo4j integration
- FastAPI REST API
- Docker deployment
- Documentation

### Phase 2A: Core Features (🔄 Planned - 10-12h)
- Real data testing
- API actual implementation (Neo4j connection)
- Integration tests

### Phase 2B: Extended Features (⏳ Waiting - 15-20h)
- AI Insights Service (Claude API)
- PDF Report Generator (WeasyPrint)
- React Frontend (3 components)

### Phase 3: Production (⏳ Waiting - 10-15h)
- Security (JWT, HTTPS, Rate limiting)
- Performance (Redis caching, Query optimization)
- DevOps (CI/CD, Kubernetes, Monitoring)

**Estimated completion**: 6 weeks (Full Stack MVP)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please follow:
- [Conventional Commits](https://www.conventionalcommits.org/)
- Test coverage ≥ 90%
- [TDD approach](plan.md#tdd-principles-kent-beck)

---

## License

MIT License - See [LICENSE](../LICENSE) file for details.

---

## Project Info

- **Version**: 2.0.0
- **Status**: Backend Core Complete (72%)
- **Project**: HVDC Logistics & Ontology System
- **Organization**: Samsung C&T Logistics (ADNOC·DSV Partnership)
- **Last Updated**: 2025-11-01

---

## Support

- [Issues](https://github.com/macho715/logi_ontol/issues) - Bug reports & feature requests
- [Discussions](https://github.com/macho715/logi_ontol/discussions) - Q&A & ideas
- Documentation: See [docs/](docs/) folder

---

**Built with** ❤️ **for HVDC Project**
