## ExecSummary (KR+EN-KR)

* 목표: **JPT71 중심**으로 4개 소스(JPT71·ABU·Lightning·Ontology)를 하나의 **인터랙티브 네트워크 HTML**로 통합. (Unify 4 sources into a JPT71-centric interactive network.)
* 스택: **Python ETL + NetworkX + Pyvis→vis-network**로 HTML 생성, 브라우저 측 **타임라인 슬라이더(noUiSlider)**·**PNG 익스포트(html-to-image)** 추가. ([Pyvis][1])
* 메타 추출: **PyPDF2**(PDF 메타), **ExifRead/EXIF.py**(이미지 EXIF)로 문서·이미지 시계열 정렬. ([PyPDF2][2])
* 가독성 강화(옵션): **Louvain/Leiden 커뮤니티 색상화**로 클러스터링 시각명료도↑. ([NetworkX][3])

---

# Plan 문서 (실행 우선)

## 0) 범위 & 가정 (Scope & Assumptions)

* 기간: **2025-08-27 ~ 2025-10-21**(JPT71 타임라인 기준, 절대날짜 고정).
* 파일 구조(가정):

  ```
  /JPT71/            # 이미지 101, PDF 13
  /ABU/              # whatsapp.txt, tags.csv(473)
  /Lightning/        # whatsapp.txt, images/, whatsapp_output/
  /ontology_unified/ # ttl/jsonld 등 온톨로지 정의
  ```
* 브라우저 배포: 단일 파일 `JPT71_INTEGRATED_NETWORK.html`을 열면 탐색 가능. (Single-file interactive report via Pyvis.) ([Pyvis][1])

---

## 1) 데이터 소스 정리 (Data Sources Analysis → 실행 포인트)

