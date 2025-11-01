#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Logistics Network Builder - Phase 1
Integrates JPT71, ABU, Lightning, and docs into a single network
"""

import json
import re
from pathlib import Path
from collections import defaultdict
import pandas as pd
import networkx as nx
from pyvis.network import Network
from networkx.algorithms.community import louvain_communities

# Output files
DATA_JSON = "unified_network_data.json"
STATS_JSON = "unified_network_stats.json"
OUT_HTML = "UNIFIED_LOGISTICS_NETWORK.html"

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

# Normalization dictionaries
VESSEL_NORMALIZATION = {
    "THURAYA": ["Thuraya", "thuraya", "THURAYA", "th-uraya"],
    "JPT71": ["JPT71", "Jpt71", "jpt71", "JPT-71", "JPTW71", "Jopetwil 71"],
    "JPT62": ["JPT62", "Jpt62", "jpt62", "JPTW62"],
    "YEAM": ["YEAM", "Yeam", "yeam"],
    "TAIBAH": ["TAIBAH", "Taibah", "taibah"],
}

PERSON_NORMALIZATION = {
    "Haitham": ["Haitham", "haitham", "HAITHAM", "haithem"],
    "Shariff": ["Shariff", "shariff", "SHARIFF", "shareef"],
    "상욱": ["상욱", "Sangwook", "SW", "sangwook"],
    "Thusar": ["Thusar", "thusar", "THUSAR"],
    "국일 Kim": ["국일 Kim", "국일", "Kim", "kim"],
    "ronpap20": ["ronpap20", "RONPAP20"],
}

PORT_NORMALIZATION = {
    "AGI": ["AGI", "agi", "Al Ghallan Island", "al-ghallan"],
    "DAS": ["DAS", "das", "Das Island"],
    "MOSB": ["MOSB", "mosb", "Musaffah Base"],
    "MW4": ["MW4", "mw4", "Mussafah Wharf 4"],
    "UMM_AL_ANBAR": ["UMM_AL_ANBAR", "Umm Al Anbar", "umm al anbar"],
}


def normalize_name(name: str, norm_dict: dict) -> str:
    """Normalize entity name using normalization dictionary"""
    name_lower = name.strip().lower()
    for canonical, variants in norm_dict.items():
        if name_lower in [v.lower() for v in variants]:
            return canonical
    return name.strip()


def load_jpt71_network() -> dict:
    """Load JPT71 48-node network data from abu_comprehensive_summary.json"""
    abu_file = Path("reports/data/abu_comprehensive_summary.json")

    if not abu_file.exists():
        print(f"[WARN] ABU data file not found: {abu_file}")
        return {"persons": {}, "vessels": [], "ports": []}

    with open(abu_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    persons = data.get("person_stats", {}).get("person_details", {})

    # Extract unique vessels and ports from person details
    vessels_set = set()
    ports_set = set()

    for person_data in persons.values():
        vessels_set.update(person_data.get("vessels", []))
        ports_set.update(person_data.get("locations", []))

    print(
        f"[INFO] Loaded JPT71 network: {len(persons)} persons, {len(vessels_set)} vessels, {len(ports_set)} ports"
    )

    return {"persons": persons, "vessels": list(vessels_set), "ports": list(ports_set)}


def load_abu_data() -> dict:
    """Load ABU comprehensive summary data"""
    return load_jpt71_network()  # Same data source


def load_lightning_data() -> pd.DataFrame:
    """Load Lightning CSV entities"""
    csv_file = Path("HVDC Project Lightning/Logistics_Entities__Summary_.csv")

    if not csv_file.exists():
        print(f"[WARN] Lightning CSV not found: {csv_file}")
        return pd.DataFrame()

    df = pd.read_csv(csv_file)
    print(f"[INFO] Loaded Lightning data: {len(df)} entities")

    return df


def load_docs_metadata() -> dict:
    """Load docs folder metadata"""
    docs_dir = Path("docs")

    if not docs_dir.exists():
        return {"files": []}

    files = list(docs_dir.rglob("*.md"))

    return {"files": [{"name": f.name, "path": str(f)} for f in files]}


def build_unified_graph() -> nx.Graph:
    """Build unified logistics network graph"""
    G = nx.Graph(name="UNIFIED_LOGISTICS_NETWORK")

    # Load all data sources
    jpt71_data = load_jpt71_network()
    abu_data = load_abu_data()
    lightning_df = load_lightning_data()
    docs_data = load_docs_metadata()

    # ===== Level 0: Root Node =====
    G.add_node(
        "HVDC_Project", type="root", label="HVDC Project", level=0, color="#ff0000"
    )

    # ===== Level 1: System Nodes =====
    systems = ["JPT71_System", "ABU_System", "Lightning_System"]
    system_colors = {
        "JPT71_System": "#ff6b6b",
        "ABU_System": "#51cf66",
        "Lightning_System": "#ffd43b",
    }

    for sys in systems:
        G.add_node(
            sys,
            type="system",
            label=sys.replace("_", " "),
            level=1,
            color=system_colors[sys],
        )
        G.add_edge("HVDC_Project", sys, rel="contains", weight=2.0)

    # ===== Level 2: Core Entities =====

    # Vessels
    vessels_set = set()
    for vessel in jpt71_data["vessels"]:
        normalized = normalize_name(vessel, VESSEL_NORMALIZATION)
        vessels_set.add(normalized)

    for vessel in vessels_set:
        vid = f"vessel:{vessel}"
        G.add_node(vid, type="vessel", label=vessel, level=2, color="#ff6b6b")
        G.add_edge("JPT71_System", vid, rel="contains", weight=1.5)

    print(f"[INFO] Added {len(vessels_set)} unique vessels")

    # Persons
    persons_set = set()
    person_data_map = {}

    for person_name, details in jpt71_data["persons"].items():
        normalized = normalize_name(person_name, PERSON_NORMALIZATION)
        persons_set.add(normalized)
        person_data_map[normalized] = details

    for person in persons_set:
        pid = f"person:{person}"
        details = person_data_map.get(person, {})

        G.add_node(
            pid,
            type="person",
            label=person,
            level=2,
            shipments=details.get("shipments", 0),
            total_work=details.get("total", 0),
            color="#74c0fc",
        )
        G.add_edge("JPT71_System", pid, rel="contains", weight=1.5)
        G.add_edge("ABU_System", pid, rel="contains", weight=1.5)

        # Connect persons to vessels they operate
        for vessel_raw in details.get("vessels", []):
            vessel_norm = normalize_name(vessel_raw, VESSEL_NORMALIZATION)
            vid = f"vessel:{vessel_norm}"
            if G.has_node(vid):
                G.add_edge(pid, vid, rel="operates", weight=1.0)

        # Connect persons to ports they work at
        for port_raw in details.get("locations", []):
            port_norm = normalize_name(port_raw, PORT_NORMALIZATION)
            port_id = f"port:{port_norm}"

            if not G.has_node(port_id):
                G.add_node(
                    port_id, type="port", label=port_norm, level=2, color="#51cf66"
                )
                G.add_edge("JPT71_System", port_id, rel="contains", weight=1.5)

            G.add_edge(pid, port_id, rel="works_at", weight=1.0)

        # Create operation node for persons with shipments
        if details.get("shipments", 0) > 0:
            op_id = f"operation:{person}_shipments"
            G.add_node(
                op_id,
                type="operation",
                label=f"{person} Shipments ({details['shipments']})",
                level=2,
                count=details["shipments"],
                color="#ffd43b",
            )
            G.add_edge("JPT71_System", op_id, rel="contains", weight=1.5)
            G.add_edge(pid, op_id, rel="performed", weight=details["shipments"] / 10)

    print(f"[INFO] Added {len(persons_set)} unique persons")

    # Ports (add any remaining from jpt71_data)
    for port_raw in jpt71_data["ports"]:
        port_norm = normalize_name(port_raw, PORT_NORMALIZATION)
        port_id = f"port:{port_norm}"

        if not G.has_node(port_id):
            G.add_node(port_id, type="port", label=port_norm, level=2, color="#51cf66")
            G.add_edge("JPT71_System", port_id, rel="contains", weight=1.5)

    # ===== Level 3: Lightning Entities =====

    if not lightning_df.empty:
        # Group by category and get top entities by count
        category_groups = lightning_df.groupby("Category")

        for category, group in category_groups:
            # Take top 20 entities per category to avoid overcrowding
            top_entities = group.nlargest(20, "Count")

            for _, row in top_entities.iterrows():
                entity = row["Entity"]
                count = row["Count"]

                if category == "Document":
                    node_id = f"doc:{entity}"
                    node_type = "document"
                    color = "#a5d8ff"
                elif category == "Equipment":
                    node_id = f"equip:{entity}"
                    node_type = "equipment"
                    color = "#ffa94d"
                elif category == "TimeTag":
                    node_id = f"time:{entity}"
                    node_type = "timetag"
                    color = "#b197fc"
                elif category == "Reference":
                    node_id = f"ref:{entity}"
                    node_type = "reference"
                    color = "#ffc9c9"
                else:
                    continue

                G.add_node(
                    node_id,
                    type=node_type,
                    label=f"{entity} ({count})",
                    level=3,
                    count=count,
                    color=color,
                )
                G.add_edge("Lightning_System", node_id, rel="contains", weight=0.5)

        print(f"[INFO] Added Lightning entities from {len(category_groups)} categories")

    # ===== Level 3: Docs Metadata =====

    for doc_file in docs_data.get("files", []):
        doc_id = f"docfile:{doc_file['name']}"
        G.add_node(
            doc_id,
            type="docfile",
            label=doc_file["name"],
            level=3,
            path=doc_file["path"],
            color="#e0e0e0",
        )
        G.add_edge("Lightning_System", doc_id, rel="contains", weight=0.5)

    print(f"[INFO] Added {len(docs_data.get('files', []))} doc files")

    return G


def detect_communities(G: nx.Graph) -> dict:
    """Detect communities using Louvain algorithm"""
    print("[INFO] Running Louvain community detection...")

    # Try different resolutions for 8-12 communities
    node2comm = {}
    best_communities = None
    best_resolution = None

    for resolution in [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]:
        try:
            communities = louvain_communities(G, resolution=resolution, seed=42)
            num_communities = len(communities)

            print(f"[INFO] Resolution {resolution}: {num_communities} communities")

            if 8 <= num_communities <= 12:
                best_communities = communities
                best_resolution = resolution
                break
            elif best_communities is None or abs(num_communities - 10) < abs(
                len(best_communities) - 10
            ):
                best_communities = communities
                best_resolution = resolution
        except Exception as e:
            print(f"[WARN] Louvain failed at resolution {resolution}: {e}")

    if best_communities:
        for cid, comm in enumerate(best_communities):
            for node in comm:
                node2comm[node] = cid

        print(
            f"[OK] Found {len(best_communities)} communities (resolution={best_resolution})"
        )
    else:
        print("[WARN] Louvain failed, using type-based communities")
        # Fallback to type-based communities
        type_communities = defaultdict(set)
        for node, data in G.nodes(data=True):
            node_type = data.get("type", "unknown")
            type_communities[node_type].add(node)

        for cid, (node_type, nodes) in enumerate(type_communities.items()):
            for node in nodes:
                node2comm[node] = cid

    return node2comm


def export_json(G: nx.Graph, path: str):
    """Export graph to JSON"""
    data = nx.readwrite.json_graph.node_link_data(G)
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[OK] Saved {path}")


def export_stats(G: nx.Graph, node2comm: dict, path: str):
    """Export network statistics to JSON"""
    # Node type distribution
    node_types = defaultdict(int)
    for _, data in G.nodes(data=True):
        node_types[data.get("type", "unknown")] += 1

    # Community sizes
    comm_sizes = defaultdict(int)
    for comm_id in node2comm.values():
        comm_sizes[comm_id] += 1

    stats = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "num_communities": len(set(node2comm.values())),
        "node_types": dict(node_types),
        "community_sizes": dict(comm_sizes),
        "avg_degree": (
            sum(dict(G.degree()).values()) / G.number_of_nodes()
            if G.number_of_nodes() > 0
            else 0
        ),
        "density": nx.density(G),
    }

    Path(path).write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[OK] Saved {path}")


def export_pyvis_html(G: nx.Graph, node2comm: dict, output_path: str):
    """Export to interactive HTML with Pyvis"""
    net = Network(height="900px", width="100%", bgcolor="#282828", font_color="#ffffff")
    net.from_nx(G)

    # Apply community colors
    for n in net.nodes:
        cid = node2comm.get(n["id"], -1)
        if cid >= 0:
            n["color"] = {
                "background": PALETTE[cid % len(PALETTE)],
                "border": "#0f172a",
            }
        else:
            n["color"] = {"background": "#334155", "border": "#0f172a"}

    # Set physics options
    options = {
        "nodes": {
            "shape": "dot",
            "size": 15,
            "borderWidth": 2,
            "font": {"color": "#ffffff", "size": 12},
        },
        "edges": {
            "smooth": {"type": "continuous"},
            "width": 1,
            "color": {"color": "#666666"},
        },
        "physics": {
            "solver": "barnesHut",
            "stabilization": {"iterations": 300},
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
    net.save_graph(output_path)

    # Post-process HTML to add toolbar, stats, legend
    html = Path(output_path).read_text(encoding="utf-8")

    inject_head = """
