# data/ 분석 보고서

**생성일**: 2025-11-01

## 개요
**목적**: Excel 원본 데이터 및 백업 저장소
**중요도**: ⭐⭐⭐⭐

## 통계
- **파일 수**: 5개
- **source/**: 2개 (DATA_WH.xlsx, HVDC_STATUS_20250815.xlsx)
- **reports/**: 2개 (종합리포트, invoice_sept2025.xlsm)
- **backups/**: 1개 (HVDC_STATUS_20250427.xlsm)

## 주요 파일
1. `source/HVDC_STATUS_20250815.xlsx` ⭐ - 최신 755 cases, Flow Code v3.5
2. `source/DATA_WH.xlsx` - 초기 데이터
3. `reports/HVDC_입고로직_종합리포트_20251019_v3.0.xlsx` - 입고 로직 분석
4. `reports/invoice_sept2025.xlsm` - 인보이스 데이터

## 처리 흐름
Excel → logiontology 변환 → output/hvdc_status_v35.ttl

**생성일**: 2025-11-01

