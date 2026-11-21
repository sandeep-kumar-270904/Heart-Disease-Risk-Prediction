# HeartXAI 2.0 — Master Implementation Roadmap (20 Milestones)
**Document ID:** HX-PR-011  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Principal Software Architect, Staff Systems Engineer & Technical Program Manager  
**Status:** Approved for Implementation Planning — Conditioned on User Governance Sign-Off  
**Date:** November 2026  

---

## 1. Executive Summary

This roadmap defines the authoritative 20-milestone engineering plan for HeartXAI 2.0. In accordance with the Phase 12.1 audit:
1. **100% Synthetic Data Mandate:** All development, unit testing, integration testing, demonstration, and staging milestones are restricted strictly to synthetic patient personas. Real patient health information (PHI) is strictly prohibited.
2. **Task A Only (MVP):** Machine learning is restricted strictly to experimental dataset classification of the heart-disease target on the UCI Cleveland cohort (Task A). Task B (prospective 10-year risk estimation) has been removed from the MVP and deferred to the future research roadmap.
3. **External Integrations Disabled:** Live hospital EHR and third-party commercial APIs remain disabled/mocked.
4. **Execution Invariant:** Antigravity must execute **exactly one milestone at a time**, verify automated tests, and pause for explicit user approval before proceeding.

---

## 2. Master Implementation Milestone Summary

```
+----+--------------------------------------------+-------------------------------------+-----------------+
| ID | Milestone Title                            | Primary Technology & Focus          | Prerequisite    |
+----+--------------------------------------------+-------------------------------------+-----------------+
| 01 | Repository & Dev Environment Foundation    | Git, Docker Compose, CI/CD Actions  | User Sign-Off   |
| 02 | Core Scaffolding & Canonical Types         | Pydantic v2, TypeScript 5.4, Linters| M01             |
| 03 | Design System & UI Component Library       | Tailwind CSS, Radix UI (WCAG 2.2 AA)| M02             |
| 04 | Database Engine & Schema Migrations        | PostgreSQL 16, SQLAlchemy, Alembic  | M02             |
| 05 | Backend Core Services & API Framework      | FastAPI, Error Middleware, CORS     | M04             |
| 06 | Authentication, Sessions & RBAC            | Argon2id, JWT, Redis Token Rotation | M05             |
| 07 | Frontend Shell, Routing & Auth State       | React 18, React Router v6, Zustand  | M03, M06        |
| 08 | Clinical Intake Wizard & Input Validation  | TanStack Form, Zod, Unit Converter  | M07             |
| 09 | ML Data Verification & Stratification      | UCI Cleveland Audit, Leak-Free Split| M02             |
| 10 | Task A Model Training & Calibration        | XGBoost 2.0, Platt/Isotonic, Brier  | M09             |
| 11 | In-Process ML Model Serving Pipeline       | In-Process C++ ML Worker, FastAPI   | M05, M10        |
| 12 | TreeSHAP Local Explanation Engine          | SHAP 0.45, Recharts Waterfall View  | M11, M08        |
| 13 | Constrained Counterfactual Engine          | DiCE-ML, Actionability Optimizer    | M11, M08        |
| 14 | Clinical Results & PDF Dossier Export      | PDF Generation, Non-Diagnostic View | M12, M13        |
| 15 | Localized Healthcare Directory             | Geo-Filtering, Emergency Contacts   | M05, M07        |
| 16 | Clinician Portal & Consent Sharing Grants  | 72-Hour Access Tokens, Doctor Notes | M06, M14        |
| 17 | Administrative Console & Audit Trail       | User Management, Audit Log Viewer   | M06, M15        |
| 18 | Security Hardening & Penetration Testing   | Bandit, Anti-IDOR, OWASP ZAP        | M16, M17        |
| 19 | Accessibility (WCAG 2.2 AA) & Performance  | axe-core, Lighthouse, K6 Stress Test| M18             |
| 20 | Staging Deployment & Final Acceptance (UAT)| Nginx SSL, Synthetic UAT Sign-Off   | M19             |
+----+--------------------------------------------+-------------------------------------+-----------------+
```

