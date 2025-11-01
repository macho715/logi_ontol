# Ontology Coverage Matrix

**Purpose**: Maps conceptual documentation (MD) → formal schemas (TTL) → operational data (TTL instances) → analytics (JSON)

**Last Updated**: 2025-10-31

---

## Complete Mapping Table

| Ontology Doc | Lines | TTL Schema Files | TTL Data Files | JSON Analytics Files | Description | Key Classes/Concepts |
|--------------|-------|------------------|----------------|---------------------|-------------|---------------------|
| **CONSOLIDATED-01** | 1,309 | `hvdc_ontology.ttl`<br>`hvdc_nodes.ttl` | `hvdc_status_v35.ttl`<br>`lightning_final.ttl`<br>`abu_final.ttl` | `integration/unified_network_*.json` | Core framework, infrastructure nodes | Party, Asset, Document, Process, Location, Warehouse, Site, MOSB, Port |
| **CONSOLIDATED-02** | 991 | `flow_code.ttl`<br>`FlowCode.shape.ttl` | `hvdc_status_v35.ttl` | `gpt_cache/cases_by_flow.json`<br>`validation/flow_event_patterns.json` | Warehouse operations, Flow Code v3.5 | FlowCode, LogisticsFlow, TransportEvent, StockEvent, AGI/DAS domain rules |
| **CONSOLIDATED-03** | 1,125 | `hvdc_ontology.ttl`<br>`shacl_shapes.ttl` | `hvdc_status_v35.ttl`<br>`specialized/invoice_*.ttl` | `validation/validation_summary.json`<br>`reports/invoice_*.json` | Document Guardian, OCR pipeline, trust layer | LDG Document, Metric, Audit, TrustLayer, OCR KPI gates (MeanConf≥0.92, TableAcc≥0.98, EntityMatch≥0.98) |
| **CONSOLIDATED-04** | 331 | `hvdc_ontology.ttl`<br>`Shipment.shape.ttl`<br>`ShipmentOOG.shape.ttl` | `abu_*.ttl`<br>`sheet_*.ttl` | `reports/abu_*.json` | Barge operations, bulk cargo handling | Barge, BulkCargo, OOG Shipment, IMSBC compliance |
| **CONSOLIDATED-05** | 434 | `hvdc_ontology.ttl` | `specialized/invoice_*.ttl` | `reports/invoice_*.json` | Invoice verification, cost management | Invoice, InvoiceLineItem, CostGuard, DeltaPercent, FX=3.6725, PRISM.KERNEL |

---

## Detailed Mapping

### CONSOLIDATED-01: Core Framework & Infrastructure

**Document Section**: Lines 1-1,309
**Purpose**: Core logistics framework and infrastructure nodes

**TTL Schema Files**:

| File | Lines | Key Classes | Key Properties |
|------|-------|-------------|----------------|
| `hvdc_ontology.ttl` | 191 | Party, Asset, Document, Process, Event, Contract, Regulation, Location, KPI | hasDocument, references, involves, locatedAt, governs, measuredBy |
| `hvdc_nodes.ttl` | 214 | Warehouse, Site, OffshoreBase (MOSB), Port, Node | operatesFrom, dispatches, consolidates, handles |

**TTL Data Instances**:

| File | Triples | Coverage |
|------|---------|----------|
| `hvdc_status_v35.ttl` | ~50,000 | 100% cases have hvdc:Vendor (Party) |
| `lightning_final.ttl` | ~200,000 | Full network with lightning entities |
| `abu_final.ttl` | ~180,000 | Full network with Abu Dhabi entities |

**JSON Analytics**:

| File | Content | Description |
|------|---------|-------------|
| `unified_network_data_v12_hvdc.json` | Network graph data | Complete node and edge structure |
| `unified_network_stats_v12_hvdc.json` | Statistics | Node/edge counts, centrality metrics |
| `unified_network_meta_v12_hvdc.json` | Metadata | Provenance, version info |

---

### CONSOLIDATED-02: Warehouse & Flow Code ⭐

**Document Section**: Lines 1-991
**Purpose**: Warehouse operations and Flow Code v3.5 algorithm

**TTL Schema Files**:

| File | Lines | Key Concepts |
|------|-------|--------------|
| `flow_code.ttl` | 209 | FlowCode enum 0-5, LogisticsFlow class, FlowCode calculation rules |
| `FlowCode.shape.ttl` | 89 | SHACL constraints for Flow 0-5, AGI/DAS ban rules, Flow 5 detection |

**Flow Code v3.5 Mapping**:

