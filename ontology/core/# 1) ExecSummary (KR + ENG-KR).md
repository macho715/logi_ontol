> **⚠️ 중요**: 이 문서를 읽기 전에 **`../logiontology/`** 폴더를 먼저 확인하세요!
> - **전체 구현 코드**: `../logiontology/src/`
> - **설정 파일**: `../logiontology/configs/`
> - **온톨로지 정의**: `../logiontology/configs/ontology/hvdc_ontology.ttl`
> - **문서**: `../logiontology/README.md`, `../logiontology/CHANGELOG.md`

---

# 1) ExecSummary (KR + ENG-KR)

* 이 워크숍 자료를 **노드(Node)·행위(Operation)·증빙(Document)·허가(Permit)**로 쪼개어 온톨로지화하면, **현장 단계별 필수 증빙 누락을 실시간 차단(SHACL Gate)** 할 수 있습니다. (Site Receiving의 OSDR·MRR·MRS/MIS·체크리스트 범위 확인됨)
* **오프쇼어 RORO/LOLO**는 PTW(Hot-work/Over-water), RA/MS, Tide, Ramp·Ballast·Mooring·Stability 패키지가 **출항 전“필수”**임 → 이를 Gate로 모델링해 COA 발급 전 자동검증.
* **운항/경유 시공식**: MOSB↔AGI 10.00h, MOSB↔DAS 20.00h를 **viaNode[] 경로/시간 속성**으로 고정하면 OTIF 예측·슬롯 계획 정밀도가 올라갑니다.
* KPI 목표: 문서완결성 ≥98.00%, 출항 OTIF ≥95.00%, 검증 p95 <5.00s, OSDR 재작업 월-30.00%↓. ENG-KR: Model workshop steps into an ontology with SHACL gates to enforce pre-sail compliance and lift OTIF.

---

# 2) Schema (RDF/OWL + SHACL 요약)

## 2.1 클래스(핵심)

