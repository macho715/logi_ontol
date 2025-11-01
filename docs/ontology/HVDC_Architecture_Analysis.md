1. 온톨로지 아키텍처 분석
1.1 계층 구조 (4-Level Hierarchy)
python# ==================== L0: Root Node ====================
HVDC_Project (루트)
├─ type: "root"
├─ ontology_class: "Project"
└─ color: #ff0000 (빨강 - 최상위 노드)

# ==================== L1: System Layer ====================
├─ JPT71_System (기존 물류 시스템)
│  ├─ ontology_class: "System"
│  ├─ color: #ff6b6b
│  └─ belongs_to → HVDC_Project
│
├─ ABU_System (Abu Dhabi 시스템)
│  ├─ ontology_class: "System"
│  ├─ color: #51cf66
│  └─ belongs_to → HVDC_Project
│
└─ HVDC_Infrastructure (신규 HVDC 인프라)
   ├─ ontology_class: "System"
   ├─ color: #339af0
   └─ belongs_to → HVDC_Project

# ==================== L2: Location Nodes (8개) ====================
HVDC_Infrastructure
├─ Ports (3개)
│  ├─ ZAYED_PORT
│  │  ├─ type: "port"
│  │  ├─ ontology_class: "Location"
│  │  ├─ customs_code: "ADNOC 47150"
│  │  └─ description: "중량/벌크 화물 처리항"
│  │
│  ├─ KHALIFA_PORT
│  │  ├─ type: "port"
│  │  ├─ description: "컨테이너 전용"
│  │  └─ customs_code: ""
│  │
│  └─ JEBEL_ALI_PORT
│     ├─ type: "port"
│     ├─ description: "Free Zone"
│     └─ customs_code: "ADOPT"
│
├─ Hub (1개)
│  └─ MOSB
│     ├─ type: "hub"
│     ├─ ontology_class: "Location"
│     ├─ operator: "ADNOC L&S"
│     ├─ area_sqm: 20000
│     └─ sct_team: "SCT 물류본부 상주"
│
├─ Onshore Sites (2개)
│  ├─ MIR (Mirfa Site)
│  │  ├─ site_type: "onshore"
│  │  └─ laydown_area_sqm: 35000
│  │
│  └─ SHU (Shuweihat Site)
│     ├─ site_type: "onshore"
│     └─ laydown_area_sqm: 10500
│
└─ Offshore Sites (2개)
   ├─ DAS (Das Island)
   │  ├─ site_type: "offshore"
   │  └─ voyage_from_mosb_hours: 20
   │
   └─ AGI (Al Ghallan Island)
      ├─ site_type: "offshore"
      └─ voyage_from_mosb_hours: 10

# ==================== L3: Entity Nodes ====================
├─ Assets (Vessels, Cargo, Equipment)
│  └─ ontology_class: "Asset"
│
├─ Parties (Persons, Organizations)
│  ├─ SCT_Logistics_Team
│  │  ├─ ontology_class: "Party"
│  │  ├─ organization: "Samsung C&T"
│  │  └─ location: "MOSB"
│  │
│  └─ ADNOC_LS
│     ├─ ontology_class: "Party"
│     └─ organization: "ADNOC"
│
├─ Processes (Operations)
│  └─ ontology_class: "Process"
│
└─ Events (Messages, Timetags)
   └─ ontology_class: "Event"
1.2 온톨로지 클래스 매핑
python# Palantir Foundry Object Types와 매핑
ONTOLOGY_CLASS_MAPPING = {
    "port":      "Location",    # Port → Location (RDF: hvdc:Port rdfs:subClassOf hvdc:Location)
    "hub":       "Location",    # Hub → Location
    "site":      "Location",    # Site → Location
    "vessel":    "Asset",       # Vessel → Asset
    "person":    "Party",       # Person → Party
    "operation": "Process",     # Operation → Process
    "cargo":     "Asset",       # Cargo → Asset
    "equipment": "Asset",       # Equipment → Asset
    "document":  "Document",    # Document → Document
    "permit":    "Document",    # Permit → Document (규제 서류)
    "timetag":   "Event",       # TimeTag → Event
    "message":   "Event",       # Message → Event
}

