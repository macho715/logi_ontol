from fastapi.testclient import TestClient
from mcp_server.mcp_ttl_server import app

client = TestClient(app)

def test_flow_distribution():
    response = client.get("/flow/distribution")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert 'flowCode' in data[0]

def test_compliance():
    response = client.get("/flow/compliance")
    assert response.status_code == 200
    data = response.json()
    assert 'compliance_rate' in data
    assert data['compliance_rate'] == 100

def test_overrides():
    response = client.get("/flow/overrides")
    assert response.status_code == 200
    assert len(response.json()) == 31

