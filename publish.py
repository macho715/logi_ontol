# logiontology/rdfio/publish.py
# Simple Fuseki publisher for Turtle files.
from __future__ import annotations
import requests
from pathlib import Path
import sys

def publish_turtle(ttl_path: str | Path, fuseki_base_url: str, dataset: str, graph: str | None = None) -> int:
    """
    Publish a TTL file to Apache Jena Fuseki.
    - fuseki_base_url: e.g., http://localhost:3030
    - dataset: e.g., hvdc_logistics
    - graph: named graph IRI; if None, publish to default graph
    """
    ttl_path = Path(ttl_path)
    url = f"{fuseki_base_url.rstrip('/')}/{dataset}/data"
    params = {"default": ""} if graph is None else {"graph": graph}
    headers = {"Content-Type": "text/turtle"}
    with open(ttl_path, "rb") as f:
        r = requests.post(url, params=params, data=f.read(), headers=headers, timeout=60)
    return r.status_code

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python -m logiontology.rdfio.publish <ttl_path> <fuseki_base_url> <dataset> [graphIRI]")
        sys.exit(2)
    ttl_path, base, dataset = sys.argv[1], sys.argv[2], sys.argv[3]
    graph = sys.argv[4] if len(sys.argv) > 4 else None
    code = publish_turtle(ttl_path, base, dataset, graph)
    print(f"HTTP {code}")
    sys.exit(0 if 200 <= code < 300 else 1)
