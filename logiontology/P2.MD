다운로드 (3파일 추가)

logiontology/mapping/clusterer.py
Download

logiontology/rdfio/publish.py
Download

logiontology/pipeline/run_map_cluster.py
Download

참고: 앞서 만든 4파일(룰 YAML 1 + SHACL 2 + registry.py 1)과 함께 총 7파일 세트로 동작.

어떻게 돌아가나 — 한 장 요약

Registry(정규화→비즈 룰 필터→엔티티 RDF)

MappingRegistry.run(df, out_ttl)

Shipment/Item/ArrivalEvent/Constraint 트리플 생성

Clusterer(Identity Rules → 클러스터/Linkset RDF)

IdentityClusterer.from_yaml(rules).run(df)

identity_rules를 실행해서 ClusterID 부여

hvdci:Cluster/<uuid> 노드 생성, 멤버에 hvdc:inCluster 링크

같은 클러스터 내 대표 노드에 owl:sameAs(희소) 연결 → 소프트 머지

Fuseki Publish

publish_turtle(ttl, http://host:3030, dataset)

디폴트 그래프 업로드(원하면 graph IRI 지정 가능)

실전 명령어 (CSV→TTL 2종→Fuseki 게시)
# 1) 엔티티 + 링크셋 생성
python logiontology/logiontology/pipeline/run_map_cluster.py \
  --rules configs/mapping_rules.v2.6.yaml \
  --in_csv data/sample.csv \
  --out_entities out/entities.ttl \
  --out_linkset out/linkset.ttl

# 2) Fuseki에 게시(옵션)
python logiontology/logiontology/pipeline/run_map_cluster.py \
  --rules configs/mapping_rules.v2.6.yaml \
  --in_csv data/sample.csv \
  --out_entities out/entities.ttl \
  --out_linkset out/linkset.ttl \
  --publish \
  --fuseki http://localhost:3030 \
  --dataset hvdc_logistics

규칙별 동작 메모

by_rotation_eta: RotationNo + ETA를 주차(bucket)로 묶어 클러스터. window_days(기본 7)로 버킷 넓이를 조정.

by_hvdc_vendor_case: HVDC_Code + Vendor + Case No. 셋이 동일하면 Shipment 군집.

by_bl_container: BL No. + Container가 같으면 Consignment 군집.

각 군집은 hvdci:Cluster/<uuid>로 IRI 부여 → 멤버 엔티티(Shipment/Consignment/BL 등)에 hvdc:inCluster 링크, 추가로 대표 노드에 owl:sameAs 희소 링크로 정규화.

통합 포인트 (네 코드에 그대로 꽂기)

엔티티 생성 후 clusterer.run(df) 호출 → linkset_graph.serialize()로 out/linkset.ttl 저장

퍼블리시는 현행 CI 배포 스텝에서 python -m logiontology.rdfio.publish 혹은 runner의 --publish 옵션 사용

커스터마이즈 팁

by_rotation_eta의 시간 윈도우가 더 정밀해야 하면:

버킷 대신, ETA를 기준으로 ±window_days 내 행을 그래프 연결(Union-Find)하는 방식으로 교체 가능 (성능: O(n log n)).

subject_iri() 로직에 DeliveryOrder, PortCall 등 추가하면 군집 링크의 주체가 더 풍부해짐.

Fuseki에 네임드 그래프로 구분하려면:

publish_turtle(ttl, base, dataset, graph="https://hvdc.example.org/graph/entities")

빠른 체크리스트

 DSV_CODES 로더를 실제 기준 테이블로 교체

 CSV 샘플 20행으로 엔티티 TTL과 링크셋 TTL 라인수/클래스 카운트 확인

 SHACL 게이트 실패 케이스가 차단 로그로 잘 남는지

 Fuseki 권한/시간초과(Timeout) 설정(대용량 시 Chunk 업로드 고려)

필요하면, by_rotation_eta를 **Union-Find 군집화(±일자 정확 윈도우)**로 강화한 버전도 바로 올려줄 수
