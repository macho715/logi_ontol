# HVDC Logistics Ontology - Documentation Index

**프로젝트**: HVDC Logistics & Ontology System
**버전**: v3.5 (Flow Code + MCP Integration)
**최종 업데이트**: 2025-10-31

---

## 📋 문서 카테고리

### 1. Flow Code v3.5 Documentation

**위치**: `docs/flow_code_v35/`

- **[FLOW_CODE_V35_ALGORITHM.md](flow_code_v35/FLOW_CODE_V35_ALGORITHM.md)** (600 lines)
  - Flow Code v3.5 알고리즘 상세 문서
  - 계산 로직, 도메인 룰, 예외 처리
  - 0~5 범위 분류 규칙

- **[FLOW_CODE_V35_IMPLEMENTATION_COMPLETE.md](flow_code_v35/FLOW_CODE_V35_IMPLEMENTATION_COMPLETE.md)**
  - 구현 완료 보고서
  - 테스트 결과 (29/29 통과)
  - 검증 결과

- **[FLOW_CODE_V35_INTEGRATION.md](flow_code_v35/FLOW_CODE_V35_INTEGRATION.md)**
  - Excel → TTL 파이프라인 통합
  - 온톨로지 스키마 확장
  - 데이터 변환 프로세스

- **[FLOW_CODE_V35_MASTER_DOCUMENTATION.md](flow_code_v35/FLOW_CODE_V35_MASTER_DOCUMENTATION.md)** (1032 lines)
  - 마스터 참조 문서
  - 전체 시스템 개요
  - 사용 가이드

### 2. MCP Integration Documentation

**위치**: `docs/mcp_integration/`

- **[MCP_FLOW_CODE_V35_INTEGRATION.md](mcp_integration/MCP_FLOW_CODE_V35_INTEGRATION.md)**
  - MCP 서버와 Flow Code v3.5 통합
  - SPARQL 쿼리 엔드포인트
  - GPT Custom Actions 연동

- **[MCP_SERVER_V35_COMPLETE.md](mcp_integration/MCP_SERVER_V35_COMPLETE.md)**
  - MCP 서버 v3.5 구현 완료
  - 아키텍처 설계
  - API 레퍼런스

- **[MCP_SERVER_INTEGRATION_FINAL_REPORT.md](mcp_integration/MCP_SERVER_INTEGRATION_FINAL_REPORT.md)**
  - 최종 통합 보고서 (한글)
  - 프로덕션 배포 가이드
  - 검증 결과

### 3. Project Reports

**위치**: `docs/project_reports/`

- **[IMPLEMENTATION_SUMMARY.md](project_reports/IMPLEMENTATION_SUMMARY.md)** (333 lines)
  - Excel → TTL 변환 구현 요약
  - 이벤트 기반 온톨로지
  - 14/14 pytest 통과

- **[HVDC_WORK_LOG.md](project_reports/HVDC_WORK_LOG.md)** (1002 lines)
  - logiontology v2.0.0 작업 로그
  - 2시간 개발 이력
  - Backend Core 완료 (72%)

- **[CHANGELOG.md](project_reports/CHANGELOG.md)** (376 lines)
  - 프로젝트 변경 이력
  - v2.0.0 릴리즈 노트
  - 계획된 기능 (Phase 2-3)

- **[PROJECT_REORGANIZATION_COMPLETE.md](project_reports/PROJECT_REORGANIZATION_COMPLETE.md)**
  - 프로젝트 재구성 완료 보고


### 4. Ontology Documentation

**위치**: `docs/ontology/`

- **[HVDC_Ontology_Analysis.md](ontology/HVDC_Ontology_Analysis.md)**
  - 온톨로지 분석 문서

### 5. Guides

**위치**: `docs/guides/`

- **[QUICK_START.md](guides/QUICK_START.md)**
  - 5분 빠른 시작 가이드

- **[API_REFERENCE.md](guides/API_REFERENCE.md)**
  - API 레퍼런스

- **[TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)**
  - 문제 해결 가이드

### 6. Architecture

**위치**: `docs/architecture/`

- **[SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md)**
  - 시스템 아키텍처 설계

- **[DATA_FLOW.md](architecture/DATA_FLOW.md)**
  - 데이터 플로우 다이어그램

