from __future__ import annotations
# Optional SHACL validation via pyshacl if installed.
from typing import Tuple
try:
    from pyshacl import validate as shacl_validate  # type: ignore
except Exception:  # pragma: no cover - optional
    shacl_validate = None

def run_shacl(data_graph_ttl: str, shapes_ttl: str) -> Tuple[bool, str]:
    if shacl_validate is None:
        return (True, "pyshacl not installed; skipped.")
    conforms, results_graph, results_text = shacl_validate(
        data_graph_ttl, shacl_graph=shapes_ttl, inference="rdfs", abort_on_error=False
    )
    return (bool(conforms), str(results_text))
