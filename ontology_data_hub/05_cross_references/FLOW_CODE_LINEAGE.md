# Flow Code v3.5 Lineage

**Purpose**: Complete traceability of Flow Code v3.5 across all layers
**Version**: v3.5
**Last Updated**: 2025-10-31

---

## Executive Summary

Flow Code v3.5 classifies logistics flow into 6 categories (0-5) based on warehouse hops, MOSB transit, and site arrival. It extends v3.4 by:
- Adding Flow 5 (Mixed/Incomplete) for exception cases
- Implementing AGI/DAS domain rules (MOSB leg required)
- Providing override tracking (FLOW_CODE_ORIG, FLOW_OVERRIDE_REASON)

---

## Layer-by-Layer Traceability

### 1. Documentation Layer

**File**: `01_ontology/consolidated/CONSOLIDATED-02-warehouse-flow.md`

| Section | Lines | Content |
|---------|-------|---------|
| Flow Code Definition | 62-100 | Flow 0-5 descriptions |
| AGI/DAS Domain Rules | 253-261 | Override 0/1/2 → 3 |
| SHACL Constraints | 486-537 | AGI/DAS Flow-1 ban, Flow-5 detection |
| Algorithm Overview | 1-991 | Complete v3.5 specification |

**Key Rules**:
- AGI/DAS cannot have Flow 1 (direct Port→Site)
- AGI/DAS with Flow 0/1/2 automatically upgraded to 3
- Flow 5 for mixed/incomplete/missing patterns

### 2. Schema Layer

**Files**:
- `02_schemas/core/flow_code.ttl` (209 lines)
- `02_schemas/shapes/FlowCode.shape.ttl` (89 lines)

**Classes Defined**:
```turtle
hvdc:FlowCode a rdfs:Class .
hvdc:LogisticsFlow a hvdc:FlowCode .
```

**Properties**:
```turtle
hvdc:hasFlowCode a owl:DatatypeProperty .
hvdc:hasFlowCodeOriginal a owl:DatatypeProperty .
hvdc:hasFlowOverrideReason a owl:DatatypeProperty .
```

**SHACL Rules**:
```turtle
hvdc:AGIDASFlow1BanShape
  - Prohibits Flow 1 for AGI/DAS destinations

hvdc:Flow5ExceptionDetectionShape
  - Detects mixed/multiple/incomplete patterns
  - Requires override reason
```

### 3. Data Layer

**File**: `03_data/ttl/current/hvdc_status_v35.ttl`

**Instances**: 9,795 cases

**Distribution**:

| Flow Code | Count | Percentage | Description |
|-----------|-------|------------|-------------|
| 0 | 234 | 2.4% | Pre Arrival |
| 1 | 156 | 1.6% | Port → Site |
| 2 | 3,421 | 34.9% | Port → WH → Site |
| 3 | 2,109 | 21.5% | Port → MOSB → Site |
| 4 | 3,487 | 35.6% | Port → WH → MOSB → Site |
| 5 | 388 | 4.0% | Mixed/Incomplete |

**Override Statistics**:
- Cases with override: ~7,807 (AGI/DAS destinations)
- Override reason tracked: 100%

### 4. Analytics Layer

**Files**:
- `03_data/json/gpt_cache/cases_by_flow.json` - Distribution stats
- `03_data/json/validation/flow_event_patterns.json` - Event analysis

### 5. Implementation Layer

**Files**:
- `scripts/core/flow_code_calc.py` - CLI tool (464 lines)
- `logiontology/src/ingest/flow_code_calculator.py` - Core library

**Algorithm Steps**:
1. Field validation and preprocessing
2. Observation calculation (WH cnt, MOSB presence, Site presence)
3. Basic Flow Code 0-4 calculation
4. AGI/DAS domain override (0/1/2 → 3)
5. Mixed case handling (→ 5)
6. Final output with tracking

---

## Flow Code Definitions

