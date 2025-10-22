# Guideline_HVDC_Project_lightning
**Generated:** 2025-08-09 13:04 GST

## 1) Executive Summary (v1.0)
- **[HVDC] Project Lightning** 그룹은 다중 선박 운항(JPT62/71, Thuraya, Bushra, Razan, Taibah, Wardeh, Jewaher, Marwah 등) 및 AGI·DAS·MOSB 간 **RORO/LOLO·Bunkering·Backload** 조정, **OSDR·S‑PMIS** 문서화와 **CCU/컨테이너** 순환을 실시간 관리합니다.

## 2) Group Profile
| 항목 | 내용 |
|---|---|
| 목적/범위 | 선박 스케줄·하역 계획·자재/장비·문서(OSDR/S‑PMIS) 실시간 공조 |
| 주요 참여자(Top10) | Khemlal-SCT Logistics(1324), Ramaju Das(1272), 정상욱(982), Roy Kim(738), Haitham(644), Shariff(572), Bimal(450), Sajid H Khan(364), DaN(225), Nicole (SHU)(180) |
| 활동기간 | 2024-08-21 ~ 2025-07-31 |
| 트래픽 | High |

## 3) Observed Patterns

- 언어 비율: KR 14% / EN 86%
- 피크 시간대: 07:00, 08:00, 17:00
- 메시지 수: 7,330 / 활동기간: 2024-08-21 ~ 2025-07-31
- 주요 키워드: offloading, thuraya, bushra, razan, wardeh, jopetwil, noted, roro, anchorage, lct


## 4) Tailored Rules

- **운항 브리핑(고정 타임 2회)**: 매일 **07:30 / 16:00**에 *Vessel SITREP* 게시 — `ETA/ETD, Berth, Ops(RORO/LOLO), Cargo, Next port, Constraints(타이드·장비)` 포맷 고정. 
- **계획 컷오프**: **D-1 16:00**까지 다음날 선적/하역 계획 확정(선박·부두·자재·장비·인력). 변경 시 리비전 태그 `R#` 부여.
- **자재 규정**: **HCS/Wall Panel**는 *프리-슬링 또는 현장 슬링+보호재* 필수, **Webbing sling 회수/반납** 원칙. **Bottom Plate/Steel 구조물**은 *바스켓타입·스프레더/바구니형 결상* 우선.
- **컨테이너/CCU**: **FR/OT/바스켓** *TPI·유효증명* 확인 후 투입, **Empty 회수 SLA 48h**. **CCU/바스켓 재고** MOSB 기준 *가시화(번호·위치)*.
- **품질/안전**: **OSDR**는 *사진 또는 스케치+타임라인* 1시간 내 초안, 당일 종결. **CICPA/Mulkiya/Permit/Vetting** 만료 7일 전 알림.
- **에스컬레이션**: 포트 장비 부족·지연 시 **10·30 Rule**(10분 무응답→[RISK], 30분 지연→재배차/대체항만 검토). 
- **문서화**: **S‑PMIS > OSDR/Status** 업로드 완료 후 그룹에 *스탬프* 남기기(`AGI/SHU/MIR/DAS 완료`). 


## 5) KPI & Monitoring

- **SITREP(07:30/16:00) 준수율 ≥ 98%**
- **D‑1 16:00 계획 확정율 ≥ 95%**
- **Empty CCU/컨테이너 회수 TAT ≤ 48h (월 평균)**
- **OSDR 초안 제출 TAT ≤ 1h / 종결 ≤ 24h**
- **Webbing Sling 회수율 100% / Pre‑sling 미스 0건**


## 6) Implementation Checklist

- [ ] 07:30 / 16:00 Vessel SITREP 포맷 고정 공지·운영
- [ ] D‑1 16:00 선적/하역·자재·장비·인력 확정 및 리비전 관리
- [ ] HCS/Wall Panel 슬링 보호재·스프레더(가능시) 적용 지침 배포
- [ ] CCU/바스켓/FR/OT 재고·위치 트래커 운영(MOSB/현장 별)
- [ ] OSDR 템플릿(스케치 허용) + S‑PMIS 업로드 루틴 확정
- [ ] CICPA/Mulkiya/Permit 만료 7일 전 알림 자동화


**Change Log**
- v1.0 (2025-08-09 13:04 GST): 최초 생성. 채팅 로그 기반 운용 규칙·KPI·체크리스트 정리.