# RDF/OWL 형식 변환 예시
"""
@prefix hvdc: <http://ontology.hvdc.project/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

hvdc:Port rdf:type owl:Class ;
    rdfs:subClassOf hvdc:Location ;
    rdfs:label "Port Node"@en ;
    rdfs:comment "Maritime port for cargo operations"@en .

hvdc:ZAYED_PORT rdf:type hvdc:Port ;
    hvdc:customsCode "ADNOC 47150" ;
    hvdc:description "중량/벌크 화물 처리항"@ko .
"""

🔗 2. 관계 타입 (12종 Relationships)
2.1 구조적 관계 (Structural)
python# 1. belongs_to (소속 관계)
# 용도: 계층 구조 정의
HVDC_Project → JPT71_System, ABU_System, HVDC_Infrastructure
HVDC_Infrastructure → ZAYED_PORT, KHALIFA_PORT, JEBEL_ALI_PORT, MOSB, MIR, SHU, DAS, AGI

# RDF 표현:
# hvdc:JPT71_System hvdc:belongsTo hvdc:HVDC_Project .
2.2 운영 관계 (Operational)
python# 2. feeds_into (물류 흐름)
ZAYED_PORT → MOSB
KHALIFA_PORT → MOSB
JEBEL_ALI_PORT → MOSB

# 3. dispatches (배송)
MOSB → MIR, SHU, DAS, AGI

# 4. connected_to (연결)
DAS ↔ AGI  # 섬 간 연결

# 5. hosts (호스팅)
MOSB → SCT_Logistics_Team

# 6. governed_by (거버넌스)
MOSB → ADNOC_LS
2.3 엔티티 관계 (Entity)
python# 7. operates (운영)
Person → Vessel

# 8. works_at (근무)
Person → Location

# 9. performed (수행)
Person → Operation

# 10. uses (사용)
Operation → Vessel

# 11. transported_by (운송)
Cargo → Vessel

# 12. stored_at (보관)
Cargo → Location
2.4 시맨틱 관계 (Semantic)
python# 13. same_as (동일 엔티티)
# 용도: 중복 제거, 엔티티 해소
vessel:JPT71_A ←same_as→ vessel:JPT71
person:John_Doe ←same_as→ person:J.Doe

# 구현:
def build_identity_graph_hvdc(G):
    """same_as 링크로 중복 엔티티 해소"""
    vessels = [n for n, d in G.nodes(data=True) if d.get("type") == "vessel"]
    for i, v1 in enumerate(vessels):
        for v2 in vessels[i + 1:]:
            # 정규화 비교
            if normalize_name(v1) == normalize_name(v2):
                G.add_edge(v1, v2, rel="same_as", weight=1.0)
            # 유사도 비교 (85% 이상)
            elif SequenceMatcher(None, v1, v2).ratio() >= 0.85:
                G.add_edge(v1, v2, rel="same_as", weight=0.9)

