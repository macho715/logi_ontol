#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 v1.2 Stage 1 - HVDC v3.0 Ontology-based Network Builder
Based on ontology/HVDC.MD + ontology/core/1_CORE-01-hvdc-core-framework.md

References:
- ontology/HVDC.MD: 6개 물류 노드 (Ports 3개, MOSB, Sites 4개)
- ontology/core/1_CORE-01-hvdc-core-framework.md: 클래스/관계 정의
- ontology/core/1_CORE-02-hvdc-infra-nodes.md: 8거점 네트워크
"""

import json
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
import pandas as pd
import networkx as nx
from pyvis.network import Network
from networkx.algorithms.community import louvain_communities

# Import from existing builder
from build_unified_network import (
    PALETTE,
    VESSEL_NORMALIZATION,
    PERSON_NORMALIZATION,
    PORT_NORMALIZATION,
    normalize_name,
    load_jpt71_network,
    load_abu_data,
    load_lightning_data,
    load_docs_metadata,
)

# Output files
DATA_JSON = "unified_network_data_v12_hvdc.json"
STATS_JSON = "unified_network_stats_v12_hvdc.json"
OUT_HTML = "UNIFIED_LOGISTICS_NETWORK_v12_HVDC.html"

# HVDC 노드 정의 (ontology/HVDC.MD)
HVDC_NODES = {
    "ports": ["ZAYED_PORT", "KHALIFA_PORT", "JEBEL_ALI_PORT"],
    "hub": ["MOSB"],
    "onshore_sites": ["MIR", "SHU"],
    "offshore_sites": ["DAS", "AGI"],
}

# 온톨로지 클래스 매핑 (ontology/core/1_CORE-01)
ONTOLOGY_CLASS_MAPPING = {
    "port": "Location",
    "hub": "Location",
    "site": "Location",
    "vessel": "Asset",
    "person": "Party",
    "operation": "Process",
    "cargo": "Asset",
    "equipment": "Asset",
    "document": "Document",
    "permit": "Document",
    "timetag": "Event",
    "message": "Event",
}

# HVDC 관계 타입 (12종 - ontology/HVDC.MD + core/1_CORE-02)
HVDC_RELATIONS = {
    "belongs_to": {},
    "operates": {},
    "works_at": {},
    "performed": {},
    "same_as": {},
    "hosts": {},
    "consolidates": {},
    "dispatches": {},
    "handles": {},
    "transported_by": {},
    "stored_at": {},
    "requires_permit": {},
    "governed_by": {},
    "connected_to": {},
    "receives_from": {},
    "has_document": {},
}


def build_hvdc_infrastructure(G: nx.Graph) -> nx.Graph:
    """
    Build HVDC infrastructure layer (ontology/HVDC.MD)

    4-Level Hierarchy:
    L0: HVDC_Project (Root)
    L1: Systems (JPT71_System, ABU_System, HVDC_Infrastructure)
    L2: HVDC Nodes (Ports, MOSB, Sites)
    L3: Entities (vessels, persons, cargo, etc.)
    """

    # L0: Root
    G.add_node(
        "HVDC_Project",
        type="root",
        ontology_class="Project",
        label="HVDC Project",
        level=0,
        color="#ff0000",
    )

    # L1: Systems (3개)
    systems = {
        "JPT71_System": "#ff6b6b",
        "ABU_System": "#51cf66",
        "HVDC_Infrastructure": "#339af0",  # HVDC 노드 시스템
    }

    for sys, color in systems.items():
        G.add_node(
            sys,
            type="system",
            ontology_class="System",
            label=sys.replace("_", " "),
            level=1,
            color=color,
        )
        G.add_edge("HVDC_Project", sys, rel="belongs_to", weight=2.0)

    # L2: HVDC Nodes (8개 노드)
    # Ports (3개)
    port_data = {
        "ZAYED_PORT": {
            "label": "Zayed Port",
            "desc": "중량/벌크 화물 처리항",
            "code": "ADNOC 47150",
        },
        "KHALIFA_PORT": {"label": "Khalifa Port", "desc": "컨테이너 전용", "code": ""},
        "JEBEL_ALI_PORT": {
            "label": "Jebel Ali Port",
            "desc": "Free Zone",
            "code": "ADOPT",
        },
    }

    for port_id, data in port_data.items():
        G.add_node(
            port_id,
            type="port",
            ontology_class="Location",
            label=data["label"],
            description=data["desc"],
            customs_code=data["code"],
            level=2,
            color="#4ecdc4",
        )
        G.add_edge("HVDC_Infrastructure", port_id, rel="belongs_to", weight=1.5)

    # Hub (1개 - MOSB)
    G.add_node(
        "MOSB",
        type="hub",
        ontology_class="Location",
        label="MOSB (Mussafah Offshore Supply Base)",
        description="중앙 물류 허브",
        operator="ADNOC L&S",
        area_sqm=20000,
        sct_team="SCT 물류본부 상주",
        level=2,
        color="#ffd43b",
    )
    G.add_edge("HVDC_Infrastructure", "MOSB", rel="belongs_to", weight=1.5)

    # Onshore Sites (2개)
    onshore_data = {
        "MIR": {"label": "Mirfa Site", "laydown_sqm": 35000},
        "SHU": {"label": "Shuweihat Site", "laydown_sqm": 10500},
    }

    for site_id, data in onshore_data.items():
        G.add_node(
            site_id,
            type="site",
            ontology_class="Location",
            label=data["label"],
            site_type="onshore",
            laydown_area_sqm=data["laydown_sqm"],
            level=2,
            color="#99e9f2",
        )
        G.add_edge("HVDC_Infrastructure", site_id, rel="belongs_to", weight=1.5)

    # Offshore Sites (2개)
    offshore_data = {
        "DAS": {"label": "Das Island", "voyage_hours": 20},
        "AGI": {"label": "Al Ghallan Island", "voyage_hours": 10},
    }

    for site_id, data in offshore_data.items():
        G.add_node(
            site_id,
            type="site",
            ontology_class="Location",
            label=data["label"],
            site_type="offshore",
            voyage_from_mosb_hours=data["voyage_hours"],
            level=2,
            color="#74c0fc",
        )
        G.add_edge("HVDC_Infrastructure", site_id, rel="belongs_to", weight=1.5)

    return G


def add_hvdc_cargo_flow(G: nx.Graph) -> nx.Graph:
    """
    Add HVDC cargo flow relations (ontology/HVDC.MD)

    Flow: Port → MOSB → Sites
    """

    # 1. Port → MOSB (consolidates)
    for port in ["ZAYED_PORT", "KHALIFA_PORT", "JEBEL_ALI_PORT"]:
        G.add_edge(port, "MOSB", rel="feeds_into", weight=1.0)

    # 2. MOSB → Sites (dispatches)
    for site in ["MIR", "SHU", "DAS", "AGI"]:
        G.add_edge("MOSB", site, rel="dispatches", weight=1.0)

    # 3. DAS ↔ AGI (connected_to)
    G.add_edge("DAS", "AGI", rel="connected_to", weight=0.5)

    # 4. MOSB hosts SCT_Logistics_Team (Party node)
    G.add_node(
        "SCT_Logistics_Team",
        type="party",
        ontology_class="Party",
        label="SCT 물류본부",
        organization="Samsung C&T",
        location="MOSB",
        level=3,
        color="#ff6b6b",
    )
    G.add_edge("MOSB", "SCT_Logistics_Team", rel="hosts", weight=1.0)

    # 5. MOSB governed_by ADNOC_L&S
    G.add_node(
        "ADNOC_LS",
        type="party",
        ontology_class="Party",
        label="ADNOC Logistics & Services",
        organization="ADNOC",
        level=3,
        color="#51cf66",
    )
    G.add_edge("MOSB", "ADNOC_LS", rel="governed_by", weight=1.0)

    return G


def integrate_existing_data_with_hvdc(G: nx.Graph) -> nx.Graph:
    """
    Integrate existing JPT71/ABU data into HVDC infrastructure

    - JPT71 vessels/persons/operations → link to HVDC nodes
    - ABU data → link to MOSB/Ports/Sites
    """

    # Load existing data
    jpt71_data = load_jpt71_network()

    # L3: Entities (vessels, persons, operations)
    # Add vessels
    vessels_set = set()
    for vessel in jpt71_data.get("vessels", []):
        normalized = normalize_name(vessel, VESSEL_NORMALIZATION)
        vessels_set.add(normalized)

    for vessel in vessels_set:
        vid = f"vessel:{vessel}"
        G.add_node(
            vid,
            type="vessel",
            ontology_class="Asset",
            label=vessel,
            level=3,
            color="#e03131",
        )
        G.add_edge("JPT71_System", vid, rel="belongs_to", weight=1.0)

        # Link vessels to MOSB (operates_from)
        G.add_edge(vid, "MOSB", rel="operates_from", weight=0.5)

    # Add persons
    persons_dict = jpt71_data.get("persons", {})
    persons_set = set(persons_dict.keys())

    for person in persons_set:
        normalized = normalize_name(person, PERSON_NORMALIZATION)
        pid = f"person:{normalized}"
        G.add_node(
            pid,
            type="person",
            ontology_class="Party",
            label=normalized,
            level=3,
            color="#fd7e14",
        )
        G.add_edge("JPT71_System", pid, rel="belongs_to", weight=1.0)

        # Link persons to vessels (operates)
        person_data = persons_dict.get(person, {})
        for vessel_name in person_data.get("vessels", []):
            vessel_norm = normalize_name(vessel_name, VESSEL_NORMALIZATION)
            vessel_id = f"vessel:{vessel_norm}"
            if vessel_id in G.nodes:
                G.add_edge(pid, vessel_id, rel="operates", weight=0.5)

    # Add ports
    ports_set = set()
    for port in jpt71_data.get("ports", []):
        normalized = normalize_name(port, PORT_NORMALIZATION)
        ports_set.add(normalized)

    for port in ports_set:
        port_id = f"port:{port}"
        G.add_node(
            port_id,
            type="port",
            ontology_class="Location",
            label=port,
            level=3,
            color="#4ecdc4",
        )
        G.add_edge("JPT71_System", port_id, rel="belongs_to", weight=1.0)

        # Link to HVDC ports (if matching)
        if "AGI" in port.upper() or "AL_GHALLAN" in port.upper():
            G.add_edge(port_id, "AGI", rel="same_as", weight=1.0)
        elif "DAS" in port.upper():
            G.add_edge(port_id, "DAS", rel="same_as", weight=1.0)
        elif "MOSB" in port.upper() or "MUSSAFAH" in port.upper():
            G.add_edge(port_id, "MOSB", rel="same_as", weight=1.0)

    # Add operations (top 10 to avoid overcrowding)
    # Note: deliveries in person_data is a count (int), not a list
    # We'll create generic operation nodes based on person-vessel pairs instead
    operation_count = 0
    for person, person_data in list(persons_dict.items())[:5]:  # Limit to 5 persons
        person_norm = normalize_name(person, PERSON_NORMALIZATION)
        for vessel_name in person_data.get("vessels", [])[
            :2
        ]:  # Max 2 vessels per person
            vessel_norm = normalize_name(vessel_name, VESSEL_NORMALIZATION)
            op_id = f"operation:delivery_{person_norm}_{vessel_norm}"
            G.add_node(
                op_id,
                type="operation",
                ontology_class="Process",
                label=f"Delivery by {person_norm} on {vessel_norm}",
                level=3,
                color="#20c997",
            )
            G.add_edge("JPT71_System", op_id, rel="belongs_to", weight=1.0)

            # Link operation to person and vessel
            person_id = f"person:{person_norm}"
            vessel_id = f"vessel:{vessel_norm}"
            if person_id in G.nodes:
                G.add_edge(person_id, op_id, rel="performed", weight=0.5)
            if vessel_id in G.nodes:
                G.add_edge(op_id, vessel_id, rel="uses", weight=0.5)

            operation_count += 1
            if operation_count >= 10:  # Stop at 10 operations
                break
        if operation_count >= 10:
            break

    return G


def build_identity_graph_hvdc(G: nx.Graph) -> nx.Graph:
    """Build identity graph with same_as links"""

    # 1. Vessel deduplication
    vessels = [n for n, d in G.nodes(data=True) if d.get("type") == "vessel"]
    for i, v1 in enumerate(vessels):
        label1 = G.nodes[v1]["label"]
        for v2 in vessels[i + 1 :]:
            label2 = G.nodes[v2]["label"]
            norm1 = normalize_name(label1, VESSEL_NORMALIZATION)
            norm2 = normalize_name(label2, VESSEL_NORMALIZATION)
            if norm1 == norm2:
                G.add_edge(v1, v2, rel="same_as", weight=1.0)
            elif SequenceMatcher(None, label1.lower(), label2.lower()).ratio() >= 0.85:
                G.add_edge(v1, v2, rel="same_as", weight=0.9)

    # 2. Port deduplication (similar logic)
    ports = [
        n
        for n, d in G.nodes(data=True)
        if d.get("type") == "port" and d.get("level") == 3
    ]
    for i, p1 in enumerate(ports):
        label1 = G.nodes[p1]["label"]
        for p2 in ports[i + 1 :]:
            label2 = G.nodes[p2]["label"]
            norm1 = normalize_name(label1, PORT_NORMALIZATION)
            norm2 = normalize_name(label2, PORT_NORMALIZATION)
            if norm1 == norm2:
                G.add_edge(p1, p2, rel="same_as", weight=1.0)

    # 3. Person deduplication
    persons = [n for n, d in G.nodes(data=True) if d.get("type") == "person"]
    for i, p1 in enumerate(persons):
        label1 = G.nodes[p1]["label"]
        for p2 in persons[i + 1 :]:
            label2 = G.nodes[p2]["label"]
            norm1 = normalize_name(label1, PERSON_NORMALIZATION)
            norm2 = normalize_name(label2, PERSON_NORMALIZATION)
            if norm1 == norm2:
                G.add_edge(p1, p2, rel="same_as", weight=1.0)

    return G


def add_inference_rules(G: nx.Graph) -> nx.Graph:
    """
    Apply ontological inference rules (p.md 5.1)

    Rules:
    1. Transitive Property: Vessel operates_from MOSB AND MOSB dispatches Site → Vessel indirectly_serves Site
    2. Cargo Flow Path: Vessel operates_from MOSB AND MOSB receives_from Port → Vessel flows_through Port
    3. Critical Path Detection: Operation.performed_by Person AND Person.operates Vessel AND Vessel.operates_from MOSB → Operation.criticality = HIGH
    4. Co-Location Clustering: Vessels operating_from same location → co_located_with
    """

    # Rule 1: Transitive Property (indirectly_serves)
    for vessel in [n for n, d in G.nodes(data=True) if d.get("type") == "vessel"]:
        if G.has_edge(vessel, "MOSB"):
            for site in ["MIR", "SHU", "DAS", "AGI"]:
                if G.has_edge("MOSB", site):
                    # Check if edge already exists
                    if not G.has_edge(vessel, site):
                        G.add_edge(
                            vessel,
                            site,
                            rel="indirectly_serves",
                            weight=0.3,
                            inferred=True,
                        )

    # Rule 2: Cargo Flow Path (flows_through)
    for vessel in [n for n, d in G.nodes(data=True) if d.get("type") == "vessel"]:
        if G.has_edge(vessel, "MOSB"):
            for port in ["ZAYED_PORT", "KHALIFA_PORT", "JEBEL_ALI_PORT"]:
                if G.has_edge(port, "MOSB") or G.has_edge("MOSB", port):
                    # Check if edge already exists
                    if not G.has_edge(vessel, port):
                        G.add_edge(
                            vessel,
                            port,
                            rel="flows_through",
                            weight=0.4,
                            inferred=True,
                        )

    # Rule 3: Critical Path Detection
    for op in [n for n, d in G.nodes(data=True) if d.get("type") == "operation"]:
        # Count dependency chain depth
        depth = 0
        for neighbor in G.neighbors(op):
            if G.nodes[neighbor].get("type") == "person":
                depth += 1
                for vessel_neighbor in G.neighbors(neighbor):
                    if G.nodes[vessel_neighbor].get("type") == "vessel":
                        depth += 1
                        if G.has_edge(vessel_neighbor, "MOSB"):
                            depth += 1

        # Mark as critical if depth >= 3
        if depth >= 3:
            G.nodes[op]["criticality"] = "HIGH"
            G.nodes[op]["dependency_depth"] = depth
            G.nodes[op]["inferred"] = True

    # Rule 4: Co-Location Clustering
    location_groups = defaultdict(list)
    for vessel in [n for n, d in G.nodes(data=True) if d.get("type") == "vessel"]:
        for neighbor in G.neighbors(vessel):
            if G.nodes[neighbor].get("type") in ["hub", "port", "site"]:
                location_groups[neighbor].append(vessel)

    for location, vessels in location_groups.items():
        if len(vessels) > 1:
            for i, vessel_a in enumerate(vessels):
                for vessel_b in vessels[i + 1 :]:
                    # Check if edge already exists
                    if not G.has_edge(vessel_a, vessel_b):
                        G.add_edge(
                            vessel_a,
                            vessel_b,
                            rel="co_located_with",
                            weight=0.2,
                            inferred=True,
                            location=location,
                        )

    return G


def validate_hvdc_ontology(G: nx.Graph) -> dict:
    """Validate HVDC v3.0 ontology compliance"""

    results = {}

    # 1. HVDC 노드 존재 확인
    hvdc_nodes_present = []
    for node in [
        "ZAYED_PORT",
        "KHALIFA_PORT",
        "JEBEL_ALI_PORT",
        "MOSB",
        "MIR",
        "SHU",
        "DAS",
        "AGI",
    ]:
        if node in G.nodes:
            hvdc_nodes_present.append(node)

    results["hvdc_nodes_count"] = len(hvdc_nodes_present)
    results["hvdc_nodes_list"] = hvdc_nodes_present

    # 2. Cargo flow 검증 (Port → MOSB → Sites)
    mosb_incoming = [u for u, v in G.edges() if v == "MOSB"]
    mosb_outgoing = [v for u, v in G.edges() if u == "MOSB"]

    results["mosb_incoming"] = len(mosb_incoming)
    results["mosb_outgoing"] = len(mosb_outgoing)

    # 3. 관계 타입 (목표: 12종+)
    edge_types = set([d.get("rel") for u, v, d in G.edges(data=True)])
    results["edge_types_count"] = len(edge_types)
    results["edge_types_list"] = sorted(edge_types)

    # 4. 온톨로지 클래스 커버리지
    ontology_classes = set(
        [
            d.get("ontology_class")
            for n, d in G.nodes(data=True)
            if "ontology_class" in d
        ]
    )
    results["ontology_classes"] = sorted(ontology_classes)

    # 5. same_as 링크
    same_as_edges = [
        (u, v) for u, v, d in G.edges(data=True) if d.get("rel") == "same_as"
    ]
    results["same_as_links"] = len(same_as_edges)

    # 6. 평균 차수
    if G.number_of_nodes() > 0:
        results["avg_degree"] = sum(dict(G.degree()).values()) / G.number_of_nodes()
    else:
        results["avg_degree"] = 0

    # 7. 노드/엣지 통계
    results["total_nodes"] = G.number_of_nodes()
    results["total_edges"] = G.number_of_edges()

    # 8. 추론된 관계 (inferred edges)
    inferred_edges = [
        (u, v, d.get("rel"))
        for u, v, d in G.edges(data=True)
        if d.get("inferred") == True
    ]
    results["inferred_edges_count"] = len(inferred_edges)
    results["inferred_relation_types"] = sorted(
        set([rel for u, v, rel in inferred_edges])
    )

    # 9. Critical path operations (criticality = HIGH)
    critical_ops = [n for n, d in G.nodes(data=True) if d.get("criticality") == "HIGH"]
    results["critical_operations"] = len(critical_ops)

    print("\n" + "=" * 60)
    print("[HVDC v3.0 ONTOLOGY VALIDATION]")
    print("=" * 60)
    print(f"[OK] HVDC Nodes: {results['hvdc_nodes_count']}/8")
    print(f"     {results['hvdc_nodes_list']}")
    print(
        f"[OK] MOSB Hub: {results['mosb_incoming']} incoming, {results['mosb_outgoing']} outgoing"
    )
    print(f"[OK] Edge types: {results['edge_types_count']} (target: >=12)")
    print(f"     {results['edge_types_list']}")
    print(f"[OK] Ontology classes: {results['ontology_classes']}")
    print(f"[OK] Same_as links: {results['same_as_links']}")
    print(f"[OK] Avg degree: {results['avg_degree']:.2f} (target: >=3.2)")
    print(f"[OK] Total: {results['total_nodes']} nodes, {results['total_edges']} edges")
    print(f"[OK] Inferred edges: {results['inferred_edges_count']}")
    print(f"     Types: {results['inferred_relation_types']}")
    print(f"[OK] Critical operations: {results['critical_operations']}")
    print("=" * 60)

    return results


def export_json(G: nx.Graph, output_path: str):
    """Export graph to JSON (node-link format)"""
    data = nx.node_link_data(G)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Exported graph to {output_path}")


def export_stats(G: nx.Graph, validation: dict, output_path: str):
    """Export network statistics to JSON"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(validation, f, ensure_ascii=False, indent=2)
    print(f"[OK] Exported stats to {output_path}")


