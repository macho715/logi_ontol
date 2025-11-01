# HVDC Full Stack MVP with Protégé Integration

## Stage 0: Protégé Master Ontology Design

### 0.1 HVDC Ontology in Protégé Desktop

- Download & install Protégé (https://protege.stanford.edu)
- Create `hvdc_ontology.owl` with IRI: `https://hvdc-project.com/ontology`
- Define classes: Project, Cargo, Site, Warehouse, FlowCode, BillOfLading
- Define Object Properties: storedAt, destinedTo, hasFlowCode, relatesToBL
- Define Datatype Properties: hasHVDCCode, weight, flowCodeValue, siteName
- Add SHACL constraints for FlowCode (0-4 range), weight (positive)
- Export as `configs/ontology/hvdc_ontology.ttl`

### 0.2 Protégé Loader Module

**파일:** `src/ontology/protege_loader.py`

- Load Protégé .owl/.ttl files into RDFLib Graph
- Extract classes, properties, SHACL constraints
- Auto-generate Pydantic models from ontology classes

### 0.3 Ontology Validator

**파일:** `src/ontology/validator.py`

- SHACL validation against Protégé schema
- Ensure data conforms to master ontology

## Stage 1: Excel → RDF Pipeline

### 1.1 Excel to RDF Converter

**파일:** `src/ingest/excel_to_rdf.py`

- Read Excel (pandas + openpyxl)
- Map to Protégé ontology classes
- Calculate Flow Codes (0-4)
- Normalize sites with `SiteNormalizer`
- Output TTL files

### 1.2 Batch Processor

**파일:** `src/ingest/batch_processor.py`

- Process multiple Excel files
- Progress logging
- SHACL validation per batch

## Stage 2: Neo4j Integration

### 2.1 Neo4j Store

**파일:** `src/graph/neo4j_store.py`

- RDF → Neo4j node/relationship mapping
- Cypher query wrapper
- Connection pooling

### 2.2 Graph Loader

**파일:** `src/graph/loader.py`

- TTL → Neo4j import
- Auto-create indexes
- Incremental updates

### 2.3 Neo4j Config

**파일:** `configs/neo4j_config.yaml`

- Connection: bolt://localhost:7687
- Indexes: flow_code, hvdc_code

## Stage 3: FastAPI Backend

### 3.1 Main API

**파일:** `src/api/main.py`

- `/api/flows` - List all flows
- `/api/flows/{id}` - Flow details
- `/api/search` - HVDC code search
- `/api/kpi` - KPI dashboard
- `/api/insights` - AI insights
- `/api/reports/pdf` - Generate reports

### 3.2 SPARQL & Cypher Endpoints

**파일:** `src/api/endpoints/sparql.py`, `cypher.py`

- Execute queries via REST

### 3.3 KPI API

**파일:** `src/api/endpoints/kpi.py`

- Reuse `FlowKPICalculator`
- Real-time metrics

## Stage 4: AI Insights

### 4.1 Insights Service

**파일:** `src/ai/insights_service.py`

- Claude/Grok API integration
- Risk analysis prompts
- Optimization suggestions

### 4.2 AI Config

**파일:** `configs/ai_config.yaml`

- Provider: claude/grok
- API key management

## Stage 5: PDF Reports

### 5.1 Report Generator

**파일:** `src/reports/pdf_generator.py`

- Jinja2 templates
- WeasyPrint PDF output
- Matplotlib chart embedding

### 5.2 Templates

**파일:** `src/reports/templates/flow_report.html`

- Flow details table
- AI insights section
- KPI charts (base64)

## Stage 6: React Frontend

### 6.1 Setup

- `npx create-react-app frontend --template typescript`
- Install: @tanstack/react-query, axios, recharts

### 6.2 Components

**SearchFlow.tsx** - Flow search UI

**KPIDashboard.tsx** - Real-time KPI charts

**ReportViewer.tsx** - PDF download & insights

## Stage 7: Docker Deployment

### 7.1 Docker Compose

**파일:** `docker-compose.yml`

- Services: neo4j, backend (FastAPI), frontend (React)
- Volumes: neo4j_data
- Environment: NEO4J_URI, AI_API_KEY

### 7.2 Dockerfiles

**Dockerfile** - Python backend (uvicorn)

**frontend/Dockerfile** - Node.js build + serve

## Stage 8: CLI Enhancement

### 8.1 New Commands

**파일:** `src/cli.py`

- `ingest-excel` - Excel → TTL
- `load-neo4j` - TTL → Neo4j
- `generate-report` - Flow → PDF

## Stage 9: Testing

### 9.1 API Tests

**tests/api/test_endpoints.py**

- Test all FastAPI endpoints

### 9.2 Integration Tests

**tests/integration/test_full_pipeline.py**

- Excel → RDF → Neo4j → API pipeline

### 9.3 Frontend Tests

**frontend/src/tests/SearchFlow.test.tsx**

- React Testing Library

## Stage 10: Documentation

### 10.1 User Guide

**docs/USER_GUIDE.md**

- Excel format guide
- API usage examples
- Frontend walkthrough

### 10.2 Architecture

**docs/ARCHITECTURE.md**

- System diagram
- Data flow

## Key Files

**Protégé Ontology:**

- `configs/ontology/hvdc_ontology.owl` (Protégé native)
- `configs/ontology/hvdc_ontology.ttl` (RDF export)

**Core Modules:**

- `src/ontology/protege_loader.py` - Protégé integration
- `src/ingest/excel_to_rdf.py` - Excel ingestion
- `src/graph/neo4j_store.py` - Neo4j driver
- `src/api/main.py` - FastAPI app
- `src/reports/pdf_generator.py` - PDF reports
- `src/ai/insights_service.py` - AI integration

**Frontend:**

- `frontend/src/components/SearchFlow.tsx`
- `frontend/src/components/KPIDashboard.tsx`

**Dependencies:**

```txt
fastapi>=0.104
uvicorn[standard]>=0.24
neo4j>=5.14
pandas>=2.1
openpyxl>=3.1
jinja2>=3.1
weasyprint>=60.0
matplotlib>=3.8
httpx>=0.25
```

## Roadmap

**Week 1:** Protégé ontology + Excel ingestion + Neo4j

**Week 2:** FastAPI + AI insights + PDF reports

**Week 3:** React frontend + Docker

**Week 4:** Testing + Documentation + Deployment

## Validation

- [ ] Protégé ontology validates with SHACL
- [ ] Excel → RDF with schema compliance
- [ ] Neo4j graph loaded
- [ ] API endpoints return correct data
- [ ] React UI searches and displays flows
- [ ] PDF reports generated
- [ ] AI insights working
- [ ] Docker Compose runs full stack
