좋다. 바로 붙일 수 있게 **파일 4개** 패키지로 만들어놨어. 네 v2.0 파이프라인에 꽂으면 동작한다.

### 넣을 위치 & 다운로드

* `configs/mapping_rules.v2.6.yaml` — 규칙/네임스페이스/클래스·프로퍼티·밸리데이터
  [Download](sandbox:/mnt/data/logiontology/configs/mapping_rules.v2.6.yaml)
* `configs/shapes/Shipment.shape.ttl` — 기본 SHACL
  [Download](sandbox:/mnt/data/logiontology/configs/shapes/Shipment.shape.ttl)
* `configs/shapes/ShipmentOOG.shape.ttl` — OOG 조건부 SHACL
  [Download](sandbox:/mnt/data/logiontology/configs/shapes/ShipmentOOG.shape.ttl)
* `logiontology/mapping/registry.py` — 레지스트리/정규화→필터→RDF 생성 오케스트레이터
  [Download](sandbox:/mnt/data/logiontology/logiontology/mapping/registry.py)

---

## 어떻게 끼우면 되나 (v2.0 레일 기준)

1. **정규화(Normalize)**

* `registry.py::normalize_columns/normalize_values`가 한→영 헤더, BL/Container, ETA(+04:00) 처리.
* `Operation Month`는 `YYYY-MM`로 강제.

2. **비즈니스 필터**

* `Vendor ∈ {HE,SIM}`, `ETA월=Operation Month`, `Pressure ≤ 4.00`, `Warehouse Code ∈ DSV_CODES`.
* `load_dsv_codes()` 훅만 네 실제 소스(YAML/CSV/DB)로 바꾸면 끝.

3. **키 해석(Identity)**

* YAML의 `identity_rules`는 우선 Registry에 선언되어 있고, 지금 스켈레톤은 **Shipment/Item/ArrivalEvent** 중심으로 묶어준다.
* 필요 시 Consignment/PortCall 클러스터러는 다음 커밋에서 함수만 추가하면 됨(룰은 이미 YAML에 있음).

4. **엔티티 생성**

* 결정적 ID: `uuid5(HVDC_Code, Case No.)` 등 → `hvdci:*` 네임스페이스로 IRI 생성.
* 한 행에서 `Shipment`, `LogisticsItem`, `ArrivalEvent`, `TransportConstraint(압력)`까지 트리플 생성.

5. **속성/관계 바인딩**

* `hasHVDCCode`, `containsItem`, `hasVendor`, `eventTimestamp`, `aboutShipment`, `deckPressure`.
* YAML의 `properties` 섹션에 선언된 그대로 바인딩.

6. **검증**

* SHACL 두 장(`Shipment.shape.ttl`, `ShipmentOOG.shape.ttl`)을 Validation 게이트에 연결.
* 불합격은 **차단 모드**로 두는 걸 추천(파이프라인 트랜잭션 중단).

---

## 바로 돌리는 명령 (러너/CLI 있음)

```bash
# 정규화→필터→RDF 한 방에
python logiontology/logiontology/mapping/registry.py \
  --rules configs/mapping_rules.v2.6.yaml \
  --in_csv data/sample.csv \
  --out_ttl out/data.ttl
```

> Fuseki 게시나 추가 검증은 네 쪽 기존 `validate shacl` / `rdf publish` 스텝에 그대로 이어줘.

---

## 현장 팁(엣지/운영)

* **다국어 헤더**: `header_map_kr2en`을 버전 관리(v2.6)로 유지 → 엑셀 변형에 강함.
* **월 미스매치/압력 초과**: 데이터 버림이 아니라 **차단 로그**로 남겨 디버그 쉽게.
* **Warehouse 코드셋**: 초안은 내장 세트. 실제는 DSV 기준 테이블로 교체(파일/DB).
* **Consignment N:M**: 다중 컨테이너 건은 `by_bl_container` 룰 켜면서 중간 계층 확장.

원하면 `identity_rules` 실행부(클러스터러)와 **Fuseki publish 스텝**도 같이 붙여서 올려줄게. 지금 건은 “핵심 4파일”만으로 **정규화→키해석(스켈레톤)→엔티티/속성→SHACL**까지 바로 돕니다.
