# HVDC Core Ontology - Consolidated Documentation

## Overview

This directory contains consolidated versions of the HVDC Core Ontology documentation, merging related concepts into comprehensive documents for better understanding and maintenance.

### 6 Categories

이 디렉토리는 6개 카테고리로 구성됩니다:
1. 코어 (Core Framework & Infrastructure)
2. 창고 (Warehouse Operations & Flow Code)
3. 문서 (Document Guardian & OCR)
4. 바지선 운영 및 벌크화물 (Barge & Bulk Cargo Operations)
5. 청구서 (Invoice & Cost Management)
6. 기타 (Reserved for future extensions)

## File Mapping

| Consolidated File | Original Files | Description |
|------------------|----------------|-------------|
| `CONSOLIDATED-01-core-framework-infra.md` | `1_CORE-01-hvdc-core-framework.md`<br>`1_CORE-02-hvdc-infra-nodes.md` | Core logistics framework and infrastructure nodes |
| `CONSOLIDATED-02-warehouse-flow.md` | `1_CORE-03-hvdc-warehouse-ops.md`<br>`1_CORE-08-flow-code.md` | Warehouse operations and flow code algorithms |
| `CONSOLIDATED-03-document-ocr.md` | `1_CORE-06-hvdc-doc-guardian.md`<br>`1_CORE-07-hvdc-ocr-pipeline.md` | Document guardian and OCR pipeline |
| `CONSOLIDATED-04-barge-bulk-cargo.md` | `1_CORE-05-hvdc-bulk-cargo-ops.md` | Barge operations and bulk cargo handling |
| `CONSOLIDATED-05-invoice-cost.md` | `1_CORE-04-hvdc-invoice-cost.md` | Invoice verification and cost management |

## Content Preservation

All consolidated files maintain the complete content from their original sources:

- **YAML Front Matter**: Combined metadata from source files
- **Part Structure**: Clear separation between original file contents
- **Source Attribution**: Each section includes source file information
- **Cross-References**: Internal links updated for consolidated structure
- **Ontology Definitions**: Complete RDF/OWL/SHACL definitions preserved

## Usage

### For Developers
- Use consolidated files for comprehensive understanding of related concepts
- Reference original files for specific implementation details
- Cross-reference between consolidated files for system-wide understanding

### For Documentation
- Consolidated files provide complete context for each domain
- Source file references maintain traceability
- Table of Contents provides quick navigation

## Verification

### Line Count Verification
Current consolidated files (as of 2025-10-31):

- `CONSOLIDATED-01`: 1,309 lines (Core Framework + Infrastructure)
- `CONSOLIDATED-02`: 991 lines (Warehouse + Flow Code v3.5)
- `CONSOLIDATED-03`: 1,125 lines (Document Guardian + OCR Pipeline)
- `CONSOLIDATED-04`: 331 lines (Bulk Cargo Operations)
- `CONSOLIDATED-05`: 434 lines (Invoice & Cost Management)
- **Total**: 4,190 lines

### Content Integrity
- All original content preserved
- No information loss during consolidation
- Proper attribution maintained
- Cross-references updated

## Original File References

### Core Framework & Infrastructure
- **Source**: `core/1_CORE-01-hvdc-core-framework.md`
- **Source**: `core/1_CORE-02-hvdc-infra-nodes.md`
- **Consolidated**: `CONSOLIDATED-01-core-framework-infra.md`

### Warehouse Operations & Flow Codes
- **Source**: `core/1_CORE-03-hvdc-warehouse-ops.md`
- **Source**: `core/1_CORE-08-flow-code.md`
- **Consolidated**: `CONSOLIDATED-02-warehouse-flow.md`

### Document Guardian & OCR Pipeline
- **Source**: `core/1_CORE-06-hvdc-doc-guardian.md`
- **Source**: `core/1_CORE-07-hvdc-ocr-pipeline.md`
- **Consolidated**: `CONSOLIDATED-03-document-ocr.md`

### Barge Operations & Bulk Cargo
- **Source**: `core/1_CORE-05-hvdc-bulk-cargo-ops.md`
- **Consolidated**: `CONSOLIDATED-04-barge-bulk-cargo.md`

### Invoice & Cost Management
- **Source**: `core/1_CORE-04-hvdc-invoice-cost.md`
- **Consolidated**: `CONSOLIDATED-05-invoice-cost.md`

## Maintenance

### Updates
- Update consolidated files when source files change
- Maintain source attribution and version information
- Update cross-references as needed

### Version Control
- Track changes to both source and consolidated files
- Maintain consistency between versions
- Document consolidation rationale

## Standards Compliance

All consolidated files maintain compliance with:
- **RDF/OWL**: Semantic web standards
- **SHACL**: Shape constraint validation
- **SPARQL**: Query language support
- **JSON-LD**: Linked data serialization
- **Turtle**: RDF serialization format

## KPI Gate Change History

### EntityMatch Threshold Update (2025-10-31)
- **Previous**: ≥ 0.90
- **Current**: ≥ 0.98
- **Reason**: Alignment with conservative operational guidelines for entity matching accuracy
- **Impact**: Stricter OCR quality gate, increased ZERO-fail-safe triggers
- **Related Files**: CONSOLIDATED-03-document-ocr.md (SHACL rule, policy table)

## Contact

For questions about consolidation or content updates, refer to the original source files or contact the HVDC project team.
