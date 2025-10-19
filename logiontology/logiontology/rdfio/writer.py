from __future__ import annotations
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD
from typing import Iterable, Any

EX = Namespace("http://example.org/lo/")

def write_ttl(records: Iterable[dict[str, Any]], path: str) -> None:
    g = Graph()
    g.bind("ex", EX)
    for r in records:
        subj = URIRef(EX[str(r.get("event_id") or r.get("snapshot_id") or r.get("deadstock_id"))])
        g.add((subj, RDF.type, EX.Record))
        for k, v in r.items():
            g.add((subj, EX[k], Literal(str(v))))
    g.serialize(destination=path, format="turtle")
