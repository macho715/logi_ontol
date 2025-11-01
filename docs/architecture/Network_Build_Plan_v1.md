# Unified Logistics Network Build Plan v1.1

**Scope**: JPT71(48), ABU, Lightning, docs → 단일 온톨로지 네트워크 (400–500 nodes / 800–1,000 edges)
**Timezone**: Asia/Dubai (UTC+04)  
**Standards**: UN/CEFACT, WCO‑DM, DCSA eBL 3.0, ICC Incoterms 2020  
**PII Policy**: 이름 공개, 전화·이메일 마스킹  

---

## 1) Business Impact (KPI Anchors)
- **시각화/탐색 시간**: Slack/WA 스크롤 대비 **−70.00%** (1.00h → 0.30h)
- **의사결정 속도**: 커뮤니티/핫스팟 자동 발견으로 **+35.00%**
- **불일치 감지율**(동일 인물/선박/항구 중복): **≥95.00%**
- **준수/추적성**: 문서↔작업↔담당자 연결 증거화(Review lead‑time **−25.00%**)

---

## 2) Schema‑First (RDF/OWL, JSON‑LD)
```ttl
@prefix hvdc: <https://example.org/hvdc#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

### Core Classes
hvdc:System a owl:Class .            # JPT71_System, ABU_System, Lightning_System
hvdc:Vessel a owl:Class .
hvdc:Person a owl:Class .
hvdc:Port a owl:Class .
hvdc:Operation a owl:Class .
hvdc:Document a owl:Class .          # CIPL/PL/BL/DO/Manifest/Permit/…
hvdc:Equipment a owl:Class .
hvdc:TimeTag a owl:Class .
hvdc:Reference a owl:Class .
hvdc:Message a owl:Class .           # WhatsApp/Email 등 메시지

### Object Properties
hvdc:belongsToSystem a owl:ObjectProperty ; rdfs:domain hvdc:Vessel, hvdc:Person, hvdc:Port, hvdc:Document ; rdfs:range hvdc:System .
hvdc:managedBy a owl:ObjectProperty ; rdfs:domain hvdc:Vessel ; rdfs:range hvdc:Person .
hvdc:operates a owl:ObjectProperty ; rdfs:domain hvdc:Person ; rdfs:range hvdc:Vessel .
hvdc:worksAt a owl:ObjectProperty ; rdfs:domain hvdc:Person ; rdfs:range hvdc:Port .
hvdc:performed a owl:ObjectProperty ; rdfs:domain hvdc:Person ; rdfs:range hvdc:Operation .
hvdc:uses a owl:ObjectProperty ; rdfs:domain hvdc:Operation ; rdfs:range hvdc:Equipment .
hvdc:references a owl:ObjectProperty ; rdfs:domain hvdc:Operation, hvdc:Document ; rdfs:range hvdc:Document, hvdc:Reference .
hvdc:scheduledAt a owl:ObjectProperty ; rdfs:domain hvdc:Operation ; rdfs:range hvdc:TimeTag .
hvdc:communicates a owl:ObjectProperty ; rdfs:domain hvdc:Person ; rdfs:range hvdc:Person .
hvdc:sameAs a owl:ObjectProperty ; owl:equivalentProperty owl:sameAs .

### Data Properties (keys)
hvdc:slug a owl:DatatypeProperty ; rdfs:range xsd:string .  # 정규화 이름
hvdc:key a owl:DatatypeProperty ; rdfs:range xsd:string .    # deterministic UUID5
hvdc:locode a owl:DatatypeProperty ; rdfs:range xsd:string . # (가능 시) UN/LOCODE
```

**JSON‑LD Context (요지)**
```json
{
  "@context": {
    "hvdc": "https://example.org/hvdc#",
    "System": "hvdc:System", "Vessel": "hvdc:Vessel", "Person": "hvdc:Person",
    "Port": "hvdc:Port", "Operation": "hvdc:Operation", "Document": "hvdc:Document",
    "Equipment": "hvdc:Equipment", "TimeTag": "hvdc:TimeTag", "Reference": "hvdc:Reference",
    "Message": "hvdc:Message",
    "belongsToSystem": {"@id": "hvdc:belongsToSystem", "@type": "@id"},
    "managedBy": {"@id": "hvdc:managedBy", "@type": "@id"},
    "sameAs": {"@id": "hvdc:sameAs", "@type": "@id"},
    "slug": "hvdc:slug", "key": "hvdc:key", "locode": "hvdc:locode"
  }
}
```

