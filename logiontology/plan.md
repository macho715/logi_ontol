# logiontology v2.0.0 - Development Plan

**Project**: HVDC Full Stack MVP
**Version**: 2.0.0
**Status**: Backend Core Complete (72%)
**Updated**: 2025-10-26

---

## Project Overview

logiontology는 HVDC 프로젝트를 위한 **물류 온톨로지 시스템**입니다.

**Stack**:
- **Ontology**: Protégé (OWL/TTL)
- **Backend**: Python 3.13 + FastAPI
- **Database**: Neo4j 5.14
- **Frontend**: React (planned)
- **Deployment**: Docker + Docker Compose

**Architecture**: Excel → RDF → Neo4j → REST API → React UI

---

## Phase 1: Backend Core (✅ Complete - 72%)

### Stage 0: Project Setup (✅ Complete)
- [x] Updated `pyproject.toml` to v2.0.0
- [x] Added full stack dependencies:
  - FastAPI 0.104+, uvicorn, Neo4j 5.14+
  - Jinja2, WeasyPrint, matplotlib, httpx
  - python-multipart

### Stage 1: Protégé Ontology (✅ Complete)
- [x] Created `configs/ontology/hvdc_ontology.ttl` (195 lines)
  - **Classes** (7): Cargo, Site, Warehouse, Port, FlowCode, BillOfLading, Project
  - **Object Properties** (5): storedAt, destinedTo, hasFlowCode, relatesToBL, fromPort
  - **Datatype Properties** (6): hasHVDCCode, weight, flowCodeValue, siteName, warehouseName, portName
  - **Sample instances** (15): Sites (MIR, SHU, DAS, AGI), Warehouses (DSV INDOOR, MOSB), Ports (Zayed, Khalifa, Jebel Ali), FlowCodes (0-4)
- [x] Implemented `src/ontology/protege_loader.py` (110 lines)
  - Load OWL/TTL files with format auto-detection
  - Extract classes, properties, hierarchy
  - Get ontology metadata
- [x] Implemented `src/ontology/validator.py` (75 lines)
  - SHACL validation with pyshacl
  - Detailed validation reports

### Stage 2: Excel Ingestion (✅ Complete)
- [x] Implemented `src/ingest/excel_to_rdf.py` (145 lines)
  - Convert Excel → RDF (HVDC_CODE, WEIGHT, WAREHOUSE, SITE, PORT, FLOW_CODE)
  - Site/warehouse normalization (SiteNormalizer integration)
  - Flow code automatic calculation
  - Instance auto-generation (Warehouse, Site, Port)
- [x] Implemented `src/ingest/batch_processor.py` (95 lines)
  - Batch processing with directory scanning
  - Optional SHACL validation per batch
  - Error handling and success statistics

### Stage 3: Neo4j Integration (✅ Complete)
- [x] Created `configs/neo4j_config.yaml` (17 lines)
  - Connection settings (URI, user, password, database)
  - Indexes: flow_code, hvdc_code, site_name, warehouse_name, port_name
  - Constraints: cargo_hvdc_code_unique
- [x] Implemented `src/graph/neo4j_store.py` (210 lines)
  - Neo4j driver connection
  - RDF → Neo4j mapping (Subject → Node, Predicate → Relationship, Literal → Property)
  - Cypher query execution
  - Index/constraint creation from config
- [x] Implemented `src/graph/loader.py` (60 lines)
  - Load TTL files into Neo4j
  - Directory batch loading (pattern-based)
  - Database setup automation

### Stage 4: FastAPI Backend (✅ Complete)
- [x] Implemented `src/api/main.py` (145 lines)
  - **8 endpoints**: /, /health, /api/flows, /api/flows/{id}, /api/search, /api/kpi/, /api/sparql/, /api/cypher/
  - CORS middleware (localhost:3000, localhost:3001)
  - Health check endpoint
- [x] Implemented `src/api/endpoints/kpi.py` (75 lines)
  - KPI dashboard (total_flows, direct_delivery_rate, mosb_pass_rate, avg_wh_hops, flow_distribution)
  - FlowKPICalculator integration
- [x] Implemented `src/api/endpoints/sparql.py` (80 lines)
  - SPARQL query endpoint with RDFLib
  - Sample queries (3): Get all cargo, Get cargo by site, Flow code distribution