def export_pyvis_html(G: nx.Graph, output_path: str):
    """Export interactive HTML visualization using Pyvis"""
    net = Network(
        height="900px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#333333",
        directed=False,
    )

    # Add nodes
    for node, data in G.nodes(data=True):
        net.add_node(
            node,
            label=data.get("label", node),
            color=data.get("color", "#97c2fc"),
            title=f"{data.get('label', node)}\nType: {data.get('type', 'unknown')}\nOntology: {data.get('ontology_class', 'N/A')}",
            size=20 if data.get("level") <= 1 else 15,
        )

    # Add edges
    for u, v, data in G.edges(data=True):
        net.add_edge(
            u,
            v,
            title=data.get("rel", ""),
            width=data.get("weight", 1) * 2,
            color="#cccccc",
        )

    # Set options
    options = {
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -30000,
                "centralGravity": 0.3,
                "springLength": 200,
                "springConstant": 0.04,
                "damping": 0.09,
            },
        },
        "nodes": {"font": {"size": 14}},
        "edges": {"smooth": {"type": "continuous"}},
        "interaction": {"hover": True, "tooltipDelay": 100},
    }

    net.set_options(json.dumps(options))
    net.save_graph(output_path)
    print(f"[OK] Exported HTML to {output_path}")

    # Inject Pro UI features
    patch_html_with_pro_ui(output_path)
    print(f"[OK] Pro UI features injected")