---

## 3) Identity & Dedupe (Deterministic UUID5)
- **Canonical Key**: `uuid5(NAMESPACE, entity_type + ':' + normalized_value)`
- **Normalization**: 대소문자/공백/하이픈/특수문자 제거, 다국어 동의어 사전 적용

```python
from uuid import uuid5, NAMESPACE_DNS
import re

def norm(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s

def make_key(kind: str, value: str) -> str:
    return str(uuid5(NAMESPACE_DNS, f"{kind}:{norm(value)}"))
```

**Blocking & Matching**
- 1차 블록: 동일 첫 글자/길이±1/토큰 수 일치
- 2차 매칭: Jaro‑Winkler ≥ 0.94 or Token‑set ratio ≥ 92
- 3차 승인: 역할/연락처/소속 교차(휴리스틱) + 수동 승인 큐(HIT 리뷰)

---

## 4) Normalization Dictionaries (초안)
```yaml
VESSEL_NORMALIZATION:
  THURAYA: ["thuraya", "th-uraya"]
  JPT71:   ["jpt71", "jpt-71", "jopetwil 71", "jptw71"]
  JPT62:   ["jpt62", "jptw62"]
  YEAM:    ["yeam"]

PERSON_NORMALIZATION:
  Haitham:  ["haitham", "haithem"]
  Shariff:  ["shariff", "shareef"]
  상욱:      ["상욱", "sangwook", "sw"]

PORT_NORMALIZATION:
  AGI: ["agi", "al ghallan island", "al-ghallan"]
  DAS: ["das", "das island"]
  MOSB: ["mosb", "musaffah base"]
  MW4: ["mw4", "mussafah wharf 4"]
```

---

## 5) SHACL Shapes (핵심 검증)
```ttl
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix hvdc: <https://example.org/hvdc#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

hvdc:VesselShape a sh:NodeShape ;
  sh:targetClass hvdc:Vessel ;
  sh:property [ sh:path hvdc:slug ; sh:minCount 1 ] ;
  sh:property [ sh:path hvdc:key ; sh:pattern "^[0-9a-f\-]{36}$" ] .

hvdc:PersonShape a sh:NodeShape ;
  sh:targetClass hvdc:Person ;
  sh:property [ sh:path hvdc:slug ; sh:minCount 1 ] ;
  sh:property [ sh:path hvdc:worksAt ; sh:minCount 0 ; sh:class hvdc:Port ] .

hvdc:PortShape a sh:NodeShape ;
  sh:targetClass hvdc:Port ;
  sh:property [ sh:path hvdc:locode ; sh:minCount 0 ; sh:datatype xsd:string ] .

hvdc:DocumentShape a sh:NodeShape ;
  sh:targetClass hvdc:Document ;
  sh:property [ sh:path hvdc:references ; sh:minCount 0 ] ;
  sh:property [ sh:path hvdc:belongsToSystem ; sh:minCount 1 ; sh:class hvdc:System ] .

hvdc:MessageShape a sh:NodeShape ;
  sh:targetClass hvdc:Message ;
  sh:property [ sh:path hvdc:communicates ; sh:minCount 0 ; sh:class hvdc:Person ] .
```

---

## 6) SPARQL – 품질/운영 질의
```sparql
# 미연결 메시지(엔티티 참조 실패)
PREFIX hvdc: <https://example.org/hvdc#>
SELECT ?msg WHERE {
  ?msg a hvdc:Message .
  FILTER NOT EXISTS { ?msg hvdc:communicates ?p }
}

# 사람↔선박 다중 매핑(중복 의심)
SELECT ?vessel (COUNT(DISTINCT ?p) AS ?ops) WHERE {
  ?vessel a hvdc:Vessel ; hvdc:managedBy ?p .
} GROUP BY ?vessel HAVING(COUNT(DISTINCT ?p) > 3)

# 시스템별 노드 분포
SELECT ?sys (COUNT(?e) AS ?cnt) WHERE {
  ?e hvdc:belongsToSystem ?sys .
} GROUP BY ?sys ORDER BY DESC(?cnt)
```

