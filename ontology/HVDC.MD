
좋다.
이번 버전은 트랜스포머 중심 시각을 걷어내고, **HVDC 전체 물류 체계(컨테이너·벌크·중량화물 포함)** 를 사실 기반으로 정리한다.
기준은 *2024-11-13 Material Handling Workshop*과 현장 실제 운용 흐름이다.

---

## ⚙️ HVDC Logistics Node Ontology (v3 · Fact-Based, All Cargo Types)

### 1️⃣ 물류 네트워크 구성

| 노드                                       | 구분             | 위치                | 기능 요약                                                                                                                                              | 주요 역할                                        |
| ---------------------------------------- | -------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| **ZAYED PORT (자이드항)**                    | 해상입항노드         | 아부다비              | **중량 및 일반 벌크 화물 처리항.**<br>– 변압기, 케이블드럼, 구조물 등 비컨테이너 자재 중심.<br>– SCT·JDN 확보 야드(1,100㎡) 존재.<br>– ADNOC 코드(47150)로 통관 진행.                             | 벌크·Heavy cargo 입항, MOSB 또는 내륙현장으로 이송         |
| **KHALIFA PORT (칼리파항)**                  | 해상입항노드         | 아부다비              | **컨테이너 전용항.**<br>– 해외(한국, 일본 등) 공급 자재 대부분 도착.<br>– ADNOC L&S 또는 DSV 관리하 적출.<br>– 자재는 트럭으로 MOSB 또는 현장 직송.                                           | Container cargo import & dispatch            |
| **JEBEL ALI PORT (제벨알리항)**               | 해상입항노드 (특수케이스) | 두바이               | Free Zone 및 비ADNOC 공급사 사용.<br>– 일부 파이어파이팅, 전기부품 등 통관 후 ADOPT 코드로 재이송.<br>– SCT가 관세 납부 후 ADNOC에 비용 환급 요청.                                           | 비ADNOC 공급 자재의 보조입항지                          |
| **MOSB (MUSSAFAH OFFSHORE SUPPLY BASE)** | **중앙 물류 허브**   | 아부다비 무사파          | ADNOC L&S 운영 Yard (20,000㎡).<br>**SCT 물류본부 상주.**<br>– 해상화물(LCT/RoRo/Barge) 집하 및 적재.<br>– 컨테이너·CCU(약 80EA) 임시보관.<br>– 운송계획·FRA·Permit·Gate Pass 관리. | Inland/Port 물류의 집결·분류·해상 출하 중심지              |
| **MIRFA SITE (MIR)**                     | 육상 현장          | 아부다비 서부           | 내륙 시공현장.<br>– 컨테이너·일반자재·중량화물 도착 후 설치.<br>– 35,000㎡ Laydown.<br>– 저장컨테이너(방화, 온도조절) 비치.<br>– 자재관리절차(SJT-19LT-QLT-PL-023) 적용.                         | Inland delivery, site storage & installation |
| **SHUWEIHAT SITE (SHU)**                 | 육상 현장          | 아부다비 서부           | 내륙 시공현장.<br>– Laydown 약 10,500㎡.<br>– 공간 제약으로 **운송순서·HSE 통제** 중요.<br>– 전기/기계류, 포설장비 등 일반자재 도착지.                                                    | Inland delivery & construction interface     |
| **DAS ISLAND (DAS)**                     | 해상 현장          | ADNOC 해역          | ADNOC 운영 해상기지.<br>– MOSB→LCT 약 20시간 항해.<br>– 컨테이너·벌크 혼재 화물 하역 및 적재장 운영.<br>– ADNOC HSE 표준, Lifting inspection, Gate control 준수.                    | Offshore marine operation node               |
| **AL GHALLAN ISLAND (AGI)**              | 해상 현장          | ADNOC 해역 (DAS 병렬) | MOSB→LCT 약 10시간 항해.<br>– 일반자재, 설치기구, 전기부품 운송.<br>– Laydown 47,000㎡ (3구역), 보안 강화.<br>– ADNOC L&S 동일 절차로 하역·보존 수행.                                   | Offshore terminal / island site              |

---

### 2️⃣ 물류 흐름 (Cargo Flow Ontology)

