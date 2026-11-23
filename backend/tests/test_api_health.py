"""HeartXAI 2.0 - API Boot & Health Endpoint Integration Tests."""

from app.api.v1.routes.health import liveness_probe, readiness_probe
from app.main import app, root


def test_root_endpoint():
    """Verify root endpoint returns project metadata."""
    data = root()
    assert data["service"] == "HeartXAI 2.0"
    assert data["version"] == "2.0.0"
    assert data["documentation"] == "/docs"
    assert data["health"] == "/health/live"


def test_health_live_endpoint():
    """Verify liveness probe returns healthy status."""
    data = liveness_probe()
    assert data["status"] == "healthy"
    assert data["service"] == "HeartXAI 2.0"
    assert "timestamp" in data


def test_health_ready_endpoint(db_session):
    """Verify readiness probe verifies operational database connectivity."""
    data = readiness_probe(db=db_session)
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert "timestamp" in data


def test_openapi_schema_generated():
    """Verify that OpenAPI documentation schema is properly compiled."""
    schema = app.openapi()
    assert schema["info"]["title"] == "HeartXAI 2.0"
    assert schema["info"]["version"] == "2.0.0"
    assert "/health/live" in schema["paths"]
    assert "/health/ready" in schema["paths"]