✅ 3. 온톨로지 검증 (Validation)
3.1 검증 로직
pythondef validate_hvdc_ontology(G: nx.Graph) -> dict:
    """HVDC v3.0 온톨로지 규칙 준수 검증"""

    results = {}

    # 1. 필수 노드 존재 확인 (8개 HVDC 노드)
    required_nodes = [
        "ZAYED_PORT", "KHALIFA_PORT", "JEBEL_ALI_PORT",  # 3 Ports
        "MOSB",                                            # 1 Hub
        "MIR", "SHU",                                      # 2 Onshore Sites
        "DAS", "AGI"                                       # 2 Offshore Sites
    ]

    hvdc_nodes_present = [n for n in required_nodes if n in G.nodes]
    results["hvdc_nodes_count"] = len(hvdc_nodes_present)
    results["hvdc_nodes_list"] = hvdc_nodes_present

    # 검증 규칙: 8/8 노드 필수
    assert len(hvdc_nodes_present) == 8, "Missing HVDC nodes!"

    # 2. MOSB 허브 연결성 검증
    # 규칙: MOSB는 3개 Port로부터 feeds_into 받고, 4개 Site로 dispatches
    mosb_incoming = [u for u, v in G.edges() if v == "MOSB"]
    mosb_outgoing = [v for u, v in G.edges() if u == "MOSB"]

    results["mosb_incoming"] = len(mosb_incoming)
    results["mosb_outgoing"] = len(mosb_outgoing)

    # 검증 규칙: MOSB incoming >= 3, outgoing >= 4
    assert len(mosb_incoming) >= 3, "MOSB must receive from 3+ ports"
    assert len(mosb_outgoing) >= 4, "MOSB must dispatch to 4+ sites"

    # 3. 관계 타입 다양성 (목표: 12종+)
    edge_types = set([d.get("rel") for u, v, d in G.edges(data=True)])
    results["edge_types_count"] = len(edge_types)
    results["edge_types_list"] = sorted(edge_types)

    # 검증 규칙: >= 12 종류
    assert len(edge_types) >= 12, f"Need 12+ edge types, got {len(edge_types)}"

    # 4. 온톨로지 클래스 커버리지
    ontology_classes = set([
        d.get("ontology_class")
        for n, d in G.nodes(data=True)
        if "ontology_class" in d
    ])
    results["ontology_classes"] = sorted(ontology_classes)

    # 검증 규칙: 최소 5개 클래스 (Location, Asset, Party, Process, Event)
    required_classes = {"Location", "Asset", "Party", "Process", "Event"}
    assert required_classes.issubset(ontology_classes), "Missing core ontology classes"

    # 5. same_as 링크 (중복 제거 효과)
    same_as_edges = [
        (u, v) for u, v, d in G.edges(data=True)
        if d.get("rel") == "same_as"
    ]
    results["same_as_links"] = len(same_as_edges)

    # 6. 네트워크 밀도 (평균 연결도)
    avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
    results["avg_degree"] = avg_degree

    # 검증 규칙: avg_degree >= 3.2 (고밀도 네트워크)
    assert avg_degree >= 3.2, f"Network too sparse: avg_degree={avg_degree:.2f}"

    # 7. 전체 통계
    results["total_nodes"] = G.number_of_nodes()
    results["total_edges"] = G.number_of_edges()

    return results
3.2 검증 출력 예시
yaml[HVDC v3.0 ONTOLOGY VALIDATION]
============================================================
[OK] HVDC Nodes: 8/8
     ['ZAYED_PORT', 'KHALIFA_PORT', 'JEBEL_ALI_PORT',
      'MOSB', 'MIR', 'SHU', 'DAS', 'AGI']

[OK] MOSB Hub: 3 incoming, 6 outgoing
     - Incoming: ZAYED_PORT, KHALIFA_PORT, JEBEL_ALI_PORT
     - Outgoing: MIR, SHU, DAS, AGI, SCT_Logistics_Team, ADNOC_LS

[OK] Edge types: 13 (target: >=12)
     ['belongs_to', 'connected_to', 'dispatches', 'feeds_into',
      'governed_by', 'hosts', 'performed', 'same_as', 'suppliedBy',
      'transported_by', 'uses', 'works_at']

[OK] Ontology classes:
     ['Asset', 'Document', 'Event', 'Location', 'Party',
      'Process', 'Project', 'System']

[OK] Same_as links: 47
     - 중복 vessel: 18쌍
     - 중복 person: 12쌍
     - 중복 port: 17쌍

[OK] Avg degree: 3.85 (target: >=3.2)

[OK] Total: 127 nodes, 245 edges
============================================================