* **JPT71/**: EXIF(DateTimeOriginal, Model), PDF Metadata(Title, Author, CreateDate) 스캔 → `doc` 노드 + `referenced` 엣지 생성. ([PyPDF2][2])
* **ABU/**, **Lightning/**: WhatsApp 로그 파싱(날짜·발신자·본문) → `person`·`comm` 노드, `communication` 엣지 생성. (정규식·미디어 메시지 예외처리 포함)
* **ontology_unified/**: Port/Operation/Compliance 카테고리 → `onto` 노드, `categorized` 엣지로 매핑.

---

## 2) 공통 스키마 (JSON → NetworkX → Pyvis)

```json
{
  "nodes":[
    {"id":"vessel:JPT71","label":"JPT71","type":"vessel","weight":1.0},
    {"id":"person:Khemlal","label":"Khemlal","type":"person","meta":{"role":"Ops"}}
  ],
  "edges":[
    {"from":"vessel:JPT71","to":"person:Khemlal","rel":"responsible","t":"2025-10-05T09:21:00Z"},
    {"from":"person:Khemlal","to":"comm:abc123","rel":"communication","t":"2025-10-05T09:21:00Z"}
  ]
}
```

* Pyvis는 **NetworkX 그래프를 그대로 변환**(`from_nx`)하며 vis-network 옵션을 **`set_options` 문자열**로 주입. 옵션 구문 오류가 흔한 실패 원인이므로(콤마/따옴표) 린트 필수. ([Pyvis][1])

---

## 3) ETL 구현 (Step 1→2: Extraction & Mapping)

1. **WhatsApp 파서**

   * 패턴: `[YYYY-MM-DD, HH:MM] Name: message` 등 변형 허용(공지, 미디어).
   * 산출: `person:<name>`, `comm:<hash>` 노드 + `communication` 엣지(t 포함).

2. **CSV/엔티티 추출**

   * 333개 엔티티 CSV → `port`·`task` 등 타입 분류 규칙 맵핑 → `operation`/`responsible` 엣지.

3. **JPT71 PDF/이미지 메타**

   * **PyPDF2** `PdfReader(...).metadata` → Title/Author/Producer/Subject/Created. ([PyPDF2][2])
   * **ExifRead / EXIF.py** 로 DateTimeOriginal, Orientation, GPS(있을 시) 추출. ([PyPI][4])

4. **Ontology 매핑**

   * 클래스/속성을 `onto:<Class>` 노드로 투영, 해당 엔티티에 `categorized` 엣지 연결.

5. **중복 제거/정규화**

   * 닉네임/이명 머지 룰: `person_id = slugify(lower(name))` + alias dict.
   * 파일명 규칙(날짜 포함 시)으로 메타 누락 보완.

---

## 4) 그래프 생성 (Step 3: Generation)

* **중앙**: `vessel:JPT71`
* **Layer 1**: `person` / `port` / `task`
* **Layer 2**: `doc` / `comm` / `timeline`
* **Layer 3**: `onto`
* 커뮤니티(옵션): **NetworkX Louvain** → 군집별 색상 팔레트 적용. 대규모는 **Leiden(igraph+leidenalg)** 고려. ([NetworkX][3])

---

## 5) 시각화 생성 (Step 4: Visualization Creation)

* **Pyvis → vis-network**

  * `from_nx(G)`로 노드/엣지 투입. ([Pyvis][1])
  * 물리엔진: `barnesHut` 권장(일반 그래프), 계층 레이아웃 시 `hierarchicalRepulsion` 자동 적용. `stabilization` on. ([Vis.js][5])
  * 옵션 주입: `set_options("""const options = { nodes:{shape:'dot'}, physics:{solver:'barnesHut'}, ...};""")` (문법 주의) ([Pyvis][6])
* **인터랙션 UI(브라우저 측)**

  * **타임라인 슬라이더**: **noUiSlider**로 `t` 필드 범위 필터(일 단위 step). ([Refreshless][7])
  * **PNG Export**: **html-to-image**로 `#mynetwork` 캔버스 PNG 저장(1920×1080, `pixelRatio:2`). ([Stack Overflow][8])
  * (선택) 서버 사이드 스냅샷은 Playwright/헤드리스로 대체 가능.

---

## 6) 산출물 (Deliverables)

1. `integration_data.json` — 통합 그래프 데이터(노드/엣지).
2. `JPT71_INTEGRATED_NETWORK.html` — 단일 인터랙티브 리포트(Pyvis/vis-network 기반). ([Pyvis][1])
3. `JPT71_INTEGRATED_NETWORK.png` — PNG 익스포트(HTML 내 버튼). ([Stack Overflow][8])
4. `INTEGRATED_SYSTEM_REPORT.md` — 소스별 커버리지·허브 노드·경로 인사이트.

---

## 7) 구현 순서 & 체크리스트 (Timeline & QA)

**D0 — ETL (20~30m)**

* [ ] WhatsApp 2개 로그 파싱(ABU/Lightning)
* [ ] CSV 333 엔티티 매핑
* [ ] JPT71 PDF/이미지 메타 스캔(PyPDF2/EXIF) ([PyPDF2][2])
* [ ] `integration_data.json` 생성

**D0 — Viz (15~20m)**

* [ ] NetworkX → Pyvis 변환(`from_nx`) ([Pyvis][1])
* [ ] vis-network 옵션 튜닝(physics/layout/interaction) ([Vis.js][5])
* [ ] noUiSlider 범위 필터, PNG 버튼 주입 ([Refreshless][9])

**D0 — Docs (10m)**

* [ ] 노드/엣지 통계(수, 고립노드, 최다 degree, betweenness 상위 10)
* [ ] 커뮤니케이션 허브/주요 포트 Top-N

**QA 게이트**

* [ ] 옵션 문자열 구문 검사(`set_options` 실패 방지) ([GitHub][10])
* [ ] 대형 DOM PNG 프리즈 시 서버 사이드 스냅샷 대안 준비
* [ ] 커뮤니티 색상 적용(옵션): Louvain/Leiden 비교 ([NetworkX][3])

---

## 8) 코드 골격 (요지)

```python
# pip install pyvis networkx pypdf2 exifread
import re, json
import networkx as nx
from pathlib import Path
from pyvis.network import Network
from PyPDF2 import PdfReader                         # PDF meta  :contentReference[oaicite:22]{index=22}
import exifread                                      # EXIF meta :contentReference[oaicite:23]{index=23}

def parse_whatsapp(s):
    pat = re.compile(r'^\[(?P<ts>[^]]+)\]\s+(?P<name>[^:]+):\s+(?P<msg>.+)$')
    for line in s.splitlines():
        m = pat.match(line.strip())
        if m: yield m.groupdict()

G = nx.Graph()
G.add_node("vessel:JPT71", label="JPT71", type="vessel", weight=1.0)

# ABU / Lightning
for f in ["ABU/whatsapp.txt","Lightning/whatsapp.txt"]:
    if Path(f).exists():
        for r in parse_whatsapp(Path(f).read_text(encoding="utf-8",errors="ignore")):
            pid = "person:"+r["name"].strip()
            G.add_node(pid, label=r["name"], type="person")
            G.add_edge("vessel:JPT71", pid, rel="responsible", t=None)
            mid = f"comm:{hash(r['ts']+r['name']+r['msg'])}"
            G.add_node(mid, label=r["msg"][:40]+"…", type="comm", meta={"t":r["ts"]})
            G.add_edge(pid, mid, rel="communication", t=r["ts"])

# JPT71 images/PDF
for p in Path("JPT71").rglob("*"):
    if p.suffix.lower() in [".jpg",".jpeg",".png",".webp"]:
        with open(p,"rb") as fh: tags = exifread.process_file(fh, details=False)   # :contentReference[oaicite:24]{index=24}
        nod = f"doc:{p.stem}"
        G.add_node(nod, label=p.name, type="doc", meta={"DateTime": str(tags.get("EXIF DateTimeOriginal"))})
        G.add_edge("vessel:JPT71", nod, rel="referenced", t=str(tags.get("EXIF DateTimeOriginal")))
    elif p.suffix.lower()==".pdf":
        meta = (lambda r: r.metadata or {})(PdfReader(str(p)))                     # :contentReference[oaicite:25]{index=25}
        nod = f"doc:{p.stem}"
        G.add_node(nod, label=meta.title or p.name, type="doc", meta={"Author": getattr(meta,"author",None)})
        G.add_edge("vessel:JPT71", nod, rel="referenced", t=None)

# dump JSON (선택)
nodes = [{"id":n, **G.nodes[n]} for n in G.nodes()]
edges = [{"from":u,"to":v, **G.edges[u,v]} for u,v in G.edges()]
Path("integration_data.json").write_text(json.dumps({"nodes":nodes,"edges":edges},ensure_ascii=False,indent=2),encoding="utf-8")

# Pyvis
net = Network(height="900px", width="100%", bgcolor="#0b0f17", font_color="#e6edf3")  # :contentReference[oaicite:26]{index=26}
net.from_nx(G)
net.set_options("""
const options = {
  nodes:{shape:"dot", borderWidth:1},
  edges:{smooth:true, color:{inherit:false}},
  physics:{solver:"barnesHut", stabilization:true},
  interaction:{hover:true, navigationButtons:true, keyboard:true},
  layout:{improvedLayout:true}
};
""")  # vis-network 옵션 구조  :contentReference[oaicite:27]{index=27}
net.save_graph("JPT71_INTEGRATED_NETWORK.html")
```

---

## 9) 성능 & 차선책

* **vis-network 물리**: `barnesHut`/`stabilization` 튜닝으로 초기 배치 안정화. 계층은 `hierarchicalRepulsion` 자동. ([Vis.js][5])
* **대규모 시**: 군집별 메타노드(에지 스파스화), 필요하면 Playwright 스냅샷 배포.
* **옵션 파싱 오류**: `set_options` 이슈 레퍼런스 참고(문법 엄수). ([GitHub][10])

---

## 10) 성공 기준 (Success Criteria)

* 4개 소스 모두 반영, **JPT71 center** 명확.
* ≥ **100노드** & 상호작용 60fps 근접(중간 그래프).
* 다크 테마 일관성, **1920×1080 PNG** 정상 저장.
* 리포트에 허브·핵심 경로·기간 트렌드 포함.

---

### 참고/근거

* **Pyvis 튜토리얼/문서**(from_nx, set_options, 템플릿) ([Pyvis][1])
* **vis-network Physics/옵션**(barnesHut, hierarchicalRepulsion, stabilization) ([Vis.js][5])
* **noUiSlider**(옵션·레인지·이벤트) ([Refreshless][7])
* **html-to-image**(DOM→PNG) 실무 팁/사례 ([Stack Overflow][8])
* **PyPDF2 메타데이터**, **ExifRead/EXIF.py**(이미지 EXIF) ([PyPDF2][2])
* **Louvain/Leiden 커뮤니티**(NetworkX·leidenalg/igraph) ([NetworkX][3])

원하면 위 **Plan** 그대로 실행할 **스크립트·HTML 템플릿**을 바로 붙여서 드릴게.

[1]: https://pyvis.readthedocs.io/en/latest/tutorial.html?utm_source=chatgpt.com "Tutorial — pyvis 0.1.3.1 documentation - Read the Docs"
[2]: https://pypdf2.readthedocs.io/en/3.0.0/user/metadata.html?utm_source=chatgpt.com "Metadata - PyPDF2 documentation"
[3]: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html?utm_source=chatgpt.com "louvain_communities — NetworkX 3.5 documentation"
[4]: https://pypi.org/project/ExifRead/?utm_source=chatgpt.com "ExifRead"
[5]: https://visjs.github.io/vis-network/docs/network/physics.html?utm_source=chatgpt.com "Physics documentation. - vis.js"
[6]: https://pyvis.readthedocs.io/en/latest/documentation.html?utm_source=chatgpt.com "pyvis 0.1.3.1 documentation - Read the Docs"
[7]: https://refreshless.com/nouislider/?utm_source=chatgpt.com "noUiSlider - JavaScript Range Slider - Refreshless.com"
[8]: https://stackoverflow.com/questions/67514926/convert-html-to-a-png-image?utm_source=chatgpt.com "Convert HTML to a PNG Image - javascript"
[9]: https://refreshless.com/nouislider/slider-options/?utm_source=chatgpt.com "noUiSlider - Options and settings - Refreshless.com"
[10]: https://github.com/WestHealth/pyvis/issues/81?utm_source=chatgpt.com "set_options() not working · Issue #81 · WestHealth/pyvis"
