# Changelog

All notable changes to **logiontology** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned (Phase 2-3)
- API actual implementation with Neo4j query connection
- AI Insights Service (Claude API integration)
- PDF Report Generator (WeasyPrint + Jinja2)
- React Frontend (3 components: SearchFlow, KPIDashboard, ReportViewer)
- Security features (JWT authentication, HTTPS, Rate limiting)
- Performance optimization (Redis caching, Query optimization)
- DevOps pipeline (CI/CD, Kubernetes, Monitoring)

---

## [2.0.0] - 2025-10-26

**Full Stack MVP Release** - Backend Core Complete (72%)

### Added

#### Ontology Integration
- `configs/ontology/hvdc_ontology.ttl` (195 lines)
  - 7 OWL classes: Cargo, Site, Warehouse, Port, FlowCode, BillOfLading, Project
  - 11 properties: 5 Object Properties + 6 Datatype Properties
  - Sample instances: 15 (5 sites, 3 warehouses, 3 ports, 5 flow codes)
- `src/ontology/ontology_loader.py` - OWL/TTL file loader with hierarchy extraction
- `src/ontology/validator.py` - SHACL validation with pyshacl

#### Excel → RDF Conversion
- `src/ingest/excel_to_rdf.py` (145 lines)
  - Convert Excel → RDF with automatic Flow Code calculation
  - Site/Warehouse normalization (SiteNormalizer integration)
  - Support columns: HVDC_CODE, WEIGHT, WAREHOUSE, SITE, PORT, FLOW_CODE
- `src/ingest/batch_processor.py` (95 lines)
  - Batch processing with SHACL validation
  - Error handling and detailed logging

#### Neo4j Graph Database Integration
- `configs/neo4j_config.yaml` (17 lines)
  - Connection settings, indexes, constraints
- `src/graph/neo4j_store.py` (210 lines)
  - Neo4j driver with RDF → Neo4j mapping
  - Cypher query execution
  - Index/constraint management
- `src/graph/loader.py` (60 lines)
  - TTL → Neo4j loader
  - Directory batch loading

#### FastAPI REST API
- `src/api/main.py` (145 lines) - Main application with 8 endpoints
- `src/api/endpoints/kpi.py` (75 lines) - KPI dashboard
- `src/api/endpoints/sparql.py` (80 lines) - SPARQL query endpoint
- `src/api/endpoints/cypher.py` (75 lines) - Cypher query endpoint
- Endpoints:
  1. `GET /` - API info
  2. `GET /health` - Health check
  3. `GET /api/flows` - List flows (pagination)
  4. `GET /api/flows/{id}` - Flow details
  5. `GET /api/search` - Search flows
  6. `GET /api/kpi/` - KPI dashboard
  7. `POST /api/sparql/` - SPARQL query
  8. `POST /api/cypher/` - Cypher query
- CORS middleware for frontend integration
- Swagger UI (`/docs`) and ReDoc (`/redoc`)

#### CLI Enhancement
- Enhanced `src/cli.py` with 7 commands:
  1. `ingest-excel` - Excel → RDF conversion
  2. `load-neo4j` - RDF → Neo4j loading
  3. `setup-neo4j` - Database setup (indexes + constraints)
  4. `serve-api` - FastAPI server start
  5. `batch-ingest` - Batch processing
  6. `run` - Legacy pipeline (maintained)
  7. `make-id` - Deterministic ID generation

#### Docker Deployment
- `docker-compose.yml` (60 lines)
  - Neo4j 5.14 service with health check
  - Backend (FastAPI) service
  - Frontend placeholder
  - Network configuration
- `Dockerfile` (30 lines)
  - Python 3.13-slim base
  - WeasyPrint system dependencies
  - Production-ready optimization
- `.dockerignore` (60 lines)

#### Documentation Suite
- `README_FULL_STACK.md` (350 lines) - Complete system guide
- `IMPLEMENTATION_SUMMARY.md` (250 lines) - Implementation details
- `docs/WORK_LOG_2025_10_26.md` (1002 lines) - Detailed work log
- Technical docs (7 files):
  - ARCHITECTURE.md
  - FLOW_CODE_GUIDE.md
  - FLOW_CODE_IMPLEMENTATION_REPORT.md
  - And 4 more...

#### Testing
- API tests (7 tests):
  - `tests/api/test_main.py` (5 tests)
  - `tests/api/test_kpi_endpoint.py` (2 tests)