---

## 3. Detailed Milestone Specifications (Milestones 01 – 20)

### Milestone 01: Repository & Development Environment Foundation
- **Objective:** Establish reproducible, containerized local development and automated CI environments with zero production infrastructure provisioning and zero patient data processing.
- **Prerequisites:** Explicit user approval of Phase 12.1 governance decisions.
- **Key Tasks:** Configure `.editorconfig`, `.gitignore`, `docker-compose.yml` (PostgreSQL 16, Redis 7.2 alpine), pre-commit hooks (Ruff, ESLint), GitHub Actions CI workflows. Set `SYNTHETIC_DATA_ONLY=true`.
- **Deliverables:** Working local multi-container stack; automated CI workflow passing on baseline commit.
- **Files Affected:** `.gitignore`, `.editorconfig`, `docker-compose.yml`, `.github/workflows/ci.yml`, `README.md`.
- **Tests Required:** `docker compose up -d` starts cleanly; CI workflow executes linting and container health check.
- **Acceptance Criteria:** Local services report `healthy`; zero cloud infrastructure provisioned; CI pipeline runs green.
- **Risks:** Container port conflicts on host. Mitigation: Configurable host port mappings in `.env.example`.
- **Approval Gate:** Pause and present container status and CI execution logs to user for review.

### Milestone 02: Core Scaffolding, Canonical Types & Synthetic Data Generator
- **Objective:** Synchronize frontend TypeScript types and backend Pydantic v2 schemas from the single source of truth, and provide a synthetic patient data generator for testing.
- **Prerequisites:** Milestone 01.
- **Key Tasks:** Implement `shared/data-dictionary.json`; generate Pydantic v2 schemas; generate TypeScript interfaces; author `scripts/generate_synthetic_patients.py` to produce test cohorts with zero PHI.
- **Deliverables:** Typed schema contracts in `backend/app/schemas/` and `frontend/src/types/`; synthetic data generator.
- **Files Affected:** `shared/data-dictionary.json`, `backend/app/schemas/*`, `frontend/src/types/*`, `scripts/generate_synthetic_patients.py`.
- **Tests Required:** `mypy --strict` passes on schemas; `tsc --noEmit` passes on frontend types; synthetic generator outputs 50 valid test records.
- **Acceptance Criteria:** 100% parity across schemas; zero type warnings.
- **Risks:** Schema field name mismatches. Mitigation: Pydantic field aliases and automated contract tests.
- **Approval Gate:** User review of generated schemas and synthetic test data sample.

### Milestone 03: Design System & UI Component Library (WCAG 2.2 AA Target)
- **Objective:** Implement the approved design system tokens, accessible Radix UI primitives, and clinical visual hierarchy targeting WCAG 2.2 AA.
- **Prerequisites:** Milestone 02.
- **Key Tasks:** Configure Tailwind CSS with design tokens; implement Button, Input, Select, Modal, Alert, Badge, Card, and Tooltip primitives. Ensure focus appearance (2.4.11/2.4.13) and minimum target sizes (2.5.8, $\ge 24\text{px}$).
- **Deliverables:** Accessible component library in `frontend/src/components/ui/`.
- **Files Affected:** `frontend/tailwind.config.ts`, `frontend/src/components/ui/*`, `frontend/src/index.css`.
- **Tests Required:** Vitest component unit tests; automated axe-core unit checks on every primitive.
- **Acceptance Criteria:** 100% keyboard navigable components; color contrast $\ge 4.5:1$ for normal text; visible focus rings.
- **Risks:** Focus ring clipping in custom containers. Mitigation: Explicit CSS outline offsets.
- **Approval Gate:** User review of component test logs and Storybook/showcase.

