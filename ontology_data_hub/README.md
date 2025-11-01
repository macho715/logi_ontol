# HVDC Ontology Data Hub

**Version**: 1.0
**Created**: 2025-10-31
**Total Files**: 92 files | 906,980 lines

---

## Overview

The HVDC Ontology Data Hub provides a unified architecture bridging:

- **Conceptual Layer** (`01_ontology/`): Consolidated documentation (4,314 lines)
- **Schema Layer** (`02_schemas/`): TTL ontology definitions (1,296 lines)
- **Data Layer** (`03_data/`): TTL instances + JSON analytics
- **Archive** (`04_archive/`): Historical versions
- **Cross-References** (`05_cross_references/`): Integration documentation

---

## Quick Access

### Core Documentation

- **Flow Code v3.5**: `01_ontology/consolidated/CONSOLIDATED-02-warehouse-flow.md`
- **Latest Data**: `03_data/ttl/current/hvdc_status_v35.ttl` (755 cases)
- **Statistics**: `03_data/json/gpt_cache/cases_by_flow.json`
- **Full Index**: `05_cross_references/MASTER_INDEX.md`
- **Data Files Guide**: `DATA_FILES_GUIDE.md` (TTL & JSON 파일 설명)

### Key Features

- ✅ **Flow Code v3.5** fully implemented (0-5 classification)
- ✅ **AGI/DAS domain rules** enforced via SHACL
- ✅ **OCR KPI gates** (EntityMatch ≥0.98, TableAcc ≥0.98)
- ✅ **Complete traceability** across all layers
- ✅ **SPARQL-ready** TTL data

---

## Directory Structure

```
ontology_data_hub/
├── 01_ontology/          # Conceptual documentation (6 files)
│   └── consolidated/     # Core consolidated docs
├── 02_schemas/           # RDF/OWL definitions (9 files)
│   ├── core/             # Ontology TTL files
│   └── shapes/           # SHACL constraints
├── 03_data/              # Operational data (36 files)
│   ├── ttl/              # TTL instances
│   │   ├── current/      # Latest (hvdc_status_v35.ttl)
│   │   ├── finalized/    # Finalized projects
│   │   └── specialized/  # Project-specific
│   └── json/             # Analytics & reports
│       ├── validation/   # QA reports
│       ├── gpt_cache/    # Pre-computed stats
│       └── reports/      # Analysis outputs
├── 04_archive/           # Historical versions (23 files)
│   ├── ttl/              # Legacy TTL
│   └── json/             # Legacy JSON
└── 05_cross_references/  # Integration docs (5 files)
    ├── MASTER_INDEX.md
    ├── ONTOLOGY_COVERAGE_MATRIX.md
    ├── FLOW_CODE_LINEAGE.md
    ├── QUERY_TEMPLATES.md
    └── USAGE_GUIDE.md
```

---

## Usage Guide

**For complete usage instructions**: See `05_cross_references/USAGE_GUIDE.md`

**For SPARQL queries**: See `05_cross_references/QUERY_TEMPLATES.md`

**For file inventory**: See `05_cross_references/MASTER_INDEX.md`

**For ontology mappings**: See `05_cross_references/ONTOLOGY_COVERAGE_MATRIX.md`

**For TTL & JSON files**: See `DATA_FILES_GUIDE.md` (한글 가이드)

---

## Key Statistics

| Category | Files | Description |
|----------|-------|-------------|
| Ontology Docs | 6 | Conceptual models (4,314 lines) |
| TTL Schemas | 9 | Formal definitions (1,296 lines) |
| TTL Data | 18 | Instances (~430K lines) |
| JSON Analytics | 36 | Reports & validations |
| Archive | 23 | Historical versions |
| **Total** | **92** | **906,980 lines** |

---

## Integration

### With Existing Systems

- **MCP Server**: Load `03_data/ttl/current/hvdc_status_v35.ttl`
- **RDFLib**: All TTL files compatible
- **SPARQL**: Query any TTL file with standard SPARQL
- **JSON**: Pre-computed analytics for fast access

### Validation

- **SHACL**: All TTL data validated against `02_schemas/shapes/`
- **Flow Code**: Automatic validation via FlowCode.shape.ttl
- **OCR KPI**: Quality gates enforced via SHACL

---

## Maintenance

### Updating Files

1. Update source files in original locations
2. Copy updates to hub (preserves originals)
3. Regenerate JSON analytics if TTL data changes
4. Update cross-reference documentation

### Adding New Files

Follow existing directory structure and update `MASTER_INDEX.md`.

---

## Contact

For questions, see `01_ontology/consolidated/README.md` or `05_cross_references/USAGE_GUIDE.md`.

---

**Note**: All files are copies. Original files remain in their source locations for safety.

