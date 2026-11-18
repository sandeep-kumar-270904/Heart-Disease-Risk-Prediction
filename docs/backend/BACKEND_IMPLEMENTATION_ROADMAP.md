# HeartXAI 2.0 — Backend Implementation Roadmap & Delivery Stages

**Document ID:** `HX2-BE-016`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect & Engineering Delivery Lead  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001 through ADR-011  

---

## 1. Roadmap Architecture & Delivery Principles

This roadmap establishes the phased engineering sequence for implementing the **HeartXAI 2.0 Backend**.

To maximize velocity for an individual engineer while maintaining production-grade reliability, the roadmap follows **Three Delivery Invariants**:
1. **Vertical Core Spine First:** Stages 1 through 9 deliver the foundational database, authentication, clinical assessment intake, XGBoost inference, and TreeSHAP explainability engine before ancillary features (directories, reports, admin command center) are added.
2. **PostgreSQL 16 Parity:** All database integrations are developed and tested against real PostgreSQL 16 instances with asyncpg.
3. **Automated Definition of Done (DoD):** Every stage requires 100% passing automated tests, zero Ruff/Mypy linting errors, and full compliance with the Stripe-style error envelope.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   15-STAGE BACKEND DELIVERY PIPELINE                   │
├────────────────────────────────────────────────────────────────────────┤
│ [Stage 1: Foundation] ──► [Stage 2: Database] ──► [Stage 3: Models/Mig]│
│                                                           │            │
│ [Stage 6: Assessment] ◄── [Stage 5: Profiles] ◄── [Stage 4: Auth/Sec]  │
│         │                                                              │
│         ▼                                                              │
│ [Stage 7: ML Inference] ──► [Stage 8: TreeSHAP] ──► [Stage 9: Scenarios]│
│                                                            │           │
│ [Stage 12: Insurance] ◄── [Stage 11: Directory] ◄── [Stage 10: History]│
│         │                                                              │
│         ▼                                                              │
│ [Stage 13: PDF Reports] ──► [Stage 14: Admin] ──► [Stage 15: Security] │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Delivery Stages

---

### Stage 01: Project Foundation, Tooling & Core Configuration
- **Scope:** Initialize Poetry manifest, FastAPI application factory, Pydantic settings parsing, structured JSON logging with correlation IDs, health liveness probe.
- **Expected Files:**
  - `pyproject.toml`, `app/main.py`, `app/config/settings.py`, `app/config/constants.py`
  - `app/core/logging.py`, `app/middleware/correlation.py`, `app/api/v1/routes/health.py`
- **Dependencies:** `fastapi`, `uvicorn`, `pydantic-settings`, `structlog`.
- **Acceptance Criteria & Tests:** `uvicorn app.main:app` boots cleanly; `GET /api/v1/health/live` returns `200 OK` with JSON; correlation ID middleware logs structured outputs.
- **Definition of Done:** Zero linting errors via Ruff, strict Mypy validation pass.

---

### Stage 02: Database Connectivity & Unit of Work Infrastructure
- **Scope:** Configure asynchronous SQLAlchemy 2.0 engine, asyncpg connection pool, session dependency injection, generic repository base, and Unit of Work context manager.
- **Expected Files:**
  - `app/core/database.py`, `app/core/unit_of_work.py`
  - `app/repositories/base.py`, `app/api/deps.py`
- **Dependencies:** `sqlalchemy`, `asyncpg`.
- **Acceptance Criteria & Tests:** Database health check verifies active asyncpg pool connection; Unit of Work commits and rolls back transactions as expected.
- **Definition of Done:** Transactional rollback test passes against PostgreSQL test container.

---

### Stage 03: SQLAlchemy Models & Alembic Migrations
- **Scope:** Implement declarative ORM entities (`User`, `PatientProfile`, `Assessment`, `InferenceResult`, `ShapExplanation`, `AuditLog`), configure Alembic environment, and generate Initial Migration 001.
- **Expected Files:**
  - `app/models/base.py`, `user.py`, `patient_profile.py`, `assessment.py`, `inference_result.py`, `shap_explanation.py`, `audit_log.py`
  - `alembic/env.py`, `alembic/versions/001_initial_schema.py`