### Milestone 04: Database Engine, PostgreSQL Migrations & Seeding
- **Objective:** Deploy production-grade PostgreSQL 16 schema, Alembic migrations, and seed scripts against a real PostgreSQL 16 test container (decommissioning SQLite for integration).
- **Prerequisites:** Milestone 02.
- **Key Tasks:** Write Alembic migration scripts for `users`, `patients`, `assessments`, `consent_grants`, `audit_logs`, and `directory_providers`. Implement UUIDv7 generation. Create synthetic database seed script.
- **Deliverables:** `backend/alembic/versions/*`; migration test harness against PostgreSQL 16.
- **Files Affected:** `backend/alembic/*`, `backend/app/models/*`, `backend/tests/conftest.py`.
- **Tests Required:** Update `conftest.py` to spin up a PostgreSQL 16 container for integration tests; execute `alembic upgrade head` and `alembic downgrade base`.
- **Acceptance Criteria:** 15 existing baseline tests pass against real PostgreSQL 16; foreign key cascades verified.
- **Risks:** PostgreSQL version-specific extensions. Mitigation: Standardize on built-in `gen_random_uuid()` and native types.
- **Approval Gate:** User review of migration execution log against real PostgreSQL 16.

### Milestone 05: Backend Core Services & RFC 7807 Error Envelopes
- **Objective:** Establish the FastAPI application core, database session lifecycle, structured JSON logging with correlation IDs, and standardized RFC 7807 Problem Details error handling.
- **Prerequisites:** Milestone 04.
- **Key Tasks:** Global exception handlers for 422, 401, 403, 404, 500; CORS configuration; correlation `request_id` middleware; health check endpoints (`/live`, `/ready`).
- **Deliverables:** Core application in `backend/app/main.py` and `backend/app/core/*`.
- **Files Affected:** `backend/app/main.py`, `backend/app/core/logging.py`, `backend/app/core/errors.py`, `backend/tests/test_api_health.py`.
- **Tests Required:** Pytest tests verifying health probes and confirming RFC 7807 error envelopes on simulated exceptions.
- **Acceptance Criteria:** All errors return `{type, title, status, detail, instance, request_id}`; zero stack traces leaked in 500 responses.
- **Risks:** Middleware performance overhead. Mitigation: Async lightweight logging with structured JSON output.
- **Approval Gate:** User review of health check and error handling test logs.

### Milestone 06: Authentication, Sessions & RBAC
- **Objective:** Implement identity management, Argon2id password hashing, in-memory access JWTs (15 min), HttpOnly refresh cookies with Redis token-family rotation, and fail-closed Redis handling.
- **Prerequisites:** Milestone 05.
- **Key Tasks:** Endpoints `/api/v1/auth/register`, `/login`, `/refresh`, `/logout`. Role-based dependencies (`require_role(UserRole.PATIENT)`). Redis token family rotation; if Redis is down, fail closed.
- **Deliverables:** `backend/app/services/auth_service.py`, `backend/app/api/v1/routes/auth.py`.
- **Files Affected:** `backend/app/services/auth_service.py`, `backend/app/api/v1/routes/auth.py`, `backend/tests/test_auth.py`.
- **Tests Required:** Test Argon2id verify/hash; test access token expiration; test refresh token rotation and replay detection; test Redis fail-closed behavior.
- **Acceptance Criteria:** Attempted reuse of a rotated refresh token invalidates the entire token family immediately.
- **Risks:** Session lockout during transient Redis network jitter. Mitigation: Redis retry with exponential backoff before failing closed.
- **Approval Gate:** User review of authentication test logs and security test suite.

### Milestone 07: Frontend Core Shell, Routing & Auth State
- **Objective:** Construct the responsive application shell, client-side routing, protected route guards, and silent token refresh targeting WCAG 2.2 AA.
- **Prerequisites:** Milestone 03, Milestone 06.
- **Key Tasks:** React Router v6 layout with Header, Footer, and Emergency Banner; Zustand auth store; Axios/fetch interceptor for silent JWT refresh; accessible authentication (3.3.8 - copy/paste supported).
- **Deliverables:** Working SPA shell in `frontend/src/`.
- **Files Affected:** `frontend/src/App.tsx`, `frontend/src/routes/*`, `frontend/src/stores/authStore.ts`, `frontend/src/components/layout/*`.
- **Tests Required:** Vitest tests for route guards (redirect unauthenticated to `/login`); test silent token refresh on 401.
- **Acceptance Criteria:** Seamless silent token refresh; full keyboard navigation of shell; WCAG 2.2 focus visibility verified.
- **Risks:** Infinite refresh loop on invalid refresh cookie. Mitigation: Break loop and redirect to `/login` on refresh failure.
- **Approval Gate:** User review of frontend shell tests and visual layout demo.