💡 4. Palantir Foundry 연동 전략
4.1 NetworkX → Palantir Ontology 변환
pythondef convert_to_palantir_ontology(G: nx.Graph) -> dict:
    """
    NetworkX 그래프를 Palantir Foundry Ontology JSON으로 변환
    """

    ontology = {
        "objectTypes": [],
        "linkTypes": [],
        "actionTypes": []
    }

    # 1. Object Types 생성
    node_types = {}
    for node, data in G.nodes(data=True):
        ontology_class = data.get("ontology_class", "Object")

        if ontology_class not in node_types:
            node_types[ontology_class] = {
                "apiName": ontology_class,
                "displayName": ontology_class,
                "pluralDisplayName": f"{ontology_class}s",
                "properties": []
            }

        # 속성 추출
        for key, value in data.items():
            if key not in ["type", "ontology_class", "label", "color", "level"]:
                property_def = {
                    "apiName": key,
                    "dataType": infer_datatype(value)
                }
                if property_def not in node_types[ontology_class]["properties"]:
                    node_types[ontology_class]["properties"].append(property_def)

    ontology["objectTypes"] = list(node_types.values())

    # 2. Link Types 생성
    link_types = {}
    for u, v, data in G.edges(data=True):
        rel = data.get("rel", "related_to")

        if rel not in link_types:
            source_class = G.nodes[u].get("ontology_class", "Object")
            target_class = G.nodes[v].get("ontology_class", "Object")

            link_types[rel] = {
                "apiName": rel,
                "displayName": rel.replace("_", " ").title(),
                "sourceObjectType": source_class,
                "targetObjectType": target_class,
                "cardinality": "MANY_TO_MANY"
            }

    ontology["linkTypes"] = list(link_types.values())

    return ontology

def infer_datatype(value):
    """값 타입 추론"""
    if isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "DOUBLE"
    elif isinstance(value, str):
        return "STRING"
    else:
        return "STRING"
4.2 Palantir Pipeline Builder 연동
pythondef create_palantir_pipeline(G: nx.Graph):
    """
    Foundry Pipeline Builder 스크립트 생성
    """

    pipeline_code = """
from transforms.api import transform, Input, Output
from pyspark.sql import functions as F

@transform(
    ontology_graph=Input("/path/to/networkx/graph"),
    hvdc_locations=Output("/HVDC/Ontology/Locations"),
    hvdc_assets=Output("/HVDC/Ontology/Assets"),
    hvdc_parties=Output("/HVDC/Ontology/Parties")
)
def build_hvdc_ontology(ontology_graph, hvdc_locations, hvdc_assets, hvdc_parties):
    '''
    NetworkX 그래프를 Palantir Object Types로 변환
    '''

    # Load NetworkX graph
    import networkx as nx
    G = nx.read_gpickle(ontology_graph.path)

    # Extract Location nodes
    locations = []
    for node, data in G.nodes(data=True):
        if data.get("ontology_class") == "Location":
            locations.append({
                "location_id": node,
                "name": data.get("label", node),
                "type": data.get("type"),
                "subtype": data.get("subtype"),
                "capacity": data.get("area_sqm") or data.get("laydown_area_sqm"),
                "operator": data.get("operator"),
                "customs_code": data.get("customs_code")
            })

    # Convert to Spark DataFrame
    locations_df = spark.createDataFrame(locations)
    hvdc_locations.write_dataframe(locations_df)

    # Similar for Assets and Parties...
"""

    return pipeline_code

🚀 5. 개선 제안 (Enhanced Features)
5.1 추론 규칙 엔진 추가
pythondef add_inference_rules(G: nx.Graph) -> nx.Graph:
    """
    온톨로지 추론 규칙 적용
    """

    # Rule 1: Transitive Property (간접 연결 추론)
    # IF Item :storedAt Location AND Location :belongsTo System
    # THEN Item :indirectlyBelongsTo System
    for item in [n for n, d in G.nodes(data=True) if d.get("type") == "item"]:
        location = get_connected_node(G, item, "storedAt")
        if location:
            system = get_connected_node(G, location, "belongs_to")
            if system:
                G.add_edge(item, system,
                          rel="indirectly_belongs_to",
                          weight=0.5,
                          inferred=True)

    # Rule 2: Cargo Flow Path (물류 경로 추론)
    # IF Cargo :transported_by Vessel AND Vessel :operates Port→MOSB
    # THEN Cargo :flows_through MOSB
    for cargo in [n for n, d in G.nodes(data=True) if d.get("type") == "cargo"]:
        vessel = get_connected_node(G, cargo, "transported_by")
        if vessel:
            ports = get_connected_nodes(G, vessel, "operates")
            for port in ports:
                if G.has_edge(port, "MOSB"):
                    G.add_edge(cargo, "MOSB",
                              rel="flows_through",
                              weight=0.7,
                              inferred=True)

    # Rule 3: Critical Path Detection (중요 경로 감지)
    # IF Item :dependsOn Item AND dependency_depth > 3
    # THEN Item.riskLevel = "HIGH"
    for item in [n for n, d in G.nodes(data=True) if d.get("type") == "item"]:
        dependency_chain = get_dependency_chain(G, item)
        if len(dependency_chain) > 3:
            G.nodes[item]["riskLevel"] = "HIGH"
            G.nodes[item]["dependency_depth"] = len(dependency_chain)
            G.nodes[item]["inferred"] = True

    # Rule 4: Co-Location Clustering (동일 위치 그룹)
    # IF Item_A :storedAt Location AND Item_B :storedAt Location
    # THEN Item_A :co_located_with Item_B
    location_groups = defaultdict(list)
    for item in [n for n, d in G.nodes(data=True) if d.get("type") == "item"]:
        location = get_connected_node(G, item, "storedAt")
        if location:
            location_groups[location].append(item)

    for location, items in location_groups.items():
        for i, item_a in enumerate(items):
            for item_b in items[i+1:]:
                G.add_edge(item_a, item_b,
                          rel="co_located_with",
                          weight=0.4,
                          inferred=True,
                          location=location)

    return G
