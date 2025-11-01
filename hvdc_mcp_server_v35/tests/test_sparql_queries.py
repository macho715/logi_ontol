import pytest
from rdflib import Graph
from mcp_server.sparql_engine import SPARQLEngine
from mcp_server.config import TTL_PATH

@pytest.fixture
def engine():
    return SPARQLEngine()

def test_flow_distribution(engine):
    dist = engine.get_flow_code_distribution_v35()
    flow_codes = [item['flowCode'] for item in dist]
    assert sorted(flow_codes) == [0, 1, 2, 3, 4, 5]  # Assumes all present
    total_cases = sum(item['count'] for item in dist)
    assert total_cases == 755  # Per plan

def test_agi_das_compliance(engine):
    comp = engine.get_agi_das_compliance()
    assert comp['compliance_rate'] == 100  # Per plan

def test_override_cases(engine):
    overrides = engine.get_override_cases()
    assert len(overrides) == 31  # Per plan

