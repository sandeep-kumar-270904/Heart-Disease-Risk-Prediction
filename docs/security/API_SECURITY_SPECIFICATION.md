# API SECURITY SPECIFICATION (OWASP API TOP 10 ALIGNED)

**Document Reference:** `docs/security/API_SECURITY_SPECIFICATION.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Design  
**Author:** Application Security Specialist & Backend Architect  
**Traceability:** FR-API-*, NFR-SEC-01 through NFR-SEC-09, ADR-009, ADR-011  

---

## 1. Executive Summary

The HeartXAI 2.0 backend exposes a comprehensive RESTful API under `/api/v1`. Because this interface directly ingests clinical biomarkers, runs machine learning models, and serves personal health records, API endpoints represent the primary attack surface.

This specification maps the platform's API defenses against the **OWASP API Security Top 10 (2023)** framework, detailing input validation, rate limiting, error sanitization, response filtering, and anti-abuse mechanisms.

---

## 2. OWASP API Security Top 10 (2023) Mapping & Controls

| OWASP API Risk | Threat Description | HeartXAI 2.0 Architectural Defense | Verification Check |
| :--- | :--- | :--- | :--- |
| **API1:2023 Broken Object Level Authorization (BOLA / IDOR)** | Attacker replaces `prediction_id` in path to view another patient's clinical history. | Reusable FastAPI route dependencies (`deps.py`) assert `prediction.user_id == current_user.id` or verified clinician consent. Database RLS enabled. | IDOR unit tests assert HTTP 404 for cross-patient ID queries. |
| **API2:2023 Broken Authentication** | Credential stuffing, weak password reset tokens, unvalidated JWT signatures. | Argon2id password hashing, Redis sliding-window brute-force lockouts, short-lived access JWTs (15 min), rotated HttpOnly refresh cookies. | Automated penetration test script simulating token replay and brute-force. |
| **API3:2023 Broken Object Property Level Authorization (Mass Assignment)** | User updates profile and injects `{"role": "ADMIN"}` or `{"is_verified": true}` into request body. | Pydantic V2 schemas (`UserUpdate`) strictly whitelist mutable fields; internal fields (`role`, `is_superuser`) are omitted. Extra fields rejected. | Schema validation test injecting forbidden keys asserts HTTP 422. |
| **API4:2023 Unrestricted Resource Consumption** | Rapid requests to `/api/v1/predictions` overwhelm CPU with XGBoost / TreeSHAP computations. | Multi-tier rate limiting: 10 req/min for ML predictions; max request payload 100 KB; bounded pagination (`limit` capped at 50 records). | Load test asserting HTTP 429 when burst threshold exceeded. |
| **API5:2023 Broken Function Level Authorization (BFLA)** | Regular patient invokes administrative endpoint (`/api/v1/admin/audit-logs`). | Strict RBAC dependency `require_role(UserRole.ADMIN)` blocks any non-admin token with HTTP 403 Forbidden. | Role boundary test executing all admin endpoints with patient token. |
| **API6:2023 Unrestricted Access to Sensitive Business Flows** | Automated bots mass-create fake accounts to scrape doctor directories or poison databases. | Rate limiting (5 registrations/hr per IP); email verification requirement; bot challenge integration on registration anomalies. | Automated account creation script blocked by rate limiter. |
| **API7:2023 Server-Side Request Forgery (SSRF)** | Attacker provides malicious URL in country directory parameters, forcing server to query internal metadata. | Strict domain whitelisting for all external HTTP clients; DNS transport validator blocks resolution to RFC 1918 private IP subnets. | SSRF penetration test injecting `169.254.169.254` into directory parameters. |
| **API8:2023 Security Misconfiguration** | Verbose error stack traces, unrestrictive CORS (`*`), unencrypted HTTP endpoints. | Centralized exception handler maps all errors to RFC 7807 Problem Details; stack traces disabled in non-dev; CORS whitelists explicit origins. | Error response test injecting divide-by-zero asserts clean JSON error. |
| **API9:2023 Improper Inventory Management** | Old unpatched API versions (e.g. `/api/v0`) left running and unauthenticated. | Explicit URI prefixing (`/api/v1`); strict deprecation headers; single active API gateway codebase without legacy endpoint rot. | Route inventory scan verifying 100% of exposed routes exist in v1 router. |
| **API10:2023 Unsafe Consumption of APIs** | Malicious or malformed responses from third-party country directories crash backend or inject XSS. | Third-party responses validated through strict Pydantic parsing schemas before internal consumption; timeouts capped at 3.0 seconds. | Injected corrupted JSON from mock external directory handled gracefully. |

---

## 3. Strict Input Validation & Range Sanitization

All incoming JSON payloads are validated using Pydantic V2. For clinical prediction requests, inputs are clamped to physiologically possible boundaries:

```python
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    age: float = Field(..., ge=20.0, le=100.0, description="Age in years (20-100)")
    sex: float = Field(..., ge=0.0, le=1.0, description="0: Female, 1: Male")
    cp: float = Field(..., ge=1.0, le=4.0, description="Chest pain type (1-4)")
    trestbps: float = Field(..., ge=80.0, le=240.0, description="Resting blood pressure mmHg (80-240)")
    chol: float = Field(..., ge=100.0, le=600.0, description="Serum cholesterol mg/dL (100-600)")
    fbs: float = Field(..., ge=0.0, le=1.0, description="Fasting blood sugar > 120 mg/dL")
    restecg: float = Field(..., ge=0.0, le=2.0, description="Resting ECG results (0-2)")
    thalach: float = Field(..., ge=60.0, le=220.0, description="Max heart rate bpm (60-220)")
    exang: float = Field(..., ge=0.0, le=1.0, description="Exercise induced angina")
    oldpeak: float = Field(..., ge=0.0, le=10.0, description="ST depression (0.0-10.0)")
    slope: float = Field(..., ge=1.0, le=3.0, description="Slope of peak exercise ST (1-3)")
    ca: float = Field(..., ge=0.0, le=3.0, description="Major vessels colored by fluoroscopy (0-3)")
    thal: float = Field(..., ge=3.0, le=7.0, description="Thallium stress test (3, 6, 7)")

    model_config = {
        "extra": "forbid", # Reject any unrecognized or unexpected keys immediately
        "str_strip_whitespace": True
    }