5.2 SPARQL 쿼리 지원
pythondef add_sparql_query_support(G: nx.Graph):
    """
    NetworkX 그래프에 SPARQL 쿼리 기능 추가
    """

    # RDF 변환
    import rdflib
    from rdflib import Graph as RDFGraph, Namespace, Literal, URIRef

    rdf_graph = RDFGraph()
    HVDC = Namespace("http://ontology.hvdc.project/")

    # 노드를 RDF 트리플로 변환
    for node, data in G.nodes(data=True):
        node_uri = HVDC[node.replace(" ", "_")]

        # rdf:type
        ontology_class = data.get("ontology_class", "Object")
        rdf_graph.add((node_uri, RDF.type, HVDC[ontology_class]))

        # 속성
        for key, value in data.items():
            if key not in ["type", "ontology_class"]:
                pred = HVDC[key]
                if isinstance(value, str):
                    rdf_graph.add((node_uri, pred, Literal(value)))
                elif isinstance(value, (int, float)):
                    rdf_graph.add((node_uri, pred, Literal(value)))

    # 엣지를 RDF 트리플로 변환
    for u, v, data in G.edges(data=True):
        u_uri = HVDC[u.replace(" ", "_")]
        v_uri = HVDC[v.replace(" ", "_")]
        rel = data.get("rel", "related_to")

        rdf_graph.add((u_uri, HVDC[rel], v_uri))

    # SPARQL 쿼리 실행 함수
    def query_sparql(sparql_query: str):
        """SPARQL 쿼리 실행"""
        results = rdf_graph.query(sparql_query)
        return list(results)

    return rdf_graph, query_sparql

# 사용 예시
rdf_graph, query = add_sparql_query_support(G)

# 쿼리: MOSB로 dispatches하는 모든 노드
sparql = """
PREFIX hvdc: <http://ontology.hvdc.project/>

SELECT ?location ?label
WHERE {
    ?mosb rdf:type hvdc:Location .
    ?mosb hvdc:label "MOSB" .
    ?mosb hvdc:dispatches ?location .
    ?location hvdc:label ?label .
}
"""

results = query(sparql)
for row in results:
    print(f"Location: {row.location}, Label: {row.label}")
