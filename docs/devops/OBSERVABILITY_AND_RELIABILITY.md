# OBSERVABILITY, MONITORING, AND RELIABILITY ENGINEERING SPECIFICATION

**Document Reference:** `docs/devops/OBSERVABILITY_AND_RELIABILITY.md`  
**Phase:** 10 — DevOps, Infrastructure, Deployment Architecture & Release Engineering  
**Status:** Approved Technical Architecture  
**Author:** Principal Site Reliability Engineer & Monitoring Architect  
**Traceability:** NFR-PERF-01, NFR-REL-01, NFR-SEC-06, ADR-001, ADR-009  

---

## 1. Executive Summary & SRE Observability Framework

Observability is the capability to infer the internal health, performance, and failure modes of a distributed software system solely from its external telemetry. In healthcare AI, observability must balance deep diagnostic visibility with strict data privacy: telemetry must pinpoint latency bottlenecks and failures while **strictly preventing personal health information (PHI) or authentication secrets from leaking into monitoring stores**.

HeartXAI 2.0 structures its reliability architecture across four pillars:
1. **Structured, Scrubbed JSONL Logging** (Correlation-ID linked).
2. **Prometheus / CloudWatch Metrics** (RED Method: Rate, Errors, Duration).
3. **Multi-Stage Health Probes** (`/health/live` and `/health/ready`).
4. **Graduated Alerting & Incident Escalation Matrices** (SEV-1 through SEV-3).

---

## 2. Structured Logging Architecture & Correlation Tracing

### 2.1 The Distributed Correlation Trace
Every incoming HTTP request receives an immutable `X-Correlation-ID` header injected at the Nginx reverse proxy. This correlation ID propagates through the FastAPI ASGI middleware, the internal `ThreadPoolExecutor` worker threads, and into database query execution contexts:

```json
{
  "timestamp": "2026-11-21T14:30:00.125Z",
  "level": "INFO",
  "service": "heartxai-backend",
  "correlation_id": "req-c8b1a432-8419-4b68-9a64-7d5a02e6b721",
  "endpoint": "/api/v1/predictions",
  "method": "POST",
  "status_code": 201,
  "duration_ms": 112.4,
  "ml_telemetry": {
    "model_version": "cleveland_xgboost_v1.0.0",
    "inference_ms": 7.8,
    "calibration_ms": 0.9,
    "shap_ms": 48.2,
    "counterfactual_ms": 55.5
  },
  "user_context": {
    "user_id_hash": "e3b0c44298fc1c149afbf4c8996fb924",
    "role": "PATIENT"
  }
}
```

### 2.2 PII/PHI Redaction Guarantee
In strict alignment with Phase 9 security specifications, all logging output routes through an automated regex filter (`app/core/logging.py`) that scrubs passwords, JWT tokens, and direct clinical biomarkers (`trestbps`, `chol`, `oldpeak`) before emission to disk or stdout.

---

## 3. Core Operational Metrics (The RED Method)

HeartXAI exports Prometheus-compatible metrics on an internal `/metrics` endpoint (accessible only to internal scrapers):

| Metric Name | Type | Description | Alert Threshold |
| :--- | :--- | :--- | :--- |
| `heartxai_http_requests_total` | Counter | Total HTTP requests partitioned by status code and method | Rate spike $> 300\text{ req/sec}$ |
| `heartxai_http_request_duration_seconds` | Histogram | Request latency distribution across endpoints | $P95 > 200\text{ ms}$ for 5 minutes |
| `heartxai_ml_pipeline_duration_seconds` | Histogram | Execution time of XGBoost + TreeSHAP + Counterfactuals | $P95 > 150\text{ ms}$ for 5 minutes |
| `heartxai_db_pool_active_connections` | Gauge | Active connections checked out of SQLAlchemy pool | $> 80\%$ pool saturation ($> 16 / 20$) |
| `heartxai_db_query_duration_seconds` | Histogram | Execution latency of PostgreSQL queries | Any query $> 250\text{ ms}$ |
| `heartxai_auth_failures_total` | Counter | Failed login attempts partitioned by failure reason | $> 15$ failures in 5 minutes |

---

## 4. Multi-Stage Health Check Probes

To integrate with container orchestrators (Docker Compose, Kubernetes, AWS ECS) and load balancers, HeartXAI exposes two distinct health endpoints:

```mermaid
graph TD
    Monitor[Load Balancer / Container Supervisor] --> Probe1{GET /health/live: Liveness Probe}
    Probe1 -- Process responsive --> LiveOK[HTTP 200 OK: Process alive]
    Probe1 -- Process deadlocked / crashed --> LiveFail[HTTP 500 / Timeout: Restart container]

    Monitor --> Probe2{GET /health/ready: Readiness Probe}
    Probe2 --> CheckDB[Test PostgreSQL connection]
    Probe2 --> CheckRedis[Test Redis ping]
    Probe2 --> CheckML[Test ML model loaded & warmed up]
    CheckDB & CheckRedis & CheckML -- All Healthy --> ReadyOK[HTTP 200 OK: Route user traffic]
    CheckDB or CheckRedis or CheckML -- Any Unhealthy --> ReadyFail[HTTP 503 Service Unavailable: Hold traffic]
```

### 4.1 `/health/live` (Liveness Probe)
- Tests whether the Python Uvicorn event loop is responsive.
- Returns `HTTP 200 {"status": "alive"}` in $< 1\text{ ms}$. If this endpoint times out for 3 consecutive checks (30 seconds), the container supervisor restarts the container.

### 4.2 `/health/ready` (Readiness Probe)
- Tests all critical internal dependencies:
  1. Executes `SELECT 1` against PostgreSQL via the connection pool.
  2. Executes `PING` against the Redis cache.
  3. Verifies that the primary XGBoost model and SHAP background tensors are loaded in memory and the warmup inference pass has passed.
- Returns `HTTP 200 {"status": "ready"}` only if **all** dependencies are verified. If any dependency is degraded, it returns `HTTP 503`, preventing the load balancer from sending user requests to an unready container.

---

## 5. Operational Alerting & Escalation Matrix

Alerts are categorized by severity and routed automatically to PagerDuty or designated Slack channels:

| Severity Level | Trigger Condition | Notification Channel | Target Response Time (MTTA) | Operational Action |
| :--- | :--- | :--- | :---: | :--- |
| **SEV-1 (Critical)** | System down (`/health/ready` failing $> 2\text{ min}$); HTTP 5xx rate $> 5\%$; Active database failover | PagerDuty On-Call (SMS / Phone Call) | **$\le 15\text{ minutes}$** | Immediate war room; rollback release or restart failed nodes. |
| **SEV-2 (High)** | API $P95$ latency $> 500\text{ ms}$ for 10 min; DB connection pool $> 85\%$; Suspicious credential stuffing spike | Slack `#alerts-high` + PagerDuty (Push) | **$\le 1.0\text{ hour}$** | Investigate slow queries, scale worker threads, inspect attacking IPs. |
| **SEV-3 (Medium)** | Background task failure; Model drift warning (PSI $\ge 0.15$); Host disk utilization $> 75\%$ | Slack `#alerts-devops` | **$\le 8.0\text{ hours}$** | Routine operational triage during business hours. |