---

## 7) Graph Build – Python 스캐폴드
```python
# build_unified_network.py (skeleton)
import json, pandas as pd, networkx as nx
from pathlib import Path
from pyvis.network import Network
from uuid import uuid5, NAMESPACE_DNS
from collections import defaultdict

# ---- config
FILTER_OPTIONS = dict(min_connections=2, exclude_isolated=True, max_nodes=500, community_threshold=0.05)

# ---- util
norm = lambda s: " ".join(__import__('re').sub(r"[^\w\s]", "", s.lower()).split())
key  = lambda k,v: str(uuid5(NAMESPACE_DNS, f"{k}:{norm(v)}"))

# ---- loaders (TODO: replace with real data sources)
def load_jpt71_network():
    # return prebuilt nodes/edges or csvs
    return dict(vessels=["JPT71","Thuraya"], persons=["Haitham","Shariff"], ports=["AGI","DAS"])

def load_abu_data():
    return dict(vessels=["JPT71","JPT62","Yeam"], persons=["Haitham"], ports=["AGI","MW4","MOSB"])

def load_lightning_data():
    # documents/equipment/timetags/references as flat lists for demo
    return dict(documents=["BL","CICPA","PL","DO"], equipment=["trailer","crane","OT","FR"], timetags=["ETA","ETD"])    

# ---- build
G = nx.Graph(name="UNIFIED_LOGISTICS_NETWORK")

# systems
for sys in ["JPT71_System","ABU_System","Lightning_System"]:
    G.add_node(sys, type="system", label=sys)

# core entities (example only)
for v in set(load_jpt71_network()["vessels"] + load_abu_data()["vessels"]):
    vid = key("vessel", v)
    G.add_node(vid, type="vessel", label=v, slug=norm(v))
    G.add_edge(vid, "JPT71_System") if v in load_jpt71_network()["vessels"] else None
    G.add_edge(vid, "ABU_System")   if v in load_abu_data()["vessels"] else None

# persons
for p in set(load_jpt71_network()["persons"] + load_abu_data()["persons"]):
    pid = key("person", p)
    G.add_node(pid, type="person", label=p, slug=norm(p))

# simple sample links
for v in [n for n,d in G.nodes(data=True) if d.get("type")=="vessel"]:
    for p in [n for n,d in G.nodes(data=True) if d.get("type")=="person"]:
        G.add_edge(v, p, rel="managed_by")

# ---- community (Louvain optional)
try:
    import community as community_louvain
    part = community_louvain.best_partition(G)
    nx.set_node_attributes(G, part, "community")
except Exception:
    pass

# ---- export json
data = nx.readwrite.json_graph.node_link_data(G)
Path("unified_network_data.json").write_text(json.dumps(data, ensure_ascii=False))

# ---- interactive html
nt = Network(height="900px", width="100%", directed=False, notebook=False)
nt.barnes_hut()
for n,d in G.nodes(data=True):
    nt.add_node(n, label=d.get("label", n), title=str(d), group=d.get("type"))
for u,v,d in G.edges(data=True):
    nt.add_edge(u, v, title=d.get("rel","linked"))
nt.show("UNIFIED_LOGISTICS_NETWORK.html")
```

**Notes**
- 실제 로더는 CSV/Parquet/JSON‑LD/WhatsApp 텍스트 파서를 붙여 교체.
- 대규모 그래프는 **Sigma.js**(json) 내보내기 옵션으로 대체 가능.

---

## 8) Output Artifacts
- `UNIFIED_LOGISTICS_NETWORK.html` (pyvis)  
- `unified_network_data.json` (node‑link)  
- `unified_network_stats.json` (node/edge/k‑core/커뮤니티 요약)  
- `reports/analysis/UNIFIED_NETWORK_ANALYSIS_REPORT.md`  
- `reports/analysis/UNIFIED_NETWORK_COMPARISON.md`  
- PNG 렌더: `reports/analysis/image/UNIFIED_NETWORK/*.png`

---

