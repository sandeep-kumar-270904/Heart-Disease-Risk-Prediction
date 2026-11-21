# HeartXAI 2.0 — Master Implementation Roadmap (20 Milestones)
**Document ID:** HX-PR-011  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal Software Architect, Staff Engineer & Technical Program Manager  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

This roadmap defines the authoritative 20-milestone sequence for engineering, testing, hardening, and delivering HeartXAI 2.0. Each milestone is designed as an independently verifiable, atomic increment of software functionality.

In accordance with strict project execution rules, **Antigravity must execute exactly one approved milestone at a time**, verify all automated tests, and receive user sign-off before proceeding to subsequent milestones.

---

## 2. Master Implementation Milestone Catalog

```
+---------------------------------------------------------------------------------------------------------+
|                                    20-MILESTONE MASTER ROADMAP SUMMARY                                  |
+----+--------------------------------------------+-------------------------------------+-----------------+
| ID | Milestone Title                            | Primary Technology & Focus          | Prerequisite    |
+----+--------------------------------------------+-------------------------------------+-----------------+
| 01 | Repository & Dev Environment Foundation    | Git, Docker Compose, CI/CD Actions  | Approved Audit  |
| 02 | Core Scaffolding & Canonical Types         | Pydantic v2, TypeScript 5.4, Linters| M01             |
| 03 | Design System & UI Component Library       | Tailwind CSS, Radix UI Primitives   | M02             |
| 04 | Database Engine & Schema Migrations        | PostgreSQL 16, SQLAlchemy, Alembic  | M02             |
| 05 | Backend Core Services & API Framework      | FastAPI, Error Middleware, CORS     | M04             |
| 06 | Authentication, Sessions & RBAC            | Argon2id, JWT, Redis Token Rotation | M05             |
| 07 | Frontend Shell, Routing & Auth State       | React 18, React Router v6, Zustand  | M03, M06        |
| 08 | Clinical Intake Wizard & Input Validation  | TanStack Form, Zod, Unit Converter  | M07             |
| 09 | ML Data Preparation & Stratification       | UCI Cleveland, Scikit-learn Pipeline| M02             |
| 10 | Model Training & Probability Calibration   | XGBoost 2.0, Platt/Isotonic, Brier  | M09             |
| 11 | In-Process ML Model Serving Pipeline       | In-Process C++ ML Worker, FastAPI   | M05, M10        |
| 12 | TreeSHAP Local Explanation Engine          | SHAP 0.45, Recharts Waterfall View  | M11, M08        |
| 13 | Constrained Counterfactual Engine          | DiCE-ML, Actionability Optimizer    | M11, M08        |
| 14 | Clinical Results & PDF Dossier Export      | PDF Generation, Non-Diagnostic View | M12, M13        |
| 15 | Verified Doctor & Hospital Directory       | Geo-Filtering, Emergency Contacts   | M05, M07        |
| 16 | Clinician Portal & Consent Sharing Grants  | 72-Hour Access Tokens, Doctor Notes | M06, M14        |
| 17 | Administrative Console & Audit Trail       | User Management, Audit Log Viewer   | M06, M15        |
| 18 | Security Hardening & Penetration Testing   | Bandit, Anti-IDOR, OWASP ZAP        | M16, M17        |
| 19 | Accessibility (WCAG 2.1 AA) & Performance  | axe-core, Lighthouse, K6 Stress Test| M18             |
| 20 | Staging Deployment & Final Acceptance (UAT)| Nginx SSL, Blue/Green, UAT Sign-off | M19             |
+----+--------------------------------------------+-------------------------------------+-----------------+
```

---

## 3. Detailed Milestone Specifications (Milestones 01 – 20)

### Milestone 01: Repository & Development Environment Foundation
- **Objective:** Establish reproducible, containerized local and CI development environments.
- **Scope:** Root configuration, Docker Compose setup for local dev, pre-commit hooks, GitHub Actions CI workflow.
- **Prerequisites:** User approval of Phase 12 audit.
- **Key Tasks:** Configure `.editorconfig`, `.gitignore`, `docker-compose.yml` (PostgreSQL 16, Redis 7.2), GitHub Actions lint/test workflow.
- **Expected Deliverables:** Functional local dev containers; automated CI pipeline running on pull requests.
- **Test Requirements:** Automated CI job passes on empty baseline commit.
- **Acceptance Criteria:** `docker compose up` starts PostgreSQL 16 and Redis cleanly with health checks reporting `healthy`.

