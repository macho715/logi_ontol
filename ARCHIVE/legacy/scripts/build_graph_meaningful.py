#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JPT71 Meaningful Network Reconstruction
Based on ABU comprehensive data analysis
"""

import re, json
from pathlib import Path
import networkx as nx
from pyvis.network import Network
from PyPDF2 import PdfReader
import exifread
from networkx.algorithms.community import louvain_communities

DATA_JSON = "integration_data_meaningful.json"
OUT_HTML = "JPT71_MEANINGFUL_NETWORK.html"

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


def load_abu_data():
    """Load ABU comprehensive summary data"""
    abu_file = Path("reports/data/abu_comprehensive_summary.json")
    if not abu_file.exists():
        print(f"[ERROR] ABU data file not found: {abu_file}")
        return None

    with open(abu_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(
        f"[INFO] Loaded ABU data: {len(data['person_stats']['person_details'])} persons"
    )
    return data


def exif_datetime(exif_tags):
    """Extract datetime from EXIF tags"""
    for key in ("EXIF DateTimeOriginal", "Image DateTime", "EXIF DateTimeDigitized"):
        if key in exif_tags:
            return str(exif_tags.get(key))
    return None


def compute_louvain_colors(G: nx.Graph):
    """Louvain community detection with resolution optimization"""
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


def apply_community_colors_to_pyvis(net: Network, node2comm: dict):
    """Apply community colors to Pyvis network nodes"""
    for n in net.nodes:
        cid = node2comm.get(n["id"], -1)
        color = PALETTE[cid % len(PALETTE)] if cid >= 0 else "#334155"
        n["color"] = {"background": color, "border": "#0f172a"}


def build_meaningful_graph() -> nx.Graph:
    """Build meaningful network using ABU data"""
    G = nx.Graph()

    # Load ABU data
    abu_data = load_abu_data()
    if not abu_data:
        print("[ERROR] Cannot proceed without ABU data")
        return G

    persons = abu_data["person_stats"]["person_details"]
    keywords = abu_data["keyword_analysis"]["top_keywords"]

    # 1. Create JPT71 center node
    G.add_node(
        "vessel:JPT71",
        label="JPT71 (Jopetwil 71)",
        type="vessel",
        weight=1.0,
        color="#ff6b6b",
    )

    # 2. Create person nodes and connect to JPT71
    print(f"[INFO] Creating {len(persons)} person nodes...")
    for person_name, details in persons.items():
        person_id = f"person:{person_name}"
        G.add_node(
            person_id,
            label=person_name,
            type="person",
            shipments=details["shipments"],
            total_work=details["total"],
            color="#74c0fc",
        )
        # JPT71 -> person connection
        G.add_edge("vessel:JPT71", person_id, rel="managed_by", weight=details["total"])

    # 3. Create vessel nodes and connect to persons
    print("[INFO] Creating vessel nodes...")
    vessels_seen = set()
    for person_name, details in persons.items():
        person_id = f"person:{person_name}"
        for vessel_name in details["vessels"]:
            vessel_id = f"vessel:{vessel_name}"
            if vessel_id not in vessels_seen:
                G.add_node(vessel_id, label=vessel_name, type="vessel", color="#ff6b6b")
                vessels_seen.add(vessel_id)
            # person -> vessel connection
            G.add_edge(person_id, vessel_id, rel="operates", weight=1.0)

    # 4. Create port nodes and connect to persons
    print("[INFO] Creating port nodes...")
    ports_seen = set()
    for person_name, details in persons.items():
        person_id = f"person:{person_name}"
        for port_name in details["locations"]:
            port_id = f"port:{port_name}"
            if port_id not in ports_seen:
                G.add_node(port_id, label=port_name, type="port", color="#51cf66")
                ports_seen.add(port_id)
            # person -> port connection
            G.add_edge(person_id, port_id, rel="works_at", weight=1.0)

    # 5. Create operation nodes for major shipments
    print("[INFO] Creating operation nodes...")
    for person_name, details in persons.items():
        if details["shipments"] > 0:
            person_id = f"person:{person_name}"
            op_id = f"operation:{person_name}_shipments"
            G.add_node(
                op_id,
                label=f"{person_name} Shipments ({details['shipments']})",
                type="operation",
                count=details["shipments"],
                color="#ffd43b",
            )
            # person -> operation connection
            G.add_edge(person_id, op_id, rel="performed", weight=details["shipments"])

    # 6. Add existing JPT71 documents (361 images + 27 PDFs) - REMOVED
    # print("[INFO] Adding JPT71 documents...")
    # jpt_dir = Path("JPT71")
    # if jpt_dir.exists():
    #     img_count = 0
    #     pdf_count = 0
    #     for fp in jpt_dir.rglob("*"):
    #         suf = fp.suffix.lower()
    #         if suf in (".jpg", ".jpeg", ".png", ".webp"):
    #             try:
    #                 with open(fp, "rb") as fh:
    #                     tags = exifread.process_file(fh, details=False)
    #                 dt = exif_datetime(tags)
    #                 nid = f"doc:{fp.stem}"
    #                 G.add_node(
    #                     nid,
    #                     label=fp.name,
    #                     type="doc",
    #                     color="#a5d8ff",
    #                     meta={"DateTime": dt},
    #                 )
    #                 # Connect to JPT71
    #                 G.add_edge(
    #                     "vessel:JPT71", nid, rel="referenced", t=dt, color="#999999"
    #                 )
    #                 img_count += 1
    #             except Exception as e:
    #                 pass
    #         elif suf == ".pdf":
    #             try:
    #                 reader = PdfReader(str(fp))
    #                 meta = reader.metadata or {}
    #                 title = getattr(meta, "title", None)
    #                 author = getattr(meta, "author", None)
    #                 nid = f"doc:{fp.stem}"
    #                 G.add_node(
    #                     nid,
    #                     label=title or fp.name,
    #                     type="doc",
    #                     color="#ffa94d",
    #                     meta={"Author": author},
    #                 )
    #                 # Connect to JPT71
    #                 G.add_edge(
    #                     "vessel:JPT71", nid, rel="referenced", t=None, color="#999999"
    #                 )
    #                 pdf_count += 1
    #             except Exception as e:
    #                 pass
    #     print(f"[OK] Added {img_count} images, {pdf_count} PDFs from JPT71/")

    # 7. Try to connect documents to responsible persons based on author - REMOVED
    # print("[INFO] Connecting documents to responsible persons...")
    # author_mapping = {
    #     "EHAB ALGIFRI": "Haitham",  # Common author mapping
    #     "SERVER": "Shariff",  # Server documents often managed by Shariff
    # }

    # doc_connections = 0
    # for node_id in list(G.nodes()):
    #     if G.nodes[node_id].get("type") == "doc":
    #         author = G.nodes[node_id].get("meta", {}).get("Author")
    #         if author and author in author_mapping:
    #             person_name = author_mapping[author]
    #             person_id = f"person:{person_name}"
    #             if G.has_node(person_id):
    #                 G.add_edge(person_id, node_id, rel="created", weight=1.0)
    #                 doc_connections += 1

    # print(f"[OK] Connected {doc_connections} documents to responsible persons")

    return G


def export_json(G: nx.Graph, path: str):
    """Export graph to JSON"""
    nodes = [{"id": n, **G.nodes[n]} for n in G.nodes()]
    edges = [{"from": u, "to": v, **G.edges[u, v]} for u, v in G.edges()]
    Path(path).write_text(
        json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] Saved {path}")


def export_pyvis_html(G: nx.Graph, path_html: str, algorithm="louvain"):
    """Export to interactive HTML with community detection"""
    net = Network(height="900px", width="100%", bgcolor="#282828", font_color="#ffffff")
    net.from_nx(G)

    # Apply community detection and coloring
    if algorithm == "louvain":
        node2comm = compute_louvain_colors(G)
        apply_community_colors_to_pyvis(net, node2comm)
        print(
            f"[INFO] Applied Louvain community detection: {len(set(node2comm.values()))} communities"
        )
    else:
        node2comm = {}

    # Set vis-network options
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

    # HTML post-processing: timeline slider + PNG Export + Community legend
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
    a.download = 'JPT71_MEANINGFUL_NETWORK.png';
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
    print("JPT71 Meaningful Network Reconstruction (No Documents)")
    print("=" * 60)

    G = build_meaningful_graph()

    print(
        f"\n[STATS] Graph has {G.number_of_nodes()} nodes, {G.number_of_edges()} edges"
    )

    # Node type statistics
    node_types = {}
    for node in G.nodes():
        node_type = G.nodes[node].get("type", "unknown")
        node_types[node_type] = node_types.get(node_type, 0) + 1

    print(f"[STATS] Node types: {node_types}")

    export_json(G, DATA_JSON)
    export_pyvis_html(G, OUT_HTML)

    print("\n" + "=" * 60)
    print("[SUCCESS] Meaningful network generated!")
    print(f"  - {DATA_JSON}")
    print(f"  - {OUT_HTML}")
    print("=" * 60)
