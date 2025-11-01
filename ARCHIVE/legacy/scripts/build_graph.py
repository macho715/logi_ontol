# build_graph.py
# -*- coding: utf-8 -*-
"""
1) ABU/Lightning WhatsApp 파싱 → person/comm
2) JPT71 이미지/PDF 메타 추출 → doc
3) 중심 JPT71 연결 → integration_data.json 저장
4) Pyvis로 인터랙티브 HTML 생성 + 타임라인 슬라이더/PNG 버튼 주입
"""

import re, json
from pathlib import Path
import networkx as nx
from pyvis.network import Network
from PyPDF2 import PdfReader
import exifread
from networkx.algorithms.community import louvain_communities

DATA_JSON = "integration_data.json"
OUT_HTML = "JPT71_INTEGRATED_NETWORK.html"

# Community detection color palette
PALETTE = [
    "#60a5fa",
    "#10b981",
    "#f59e0b",
    "#a855f7",
    "#f43f5e",
    "#84cc16",
    "#38bdf8",
    "#eab308",
    "#f97316",
    "#22d3ee",
]


def parse_whatsapp_text(text: str):
    """
    WhatsApp 일반 포맷 예: [2025-10-05, 09:21] Name: message
    공지/미디어 줄은 스킵(필요시 규칙 확장)
    """
    pat = re.compile(r"^\[(?P<ts>[^]]+)\]\s+(?P<name>[^:]+):\s+(?P<msg>.+)$")
    for line in text.splitlines():
        m = pat.match(line.strip())
        if m:
            yield {"t": m["ts"], "name": m["name"].strip(), "msg": m["msg"].strip()}


def exif_datetime(exif_tags):
    # 표준 태그: EXIF DateTimeOriginal / Image DateTime 등
    for key in ("EXIF DateTimeOriginal", "Image DateTime", "EXIF DateTimeDigitized"):
        if key in exif_tags:
            return str(exif_tags.get(key))
    return None


def compute_louvain_colors(G: nx.Graph):
    """Louvain community detection using NetworkX built-in"""
    try:
        # Try different resolution values to get 5-15 communities
        for resolution in [0.1, 0.2, 0.5, 0.8, 1.0]:
            parts = louvain_communities(
                G, weight="weight", resolution=resolution, seed=42
            )
            if 5 <= len(parts) <= 15:  # Good number of communities
                print(
                    f"[INFO] Louvain found {len(parts)} communities with resolution={resolution}"
                )
                break
            elif len(parts) > 1 and len(parts) < 5:
                # Use this if it's the best we can get
                print(
                    f"[INFO] Louvain found {len(parts)} communities with resolution={resolution} (fewer than ideal)"
                )
                break
        else:
            # If still only 1 community, force split by node type
            print("[INFO] Louvain found only 1 community, using type-based communities")
            type_communities = {}
            for node in G.nodes():
                node_type = G.nodes[node].get("type", "unknown")
                if node_type not in type_communities:
                    type_communities[node_type] = len(type_communities)

            parts = [set() for _ in range(len(type_communities))]
            for node in G.nodes():
                node_type = G.nodes[node].get("type", "unknown")
                comm_id = type_communities[node_type]
                parts[comm_id].add(node)

        # node -> community id
        cmap = {}
        for cid, comm in enumerate(parts):
            for n in comm:
                cmap[n] = cid
        return cmap
    except Exception as e:
        print(f"[WARN] Louvain community detection failed: {e}")
        return {}


def compute_leiden_colors(G: nx.Graph):
    """Leiden community detection using igraph + leidenalg"""
    try:
        import igraph as ig
        import leidenalg as la

        # NetworkX 노드 인덱싱: 0..N-1
        nodes = list(G.nodes())
        idx = {n: i for i, n in enumerate(nodes)}
        edges = [(idx[u], idx[v]) for u, v in G.edges()]

        ig_g = ig.Graph(n=len(nodes), edges=edges)
        part = la.find_partition(ig_g, la.RBConfigurationVertexPartition)
        membership = part.membership

        # node -> community id
        cmap = {node: membership[i] for node, i in idx.items()}
        return cmap
    except ImportError:
        print("[WARN] igraph/leidenalg not available, skipping Leiden")
        return {}
    except Exception as e:
        print(f"[WARN] Leiden community detection failed: {e}")
        return {}


