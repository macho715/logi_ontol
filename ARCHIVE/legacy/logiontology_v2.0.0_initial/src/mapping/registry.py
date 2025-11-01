#!/usr/bin/env python3
"""
HVDC Ontology Mapper v2.6 - DataFrame → RDF 변환

mapping_rules.v2.6.yaml 기반으로 DataFrame을 RDF로 변환하는 최신 실전 예제
P.MD v2.6 시스템 통합
"""

from __future__ import annotations
import re
import uuid
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD
import pytz
import yaml
import logging

logger = logging.getLogger(__name__)

# HVDC Namespaces
HVDC = Namespace("https://hvdc.example.org/ns#")
OPS = Namespace("https://hvdc.example.org/ops#")
ORG = Namespace("https://schema.org/")
HVDCI = Namespace("https://hvdc.example.org/id/")

DXB_TZ = pytz.timezone("Asia/Dubai")


def uuid5_from(*parts: str) -> str:
    """Generate deterministic UUID5 from parts"""
    base = "00000000-0000-0000-0000-000000000000"
    name = "::".join("" if p is None else str(p) for p in parts)
    return str(uuid.uuid5(uuid.UUID(base), name))


def load_dsv_codes() -> set:
    """Load DSV warehouse codes - TODO: Replace with actual source"""
    return {"MZP", "MOSB", "DAS", "AGI", "AAA", "INDOOR", "OUTDOOR"}


def normalize_container(c: str) -> str:
    """Normalize container number"""
    if pd.isna(c):
        return c
    c = str(c).strip().upper()
    return re.sub(r"[^A-Z0-9]", "", c)


def normalize_bl(bl: str) -> str:
    """Normalize BL number"""
    if pd.isna(bl):
        return bl
    return re.sub(r"[-\s]", "", str(bl).strip().upper())


def to_iso8601_dxb(v):
    """Convert to ISO8601 with Dubai timezone"""
    if pd.isna(v):
        return None
    ts = pd.to_datetime(v, errors="coerce")
    if ts.tzinfo is None:
        ts = DXB_TZ.localize(ts.to_pydatetime())
    else:
        ts = ts.tz_convert(DXB_TZ)
    return ts.isoformat()


