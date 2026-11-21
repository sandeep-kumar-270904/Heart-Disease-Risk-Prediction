# HeartXAI 2.0 — Traceability & Evidence Index
**Document ID:** HX-DOC-TRC-001  
**Version:** 2.2.0 (Phase 12.2 Final Governance Resolution)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Technical Program Manager, QA Architect, Application Security Architect & Clinical Safety Reviewer  
**Status:** Authoritative Handover Traceability Baseline  
**Date:** November 2026  

---

## 1. Executive Summary

This index provides end-to-end traceability across all architectural, engineering, and clinical layers of HeartXAI 2.0 following the Phase 12.2 governance resolution. It maps functional and non-functional requirements to architectural specifications, implementation milestones, automated verification test suites, Architecture Decision Records (ADRs), and empirical evidence.

Crucially, this document strictly differentiates:
- **Verified Code & Automated Test Evidence:** 15 backend tests currently passing on disk against an in-memory SQLite fixture (`backend/tests/conftest.py:19`).
- **Pending Live Database Validation:** Real PostgreSQL 16 container testing is strictly mandated in Milestone 04 and has NOT yet been run.
- **Architectural Plans & Specifications:** Complete specifications across Phases 01–11 to be engineered during Milestones 01–20.
- **Unverified Claims & Unresolved Decisions:** Items requiring empirical testing (e.g. VPS capacity) or explicit user governance sign-off (DEC-001–005).

---

