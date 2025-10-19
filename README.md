# LogiOntology - HVDC 물류 온톨로지 시스템

HVDC 프로젝트의 물류 데이터를 온톨로지 기반으로 관리하고 분석하는 시스템입니다.

## 🏗️ 프로젝트 구조 (v3.0 - 시스템 폴더 재정리 완료)

```
logi_ontol/
├── logiontology/           # 🚀 메인 패키지 (활성 개발)
│   ├── src/                # 소스 코드
│   │   ├── core/           # 핵심 모델 및 계약
│   │   ├── mapping/        # 온톨로지 매핑 (v2.6)
│   │   ├── validation/     # 스키마 검증
│   │   ├── ingest/         # 데이터 수집 (Excel)
│   │   ├── rdfio/          # RDF 입출력
│   │   ├── reasoning/      # AI 추론
│   │   └── pipeline/       # 파이프라인
│   ├── tests/              # 테스트 (95% 커버리지)
│   │   ├── unit/           # 단위 테스트
│   │   ├── integration/    # 통합 테스트
│   │   └── fixtures/       # 테스트 데이터
│   ├── configs/            # 설정 파일
│   ├── docs/               # 패키지 문서
│   └── .github/            # CI/CD
├── scripts/                # 실행 스크립트
│   └── process_hvdc_excel.py
├── data/                   # 입력 데이터
│   └── *.xlsx
├── output/                 # 출력 결과
│   └── *.ttl
├── reports/                # 보고서
│   ├── WORK_SUMMARY.md
│   ├── PROJECT_CLEANUP_REPORT.md
│   └── HVDC_PROCESSING_REPORT.md
├── examples/               # 예제 코드
├── archive/                # 통합 아카이브
│   ├── root_legacy/        # 루트 레거시 파일들
│   ├── duplicates/         # 중복 파일들
│   ├── legacy/             # 기존 레거시 파일들
│   └── logiontology_archive/ # 패키지 아카이브
├── docs/                   # 프로젝트 문서
├── README.md               # 이 파일
├── CHANGELOG.md            # 변경 이력
└── requirements.txt        # 의존성
```

## 🚀 주요 기능

- **Excel → RDF 변환**: HVDC 데이터를 표준 RDF/TTL 형식으로 변환
- **재고 무결성 검증**: 자동 재고 계산 검증 (Opening + In - Out = Closing)
- **AI/ML 기반 패턴 발견**: Decision Tree, Random Forest를 통한 비즈니스 규칙 추론
- **FANR/MOIAT 규정 준수**: 자동 규정 준수 검증
- **실시간 KPI 모니터링**: 물류 지표 실시간 추적

## 📦 설치

```bash
# 1. 저장소 클론
git clone https://github.com/macho715/logi_ontol.git
cd logi_ontol

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 개발 모드 설치 (새 구조)
cd logiontology
pip install -e ".[dev]"
```

## 🚀 빠른 시작

### 스크립트 실행
```bash
# HVDC Excel 파일 처리
python scripts/process_hvdc_excel.py

# 개발 모드 설치 후 CLI 사용
cd logiontology
pip install -e ".[dev]"
logiontology --help
```

## 🔧 사용법

### 새로운 구조 (권장)

```python
from logiontology.src.mapping.registry import MappingRegistry
from logiontology.src.ingest.excel import convert_excel_to_rdf

# Excel 파일을 RDF로 변환
rdf_path = convert_excel_to_rdf("data/warehouse_data.xlsx")

# 매핑 규칙 로드
mapper = MappingRegistry()
mapper.load("configs/mapping_rules.v2.6.yaml")
```

### 레거시 코드

```python
# 기존 방식 (호환성 유지)
from ontology_mapper import dataframe_to_rdf
from schema_validator import SchemaValidator

# DataFrame을 RDF로 변환
df = pd.read_excel("data.xlsx")
rdf_path = dataframe_to_rdf(df, "output.ttl")
```

