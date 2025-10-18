# ARCHIVE 폴더 가이드

## 📦 보관된 파일: 22개

### 카테고리
- **duplicates/mapper**: 5개 (ontology_mapper 구버전)
- **duplicates/tests**: 1개 (테스트 중복)
- **duplicates/analyzers**: 2개 (RDF analyzer 구버전)
- **legacy**: 17개 (레거시 코드)
- **old_versions**: 1개 (test_inference 구버전)

### 🔒 보안 정책
- ✅ 모든 파일 Git으로 버전 관리
- ✅ 원본 그대로 보존
- ✅ 언제든 복구 가능
- ❌ 절대 삭제 금지

### 📊 통계
- 원본 파일: 52개
- 활성 파일: 26개
- 보관 파일: 26개
- 절감률: 50%

### 🔄 복구 절차
1. 원하는 파일 확인
2. Move-Item으로 원래 위치로 이동
3. Git commit으로 변경 기록

예시:
```powershell
Move-Item ARCHIVE\duplicates\mapper\ontology_mapper_3.py .
git add .
git commit -m "restore: ontology_mapper_3.py from archive"
```

Last Updated: 2025-10-18