def aggregate_by_community(G: nx.Graph, node2comm: dict) -> nx.Graph:
    """
    Create meta-graph by aggregating nodes by community

    Returns:
        H: Meta-graph where each node is a community
    """
    H = nx.Graph()

    # Create super-nodes (one per community)
    communities = set(node2comm.values())
    for cid in communities:
        H.add_node(
            f"comm:{cid}",
            label=f"Community {cid}",
            type="community",
            community_id=cid,
            color=PALETTE[cid % len(PALETTE)],
        )

    # Aggregate inter-community edges
    for u, v, d in G.edges(data=True):
        cu, cv = node2comm.get(u), node2comm.get(v)
        if cu is None or cv is None:
            continue
        if cu == cv:  # Skip intra-community edges
            continue

        a, b = (f"comm:{cu}", f"comm:{cv}")
        w = d.get("weight", 1.0)

        if H.has_edge(a, b):
            H[a][b]["weight"] += w
        else:
            H.add_edge(a, b, weight=w, rel="community-bridge")

    return H


def patch_html_with_pro_ui(html_path: str) -> None:
    """Inject Pro UI features into Pyvis HTML"""
    html = Path(html_path).read_text(encoding="utf-8")

    # Head injection (CSS + CDN)
    head_inject = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/nouislider@15.8.1/dist/nouislider.min.css">
