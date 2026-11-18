# HeartXAI 2.0 — Backend Engineering Acceptance Criteria

**Document ID:** `HX2-BE-017`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect & Quality Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001 through ADR-011  

---

## 1. Overview & Verification Policy

This document defines the **binding, measurable acceptance criteria** required for signing off the backend implementation of **HeartXAI 2.0**.

No pull request or deployment may be approved without passing 100% of the criteria across all ten engineering categories detailed below.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   BACKEND ACCEPTANCE AUDIT DOMAINS                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Architecture & Layer Boundaries   │ 6. ML & Explainability Bounds   │
│ 2. Type Safety & Schema Validation   │ 7. Error Handling & Redaction   │
│ 3. Database Integrity & UoW          │ 8. Observability & Logging      │
│ 4. Authentication & Session Hygiene  │ 9. Performance & Latency        │
│ 5. Authorization & Patient Isolation │ 10. Automated Test Coverage     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Binding Engineering Acceptance Checklist

### 1. Architecture & Layer Boundaries
- [ ] **Four-Layer Inward Flow:** Dependencies flow strictly inward from Transport $\rightarrow$ Services $\rightarrow$ ML/Domain $\rightarrow$ Repositories.
- [ ] **No Raw Queries in Routes:** Route handlers contain zero raw SQLAlchemy queries or direct database cursor operations.
- [ ] **No Circular Imports:** Verified via Ruff and Mypy with zero circular import warnings.
- [ ] **Unit of Work Pattern:** Multi-entity operations (e.g., assessment + inference + SHAP) execute inside an atomic Unit of Work context.

### 2. Type Safety & Schema Validation
- [ ] **Pydantic v2 Strict Mode:** All request DTOs enforce `extra = "forbid"` and numeric validation bounds via `Field(ge=..., le=...)`.
- [ ] **Strict Mypy Compliance:** Zero `Any` types in service interfaces; Mypy passes with `--strict` and zero errors.
- [ ] **OpenAPI 3.1 Alignment:** Generated `/openapi.json` schema matches frontend client expectations 100%.

### 3. Database Integrity & Persistence
- [ ] **PostgreSQL 16 Parity:** All integration tests pass against an active PostgreSQL 16 instance.
- [ ] **Alembic Migration Reversibility:** All migrations execute `upgrade head` and `downgrade -1` cleanly without data truncation.
- [ ] **Foreign Key Enforcement:** Cascade deletes work as designed (deleting a patient cleanly purges assessments, inferences, and SHAP vectors).
- [ ] **Connection Pool Recycling:** Asyncpg pool recycles connections every 30 minutes to eliminate memory leaks.

### 4. Authentication & Session Hygiene
- [ ] **Argon2id Exclusivity:** All user passwords are encrypted using Argon2id (`time_cost=3, memory_cost=65536, parallelism=4`).
- [ ] **Zero LocalStorage Tokens:** JWT access and refresh tokens are transported exclusively via `HttpOnly`, `SameSite=Strict`, `Secure` cookies.
- [ ] **Double-Submit CSRF:** State-changing requests (`POST`, `PUT`, `DELETE`) require a valid `X-CSRF-Token` header matching the cookie.
- [ ] **Account Lockout:** 5 consecutive failed login attempts lock the target account for 15 minutes.

### 5. Authorization & Patient Data Isolation
- [ ] **Strict BOLA Prevention:** A patient cannot view, modify, or delete another patient's assessment records under any circumstances.
- [ ] **Anti-Enumeration 404:** Querying another patient's assessment returns `404 Not Found` rather than `403 Forbidden`.
- [ ] **Clinician Consent Grant Enforcement:** Clinicians cannot query patient records without an active, unexpired, unrevoked consent grant.
- [ ] **Immutable Audit Logging:** Every assessment creation, record access, clinician verification decision, and authentication failure is recorded in `audit_logs`.

### 6. Machine Learning & Explainability Invariants
- [ ] **Model Checksum Verification:** Application halts startup immediately if the model artifact SHA256 checksum does not match `checksums.sha256`.
- [ ] **Non-Diagnostic Output Labeling:** Model output is labeled strictly as *"Angiographic CAD Association Likelihood (Educational Model)"*. The terms *"Diagnosis"* or *"Heart Attack Probability"* are completely absent.
- [ ] **TreeSHAP Sum Consistency:** For every inference, $\sum \phi_i = f(x) - E[f(x)]$ within $10^{-4}$ tolerance.
- [ ] **Counterfactual Biological Clamps:** Sliders for non-modifiable factors (Age, Sex) cannot be modified; simulated physiological values must fall within outpatient viability ranges.

### 7. Error Handling & Redaction
- [ ] **Stripe-Style Error Envelope:** 100% of non-2xx HTTP responses adhere to the standard JSON error structure.
- [ ] **Zero Leaked Stack Traces:** Stack traces, internal file paths, and raw SQL queries never appear in HTTP response bodies.
- [ ] **Correlation ID Binding:** Every error response includes an incident correlation ID matching the structured server log.

### 8. Observability & Logging
- [ ] **Structured JSON Logs:** All logs are emitted as structured JSON to `stdout` via `structlog`.
- [ ] **PII/Password Scrubbing:** Keys matching `password`, `token`, `secret`, and `national_id` are automatically replaced with `"[REDACTED]"`.
- [ ] **Probes Operational:** `/api/v1/health/live` and `/api/v1/health/ready` respond accurately to container lifecycle events.

### 9. Performance & Latency Budgets
- [ ] **P95 API Latency:** 95% of API requests respond in $< 50\text{ms}$ under standard load.
- [ ] **ML Inference & SHAP Latency:** Combined XGBoost inference and TreeSHAP calculation executes in $< 25\text{ms}$.
- [ ] **PDF Generation Duration:** WeasyPrint server-side consultation PDF compiles in $< 800\text{ms}$.

### 10. Automated Test Coverage
- [ ] **Code Coverage:** Automated test suite achieves $\ge 85\%$ line and branch coverage.
- [ ] **OWASP API Top 10 Suite:** All 10 security test scenarios in `tests/security/` pass with zero failures.
- [ ] **End-to-End Suite:** Full patient lifecycle and admin verification E2E integration tests pass reliably.