## 📊 데이터 플로우

```
Excel 파일 (HVDC WAREHOUSE_*.xlsx)
    ↓
EnhancedDataLoader.load_and_process_files()
    • 파일 패턴 매칭 (HITACHI*/SIMENSE*)
    • 시트 선택 (Case List 우선)
    ↓
EnhancedTransactionEngine.create_transaction_log()
    • IN 트랜잭션 생성
    • OUT 트랜잭션 생성 (TRANSFER_OUT/FINAL_OUT)
    ↓
apply_hvdc_filters_to_rdf()
    • HVDC CODE 정규화
    • 벤더 필터 (HE/SIM)
    • 월 매칭 검증
    ↓
dataframe_to_rdf()
    • TransportEvent URI 생성
    • 프로퍼티 매핑 (mapping_rules)
    • XSD 데이터 타입 적용
    ↓
RDF/TTL 파일 출력
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src

# 특정 모듈 테스트
pytest tests/test_mapping.py
```

## 📈 성능 최적화

- **Excel 로드**: 청크 단위 처리 (15초 → 5초)
- **벡터화 연산**: 중첩 루프 제거 (20초 → 5초)
- **병렬 처리**: 4배 속도 향상
- **메모리 최적화**: 데이터 타입 최적화 (500MB → 200MB)

## 🔒 보안 및 규정 준수

- **FANR**: Federal Authority for Nuclear Regulation 검증
- **MOIAT**: Ministry of Industry and Advanced Technology 검증
- **IMO**: International Maritime Organization 안전 한계 검증
- **Confidence 기반 품질 관리**: ≥0.95 for critical fields

## 📚 문서

- [패키지 문서](logiontology/docs/README.md)
- [시스템 아키텍처](logiontology/docs/ARCHITECTURE.md)
- [개발자 가이드](logiontology/Cursor_Project_Setup_v1.3.md)
- [종합 분석 보고서](reports/python_files_comprehensive_analysis_report.md)

## 🤝 기여

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📊 프로젝트 상태 (2025-10-19)

### ✅ 정리 완료 (v3.0)
- **시스템 폴더 재정리**: logiontology/logiontology/ → logiontology/src/ 현대화
- **디렉토리 체계화**: scripts/, data/, reports/, docs/ 역할별 분리
- **아카이브 통합**: 단일 archive/ 디렉토리로 통합 (ARCHIVE → archive)
- **테스트 커버리지**: 95% 달성 (152개 테스트)
- **Git 상태**: 깨끗한 상태 유지

### 🚀 활성 개발 영역
- **logiontology/src/**: 현대적 src/ 구조
- **테스트**: 단위/통합 테스트 완비 (95% 커버리지)
- **문서**: 체계화된 문서 구조
- **스크립트**: 실행 가능한 스크립트 제공

### 📦 아카이브 보관
- **archive/**: 통합된 아카이브 디렉토리
  - **root_legacy/**: 루트에서 이동한 20개 파일
  - **duplicates/**: 중복 파일들
  - **legacy/**: 기존 레거시 파일들
  - **logiontology_archive/**: 패키지 아카이브
  - **migrations/**: 데이터베이스 마이그레이션
- **복원 가능**: 언제든지 복원 가능

## 🔄 마이그레이션 상태

- ✅ **완료**: 시스템 폴더 재정리, 디렉토리 체계화, 아카이브 통합
- ✅ **완료**: 테스트 커버리지 95% 달성, import 경로 현대화
- ✅ **완료**: 문서 체계화, 스크립트 실행 환경 구축
- 🚧 **진행중**: 성능 최적화, CLI 모듈 테스트
- 📋 **예정**: 대시보드 개발, 사용자 교육

---

**개발**: MACHO-GPT v3.4-mini Analysis Engine
**프로젝트**: HVDC Samsung C&T Logistics & ADNOC·DSV Partnership
