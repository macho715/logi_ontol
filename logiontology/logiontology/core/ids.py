from __future__ import annotations
from uuid import uuid5, NAMESPACE_DNS, UUID
from typing import Any

# Stable project-level namespace derived once from a constant label.
PROJECT_NAMESPACE: UUID = uuid5(NAMESPACE_DNS, "logiontology.namespace")

def deterministic_id(kind: str, *parts: Any, **attrs: Any) -> str:
    """Deterministic UUIDv5 from kind + parts + sorted key=value attrs.

    Example:
        deterministic_id("transport_event", "SHIP123", "ARRIVE", occurred_at="2024-01-01T00:00Z")
    """
    seq = [str(kind), *[str(p) for p in parts]]
    for k in sorted(attrs.keys()):
        seq.append(f"{k}={attrs[k]}")
    key = "|".join(seq)
    return str(uuid5(PROJECT_NAMESPACE, key))
