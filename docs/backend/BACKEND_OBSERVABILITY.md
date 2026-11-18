# HeartXAI 2.0 — Backend Observability, Logging & Operations

**Document ID:** `HX2-BE-015`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal SRE & Lead Backend Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-007, HXAI-ARCH-013  

---

## 1. Observability Philosophy & The Three Pillars

The HeartXAI 2.0 observability framework is designed for **rapid fault detection**, **security forensics**, and **clinical audit defensibility**, while strictly enforcing **PHI/PII Redaction**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE THREE PILLARS OF OBSERVABILITY                   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Structured JSON Logs ── Context-bound, correlation-tagged, redacted │
│ 2. Telemetry & Metrics  ── Latency distributions, DB pools, ML timings │
│ 3. Distributed Tracing  ── Request propagation via X-Correlation-ID    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Structured JSON Logging Specification (`structlog`)

### 2.1 Logger Configuration
In production, all logs are emitted as single-line JSON objects to standard output (`stdout`), formatted for ingestion by CloudWatch, Datadog, or Grafana Loki:

```python
import structlog
from app.core.logging import scrub_sensitive_keys

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        scrub_sensitive_keys,  # Redacts password, token, authorization headers
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
```

### 2.2 Sensitive Data Scrubbing Filter
Keys matching sensitive patterns are replaced with `"[REDACTED]"` before log serialization:
- `password`, `hashed_password`, `new_password`
- `access_token`, `refresh_token`, `csrf_token`, `authorization`
- `national_id`, `ssn`, `aadhaar`

---

## 3. Correlation ID Lifecycle & Request Tracking

1. **Incoming Request:** `CorrelationIdMiddleware` extracts `X-Correlation-ID` from incoming headers (or generates a fresh `uuid4`).
2. **Context Binding:** Bound to Python's `contextvars` context, automatically injecting `correlation_id` into every log statement emitted during that request lifecycle.
3. **Response Header:** Injected into outgoing response: `X-Correlation-ID: {correlation_id}`.
4. **Error Alignment:** In the event of an unhandled HTTP 500 error, the correlation ID is included in the JSON error envelope, allowing users to report the exact incident identifier to technical support.

---

## 4. Health & Readiness Probes (`/api/v1/health/*`)

HeartXAI 2.0 provides two distinct health endpoints for container orchestrators (Kubernetes / AWS ECS):

### 4.1 Liveness Probe (`GET /api/v1/health/live`)
- **Purpose:** Verifies that the FastAPI process is responsive and the event loop is not deadlocked.
- **Response:** `HTTP 200 OK` $\rightarrow$ `{ "status": "alive" }`.

### 4.2 Readiness Probe (`GET /api/v1/health/ready`)
- **Purpose:** Verifies that all foundational downstream dependencies are healthy and capable of serving traffic.
- **Checks Executed:**
  1. *Database Connectivity:* Executes `SELECT 1` via `AsyncSession` (timeout: $2.0\text{s}$).
  2. *Model Artifact Verification:* Verifies XGBoost model and TreeSHAP explainer are loaded in memory with valid checksums.
  3. *Disk Capacity:* Confirms writable temporary storage has $\ge 500\text{ MB}$ available.
- **Response:**
  - If all pass: `HTTP 200 OK` $\rightarrow$ `{ "status": "ready", "database": "healthy", "ml_engine": "healthy" }`.
  - If any fail: `HTTP 503 Service Unavailable` $\rightarrow$ `{ "status": "unhealthy", "failing_component": "database" }`.

---

## 5. Metrics & Operational Telemetry

Key service performance indicators monitored in production:

| Metric Name | Type | Target / Alert Threshold | Purpose |
| :--- | :---: | :--- | :--- |
| `http_request_duration_seconds` | Histogram | $\text{P95} < 50\text{ms}$, $\text{P99} < 200\text{ms}$ | Tracks API responsiveness. |
| `ml_inference_duration_seconds` | Histogram | $\text{P95} < 25\text{ms}$ | Measures XGBoost + TreeSHAP execution speed. |
| `db_connection_pool_saturation` | Gauge | Alert if saturation $> 80\%$ for $2\text{ mins}$ | Prevents connection starvation. |
| `failed_auth_attempts_total` | Counter | Alert if $> 20\text{ failures / min}$ | Detects brute-force credential stuffing. |
| `emergency_warning_triggered_total`| Counter | Track count of acute symptom alerts | Monitors clinical safety triage events. |
| `model_drift_psi_score` | Gauge | Alert if $\text{PSI} > 0.15$ | Detects population covariate dataset shift. |

---

## 6. Sentry Exception Capture & Performance Tracing

- Initialized in `app/main.py`:
  ```python
  import sentry_sdk
  from sentry_sdk.integrations.fastapi import FastApiIntegration

  sentry_sdk.init(
      dsn=settings.SENTRY_DSN,
      environment=settings.ENVIRONMENT,
      integrations=[FastApiIntegration(transaction_style="endpoint")],
      traces_sample_rate=0.1, # 10% performance tracing in production
      send_default_pii=False, # Strictly disables PII capture
  )
  ```
- Before Sentry transmission, a custom `before_send` hook strips any query parameters or form fields containing clinical biomarker measurements.