| Flow Code | TTL Value | Documentation | TTL Schema | Data Instances | SHACL Validation |
|-----------|-----------|---------------|------------|----------------|------------------|
| **0** (Pre Arrival) | `xsd:string "0"` | Lines 62-64 | flow_code.ttl L45 | hvdc_status_v35.ttl | FlowCode.shape.ttl L12 |
| **1** (Port→Site) | `xsd:string "1"` | Lines 66-68 | flow_code.ttl L50 | 156 cases (1.6%) | FlowCode.shape.ttl L20 |
| **2** (Port→WH→Site) | `xsd:string "2"` | Lines 70-72 | flow_code.ttl L55 | 3,421 cases (34.9%) | FlowCode.shape.ttl L28 |
| **3** (Port→MOSB→Site) | `xsd:string "3"` | Lines 74-76 | flow_code.ttl L60 | 2,109 cases (21.5%) | FlowCode.shape.ttl L36 |
| **4** (Port→WH→MOSB→Site) | `xsd:string "4"` | Lines 78-80 | flow_code.ttl L65 | 3,487 cases (35.6%) | FlowCode.shape.ttl L44 |
| **5** (Mixed/Incomplete) | `xsd:string "5"` | Lines 82-89 | flow_code.ttl L70 | 388 cases (4.0%) | FlowCode.shape.ttl L52 |

**AGI/DAS Domain Rules**:

| Rule | Documentation | TTL Schema | SHACL Validation | Data Impact |
|------|---------------|------------|------------------|-------------|
| AGI/DAS Flow-1 Ban | Lines 486-506 | FlowCode.shape.ttl L62 | AGIDASFlow1BanShape | Blocks Flow 1 for AGI/DAS |
| AGI/DAS Flow 0/1/2 → 3 Override | Lines 253-261 | flow_code.ttl L75 | Auto-applied | Override reason tracked |
| Flow 5 Detection | Lines 506-537 | FlowCode.shape.ttl L84 | Flow5ExceptionDetectionShape | Requires override reason |

**TTL Data Instances**:

| File | Instances | Flow Distribution |
|------|-----------|-------------------|
| `hvdc_status_v35.ttl` | 9,795 cases | Complete Flow 0-5 distribution |
| 7,807 cases have AGI/DAS Final_Location |  | Subject to MOSB leg requirement |

**JSON Analytics**:

| File | Content | Description |
|------|---------|-------------|
| `cases_by_flow.json` | Flow distribution | 6 Flow Code buckets with counts/percentages |
| `flow_event_patterns.json` | Event patterns | WH/MOSB/Site event sequences |

---

### CONSOLIDATED-03: Document Guardian & OCR

**Document Section**: Lines 1-1,125
**Purpose**: Document processing, OCR pipeline, trust validation

**TTL Schema Files**:

| File | Lines | Key Classes | KPI Gates |
|------|-------|-------------|-----------|
| `hvdc_ontology.ttl` | LDG section | LDG Document, Metric, Audit, TrustLayer | MeanConf≥0.92, TableAcc≥0.98, NumericIntegrity=1.00, **EntityMatch≥0.98** |

**OCR KPI Gate Policy**:

| KPI | Threshold | SHACL Rule | Enforcement | Source |
|-----|-----------|------------|-------------|--------|
| MeanConf (평균 신뢰도) | ≥ 0.92 | OCRKPIGateShape | ZERO-fail-safe | Lines 854-880 |
| TableAcc (테이블 정확도) | ≥ 0.98 | OCRKPIGateShape | ZERO-fail-safe | Lines 1108-1111 |
| NumericIntegrity (수치 무결성) | = 1.00 | OCRKPIGateShape | ZERO-fail-safe | Lines 1110 |
| EntityMatch (엔티티 매칭률) | ≥ 0.98 ⭐ | OCRKPIGateShape | ZERO-fail-safe | Lines 1111 |

**Note**: EntityMatch threshold upgraded from 0.90 to 0.98 on 2025-10-31 (see README.md KPI Gate Change History).

**TTL Data Instances**:

| File | Coverage |
|------|----------|
| `hvdc_status_v35.ttl` | Document metadata embedded in Case instances |
| `specialized/invoice_*.ttl` | Invoice OCR results |

**JSON Analytics**:

| File | Content |
|------|---------|
| `validation_summary.json` | OCR quality metrics |
| `reports/invoice_*.json` | Invoice analysis with trust scores |

---

### CONSOLIDATED-04: Barge & Bulk Cargo

**Document Section**: Lines 1-331
**Purpose**: Barge operations, bulk cargo handling, OOG cargo

**TTL Schema Files**:

| File | Lines | Key Classes |
|------|-------|-------------|
| `hvdc_ontology.ttl` | Barge section | Barge, BulkCargo, Shipment, OOG Shipment |
| `Shipment.shape.ttl` | 78 | General shipment constraints |
| `ShipmentOOG.shape.ttl` | 56 | OOG dimension and weight constraints |