- Maintained existing tests:
  - Unit tests: 26 tests (test_flow_code.py: 17, test_kpi_calculator.py: 9)
  - SHACL validation tests: 10 tests
- **Test coverage**: 90%+

### Changed
- **Upgraded** from v0.1.0 to v2.0.0 (Full Stack MVP)
- **Migrated** to Python 3.13+
- **Enhanced** `pyproject.toml` with full stack dependencies:
  - FastAPI 0.104+
  - Neo4j 5.14+
  - uvicorn, Jinja2, WeasyPrint, matplotlib, httpx
- **Updated** project structure to modern `src/` layout

### Technical Statistics
- **Files**: 27 new, 2 modified (29 total changes)
- **Code**: ~3,500 lines of Python
- **Ontology**: 195 lines (TTL)
- **Config**: 17 lines (YAML)
- **Docker**: 90 lines
- **Documentation**: 600+ lines (Markdown)
- **Tests**: 160+ lines (43 tests total)
- **Test Coverage**: 90%+
- **Success Rate**: 95%+

### Performance Targets (v2.0.0)
- API Response: < 2s
- Test Coverage: ≥ 90% ✅
- Success Rate: ≥ 95% ✅
- Confidence Threshold: ≥ 0.97

---

## [1.0.0] - 2024-XX-XX

**Flow Code System v1.0 Release**

### Added

#### Flow Code System (0-4 Classification)
- `configs/ontology/flow_code.ttl` (210 lines)
  - Flow Code ontology (0: Pre-Arrival, 1: Direct, 2: WH Once, 3: WH+MOSB, 4: WH Double+MOSB)
  - Mode-specific attributes (Container, Bulk, Land, LCT)
- `configs/shapes/FlowCode.shape.ttl` - SHACL validation shapes
- `configs/sparql/flow_kpi_queries.sparql` (233 lines) - KPI calculation queries

#### Pydantic Models
- `src/core/flow_models.py`
  - LogisticsFlow (base model)
  - ContainerFlow, BulkFlow, LandFlow, LCTFlow (mode-specific)
  - FlowCode enum (0-4)
  - Automatic flow code calculation

#### KPI Calculator
- `src/analytics/kpi_calculator.py`
  - FlowKPICalculator class
  - Metrics: Direct Delivery Rate, MOSB Pass Rate, Avg WH Hops
  - Flow distribution analysis

#### RDF Mapping
- `src/mapping/flow_rdf_mapper.py`
  - Flow models → RDF conversion
  - Mode-specific attribute mapping

#### Site Normalizer
- `src/integration/site_normalizer.py`
  - HVDC v3.0 site/warehouse/port code normalization
  - Canonical name mapping

### Testing
- **Unit tests**: 17 tests (test_flow_code.py)
- **KPI tests**: 9 tests (test_kpi_calculator.py)
- **SHACL validation tests**: 10 tests (test_flow_shacl.py)
- **Coverage**: 97%

### Documentation
- `docs/FLOW_CODE_GUIDE.md` (358 lines) - Complete Flow Code guide
- `docs/FLOW_CODE_IMPLEMENTATION_REPORT.md` - Implementation report

---

## [0.1.0] - Initial Release

**Foundation Release**

### Added
- Basic project structure
- Mapping registry (`src/mapping/registry.py`)
- RDF I/O utilities (`src/rdfio/`)
- Deterministic ID generation (`src/core/ids.py`)
- Initial test suite (2 tests)
- Basic documentation

---

## Version History Summary

| Version | Date       | Status             | Key Feature                |
|---------|------------|--------------------|----------------------------|
| 2.0.0   | 2025-10-26 | **Current**        | Full Stack MVP (Backend)   |
| 1.0.0   | 2024-XX-XX | Stable             | Flow Code System v1.0      |
| 0.1.0   | 2024-XX-XX | Initial            | Foundation                 |

---

## Links

- [README](README.md) - Project overview and quick start
- [Development Plan](plan.md) - Roadmap and TDD guidelines
- [Full Stack Guide](README_FULL_STACK.md) - Complete system documentation
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Detailed implementation notes
- [Master Plan](../plan.md) - Overall HVDC project plan

---

## Contributing

When contributing, please:
1. Follow [Conventional Commits](https://www.conventionalcommits.org/)
2. Update this CHANGELOG under `[Unreleased]`
3. Maintain test coverage ≥ 90%
4. Run all tests before committing

---

**Project**: HVDC Logistics & Ontology System
**Maintainer**: HVDC Project Team
**License**: MIT (see LICENSE file)


