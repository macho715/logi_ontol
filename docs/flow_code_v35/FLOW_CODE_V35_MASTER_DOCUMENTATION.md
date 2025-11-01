# Flow Code v3.5 Master Documentation

**Version**: v3.5
**Last Updated**: 2025-01-25
**Status**: Production Ready
**Project**: HVDC Logistics Ontology

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Complete Implementation Guide](#complete-implementation-guide)
4. [Ontology Integration Details](#ontology-integration-details)
5. [Algorithm Reference](#algorithm-reference)
6. [Usage Guide](#usage-guide)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)
9. [References & Related Documents](#references--related-documents)
10. [Appendices](#appendices)

---

## Executive Summary

### Project Overview

Flow Code v3.5 is a comprehensive logistics flow classification system for the HVDC project that categorizes material movement patterns into 6 distinct categories (0-5). It represents a significant upgrade from v3.4, introducing domain rules for offshore sites (AGI/DAS), mixed/incomplete case handling, and comprehensive tracking capabilities.

### Key Achievements

- **756 Excel records** converted to semantic RDF/TTL format
- **818 events** generated (573 inbound, 245 outbound)
- **31 AGI/DAS cases** automatically upgraded to Flow 3 (MOSB leg required)
- **19/19 tests** passing (100% coverage)
- **Zero domain rule violations** verified via SPARQL

### Quick Start

```bash
# Install dependencies
pip install pandas numpy rdflib

# Run conversion
python -m logiontology.src.ingest.excel_to_ttl_with_events \
    --input "HVDC STATUS(20250815) (1).xlsx" \
    --output "output/hvdc_status_v35.ttl" \
    --flow-version 3.5

# Run tests
pytest tests/test_flow_code_v35*.py -v

# Validate with SPARQL
python scripts/validate_events_with_sparql.py output/hvdc_status_v35.ttl
```

---

## System Architecture

### Data Flow Diagram

```
Excel File (755 rows, 80 cols)
    ↓
Column Normalization
    ↓
Flow Code v3.5 Calculation
    ├─ Pre Arrival Detection (ATA-based)
    ├─ Final Location Extraction (Site columns)
    ├─ Warehouse/MOSB/Site Observation
    ├─ Basic Flow Code (0-4)
    ├─ AGI/DAS Domain Override (0/1/2 → 3)
    └─ Mixed Case Detection (→ 5)
    ↓
Event Injection
    ├─ Inbound Events (Warehouse entries)
    └─ Outbound Events (Site arrivals)
    ↓
TTL Generation
    ├─ Case Instances
    ├─ StockEvents
    └─ Flow Code Properties
    ↓
RDF Graph (9,845 lines)
```

### Component Relationships

```
flow_code_calculator.py
    ├─ Core Algorithm
    │   ├─ normalize_column_names()
    │   ├─ extract_final_location()
    │   ├─ is_pre_arrival()
    │   └─ calculate_flow_code_v35()
    │
excel_to_ttl_with_events.py
    ├─ Conversion Pipeline
    │   ├─ Excel Loading
    │   ├─ Flow Code Calculation (v3.5)
    │   ├─ Event Injection
    │   └─ TTL Serialization
    │
hvdc_event_schema.ttl
    ├─ Ontology Definition
    │   ├─ Classes (Case, StockEvent, etc.)
    │   ├─ Properties (hasFlowCode, hasFlowCodeOriginal, etc.)
    │   └─ SHACL Constraints
```

### Module Dependencies

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `flow_code_calculator.py` | Flow Code calculation engine | pandas, numpy |
| `excel_to_ttl_with_events.py` | Conversion pipeline | flow_code_calculator, rdflib |
| `hvdc_event_schema.ttl` | Ontology schema | OWL, SHACL |
| `test_flow_code_v35.py` | Unit tests | pytest, pandas |
| `test_flow_code_v35_validation.py` | Integration tests | pytest, rdflib |

---

## Complete Implementation Guide

### File Structure

```
logiontology/
├── src/
│   └── ingest/
│       ├── flow_code_calculator.py       # Flow Code v3.5 algorithm
│       └── excel_to_ttl_with_events.py   # Conversion pipeline
│
├── configs/
│   └── ontology/
│       └── hvdc_event_schema.ttl         # Ontology schema (updated)
│
tests/
├── test_flow_code_v35.py                 # Unit tests (12 tests)
└── test_flow_code_v35_validation.py      # Integration tests (7 tests)

core/
└── 1_CORE-08-flow-code.md                # Core ontology docs

core_consolidated/
└── CONSOLIDATED-02-warehouse-flow.md     # Consolidated docs

output/
└── hvdc_status_v35.ttl                   # Generated RDF/TTL
```

### Configuration

**Warehouse Columns** (15 locations):
```python
WAREHOUSE_KEYS = [
    "DSV Indoor", "DSV Outdoor", "DSV MZD", "DSV Al Markaz", "DSV MZP",
    "JDN MZD", "JDN Waterfront",
    "MOSB",  # Offshore base (special handling)
    "AAA Storage", "Hauler Indoor", "Hauler DG Storage",
    "DHL WH", "ZENER (WH)", "Vijay Tanks"
]
```

**Site Columns** (4 locations):
```python
SITE_KEYS = ["SHU", "MIR", "DAS", "AGI"]
```

**Note**: AGI and DAS are offshore sites requiring MOSB transit (domain rule).

---

## Ontology Integration Details

### Updated Core Ontology Files

#### `core/1_CORE-08-flow-code.md` (unified-3.5)

**Changes**:
- Version: unified-3.4 → unified-3.5
- Date: 2025-10-26 → 2025-10-31
- Tags: +agi-das, +offshore
- Flow Code range: 0-4 → 0-5

**New Sections**:
- v3.5 Algorithm Upgrade
- AGI/DAS Domain Rules
- Flow 5 Mixed Cases
- New Properties: hasFlowCodeOriginal, hasFlowOverrideReason, hasFinalLocation

#### `core_consolidated/CONSOLIDATED-02-warehouse-flow.md` (v3.5)

**Changes**:
- Version: consolidated-1.0 → consolidated-1.0-v3.5
- Flow Code range: 0-4 → 0-5
- Rule-7: Updated range constraint
- Rule-8A: AGI/DAS domain rule added
- Rule-8B: Flow 5 conditions added
- SHACL: maxInclusive updated to 5

### New Ontology Properties

**Added to `hvdc_event_schema.ttl`**:

```turtle
# Flow Code Tracking Properties
hvdc:hasFlowCodeOriginal a owl:DatatypeProperty ;
    rdfs:domain hvdc:Case ;
    rdfs:range xsd:integer ;
    rdfs:comment "도메인 룰 적용 전 원본 Flow Code (v3.5 추적용)"@ko .

hvdc:hasFlowOverrideReason a owl:DatatypeProperty ;
    rdfs:domain hvdc:Case ;
    rdfs:range xsd:string ;
    rdfs:comment "Flow Code 오버라이드 사유 (예: AGI/DAS requires MOSB leg)"@ko .

hvdc:hasFlowDescription a owl:DatatypeProperty ;
    rdfs:domain hvdc:Case ;
    rdfs:range xsd:string ;
    rdfs:comment "Flow Code 패턴 설명 (예: Flow 3: Port → MOSB → Site)"@ko .

hvdc:hasFinalLocation a owl:DatatypeProperty ;
    rdfs:domain hvdc:Case ;
    rdfs:range xsd:string ;
    rdfs:comment "최종 위치 (자동 추출된 값)"@ko .

# Updated Range Constraint
hvdc:hasFlowCode a owl:DatatypeProperty ;
    rdfs:range xsd:string ;
    rdfs:comment "물류 흐름 코드 (0=Pre Arrival, 1=직송, 2=창고경유, 3=MOSB경유, 4=창고+MOSB, 5=혼합/미완료)"@ko .
```

### SHACL Constraints

**Flow Code Range Validation**:
```turtle
hvdc:FlowCodeRangeShape a sh:NodeShape ;
    sh:targetClass hvdc:LogisticsFlow ;
    sh:property [
        sh:path hvdc:hasFlowCode ;
        sh:minInclusive 0 ;
        sh:maxInclusive 5 ;
        sh:message "Flow Code는 0~5 범위 내에 있어야 함"
    ] .
```

**AGI/DAS Domain Rule Validation**:
```turtle
hvdc:AGIDASFlowRuleShape a sh:NodeShape ;
    sh:targetClass hvdc:Case ;
    sh:sparql [
        sh:message "AGI/DAS 케이스는 Flow Code 3 이상이어야 함" ;
        sh:select """
            PREFIX hvdc: <http://samsung.com/project-logistics#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT $this
            WHERE {
                $this hvdc:hasFinalLocation ?loc .
                FILTER(?loc IN ("AGI", "DAS"))
                $this hvdc:hasFlowCode ?flow .
                FILTER(xsd:integer(?flow) < 3)
            }
        """
    ] .
```

---

## Algorithm Reference

### Flow Code Definitions (0-5)

| Code | Description | Pattern | Example |
|------|-------------|---------|---------|
| **0** | Pre Arrival | Not yet arrived | Status_Location contains "Pre Arrival" |
| **1** | Port → Site | Direct delivery | Port → SHU (no warehouse, no MOSB) |
| **2** | Port → WH → Site | Warehouse transit | Port → DSV Indoor → MIR |
| **3** | Port → MOSB → Site | MOSB transit | Port → MOSB → DAS (AGI/DAS required) |
| **4** | Port → WH → MOSB → Site | Warehouse + MOSB | Port → DSV Indoor → MOSB → AGI |
| **5** | Mixed/Incomplete | Abnormal pattern | MOSB exists but no Site, or WH≥2 + no MOSB |

### Calculation Logic

**Step 1: Preprocessing**
- Normalize column names (remove newlines, normalize spaces)
- Replace 0 and "" with NaN for consistent null handling
- Separate WH_COLS and MOSB_COLS

**Step 2: Observations**
```python
is_pre_arrival = Status_Location.str.contains("Pre Arrival", case=False)
wh_cnt = count_non_null(WH_COLS)  # Warehouse count
has_mosb = any_non_null(MOSB_COLS)  # MOSB exists
has_site = any_non_null(SITE_COLS)  # Site exists
final_location = latest_non_null(SITE_COLS)  # Latest site date
```

**Step 3: Basic Flow Code**
```
Flow 0: is_pre_arrival = True
Flow 1: wh_cnt = 0 AND has_mosb = False
Flow 2: wh_cnt ≥ 1 AND has_mosb = False
Flow 3: wh_cnt = 0 AND has_mosb = True
Flow 4: wh_cnt ≥ 1 AND has_mosb = True
```

**Step 4: AGI/DAS Domain Override**
```
IF final_location IN ("AGI", "DAS") AND flow_code IN (0, 1, 2):
    flow_code = 3
    flow_override_reason = "AGI/DAS requires MOSB leg"
    flow_code_original = previous_flow_code
```

**Step 5: Mixed Cases (Flow 5)**
```
IF (has_mosb = True AND has_site = False) OR (wh_cnt ≥ 2 AND has_mosb = False):
    flow_code = 5
    flow_description = "Flow 5: Mixed / Waiting / Incomplete leg"
```

### Pre-Arrival Logic

Two methods supported:

**Method 1: ATA Column**
```python
if ATA is NaN:
    is_pre_arrival = True
```

**Method 2: Date Columns**
```python
if all warehouse/site columns are NaN:
    is_pre_arrival = True
```

### Final Location Extraction

Algorithm extracts latest site based on dates:
```python
for each Site column:
    if date value exists:
        store (column_name, date_value)
return column_name with maximum date
```

Example:
- SHU=2024-01-10, MIR=2024-01-15, DAS=NaN
- Final_Location = "MIR"

---

## Usage Guide

### Python API

#### Basic Conversion

```python
from logiontology.src.ingest.excel_to_ttl_with_events import convert_data_wh_to_ttl_with_events

result = convert_data_wh_to_ttl_with_events(
    excel_path="HVDC STATUS(20250815) (1).xlsx",
    output_path="output/hvdc_status_v35.ttl",
    flow_version="3.5"
)

print(f"Cases: {result['cases_created']}")
print(f"Inbound events: {result['inbound_events']}")
print(f"Outbound events: {result['outbound_events']}")
```

#### Standalone Flow Code Calculation

```python
from logiontology.src.ingest.flow_code_calculator import calculate_flow_code_v35
import pandas as pd

# Load Excel
df = pd.read_excel("data.xlsx")

# Define columns
warehouse_columns = [
    "DSV Indoor", "DSV Outdoor", "DSV MZD", "MOSB",
    "AAA Storage", "Hauler DG Storage"
]
site_columns = ["SHU", "MIR", "DAS", "AGI"]

# Calculate Flow Code v3.5
df = calculate_flow_code_v35(df, warehouse_columns, site_columns)

# Results
print(df[['FLOW_CODE', 'FLOW_DESCRIPTION', 'FLOW_CODE_ORIG', 'Final_Location']].head(10))
```

### Command-Line Interface

```bash
# Basic conversion
python -m scripts.convert_data_wh_to_ttl \
    --input "HVDC STATUS(20250815) (1).xlsx" \
    --output "output/hvdc_status_v35.ttl"

# With Flow Code version
python -m scripts.convert_data_wh_to_ttl \
    --input "data.xlsx" \
    --output "output.ttl" \
    --flow-version 3.5

# Validate with SPARQL
python -m scripts.validate_events_with_sparql \
    --ttl "output/hvdc_status_v35.ttl" \
    --output "validation_report.json"
```

### SPARQL Querying

#### Flow Code Distribution

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
    ?flowCode
    ?description
    (COUNT(?case) AS ?count)
WHERE {
    ?case hvdc:hasFlowCode ?flowStr .
    BIND(xsd:integer(?flowStr) AS ?flowCode)
    ?case hvdc:hasFlowDescription ?description .
}
GROUP BY ?flowCode ?description
ORDER BY ?flowCode
```

#### AGI/DAS Compliance Check

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
    (COUNT(?agi) AS ?agiTotal)
    (COUNT(?agiCompliant) AS ?agiCompliant)
    ((COUNT(?agiCompliant) * 100.0 / COUNT(?agi)) AS ?complianceRate)
WHERE {
    ?case hvdc:hasFinalLocation "AGI" .
    ?case hvdc:hasFlowCode ?flow .
    BIND(?case AS ?agi)
    OPTIONAL {
        ?case hvdc:hasFlowCode ?flowComp .
        FILTER(xsd:integer(?flowComp) >= 3)
        BIND(?case AS ?agiCompliant)
    }
}
```

#### Override Tracking

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT
    ?case
    ?flowCode
    ?flowCodeOrig
    ?overrideReason
    ?finalLocation
WHERE {
    ?case hvdc:hasFlowCodeOriginal ?flowCodeOrig ;
          hvdc:hasFlowOverrideReason ?overrideReason ;
          hvdc:hasFinalLocation ?finalLocation ;
          hvdc:hasFlowCode ?flowCode .
}
```

### Integration with MCP Server

The MCP (Model Context Protocol) server can query the TTL data:

```python
# MCP server configuration
MCP_SERVER_CONFIG = {
    "ttl_path": "output/hvdc_status_v35.ttl",
    "namespace": "http://samsung.com/project-logistics#",
    "sparql_endpoint": "http://localhost:8000/sparql"
}

# Available commands
- /flow_code_distribution
- /agi_das_compliance
- /case_by_flow
- /vendor_summary
- /monthly_warehouse_inbound
```

---

## Testing & Validation

### Unit Tests

**File**: `tests/test_flow_code_v35.py`

12 test cases covering:
- Column normalization
- Final location extraction
- Pre-arrival detection (ATA-based and date-based)
- Flow 0 (Pre Arrival)
- Flow 1 (Direct delivery)
- Flow 2 (Warehouse transit)
- Flow 3 (MOSB transit)
- Flow 4 (Warehouse + MOSB)
- Flow 5 (Mixed case)
- AGI/DAS force upgrade
- Final location extraction validation

**Execution**:
```bash
pytest tests/test_flow_code_v35.py -v
```

**Expected Output**:
```
12 passed in 0.73s
```

### Integration Tests

**File**: `tests/test_flow_code_v35_validation.py`

7 test cases covering:
- AGI cases all Flow 3 or higher
- DAS cases all Flow 3 or higher
- AGI/DAS override tracking
- Flow 5 cases exist
- Flow 5 has description
- All Flow codes exist
- Flow code range validation

**Execution**:
```bash
pytest tests/test_flow_code_v35_validation.py -v
```

**Expected Output**:
```
7 passed in 0.86s
```

### Validation Queries

**File**: `queries/event_validation.sparql`

10 SPARQL queries for data quality:
1. Event coverage check
2. Missing dates detection
3. Flow 0-5 event patterns
4. AGI/DAS compliance
5. Override reason presence
6. Final location accuracy
7. Duplicate case detection
8. Schema compliance
9. Data type validation
10. Relationship completeness

**Execution**:
```bash
python scripts/validate_events_with_sparql.py output/hvdc_status_v35.ttl
```

### Performance Metrics

**Real Data Conversion** (755 cases):
- Processing time: ~2.5 seconds
- Memory usage: ~150MB peak
- TTL output: 9,845 lines
- Event generation: 818 events (573 inbound, 245 outbound)

**Test Execution**:
- Unit tests: 0.73s
- Integration tests: 0.86s
- Total: 1.59s

---

## Troubleshooting

### Common Issues

#### Issue 1: Flow Code > 5

**Symptom**: Validation error "Flow Code exceeds 5"

**Cause**: Data corruption or invalid warehouse/site columns

**Solution**:
```python
# Check column mapping
warehouse_columns = [...]  # Verify columns exist in Excel
site_columns = [...]  # Verify columns exist in Excel

# Run calculation with logging
import logging
logging.basicConfig(level=logging.DEBUG)
df = calculate_flow_code_v35(df, warehouse_columns, site_columns)

# Check for anomalies
invalid = df[~df["FLOW_CODE"].isin([0, 1, 2, 3, 4, 5])]
print(f"Invalid flow codes: {invalid[['FLOW_CODE', 'FLOW_DESCRIPTION']]}")
```

#### Issue 2: AGI/DAS Not Upgraded

**Symptom**: AGI or DAS cases with Flow Code < 3

**Cause**: Final_Location column not found or incorrectly extracted

**Solution**:
```python
# Check Final_Location extraction
df['Final_Location_CHECK'] = df.apply(
    lambda row: extract_final_location(row, SITE_COLS),
    axis=1
)

# Verify AGI/DAS in Final_Location
agi_das_cases = df[df['Final_Location_CHECK'].isin(['AGI', 'DAS'])]
print(f"AGI/DAS cases: {len(agi_das_cases)}")
print(f"Flow < 3: {len(agi_das_cases[agi_das_cases['FLOW_CODE'] < 3])}")
```

#### Issue 3: No Events Generated

**Symptom**: Empty TTL file or no stock events

**Cause**: All cases classified as Flow 0 (Pre Arrival) or Flow 5

**Solution**:
```python
# Check Flow Code distribution
distribution = df['FLOW_CODE'].value_counts().sort_index()
print(f"Flow Code distribution:\n{distribution}")

# Check Pre Arrival cases
pre_arrival = df[df['is_pre_arrival'] == True]
print(f"Pre Arrival: {len(pre_arrival)}")

# Check data quality
missing_dates = df.isna().sum()
print(f"Missing dates:\n{missing_dates[missing_dates > 0]}")
```

#### Issue 4: Column Not Found

**Symptom**: Warning "Column not found" or empty WH_COLS/SITE_COLS

**Cause**: Column name mismatch between WAREHOUSE_KEYS and actual Excel columns

**Solution**:
```python
# Inspect actual column names
df = pd.read_excel("data.xlsx")
print("Available columns:")
print(df.columns.tolist())

# Use column name normalization
from logiontology.src.ingest.flow_code_calculator import normalize_column_names
df_normalized = normalize_column_names(df)
print("Normalized columns:")
print(df_normalized.columns.tolist())
```

### Debug Logging

Enable detailed logging:

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run conversion
result = convert_data_wh_to_ttl_with_events(...)
```

### Data Quality Checks

**Pre-conversion Checklist**:
- [ ] Excel file readable
- [ ] Column names match WAREHOUSE_KEYS/SITE_KEYS
- [ ] Date columns contain valid dates or NaN
- [ ] ATA column exists (optional but recommended)
- [ ] Status_Location column exists

**Post-conversion Checklist**:
- [ ] TTL file size > 0
- [ ] Flow Code 0-5 distribution is balanced
- [ ] AGI/DAS cases all Flow 3+
- [ ] Event counts reasonable
- [ ] SPARQL validation passes

### Migration from v3.4

**Step 1**: Backup existing data
```bash
cp output/data_wh_v34.ttl output/data_wh_v34_backup.ttl
```

**Step 2**: Update Flow Code version
```python
# Change default version
flow_version = "3.5"  # from "3.4"
```

**Step 3**: Re-run conversion
```bash
python -m scripts.convert_data_wh_to_ttl \
    --input "DATA WH.xlsx" \
    --output "output/data_wh_v35.ttl" \
    --flow-version 3.5
```

**Step 4**: Validate differences
```python
# Compare Flow Code distributions
# v3.4: Flow 0-4
# v3.5: Flow 0-5

# Check for new Flow 5 cases
flow5_cases = df[df['FLOW_CODE'] == 5]
print(f"New Flow 5 cases: {len(flow5_cases)}")

# Check for AGI/DAS upgrades
agi_das_overrides = df[df['FLOW_OVERRIDE_REASON'].notna()]
print(f"AGI/DAS overrides: {len(agi_das_overrides)}")
```

---

## MCP Server Integration

After generating the TTL file, you can query the data in real-time using the MCP (Model Context Protocol) Server.

### Server Setup

**1. Navigate to MCP Server directory**:
```bash
cd hvdc_mcp_server_v35
```

**2. Install dependencies**:
```bash
pip install -r requirements.txt
```

**3. Configure TTL path**:
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env
TTL_PATH=../output/hvdc_status_v35.ttl
```

**4. Start the server**:
```bash
uvicorn mcp_server.mcp_ttl_server:app --reload
```

Server will be available at http://localhost:8000

### API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/flow/distribution` | GET | Flow 0-5 statistics | Returns 6 flow code entries |
| `/flow/compliance` | GET | AGI/DAS compliance | Returns 100% compliance |
| `/flow/overrides` | GET | Override tracking | Returns 31 override records |
| `/case/{case_id}` | GET | Case details | `/case/00045` |
| `/flow/5/analysis` | GET | Mixed cases | Returns 81 Flow 5 cases |
| `/flow/0/status` | GET | Pre-arrival cases | Returns 71 Flow 0 cases |
| `/mcp/query` | POST | Custom SPARQL | Body: `{"query": "..."}` |

### Example Queries

**Get Flow Code Distribution**:
```bash
curl http://localhost:8000/flow/distribution
```

Response:
```json
[
  {"flowCode": 0, "description": "Flow 0: Pre Arrival", "count": 71},
  {"flowCode": 1, "description": "Flow 1: Port → Site", "count": 255},
  {"flowCode": 2, "description": "Flow 2: Port → WH → Site", "count": 152},
  {"flowCode": 3, "description": "Flow 3: Port → MOSB → Site", "count": 131},
  {"flowCode": 4, "description": "Flow 4: Port → WH → MOSB → Site", "count": 65},
  {"flowCode": 5, "description": "Flow 5: Mixed / Waiting / Incomplete leg", "count": 81}
]
```

**Check AGI/DAS Compliance**:
```bash
curl http://localhost:8000/flow/compliance
```

Response:
```json
{
  "total_agi_das": 31,
  "compliant_count": 31,
  "compliance_rate": 100.0
}
```

**Get Override Cases**:
```bash
curl http://localhost:8000/flow/overrides
```

Returns 31 cases with original and new flow codes, reasons, and final locations.

**Custom SPARQL Query**:
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "PREFIX hvdc: <http://samsung.com/project-logistics#> SELECT (COUNT(*) AS ?total) WHERE { ?s a hvdc:Case }"
  }'
```

### CLI Commands

The MCP server also provides CLI commands:

```bash
# Flow Code distribution
python -m mcp_server.commands flow_code_distribution_v35

# AGI/DAS compliance check
python -m mcp_server.commands agi_das_compliance

# Override cases
python -m mcp_server.commands override_cases

# Look up specific case
python -m mcp_server.commands case_lookup 00045

# Flow 5 analysis
python -m mcp_server.commands flow_5_analysis

# Pre-arrival status
python -m mcp_server.commands pre_arrival_status
```

### GPT Custom Action Integration

**1. Start the MCP server**:
```bash
uvicorn mcp_server.mcp_ttl_server:app --host 0.0.0.0 --port 8000
```

**2. Download OpenAPI specification**:
Visit http://localhost:8000/openapi.json or use:
```bash
curl http://localhost:8000/openapi.json > hvdc_mcp_openapi.json
```

**3. Configure GPT Custom Actions**:
- Open GPT → Configure → Actions
- Import `hvdc_mcp_openapi.json`
- Set server URL (e.g., `http://your-server:8000`)

**4. Define Actions**:
- `get_flow_distribution`: Calls `/flow/distribution`
- `check_compliance`: Calls `/flow/compliance`
- `get_overrides`: Calls `/flow/overrides`
- `get_case`: Calls `/case/{case_id}`

**5. Example GPT Queries**:
- "What's the distribution of Flow Codes?"
- "Are all AGI/DAS cases compliant with MOSB requirements?"
- "Show me cases that had their Flow Code overridden"
- "Analyze Flow 5 mixed/incomplete cases"

### Docker Deployment

**1. Build and run with Docker Compose**:
```bash
cd hvdc_mcp_server_v35
docker-compose up
```

**2. Access the API**:
http://localhost:8000

**3. View OpenAPI docs**:
http://localhost:8000/docs

### Performance

- **Query Time**: <100ms per query (755 cases)
- **Memory**: ~150MB
- **Concurrent Users**: 10+ supported
- **Scalability**: Good for <10K cases

For larger datasets, consider Apache Fuseki or Virtuoso.

### Integration with Conversion Pipeline

The conversion script automatically logs MCP server information:

```python
# In excel_to_ttl_with_events.py
logger.info(f"TTL generated for MCP server: {output_path}")
logger.info("Start server: uvicorn mcp_server.mcp_ttl_server:app --reload")
logger.info("Query endpoint: http://localhost:8000/mcp/query")
```

### Troubleshooting

**Server won't start**:
- Check if TTL file exists at specified path
- Verify RDFLib can parse the file: `python -c "from rdflib import Graph; g = Graph(); g.parse('output/hvdc_status_v35.ttl', format='turtle'); print(len(g))"`

**Queries return empty results**:
- Verify namespace: `PREFIX hvdc: <http://samsung.com/project-logistics#>`
- Check property names: `hvdc:hasFlowCode` not `mcp:flow_code`
- Test with simple query via `/docs` endpoint

**Performance issues**:
- Expected: <500ms per query
- Actual: ~50-100ms with RDFLib
- If slower, check dataset size and consider Fuseki

For more details, see:
- `hvdc_mcp_server_v35/README.md` - Complete server documentation
- `MCP_FLOW_CODE_V35_INTEGRATION.md` - Integration architecture

---

## References & Related Documents

### Primary Documentation

1. **Algorithm Specification** (Detailed)
   - `FLOW_CODE_V35_ALGORITHM.md` - Complete algorithm logic, examples, edge cases

2. **Implementation Report** (Status)
   - `FLOW_CODE_V35_IMPLEMENTATION_COMPLETE.md` - Implementation details, test results

3. **Integration Guide** (Usage)
   - `FLOW_CODE_V35_INTEGRATION.md` - Integration steps, API reference

4. **This Document** (Master)
   - `FLOW_CODE_V35_MASTER_DOCUMENTATION.md` - Comprehensive reference

### Ontology Documentation

**Core Ontology**:
- `core/1_CORE-08-flow-code.md` - Core Flow Code ontology (unified-3.5)
- `core/1_CORE-03-hvdc-warehouse-ops.md` - Warehouse operations ontology

**Consolidated**:
- `core_consolidated/CONSOLIDATED-02-warehouse-flow.md` - Warehouse + Flow consolidated (v3.5)
- `core_consolidated/README.md` - Consolidated docs overview

**Extended**:
- `extended/2_EXT-05-hvdc-ops-management.md` - Operations management
- `extended/2_EXT-06-hvdc-compliance-customs.md` - Compliance and customs

### Source Code

**Implementation**:
- `logiontology/src/ingest/flow_code_calculator.py` - Core algorithm
- `logiontology/src/ingest/excel_to_ttl_with_events.py` - Conversion pipeline
- `logiontology/configs/ontology/hvdc_event_schema.ttl` - Ontology schema

**Testing**:
- `tests/test_flow_code_v35.py` - Unit tests
- `tests/test_flow_code_v35_validation.py` - Integration tests

**Scripts**:
- `scripts/convert_data_wh_to_ttl.py` - CLI conversion script
- `scripts/validate_events_with_sparql.py` - Validation script

### Planning Documents

- `\data-wh-excel-to-ttl-conversion.plan.md` - Original conversion plan
- Plan documents contain detailed requirements and architecture

### Generated Output

- `output/hvdc_status_v35.ttl` - Generated RDF/TTL (9,845 lines)
- `test_output_v35.ttl` - Test TTL output
- `validation_results/` - SPARQL validation reports

---

## Appendices

### Appendix A: Complete Flow Code Matrix

| Scenario | WH Count | MOSB | Site | Pre Arrival | Final Loc | Flow Code | Notes |
|----------|----------|------|------|-------------|-----------|-----------|-------|
| Nothing | 0 | No | No | Yes | - | 0 | Pre Arrival |
| Direct | 0 | No | Yes | No | MIR | 1 | Port → MIR |
| 1 WH | 1 | No | Yes | No | SHU | 2 | Port → WH → SHU |
| MOSB | 0 | Yes | Yes | No | DAS | 3 | AGI/DAS required |
| AGI Direct | 0 | No | Yes | No | AGI | 3 | Upgraded (forced) |
| WH+MOSB | 1 | Yes | Yes | No | AGI | 4 | Port → WH → MOSB → AGI |
| MOSB No Site | 0 | Yes | No | No | - | 5 | Incomplete |
| 2 WH No MOSB | 2 | No | Yes | No | SHU | 5 | Abnormal pattern |

### Appendix B: Excel Column Mapping

**Standard Mapping** (from `HVDC STATUS(20250815) (1).xlsx`):

| Category | Column Names | Count |
|----------|--------------|-------|
| **Warehouses** | DSV Indoor, DSV Outdoor, DSV MZD, DSV Al Markaz, DSV MZP, JDN MZD, JDN Waterfront, MOSB, AAA Storage, Hauler Indoor, Hauler DG Storage, DHL WH, ZENER (WH), Vijay Tanks | 14 |
| **Sites** | SHU, MIR, DAS, AGI | 4 |
| **Metadata** | Status_Location, Final_Location, ATA, Vendor, HVDC Code, Pkg, CBM, G.W(KG) | 8+ |

**Note**: Column names are normalized (newlines removed, spaces trimmed).

### Appendix C: RDF/TTL Examples

#### Example 1: Flow 2 (Warehouse Transit)

```turtle
hvdc:Case_00003 a hvdc:Case ;
    hvdc:hasFlowCode "2"^^xsd:string ;
    hvdc:hasFlowCodeOriginal 2 ;
    hvdc:hasFlowDescription "Flow 2: Port → WH → Site"^^xsd:string ;
    hvdc:hasHvdcCode "HVDC-ADOPT-HS-0001"^^xsd:string ;
    hvdc:hasInboundEvent [ a hvdc:StockEvent ;
            hvdc:hasEventDate "2024-01-20"^^xsd:date ;
            hvdc:hasLocationAtEvent "Vijay Tanks"^^xsd:string ;
            hvdc:hasQuantity 1.0 ] ;
    hvdc:hasVendor "SCT Trade"^^xsd:string .
```

#### Example 2: AGI Force Upgrade (Flow 3)

```turtle
hvdc:Case_00011 a hvdc:Case ;
    hvdc:hasFlowCode "3"^^xsd:string ;
    hvdc:hasFlowCodeOriginal 2 ;
    hvdc:hasFlowDescription "Flow 3: Port → MOSB → Site (AGI/DAS forced)"^^xsd:string ;
    hvdc:hasFlowOverrideReason "AGI/DAS requires MOSB leg"^^xsd:string ;
    hvdc:hasFinalLocation "DAS"^^xsd:string ;
    hvdc:hasOutboundEvent [ a hvdc:StockEvent ;
            hvdc:hasEventDate "2024-01-30"^^xsd:date ;
            hvdc:hasLocationAtEvent "DAS"^^xsd:string ;
            hvdc:hasQuantity 1.0 ] .
```

#### Example 3: Flow 5 (Mixed Case)

```turtle
hvdc:Case_00001 a hvdc:Case ;
    hvdc:hasFlowCode "5"^^xsd:string ;
    hvdc:hasFlowCodeOriginal 2 ;
    hvdc:hasFlowDescription "Flow 5: Mixed / Waiting / Incomplete leg"^^xsd:string ;
    hvdc:hasHvdcCode "HVDC-ADOPT-PPL-0001"^^xsd:string .
```

### Appendix D: Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| v3.4 | 2025-10-26 | Bug fix: Off-by-one error, Pre Arrival detection |
| v3.5 | 2025-10-31 | Flow 5 added, AGI/DAS domain rules, override tracking |

### Appendix E: Change Log

**v3.5 Changes (2025-10-31)**:
- Added Flow Code 5 for mixed/incomplete cases
- Implemented AGI/DAS domain rule (forced Flow 3)
- Added FLOW_CODE_ORIG for tracking
- Added FLOW_OVERRIDE_REASON for audit trail
- Added Final_Location auto-extraction
- Extended ontology properties (4 new)
- Updated SHACL constraints (0-5 range)
- Comprehensive test coverage (19 tests)
- Real data validation (755 cases)

---

## Glossary

| Term | Definition |
|------|------------|
| **AGI** | Al Ghallan Island - Offshore site requiring MOSB transit |
| **ATA** | Actual Time of Arrival - Real arrival date |
| **DAS** | Das Island - Offshore site requiring MOSB transit |
| **Flow Code** | Numerical classification of logistics flow pattern (0-5) |
| **Final_Location** | Last site destination automatically extracted from site columns |
| **MIR** | Mirfa - Onshore site allowing direct delivery |
| **MOSB** | Mussafah Offshore Supply Base - Central logistics hub |
| **RDF** | Resource Description Framework - Graph data format |
| **SHACL** | Shapes Constraint Language - Data validation |
| **SHU** | Shuweihat - Onshore site allowing direct delivery |
| **SPARQL** | Query language for RDF graphs |
| **TTL** | Turtle - Human-readable RDF serialization |

---

## Contributing

When updating Flow Code logic:

1. Update `flow_code_calculator.py` algorithm
2. Add/update unit tests in `test_flow_code_v35.py`
3. Update ontology schema if new properties needed
4. Regenerate TTL with test data
5. Validate with `test_flow_code_v35_validation.py`
6. Update all documentation files
7. Run full test suite
8. Commit with descriptive message

---

## License

HVDC Logistics Ontology - Internal Use Only

---

## Contact

For questions or issues:
- Technical: Check existing tests and SPARQL validation
- Documentation: Refer to FLOW_CODE_V35_ALGORITHM.md
- Integration: See FLOW_CODE_V35_INTEGRATION.md

---

**Document Version**: 1.0
**Last Updated**: 2025-01-25
**Maintained By**: HVDC Project Team