### Milestone 08: Clinical Intake Wizard & Input Validation
- **Objective:** Implement the 14-biomarker multi-step clinical assessment intake wizard with instant unit conversion ($\text{mg/dL} \leftrightarrow \text{mmol/L}$) and physiological bounds enforcement.
- **Prerequisites:** Milestone 07.
- **Key Tasks:** Multi-step intake form; Zod schema validation; physiological bounds checks (BP 40–300, Chol 50–600); emergency red-flag triggers (resting BP $>180$ renders emergency hotline alert); redundant entry prevention (3.3.7).
- **Deliverables:** Intake wizard in `frontend/src/features/intake/`.
- **Files Affected:** `frontend/src/features/intake/*`, `frontend/src/lib/unitConverter.ts`, `frontend/tests/intake_wizard.test.tsx`.
- **Tests Required:** Vitest unit tests verifying unit conversion math to 4 decimal places; test emergency alert tripping on crisis inputs.
- **Acceptance Criteria:** Rejects biologically implausible inputs; emergency hotline banner appears instantly on severe symptoms; saves draft locally.
- **Risks:** Floating point rounding errors in unit conversions. Mitigation: Rounding helpers locked to standard clinical tolerances.
- **Approval Gate:** User review of intake wizard test logs and validation test cases.

### Milestone 09: ML Data Verification & Stratification
- **Objective:** Verify provenance of the UCI Cleveland dataset, audit target semantics (`num`), establish leakage-free preprocessing, and generate a reproducible stratified split.
- **Prerequisites:** Milestone 02.
- **Key Tasks:** Script `ml/pipelines/prepare_data.py` to ingest raw Cleveland data, verify 14 features, document 6 missing records (`ca`, `thal`), map binary target ($0$ vs $1$), and perform stratified 5-fold cross-validation split with fixed seed.
- **Deliverables:** `ml/pipelines/prepare_data.py`; versioned, hashed train/test splits (`train.parquet`, `test.parquet`).
- **Files Affected:** `ml/pipelines/prepare_data.py`, `ml/data/processed/*`, `ml/tests/test_data_preparation.py`.
- **Tests Required:** Assert zero index overlap between train and test splits; assert exact class distributions across folds.
- **Acceptance Criteria:** Pipeline is 100% deterministic given seed; target distribution verified (164 negative / 139 positive).
- **Risks:** Data leakage during feature scaling. Mitigation: Fit scalers exclusively on training folds within cross-validation loop.
- **Approval Gate:** User review of dataset verification report and split audit.

### Milestone 10: Task A Model Training & Probability Calibration
- **Objective:** Train, evaluate, and calibrate the Task A XGBoost 2.0 classifier for experimental dataset classification with strict calibration verification.
- **Prerequisites:** Milestone 09.
- **Key Tasks:** Hyperparameter tuning via nested CV; post-hoc calibration via Platt Scaling / Isotonic Regression; compute Brier score ($\le 0.12$) and Expected Calibration Error (ECE $\le 0.05$); generate reliability diagram; register model artifact with SHA-256 hash.
- **Deliverables:** Calibrated model artifact `model.joblib`; model evaluation report and reliability curve.
- **Files Affected:** `ml/pipelines/train_model.py`, `ml/pipelines/evaluate_model.py`, `ml/registry/*`.
- **Tests Required:** Automated test asserting test-set Brier score $\le 0.12$ and ECE $\le 0.05$; subgroup fairness evaluation across sex.
- **Acceptance Criteria:** Calibration verified; model output strictly categorized as an experimental dataset classifier; zero diagnostic claims.
- **Risks:** Overfitting on small sample ($N=303$). Mitigation: L1/L2 regularization (`reg_alpha`, `reg_lambda`) and shallow tree depth (max_depth $\le 3$).
- **Approval Gate:** User review of model calibration curves and evaluation metrics.