<style>
  #pro-toolbar{position:absolute;left:12px;top:12px;z-index:9;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  #pro-toolbar .btn{padding:6px 10px;background:#111827;border:1px solid #374151;border-radius:8px;color:#e6edf3;cursor:pointer}
  #searchBox{min-width:240px;padding:6px 10px;background:#0f172a;border:1px solid #374151;border-radius:8px;color:#e6edf3}
  #legend{position:absolute;left:12px;top:56px;z-index:9;background:#0b1220;padding:8px 10px;border:1px solid #223;border-radius:8px;max-width:320px}
  .chip{display:inline-block;width:14px;height:14px;border-radius:4px;border:1px solid #0f172a;margin-right:6px}
</style>
"""
    html = html.replace("</head>", head_inject + "\n</head>")

    # Body injection (UI + JS)
    body_inject = r"""
<div id="pro-toolbar">
  <input id="searchBox" placeholder="Search label/type/ontology…" />
  <button id="btn-cluster-zoom" class="btn">Cluster on Zoom</button>
  <button id="btn-uncluster" class="btn">Uncluster All</button>
  <button id="btn-centrality" class="btn">Size by Centrality</button>
  <button id="btn-export" class="btn">Export PNG</button>
  <button id="btn-fit" class="btn">Fit</button>
  <button id="btn-config" class="btn">Config Panel</button>
  <button id="btn-cluster-cid" class="btn">Cluster by Community</button>
  <button id="btn-meta" class="btn">Meta View (Communities)</button>
</div>
<div id="legend">
  <div style="margin-bottom:6px;font-weight:600">HVDC Network</div>
  <div id="legendColors" style="display:flex;gap:6px;flex-wrap:wrap"></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/nouislider@15.8.1/dist/nouislider.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.min.js"></script>
<script>
(function(){
  if(!window.network){ console.warn("network not ready"); return; }

  // Community legend chips
  const PALETTE = ["#60a5fa","#10b981","#f59e0b","#a855f7","#f43f5e","#84cc16","#38bdf8","#eab308","#f97316","#22d3ee"];
  document.getElementById('legendColors').innerHTML =
    PALETTE.map(c=>`<span class="chip" style="background:${c}"></span>`).join('');

  // Zoom-based clustering
  let clusterOnZoom = false;
  function clusterByZoomLevel(){
    const zoom = network.getScale();
    if(zoom < 0.7){
      const options = {
        processProperties: function(clusterOptions, childNodes){
          clusterOptions.label = "Cluster ("+childNodes.length+")";
          clusterOptions.borderWidth = 2;
          return clusterOptions;
        },
        clusterNodeProperties: { id: 'zoomCluster', allowSingleNodeCluster: true }
      };
      network.cluster(options);
    } else {
      try{ network.openCluster('zoomCluster'); }catch(e){}
      network.uncluster();
    }
  }
  network.on("zoom", () => { if(clusterOnZoom) clusterByZoomLevel(); });
  document.getElementById('btn-cluster-zoom').onclick = ()=>{
    clusterOnZoom = !clusterOnZoom;
    if(!clusterOnZoom) network.uncluster(); else clusterByZoomLevel();
    document.getElementById('btn-cluster-zoom').textContent = clusterOnZoom ? "Cluster on Zoom ✓" : "Cluster on Zoom";
  };
  document.getElementById('btn-uncluster').onclick = ()=> network.uncluster();

  // Search/highlight
  const originalColors = {};
  nodes.forEach(n => { originalColors[n.id] = n.color; });
  function clearHighlight(){
    nodes.forEach(n => nodes.update({id:n.id, hidden:false, color: originalColors[n.id]}));
  }
  document.getElementById('searchBox').addEventListener('input', (e)=>{
    const q = e.target.value.trim().toLowerCase();
    if(!q){ clearHighlight(); return; }
    nodes.forEach(n => {
      const label = (n.label||"").toLowerCase();
      const type  = (n.group||n.type||"").toLowerCase();
      const onto  = (n.ontology_class||"").toLowerCase();
      const hit = label.includes(q) || type.includes(q) || onto.includes(q);
      nodes.update({id:n.id, hidden: !hit});
    });
  });

  // Centrality sizing toggle
  let sizedByCentrality = false;
  document.getElementById('btn-centrality').onclick = ()=>{
    sizedByCentrality = !sizedByCentrality;
    if(!sizedByCentrality){
      nodes.forEach(n => nodes.update({id:n.id, size: n.baseSize || 15}));
      document.getElementById('btn-centrality').textContent = "Size by Centrality";
      return;
    }
    const degree = {};
    edges.forEach(e => { degree[e.from]=(degree[e.from]||0)+1; degree[e.to]=(degree[e.to]||0)+1; });
    const maxDeg = Math.max(1, ...Object.values(degree));
    nodes.forEach(n => {
      const d = degree[n.id] || 1;
      const size = Math.max(8, Math.min(36, 12 + (d/maxDeg)*24));
      n.baseSize = n.baseSize || n.size || 15;
      nodes.update({id:n.id, size});
    });
    document.getElementById('btn-centrality').textContent = "Size by Centrality ✓";
  };

  // PNG Export & Fit
  document.getElementById('btn-export').onclick = async ()=>{
    if(window.htmlToImage){
      const dataUrl = await htmlToImage.toPng(document.getElementById('mynetwork'), { pixelRatio: 2 });
      const a = document.createElement('a'); a.href = dataUrl; a.download = 'HVDC_NETWORK_v12.png'; a.click();
    } else { alert("html-to-image not found."); }
  };
  document.getElementById('btn-fit').onclick = ()=> network.fit({animation:true});

  // Config Panel toggle
  let configuratorOn = false;
  document.getElementById('btn-config').onclick = ()=>{
    configuratorOn = !configuratorOn;
    network.setOptions({ configure: configuratorOn ? { filter: ['physics','layout','interaction','nodes','edges'] } : false });
    document.getElementById('btn-config').textContent = configuratorOn ? "Config Panel ✓" : "Config Panel";
  };

  // Timeline slider (edge.t filter)
  const times = [];
  edges.forEach(e => { const t = Date.parse(e.t || '1970-01-01'); if(!isNaN(t)) times.push(t); });
  const minT = times.length ? Math.min(...times) : Date.parse('1970-01-01');
  const maxT = times.length ? Math.max(...times) : Date.now();
  const rangeDiv = document.createElement('div');
  rangeDiv.id = 'range';
  rangeDiv.style.position = 'absolute';
  rangeDiv.style.right = '12px';
  rangeDiv.style.top = '12px';
  rangeDiv.style.zIndex = 9;
  rangeDiv.style.width = '340px';
  document.body.appendChild(rangeDiv);
  if(window.noUiSlider){
    noUiSlider.create(rangeDiv, {
      start:[minT,maxT], connect:true, range:{min:minT,max:maxT}, step:24*3600*1000, tooltips:true,
      format:{ to:v => new Date(v).toISOString().slice(0,10), from:v => Date.parse(v) }
    });
    rangeDiv.noUiSlider.on('update', vals => {
      const lo = Date.parse(vals[0]), hi = Date.parse(vals[1]);
      edges.forEach(e => {
        const t = Date.parse(e.t || '1970-01-01');
        edges.update({ id:e.id, hidden: Number.isFinite(t) ? (t<lo || t>hi) : false });
      });
    });
  }

  // ========== 커뮤니티별 클러스터 ==========
  function getCid(n){ return (n.community_id ?? n.group_cid ?? null); }
  function clusterByCommunity(){
    const seen = new Set();
    nodes.forEach(n => {
      const cid = getCid(n);
      if(cid === null || seen.has(cid)) return;
      seen.add(cid);
      network.cluster({
        joinCondition: nodeOptions => (nodeOptions.community_id ?? null) === cid,
        clusterNodeProperties: {
          id: `cluster:cid:${cid}`,
          label: `Community ${cid}`,
          borderWidth: 3,
          color: { background: PALETTE[cid % PALETTE.length], border: "#0f172a" }
        }
      });
    });
  }
  document.getElementById('btn-cluster-cid').onclick = clusterByCommunity;

  // ========== 메타 뷰 전환 ==========
  async function switchToMetaGraph(){
    try {
      const meta = await fetch('unified_network_meta_v12_hvdc.json').then(r=>r.json());
      const nset = new vis.DataSet(meta.nodes);
      const eset = new vis.DataSet(meta.edges);
      network.setData({nodes:nset, edges:eset});
      document.getElementById('btn-meta').textContent = "Meta View ✓";
    } catch(e) {
      alert("Meta-graph file not found. Please regenerate the network.");
    }
  }
  document.getElementById('btn-meta').onclick = () => switchToMetaGraph();
})();
</script>
"""
    html = html.replace("</body>", body_inject + "\n</body>")
    Path(html_path).write_text(html, encoding="utf-8")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1 v1.2 Stage 1 - HVDC v3.0 Ontology")
    print("=" * 60)

    G = nx.Graph(name="UNIFIED_LOGISTICS_NETWORK_v12_HVDC")

    # 1. Build HVDC infrastructure (L0-L2)
    print("\n[1/6] Building HVDC infrastructure...")
    G = build_hvdc_infrastructure(G)

    # 2. Add HVDC cargo flow
    print("[2/6] Adding HVDC cargo flow...")
    G = add_hvdc_cargo_flow(G)

    # 3. Integrate existing data (L3)
    print("[3/6] Integrating existing JPT71/ABU data...")
    G = integrate_existing_data_with_hvdc(G)

    # 4. Build identity graph
    print("[4/6] Building identity graph (same_as links)...")
    G = build_identity_graph_hvdc(G)

    # 5. Apply inference rules
    print("[5/6] Applying ontological inference rules...")
    G = add_inference_rules(G)

    # 6. Validate
    print("[6/8] Validating HVDC v3.0 ontology...")
    validation = validate_hvdc_ontology(G)

    # 7. Community detection for meta-graph
    print("[7/8] Generating meta-graph...")
    if validation.get("total_nodes", 0) > 0:
        # Apply Louvain community detection
        try:
            node2comm = {}
            communities = louvain_communities(G, seed=42)
            for cid, comm in enumerate(communities):
                for node in comm:
                    node2comm[node] = cid

            # Stamp community_id to nodes
            for node, cid in node2comm.items():
                if G.has_node(node):
                    G.nodes[node]["community_id"] = cid

            # Generate meta-graph
            H = aggregate_by_community(G, node2comm)

            # Export meta-graph JSON
            meta_json = "unified_network_meta_v12_hvdc.json"
            export_json(H, meta_json)
            print(f"[OK] Meta-graph exported: {meta_json}")
        except Exception as e:
            print(f"[WARN] Meta-graph generation failed: {e}")

    # 8. Export
    print("[8/8] Exporting outputs...")
    export_json(G, DATA_JSON)
    export_stats(G, validation, STATS_JSON)
    export_pyvis_html(G, OUT_HTML)

    print("\n" + "=" * 60)
    print("[SUCCESS] HVDC v3.0 Ontology-based network generated!")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - {DATA_JSON}")
    print(f"  - {STATS_JSON}")
    print(f"  - {OUT_HTML}")
    print("\nOpen the HTML file in a browser to view the interactive network.")
