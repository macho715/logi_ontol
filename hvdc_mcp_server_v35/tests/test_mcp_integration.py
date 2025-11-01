import subprocess
import pytest
import httpx
from mcp_server.sparql_engine import SPARQLEngine

@pytest.fixture(scope="session")
def ttl_path():
    # Assume TTL is generated; in real, call excel_to_ttl script
    return "output/hvdc_status_v35.ttl"

def test_full_pipeline(ttl_path):
    # 1. Assume TTL generated
    engine = SPARQLEngine()
    # 2. Query distribution
    dist = engine.get_flow_code_distribution_v35()
    assert sum(d['count'] for d in dist) == 755
    # 3. Compliance
    comp = engine.get_agi_das_compliance()
    assert comp['compliance_rate'] == 100
    # 4. Overrides
    overrides = engine.get_override_cases()
    assert len(overrides) == 31