class MappingRegistry:
    def __init__(self, rules: Dict[str, Any] = None) -> None:
        self.rules = rules or {}
        self.ns_map = {}
        self.header_map = {}
        self.business_rules = {}
        self.identity_rules = {}
        self.property_mappings = {}
        self.class_mappings = {}

    @classmethod
    def load_rules(cls, path: str | Path) -> "MappingRegistry":
        """Load rules from YAML file"""
        import yaml

        with open(path, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f)
        instance = cls(rules)
        instance._parse_rules()
        return instance

    def _parse_rules(self) -> None:
        """Parse loaded rules into internal structures"""
        self.ns_map = {k.rstrip(":"): v for k, v in self.rules.get("namespaces", {}).items()}
        self.header_map = self.rules.get("header_map_kr2en", {})
        self.business_rules = self.rules.get("business_rules", {})
        self.identity_rules = self.rules.get("identity_rules", {})
        self.property_mappings = self.rules.get("property_mappings", {})
        self.class_mappings = self.rules.get("class_mappings", {})

    # ---------- Processing Stages ----------
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column headers using Korean to English mapping"""
        df = df.rename(columns=self.header_map)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    def normalize_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize data values"""
        if "BL No." in df.columns:
            df["BL No."] = df["BL No."].map(normalize_bl)
        if "Container" in df.columns:
            df["Container"] = df["Container"].map(normalize_container)
        if "ETA" in df.columns:
            df["ETA_iso"] = df["ETA"].map(to_iso8601_dxb)
        if "Operation Month" in df.columns:
            df["Operation Month"] = pd.to_datetime(
                df["Operation Month"], errors="coerce"
            ).dt.strftime("%Y-%m")
        return df

    def apply_business_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply business rule filters"""
        wl = set(self.business_rules.get("vendor_whitelist", []))
        if "Vendor" in df.columns and wl:
            df = df[df["Vendor"].isin(wl)]

        if "ETA" in df.columns and "Operation Month" in df.columns:
            eta_month = pd.to_datetime(df["ETA"], errors="coerce").dt.strftime("%Y-%m")
            df = df[eta_month == df["Operation Month"]]

        pressure_col = None
        for col in df.columns:
            if "Pressure" in col and "t/m" in col:
                pressure_col = col
                break

        if pressure_col:
            pressure_max = float(self.business_rules.get("pressure_max", 4.0))
            df = df[pd.to_numeric(df[pressure_col], errors="coerce") <= pressure_max]

        if "Warehouse Code" in df.columns:
            dsv = load_dsv_codes()
            df = df[df["Warehouse Code"].isin(dsv)]

        return df

    # ---------- RDF Generation ----------
    def _graph(self) -> Graph:
        """Create RDF graph with namespaces"""
        g = Graph()
        for pfx, iri in self.ns_map.items():
            g.bind(pfx, Namespace(iri))
        return g

    def dataframe_to_rdf(self, df: pd.DataFrame, out_ttl: str | Path) -> Path:
        """Convert DataFrame to RDF using v2.6 mapping rules"""
        g = self._graph()

        for idx, row in df.iterrows():
            rowd = row.to_dict()

            hvdc_code = rowd.get("HVDC_Code")
            case_no = rowd.get("Case No.")
            vendor = rowd.get("Vendor")
            blno = rowd.get("BL No.")
            eta_iso = rowd.get("ETA_iso")
            pressure = None
            for key in rowd.keys():
                if "Pressure" in key and "t/m" in key:
                    pressure = rowd.get(key)
                    break

            # Shipment
            s_iri = URIRef(f"{HVDCI}Shipment/{uuid5_from(hvdc_code, case_no)}")
            g.add((s_iri, RDF.type, URIRef(f"{HVDC}Shipment")))
            if hvdc_code:
                g.add((s_iri, URIRef(f"{HVDC}hasHVDCCode"), Literal(hvdc_code)))

            # Item
            if case_no:
                item_iri = URIRef(f"{HVDCI}Item/{uuid5_from(case_no)}")
                g.add((item_iri, RDF.type, URIRef(f"{HVDC}LogisticsItem")))
                g.add((item_iri, URIRef(f"{HVDC}hasCaseNo"), Literal(case_no)))
                g.add((s_iri, URIRef(f"{HVDC}containsItem"), item_iri))

            # Organization
            if vendor:
                org_id = re.sub(r"\s+", "_", str(vendor).strip())
                org_iri = URIRef(f"{HVDCI}Org/{org_id}")
                g.add((org_iri, RDF.type, URIRef(f"{ORG}Organization")))
                g.add((org_iri, URIRef(f"{ORG}name"), Literal(vendor)))
                g.add((s_iri, URIRef(f"{HVDC}hasVendor"), org_iri))

            # ArrivalEvent
            if blno and eta_iso:
                e_iri = URIRef(f"{HVDCI}Event/ARR/{uuid5_from(blno, eta_iso)}")
                g.add((e_iri, RDF.type, URIRef(f"{OPS}ArrivalEvent")))
                g.add(
                    (
                        e_iri,
                        URIRef(f"{HVDC}eventTimestamp"),
                        Literal(eta_iso, datatype=XSD.dateTime),
                    )
                )
                g.add((e_iri, URIRef(f"{HVDC}aboutShipment"), s_iri))

            # TransportConstraint
            if pressure is not None and str(pressure).strip() != "":
                try:
                    pv = round(float(pressure), 2)
                    c_iri = URIRef(f"{HVDCI}Constraint/{uuid5_from(hvdc_code, case_no, str(pv))}")
                    g.add((c_iri, RDF.type, URIRef(f"{HVDC}TransportConstraint")))
                    g.add((c_iri, URIRef(f"{HVDC}deckPressure"), Literal(pv)))
                except Exception:
                    pass

        out = Path(out_ttl)
        out.parent.mkdir(parents=True, exist_ok=True)
        g.serialize(out, format="turtle")
        return out

    # Orchestrator
    def run(self, df: pd.DataFrame, out_ttl: str | Path) -> Path:
        """Run complete pipeline: normalize → filter → RDF"""
        self._parse_rules()
        df1 = self.normalize_columns(df.copy())
        df2 = self.normalize_values(df1)
        df3 = self.apply_business_filters(df2)
        return self.dataframe_to_rdf(df3, out_ttl)

    # Legacy compatibility methods
    def load(self, path: str | Path) -> None:
        """Load rules from file (legacy compatibility)"""
        self.rules = MappingRegistry.load_rules(path).rules
        self._parse_rules()

    def apply_hvdc_filters_to_rdf(self, df: pd.DataFrame) -> pd.DataFrame:
        """Legacy method - now uses apply_business_filters"""
        return self.apply_business_filters(df)

    def validate_rdf_conversion(self, df: pd.DataFrame) -> dict:
        """Validate RDF conversion"""
        return {
            "total_records": len(df),
            "mappable_fields": len([c for c in df.columns if c in self.header_map]),
            "unmappable_fields": [c for c in df.columns if c not in self.header_map],
            "missing_mappings": [],
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HVDC Ontology Mapper v2.6")
    parser.add_argument("--rules", required=True, help="Path to mapping rules YAML file")
    parser.add_argument("--in_csv", required=True, help="Input CSV file")
    parser.add_argument("--out_ttl", required=True, help="Output TTL file")
    args = parser.parse_args()

    reg = MappingRegistry.load_rules(args.rules)
    df = pd.read_csv(args.in_csv)
    out = reg.run(df, args.out_ttl)
    print(f"RDF written → {out}")
