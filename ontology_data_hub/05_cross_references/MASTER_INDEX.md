# HVDC Ontology Data Hub - Master Index

**Last Updated**: 2025-10-31
**Total Files**: 92 files | 906,980 lines
**Structure**: 5 main sections | 12 subdirectories

---

## Quick Navigation

| Section | Description | Files | Lines | Key Files |
|---------|-------------|-------|-------|-----------|
| [01_ontology](#01_ontology) | Conceptual documentation | 6 | 4,314 | Consolidated docs |
| [02_schemas](#02_schemas) | RDF/OWL definitions | 9 | 1,296 | Ontology + shapes |
| [03_data](#03_data) | Operational data | 36 | 443,181 | TTL instances + JSON analytics |
| [04_archive](#04_archive) | Historical versions | 23 | 407,585 | Legacy files |
| [05_cross_references](#05_cross_references) | Integration docs | 5 | New | This index |

---

## 01_ontology

### consolidated/ (6 files, 4,314 lines)

Conceptual model documentation - HVDC Core Ontology consolidated into 6 categories.

| File | Lines | Description |
|------|-------|-------------|
| `CONSOLIDATED-01-core-framework-infra.md` | 1,309 | Core logistics framework and infrastructure nodes |
| `CONSOLIDATED-02-warehouse-flow.md` | 991 | Warehouse operations and Flow Code v3.5 algorithm |
| `CONSOLIDATED-03-document-ocr.md` | 1,125 | Document Guardian and OCR pipeline |
| `CONSOLIDATED-04-barge-bulk-cargo.md` | 331 | Barge operations and bulk cargo handling |
| `CONSOLIDATED-05-invoice-cost.md` | 434 | Invoice verification and cost management |
| `README.md` | 124 | Consolidation overview and usage guide |

**Key Features**:
- Flow Code v3.5 (0-5) algorithm documented
- SHACL validation rules for each domain
- Cross-domain relationships and dependencies
- Operational guidelines and best practices

**Related Files**:
- TTL Schemas: `02_schemas/core/` → Formal implementations
- TTL Data: `03_data/ttl/current/hvdc_status_v35.ttl` → Flow Code instances
- JSON Analytics: `03_data/json/gpt_cache/cases_by_flow.json` → Statistics

---

## 02_schemas

### core/ (5 files, 1,028 lines)

RDF/OWL ontology definitions - formal semantic web models.

| File | Lines | Key Classes | Purpose |
|------|-------|-------------|---------|
| `hvdc_event_schema.ttl` | 175 | StockEvent, TransportEvent | Event tracking |
| `hvdc_nodes.ttl` | 214 | Warehouse, Site, MOSB, Port | Location infrastructure |
| `hvdc_ontology.ttl` | 191 | Party, Asset, Document, Process | Core concepts |
| `flow_code.ttl` | 209 | FlowCode, LogisticsFlow | Flow Code v3.5 |
| `2_EXT-03-hvdc-comm-email-enhanced.ttl` | 239 | CommunicationEvent, Email | Communication ontology |

**Related Files**:
- Documentation: `01_ontology/consolidated/` → Conceptual models
- Shapes: `02_schemas/shapes/` → Validation constraints
- Data: `03_data/ttl/current/` → Instances

### shapes/ (4 files, 268 lines)

SHACL shape constraints - data validation rules.

| File | Lines | Constraints | Purpose |
|------|-------|-------------|---------|
| `FlowCode.shape.ttl` | 89 | FlowCode 0-5, AGI/DAS rules | Flow Code validation |
| `ShipmentOOG.shape.ttl` | 56 | Out-of-gauge dimensions | OOG cargo validation |
| `Shipment.shape.ttl` | 78 | General shipment rules | Shipment validation |
| `shacl_shapes.ttl` | 45 | Combined constraints | Unified validation |

**Related Files**:
- Documentation: `01_ontology/consolidated/CONSOLIDATED-02` (Lines 486-537) → SHACL rules
- Schemas: `02_schemas/core/` → Classes being validated
- Validation: `03_data/json/validation/` → Validation reports

---

## 03_data

### ttl/current/ (1 file, 9,844 lines) ⭐

**`hvdc_status_v35.ttl`** - Latest Flow Code v3.5 data

- **Instances**: 9,795+ cases
- **Classes**: Case, StockEvent, TransportEvent
- **Flow Codes**: 0-5 distribution
  - Flow 0 (Pre Arrival): 2.4%
  - Flow 1 (Port→Site): 1.6%
  - Flow 2 (Port→WH→Site): 34.9%
  - Flow 3 (Port→MOSB→Site): 21.5%
  - Flow 4 (Port→WH→MOSB→Site): 35.6%
  - Flow 5 (Mixed/Incomplete): 4.0%

**Properties**:
- `hvdc:hasFlowCode` - 9,795 (100%)
- `hvdc:hasFlowCodeOriginal` - 9,795 (100%)
- `hvdc:hasFlowDescription` - 9,795 (100%)
- `hvdc:hasInboundEvent` - 6,823 (69.7%)

**Related Files**:
- Schema: `02_schemas/core/flow_code.ttl` → Class definitions
- Validation: `02_schemas/shapes/FlowCode.shape.ttl` → Constraints
- Analytics: `03_data/json/gpt_cache/cases_by_flow.json` → Statistics

### ttl/finalized/ (2 files, 92,778 lines)

| File | Lines | Description |
|------|-------|-------------|
| `lightning_final.ttl` | 48,156 | Lightning project finalized data |
| `abu_final.ttl` | 44,622 | Abu Dhabi project finalized data |

### ttl/specialized/ (15 files, 326,175 lines)

Project-specific TTL instances:
- **Lightning**: 5 files (lightning_*.ttl)
- **Abu Dhabi**: 4 files (abu_*.ttl)
- **Invoices**: 3 files (invoice_*.ttl)
- **Sheet extracts**: 3 files (sheet_*.ttl)

### json/validation/ (5 files, 103 lines)

Quality assurance reports:
- `validation_summary.json` - Overall validation results
- `flow_event_patterns.json` - Flow event analysis
- `event_coverage_stats.json` - Event coverage metrics
- `human_gate_missing_dates.json` - Missing date issues
- `human_gate_flow23_no_inbound.json` - Flow 2/3 validation

### json/gpt_cache/ (3 files, 544 lines)

Pre-computed aggregations for GPT queries:
- `cases_by_flow.json` - Flow Code distribution
- `vendor_summary.json` - Vendor statistics
- `monthly_warehouse_inbound.json` - Warehouse inbound trends

**Usage**: MCP server uses these for fast GPT responses.

### json/integration/ (10 files, 11,265 lines)

Network integration data:
- `unified_network_data_v12_hvdc.json` - Main network data
- `unified_network_stats_v12_hvdc.json` - Network statistics
- `unified_network_meta_v12_hvdc.json` - Metadata
- `integration_data_meaningful.json` - Filtered meaningful data
- `abu_lightning_comparison_data.json` - Project comparison
- + 5 more integration files

### json/reports/ (18 files, 53,076 lines)

Analysis reports:
- **Lightning**: 6 analysis files (enhancement, enrichment, whatsapp)
- **Abu Dhabi**: 10 analysis files (comprehensive, LPO, whatsapp, etc.)
- **Tag dictionary**: 1 file (abu_dhabi_logistics_tag_dict_v1.json)

---

## 04_archive

Historical versions preserved for version control and reference.

### ttl/ (9 files, 149,677 lines)

Legacy TTL files from:
- `archive/legacy/mcp_v1.0/` - MCP v1.0 schemas and data
- `archive/legacy/mcp_v2.0/` - MCP v2.0 data
- `archive/legacy/event_ontology/` - Event ontology snapshots
- `archive/legacy/logiontology_v2.0.0_initial/` - Initial v2.0 configs

### json/ (14 files, 257,908 lines)

Legacy JSON analytics from:
- `archive/legacy/mcp_v1.0/` - Test results and sample outputs
- `archive/legacy/event_ontology/` - Output snapshots
- `archive/output_history/rdf_output_legacy/` - Historical RDF outputs
- `archive/legacy/logiontology_v2.0.0_initial/` - Initial test fixtures

---

## 05_cross_references

Integration documentation providing navigation and traceability.

| File | Purpose |
|------|---------|
| `MASTER_INDEX.md` | This file - complete inventory |
| `ONTOLOGY_COVERAGE_MATRIX.md` | Docs ↔ Schemas ↔ Data mapping |
| `FLOW_CODE_LINEAGE.md` | Flow Code v3.5 traceability |
| `QUERY_TEMPLATES.md` | SPARQL query examples |
| `USAGE_GUIDE.md` | How to navigate and use the hub |

---

## File Relationships

### Conceptual → Formal → Operational

```
01_ontology/consolidated/
    ├─ CONSOLIDATED-01 → 02_schemas/core/hvdc_ontology.ttl
    ├─ CONSOLIDATED-02 → 02_schemas/core/flow_code.ttl + shapes/FlowCode.shape.ttl
    ├─ CONSOLIDATED-03 → 02_schemas/core/hvdc_ontology.ttl (LDG classes)
    ├─ CONSOLIDATED-04 → 03_data/ttl/specialized/abu_*.ttl
    └─ CONSOLIDATED-05 → 03_data/ttl/specialized/invoice_*.ttl
                            ↓
                        03_data/ttl/current/hvdc_status_v35.ttl
                            ↓
                    03_data/json/gpt_cache/cases_by_flow.json
```

### Validation Flow

```
02_schemas/shapes/FlowCode.shape.ttl
    ↓ (validates)
03_data/ttl/current/hvdc_status_v35.ttl
    ↓ (generates)
03_data/json/validation/validation_summary.json
```

---

## Quick Access Guide

### I want to...

**Understand the ontology**: Start with `01_ontology/consolidated/README.md`

**Query Flow Code data**: Use `03_data/ttl/current/hvdc_status_v35.ttl` + SPARQL

**View validation results**: Check `03_data/json/validation/`

**Run pre-computed statistics**: Load `03_data/json/gpt_cache/`

**Find specific classes**: Search in `02_schemas/core/` + `05_cross_references/ONTOLOGY_COVERAGE_MATRIX.md`

**Cross-reference concepts**: Use `05_cross_references/FLOW_CODE_LINEAGE.md`

**See example queries**: Browse `05_cross_references/QUERY_TEMPLATES.md`

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-31 | 1.0 | Initial hub creation, 92 files consolidated |
| | | Flow Code v3.5 integration complete |
| | | OCR KPI hardening applied (EntityMatch ≥0.98) |

---

## Maintenance

### Updating Files

1. **Ontology docs**: Update in `01_ontology/consolidated/`, verify schemas match
2. **TTL schemas**: Update in `02_schemas/`, regenerate data if needed
3. **TTL data**: Update `03_data/ttl/current/`, run validation
4. **JSON analytics**: Regenerate from latest TTL data

### Adding New Files

Follow existing directory structure and update this index.

### Sync with Sources

Original files remain in source locations:
- `core_consolidated/` → `01_ontology/consolidated/`
- `logiontology/configs/ontology/` → `02_schemas/core/`
- `output/` → `03_data/ttl/current/` and `03_data/json/`
- `archive/legacy/` → `04_archive/`

---

**For detailed usage instructions, see**: `05_cross_references/USAGE_GUIDE.md`

