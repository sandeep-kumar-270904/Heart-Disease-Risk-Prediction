"""HeartXAI 2.0 - API Boot, Correlation ID, RFC 7807 Error & Health Tests."""

from fastapi.testclient import TestClient

from app.api.v1.routes.health import liveness_probe, readiness_probe
from app.core.database import get_db
from app.core.errors import AuthenticationError, AuthorizationError
from app.core.logging import scrub_sensitive_text
from app.main import app, root


def test_root_endpoint() -> None:
    """Verify root endpoint returns project metadata."""
    data = root()
    assert data["service"] == "HeartXAI 2.0"
    assert data["version"] == "2.0.0"
    assert data["documentation"] == "/docs"
    assert data["health"] == "/health/live"


def test_health_live_endpoint() -> None:
    """Verify liveness probe returns healthy status."""
    data = liveness_probe()
    assert data["status"] == "healthy"
    assert data["service"] == "HeartXAI 2.0"
    assert "timestamp" in data


def test_health_ready_endpoint(db_session) -> None:
    """Verify readiness probe verifies operational database connectivity."""
    data = readiness_probe(db=db_session)
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert "model_version" in data
    assert "timestamp" in data


def test_openapi_schema_generated() -> None:
    """Verify that OpenAPI documentation schema is properly compiled."""
    schema = app.openapi()
    assert schema["info"]["title"] == "HeartXAI 2.0"
    assert schema["info"]["version"] == "2.0.0"
    assert "/health/live" in schema["paths"]
    assert "/health/ready" in schema["paths"]


def test_correlation_id_propagation_and_generation(db_session) -> None:
    """Verify X-Request-ID middleware propagates client IDs and generates defaults."""
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        client = TestClient(app)
        resp_auto = client.get("/health/live")
        assert resp_auto.status_code == 200
        assert resp_auto.headers["X-Request-ID"].startswith("req_")

        resp_custom = client.get("/health/ready", headers={"X-Request-ID": "req-custom-trace-001"})
        assert resp_custom.status_code == 200
        assert resp_custom.headers["X-Request-ID"] == "req-custom-trace-001"
    finally:
        app.dependency_overrides.clear()


def test_rfc7807_error_envelopes_and_no_stack_trace_leak() -> None:
    """Verify 404, 401, 403, 422, and 500 errors return RFC 7807 with zero stack trace leaks."""

    @app.get("/_test/raise-401")
    def _raise_401() -> None:
        raise AuthenticationError("Expired session token.")

    @app.get("/_test/raise-403")
    def _raise_403() -> None:
        raise AuthorizationError("Patient consent revoked.")

    @app.get("/_test/raise-422")
    def _raise_422(age: int) -> dict[str, int]:
        return {"age": age}

    @app.get("/_test/raise-500")
    def _raise_500() -> None:
        raise RuntimeError("SECRET_DB_INTERNAL_FAILURE_DETAILS")

    client = TestClient(app, raise_server_exceptions=False)

    # 404 Not Found
    res_404 = client.get("/nonexistent-endpoint-xyz", headers={"X-Request-ID": "trace-404"})
    assert res_404.status_code == 404
    body_404 = res_404.json()
    assert {"type", "title", "status", "detail", "instance", "request_id"}.issubset(body_404.keys())
    assert body_404["status"] == 404
    assert body_404["request_id"] == "trace-404"

    # 401 Unauthorized
    res_401 = client.get("/_test/raise-401")
    assert res_401.status_code == 401
    assert res_401.json()["title"] == "Unauthorized"

    # 403 Forbidden
    res_403 = client.get("/_test/raise-403")
    assert res_403.status_code == 403
    assert res_403.json()["title"] == "Forbidden"

    # 422 Validation Error
    res_422 = client.get("/_test/raise-422?age=not_an_int")
    assert res_422.status_code == 422
    body_422 = res_422.json()
    assert body_422["status"] == 422
    assert "invalid_params" in body_422
    assert len(body_422["invalid_params"]) >= 1

    # 500 Unhandled Error must NOT leak internal exception string or Traceback
    res_500 = client.get("/_test/raise-500", headers={"X-Request-ID": "trace-500"})
    assert res_500.status_code == 500
    body_500 = res_500.json()
    assert body_500["status"] == 500
    assert body_500["request_id"] == "trace-500"
    assert "SECRET_DB_INTERNAL_FAILURE_DETAILS" not in res_500.text
    assert "Traceback" not in res_500.text


def test_logging_phi_scrubbing() -> None:
    """Verify structured logger redacts credentials and emails."""
    raw = "Auth failed for email=patient@example.com password=SuperSecret123 token=eyJabc"
    scrubbed = scrub_sensitive_text(raw)
    assert "SuperSecret123" not in scrubbed
    assert "patient@example.com" not in scrubbed
    assert "eyJabc" not in scrubbed
    assert "[REDACTED]" in scrubbed
