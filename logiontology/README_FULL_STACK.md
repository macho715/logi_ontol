# HVDC Full Stack MVP v2.0.0

**Complete logistics ontology system**: Protégé Ontology + Excel→RDF→Neo4j→FastAPI→React + AI Insights + PDF Reports

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Neo4j 5.14+ (or Docker)
- Node.js 20+ (for React frontend)
- Java 11+ (for Protégé)

### Installation

```bash
# Clone repository
cd logiontology

# Install Python dependencies
pip install -e ".[dev,api,graph,reports,ai]"

# Start Neo4j (Docker)
docker run -d \
  --name hvdc-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/hvdc_password \
  neo4j:5.14

# Or use Docker Compose for full stack
docker-compose up -d
```

## 📋 Features

### 1. Protégé Ontology (Visual Design)
- **Location**: `configs/ontology/hvdc_ontology.ttl`
- **Classes**: Cargo, Site, Warehouse, Port, FlowCode, BillOfLading
- **Properties**: storedAt, destinedTo, hasFlowCode, weight, hasHVDCCode
- **SHACL Validation**: Flow Code (0-4), Weight (positive)

### 2. Excel → RDF Ingestion
Convert Excel logistics data to RDF format:
```bash
# Single file
logiontology ingest-excel data/shipments.xlsx --out output/shipments.ttl

# Batch processing
logiontology batch-ingest data/ --output-dir output/
```

**Excel Format Expected:**
| HVDC_CODE | WEIGHT | WAREHOUSE | SITE | PORT | FLOW_CODE |
|-----------|--------|-----------|------|------|-----------|
| HVDC-001  | 25.5   | DSV INDOOR| MIR  | ZAYED| 2         |

### 3. Neo4j Graph Database
Load RDF data into Neo4j:
```bash
# Setup database (indexes + constraints)
logiontology setup-neo4j

# Load TTL files
logiontology load-neo4j output/shipments.ttl

# Query with Cypher
# Open Neo4j Browser: http://localhost:7474
# Credentials: neo4j / hvdc_password
```

**Sample Cypher Queries:**
```cypher
# Get all cargo
MATCH (c:Cargo) RETURN c LIMIT 10

# Flow distribution
MATCH (c:Cargo)-[:HASFLOWCODE]->(f:FlowCode)
RETURN f.flowCodeValue AS code, COUNT(c) AS count
ORDER BY code
```

### 4. FastAPI Backend
Start REST API server:
```bash
logiontology serve-api --reload

# Access API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

**API Endpoints:**
- `GET /api/flows` - List all flows
- `GET /api/flows/{id}` - Get flow details
- `GET /api/kpi` - KPI dashboard data
- `POST /api/sparql` - Execute SPARQL query
- `POST /api/cypher` - Execute Cypher query

**Example Request:**
```bash
curl http://localhost:8000/api/kpi
```

### 5. React Frontend (Optional)
```bash
cd frontend
npm install
npm start

# Open http://localhost:3000
```

**Features:**
- Flow search by HVDC code
- KPI dashboard with charts
- Real-time metrics

### 6. Flow Code System v1.0
**Already Implemented** (from previous phase):
- Flow Code 0-4 classification
- Mode-specific attributes (Container/Bulk/Land/LCT)
- KPI calculator
- SHACL validation

**Flow Codes:**
- **0**: Pre-Arrival (Documents only)
- **1**: Direct (Port→Site)
- **2**: WH Once (Port→WH→Site)
- **3**: WH + MOSB (Port→WH→MOSB→Site)
- **4**: WH Double + MOSB

## 🏗️ Architecture

```
┌─────────────┐
│ Protégé OWL │ (Visual Design)
└──────┬──────┘
       │ Export TTL
       ▼
┌─────────────┐
│ Excel Files │
└──────┬──────┘
       │ pandas + rdflib
       ▼
┌─────────────┐
│  RDF Graph  │ (TTL files)
└──────┬──────┘
       │ Neo4j Driver
       ▼
┌─────────────┐
│   Neo4j DB  │◄────┐
└──────┬──────┘     │
       │ Cypher     │
       ▼            │
┌─────────────┐     │
│  FastAPI    │─────┘
│  Backend    │
└──────┬──────┘
       │ REST API
       ▼
┌─────────────┐
│   React UI  │
└─────────────┘
```

## 📊 CLI Commands

```bash
# Ingestion
logiontology ingest-excel FILE.xlsx --out OUTPUT.ttl
logiontology batch-ingest INPUT_DIR/ --output-dir OUTPUT_DIR/

# Neo4j
logiontology setup-neo4j
logiontology load-neo4j FILE.ttl

# API Server
logiontology serve-api --reload --port 8000

# Legacy commands (still available)
logiontology run FILE.xlsx  # Old pipeline
logiontology make-id cargo HVDC-001  # ID generator
```

## 🐳 Docker Deployment

### Full Stack with Docker Compose
```bash
# Start all services
docker-compose up -d

