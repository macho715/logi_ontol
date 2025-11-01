"""Tests for main FastAPI application."""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_flows():
    """Test list flows endpoint."""
    response = client.get("/api/flows")
    assert response.status_code == 200
    data = response.json()
    assert "flows" in data
    assert "total" in data


def test_get_flow_by_id():
    """Test get flow by ID endpoint."""
    response = client.get("/api/flows/CT001")
    assert response.status_code == 200
    data = response.json()
    assert data["flow_id"] == "CT001"


def test_search_flows():
    """Test search flows endpoint."""
    response = client.get("/api/search?hvdc_code=HVDC-001")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