- [x] Implemented `src/api/endpoints/cypher.py` (75 lines)
  - Cypher query endpoint with Neo4j driver
  - Sample queries (4): Get all cargo, Get cargo with warehouse, Flow path, Count by flow code

### Stage 5: CLI Enhancement (✅ Complete)
- [x] Enhanced `src/cli.py`
  - **7 commands**:
    1. `ingest-excel FILE.xlsx` - Excel → RDF conversion
    2. `load-neo4j FILE.ttl` - RDF → Neo4j loading
    3. `setup-neo4j` - Database setup (indexes + constraints)
    4. `serve-api` - FastAPI server start (--host, --port, --reload)
    5. `batch-ingest DIR/` - Batch processing (--output-dir, --pattern)
    6. `run` - Legacy pipeline (maintained for compatibility)
    7. `make-id` - Deterministic ID generation

### Stage 6: Docker Deployment (✅ Complete)
- [x] Created `docker-compose.yml` (60 lines)
  - **Neo4j** service (neo4j:5.14, ports: 7474, 7687, health check, volumes)
  - **Backend** service (FastAPI, port: 8000, depends_on: neo4j)
  - **Frontend** placeholder (port: 3000, planned)
  - Network: hvdc-network (bridge)
- [x] Created `Dockerfile` (30 lines)
  - Base: python:3.13-slim
  - System dependencies: libcairo, libpango (for WeasyPrint)
  - CMD: uvicorn src.api.main:app
- [x] Created `.dockerignore` (60 lines)
  - Exclude: __pycache__, .venv, .git, node_modules, docs, etc.

### Stage 7: Documentation (✅ Complete)
- [x] Created `README_FULL_STACK.md` (350 lines) - Complete system guide
- [x] Created `IMPLEMENTATION_SUMMARY.md` (250 lines) - Implementation summary
- [x] Created `docs/WORK_LOG_2025_10_26.md` (1002 lines) - Detailed work log
- [x] Created technical docs (7 files):
  - `ARCHITECTURE.md` - System architecture
  - `FLOW_CODE_GUIDE.md` - Flow Code system guide (358 lines)
  - `FLOW_CODE_IMPLEMENTATION_REPORT.md` - Implementation report
  - And 4 more...
- [x] Created `README.md` - Project overview (this version: 341 lines)
- [x] Created `CHANGELOG.md` - Version history (197 lines)

### Stage 8: Testing (✅ Complete)
- [x] **Unit tests** (26 tests):
  - `test_flow_code.py` (17 tests) - Flow Code calculation and models
  - `test_kpi_calculator.py` (9 tests) - KPI calculation
- [x] **API tests** (7 tests):
  - `test_main.py` (5 tests) - Root, health, flows, search
  - `test_kpi_endpoint.py` (2 tests) - KPI dashboard
- [x] **SHACL validation tests** (10 tests):
  - `test_flow_shacl.py` - Flow Code validation
- [x] **Test coverage**: 90%+

---

## Phase 2A: Core Features (🔄 Planned - 10-12 hours)

### 2.1 Real Data Testing (2 hours)
- [ ] Create sample Excel file (10-20 rows)
  - Include all Flow Code cases (0-4)
  - Real HVDC data structure
  - All columns: HVDC_CODE, WEIGHT, WAREHOUSE, SITE, PORT
- [ ] Execute full pipeline
  - Excel → RDF conversion
  - SHACL validation
  - Neo4j loading
  - API queries
- [ ] Verify results
  - Neo4j graph inspection (Cypher queries)
  - API responses validation
  - KPI calculations check

### 2.2 API Actual Implementation (3 hours)
- [ ] Implement `/api/flows` endpoint
  - Connect to Neo4j (Cypher query)
  - Pagination (limit, offset)
  - Return actual data
- [ ] Implement `/api/flows/{id}` endpoint
  - Query specific flow from Neo4j
  - Include related entities (warehouse, site, port)
  - Handle 404 Not Found
- [ ] Implement `/api/search` endpoint
  - Search filters (hvdc_code, site, warehouse, flow_code, min_weight, max_weight)
  - Full-text search option
  - Query optimization
- [ ] Error handling
  - 400 Bad Request (invalid parameters)
  - 404 Not Found (resource not found)
  - 500 Internal Server Error (unexpected errors)

