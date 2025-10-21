# Reports 폴더 가이드

이 폴더는 LogiOntology v3.1 프로젝트의 모든 분석 보고서와 데이터를 체계적으로 정리한 곳입니다.

## 📁 폴더 구조

```
reports/
├── final/                              # 최종 통합 보고서
├── data/                               # JSON 원시 데이터
├── analysis/                           # 상세 분석 보고서
├── archive/                            # 중간 보고서 및 히스토리
└── README.md                           # 이 파일
```

## 📋 폴더별 설명

### 🎯 final/ - 최종 통합 보고서
프로젝트의 최종 결과물과 통합 보고서가 포함되어 있습니다.

- **`LOGIONTOLOGY_FINAL_REPORT.md`** - 📊 **메인 보고서** (읽기 권장)
  - 전체 프로젝트 개요 및 핵심 성과
  - ABU, Invoice, HVDC 시스템 통합 요약
  - 시스템 아키텍처 및 프로세스 플로우
  - Mermaid 다이어그램으로 시각화된 데이터

- **`abu_integration_final_report.md`** - ABU 통합 시스템 상세 보고서
- **`abu_sparql_analysis_report.md`** - SPARQL 쿼리 분석 결과
- **`abu_integrated_visualization.md`** - ABU 시스템 시각화 대시보드
- **`INVOICE_VISUALIZATION_REPORT.md`** - Invoice 시스템 분석 보고서

### 📊 data/ - JSON 원시 데이터
모든 분석의 원시 데이터가 JSON 형태로 저장되어 있습니다.

**ABU 관련 데이터:**
- `abu_lpo_analysis.json` (127KB) - LPO 데이터 상세 분석
- `abu_whatsapp_analysis.json` (120KB) - WhatsApp 메시지 분석
- `abu_responsible_persons_analysis.json` (25KB) - 담당자별 분석
- `abu_comprehensive_summary.json` (9.5KB) - 종합 요약
- `abu_data_summary.json` (1.4KB) - 기본 통계
- `abu_integrated_stats.json` (167B) - 통합 통계
- `abu_sparql_analysis_data.json` (3.5KB) - SPARQL 분석 결과
- `abu_guidelines_analysis.json` (4.0KB) - 가이드라인 분석
- `whatsapp_images_analysis.json` (92KB) - 이미지 메타데이터 분석

**Invoice 관련 데이터:**
- `invoice_analysis_report.json` (183KB) - Invoice 상세 분석
- `invoice_data_summary.json` (2.0KB) - Invoice 기본 통계

### 🔍 analysis/ - 상세 분석 보고서
각 시스템별 상세한 분석 보고서가 포함되어 있습니다.

- `abu_comprehensive_analysis.md` - ABU 시스템 종합 분석
- `abu_visualization_report.md` - ABU 시각화 상세 보고서
- `HVDC_PROCESSING_REPORT.md` - HVDC 시스템 처리 보고서
- `python_files_comprehensive_analysis_report.md` - Python 코드 분석
- `whatsapp_images_integration_report.md` - 이미지 통합 보고서

### 📚 archive/ - 중간 보고서 및 히스토리
프로젝트 진행 과정에서 생성된 중간 보고서와 히스토리 파일들입니다.

- `abu_cross_references_report.md` - 크로스 레퍼런스 매핑 보고서
- `lpo_processing_report.md` - LPO 처리 보고서
- `PROJECT_CLEANUP_REPORT.md` - 프로젝트 정리 보고서
- `WORK_SUMMARY.md` - 작업 요약 보고서

## 🚀 사용 방법

### 1. 빠른 시작
프로젝트의 전체적인 내용을 파악하려면:
```
reports/final/LOGIONTOLOGY_FINAL_REPORT.md
```

### 2. 특정 시스템 분석
- **ABU 시스템**: `final/abu_integration_final_report.md`
- **Invoice 시스템**: `final/INVOICE_VISUALIZATION_REPORT.md`
- **SPARQL 분석**: `final/abu_sparql_analysis_report.md`

### 3. 원시 데이터 접근
JSON 데이터를 프로그래밍적으로 활용하려면:
```
reports/data/
```

### 4. 상세 분석
특정 주제에 대한 깊이 있는 분석이 필요하면:
```
reports/analysis/
```

## 📈 주요 통계

- **총 파일 수**: 24개 (임시 파일 5개 삭제 후)
- **최종 보고서**: 5개
- **JSON 데이터**: 11개
- **상세 분석**: 5개
- **아카이브**: 3개

## 🔧 기술 스택

- **RDF/OWL**: 온톨로지 표준
- **SPARQL**: 쿼리 언어
- **Mermaid**: 다이어그램 생성
- **JSON**: 데이터 교환
- **Markdown**: 문서 작성

## 📞 지원

프로젝트 관련 문의사항이 있으시면:
- 프로젝트 관리: Samsung C&T Logistics
- 기술 지원: HVDC Project Team
- 시스템 버전: LogiOntology v3.1

---

*이 가이드는 LogiOntology v3.1 프로젝트의 보고서 구조를 이해하는 데 도움이 됩니다.*
