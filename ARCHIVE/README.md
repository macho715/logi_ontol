# LogiOntology Archive

이 디렉토리는 LogiOntology 프로젝트의 정리 과정에서 아카이브된 파일들을 보관합니다.

## 📁 아카이브 구조

```
ARCHIVE/
├── root_legacy/           # 루트 디렉토리에서 이동한 레거시 파일들 (2025-01-19)
├── duplicates/            # 중복 파일들
│   ├── analyzers/         # RDF 분석기 중복 버전들
│   ├── mapper/            # 온톨로지 매퍼 중복 버전들 (1-5)
│   └── tests/             # 테스트 파일 중복
├── legacy/                # 기존 레거시 파일들 (v1 버전들)
├── old_versions/          # 이전 버전들
├── python_files_backup/   # 정리된 Python 파일 백업
├── tests_backup/          # 테스트 파일 백업
└── README.md              # 이 파일
```

## 🔄 복원 방법

### 루트 레거시 파일 복원
```bash
# 특정 파일 복원
cp ARCHIVE/root_legacy/ontology_mapper.py ./

# 모든 루트 레거시 파일 복원
cp ARCHIVE/root_legacy/*.py ./
```

### 중복 파일 확인
```bash
# 중복 파일 목록 확인
find ARCHIVE/duplicates/ -name "*.py" | sort

# 특정 기능의 모든 버전 확인
find ARCHIVE/ -name "*ontology_mapper*" | sort
```

## 📋 아카이브된 파일 목록

### root_legacy/ (2025-01-19 이동)
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

### duplicates/ (기존 중복 파일들)
- `analyzers/` - RDF 분석기 중복 버전들
- `mapper/` - 온톨로지 매퍼 중복 버전들 (1-5)
- `tests/` - 테스트 파일 중복

### legacy/ (기존 레거시 파일들)
- v1 버전들의 모든 파일들

## ⚠️ 주의사항

1. **복원 전 확인**: 복원하려는 파일이 현재 프로젝트와 호환되는지 확인
2. **백업 권장**: 복원 전 현재 상태를 백업
3. **테스트 실행**: 복원 후 테스트 실행으로 정상 동작 확인
4. **의존성 확인**: 복원된 파일의 의존성이 현재 환경에 있는지 확인

## 🔍 파일 검색

```bash
# 특정 기능 관련 파일 찾기
find ARCHIVE/ -name "*mapping*" -type f

# 특정 날짜 이후 파일 찾기
find ARCHIVE/ -newermt "2025-01-01" -type f

# Python 파일만 찾기
find ARCHIVE/ -name "*.py" -type f | wc -l
```

## 📊 아카이브 통계

- **총 파일 수**: 약 100+ 개
- **Python 파일**: 약 80+ 개
- **아카이브 날짜**: 2025-01-19
- **정리 이유**: 프로젝트 구조 개선 및 중복 제거

---

**마지막 업데이트**: 2025-01-19  
**관리자**: MACHO-GPT v3.4-mini