def apply_community_colors_to_pyvis(net: Network, node2comm: dict):
    """Apply community colors to Pyvis network nodes"""
    for n in net.nodes:
        cid = node2comm.get(n["id"], -1)
        color = PALETTE[cid % len(PALETTE)] if cid >= 0 else "#334155"
        n["color"] = {"background": color, "border": "#0f172a"}


def apply_dual_colors_to_pyvis(net: Network, node2comm: dict):
    """Apply type-based background + community-based border colors"""
    type_colors = {
        "vessel": "#ff6b6b",
        "person": "#74c0fc",
        "comm": "#ffd43b",
        "doc": "#a5d8ff",
        "port": "#51cf66",
        "entity": "#a5d8ff",
    }

    for n in net.nodes:
        node_type = n.get("type", "unknown")
        bg_color = type_colors.get(node_type, "#a5d8ff")

        cid = node2comm.get(n["id"], -1)
        border_color = PALETTE[cid % len(PALETTE)] if cid >= 0 else "#0f172a"

        n["color"] = {
            "background": bg_color,
            "border": border_color,
            "highlight": {"border": border_color},
        }


def build_graph() -> nx.Graph:
    G = nx.Graph()
    G.add_node(
        "vessel:JPT71",
        label="JPT71 (Jopetwil 71)",
        type="vessel",
        weight=1.0,
        color="#ff6b6b",
    )

    # 1) WhatsApp (ABU / Lightning)
    whatsapp_files = [
        "ABU/‎Abu Dhabi Logistics님과의 WhatsApp 대화.txt",
        "HVDC Project Lightning/‎[HVDC]⚡️Project lightning⚡️님과의 WhatsApp 대화.txt",
    ]

    for log_path in whatsapp_files:
        p = Path(log_path)
        if not p.exists():
            print(f"[SKIP] File not found")
            continue
        print(f"[INFO] Parsing WhatsApp log")
        txt = p.read_text(encoding="utf-8", errors="ignore")
        count = 0
        for r in parse_whatsapp_text(txt):
            pid = "person:" + r["name"]
            if not G.has_node(pid):
                G.add_node(pid, label=r["name"], type="person", color="#74c0fc")
                G.add_edge(
                    "vessel:JPT71", pid, rel="responsible", t=None, color="#999999"
                )

            mid = f"comm:{hash((r['t']+r['name']+r['msg']))}"
            G.add_node(
                mid,
                label=(r["msg"][:60] + "…") if len(r["msg"]) > 60 else r["msg"],
                type="comm",
                color="#ffd43b",
                meta={"t": r["t"]},
            )
            G.add_edge(pid, mid, rel="communication", t=r["t"], color="#666666")
            count += 1
        print(f"[OK] Extracted {count} messages")

    # 2) JPT71 이미지/PDF 메타
    jpt_dir = Path("JPT71")
    if jpt_dir.exists():
        img_count = 0
        pdf_count = 0
        for fp in jpt_dir.rglob("*"):
            suf = fp.suffix.lower()
            if suf in (".jpg", ".jpeg", ".png", ".webp"):
                try:
                    with open(fp, "rb") as fh:
                        tags = exifread.process_file(fh, details=False)
                    dt = exif_datetime(tags)
                    nid = f"doc:{fp.stem}"
                    G.add_node(
                        nid,
                        label=fp.name,
                        type="doc",
                        color="#a5d8ff",
                        meta={"DateTime": dt},
                    )
                    G.add_edge(
                        "vessel:JPT71", nid, rel="referenced", t=dt, color="#999999"
                    )
                    img_count += 1
                except Exception as e:
                    pass
            elif suf == ".pdf":
                try:
                    reader = PdfReader(str(fp))
                    meta = reader.metadata or {}
                    title = getattr(meta, "title", None)
                    author = getattr(meta, "author", None)
                    nid = f"doc:{fp.stem}"
                    G.add_node(
                        nid,
                        label=title or fp.name,
                        type="doc",
                        color="#ffa94d",
                        meta={"Author": author},
                    )
                    G.add_edge(
                        "vessel:JPT71", nid, rel="referenced", t=None, color="#999999"
                    )
                    pdf_count += 1
                except Exception as e:
                    pass
        print(f"[OK] Extracted {img_count} images, {pdf_count} PDFs from JPT71/")

    # 3) CSV entities (Lightning)
    csv_path = Path("HVDC Project Lightning/Logistics_Entities__Summary_.csv")
    if csv_path.exists():
        print(f"[INFO] Parsing CSV entities")
        import csv

        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            entity_count = 0
            for row in reader:
                entity_type = row.get("Type", "unknown").lower()
                entity_name = row.get("Name", "").strip()
                if not entity_name:
                    continue

                eid = f"entity:{entity_type}:{entity_name}"
                if entity_type == "port":
                    G.add_node(eid, label=entity_name, type="port", color="#51cf66")
                elif entity_type == "vessel":
                    G.add_node(eid, label=entity_name, type="vessel", color="#ff6b6b")
                else:
                    G.add_node(
                        eid, label=entity_name, type=entity_type, color="#a5d8ff"
                    )

                G.add_edge(
                    "vessel:JPT71", eid, rel="operation", t=None, color="#999999"
                )
                entity_count += 1
        print(f"[OK] Extracted {entity_count} entities from CSV")

    return G