```

---

## 4. Response Filtering & Zero-Leakage Error Handling

### 4.1 Strict Response Schemas (Outbound Filtering)
Internal database entities are never returned directly to the client. Dedicated Pydantic response models filter sensitive attributes:
- `UserResponse` excludes `hashed_password`, `mfa_secret`, `failed_login_attempts`, and internal notes.
- `PredictionResponse` excludes internal model tree pointers and unrounded raw log-odds.

### 4.2 Centralized Exception Handling (RFC 7807 Problem Details)
To ensure that database errors, internal file paths, and Python stack traces are never exposed in API responses:

```python
# Centralized Error Envelope Response
{
  "type": "https://heartxai.internal/errors/validation-error",
  "title": "Invalid Request Parameters",
  "status": 422,
  "detail": "Resting blood pressure value 280 mmHg exceeds physiological limit of 240 mmHg.",
  "instance": "/api/v1/predictions",
  "correlation_id": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```

In production mode (`DEBUG=False`), unexpected internal server exceptions return a generic HTTP 500 Problem Details envelope with the correlation ID, while the full traceback is routed exclusively to secure internal log storage for investigation.

---

## 5. Rate Limiting Architecture & Tiers

Rate limits are implemented via a Redis token-bucket / sliding-window counter:

| Endpoint Family | Rate Limit (Anonymous IP) | Rate Limit (Authenticated User) | Burst Tolerance |
| :--- | :---: | :---: | :---: |
| **Authentication (`/auth/login`, `/auth/register`)** | $20\text{ req / min}$ | $5\text{ failed / 15 min}$ | 5 requests |
| **Password Reset (`/auth/reset-password`)** | $5\text{ req / hr}$ | $3\text{ req / hr}$ | 1 request |
| **Clinical Predictions (`/predictions`)** | Blocked (Requires Auth) | $10\text{ req / min}$ | 2 requests |
| **General Read (`/users/me`, `/directories`)** | $60\text{ req / min}$ | $120\text{ req / min}$ | 20 requests |
| **File Uploads (`/files/upload`)** | Blocked (Requires Auth) | $5\text{ uploads / hr}$ | 1 request |

---

## 6. Cross-Origin Resource Sharing (CORS) Configuration

In production, CORS is locked down to explicit trusted web application domains:
```python
# Production CORS Settings (FastAPI CORSMiddleware)
CORS_ORIGINS = [
    "https://app.heartxai.org",
    "https://admin.heartxai.org"
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = [
    "Authorization",
    "Content-Type",
    "X-Correlation-ID",
    "X-Country-Code"
]
```
Wildcard origins (`*`) are explicitly rejected when credentials are enabled.
