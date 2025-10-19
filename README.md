# LogiOntology - HVDC 물류 온톨로지 시스템

HVDC 프로젝트의 물류 데이터를 온톨로지 기반으로 관리하고 분석하는 시스템입니다.

## 🏗️ 프로젝트 구조

```
logi_ontol/
├── logiontology/           # 새로운 모던 구조 (권장)
│   ├── logiontology/       # 핵심 모듈
│   │   ├── mapping/        # 온톨로지 매핑
│   │   ├── validation/     # 스키마 검증
│   │   ├── ingest/         # 데이터 수집
│   │   ├── rdfio/          # RDF 입출력
│   │   ├── reasoning/      # AI 추론
│   │   └── pipeline/       # 파이프라인
│   ├── tests/              # 테스트
│   ├── configs/            # 설정 파일
│   └── .github/            # CI/CD
├── archive/                # 레거시 코드 아카이브
│   ├── python_files_backup/
│   └── tests_backup/
└── ARCHIVE/               # 기존 아카이브
    ├── duplicates/        # 중복 파일들
    └── legacy/           # 레거시 파일들
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

## 🔧 사용법

### 새로운 구조 (권장)

```python
from logiontology.mapping.registry import MappingRegistry
from logiontology.ingest.excel import convert_excel_to_rdf

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
pytest --cov=logiontology

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

- [API 문서](logiontology/README.md)
- [개발자 가이드](logiontology/Cursor_Project_Setup_v1.3.md)
- [종합 분석 보고서](python_files_comprehensive_analysis_report.md)

## 🤝 기여

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🔄 마이그레이션 상태

- ✅ **완료**: 중복 파일 정리, 핵심 모듈 마이그레이션
- 🚧 **진행중**: 테스트 커버리지 확대, 성능 최적화
- 📋 **예정**: 대시보드 개발, 사용자 교육

---

**개발**: MACHO-GPT v3.4-mini Analysis Engine  
**프로젝트**: HVDC Samsung C&T Logistics & ADNOC·DSV Partnership