**Standards Compliance**:

| Standard | Coverage | TTL Schema | Data Instances |
|----------|----------|------------|----------------|
| IMSBC Code | Bulk cargo classification | hvdc_ontology.ttl | abu_*.ttl, sheet_*.ttl |
| SOLAS | Safety of Life at Sea | hvdc_ontology.ttl | abu_final.ttl |
| OOG Dimensions | Length/width/height limits | ShipmentOOG.shape.ttl | specialized/abu_*.ttl |

**TTL Data Instances**:

| File | Instances | Description |
|------|-----------|-------------|
| `abu_final.ttl` | Complete Abu Dhabi network | Includes barge operations |
| `specialized/abu_*.ttl` (4 files) | ~100K triples | Detailed barge and bulk cargo data |
| `specialized/sheet_*.ttl` (3 files) | ~50K triples | Sheet-based bulk cargo extracts |

**JSON Analytics**:

| File | Content |
|------|---------|
| `reports/abu_comprehensive_summary.json` | Comprehensive Abu Dhabi analysis |
| `reports/abu_lpo_analysis.json` | LPO (Large Project Operations) analysis |
| `reports/abu_guidelines_analysis.json` | Operational guidelines |

---

### CONSOLIDATED-05: Invoice & Cost Management

**Document Section**: Lines 1-434
**Purpose**: Invoice verification, cost guard, PRISM.KERNEL

**TTL Schema Files**:

| File | Lines | Key Classes |
|------|-------|-------------|
| `hvdc_ontology.ttl` | Invoice section | Invoice, InvoiceLineItem, CostGuard |

**Cost Guard Rules**:

| Rule | Value | Documentation | Enforcement |
|------|-------|---------------|-------------|
| Base Currency | USD | Lines 25-29 | Fixed |
| FX Rate | 3.6725 AED/USD | Lines 62-69 | Locked |
| Delta% Band | PASS: ±3%<br>WARN: ±5%<br>CRITICAL: ±8% | Lines 62-69 | SHACL validation |
| Lane Normalization | Standard lanes | Lines 84-90 | Auto-mapping |

**PRISM.KERNEL Format**:

| Component | Description | Example |
|-----------|-------------|---------|
| Recap (5 lines) | Summary with verdict | "INV-2025-001 \| DSV Logistics \| USD 15,000.00 \| Δ% 2.1% \| VERDICT: PASS" |
| Artifact (JSON) | Complete proof data | Line items, rate refs, calculations, proof hash |

**TTL Data Instances**:

| File | Instances |
|------|-----------|
| `specialized/invoice_*.ttl` (3 files) | ~30K triples |
| Invoice LineItems with CostGuard validation |

**JSON Analytics**:

| File | Content |
|------|---------|
| `reports/invoice_analysis_report.json` | Invoice analysis |
| `reports/invoice_data_summary.json` | Invoice statistics |
| `integration_data.json` | Includes invoice metadata |

---

## Cross-Domain Dependencies

### Flow Code → OCR → Invoice

```
CONSOLIDATED-02 (Flow Code)
    ↓ (cases have documents)
CONSOLIDATED-03 (Document OCR)
    ↓ (invoice validation)
CONSOLIDATED-05 (Invoice & Cost)
```

### Framework → Flow → Operations

```
CONSOLIDATED-01 (Core Framework)
    ↓ (defines infrastructure)
CONSOLIDATED-02 (Warehouse Flow)
    ↓ (operates on nodes)
CONSOLIDATED-04 (Barge & Bulk)
```

---

## Validation Coverage

| Validation Type | Source | Target | Files |
|-----------------|--------|--------|-------|
| SHACL Shape | `02_schemas/shapes/` | `03_data/ttl/current/` | All TTL data |
| Flow Code Rules | FlowCode.shape.ttl | hvdc_status_v35.ttl | 9,795 cases |
| OCR KPI Gates | CONSOLIDATED-03 | Invoice TTL files | All invoices |
| Cost Guard Bands | CONSOLIDATED-05 | Invoice TTL files | All invoice line items |

---

## Summary Statistics

| Category | Documentation | TTL Schemas | TTL Data | JSON Analytics | Validation |
|----------|---------------|-------------|----------|----------------|------------|
| Files | 5 consolidated | 9 TTL files | 18 TTL files | 36 JSON files | 5 reports |
| Lines | 4,190 | 1,296 | 428,797 | 65,016 | 103 |
| Coverage | 100% concepts | 100% ontologies | 100% instances | 100% analysis | Continuous |

---

**For implementation details, see**: `05_cross_references/FLOW_CODE_LINEAGE.md`

**For query examples, see**: `05_cross_references/QUERY_TEMPLATES.md`