def export_json(G: nx.Graph, path: str):
    nodes = [{"id": n, **G.nodes[n]} for n in G.nodes()]
    edges = [{"from": u, "to": v, **G.edges[u, v]} for u, v in G.edges()]
    Path(path).write_text(
        json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] Saved {path}")


def export_pyvis_html(G: nx.Graph, path_html: str, algorithm="louvain"):
    net = Network(height="900px", width="100%", bgcolor="#282828", font_color="#ffffff")
    net.from_nx(G)

    # Apply community detection and coloring
    if algorithm == "louvain":
        node2comm = compute_louvain_colors(G)
        apply_community_colors_to_pyvis(net, node2comm)
        print(
            f"[INFO] Applied Louvain community detection: {len(set(node2comm.values()))} communities"
        )
    elif algorithm == "leiden":
        node2comm = compute_leiden_colors(G)
        if node2comm:
            apply_community_colors_to_pyvis(net, node2comm)
            print(
                f"[INFO] Applied Leiden community detection: {len(set(node2comm.values()))} communities"
            )
        else:
            print("[WARN] Leiden failed, using original colors")
    else:
        node2comm = {}

    # Set vis-network options (JSON format only, no JavaScript)
    options = {
        "nodes": {
            "shape": "dot",
            "size": 15,
            "borderWidth": 2,
            "font": {"color": "#ffffff"},
        },
        "edges": {"smooth": {"type": "continuous"}, "width": 1},
        "physics": {
            "solver": "barnesHut",
            "stabilization": {"iterations": 200},
            "barnesHut": {
                "gravitationalConstant": -20000,
                "springLength": 150,
                "springConstant": 0.01,
            },
        },
        "interaction": {
            "hover": True,
            "navigationButtons": True,
            "keyboard": True,
            "tooltipDelay": 100,
        },
        "layout": {"improvedLayout": True},
    }
    net.set_options(json.dumps(options))
    net.save_graph(path_html)

    # HTML 후처리: 타임라인 슬라이더 + PNG Export 주입
    html = Path(path_html).read_text(encoding="utf-8")

    inject_head = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/nouislider@15.8.1/dist/nouislider.min.css">