# Services:
# - Neo4j: http://localhost:7474
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
```

### Backend Only
```bash
docker build -t hvdc-backend .
docker run -p 8000:8000 \
  -e NEO4J_URI=bolt://host.docker.internal:7687 \
  -e NEO4J_PASSWORD=hvdc_password \
  hvdc-backend
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/unit/  # Unit tests
pytest tests/validation/  # SHACL validation tests
pytest tests/api/  # API tests (when implemented)

# With coverage
pytest --cov=src --cov-report=html
```

## 📁 Project Structure

```
logiontology/
├── configs/
│   ├── ontology/
│   │   ├── hvdc_ontology.ttl      # Protégé ontology
│   │   └── flow_code.ttl          # Flow code ontology
│   ├── shapes/
│   │   └── FlowCode.shape.ttl     # SHACL validation
│   ├── sparql/
│   │   └── flow_kpi_queries.sparql
│   ├── neo4j_config.yaml          # Neo4j configuration
│   └── ai_config.yaml             # AI insights config
├── src/
│   ├── ontology/                  # NEW: Protégé integration
│   │   ├── protege_loader.py
│   │   └── validator.py
│   ├── ingest/                    # NEW: Excel to RDF
│   │   ├── excel_to_rdf.py
│   │   └── batch_processor.py
│   ├── graph/                     # NEW: Neo4j integration
│   │   ├── neo4j_store.py
│   │   └── loader.py
│   ├── api/                       # NEW: FastAPI backend
│   │   ├── main.py
│   │   └── endpoints/
│   │       ├── kpi.py
│   │       ├── sparql.py
│   │       └── cypher.py
│   ├── core/                      # Existing: Flow models
│   ├── analytics/                 # Existing: KPI calculator
│   ├── mapping/                   # Existing: RDF mapper
│   ├── integration/               # Existing: Site normalizer
│   └── cli.py                     # Enhanced CLI
├── tests/
│   ├── unit/
│   ├── validation/
│   ├── api/                       # NEW: API tests
│   └── integration/               # NEW: Full pipeline tests
├── frontend/                      # NEW: React UI
├── docker-compose.yml             # NEW: Full stack deployment
├── Dockerfile                     # NEW: Backend image
└── pyproject.toml                 # Updated dependencies
```

## 🔧 Configuration

### Neo4j Connection
Set environment variable:
```bash
export NEO4J_PASSWORD=your_password
```

Or edit `configs/neo4j_config.yaml`:
```yaml
neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "${NEO4J_PASSWORD}"
  database: "hvdc"
```

### AI Insights (Optional)
Edit `configs/ai_config.yaml`:
```yaml
ai:
  provider: "claude"
  api_key: "${AI_API_KEY}"
  model: "claude-3-sonnet-20240229"
```

## 📖 Documentation

- **Flow Code Guide**: `docs/FLOW_CODE_GUIDE.md`
- **Implementation Report**: `docs/FLOW_CODE_IMPLEMENTATION_REPORT.md`
- **Protégé Guide**: `../ontology/Protégé 온톨로지 에디터.md`
- **Architecture Report**: `../ontology/HVDC 프로젝트 온톨로지 기반 통합 시스템 아키텍처 설계 보고서.md`
- **API Docs**: http://localhost:8000/docs (when server running)

## 🎯 Performance Targets

- **ETA MAPE**: ≤ 12.00%
- **Flow Verification**: ≥ 99.90%
- **Direct Delivery Rate**: Maximize
- **MOSB Pass Rate**: Monitor

## 🆕 What's New in v2.0.0

### Added
✅ Protégé ontology integration (visual design)
✅ Excel → RDF conversion
✅ Neo4j graph database
✅ FastAPI REST API
✅ SPARQL/Cypher query endpoints
✅ KPI dashboard API
✅ Enhanced CLI commands
✅ Docker Compose deployment
✅ Full stack architecture

### Maintained from v1.0.0
✅ Flow Code 0-4 system
✅ Pydantic models (Container/Bulk/Land/LCT)
✅ KPI calculator
✅ SHACL validation
✅ Site normalizer
✅ RDF mapper

## 🚧 Roadmap

### Phase 2 (Next)
- [ ] AI insights service (Claude/Grok integration)
- [ ] PDF report generation
- [ ] React frontend components
- [ ] Full pipeline integration tests
- [ ] Real-time KPI dashboard

### Phase 3
- [ ] Production deployment
- [ ] Performance optimization
- [ ] Security hardening
- [ ] User authentication

## 📝 License

MIT

## 🤝 Contributing

See main README.md for contribution guidelines.

## 📞 Support

For issues or questions, please refer to the main project documentation.

---

**Version**: 2.0.0
**Last Updated**: 2025-10-26
**Status**: MVP Complete (Backend Core)