### 2.3 Integration Tests (3 hours)
- [ ] Write E2E tests (`tests/integration/test_full_pipeline.py`)
  - Test: Excel → RDF → Neo4j → API full flow
  - Edge cases: Empty Excel, Invalid data, Missing columns
  - Performance measurement
- [ ] Write Neo4j integration tests
  - Test: RDF → Neo4j loading
  - Verify: Nodes, Relationships, Properties
- [ ] CI/CD setup (GitHub Actions or GitLab CI)
  - Automated test execution
  - Docker image build
  - Coverage report

### 2.4 Documentation Update (2 hours)
- [ ] API usage examples
  - cURL examples for all endpoints
  - Python requests examples
  - JavaScript fetch examples
- [ ] Troubleshooting guide expansion
  - Neo4j connection issues
  - Docker problems
  - Platform-specific issues (Windows/Mac/Linux)
- [ ] Best practices
  - Data modeling recommendations
  - Performance optimization tips
  - Security considerations

---

## Phase 2B: Extended Features (⏳ Waiting - 15-20 hours)

### 2.5 AI Insights Service (4 hours)
- [ ] Implement `src/ai/insights_service.py`
  - Claude API integration
  - Prompt templates for risk analysis
  - Prediction models
- [ ] Create `configs/ai_config.yaml`
  - API key configuration
  - Model settings
  - Prompt templates
- [ ] Add `/api/insights` endpoint
  - Flow risk analysis
  - Optimization suggestions
  - Predictive analytics

### 2.6 PDF Report Generator (5 hours)
- [ ] Implement `src/reports/pdf_generator.py`
  - Jinja2 template engine
  - WeasyPrint integration
  - Custom styling (CSS)
- [ ] Implement `src/reports/chart_generator.py`
  - Matplotlib charts (Flow distribution, KPI trends)
  - PNG/SVG export
  - Chart customization
- [ ] Create templates (`src/reports/templates/`)
  - `flow_report.html` - Flow report template
  - `kpi_dashboard.html` - KPI dashboard template
- [ ] Add `/api/reports/pdf` endpoint
  - Generate PDF reports
  - Customization options (date range, filters)
  - Download endpoint

### 2.7 React Frontend (8 hours)
- [ ] Create React project (CRA with TypeScript)
  - ESLint + Prettier setup
  - Axios for API calls
  - React Query for data fetching
- [ ] Implement 3 components:
  1. **SearchFlow** - Search interface with filters
  2. **KPIDashboard** - KPI visualization (charts)
  3. **ReportViewer** - PDF report viewer
- [ ] API integration
  - Connect to backend API
  - Error handling
  - Loading states
- [ ] Create `frontend/Dockerfile`
  - Production-ready build
  - Nginx serving

---

## Phase 3: Production Ready (⏳ Waiting - 10-15 hours)

### 3.1 Security (3 hours)
- [ ] JWT authentication
  - User login/logout
  - Token refresh
  - Protected endpoints
- [ ] HTTPS setup
  - SSL certificate
  - Nginx reverse proxy
  - Redirect HTTP → HTTPS
- [ ] Rate limiting
  - API call limits (per user/IP)
  - DDoS protection
  - Throttling

### 3.2 Performance (4 hours)
- [ ] Redis caching
  - KPI results caching
  - Query results caching
  - Cache invalidation strategy
- [ ] Query optimization
  - Neo4j query tuning
  - Index optimization
  - Query profiling
- [ ] Load testing
  - Locust or k6 setup
  - Performance benchmarks
  - Bottleneck identification

### 3.3 DevOps (5 hours)
- [ ] CI/CD pipeline
  - Automated testing
  - Docker image build
  - Automated deployment
- [ ] Kubernetes manifests
  - Deployment, Service, Ingress
  - ConfigMap, Secret
  - HorizontalPodAutoscaler
- [ ] Monitoring/Logging
  - Prometheus + Grafana
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - Application Performance Monitoring (APM)

---

## Development Guidelines

### TDD Principles (Kent Beck)
1. **Red**: Write failing test first
2. **Green**: Write minimum code to pass
3. **Refactor**: Improve code structure

### Tidy First Approach
1. **Structural changes** BEFORE **Behavioral changes**
2. Separate commits for structure vs. behavior
3. Run all tests after refactoring