## 9) Performance & Filters
- **Targets**: Build < **60.00 s**, HTML < **5.00 MB**, PNG < **0.50 MB**
- 필터: `min_connections=2`, `exclude_isolated=True`, `max_nodes=500`, `community_threshold=0.05`
- 캐시: 정규화 사전/키 매핑 `cache/*.json` (uuid5 안정화)

---

## 10) Community Detection (Expected 8–12)
1) JPT71 Ops, 2) Thuraya Ops, 3) AGI cluster, 4) DAS cluster, 5) Docs cluster, 6) Equipment cluster, 7) Lightning participants, 8) ABU participants, (9–12) 시점/프로젝트 하위군

---

## 11) Foundry Integration (옵션)
- **Ontology**: `hvdc.core` Types(Vessel/Person/Port/Document/Equipment/Message) + Relations(managedBy/worksAt/references/communicates)
- **Object Sets**: JPT71/ABU/Lightning/doc ingest 데이터셋 매핑
- **Pipelines**:
  - `OPI_JPT71/ABU/Lightning_ingest` → row‑level 정규화
  - `OPI_dedupe_linkage` → uuid5 + sameAs/LinkSet
  - `OPI_kg_export` → RDF/JSON‑LD + Quiver dataset
- **Workshop/Quiver**: 시각 대시보드(커뮤니티, KPI, 경보)

---

## 12) WhatsApp Fusion (요지)
- Message(header/attachments/tags) → EntityRef(Vessel/Port/Document/Equipment) 추출
- `[URGENT][ACTION][ETA]` 태그 → SLAClock 시작/해제
- `person→person`(communication), `person→document/equipment`(referenced) 생성

---

## 13) Validation & QA
- **Data Integrity**: 중복 제거율 ≥ **95.00%**, 정규화 정확도 ≥ **98.00%**
- **Network Quality**: 평균 차수 3–5, 커뮤니티 8–12, giant component ≥ 90%
- **Sampling**: Top‑degree/Betweenness 상위 20 노드 수동검증
- **Human‑Gate**: 동일인 후보(점수 0.90–0.94) 수동 승인 큐

---

## 14) Automation Hooks (Slash Cmd)
- `/ontology-mapper --unify JPT71 ABU Lightning docs`  
- `/logi-master kpi-dash --KRsummary`  
- `/automate_workflow network-build --export html,json --notify TG`  
- `/redo step` (사전/맵 업데이트 후 재빌드)

---

## 15) ZERO / Fail‑Safe (중단 로그 템플릿)
| 단계 | 이유 | 위험 | 요청데이터 | 다음조치 |
|---|---|---|---|---|
| normalize | 동의어 사전 누락(Thuraya 변형) | 중복 합치기 오류 | VESSEL_NORMALIZATION 최신판 | 사전 보강 후 재시도 |
| dedupe | Jaro‑W < 0.90 | 잘못된 sameAs | 원문 캡처·소스 라인 | 수동 승인 큐 배치 |
| link | Message→Entity 매핑 실패 | SLA 추적 누락 | 메시지 헤더 규칙/예시 | 헤더 패턴 강화 |

---

## 16) Roadmap (P→Pi→B→O→S)
- **Prepare**: 사전/동의어·키 정책 확정, CSV 스키마 고정  
- **Pilot**(1주): JPT71+ABU만으로 PoC(노드~250)  
- **Build**(2주): Lightning+docs 흡수, WhatsApp 파서 연결  
- **Operate**(2주): KPI/알림, 주간 리포트  
- **Scale**(N): Foundry 온톨로지·Quiver 연동  

**KPI**: Build SLA 60.00s 이내 95% 달성, 중복제거 ≥95.00%, 정규화 ≥98.00%, 커뮤니티 8–12 유지

---

## 17) Security & PII
- 이름만 원문 유지, 전화/이메일 마스킹(****)
- 소스별 접근권한 라벨링(RBAC), Provenance 기록

---

## 18) Test Plan (TDD‑Lite)
- Unit: norm(), make_key(), edge 생성기  
- Integration: dedupe 블록/매칭 ±케이스  
- E2E: ingest→normalize→dedupe→link→export→html 렌더  

---

## 19) Changelog
- v1.1: uuid5 기반 키, SHACL 핵심 Shape, SPARQL QA, pyvis HTML 스캐폴드 추가  
- v1.0: 사용자 계획 원안 정리