<style>
  body { margin: 0; padding: 0; background: #282828; font-family: 'Segoe UI', Arial, sans-serif; }
  #toolbar { position: absolute; left: 12px; top: 12px; z-index: 999; display: flex; gap: 8px; align-items: center; background: rgba(0,0,0,0.8); padding: 12px; border-radius: 8px; }
  .btn { padding: 8px 14px; background: #111827; border: 1px solid #374151; border-radius: 6px; color: #e6edf3; cursor: pointer; font-size: 13px; }
  .btn:hover { background: #1f2937; }
  #stats { position: absolute; right: 12px; top: 12px; z-index: 999; background: rgba(0,0,0,0.8); padding: 12px 16px; border-radius: 8px; color: #ffffff; font-size: 13px; }
  .stat-line { margin: 4px 0; }
  .stat-value { font-weight: bold; color: #4caf50; }
  #legend { position: absolute; left: 12px; top: 56px; z-index: 9; background: #0b1220; padding: 8px 10px; border: 1px solid #223; border-radius: 8px; }
  #legendColors { display: flex; gap: 6px; flex-wrap: wrap; max-width: 200px; }
  .legend-chip { display: inline-block; width: 14px; height: 14px; border-radius: 4px; border: 1px solid #0f172a; }
</style>
"""

    inject_body = f"""
<div id="toolbar">
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
  <div class="stat-line">Center: <span class="stat-value">HVDC Project</span></div>
</div>
<script>
  setTimeout(() => {{
    document.getElementById('stat-nodes').textContent = nodes.length;
    document.getElementById('stat-edges').textContent = edges.length;

    const communities = new Set();
    nodes.forEach(n => {{
      if (n.color && n.color.background) {{
        communities.add(n.color.background);
      }}
    }});
    document.getElementById('stat-communities').textContent = communities.size;

    const palette = {json.dumps(PALETTE)};
    document.getElementById('legendColors').innerHTML =
      palette.map(c => `<span class="legend-chip" style="background:${{c}}"></span>`).join('');
  }}, 1000);

  document.getElementById('btn-reset').onclick = () => {{
    if (window.network) window.network.fit({{ animation: true }});
  }};
</script>
"""

    html = html.replace("</head>", inject_head + "\n</head>")
    html = html.replace("</body>", inject_body + "\n</body>")

    Path(output_path).write_text(html, encoding="utf-8")
    print(f"[OK] Saved {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("Unified Logistics Network Builder - Phase 1")
    print("=" * 60)

    # Build graph
    G = build_unified_graph()

    print(
        f"\n[STATS] Graph has {G.number_of_nodes()} nodes, {G.number_of_edges()} edges"
    )

    # Node type statistics
    node_types = defaultdict(int)
    for _, data in G.nodes(data=True):
        node_types[data.get("type", "unknown")] += 1

    print(f"[STATS] Node types: {dict(node_types)}")

    # Detect communities
    node2comm = detect_communities(G)

    # Export files
    export_json(G, DATA_JSON)
    export_stats(G, node2comm, STATS_JSON)
    export_pyvis_html(G, node2comm, OUT_HTML)

    print("\n" + "=" * 60)
    print("[SUCCESS] Unified network generated!")
    print(f"  - {DATA_JSON}")
    print(f"  - {STATS_JSON}")
    print(f"  - {OUT_HTML}")
    print("=" * 60)