### Milestone 02: Core Scaffolding & Canonical Types
- **Objective:** Synchronize frontend and backend type definitions from the canonical data dictionary.
- **Scope:** Python Pydantic v2 models, TypeScript interfaces, Ruff and ESLint configurations.
- **Prerequisites:** Milestone 01.
- **Key Tasks:** Author `shared/types`, Pydantic schemas for 13 biomarkers, TypeScript equivalents, configure strict linting.
- **Expected Deliverables:** Synchronized schema repository; zero type errors across Python and TypeScript.
- **Test Requirements:** `mypy --strict` and `tsc --noEmit` pass with zero warnings.
- **Acceptance Criteria:** Complete parity between Pydantic `AssessmentInput` and TypeScript `AssessmentInputPayload`.

### Milestone 03: Design System & Shared UI Component Library
- **Objective:** Implement the approved design system tokens, typography, and accessible UI primitives.
- **Scope:** Tailwind CSS configuration, Radix UI accessible primitives, high-stress visual hierarchy.
- **Prerequisites:** Milestone 02.
- **Key Tasks:** Button, Input, Select, Modal, Alert, Badge, Card, Tooltip components with WCAG 2.1 AA contrast.
- **Expected Deliverables:** Component library in `frontend/src/components/ui/`; Storybook or component showcase.
- **Test Requirements:** Vitest component unit tests; axe-core accessibility checks on all primitives.
- **Acceptance Criteria:** 100% keyboard navigable primitives; color contrast $\ge 4.5:1$ for normal text.

### Milestone 04: Database Engine & Schema Migrations
- **Objective:** Deploy production-grade PostgreSQL 16 schema, Alembic migrations, and seed scripts.
- **Scope:** Relational tables: `users`, `patients`, `assessments`, `consent_grants`, `audit_logs`, `directory_providers`.
- **Prerequisites:** Milestone 02.
- **Key Tasks:** Alembic migration scripts, SQLAlchemy 2.0 async models, UUIDv7 generators, index creation.
- **Expected Deliverables:** `alembic/versions/` migration scripts; database seed script for country configurations.
- **Test Requirements:** 15 existing backend tests pass against real PostgreSQL 16 container; migration rollback test passes.
- **Acceptance Criteria:** `alembic upgrade head` and `alembic downgrade base` execute without errors.

### Milestone 05: Backend Core Services & API Framework
- **Objective:** Build robust FastAPI routing, RFC 7807 error envelopes, CORS, and request logging.
- **Scope:** Application lifespan events, database session middleware, structured JSON logging with correlation IDs.
- **Prerequisites:** Milestone 04.
- **Key Tasks:** Centralized exception handlers, standardized response envelopes, health check probes (`/live`, `/ready`).
- **Expected Deliverables:** Core FastAPI app in `backend/app/main.py` with modular router registration.
- **Test Requirements:** Pytest API health checks; test error handler returns RFC 7807 formatted JSON on unhandled exceptions.
- **Acceptance Criteria:** Standardized error response on all 4xx/5xx responses; request IDs logged across all requests.

### Milestone 06: Authentication, Sessions & RBAC
- **Objective:** Implement production-grade identity, password security, and session management.
- **Scope:** Argon2id hashing, short-lived JWTs (15 min), HttpOnly refresh cookies, Redis rotation, RBAC guards.
- **Prerequisites:** Milestone 05.
- **Key Tasks:** `/api/v1/auth/register`, `/login`, `/refresh`, `/logout`, role-based dependency injectors (`require_role`).
- **Expected Deliverables:** Authentication service in `backend/app/services/auth.py`.
- **Test Requirements:** Unit tests for Argon2id verify/hash; integration tests for token expiration and Redis blacklisting.
- **Acceptance Criteria:** Replay attack on refresh token triggers instant invalidation of token family.

### Milestone 07: Frontend Core Shell, Routing & Auth State
- **Objective:** Construct responsive frontend navigation shell, protected route guards, and session persistence.
- **Scope:** React Router v6 layout, TanStack Query client, Zustand auth store, automatic silent token refresh.
- **Prerequisites:** Milestone 03, Milestone 06.
- **Key Tasks:** App layout, header, footer, emergency banner bar, protected route wrapper, Axios/fetch interceptor.
- **Expected Deliverables:** Functional single-page application shell in `frontend/src/`.
- **Test Requirements:** Vitest routing tests; mock auth state transitions (logged out -> logging in -> authenticated).
- **Acceptance Criteria:** Unauthenticated access to `/dashboard` redirects to `/login`; expired token silently refreshes.

### Milestone 08: Clinical Intake Wizard & Input Validation
- **Objective:** Deliver the 14-feature multi-step clinical assessment intake form.
- **Scope:** Multi-step wizard, instant unit conversion ($\text{mg/dL} \leftrightarrow \text{mmol/L}$), physiological plausibility validation.
- **Prerequisites:** Milestone 07.
- **Key Tasks:** Multi-step form with progress indicator; real-time validation via Zod; unit toggle buttons.
- **Expected Deliverables:** Intake wizard components in `frontend/src/features/intake/`.
- **Test Requirements:** Unit tests for biomarker bounds; test unit conversion math; accessibility keyboard trap testing.
- **Acceptance Criteria:** Form rejects physiologically impossible inputs (e.g., BP $<40$ or $>300$); saves draft state locally.