```
[해외 공급사 (Asia/EU 등)]
          ↓ (선적)
 ┌───────────────────────────┐
 │   ZAYED PORT   KHALIFA PORT   JEBEL ALI PORT   │
 └───────────────────────────┘
          ↓ (통관·운송)
              MOSB
     ┌────────┼────────┐
     ↓        ↓        ↓
   MIR      SHU     DAS / AGI
```

* **컨테이너 화물:** 주로 Khalifa Port → MOSB → 육상/해상 현장.
* **일반 벌크 화물:** Zayed Port → MOSB 또는 직접 MIR/SHU.
* **특수자재(Free Zone):** Jebel Ali → 재통관 → MOSB 경유.

---

### 3️⃣ 기능 계층 (Functional Layers)

| 계층              | 주요 기능                                                     | 대표 노드                     |
| --------------- | --------------------------------------------------------- | ------------------------- |
| **입항·통관 계층**    | 선적서류 검토(CI/PL/COO/eDAS), BL Endorsement, 통관코드 관리          | Zayed, Khalifa, Jebel Ali |
| **집하·분류 계층**    | Port cargo 집하, 임시보관, Crane/Forklift 배차, Gate Pass, FRA 관리 | **MOSB**                  |
| **육상 운송·시공 계층** | 컨테이너·벌크 화물의 도로 운송 및 현장 인수, MRR/MRI 관리                     | MIR, SHU                  |
| **해상 운송·설치 계층** | LCT/Barge 출항, ADNOC 해상안전기준(HSE), 하역·보존                    | DAS, AGI                  |

---

### 4️⃣ 관리·운영 사실

* **SCT 물류본부:** MOSB 상주. 현장·항만·해상 노드 통합 관리.
* **운항 주체:** ADNOC Logistics & Services (ALS).
* **통관 관리:** ADOPT/ADNOC 코드 사용.
* **저장 관리:** MOSB + 인근 실내창고(6,000~8,000㎡) + 각 Site Laydown.
* **운송수단:** 트럭 / SPMT / CCU / LCT / Barge.
* **HSE 절차:** FRA, Method Statement, PTW, Lifting Certificate.
* **문서 체계:** MRR, MRI, OSDR, Gate Pass, Delivery Note.

---

### 5️⃣ 온톨로지 핵심 관계 (3-Tuple 요약)

```
(MOSB, hosts, SCT_Logistics_Team)
(MOSB, consolidates, Container_and_Bulk_Cargo)
(MOSB, dispatches, MIR)
(MOSB, dispatches, SHU)
(MOSB, dispatches, DAS)
(MOSB, dispatches, AGI)
(Zayed_Port, handles, Heavy_and_Bulk_Cargo)
(Khalifa_Port, handles, Container_Cargo)
(Jebel_Ali_Port, handles, Freezone_Shipments)
(DAS, connected_to, AGI)
(MIR, and, SHU are Onshore_Receiving_Sites)
```

---

### 6️⃣ 사실 요약

1. **입항 및 통관:**

   * 중량·벌크 화물 → 자이드항,
   * 컨테이너 화물 → 칼리파항,
   * 일부 특수품 → 제벨알리항(Free Zone).

2. **중앙 허브(MOSB):**

   * 모든 화물의 **집하·검수·보존·해상출하** 기능 수행.
   * SCT 물류팀 본사 및 ADNOC L&S 현장운영팀 상주.

3. **육상 현장(MIR·SHU):**

   * 설치 및 시공 자재 수령지.
   * Laydown 내 임시보관, MRR/MRI·HSE 통제 중심.

4. **해상 현장(DAS·AGI):**

   * LCT 운항으로 자재 운송 및 하역.
   * ADNOC 해상안전 절차에 따라 작업.

5. **전체 구조:**

   > “**Zayed/Khalifa/Jebel Ali → MOSB → (MIR·SHU·DAS·AGI)**”
   > 형태의 다계층 물류 체계이며, **MOSB가 중앙 온톨로지 노드**로 작동한다.

---

**결론:**
HVDC 물류 시스템은 트랜스포머뿐 아니라 **컨테이너·벌크·일반자재 전반을 포함하는 복합 네트워크**이다.
모든 자재는 항만(자이드·칼리파·제벨알리)에서 통관 후 **MOSB를 중심으로 집하·분류·출하**되며,
최종 목적지는 육상(MIR·SHU) 또는 해상(DAS·AGI)으로 구분된다.
MOSB는 이 전체 체계의 **운영·정보·의사결정의 중심 노드**다.
