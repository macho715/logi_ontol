# Flow Code v3.5 – Summary Rules

**프로젝트**: HVDC Logistics Ontology
**버전**: v3.5 (unified-3.5)
**데이터 소스**: HVDC STATUS(20250815) (1).xlsx (755 cases)

---

## Flow Code 정의

| 코드 | 경로 | 조건 | 설명 |
|------|------|------|------|
| 0 | Pre Arrival | WH/MOSB 미입고 | 선적은 완료되었으나 입고 전 |
| 1 | Port→Site | Site MIR/SHU 직송 | AGI/DAS는 금지 |
| 2 | Port→WH→Site | WH 경유 후 현장 도착 | 일반 루트 |
| 3 | Port→MOSB→Site | AGI/DAS 대상 MOSB 경유 | MOSB only |
| 4 | Port→WH→MOSB→Site | AGI/DAS 대상 WH+MOSB 경유 | 복합 루트 |
| 5 | Mixed / Exception | WH/MOSB 혼합 | 예외·대기건 |

---

## 실제 분포 (755 Cases)

```
Flow 0 (Pre Arrival):             71건 (9.4%)
Flow 1 (Port → Site):            255건 (33.8%)
Flow 2 (Port → WH → Site):       152건 (20.1%)
Flow 3 (Port → MOSB → Site):     131건 (17.4%)
Flow 4 (Port → WH → MOSB → Site): 65건 (8.6%)
Flow 5 (Mixed / Exception):       81건 (10.7%)
```

**총 케이스**: 755
**이벤트**: 573 Inbound, 245 Outbound

---

## 검증 규칙

### 1. AGI/DAS 도메인 룰
- **조건**: Final_Location ∈ {AGI, DAS}
- **강제**: Flow Code ≥ 3 (MOSB leg 필수)
- **적용**: 31건 자동 승급 (Flow 1/2 → Flow 3)
- **검증**: AGI/DAS 케이스 중 Flow < 3인 것 0건 ✅

### 2. Flow Code 범위
- **최소**: 0 (Pre Arrival)
- **최대**: 5 (Mixed)
- **검증**: 모든 케이스가 0~5 범위 내 ✅

### 3. Final_Location 검증
- **필수**: 모든 케이스 (Flow 0 제외)
- **형식**: MIR, SHU, DAS, AGI
- **누락 시**: "보정 필요" 플래그

### 4. 이벤트 일관성
- **Flow 1**: Inbound만 (Site 직접)
- **Flow 2**: Inbound + Outbound (WH 경유)
- **Flow 3**: Inbound + Outbound (MOSB 경유)
- **Flow 0/5**: 이벤트 제한적 또는 없음

---

## 계산 로직 (Pseudo-code)

```python
def calculate_flow_code_v35(wh_cnt, has_mosb, has_site, final_location):
    # Pre Arrival 판별
    if is_pre_arrival():
        return 0

    # 기본 Flow 계산
    if has_site and not wh_cnt and not has_mosb:
        flow = 1  # Direct
    elif wh_cnt and has_site and not has_mosb:
        flow = 2  # WH
    elif has_mosb and has_site and not wh_cnt:
        flow = 3  # MOSB only
    elif wh_cnt and has_mosb and has_site:
        flow = 4  # WH + MOSB
    else:
        flow = 5  # Mixed

    # AGI/DAS 도메인 오버라이드
    if final_location in ['AGI', 'DAS'] and flow < 3:
        original_flow = flow
        flow = 3
        reason = "AGI/DAS requires MOSB leg"

    return flow
```

---

## 참조 문서

- **알고리즘 상세**: `docs/flow_code_v35/FLOW_CODE_V35_ALGORITHM.md`
- **구현 코드**: `logiontology/src/ingest/flow_code_calculator.py`
- **테스트**: `tests/test_flow_code_v35.py`
- **스키마**: `logiontology/configs/ontology/hvdc_event_schema.ttl`

---

**작성일**: 2025-11-01
**상태**: 프로덕션