- **[INTEGRATION_POINTS.md](architecture/INTEGRATION_POINTS.md)**
  - 통합 포인트 문서

### 7. MCP Configuration

**위치**: `docs/`

- **[MCP_Configuration_Guide.md](MCP_Configuration_Guide.md)**
  - MCP 설정 가이드

### 8. Mapping Documentation

**위치**: `docs/`

- **[P_MD_v2.6_mapping.md](P_MD_v2.6_mapping.md)**
  - Mapping 문서 v2.6

- **[P2_MD_v2.6_clustering.md](P2_MD_v2.6_clustering.md)**
  - Clustering 문서 v2.6

---

## 🔍 검색 키워드

### Flow Code
- Algorithm, v3.5, 0-5 범위, AGI/DAS 강제, Pre Arrival
- 관련 문서: `docs/flow_code_v35/`

### MCP Server
- SPARQL, REST API, GPT Custom Actions, FastAPI
- 관련 문서: `docs/mcp_integration/`

### Implementation
- Excel → TTL, Event-based Ontology, pytest
- 관련 문서: `docs/project_reports/IMPLEMENTATION_SUMMARY.md`

### logiontology
- v2.0.0, Backend Core, Ontology, Neo4j
- 관련 문서: `docs/project_reports/HVDC_WORK_LOG.md`

### Changelog
- Release Notes, Phase 2-3
- 관련 문서: `docs/project_reports/CHANGELOG.md`

---

## 📁 루트 레벨 문서

**위치**: `c:\logi_ontol\`

- **[README.md](../README.md)**
  - 프로젝트 개요
  - 빠른 시작
  - 주요 기능

- **[plan.md](../plan.md)**
  - Master Plan v2.0.0
  - Phase 1-3 로드맵
  - 프로젝트 상태

- **[PROJECT_COMPLETE_DOCUMENTATION.md](../PROJECT_COMPLETE_DOCUMENTATION.md)** (792 lines)
  - v3.5 완전 문서
  - 전체 시스템 개요
  - 구현, 데이터, 테스트 상태

---

## 🗂️ 온톨로지 참조 문서

### Core Ontology

**위치**: `c:\logi_ontol\core/`

8개 핵심 온톨로지 문서:
1. `1_CORE-01-hvdc-core-framework.md`
2. `1_CORE-02-hvdc-infra-nodes.md`
3. `1_CORE-03-hvdc-warehouse-ops.md`
4. `1_CORE-04-hvdc-invoice-cost.md`
5. `1_CORE-05-hvdc-bulk-cargo-ops.md`
6. `1_CORE-06-hvdc-doc-guardian.md`
7. `1_CORE-07-hvdc-ocr-pipeline.md`
8. `1_CORE-08-flow-code.md` (Flow Code v3.5 통합)

### Core Consolidated

**위치**: `c:\logi_ontol\core_consolidated/`

5개 통합 온톨로지 문서:
1. `CONSOLIDATED-01-framework-infra.md`
2. `CONSOLIDATED-02-warehouse-flow.md`
3. `CONSOLIDATED-03-cost-bulk.md`
4. `CONSOLIDATED-04-document-ocr.md`
5. `README.md`

### Extended Ontology

**위치**: `c:\logi_ontol\extended/`

15개 확장 온톨로지 문서 (포트 운영, 커뮤니케이션, 규제 등)

---

## 📊 문서 통계

- **Flow Code v3.5**: 4개 문서 (약 2,700 lines)
- **MCP Integration**: 3개 문서 (약 1,500 lines)
- **Project Reports**: 7개 문서 (약 2,800 lines)
- **Guides**: 3개 문서
- **Architecture**: 3개 문서
- **Ontology**: 28개 문서 (core + consolidated + extended)

**총 문서**: 48개+

---

## 🔗 관련 링크

- **메인 패키지**: [logiontology/](../logiontology/)
- **MCP 서버**: [hvdc_mcp_server_v35/](../hvdc_mcp_server_v35/)
- **데이터**: [data/](../data/)
- **출력**: [output/](../output/)
- **레거시 아카이브**: [archive/](../archive/)

---

**문서 버전**: v1.0
**작성일**: 2025-10-31
**작성자**: HVDC Project Team