### Milestone 11: In-Process ML Model Serving Pipeline
- **Objective:** Integrate the calibrated Task A model into the FastAPI backend for synchronous in-process C++ inference with sub-20ms latency.
- **Prerequisites:** Milestone 05, Milestone 10.
- **Key Tasks:** Implement `InferenceService` loading calibrated model at application startup; normalize input feature vector; execute inference; persist prediction and non-diagnostic risk tier to `assessments` table.
- **Deliverables:** `backend/app/ml/inference_service.py`; endpoint `POST /api/v1/assessments`.
- **Files Affected:** `backend/app/ml/inference_service.py`, `backend/app/api/v1/routes/assessments.py`, `backend/tests/test_inference.py`.
- **Tests Required:** Benchmark inference execution under concurrent load; assert output probabilities stay bounded in $[0, 1]$; test PostgreSQL persistence.
- **Acceptance Criteria:** $p95$ inference latency $<20\text{ ms}$; zero memory leaks over 1,000 consecutive predictions; non-diagnostic disclaimer included in response.
- **Risks:** Thread safety of C-API model worker. Mitigation: Use dedicated worker threads or in-process inference locks.
- **Approval Gate:** User review of inference benchmark and API response payload.

### Milestone 12: TreeSHAP Local Explanation Engine
- **Objective:** Compute exact local feature attributions via TreeSHAP and render interactive waterfall attribution charts with explicit non-causal disclaimers.
- **Prerequisites:** Milestone 11, Milestone 08.
- **Key Tasks:** Integrate fast TreeSHAP explainer; persist SHAP values to `assessments.shap_values` JSONB; render Recharts waterfall chart in frontend showing top positive and negative risk contributors with accessible SVG labels.
- **Deliverables:** `backend/app/ml/shap_service.py`; frontend waterfall component in `frontend/src/features/assessment/`.
- **Files Affected:** `backend/app/ml/shap_service.py`, `frontend/src/features/assessment/ShapWaterfall.tsx`, `backend/tests/test_shap.py`.
- **Tests Required:** Verify efficiency axiom: $\sum \phi_i + \phi_0 = f(\mathbf{x})$ within $10^{-5}$ tolerance; verify contrast ratio on chart bars.
- **Acceptance Criteria:** Attributions satisfy mathematical axioms; UI explicitly notes that SHAP reflects statistical associations, not biological causation.
- **Risks:** TreeSHAP memory spikes. Mitigation: Pre-initialize explainer once at startup using background data summary.
- **Approval Gate:** User review of SHAP calculation logs and frontend waterfall depiction.

### Milestone 13: Constrained Counterfactual Engine
- **Objective:** Generate actionable, biologically constrained lifestyle modification scenarios using DiCE-ML or constrained gradient optimization, with immutable features strictly frozen.
- **Prerequisites:** Milestone 11, Milestone 08.
- **Key Tasks:** Implement counterfactual optimizer freezing Age, Sex, and clinical history; restrict perturbations to resting BP ($\ge 90$), cholesterol ($\ge 120$), and fasting blood sugar; render "What-If" scenario sliders with single-pointer click alternatives (WCAG 2.5.7).
- **Deliverables:** `backend/app/ml/counterfactual_service.py`; scenario simulator component in frontend.
- **Files Affected:** `backend/app/ml/counterfactual_service.py`, `frontend/src/features/assessment/CounterfactualSimulator.tsx`.
- **Tests Required:** Automated test asserting immutable features never change; target values stay within physiological floors; non-prescription disclaimer verified.
- **Acceptance Criteria:** Generated scenarios are biologically plausible and non-prescriptive; UI disclaims counterfactuals as exploratory models, not prescriptions.
- **Risks:** Counterfactual optimization non-convergence. Mitigation: Fallback to grid search across pre-computed actionable hyperplanes.
- **Approval Gate:** User review of counterfactual constraint test logs and simulator UI.