- **Dependencies:** `alembic`, `sqlalchemy`.
- **Acceptance Criteria & Tests:** `alembic upgrade head` creates all tables and foreign key indexes cleanly; `alembic downgrade base` cleanly reverts schema.
- **Definition of Done:** Automated test executes upgrade and downgrade against live PostgreSQL instance without errors.

---

### Stage 04: Authentication, Argon2id & Session Cookies
- **Scope:** Password hashing via Argon2id, JWT token issuance, HttpOnly cookie management, CSRF middleware, login, registration, logout, and `/auth/me` endpoints.
- **Expected Files:**
  - `app/core/security.py`, `app/services/auth_service.py`, `app/repositories/user_repo.py`
  - `app/api/v1/routes/auth.py`, `app/schemas/auth.py`, `app/middleware/security_headers.py`
- **Dependencies:** `argon2-cffi`, `pyjwt`.
- **Acceptance Criteria & Tests:** Registration hashes passwords with Argon2id; login sets `HttpOnly` cookie; invalid credentials return 401; 5 failed logins lock account for 15 minutes.
- **Definition of Done:** 100% test pass on registration, login, logout, refresh, and CSRF header validation.

---

### Stage 05: Patient Profiles & Consent Grant Management
- **Scope:** Patient demographic baselines, measurement unit preferences (`UnitContext`), clinician consent grant issuance and revocation endpoints.
- **Expected Files:**
  - `app/services/patient_service.py`, `app/repositories/grant_repo.py`
  - `app/api/v1/routes/patients.py`, `app/schemas/patients.py`
- **Acceptance Criteria & Tests:** Patient can update preferred units ($\text{mg/dL} \leftrightarrow \text{mmol/L}$); patient can issue and revoke doctor consent grants with instant expiration enforcement.
- **Definition of Done:** Zero cross-tenant consent leakage in unit tests.

---

### Stage 06: Clinical Assessment Intake & Boundary Validation
- **Scope:** Ingest 13 raw clinical biomarkers, execute Pydantic v2 range validation, unit conversion normalization, acute symptom emergency intercept, and draft persistence.
- **Expected Files:**
  - `app/services/assessment_service.py`, `app/repositories/assessment_repo.py`
  - `app/api/v1/routes/assessments.py`, `app/schemas/assessment.py`
- **Acceptance Criteria & Tests:** Rejects systolic BP $< 70$ or $> 240\text{ mmHg}$; converts `mmol/L` cholesterol to `mg/dL`; flags acute symptom emergencies if resting angina + severe hypertension.
- **Definition of Done:** Validation test suite achieves $100\%$ boundary condition coverage.

---

### Stage 07: ML Prediction Subsystem Integration
- **Scope:** Load Cleveland-cohort XGBoost artifact, verify SHA256 checksum at startup, execute inference via `asyncio.to_thread`, compute 95% Wilson confidence intervals, and map risk strata.
- **Expected Files:**
  - `app/ml/pipeline.py`, `app/ml/preprocessor.py`, `app/services/inference_service.py`
  - `app/schemas/inference.py`, `app/ml/artifacts/checksums.sha256`
- **Dependencies:** `xgboost`, `scikit-learn`, `numpy`.
- **Acceptance Criteria & Tests:** Inference executes in $< 15\text{ms}$; checksum verification halts startup on tampered artifact; Wilson confidence intervals calculate accurately.
- **Definition of Done:** Prediction output labeled strictly as *"Angiographic CAD Association Likelihood"*.

---

### Stage 08: TreeSHAP Feature Explainability Integration
- **Scope:** Integrate `shap.TreeExplainer`, compute local feature attributions for 13 features, enforce local accuracy property ($\sum \phi_i = f(x) - E[f(x)]$), and generate plain-language explanations.
- **Expected Files:**
  - `app/ml/explainer.py`, `app/services/explainability_service.py`
  - `app/schemas/explainability.py`, `app/repositories/inference_repo.py`
- **Dependencies:** `shap`.
- **Acceptance Criteria & Tests:** Asserts local accuracy within $10^{-4}$ tolerance across 100 synthetic test profiles; maps Crimson `▲` vs Blue `▼` directional impacts.
- **Definition of Done:** TreeSHAP pipeline runs reliably under $50\text{ms}$ execution budget.

---