<style>
  body { margin: 0; padding: 0; background: #282828; font-family: 'Segoe UI', Arial, sans-serif; }
  #toolbar { position: absolute; left: 12px; top: 12px; z-index: 999; display: flex; gap: 8px; align-items: center; background: rgba(0,0,0,0.8); padding: 12px; border-radius: 8px; }
  #range { width: 340px; }
  .btn { padding: 8px 14px; background: #111827; border: 1px solid #374151; border-radius: 6px; color: #e6edf3; cursor: pointer; font-size: 13px; }
  .btn:hover { background: #1f2937; }
  #stats { position: absolute; right: 12px; top: 12px; z-index: 999; background: rgba(0,0,0,0.8); padding: 12px 16px; border-radius: 8px; color: #ffffff; font-size: 13px; }
  .stat-line { margin: 4px 0; }
  .stat-value { font-weight: bold; color: #4caf50; }
  #legend { position: absolute; left: 12px; top: 56px; z-index: 9; background: #0b1220; padding: 8px 10px; border: 1px solid #223; border-radius: 8px; }
  #legendColors { display: flex; gap: 6px; flex-wrap: wrap; }
  .legend-chip { display: inline-block; width: 14px; height: 14px; border-radius: 4px; border: 1px solid #0f172a; }
</style>
"""
    inject_body = """
<div id="toolbar">
  <div id="range"></div>
  <button id="btn-export" class="btn">📸 Export PNG</button>
  <button id="btn-reset" class="btn">🔄 Reset View</button>
</div>
<div id="legend">
  <div style="margin-bottom:6px;font-weight:600">Communities</div>
  <div id="legendColors"></div>
</div>
<div id="stats">
  <div class="stat-line">Nodes: <span class="stat-value" id="stat-nodes">0</span></div>
  <div class="stat-line">Edges: <span class="stat-value" id="stat-edges">0</span></div>
  <div class="stat-line">Communities: <span class="stat-value" id="stat-communities">0</span></div>
  <div class="stat-line">Center: <span class="stat-value">JPT71</span></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/nouislider@15.8.1/dist/nouislider.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.min.js"></script>
<script>
  const container = document.getElementById('mynetwork');

  // Stats
  setTimeout(() => {
    document.getElementById('stat-nodes').textContent = nodes.length;
    document.getElementById('stat-edges').textContent = edges.length;

    // Community stats
    const communities = new Set();
    nodes.forEach(n => {
      if (n.color && n.color.background) {
        communities.add(n.color.background);
      }
    });
    document.getElementById('stat-communities').textContent = communities.size;

    // Community legend
    const palette = ["#60a5fa","#10b981","#f59e0b","#a855f7","#f43f5e","#84cc16","#38bdf8","#eab308","#f97316","#22d3ee"];
    document.getElementById('legendColors').innerHTML =
      palette.map(c => `<span class="legend-chip" style="background:${c}"></span>`).join('');
  }, 1000);

  // PNG Export
  document.getElementById('btn-export').onclick = async () => {
    const dataUrl = await htmlToImage.toPng(container, { pixelRatio: 2 });
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = 'JPT71_INTEGRATED_NETWORK.png';
    a.click();
  };

  document.getElementById('btn-reset').onclick = () => {
    if (window.network) window.network.fit({ animation: true });
  };

  // Timeline slider
  const times = [];
  edges.forEach(e => {
    const t = Date.parse(e.t || '1970-01-01');
    if (!isNaN(t)) times.push(t);
  });
  const minT = times.length ? Math.min(...times) : Date.parse('2025-08-27');
  const maxT = times.length ? Math.max(...times) : Date.parse('2025-10-21');
  const range = document.getElementById('range');

  noUiSlider.create(range, {
    start: [minT, maxT],
    connect: true,
    range: { min: minT, max: maxT },
    step: 24*3600*1000,
    tooltips: true,
    format: {
      to: v => new Date(v).toISOString().slice(0,10),
      from: v => Date.parse(v)
    }
  });

  range.noUiSlider.on('update', vals => {
    const lo = Date.parse(vals[0]), hi = Date.parse(vals[1]);
    edges.forEach(e => {
      const t = Date.parse(e.t || '1970-01-01');
      const hide = Number.isFinite(t) ? (t < lo || t > hi) : false;
      edges.update({ id: e.id, hidden: hide });
    });
  });
</script>
"""
    html = html.replace("</head>", inject_head + "\n</head>")
    html = html.replace("</body>", inject_body + "\n</body>")
    Path(path_html).write_text(html, encoding="utf-8")
    print(f"[OK] Saved {path_html}")


if __name__ == "__main__":
    print("=" * 60)
    print("JPT71 Integrated Network Visualization with Community Detection")
    print("=" * 60)

    G = build_graph()

    print(
        f"\n[STATS] Graph has {G.number_of_nodes()} nodes, {G.number_of_edges()} edges"
    )

    export_json(G, DATA_JSON)

    # Generate Louvain version
    louvain_html = "JPT71_INTEGRATED_NETWORK_LOUVAIN.html"
    export_pyvis_html(G, louvain_html, algorithm="louvain")

    # Generate Leiden version (if available)
    leiden_html = "JPT71_INTEGRATED_NETWORK_LEIDEN.html"
    export_pyvis_html(G, leiden_html, algorithm="leiden")

    print("\n" + "=" * 60)
    print("[SUCCESS] All files generated!")
    print(f"  - {DATA_JSON}")
    print(f"  - {louvain_html}")
    print(f"  - {leiden_html}")
    print("=" * 60)
