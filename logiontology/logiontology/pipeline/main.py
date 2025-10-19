from __future__ import annotations
from logiontology.ingest.excel import load_excel
from logiontology.validation.schema_validator import (
    validate_transport_events
)
from logiontology.reasoning.engine import reason
from logiontology.rdfio.writer import write_ttl

def run_pipeline_excel_to_ttl(xlsx_path: str, ttl_out: str) -> None:
    df = load_excel(xlsx_path)
    records = df.to_dict(orient="records")
    ok, errs = validate_transport_events(records)
    if not ok:
        raise ValueError(f"Validation failed: {len(errs)} errors")
    enriched = list(reason(records))
    write_ttl(enriched, ttl_out)
