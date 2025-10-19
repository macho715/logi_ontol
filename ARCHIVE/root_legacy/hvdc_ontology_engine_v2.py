
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef
import pandas as pd, json, re
from typing import Dict, Any, Optional

EX = Namespace("http://samsung.com/project-logistics#")
HVDC = EX  # same namespace

def load_hs_risk(path:str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version":"0","rules":[], "risk_weights":{"LOW":0.5,"MED":1.0,"HIGH":2.0,"CRIT":3.0}}

def classify_hs_risk(hs_code:str, cfg:Dict[str,Any]) -> str:
    if not hs_code:
        return "LOW"
    s = re.sub(r"\\D","", hs_code)
    chap = s[:2]; head = s[:4]; code6 = s[:6]
    for r in cfg.get("rules", []):
        m = r.get("match",{})
        if m.get("code6") and m["code6"] == code6:
            return r.get("risk","LOW")
        if m.get("heading") and m["heading"] == head:
            return r.get("risk","LOW")
        if m.get("chapter") and m["chapter"] == chap:
            return r.get("risk","LOW")
    return "LOW"

def ensure_prop(g, prop, domain=None, rng=None, is_obj=False):
    ns = EX[prop]
    g.add((ns, RDF.type, OWL.ObjectProperty if is_obj else OWL.DatatypeProperty))
    if domain: g.add((ns, RDFS.domain, EX[domain]))
    if rng:    
        if is_obj and isinstance(rng, str):
            g.add((ns, RDFS.range, EX[rng]))
        else:
            g.add((ns, RDFS.range, rng))
    return ns

class HVDCOntologyEngineV2:
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("ex", EX)
        for c in ["Package","ChargeItem","Invoice","ProgressPayment","Warehouse","Site","HVDCKey","CargoItem","HSCode"]:
            self.graph.add((EX[c], RDF.type, OWL.Class))
        ensure_prop(self.graph, "hasHVDCKey", "Package", "HVDCKey", is_obj=True)
        ensure_prop(self.graph, "hvdcCode", "HVDCKey", XSD.string)
        ensure_prop(self.graph, "grossWeightKg", "Package", XSD.decimal)
        ensure_prop(self.graph, "netWeightKg", "Package", XSD.decimal)
        ensure_prop(self.graph, "volumeM3", "Package", XSD.decimal)
        ensure_prop(self.graph, "pieces", "Package", XSD.integer)
        ensure_prop(self.graph, "isOOG", "CargoItem", XSD.boolean)
        ensure_prop(self.graph, "hasHSCode", "CargoItem", "HSCode", is_obj=True)
        ensure_prop(self.graph, "code", "HSCode", XSD.string)
        ensure_prop(self.graph, "riskLevel", "Package", XSD.string)
        ensure_prop(self.graph, "riskScore", "Package", XSD.decimal)
        ensure_prop(self.graph, "riskDetail", "Package", XSD.string)
        ensure_prop(self.graph, "hasCargo", "Package", "CargoItem", is_obj=True)

    def _hvdc_key_uri(self, code:str) -> URIRef:
        u = EX[f"HVDC_{re.sub(r'[^A-Za-z0-9]+','_', code)}"]
        self.graph.add((u, RDF.type, EX.HVDCKey))
        self.graph.add((u, EX.hvdcCode, Literal(code)))
        return u

    def add_package(self, hvdc_code:str, pkg:Dict[str,Any], cargo:Optional[Dict[str,Any]]=None) -> URIRef:
        """
        Add a Package node and optional CargoItem/HSCode linkage.
        pkg keys: grossWeightKg, netWeightKg, volumeM3, pieces
        cargo keys: isOOG, hsCode
        """
        p_uri = EX[f"PKG_{abs(hash((hvdc_code, str(pkg))))}"]
        self.graph.add((p_uri, RDF.type, EX.Package))
        k_uri = self._hvdc_key_uri(hvdc_code)
        self.graph.add((p_uri, EX.hasHVDCKey, k_uri))
        for k in ["grossWeightKg","netWeightKg","volumeM3","pieces"]:
            if k in pkg and pkg[k] is not None and str(pkg[k]) != "":
                dt = XSD.decimal if k != "pieces" else XSD.integer
                self.graph.add((p_uri, EX[k], Literal(pkg[k], datatype=dt)))
        if cargo:
            c_uri = EX[f"CARGO_{abs(hash((hvdc_code, str(cargo))))}"]
            self.graph.add((c_uri, RDF.type, EX.CargoItem))
            if "isOOG" in cargo:
                self.graph.add((c_uri, EX.isOOG, Literal(bool(cargo["isOOG"]), datatype=XSD.boolean)))
            if "hsCode" in cargo and cargo["hsCode"]:
                hs_clean = re.sub(r"\D","", str(cargo["hsCode"]))
                hs_uri = EX[f"HS_{hs_clean}"]
                self.graph.add((hs_uri, RDF.type, EX.HSCode))
                self.graph.add((hs_uri, EX.code, Literal(str(cargo["hsCode"]))))
                self.graph.add((c_uri, EX.hasHSCode, hs_uri))
            self.graph.add((p_uri, EX.hasCargo, c_uri))
        return p_uri

    def validate_weight_risk(self, p_uri:URIRef, cargo:Optional[Dict[str,Any]]=None, hs_risk_cfg:Optional[Dict[str,Any]]=None):
        """
        Enhanced risk scoring: weight tiers + OOG + HS risk
        - Weight tiers (kg): <10000=LOW, 10-25t=MED, 25-50t=HIGH, >=50t=CRIT
        - OOG True => +1 tier
        - HS risk factor (cfg) multiplies
        """
        g = self.graph
        hs_cfg = hs_risk_cfg or {"risk_weights":{"LOW":0.5,"MED":1.0,"HIGH":2.0,"CRIT":3.0}}
        gw = None
        for _,_,w in g.triples((p_uri, EX.grossWeightKg, None)):
            try: gw = float(w)
            except Exception: pass
        tier = "LOW"
        if gw is not None:
            if gw >= 50000: tier = "CRIT"
            elif gw >= 25000: tier = "HIGH"
            elif gw >= 10000: tier = "MED"
            else: tier = "LOW"
        oog = False
        if cargo and "isOOG" in cargo:
            oog = bool(cargo["isOOG"])
        if oog:
            tier = {"LOW":"MED","MED":"HIGH","HIGH":"CRIT","CRIT":"CRIT"}[tier]
        hs_risk = "LOW"
        if cargo and cargo.get("hsCode"):
            hs_risk = classify_hs_risk(str(cargo["hsCode"]), hs_cfg)
        weight_score = {"LOW":1.0,"MED":2.0,"HIGH":3.0,"CRIT":4.0}[tier]
        hs_mult = hs_cfg.get("risk_weights",{}).get(hs_risk,1.0)
        score = round(weight_score * hs_mult, 2)
        detail = f"tier={tier}, oog={oog}, hs_risk={hs_risk}, gw={gw}kg"
        g.set((p_uri, EX.riskLevel, Literal(tier)))
        g.set((p_uri, EX.riskScore, Literal(score, datatype=XSD.decimal)))
        g.set((p_uri, EX.riskDetail, Literal(detail)))
        return {"tier":tier, "score":score, "detail":detail}

    def serialize(self, path:str):
        self.graph.serialize(destination=path, format="turtle")
        return path

    # Backward compatibility
    def validate_weight_consistency(self, p_uri, cargo=None, hs_risk_cfg=None):
        return self.validate_weight_risk(p_uri, cargo, hs_risk_cfg)
