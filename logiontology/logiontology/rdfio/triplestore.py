from __future__ import annotations
# Placeholder client abstraction. Implement specific store client as needed.
from typing import Iterable

class TripleStoreClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def load_ttl(self, path: str) -> None:
        # TODO: implement upload to the triple store
        pass

    def query(self, sparql: str) -> list[dict]:
        # TODO: run SPARQL against the store
        return []