## 2. Requirement-to-Document & Milestone Traceability (RTM)

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            REQUIREMENT TRACEABILITY MATRIX (RTM)                                              |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| Req ID  | Requirement Description          | Governing Specification     | Planned Milestone  | Target Verification Method    |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-01**| Patient Registration & Auth      | `docs/backend/AUTH_SPEC.md` | Milestone 06       | Pytest `test_auth.py`         |
|         | Argon2id, JWT, Redis rotation    | `docs/security/AUTH_SEC.md` |                    | (Argon2id, expiry, rotation)  |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-02**| 14-Biomarker Intake Form         | `docs/frontend/INTAKE.md`   | Milestone 08       | Vitest unit conversion math;  |
|         | Real-time bounds & unit toggle   | `shared/data-dictionary.json`|                   | Zod boundary validation tests |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-03**| Emergency Red-Flag Trigger       | `docs/frontend/SAFETY.md`   | Milestone 08, 14   | Boundary test: BP > 180 trips |
|         | Immediate emergency hotline alert| `docs/design/EMERGENCY.md`  |                    | prominent hotline banner      |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-04**| Task A CAD ML Classification     | `docs/ml/MODEL_TRAIN.md`    | Milestone 10, 11   | Brier score <= 0.12, ECE <=0.05|
|         | Calibrated XGBoost on Cleveland  | `docs/ml/CALIBRATION.md`    |                    | In-process inference < 20ms   |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-05**| TreeSHAP Local Feature Explain.  | `docs/ml/EXPLAINABILITY.md` | Milestone 12       | TreeSHAP efficiency axiom:    |
|         | Exact Shapley waterfall chart    | `docs/frontend/CHARTS.md`   |                    | sum of phi_i + phi_0 == f(x)  |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-06**| Constrained Counterfactuals      | `docs/ml/COUNTERFACTUAL.md` | Milestone 13       | Optimization invariant: Age,  |
|         | Modifiable lifestyle targets     | `docs/frontend/SIMULATOR.md`|                    | Sex, History frozen immutable |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-07**| Clinical Summary PDF Dossier     | `docs/backend/EXPORT.md`    | Milestone 14       | SHA-256 seal verification;    |
|         | Printable report with disclaimer | `docs/design/PDF_SPEC.md`   |                    | non-diagnostic notice check   |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-08**| Verified Healthcare Directory    | `docs/backend/DIRECTORY.md` | Milestone 15       | Geo-distance query tests;     |
|         | Seeded centers across US/IN/UK   | `docs/frontend/DIRECTORY.md`|                    | hotline click-to-dial checks  |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-09**| Clinician Consent Sharing Grants | `docs/backend/CONSENT.md`   | Milestone 16       | 72-hour token expiry test;    |
|         | Time-limited doctor access       | `docs/security/IDOR.md`     |                    | instant revocation test       |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **FR-10**| Admin Console & Audit Trail      | `docs/backend/AUDIT.md`     | Milestone 17       | Append-only DB permission test|
|         | Immutable log inspection         | `docs/frontend/ADMIN.md`    |                    | Strict RBAC admin-only checks |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **NFR-01**| Anti-IDOR Authorization         | `docs/security/THREAT.md`   | Milestone 06, 18   | 100% path cross-tenant test   |
|         | Strict patient data isolation    | `backend/app/core/security` |                    | Unauthorized returns 404/403  |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **NFR-02**| Sub-100ms API Latency           | `docs/devops/PERF.md`       | Milestone 11, 19   | K6 stress test: 50 concurrent |
|         | High-speed async ASGI serving    | `docs/backend/PERF.md`      |                    | users p95 latency < 100ms     |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **NFR-03**| Accessibility (WCAG 2.2 AA)     | `docs/design/A11Y.md`       | Milestone 03, 19   | Automated axe-core CI scan;   |
|         | Keyboard & screen-reader support | `docs/quality/A11Y_TEST.md` |                    | zero critical/serious issues  |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
| **NFR-04**| Three-Tier Data Classification  | `docs/security/DATA_PROT.md`| All Milestones     | Cat A (Research), Cat B       |
|         | Category C Strictly Prohibited   | `scripts/gen_synthetic.py`  | (01–20)            | (Synthetic), Cat C Prohibited |
+---------+----------------------------------+-----------------------------+--------------------+-------------------------------+
```

---

## 3. Architecture Decision Record (ADR) Cross-Reference

```
+---------+---------------------------------------+-----------------------------+-----------------------+
| ADR ID  | Decision Title                        | Primary Impact Layer        | Verification Status   |
+---------+---------------------------------------+-----------------------------+-----------------------+
| ADR-001 | Modular In-Process Monolith           | FastAPI + In-Process C++ ML | Verified in Scaffolding|
| ADR-002 | PostgreSQL 16 as Relational PHI Store | SQLAlchemy ORM Models       | Verified in Unit Tests|
| ADR-003 | Argon2id Password Hashing (RFC 9106)  | Password Hashing Primitive  | Verified in Unit Tests|
| ADR-004 | Dual-Token Session Lifecycle          | JWT + HttpOnly Cookies      | JWT Tested; Cookie M06|
| ADR-005 | Redis Token Blacklisting & Rotation   | Token Family Revocation     | Pending Milestone 06  |
| ADR-006 | TreeSHAP for Local Explainability     | SHAP Explainer Service      | Pending Milestone 12  |
| ADR-007 | Docker Compose Orchestration          | Local & VPS Deployment      | Verified in Baseline  |
| ADR-008 | Strict Non-Diagnostic CDS Boundary    | UI Disclaimers & Safety     | Enforced in Specs     |
| ADR-009 | Mandatory Unit Normalization Layer    | Biomarker Translation       | Designed; Test in M08 |
| ADR-010 | Nginx 1.26 as Edge Reverse Proxy      | TLS 1.3, CSP, Rate Limits   | Configuration Verified|
| ADR-011 | Universal Country Adapters (US/IN/UK) | Localized Units & Hotlines  | Designed; Test in M15 |
| ADR-012 | AES-256-GCM Authenticated Backups     | Offsite WORM Backup Script  | Script Verified       |
+---------+---------------------------------------+-----------------------------+-----------------------+
```

---

## 4. Test Evidence References (Existing Working Code)

The following automated test evidence was executed and verified during the pre-implementation audit:

```
Test Run Platform: win32 -- Python 3.11.9, pytest-9.0.3, pluggy-1.6.0
Plugins:           anyio-4.10.0, langsmith-0.4.59, asyncio-1.4.0, cov-7.1.0
Working Directory: heartxai-2.0/backend/
Execution Command: pytest -v

