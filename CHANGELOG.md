# Changelog

## [2.0.0] - 2025-10-18

### Changed
- Reorganized 52 files into 26 active + 26 archived
- All files preserved in ARCHIVE/ folder (no deletions)
- Structured directory layout with categories

### Archived (ARCHIVE/)
- 5x ontology_mapper_*.py → ARCHIVE/duplicates/mapper/
- 2x RDF analyzer variants → ARCHIVE/duplicates/analyzers/
- 17x legacy files → ARCHIVE/legacy/
- 1x test duplicate → ARCHIVE/duplicates/tests/
- 1x old test_inference → ARCHIVE/old_versions/

### Added
- Git version control with tags
- ARCHIVE/ with full metadata and recovery docs
- README.md with project overview
- examples/ and migrations/ directories
- .gitignore for Python projects

### Migration Guide
- Import paths unchanged for active files
- Archived files recoverable anytime
- See ARCHIVE/README.md for recovery procedures

## [1.0.0] - Legacy
- Initial 52-file structure