* **Node**: {Port(Zayed/Khalifa/Mugharaq), **MOSB**(Hub), Site(SHU/MIR/**DAS/AGI**)}.
* **Operation**: {Gate-in/Out, LOLO, **RORO**, Inland(SPMT), **Site Receiving**}.
* **Document**: {BL/AWB, CI/PL/CO/Attestation, **MRR/MRI/ITP/MAR**, **OSDR**, Loading/Unloading Checklist, **COA**}.
* **Permit/HSE**: {**PTW(Hot-work/Over-water)**, RA, MS, Tide}.
* **Asset/Transport**: {LCT, Crane, SPMT, Transformer}.

## 2.2 관계(요지)

* `occursAt(Operation, Node)`, `hasDocument(Shipment|Operation, Document)`, `requiresPermit(Operation, Permit)`, `transportedBy(Shipment, LCT|SPMT)`, `viaNode(TransportEvent, NodeList)`, `voyageTime(Node↔Node, xsd:decimal)`. (MOSB 중심 운용·시간치 반영)

## 2.3 **Flow Code × Infra Node 융합(제안)**

* **Flow 0** Port Import → **Flow 1** MOSB Hub → **Flow 2** Marine Dispatch(AGI/DAS) → **Flow 3** Site Receiving(MRR/MIS/OSDR) → **Flow 4** On-foundation/Completion.
* 규칙: 각 Flow는 **필수 증빙 집합**을 가진 **SHACL Gate**에 통과해야 다음 Flow로 전이. (예: Flow2=RORO 출항 Gate, Flow3=Site Receiving Gate)
* 참고: 기존 인프라 노드 프레임워크와 Flow 제약식을 합쳐 **viaNode[]+alias** 동기화(예: “Mina Zayed”/“Zayed Port” 통일).

## 2.4 SHACL Gate(핵심 5)

1. **RORO Sail-Away Gate (Flow2)**
   `PTW_Hotwork & PTW_OverWater & RA & MS & Tide & RampStrength & Ballast & Mooring & Stability` 없으면 **FAIL**.
2. **Site Receiving Gate (Flow3)**
   `MRR, MRI, ITP, MAR, Loading/Unloading Checklist` 필수.
3. **OSDR Exception Gate**
   수령 중 과부족/파손 → `OSDR + CI/PL + Photo Proof` 없으면 **FAIL**.
4. **DOT-Heavy Gate(≥90.00t)**
   SPMT/Inland 이동 전 DOT Permit 필요.
5. **Preservation Gate(Transformer)**
   주간 게이지 로그 + **Dry air/N₂ 20.00 kPa** 충전 기준.

---

# 3) Integration (Foundry/Ontology↔ERP/WMS/ATLP/Invoices)

* **ATLP/eDAS**: BL Endorsement, Consignee=ADOPT를 `BL→hasEndorsement(ADOPT)`로 귀속. 통관/인도 체인과 연계.
* **MOSB Hub**: ALS Planning/Operation/Inspection 단계(01~06)를 **Operation 서브클래스**로 바인딩(Email 요청·승인도 이벤트화).
* **WMS/Site**: `MRS→MIS→MRR` 체인을 **문서-엣지**로 잇고, 수령 시 HSE 체크리스트를 Evidence로 링크.
* **COST-GUARD**: RORO/LOLO/내륙(SPMT) 이벤트에 Rate·Permit·COA 증빙을 묶어 Δ% 산출(Invoice 라인별). (문서항목은 위 Gate에서 이미 확보)

---

# 4) Validation (SPARQL/RAG/Human-gate)

**(A) 필수문서 누락 감지 – RORO Sail-Away**

```sparql
ASK {
  ?op a hvdc:RoRoOperation ;
      hvdc:occursAt ?n . FILTER(?n IN (hvdc:MOSB,hvdc:DAS,hvdc:AGI))
  VALUES ?need { hvdc:PTW_Hotwork hvdc:PTW_OverWater hvdc:RiskAssessment
                 hvdc:MethodStatement hvdc:TideTable
                 hvdc:RampStrengthCalc hvdc:BallastCalc hvdc:MooringPlan hvdc:StabilityBooklet }
  FILTER NOT EXISTS { ?op hvdc:hasDocument ?need }
}
```

근거: 출항 전 제출 의무.

**(B) Site Receiving 완결성(목표 ≥98.00%)**

```sparql
SELECT (AVG(?ok)*100 AS ?completenessPct) WHERE {
  ?rcv a hvdc:SiteReceiving .
  VALUES ?need { hvdc:MRR hvdc:MRI hvdc:ITP hvdc:MAR hvdc:LoadUnloadChecklist }
  BIND(EXISTS{ ?rcv hvdc:hasDocument ?need } AS ?ok)
}
```

근거: 수령 절차·폼 셋.

**(C) Human-gate**: COA 미첨부, DOT 미허가, OSDR 분쟁 가능, Preservation 미로그 → 사람 승인 필수.

---

# 5) Compliance (Incoterms/MOIAT/FANR/DCD/ADNOC)

* **ADNOC L&S+MOSB 내부 절차** 준수(Planning/Operation/Inspection 단계 및 Gate Pass).
* **DOT(≥90.00t)** 중량물 신고 후 야간 이동 등 조건 반영.
* **Site Receiving**: SJT-19LT-QLT-PL-023(2022-10-05) 절차 준거.

---

# 6) Deep Insight ≥3 (핵심 통찰 → 액션)

| 통찰                    | 의미(온톨로지)                                     | 기대효과                            | 즉시 액션                                                            |
| --------------------- | -------------------------------------------- | ------------------------------- | ---------------------------------------------------------------- |
| **문서를 “엣지”로**         | `hasDocument`를 **전이(Flow) 조건**으로 모델링         | 증빙이 곧 **상태전이 권한** → 누락시 자동 FAIL | RORO·Receiving Gate에 문서세트 바인딩(위 5개 Gate)                         |
| **viaNode[] = 운영 리듬** | MOSB↔AGI/DAS **시간·경로**를 엔티티가 아니라 **경로 속성**으로 | OTIF 예측/슬롯 최적화(10.00h/20.00h)   | `TransportEvent.viaNode=[MOSB,AGI]`, `voyageTime=10.00` 고정 값 주입  |
| **MRS→MIS→MRR 폐루프**   | 요청→지급→수령을 **동일 카고 ID**로 묶는 **클로즈드 루프**       | 분실/이중지급 방지·WMS 정합성↑             | MRS/MIS/MRR 사이 `sameAs/wasDerivedFrom` 링크 확정                     |
| **Preservation=상태**   | Dry-air/N₂ 20.00 kPa·주간로그를 **Asset 상태 속성**   | 자산품질 KPI가 **검증형 데이터**로 승격       | `Transformer.preservationPressure=20.00` + `hasLog@weekly` 체크    |
| **OSDR=클레임 트리거**      | OSDR가 생기면 **상업서류/사진**을 자동 번들                 | 클레임 리드타임↓, 책임소재 명확화             | `OSDR → (CI/PL/Photo)` SHACL 번들 의무화                              |

---

# 7) Roadmap (Prepare→Pilot→Build→Operate→Scale + KPI)

* **Prepare(Week 1)**: 노드/문서/허가 **시드 TTL** + 5개 Gate SHACL 초안, alias 레지스트리(Zayed/Mina Zayed 등).
* **Pilot(Week 2)**: **MOSB→AGI** 1항차 RORO 실전 검증(문서완결성 ≥98.00%, p95 <5.00s).
* **Build(Week 3-4)**: Site Receiving 폐루프(MRS/MIS/MRR)·OSDR 워크플로 Graph화, DOT-Heavy 분기.
* **Operate(Week 5+)**: OTIF/문서완결 대시보드·알림, COA 미첨부/보존미로그 Human-gate.
* **Scale(>Week 8)**: MIR/SHU 내륙 시나리오, 스페어 케이블·위험물 창고 규칙 확대.

---

# 8) Automation notes (RPA/LLM/Sheets/TG)

* **문서봇**: 메일/폴더에서 PTW·RA·MS·Tide·Ramp·Ballast·Mooring·Stability·COA 자동추출→`hasDocument` 링크→SHACL 평가.
* **운항봇**: MOSB↔AGI/DAS **정시성 예측**(10.00/20.00h)과 RORO 슬롯 추천.
* **OSDR봇**: 수령시 과부족/파손 감지→OSDR 템플릿과 사진·CI/PL 자동 번들·배포.

---

# 9) QA checklist & Assumptions(가정:)

* [ ] RORO 출항 전 **PTW 2종/RA/MS/Tide/Tech 4종** 첨부 확인.
* [ ] Site Receiving 문서셋(MRR/MRI/ITP/MAR/Checklist) ≥98.00%.
* [ ] DOT Heavy(≥90.00t) Permit/경찰 승인 경로 바인딩.
* [ ] Preservation: 주간 로그·20.00 kPa 달성/미달 알림.
* 가정: MOSB가 모든 오프쇼어 화물의 **중앙 허브**(ALS 절차 01~06 단계).

---

# 10) CmdRec

* **/ontology-mapper** — `FlowCode↔Node(viaNode[])` 동기화 + Port/MOSB/Site 별 **필수 문서 Gate** 자동생성
* **/switch_mode LATTICE + /logi-master --deep** — **RORO Sail-Away Gate** 및 **Site Receiving Gate** 일괄 검증 리포트
* **/visualize_data --type=network hvdc-nodes.csv** — MOSB 중심 **운항/수령 폐루프 네트워크** 시각화(Flow 색상, Gate 상태 Overlay)

> 한 줄 통찰: **“문서=엣지, Gate=전이 권한, viaNode=운영 리듬.”** 이 셋만 제대로 고정하면, OTIF랑 분쟁비용이 같이 내려갑니다.