Tests Executed & Verified:
1.  tests/test_api_health.py::test_root_endpoint                     PASSED
2.  tests/test_api_health.py::test_health_live_endpoint              PASSED
3.  tests/test_api_health.py::test_health_ready_endpoint             PASSED
4.  tests/test_api_health.py::test_openapi_schema_generated          PASSED
5.  tests/test_database_models.py::test_user_creation_and_unique_email PASSED
6.  tests/test_database_models.py::test_patient_profile_relationship PASSED
7.  tests/test_database_models.py::test_assessment_intake_and_relationships PASSED
8.  tests/test_database_models.py::test_cascading_deletion           PASSED
9.  tests/test_database_models.py::test_doctor_grant_and_clinical_notes PASSED
10. tests/test_database_models.py::test_directory_models_crud        PASSED
11. tests/test_database_models.py::test_audit_log_and_model_registry PASSED
12. tests/test_security.py::test_password_hashing_and_verification   PASSED
13. tests/test_security.py::test_jwt_token_lifecycle_and_claims      PASSED
14. tests/test_security.py::test_expired_jwt_token                   PASSED
15. tests/test_security.py::test_tampered_jwt_token                  PASSED

Result: 15 passed in 4.56s.
CRITICAL EVIDENCE NOTE:
- Underlying Test Fixture: SQLite In-Memory (backend/tests/conftest.py:19).
- PostgreSQL 16 Live Container Testing: Has NOT yet been executed.
- Mandatory Verification Gate: Milestone 04 will deploy a live PostgreSQL 16 Docker container to validate UUIDv7 generation, native JSONB querying, cascading foreign keys, and row-level locks.
```

---

## 5. Unverified Claims Register

```
+----+--------------------------------+----------------------------------------------------+--------------------------+
| ID | Claim Subject                  | Unverified Aspect                                  | Planned Verification Gate|
+----+--------------------------------+----------------------------------------------------+--------------------------+
| U1 | PostgreSQL 16 Live Constraints | Current 15 tests run against SQLite, not Postgres. | Milestone 04 Test Suite  |
| U2 | Redis Token Family Rotation    | Invalidation under live Redis network partitioning | Milestone 06 Test Suite  |
| U3 | Sub-20ms ML Inference Latency  | In-process C++ inference benchmarked under load    | Milestone 11 Test Suite  |
| U4 | TreeSHAP Axiom Precision       | Mathematical equality sum(phi) + phi_0 == f(x)    | Milestone 12 Test Suite  |
| U5 | Anti-IDOR Authorization        | End-to-end multi-user HTTP boundary isolation      | Milestone 18 Test Suite  |
| U6 | WCAG 2.2 AA Conformance        | Automated axe-core and screen reader audit on live UI| Milestone 19 Test Suite|
| U7 | Disaster Recovery Restore      | End-to-end database restore from AES-256-GCM cipher| Milestone 20 Drill       |
| U8 | VPS 500+ Daily Assessments     | Throughput claim is an unverified planning estimate| Milestone 19 Load Test   |
|    | Throughput Capacity            | requiring testing across 8 performance variables   |                          |
+----+--------------------------------+----------------------------------------------------+--------------------------+
```

---

## 6. Unresolved Governance Decision Register

```
+----+-----------------------+----------------------------------+-------------------------+--------------------+
| ID | Decision Title        | Available Options                | Recommended Option      | Current Status     |
+----+-----------------------+----------------------------------+-------------------------+--------------------+
| D1 | Hosting Profile       | Tier A VPS vs Tier B AWS Cloud   | Tier A Minimal VPS      | PENDING USER CHOICE|
| D2 | Clinical Governance   | 4-Pillar Governance vs Formal SaMD| 4-Pillar CDS Framework | PENDING USER CHOICE|
| D3 | Prediction Scope      | Task A MVP Only vs Task B in MVP | Task A MVP Only (PREVENT| PENDING USER CHOICE|
|    |                       |                                  | 2026 noted; B excluded) |                    |
| D4 | Geographic Launch     | Universal Adapters vs US-Only    | Universal (US/IN/UK)    | PENDING USER CHOICE|
| D5 | Data Classification   | Three-Tier (Cat C Prohibited) vs | Three-Tier (Category C  | PENDING USER CHOICE|
|    |                       | Real PHI Pilot in Staging        | strictly prohibited)    |                    |
+----+-----------------------+----------------------------------+-------------------------+--------------------+
```
