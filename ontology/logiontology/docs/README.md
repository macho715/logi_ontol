# LogiOntology Documentation

## 📚 Documentation Overview

LogiOntology 시스템의 포괄적인 문서 모음입니다. 시스템 아키텍처, 사용법, API 레퍼런스, 그리고 개발자 가이드를 포함합니다.

## 📖 Available Documentation

### 🏗️ Architecture Documentation

| 문서 | 설명 | 상태 |
|------|------|------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 시스템 아키텍처 상세 문서 | ✅ 완료 |
| [ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md) | 아키텍처 다이어그램 (ASCII) | ✅ 완료 |
| [ARCHITECTURE_Mermaid.md](./ARCHITECTURE_Mermaid.md) | Mermaid 다이어그램 | ✅ 완료 |

### 🔧 Technical Documentation

| 문서 | 설명 | 상태 |
|------|------|------|
| [API_REFERENCE.md](./API_REFERENCE.md) | REST API 레퍼런스 | 🚧 진행중 |
| [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) | 개발자 가이드 | 🚧 진행중 |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | 배포 가이드 | 🚧 진행중 |

### 📊 User Documentation

| 문서 | 설명 | 상태 |
|------|------|------|
| [USER_GUIDE.md](./USER_GUIDE.md) | 사용자 가이드 | 🚧 진행중 |
| [TUTORIAL.md](./TUTORIAL.md) | 튜토리얼 | 🚧 진행중 |
| [FAQ.md](./FAQ.md) | 자주 묻는 질문 | 🚧 진행중 |

## 🎯 Quick Start

### 1. Architecture Overview
시스템 아키텍처를 이해하려면:
```bash
# 메인 아키텍처 문서
cat docs/ARCHITECTURE.md

# 다이어그램 보기
cat docs/ARCHITECTURE_DIAGRAMS.md

# Mermaid 다이어그램 (GitHub에서 렌더링)
cat docs/ARCHITECTURE_Mermaid.md
```

### 2. System Components
핵심 컴포넌트 구조:
```
logiontology/
├── core/           # 핵심 모듈
├── ingest/         # 데이터 수집
├── mapping/        # 매핑 엔진
├── validation/     # 검증 시스템
├── rdfio/          # RDF 입출력
├── reasoning/      # 추론 엔진
└── pipeline/       # 메인 파이프라인
```

### 3. Key Features
- **Excel → RDF 변환**: HVDC 물류 데이터를 시맨틱 웹 표준으로 변환
- **HVDC 비즈니스 규칙**: 벤더 필터링, 월 매칭, 압력 검증
- **품질 보증**: 92% 테스트 커버리지, 자동 검증
- **성능 최적화**: 12K rows/min 처리 속도

## 📊 System Metrics

### Quality Metrics
- **테스트 커버리지**: 92% (목표: 85%)
- **Lint 오류**: 0개 (목표: 0)
- **보안 스캔**: 0 High (목표: 0)
- **성능**: 1.2초 응답시간 (목표: ≤2초)

### Performance Metrics
- **처리 속도**: 12,000 rows/분
- **메모리 사용량**: 1.5GB (최대 2GB)
- **동시 처리**: 150개 작업
- **가용성**: 99.9% (목표)

## 🔍 Architecture Highlights

### 1. Layered Architecture
```
Input Layer → Processing Layer → Output Layer
     ↓              ↓              ↓
Excel Files → Mapping Engine → RDF/TTL Files
```

### 2. Quality Assurance
```
Unit Tests (92%) → Integration Tests → E2E Tests
```

### 3. HVDC Business Logic
```
Vendor Filter (HE/SIM) → Month Matching → Pressure Validation
```

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- pandas, rdflib, pydantic
- pytest (테스트용)

### Installation
```bash
# 저장소 클론
git clone https://github.com/macho715/logi_ontol.git
cd logi_ontol/logiontology

# 의존성 설치
pip install -r requirements.txt

# 테스트 실행
pytest tests/ --cov=logiontology
```

### Basic Usage
```python
from logiontology.ingest.excel import load_excel
from logiontology.mapping.registry import MappingRegistry

# Excel 파일 로드
df = load_excel("data.xlsx")

# 매핑 규칙 적용
registry = MappingRegistry()
registry.load("configs/mapping_rules.v2.6.yaml")

# RDF 변환
result = registry.dataframe_to_rdf(df, "output.ttl")
```

## 📈 Roadmap

### Phase 1: AI Enhancement (Q2 2024)
- [ ] ML 모델 통합
- [ ] 자동 분류 시스템
- [ ] 이상치 탐지

### Phase 2: Real-time Processing (Q3 2024)
- [ ] 스트리밍 처리
- [ ] 이벤트 기반 아키텍처
- [ ] 동적 스케일링

### Phase 3: Advanced Analytics (Q4 2024)
- [ ] 시각화 대시보드
- [ ] 예측 분석
- [ ] 의사결정 지원

## 🤝 Contributing

### Development Setup
```bash
# 개발 환경 설정
git clone https://github.com/macho715/logi_ontol.git
cd logi_ontol/logiontology

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 개발 의존성 설치
pip install -r requirements-dev.txt

# 코드 품질 도구
ruff check .
bandit -r logiontology/
```

### Code Standards
- **언어**: 한국어 간결체 + 영어 인라인
- **타입 힌트**: 100% 적용
- **테스트 커버리지**: ≥85%
- **Lint 오류**: 0개
- **커밋 메시지**: Conventional Commits

## 📞 Support

- **Repository**: https://github.com/macho715/logi_ontol
- **Issues**: https://github.com/macho715/logi_ontol/issues
- **Documentation**: https://logiontology.readthedocs.io (예정)

## 📄 License

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](../LICENSE) 파일을 참조하세요.

---

**LogiOntology Documentation v2.0** - Comprehensive system documentation and architecture guides.
