# HVDC Ontology Data Hub - Usage Guide

**Purpose**: Step-by-step guide for navigating and using the ontology data hub
**Last Updated**: 2025-10-31

---

## Quick Start

### For Ontology Developers

1. Start with `01_ontology/consolidated/README.md` for overview
2. Review `05_cross_references/ONTOLOGY_COVERAGE_MATRIX.md` for mappings
3. Check `02_schemas/core/` for TTL implementations
4. Query `03_data/ttl/current/hvdc_status_v35.ttl` for instances

### For Data Analysts

1. Use `03_data/json/gpt_cache/` for pre-computed aggregations
2. Browse `03_data/json/reports/` for analysis results
3. Query `03_data/ttl/current/hvdc_status_v35.ttl` with SPARQL
4. Check `05_cross_references/QUERY_TEMPLATES.md` for examples

### For MCP/GPT Integration

1. Load `03_data/ttl/current/hvdc_status_v35.ttl` into RDFLib
2. Use `03_data/json/gpt_cache/` for fast responses
3. Reference `05_cross_references/FLOW_CODE_LINEAGE.md` for context
4. Apply SHACL validation from `02_schemas/shapes/`

---

## Common Tasks

### Task 1: Understand Flow Code v3.5

**Documents**:
- `01_ontology/consolidated/CONSOLIDATED-02-warehouse-flow.md` (Lines 62-100)
- `02_schemas/core/flow_code.ttl`
- `02_schemas/shapes/FlowCode.shape.ttl`

**Data**:
- `03_data/ttl/current/hvdc_status_v35.ttl` (9,795 cases)
- `03_data/json/gpt_cache/cases_by_flow.json`

**Queries**:
- See `05_cross_references/QUERY_TEMPLATES.md` → Flow Code section

### Task 2: Query AGI/DAS Compliance

**Documents**:
- `01_ontology/consolidated/CONSOLIDATED-02-warehouse-flow.md` (Lines 486-537)
- `02_schemas/shapes/FlowCode.shape.ttl` (Lines 62-89)

**Data**:
- `03_data/ttl/current/hvdc_status_v35.ttl`

**Query**:
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?case ?flowCode ?overrideReason
WHERE {
  ?case hvdc:hasFinalLocation ?site .
  FILTER(?site IN ("AGI", "DAS"))
  ?case hvdc:hasFlowCode ?flowCode .
  OPTIONAL { ?case hvdc:hasFlowOverrideReason ?overrideReason }
}
ORDER BY ?flowCode
```

### Task 3: Validate OCR Quality

**Documents**:
- `01_ontology/consolidated/CONSOLIDATED-03-document-ocr.md` (Lines 849-880, 1102-1115)

**Constraints**:
- MeanConf ≥ 0.92
- TableAcc ≥ 0.98
- NumericIntegrity = 1.00
- EntityMatch ≥ 0.98 ⭐

**Validation**:
```sparql
PREFIX ldg: <http://example.com/ldg#>
SELECT ?doc ?meanConf ?tableAcc ?entityMatch
WHERE {
  ?doc ldg:hasMetric ?metric .
  ?metric ldg:hasMeanConf ?meanConf ;
          ldg:hasTableAcc ?tableAcc ;
          ldg:hasEntityMatch ?entityMatch .
  FILTER(?meanConf < 0.92 || ?tableAcc < 0.98 || ?entityMatch < 0.98)
}
```

---

## File Relationships

### Conceptual → Formal → Operational

```
Documentation (MD)        Schema (TTL)               Data (TTL/JSON)
─────────────────────────────────────────────────────────────────────
01_ontology/             02_schemas/                03_data/
├─ CONSOLIDATED-01  →    ├─ hvdc_ontology.ttl  →    ├─ ttl/current/
├─ CONSOLIDATED-02  →    ├─ flow_code.ttl      →    │  └─ hvdc_status_v35.ttl
├─ CONSOLIDATED-03  →    ├─ hvdc_nodes.ttl     →    │
├─ CONSOLIDATED-04  →    └─ shapes/            →    ├─ ttl/finalized/
└─ CONSOLIDATED-05  →       └─ FlowCode.shape  →    ├─ ttl/specialized/
                                                     └─ json/
                                                        ├─ gpt_cache/
                                                        ├─ integration/
                                                        └─ reports/
```

---

## Integration Points

### With MCP Server

Use `hvdc_status_v35.ttl` for SPARQL queries, `gpt_cache/*.json` for fast aggregations.

### With Validation

SHACL shapes from `02_schemas/shapes/` validate all TTL data.

### With Reporting

JSON analytics in `03_data/json/reports/` derived from TTL data.

---

**See Also**: `MASTER_INDEX.md`, `ONTOLOGY_COVERAGE_MATRIX.md`, `FLOW_CODE_LINEAGE.md`