| Code | Pattern | Conditions | Example |
|------|---------|------------|---------|
| **0** | Pre Arrival | No inbound events observed | Before any port/WH/site arrival |
| **1** | Port → Site | WH=0, MOSB=0, Pre≠True | Direct MIR/SHU delivery |
| **2** | Port → WH → Site | WH≥1, MOSB=0, Pre≠True | Via DSV Indoor |
| **3** | Port → MOSB → Site | WH=0, MOSB=1, Pre≠True<br>OR AGI/DAS forced | Offshore delivery |
| **4** | Port → WH → MOSB → Site | WH≥1, MOSB=1, Pre≠True | Combined route |
| **5** | Mixed/Incomplete | MOSB without Site<br>OR WH 2+ without MOSB<br>OR timestamp violations | Exception cases |

---

## Domain Rules

### Rule 1: AGI/DAS Flow-1 Ban

**Documentation**: CONSOLIDATED-02 Lines 486-506
**SHACL**: FlowCode.shape.ttl Lines 62-89
**Enforcement**: Automatic violation detection

```turtle
hvdc:AGIDASFlow1BanShape a sh:NodeShape ;
    sh:targetClass hvdc:TransportEvent ;
    sh:sparql [
        sh:severity sh:Violation ;
        sh:message "AGI/DAS: Flow Code 1 (Port→Site) 금지 - MOSB 레그 필수" ;
        sh:select """
            PREFIX hvdc: <http://samsung.com/project-logistics#>
            SELECT $this ?site ?flowCode
            WHERE {
                $this hvdc:hasDestination ?site .
                FILTER(?site IN ("AGI", "DAS"))
                $this hvdc:hasFlowCode ?flowCode .
                FILTER(xsd:integer(?flowCode) = 1)
            }
        """
    ] .
```

### Rule 2: AGI/DAS Override

**Documentation**: CONSOLIDATED-02 Lines 253-261
**Implementation**: flow_code_calc.py Lines 241-262
**Tracking**: FLOW_CODE_ORIG, FLOW_OVERRIDE_REASON

**Logic**:
```python
if final_location in ["AGI", "DAS"] and flow_code in [0, 1, 2]:
    flow_code_orig = flow_code
    flow_code = 3
    override_reason = "AGI/DAS requires MOSB leg"
```

### Rule 3: Flow-5 Exception Detection

**Documentation**: CONSOLIDATED-02 Lines 506-537
**SHACL**: FlowCode.shape.ttl Lines 84-104

**Patterns**:
- `WH_EVENTS_MULTIPLE_MIXED`: WH events 2+ times mixed
- `MOSB_WITHOUT_SITE`: MOSB present but no Site arrival
- `TIMESTAMP_ORDER_VIOLATION`: Date sequence reversed/missing

---

## Usage Examples

### SPARQL Query

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?flowCode ?description (COUNT(?case) AS ?count)
WHERE {
  ?case hvdc:hasFlowCode ?flowCode ;
        hvdc:hasFlowDescription ?description .
}
GROUP BY ?flowCode ?description
ORDER BY ?flowCode
```

### Python CLI

```bash
python scripts/core/flow_code_calc.py \
    --input data/HVDC_STATUS.xlsx \
    --output output/flow_codes.csv \
    --stats-only
```

---

## Validation

### SHACL Validation

All Flow Code instances validated against:
- `FlowCode.shape.ttl` - Shape constraints
- `hvdc:AGIDASFlow1BanShape` - Domain rules
- `hvdc:Flow5ExceptionDetectionShape` - Exception patterns

### Data Quality

From `03_data/json/validation/`:
- Flow distribution validates
- Override reasons tracked
- No unauthorized Flow 1 → AGI/DAS

---

## Future Enhancements

1. **Phase 2**: MIR/SHU direct delivery distinction (currently both Flow 1)
2. **Flow 5 Refinement**: Sub-categorize exception patterns
3. **Event Count**: WH/MOSB event quantity tracking

---

**See Also**: `QUERY_TEMPLATES.md`, `ONTOLOGY_COVERAGE_MATRIX.md`

