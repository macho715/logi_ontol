# logiontology/mapping/clusterer.py
# Identity Clusterer v2.6 — executes identity_rules from YAML to produce clusters + linksets.
from __future__ import annotations
import re
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, RDF
from datetime import timedelta

HVDC = Namespace("https://hvdc.example.org/ns#")
OPS = Namespace("https://hvdc.example.org/ops#")
HVDCI = Namespace("https://hvdc.example.org/id/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")


def uuid5_from(*parts: str) -> str:
    base = "00000000-0000-0000-0000-000000000000"
    name = "::".join("" if p is None else str(p) for p in parts)
    return str(uuid.uuid5(uuid.UUID(base), name))


@dataclass
class ClusterRule:
    name: str
    when: List[str]
    cluster_as: str
    window_days: Optional[int] = None
    same_port: Optional[bool] = None


class IdentityClusterer:
    def __init__(self, rules: Dict[str, Any]):
        self.raw_rules = rules.get("identity_rules", [])
        self.rules = [ClusterRule(**r) for r in self.raw_rules]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "IdentityClusterer":
        import yaml

        with open(path, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f)
        return cls(rules)

    def _cluster_by_simple_keys(
        self, df: pd.DataFrame, keys: List[str], as_type: str
    ) -> pd.DataFrame:
        present = [k for k in keys if k in df.columns]
        if not present:
            return pd.DataFrame(columns=["ClusterID", "ClusterType", "RowIndex"])
        # Build cluster id as uuid5 of concatenated key values
        ids = []
        for i, row in df[present].iterrows():
            parts = [str(row.get(k, "") or "") for k in present]
            cid = uuid5_from(*parts)
            ids.append((i, cid))
        out = pd.DataFrame(ids, columns=["RowIndex", "ClusterID"])
        out["ClusterType"] = as_type
        return out

    def _cluster_by_rotation_eta(self, df: pd.DataFrame, rule: ClusterRule) -> pd.DataFrame:
        # Requires 'RotationNo' and 'ETA' columns
        if "RotationNo" not in df.columns or "ETA" not in df.columns:
            return pd.DataFrame(columns=["ClusterID", "ClusterType", "RowIndex"])
        tmp = df[["RotationNo", "ETA"]].copy()
        tmp["ETA"] = pd.to_datetime(tmp["ETA"], errors="coerce")
        # Bucket by rotation + week window (±window_days collapsed to week index)
        w = max(rule.window_days or 7, 1)
        # Use ISO week start as bucket; different windows approximate by floor to w-day bins
        tmp["bucket"] = (
            tmp["ETA"].dt.floor("D") - pd.to_timedelta(tmp["ETA"].dt.dayofyear % w, unit="D")
        ).astype("datetime64[ns]")
        ids = []
        for i, r in tmp.iterrows():
            parts = [str(r.get("RotationNo") or ""), str(r.get("bucket") or "")]
            cid = uuid5_from(*parts)
            ids.append((i, cid))
        out = pd.DataFrame(ids, columns=["RowIndex", "ClusterID"])
        out["ClusterType"] = rule.cluster_as
        return out

    def compute_clusters(self, df: pd.DataFrame) -> pd.DataFrame:
        clusters = []
        for r in self.rules:
            if r.name == "by_rotation_eta":
                c = self._cluster_by_rotation_eta(df, r)
            else:
                c = self._cluster_by_simple_keys(df, r.when, r.cluster_as)
            if not c.empty:
                c["RuleName"] = r.name
                clusters.append(c)
        if not clusters:
            return pd.DataFrame(columns=["ClusterID", "ClusterType", "RowIndex", "RuleName"])
        # Prefer first rule hit per row
        allc = pd.concat(clusters, ignore_index=True)
        allc = allc.sort_values(["RowIndex"]).drop_duplicates(subset=["RowIndex"], keep="first")
        return allc

    def build_linkset_graph(self, df: pd.DataFrame, clusters: pd.DataFrame) -> Graph:
        """
        Create RDF assertions linking row-derived entities into clusters:
          - hvdc:inCluster link from Shipment/Consignment/etc to Cluster node
          - owl:sameAs links between items in same cluster (lightweight)
        """
        g = Graph()
        g.bind("hvdc", HVDC)
        g.bind("ops", OPS)
        g.bind("hvdci", HVDCI)
        g.bind("owl", OWL)

        # Build minimal subject IRI per row: prefer Shipment if we have HVDC+Case
        def subject_iri(row) -> Optional[URIRef]:
            hv = row.get("HVDC_Code")
            cn = row.get("Case No.")
            bl = row.get("BL No.")
            co = row.get("Container")
            if pd.notna(hv) and pd.notna(cn):
                return URIRef(f"{HVDCI}Shipment/{uuid5_from(hv, cn)}")
            if pd.notna(bl) and pd.notna(co):
                return URIRef(f"{HVDCI}Consignment/{uuid5_from(bl, co)}")
            if pd.notna(bl):
                return URIRef(f"{HVDCI}BL/{uuid5_from(bl)}")
            return None

        # Precompute subjects
        subj_map: Dict[int, Optional[URIRef]] = {i: subject_iri(df.loc[i]) for i in df.index}

        # For each cluster, create a Cluster node and link members
        for cid, gdf in clusters.groupby("ClusterID"):
            cnode = URIRef(f"{HVDCI}Cluster/{cid}")
            g.add((cnode, RDF.type, HVDC.Cluster))
            # member links
            members = []
            for i in gdf["RowIndex"].tolist():
                s = subj_map.get(i)
                if s is None:
                    continue
                members.append(s)
                g.add((s, HVDC.inCluster, cnode))
            # pairwise owl:sameAs (sparse: link to first only)
            if len(members) > 1:
                head = members[0]
                for m in members[1:]:
                    g.add((m, OWL.sameAs, head))
        return g

    def run(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Graph]:
        clusters = self.compute_clusters(df)
        linkset_graph = self.build_linkset_graph(df, clusters)
        return clusters, linkset_graph
