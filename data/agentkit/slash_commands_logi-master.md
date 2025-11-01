# Slash Command Reference – HVDC Logistics

**프로젝트**: HVDC Logistics & Ontology System
**버전**: v3.5
**통합**: MACHO-GPT v3.4-mini + AgentKit

---

## LogiMaster 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/logi-master invoice-audit` | 인보이스 자동 검증 | `/switch_mode COST-GUARD + /logi-master invoice-audit` |
| `/logi-master predict` | 창고 점유율 예측 | `/switch_mode ORACLE + /logi-master predict` |
| `/logi-master hs-risk` | HS Code 리스크 평가 | `/switch_mode ORACLE + /logi-master hs-risk` |
| `/logi-master flow-check` | Flow Code 검증 | `/switch_mode LATTICE + /logi-master flow-check` |
| `/logi-master kpi-dash` | 실시간 KPI 대시보드 | `/switch_mode RHYTHM + /logi-master kpi-dash` |

---

## Mode 전환 명령어

| 명령어 | 설명 | 주요 기능 |
|--------|------|----------|
| `/switch_mode PRIME` | 계약·SUPPLYTIME 분석 모드 | 계약서, BL, 인코텀즈 |
| `/switch_mode ORACLE` | 데이터 예측·분석 모드 | ETA 예측, 비용 최적화 |
| `/switch_mode ZERO` | Fail-safe 모드 | 수동 검증 필수 |
| `/switch_mode LATTICE` | 문서 정합성 확인 모드 | CIPL↔BL, OCR 검증 |
| `/switch_mode RHYTHM` | 실시간 모니터링 모드 | KPI, 알림, 대시보드 |
| `/switch_mode COST-GUARD` | 비용 관리 모드 | 인보이스, 청구서, 이상 탐지 |

---

## 데이터 시각화

| 명령어 | 설명 | 출력 |
|--------|------|------|
| `/visualize_data --type=heatmap` | Heat-Stow 시각화 | 적재 압력 히트맵 |
| `/visualize_data --type=flowchart` | Flow Code 분포 | Flow 0~5 차트 |
| `/visualize_data --type=timeline` | 이벤트 타임라인 | 입출고 시계열 |
| `/visualize_data --type=network` | 물류 네트워크 | Port→WH→Site 그래프 |

---

## 검증 명령어

| 명령어 | 설명 | 검증 항목 |
|--------|------|----------|
| `/validate-data compliance` | 규제 준수 검증 | FANR, MOIAT, AGI/DAS 룰 |
| `/validate-data flow-code` | Flow Code 검증 | 0~5 범위, 도메인 룰 |
| `/validate-data events` | 이벤트 검증 | Inbound/Outbound 일관성 |
| `/validate-data schema` | 스키마 검증 | SHACL, OWL 제약 |

---

## 고급 명령어

| 명령어 | 설명 | 사용 시기 |
|--------|------|----------|
| `/automate invoice-pipeline` | 인보이스 자동화 파이프라인 | 주간/월간 배치 처리 |
| `/rpa-builder warehouse-audit` | 창고 감사 RPA | 정기 재고 조사 |
| `/emergency-response delay-alert` | 긴급 대응 프로토콜 | ETA 지연 24h 초과 시 |
| `/predictive-analysis capacity` | 예측 분석 엔진 | 창고 용량 예측 |

---

## AgentKit 통합 (v3.5)

### 데이터 파일 참조
- `hvdc_schema_events_8997_sample.csv` - 샘플 이벤트 데이터
- `hvdc_ontology_core_no-hasLocation.ttl` - TTL 스키마 샘플
- `flow_code_v3.5_rules.md` - Flow Code 규칙 요약
- `validation_report_sample.txt` - 검증 보고서 샘플
- `stock_audit_sample.csv` - 재고 감사 데이터

### 사용 예시
```bash
# 1. 데이터 로드
/logi-master load-agentkit data/agentkit/

# 2. Flow Code 검증
/validate-data flow-code --source=agentkit

# 3. 시각화
/visualize_data --type=flowchart --data=agentkit

# 4. 보고서 생성
/logi-master report --template=validation --output=exports/
```

---

## 참조 문서

- **MACHO-GPT Guide**: `.cursorrules` (v3.4-mini)
- **Flow Code Algorithm**: `docs/flow_code_v35/FLOW_CODE_V35_ALGORITHM.md`
- **MCP Server**: `hvdc_mcp_server_v35/README.md`
- **API Docs**: http://localhost:8000/docs

---

**작성일**: 2025-11-01
**버전**: AgentKit v1.0
**상태**: 프로덕션