### Milestone 14: Clinical Assessment Results & PDF Dossier Export (Task B Excluded)
- **Objective:** Assemble the complete clinical assessment results view, mandatory non-diagnostic disclaimers, emergency hotline warnings, and cryptographically signed PDF summary export (with Task B completely excluded).
- **Prerequisites:** Milestone 12, Milestone 13.
- **Key Tasks:** Results dashboard layout; emergency indicator triggers; WeasyPrint / ReportLab PDF generation with SHA-256 digital seal; non-diagnostic statutory notices prominently displayed. Confirm zero Task B / 10-year risk calculators are included.
- **Deliverables:** Results feature in `frontend/src/features/assessment/`; `GET /api/v1/assessments/{id}/export-pdf` endpoint.
- **Files Affected:** `frontend/src/features/assessment/*`, `backend/app/services/export_service.py`, `backend/tests/test_export.py`.
- **Tests Required:** Verify PDF layout renders cleanly on 2-page format; assert presence of mandatory clinical disclaimers; test emergency warning trigger.
- **Acceptance Criteria:** Comprehensive, accessible results screen; PDF export generates with valid cryptographic hash; zero prospective 10-year risk claims.
- **Risks:** PDF styling inconsistencies across environments. Mitigation: Use headless HTML-to-PDF rendering with locked print CSS.
- **Approval Gate:** User review of sample exported PDF dossier and results screen layout.

### Milestone 15: Localized Healthcare Directory & Emergency Hotlines
- **Objective:** Deploy searchable, filterable directory of verified cardiac care providers and hospitals for US, IN, and UK, with emergency hotline quick-dial buttons (external commercial APIs disabled/mocked).
- **Prerequisites:** Milestone 05, Milestone 07.
- **Key Tasks:** Directory database tables; seed with 150+ verified academic medical centers and hospitals across US, IN, UK; implement city and specialty filtering; emergency hotline quick-dial buttons (911, 112, 999).
- **Deliverables:** Directory service in `backend/app/services/directory_service.py`; search UI in `frontend/src/features/directory/`.
- **Files Affected:** `backend/app/services/directory_service.py`, `backend/app/api/v1/routes/directory.py`, `frontend/src/features/directory/*`.
- **Tests Required:** Filter query unit tests; emergency phone link mobile tap tests; verify zero external unverified API calls.
- **Acceptance Criteria:** Users can filter providers by jurisdiction within 2 clicks; emergency contacts prominent.
- **Risks:** Outdated provider telephone numbers. Mitigation: Seed records restricted to verified major academic hospitals and official hotline numbers.
- **Approval Gate:** User review of directory listings and search functionality.

### Milestone 16: Clinician Portal & Consent Sharing Grants
- **Objective:** Enable secure, time-limited clinician access to patient assessments via 72-hour cryptographic tokens, with clinician review notes and patient revocation dashboard.
- **Prerequisites:** Milestone 06, Milestone 14.
- **Key Tasks:** Implement `ConsentService` generating 72-hour signed tokens; doctor assessment view; patient consent management dashboard with instant revocation.
- **Deliverables:** `backend/app/services/consent_service.py`; doctor portal view in `frontend/src/features/doctor/`.
- **Files Affected:** `backend/app/services/consent_service.py`, `backend/app/api/v1/routes/consents.py`, `frontend/src/features/doctor/*`.
- **Tests Required:** Security tests verifying expired or revoked consent tokens immediately return 403 Forbidden; test doctor note appending.
- **Acceptance Criteria:** Patient can revoke access with single click; audit trail logs all shared record accesses.
- **Risks:** Token leakage via shared URLs. Mitigation: Require doctor account authentication before consent grant redemption.
- **Approval Gate:** User review of consent sharing flow and security test logs.

