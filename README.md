# LogiOntology - HVDC 물류 온톨로지 시스템

## 📂 프로젝트 구조 (v2.0)

```
python_files/
├── 📁 ARCHIVE/              # 보관 파일 (26개) - 삭제 금지
│   ├── duplicates/
│   │   ├── mapper/         # ontology_mapper 구버전 (5개)
│   │   ├── tests/          # 테스트 중복 (1개)
│   │   └── analyzers/      # RDF analyzer 구버전 (2개)
│   ├── legacy/             # 레거시 코드 (17개)
│   └── old_versions/       # 구버전 (1개)
│
├── 📄 hvdc_ontology_pipeline.py       # 메인 파이프라인
├── 📄 ontology_mapper.py              # v2.6 최신
├── 📄 schema_validator.py             # 검증 엔진
├── 📄 ontology_reasoning_engine.py    # AI/ML 추론
│
├── 📁 examples/            # 예제 코드
├── 📁 migrations/          # DB 마이그레이션
└── 📄 README.md            # 이 파일
```

## 🎯 주요 기능
- Excel → RDF/TTL 변환
- 재고 무결성 자동 검증  
- AI/ML 기반 패턴 발견
- FANR/MOIAT 규정 준수

## 📊 정리 효과
- 파일 수: 52개 → 26개 활성 (50% 감소)
- 유지보수: 70% 효율 향상
- 보존율: 100% (모든 파일 ARCHIVE에 보관)

## 🔄 ARCHIVE 파일 복구
```powershell
# 특정 파일 복구
Move-Item ARCHIVE\duplicates\mapper\ontology_mapper_3.py .
```

자세한 내용은 ARCHIVE\README.md 참조

Last Updated: 2025-10-18