### Stage 09: Counterfactual "What-If" Scenario Simulator
- **Scope:** Constrained physiological perturbation engine for modifiable clinical variables, biological clamp enforcement, and simulated delta computation.
- **Expected Files:**
  - `app/ml/counterfactual_engine.py`, `app/services/counterfactual_service.py`
  - `app/schemas/counterfactual.py`
- **Acceptance Criteria & Tests:** Rejects modification of Age/Sex; asserts simulated blood pressure adheres to outpatient viability bounds; calculates correct probability delta.
- **Definition of Done:** Counterfactual endpoint returns simulated result in $< 20\text{ms}$.

---

### Stage 10: Assessment History & Longitudinal Trends
- **Scope:** Filterable assessment history queries, pagination controls, and multi-biomarker longitudinal trend aggregations.
- **Expected Files:**
  - `app/api/v1/routes/history.py`, `app/schemas/history.py`
- **Acceptance Criteria & Tests:** Paginated queries enforce limit clamps; trend queries return chronologically ordered arrays distinguishing missing readings from zero values.
- **Definition of Done:** Query execution time verified $< 30\text{ms}$ on 10,000 synthetic assessment rows.

---

### Stage 11: Country-Configurable Healthcare Directories (ADR-011)
- **Scope:** Implement `ICountryAdapter` base class and country adapters for India (`IN`), USA (`US`), and UK (`GB`), with caching and verified emergency hotline endpoints.
- **Expected Files:**
  - `app/integrations/base.py`, `india_adapter.py`, `usa_adapter.py`, `uk_adapter.py`
  - `app/services/directory_service.py`, `app/api/v1/routes/directory.py`
- **Acceptance Criteria & Tests:** `?country=IN` routes through India adapter returning NMC registry details and 112/102 emergency numbers; handles external API timeout gracefully via cached fallbacks.
- **Definition of Done:** All 3 country adapters verified with mock external integration tests.

---

### Stage 12: Health Insurance Guidance
- **Scope:** Localized health insurance policy information, cardiac diagnostic coverage summaries, pre-authorization checklists, and TPA helplines.
- **Expected Files:**
  - `app/services/insurance_service.py`, `app/schemas/insurance.py`
- **Acceptance Criteria & Tests:** Returns accurate IRDAI / PM-JAY information for India and ACA preventative care rules for USA.
- **Definition of Done:** Static insurance guides validated against official national healthcare sources.

---

### Stage 13: Consultation PDF Report Generation
- **Scope:** HTML/CSS Jinja2 clinical template compilation, server-side PDF generation via WeasyPrint, and streaming delivery endpoint with ownership enforcement.
- **Expected Files:**
  - `app/services/report_service.py`, `app/templates/clinical_report.html`, `app/templates/report_styles.css`
  - `app/api/v1/routes/reports.py`
- **Dependencies:** `weasyprint`.
- **Acceptance Criteria & Tests:** Generates valid PDF ($> 10\text{ KB}$) in memory; streams with `Content-Disposition: attachment`; rejects unauthorized patient or clinician access attempts.
- **Definition of Done:** Zero temporary files written to unencrypted disk; PDF compiles in $< 800\text{ms}$.

---

### Stage 14: Administrative Command Center & Governance
- **Scope:** System telemetry metrics endpoint, clinician credential verification queue with PDF inspection, model registry metadata, and immutable audit log queries.
- **Expected Files:**
  - `app/services/admin_service.py`, `app/repositories/audit_repo.py`
  - `app/api/v1/routes/admin.py`, `app/schemas/admin.py`
- **Acceptance Criteria & Tests:** Non-admin accounts receive `403 Forbidden`; administrative decisions write immutable audit events with actor ID and timestamp.
- **Definition of Done:** All administrative endpoints covered by role-based integration tests.

---

### Stage 15: Security Hardening, OWASP Verification & Performance Sign-Off
- **Scope:** Execute automated OWASP API Top 10 security test suite (BOLA, BFLA, CSRF, Injection), load testing via Locust/k6, and final readiness validation.
- **Expected Files:**
  - `tests/security/test_bola.py`, `test_bfla.py`, `test_csrf.py`, `test_rate_limiting.py`
- **Acceptance Criteria & Tests:** Zero OWASP API Top 10 vulnerabilities; P95 API response duration $< 50\text{ms}$; 100% test pass on full regression suite.
- **Definition of Done:** Backend signed off and ready for deployment.