### Milestone 09: ML Data Preparation & Stratification
- **Objective:** Establish reproducible, leakage-free data preparation pipeline for the UCI Cleveland dataset.
- **Scope:** Dataset ingestion, missing value imputation, stratified train/test split (80/20), feature scaling.
- **Prerequisites:** Milestone 02.
- **Key Tasks:** Automated data cleaning script; stratified 5-fold cross-validation split generator; artifact hashing.
- **Expected Deliverables:** `ml/pipelines/prepare_data.py`; versioned CSV/Parquet artifacts with SHA-256 signatures.
- **Test Requirements:** Pytest checks verifying zero overlap between train and test indices; schema validation.
- **Acceptance Criteria:** Data preparation pipeline is 100% deterministic given a fixed random seed.

### Milestone 10: Model Training & Probability Calibration
- **Objective:** Train, tune, and calibrate the primary Task A gradient boosted decision tree model.
- **Scope:** XGBoost 2.0 hyperparameter optimization, Platt scaling / Isotonic regression calibration, Brier score validation.
- **Prerequisites:** Milestone 09.
- **Key Tasks:** 5-fold nested CV training; calibration curves generation; compute Brier score and ECE.
- **Expected Deliverables:** Trained, calibrated model artifact (`model.joblib`); model card and evaluation metrics report.
- **Test Requirements:** Automated test asserting test set Brier score $\le 0.12$ and ECE $\le 0.05$; ROC-AUC $\ge 0.85$.
- **Acceptance Criteria:** Calibration curve demonstrates monotonic, close alignment to ideal diagonal.

### Milestone 11: In-Process ML Model Serving Pipeline
- **Objective:** Integrate the calibrated model into the FastAPI application for zero-network-overhead inference.
- **Scope:** In-process C++ inference execution, feature preprocessing pipeline, prediction persistence to PostgreSQL.
- **Prerequisites:** Milestone 05, Milestone 10.
- **Key Tasks:** `InferenceService` loading model at app startup; synchronous prediction execution; persist result to `assessments`.
- **Expected Deliverables:** `backend/app/services/inference.py`; endpoint `POST /api/v1/assessments`.
- **Test Requirements:** Benchmark test verifying inference latency $<20\text{ ms}$; integration test verifying database persistence.
- **Acceptance Criteria:** Concurrent load of 50 requests/sec completes with $p99 \le 50\text{ ms}$ and zero memory leaks.

### Milestone 12: TreeSHAP Local Explanation Engine
- **Objective:** Generate exact local feature attributions for individual assessment results.
- **Scope:** Fast TreeSHAP computation, waterfall chart data transformation, localized plain-language explanation generation.
- **Prerequisites:** Milestone 11, Milestone 08.
- **Key Tasks:** TreeSHAP explainer integration; persist SHAP values to `assessments.shap_values` JSONB; frontend waterfall view.
- **Expected Deliverables:** SHAP calculation service; Recharts-based interactive waterfall component in frontend.
- **Test Requirements:** Mathematical invariant test: $\sum \phi_i + \phi_0 = f(\mathbf{x})$; visual contrast check on chart bars.
- **Acceptance Criteria:** User sees top 3 risk-increasing and top 3 risk-decreasing factors with plain-language context.

### Milestone 13: Constrained Counterfactual Engine
- **Objective:** Provide actionable, biologically realistic lifestyle modification scenarios.
- **Scope:** Optimization algorithm constrained to modifiable factors (BP, cholesterol, glucose), immutable feature freezing.
- **Prerequisites:** Milestone 11, Milestone 08.
- **Key Tasks:** DiCE-ML or custom gradient descent constrained optimizer; generate 2–3 actionable target scenarios.
- **Expected Deliverables:** Counterfactual service; interactive "What-If" scenario simulator slider component.
- **Test Requirements:** Automated tests asserting age/sex/history features never change; target values stay within physiological floors.
- **Acceptance Criteria:** Counterfactual scenario successfully shifts predicted risk from Elevated to Moderate/Low.

### Milestone 14: Clinical Results & PDF Dossier Export
- **Objective:** Assemble comprehensive clinical results view, statutory disclaimers, and physician summary export.
- **Scope:** Complete assessment summary screen, emergency hotline indicators, cryptographic PDF generation.
- **Prerequisites:** Milestone 12, Milestone 13.
- **Key Tasks:** Results dashboard layout; emergency indicator triggers; WeasyPrint / ReportLab PDF generation with SHA-256 seal.
- **Expected Deliverables:** Assessment results feature in frontend; `GET /api/v1/assessments/{id}/export-pdf` endpoint.
- **Test Requirements:** PDF layout tests; verify mandatory disclaimer presence on exported document.
- **Acceptance Criteria:** Generated PDF renders cleanly on single 2-page clinical layout with clickable doctor contact info.

