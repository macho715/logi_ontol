# logiontology/pipeline/run_map_cluster.py
# End-to-end: CSV -> RDF (entities) + RDF (linkset) via identity_rules clusterer.
from __future__ import annotations
import argparse
import yaml
from pathlib import Path
import pandas as pd
from rdflib import Graph
from ..mapping.registry import MappingRegistry
from ..mapping.clusterer import IdentityClusterer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True)
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_entities", required=True)  # TTL
    ap.add_argument("--out_linkset", required=True)  # TTL
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--fuseki", help="http://localhost:3030")
    ap.add_argument("--dataset", help="dataset name")
    args = ap.parse_args()

    # Load data
    df = pd.read_csv(args.in_csv)

    # Stage 1-5: entities
    reg = MappingRegistry.load_rules(args.rules)
    ent_ttl = reg.run(df, args.out_entities)

    # Stage 3 extended: clusterer + linkset
    clu = IdentityClusterer.from_yaml(args.rules)
    clusters, linkset_graph = clu.run(df)
    linkset_path = Path(args.out_linkset)
    linkset_graph.serialize(linkset_path, format="turtle")

    print(f"[OK] Entities TTL → {ent_ttl}")
    print(f"[OK] Linkset TTL  → {linkset_path} (clusters: {len(clusters)})")

    # Optional publish
    if args.publish:
        from ..rdfio.publish import publish_turtle

        if not args.fuseki or not args.dataset:
            raise SystemExit("--publish requires --fuseki and --dataset")
        c1 = publish_turtle(ent_ttl, args.fuseki, args.dataset)
        c2 = publish_turtle(linkset_path, args.fuseki, args.dataset)
        print(f"Publish status: entities={c1}, linkset={c2}")


if __name__ == "__main__":
    main()