### Milestone 17: Administrative Console & Immutable Audit Trail
- **Objective:** Provide system health monitoring, immutable security audit log viewer, and user account administration.
- **Prerequisites:** Milestone 06, Milestone 15.
- **Key Tasks:** Admin dashboard UI; paginated audit log search by correlation `request_id`, user, and timestamp; model registry inspection; user status toggle (active/suspended).
- **Deliverables:** Admin module in frontend and backend.
- **Files Affected:** `backend/app/api/v1/routes/admin.py`, `frontend/src/features/admin/*`, `backend/tests/test_admin.py`.
- **Tests Required:** Strict RBAC test: non-admin roles attempting access receive 403 Forbidden; assert audit logs cannot be modified or deleted via API.
- **Acceptance Criteria:** Admin can inspect all security-relevant events; audit table enforces append-only rules.
- **Risks:** Performance degradation on large audit log queries. Mitigation: B-tree indexing on `created_at` and `actor_id`.
- **Approval Gate:** User review of admin console and audit log verification tests.

### Milestone 18: Security Hardening, Penetration Testing & Anti-IDOR Verification
- **Objective:** Execute automated vulnerability scanning, comprehensive anti-IDOR verification, and Nginx security header hardening.
- **Prerequisites:** Milestone 16, Milestone 17.
- **Key Tasks:** Run Bandit static analysis; run `pip-audit` and `npm audit`; execute automated anti-IDOR test suite across all patient endpoints; tune Nginx Content Security Policy (CSP), HSTS, and rate limiting.
- **Deliverables:** Security hardening report; zero high/critical vulnerabilities in dependencies; hardened Nginx configuration.
- **Files Affected:** `infra/nginx/nginx.conf`, `backend/tests/test_security_audit.py`.
- **Tests Required:** Automated IDOR test suite passing with 100% rejection of cross-tenant requests; OWASP ZAP baseline scan.
- **Acceptance Criteria:** Zero high/critical findings; anti-IDOR verified across 100% of patient routes.
- **Risks:** Overly restrictive CSP breaking chart rendering. Mitigation: Strict whitelist of self-hosted assets and inline SVGs.
- **Approval Gate:** User review of security test reports and vulnerability scan logs.

### Milestone 19: Accessibility (WCAG 2.2 AA Conformance Testing) & Performance Validation
- **Objective:** Execute comprehensive accessibility audits targeting WCAG 2.2 AA and validate sub-100ms API response times under simulated load.
- **Prerequisites:** Milestone 18.
- **Key Tasks:** Run automated axe-core audits across all frontend routes; execute full keyboard-only traversal; test screen reader compatibility (NVDA / VoiceOver); run K6 / Locust load testing on API endpoints.
- **Deliverables:** WCAG 2.2 AA accessibility scorecard; API performance benchmark report.
- **Files Affected:** `frontend/tests/a11y.spec.ts`, `infra/scripts/load_test.js`.
- **Tests Required:** Zero critical or serious axe-core violations; $p95$ API latency $<100\text{ ms}$ under 50 concurrent virtual users.
- **Acceptance Criteria:** Accessibility conformance verified; performance criteria met.
- **Risks:** Chart SVG accessibility gaps. Mitigation: Provide accessible HTML table alternatives for all charts.
- **Approval Gate:** User review of accessibility and performance reports.

### Milestone 20: Staging Deployment & Final Acceptance Testing (Synthetic UAT)
- **Objective:** Deploy to isolated staging VPS environment behind Nginx SSL, execute end-to-end synthetic user journeys, verify disaster recovery backup restore, and obtain final stakeholder acceptance.
- **Prerequisites:** Milestone 19.
- **Key Tasks:** Deploy multi-container stack to staging VPS via Docker Compose; execute full Playwright E2E test suite using synthetic patient personas; execute `restore_encrypted.sh` to verify AES-256-GCM backup recovery; conduct final UAT demonstration. Confirm zero real patient data is used.
- **Deliverables:** Live staging deployment; automated E2E test report; disaster recovery verification log; final UAT sign-off report.
- **Files Affected:** `infra/docker-compose.yml`, `infra/scripts/*`, `tests/e2e/*`.
- **Tests Required:** 100% pass rate on full Playwright E2E suite; successful database restore from encrypted backup.
- **Acceptance Criteria:** Complete system operating cleanly in staging; disaster recovery verified; formal stakeholder sign-off obtained.
- **Risks:** Staging environment configuration drift from local dev. Mitigation: Identical Docker Compose base with environment-variable overrides.
- **Approval Gate:** Final stakeholder review and authorization for milestone completion.
