"""Tests for KPI endpoint."""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_get_kpis():
    """Test KPI dashboard endpoint."""
    response = client.get("/api/kpi/")
    assert response.status_code == 200
    data = response.json()
    assert "total_flows" in data
    assert "direct_delivery_rate" in data
    assert "mosb_pass_rate" in data
    assert "flow_distribution" in data


def test_get_flow_distribution():
    """Test flow distribution endpoint."""
    response = client.get("/api/kpi/flow-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "distribution" in data
    assert len(data["distribution"]) == 5  # 5 flow codes (0-4)


