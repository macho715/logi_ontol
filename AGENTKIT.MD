1️⃣ hvdc_schema_events_8997_sample.csv
Case No,Vendor,Event_Type,Flow_Code,Warehouse_Code,Final_Location,Status_Location_Date,Final_Location_Date,Weight_ton,Qty,Container_No
HVDC-00001,SCT,Inbound,2,DSV_ALMARKAZ,DAS,2025-10-01,2025-10-04,12.50,40,HMMU1234567
HVDC-00002,DSV,Outbound,3,MOSB,AGI,2025-10-03,2025-10-08,24.20,80,HMMU1234568
HVDC-00003,SCT,Inbound,1,,MIR,2025-10-02,2025-10-05,18.00,60,HMMU1234569
# 샘플 3행 / 실제 데이터 200행 이하 권장

2️⃣ hvdc_ontology_core_no-hasLocation.ttl
@prefix hvdc: <https://samsungcnt.com/hvdc#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

hvdc:Case_00001 a hvdc:CargoCase ;
    hvdc:hasVendor "SCT" ;
    hvdc:hasFinalLocation "DAS" ;
    hvdc:hasFinalLocationDate "2025-10-04"^^xsd:date ;
    hvdc:hasSCTRefNo "SCT-REF-00923" ;
    hvdc:hasFlowCode "2" .

# hasLocation 제거됨. hasFinalLocation만 유지.

3️⃣ flow_code_v3.5_rules.md
# Flow Code v3.5 – Summary Rules

| 코드 | 경로 | 조건 | 설명 |
|------|------|------|------|
| 0 | Pre Arrival | WH/MOSB 미입고 | 선적은 완료되었으나 입고 전 |
| 1 | Port→Site | Site MIR/SHU 직송 | AGI/DAS는 금지 |
| 2 | Port→WH→Site | WH 경유 후 현장 도착 | 일반 루트 |
| 3 | Port→MOSB→Site | AGI/DAS 대상 MOSB 경유 | MOSB only |
| 4 | Port→WH→MOSB→Site | AGI/DAS 대상 WH+MOSB 경유 | 복합 루트 |
| 5 | Mixed / Exception | WH/MOSB 혼합 | 예외·대기건 |

**검증 규칙**
- Flow 3,4는 Final_Location ∈ {AGI, DAS}
- Flow 1은 MIR/SHU만 허용
- Final_Location 누락 → “보정 필요”

4️⃣ validation_report_sample.txt
[Validation Report – Sample Extract]
Date: 2025-10-31
Source: exports/validation/report.txt

1. Missing Final_Location: 12건
   - Example: HVDC-00025 / Outbound / SiteInbound
2. Flow Code ↔ WH Handling 불일치: 5건
   - Example: HVDC-00047 / Flow 3인데 WH 미경유
3. Vendor=SCT Ref.No 누락: 8건
   - Example: HVDC-00056 / SCT / Ref.No 없음

5️⃣ stock_audit_sample.csv
Final_Location,Event_Type,Count,First_Date,Last_Date
DAS,Inbound,324,2025-08-01,2025-10-31
AGI,Outbound,289,2025-07-15,2025-10-30
MIR,Inbound,110,2025-09-05,2025-10-29
SHU,Outbound,88,2025-09-12,2025-10-27
# Count 단위: 건수 / 날짜 ISO8601

6️⃣ slash_commands_logi-master.md
# Slash Command Reference – HVDC Logistics

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/logi-master invoice-audit` | 인보이스 자동 검증 | `/switch_mode COST-GUARD + /logi-master invoice-audit` |
| `/logi-master predict` | 창고 점유율 예측 | `/switch_mode ORACLE + /logi-master predict` |
| `/logi-master hs-risk` | HS Code 리스크 평가 | `/switch_mode ORACLE + /logi-master hs-risk` |
| `/switch_mode PRIME` | 계약·SUPPLYTIME 분석 모드 |  |
| `/switch_mode LATTICE` | CIPL↔BL 문서 정합성 확인 |  |
| `/visualize_data --type=heatmap` | Heat-Stow 시각화 |  |
