# HeartXAI 2.0 — Backend Testing Strategy & Quality Assurance Plan

**Document ID:** `HX2-BE-014`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Backend Quality Lead & Test Automation Architect  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-006  

---

## 1. Testing Philosophy & Test Pyramid

In healthcare machine learning systems, testing must verify both standard software functionality and **mathematical/clinical invariants**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TESTING PYRAMID LAYERS                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. End-to-End API Integration Tests (PostgreSQL 16)                    │
│ 2. Security & Cross-Tenant Access Prevention Tests (OWASP Top 10)     │
│ 3. ML Subsystem & TreeSHAP Mathematical Property Tests                 │
│ 4. Unit of Work & Transactional Rollback Tests                         │
│ 5. Isolated Unit Tests (Argon2id, Preprocessors, Unit Converters)      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Test Harness Tooling & Configuration

- **Test Runner:** `pytest` (`^8.2.0`) with `pytest-asyncio` (`^0.23.6`) in `asyncio_mode = "auto"`.
- **Database Strategy (ADR-006):**
  - Unit tests run against fast in-memory SQLite for rapid TDD iterations.
  - Integration, migration, and security tests execute against an ephemeral, containerized **PostgreSQL 16** test instance via `testcontainers` or Docker Compose.
- **HTTP Client:** `httpx.AsyncClient` with `ASGITransport(app=app)` for direct in-process asynchronous endpoint testing.
- **Coverage Target:** $\ge 85\%$ branch and line coverage enforced via `pytest-cov`.

---

## 3. Detailed Test Suites by Engineering Domain

### 3.1 Domain 1: Unit & Preprocessing Tests (`tests/unit/`)
- `test_units.py`:
  - Asserts $200.0\text{ mg/dL} \leftrightarrow 5.17\text{ mmol/L}$ conversion fidelity.
  - Asserts physiological clamping rejects negative blood pressure ($< 70\text{ mmHg}$) and impossible cholesterol ($> 600\text{ mg/dL}$).
- `test_preprocessor.py`:
  - Verifies 13-feature array ordering matches Cleveland training vector index mapping.
  - Asserts missing `ca` and `thal` are imputed with cohort median values ($0.0$ and $2.0$).
- `test_crypto.py`:
  - Verifies Argon2id password hashing produces valid hashes and rejects incorrect plaintexts.
  - Asserts JWT expiry enforcement and signature verification.

### 3.2 Domain 2: ML & Explainability Mathematical Invariants (`tests/integration/test_ml.py`)
- **Model Checksum Test:** Asserts `cleveland_xgboost_v2.4.1.json` matches SHA256 checksum in `checksums.sha256`.
- **TreeSHAP Sum Consistency (Local Accuracy):**
  - For 100 synthetic test patients, asserts:
    $$\left| \left( E[f(x)] + \sum_{i=1}^{13} \phi_i \right) - f(x) \right| < 10^{-4}$$
- **Counterfactual Guardrails Test:**
  - Asserts attempt to modify Age or Biological Sex raises `ClinicalBoundaryException`.
  - Asserts simulating blood pressure outside $[90, 200]\text{ mmHg}$ raises `PhysiologicalClampException`.

### 3.3 Domain 3: Database Transactions & Unit of Work (`tests/integration/test_database.py`)
- **Atomic Rollback Test:**
  - Simulates an unhandled exception thrown during SHAP calculation.
  - Asserts that neither the `assessments` row nor the `inference_results` row remains in the database (100% rollback).
- **Foreign Key Cascade Test:**
  - Deleting a patient user automatically deletes associated `assessments`, `inferences`, and `shap_explanations`.

### 3.4 Domain 4: Authorization & Cross-Tenant Access Prevention (`tests/security/`)
- **Cross-Patient Isolation Test (`test_patient_isolation.py`):**
  - Create Patient A and Patient B with separate assessments.
  - Patient A requests `GET /api/v1/assessments/{Patient_B_Assessment_ID}`.
  - Assert response is strictly `404 Not Found` (anti-enumeration).
- **Clinician Consent Grant Test (`test_clinician_access.py`):**
  - Clinician queries Patient A's assessment without grant $\rightarrow$ Assert `403 Forbidden`.
  - Patient A grants consent $\rightarrow$ Clinician queries assessment $\rightarrow$ Assert `200 OK`.
  - Patient A revokes grant $\rightarrow$ Clinician queries assessment $\rightarrow$ Assert `403 Forbidden`.
- **Admin Privilege Limitation Test (`test_admin_limits.py`):**
  - Administrator attempts to submit an assessment $\rightarrow$ Assert `403 Forbidden` (Admin role cannot create clinical patient data).

### 3.5 Domain 5: End-to-End Workflow Tests (`tests/integration/test_e2e_workflows.py`)
- Full lifecycle scenario:
  1. Register new patient $\rightarrow$ Verify email $\rightarrow$ Login $\rightarrow$ Capture session cookies.
  2. Submit 13 clinical biomarkers via `POST /api/v1/assessments`.
  3. Verify `HTTP 201 Created` with CAD likelihood and 95% confidence intervals.
  4. Query `GET /api/v1/assessments/:id/shap` $\rightarrow$ Assert 13 feature impact objects returned.
  5. Query `POST /api/v1/assessments/:id/scenarios` $\rightarrow$ Modify systolic BP from 154 to 125 $\rightarrow$ Assert simulated risk delta is negative.
  6. Request `GET /api/v1/reports/assessments/:id/pdf` $\rightarrow$ Verify binary PDF stream ($> 10\text{ KB}$, valid `%PDF-1.` header).
  7. Verify immutable audit log table contains records for registration, assessment creation, and report generation.
