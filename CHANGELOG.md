# Changelog

## [2.1.0] - 2025-01-19

### 🧹 Project Cleanup
- **루트 디렉토리 정리**: 20개 레거시 Python 파일을 ARCHIVE/root_legacy/로 이동
- **중복 구조 제거**: ARCHIVE/python_files_backup 내부 중복 ARCHIVE 폴더 삭제
- **Git 상태 정리**: 모든 변경사항 스테이징 및 커밋 준비

### 📦 Archived Files (ARCHIVE/root_legacy/)
- `_schema_validator.py` - 스키마 검증기 (레거시)
- `full_data_ontology_mapping.py` - 전체 데이터 온톨로지 매핑
- `hvdc_enhanced_ontology_with_invoice.py` - HVDC 향상된 온톨로지 (송장 포함)
- `hvdc_excel_to_rdf_converter.py` - HVDC Excel to RDF 변환기
- `hvdc_ontology_engine_v2.py` - HVDC 온톨로지 엔진 v2
- `hvdc_ontology_engine.py` - HVDC 온톨로지 엔진 v1
- `hvdc_ontology_pipeline.py` - HVDC 온톨로지 파이프라인
- `hvdc_rdf_analyzer.py` - HVDC RDF 분석기
- `hvdc_simple_rdf_converter.py` - HVDC 간단 RDF 변환기
- `inference.py` - 추론 엔진
- `knowledge.py` - 지식 베이스
- `logi_master_ontology.py` - 물류 마스터 온톨로지
- `lowlevel.py` - 저수준 함수들
- `ontology_mapper.py` - 온톨로지 매퍼 (v2.6)
- `ontology_reasoning_engine.py` - 온톨로지 추론 엔진
- `ontology.py` - 온톨로지 핵심
- `real_data_ontology_mapping.py` - 실제 데이터 온톨로지 매핑
- `schema_validator.py` - 스키마 검증기
- `tools_ontology_mapper.py` - 온톨로지 매퍼 도구
- `tools_validate_yaml_ontology.py` - YAML 온톨로지 검증 도구
- `validate_ontology.py` - 온톨로지 검증

### 📚 Documentation Updates
- **ARCHIVE/README.md**: 아카이브 구조 및 복원 방법 상세 설명
- **루트 README.md**: 프로젝트 상태 섹션 추가, 정리 후 구조 반영
- **프로젝트 구조**: v2.0으로 업데이트, 정리 완료 상태 명시

### 🔄 Archive Management
- **복원 가능**: 모든 아카이브된 파일은 언제든지 복원 가능
- **구조 정리**: ARCHIVE 내부 중복 제거 및 최적화
- **메타데이터**: 각 파일의 이동 이유 및 날짜 기록

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