5.3 실시간 데이터 업데이트 파이프라인
pythondef create_streaming_pipeline():
    """
    실시간 온톨로지 업데이트 파이프라인
    """

    streaming_code = """
from kafka import KafkaConsumer
import json
import networkx as nx

# Kafka 컨슈머 설정
consumer = KafkaConsumer(
    'hvdc-events',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# 온톨로지 그래프 로드
G = nx.read_gpickle("unified_network_data_v12_hvdc.gpickle")

def update_ontology(event):
    '''이벤트 기반 온톨로지 업데이트'''

    if event['type'] == 'item_moved':
        # 아이템 위치 변경
        item_id = event['item_id']
        new_location = event['new_location']
        old_location = event['old_location']

        # 기존 링크 제거
        if G.has_edge(item_id, old_location):
            G.remove_edge(item_id, old_location)

        # 새 링크 추가
        G.add_edge(item_id, new_location,
                  rel="storedAt",
                  weight=1.0,
                  timestamp=event['timestamp'])

        # 추론 규칙 재실행
        G = add_inference_rules(G)

        # 검증
        validate_hvdc_ontology(G)

        # 저장
        nx.write_gpickle(G, "unified_network_data_v12_hvdc.gpickle")

    elif event['type'] == 'new_shipment':
        # 새 선적 도착
        shipment_id = event['shipment_id']
        items = event['items']
        port = event['arrival_port']

        for item in items:
            G.add_node(item['id'],
                      type='item',
                      ontology_class='Asset',
                      **item['properties'])

            G.add_edge(item['id'], shipment_id, rel='belongsTo')
            G.add_edge(item['id'], port, rel='arrivedAt')

# 스트림 처리
for message in consumer:
    event = message.value
    update_ontology(event)
    print(f"Updated ontology: {event['type']}")
"""

    return streaming_code

📊 6. 코드 품질 및 개선점
6.1 현재 구현의 강점
yaml✅ Strengths:
  Architecture:
    - 명확한 4-Level Hierarchy
    - RDF/OWL 스타일 시맨틱 모델
    - 계층적 노드 구조 (level 0-3)

  Data Quality:
    - same_as 관계로 중복 제거
    - 정규화 함수 (normalize_name)
    - 유사도 기반 자동 매칭 (85% threshold)

  Validation:
    - 포괄적인 검증 로직
    - 필수 노드/관계 확인
    - 네트워크 밀도 검증

  Extensibility:
    - 온톨로지 클래스 매핑 확장 가능
    - 관계 타입 추가 용이
    - 모듈화된 함수 구조
6.2 개선 필요 영역
yaml⚠️ Areas for Improvement:

1. 속성 스키마 부족:
   Problem: 노드 속성이 동적으로 추가됨 (타입 불명확)
   Solution: Pydantic 모델로 속성 스키마 정의

   # 개선 코드
   from pydantic import BaseModel, Field

   class LocationNode(BaseModel):
       id: str
       label: str
       type: Literal["port", "hub", "site"]
       ontology_class: str = "Location"
       capacity: Optional[int] = None
       operator: Optional[str] = None
       customs_code: Optional[str] = None

2. 추론 규칙 미구현:
   Problem: same_as만 있고 다른 추론 없음
   Solution: add_inference_rules() 함수 추가 (위 5.1 참조)

3. SPARQL 지원 부재:
   Problem: 복잡한 쿼리 불가능
   Solution: RDFLib 통합 (위 5.2 참조)

4. 실시간 업데이트 미지원:
   Problem: 정적 그래프만 생성
   Solution: Kafka/Redis 스트리밍 파이프라인 (위 5.3 참조)

5. Palantir 직접 연동 부재:
   Problem: JSON 내보내기만 있음
   Solution: Foundry SDK 사용한 직접 업로드

6. 성능 최적화 필요:
   Problem: same_as O(n²) 비교
   Solution: Locality-Sensitive Hashing (LSH)

   # 개선 코드
   from datasketch import MinHash, MinHashLSH

   def fast_deduplication(G):
       lsh = MinHashLSH(threshold=0.85, num_perm=128)

       vessels = [n for n, d in G.nodes(data=True) if d.get("type") == "vessel"]

       for vessel in vessels:
           mh = MinHash(num_perm=128)
           for char in G.nodes[vessel]["label"]:
               mh.update(char.encode('utf8'))
           lsh.insert(vessel, mh)

       # 유사 노드 찾기 (O(n) 시간)
       for vessel in vessels:
           mh = MinHash(num_perm=128)
           for char in G.nodes[vessel]["label"]:
               mh.update(char.encode('utf8'))

           similar = lsh.query(mh)
           for sim in similar:
               if sim != vessel:
                   G.add_edge(vessel, sim, rel="same_as", weight=0.9)