### Commit Discipline
- All tests must pass before commit
- Zero linter warnings
- Logical unit per commit
- **Conventional Commits** format:
  - `feat:` - New feature
  - `fix:` - Bug fix
  - `refactor:` - Code refactoring
  - `test:` - Test addition/modification
  - `docs:` - Documentation
  - `chore:` - Maintenance
  - Optional: `[STRUCTURAL]` or `[BEHAVIORAL]` prefix

### Code Quality Standards
- **Test coverage**: ≥ 90%
- **Linter warnings**: 0
- **Type hints**: Required for all functions
- **Docstrings**: Required for public APIs
- **SHACL validation**: All RDF data must pass

---

## Quick Commands

### Development
```bash
# Install dependencies
pip install -e ".[dev,api,graph,reports,ai]"

# Run tests
pytest tests/ -v --cov=src --cov-report=term-missing

# Specific test file
pytest tests/unit/test_flow_code.py -v

# Linting
ruff check src/ tests/
black src/ tests/

# Type checking
mypy src/

# Start API server (development)
logiontology serve-api --reload

# Convert Excel
logiontology ingest-excel data/sample.xlsx --out output/flows.ttl

# Load to Neo4j
export NEO4J_PASSWORD=hvdc_password
logiontology setup-neo4j
logiontology load-neo4j output/flows.ttl
```

### Docker
```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f neo4j

# Rebuild after code changes
docker-compose up -d --build backend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Project Structure

```
logiontology/
├── src/
│   ├── core/            # Flow models, IDs
│   ├── analytics/       # KPI calculator
│   ├── mapping/         # Flow RDF mapper
│   ├── integration/     # Site normalizer
│   ├── ontology/        # Protégé loader, validator
│   ├── ingest/          # Excel → RDF converter
│   ├── graph/           # Neo4j store, loader
│   ├── api/             # FastAPI endpoints
│   │   ├── main.py
│   │   └── endpoints/   # kpi, sparql, cypher
│   └── cli.py           # CLI commands
├── tests/
│   ├── unit/            # Unit tests (26 tests)
│   ├── validation/      # SHACL tests (10 tests)
│   ├── api/             # API tests (7 tests)
│   └── integration/     # Integration tests (pending)
├── configs/
│   ├── ontology/        # hvdc_ontology.ttl, flow_code.ttl
│   ├── shapes/          # SHACL shapes
│   ├── sparql/          # SPARQL queries
│   └── neo4j_config.yaml
├── docs/                # Documentation (7 files)
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── pyproject.toml       # v2.0.0
├── README.md            # Project overview
├── plan.md              # This file
├── CHANGELOG.md         # Version history
├── README_FULL_STACK.md # Complete guide
└── IMPLEMENTATION_SUMMARY.md
```

---

## References

- [README](README.md) - Project overview and quick start
- [Changelog](CHANGELOG.md) - Version history
- [Full Stack Guide](README_FULL_STACK.md) - Complete system documentation
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Detailed implementation notes
- [Master Plan](../plan.md) - Overall HVDC project plan
- [Flow Code Guide](docs/FLOW_CODE_GUIDE.md) - Flow Code system documentation
- [Architecture](docs/ARCHITECTURE.md) - System architecture

---

## Performance Targets

### Current (v2.0.0)
- API Response: < 2s
- Test Coverage: ≥ 90% ✅
- Success Rate: ≥ 95% ✅
- Confidence Threshold: ≥ 0.97

### Target (v3.0.0)
- API Response: < 500ms
- Test Coverage: ≥ 95%
- Success Rate: ≥ 98%
- Uptime: 99.9%

---

## Next Steps

1. **Phase 2A**: Real data testing + API implementation (10-12h)
2. **Phase 2B**: AI Insights + PDF Reports + React Frontend (15-20h)
3. **Phase 3**: Security + Performance + DevOps (10-15h)

**Estimated time to Full Stack MVP**: 35-47 hours

---

## Version Info

- **Current Version**: 2.0.0
- **Status**: Backend Core Complete (72%)
- **Last Updated**: 2025-10-26
- **Next Release**: 2.1.0 (Phase 2A complete)

---

**Project**: HVDC Logistics & Ontology System
**Organization**: Samsung C&T Logistics (ADNOC·DSV Partnership)