### Milestone 15: Verified Doctor & Hospital Directory
- **Objective:** Provide localized, searchable directory of verified cardiac care providers and hospitals.
- **Scope:** Geospatial / city-based filtering, verified credential badges, emergency hotline quick-dial buttons.
- **Prerequisites:** Milestone 05, Milestone 07.
- **Key Tasks:** Directory database tables; seed data for US, IN, and UK launch hubs; search and filter UI.
- **Expected Deliverables:** Directory service and frontend directory search page.
- **Test Requirements:** Filter query unit tests; emergency phone link mobile tap tests.
- **Acceptance Criteria:** Users can filter providers by country, city, and accepted insurance/payment within 2 clicks.

### Milestone 16: Clinician Portal & Consent Sharing Grants
- **Objective:** Enable secure, time-limited doctor access to patient assessments via cryptographic grants.
- **Scope:** 72-hour consent tokens, doctor review notes, patient revocation dashboard.
- **Prerequisites:** Milestone 06, Milestone 14.
- **Key Tasks:** Consent token generation service; doctor portal view; patient consent management interface.
- **Expected Deliverables:** `ConsentService`; doctor assessment view UI; audit logging for all shared views.
- **Test Requirements:** Security tests verifying expired or revoked tokens immediately return 403 Forbidden.
- **Acceptance Criteria:** Patient can revoke access instantly; doctor sees read-only assessment with ability to append clinical notes.

### Milestone 17: Administrative Console & Audit Trail
- **Objective:** Provide system monitoring, immutable security audit log viewer, and user administration.
- **Scope:** Admin-only routes, paginated audit log search, system health metrics, model version tracking.
- **Prerequisites:** Milestone 06, Milestone 15.
- **Key Tasks:** Admin dashboard UI; audit log query endpoints; user status toggle (active/suspended).
- **Expected Deliverables:** Administrative module in frontend and backend.
- **Test Requirements:** Strict RBAC test: non-admin roles attempting access receive 403 Forbidden.
- **Acceptance Criteria:** Admin can inspect all security-relevant events with correlation ID and IP tracing.

### Milestone 18: Security Hardening & Penetration Testing
- **Objective:** Execute automated vulnerability scanning, anti-IDOR verification, and security hardening.
- **Scope:** Dependency vulnerability auditing, static security analysis (Bandit), OWASP ZAP baseline scan, CSP tuning.
- **Prerequisites:** Milestone 16, Milestone 17.
- **Key Tasks:** Remediate flagged dependencies; verify zero IDOR across all endpoints; tune Nginx security headers.
- **Expected Deliverables:** Security audit sign-off report; zero high/critical vulnerabilities in CI scans.
- **Test Requirements:** Automated IDOR test suite passing; OWASP ZAP scan reports zero high-risk findings.
- **Acceptance Criteria:** Complete security sign-off with all security controls verified.

### Milestone 19: Accessibility (WCAG 2.1 AA) & Performance Validation
- **Objective:** Ensure universal accessibility compliance, cross-browser compatibility, and sub-100ms response times.
- **Scope:** Full keyboard navigation, screen reader testing, axe-core automated audit, Lighthouse performance optimization.
- **Prerequisites:** Milestone 18.
- **Key Tasks:** Fix any accessibility contrast or focus issues; optimize Vite bundle sizes; load test API with Locust/K6.
- **Expected Deliverables:** Accessibility compliance scorecard; performance benchmark report.
- **Test Requirements:** Lighthouse Accessibility score $\ge 95$; API response time $p95 < 100\text{ ms}$ under 100 concurrent users.
- **Acceptance Criteria:** Zero critical/serious axe-core violations across all pages; WCAG 2.1 AA certified.

### Milestone 20: Staging Deployment & Final Acceptance (UAT)
- **Objective:** Deploy to isolated staging environment, execute end-to-end user journeys, and obtain final sign-off.
- **Scope:** Containerized deployment behind Nginx SSL, automated database migrations, user acceptance testing (UAT).
- **Prerequisites:** Milestone 19.
- **Key Tasks:** Blue/green deployment execution; execute complete Playwright E2E suite against live staging; clinical UAT review.
- **Expected Deliverables:** Live staging deployment; final UAT sign-off documentation.
- **Test Requirements:** 100% pass rate on full Playwright E2E suite; disaster recovery backup/restore test passes.
- **Acceptance Criteria:** Formal stakeholder and clinical advisory acceptance; system ready for production traffic.
