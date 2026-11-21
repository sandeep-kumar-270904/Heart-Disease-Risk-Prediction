# HeartXAI 2.0 — Testing Readiness Audit
**Document ID:** HX-PR-008  
**Version:** 2.2.0 (Phase 12.2 Revision)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Principal QA Architect & Healthcare Reliability Lead  
**Status:** Risk-Based Quality Strategy Approved — Execution Pending Implementation  
**Date:** November 2026  

---

## 1. Executive Summary

In healthcare software, arbitrary percentage distributions (such as 65% unit / 25% integration / 10% E2E) do not guarantee software safety. A system can achieve 90% unit test coverage while remaining vulnerable to cross-patient data leaks, mathematical calculation errors, or database dialect failures.

In accordance with Phase 12.2 requirements, HeartXAI 2.0 decommissions rigid testing pyramid percentages and institutes an **authoritative, 10-Tier Risk-Based Testing Strategy**. Testing effort is distributed based on clinical risk, security exposure, and data integrity, using strictly **Category B synthetic application data**.

---

## 2. The 10-Tier Risk-Based Testing Strategy

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            RISK-BASED TESTING PRIORITY MATRIX                                                 |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| Tier | Risk Dimension              | Severity | Verification Scope & Test Harness     | Mandatory Quality Requirement         |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **01**| **Patient Data Isolation    | CRITICAL | Automated anti-IDOR test suite        | 100% path coverage. Zero cross-tenant |
|      | & Anti-IDOR Security**      |          | (Pytest + TestClient).                | access permitted. Return 404 on leak. |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **02**| **Healthcare Safety &       | CRITICAL | Physiological biomarker bounds checks | 100% boundary value test coverage.    |
|      | Emergency Triggers**        |          | and emergency alert trigger tests.    | BP > 180 trips emergency banner.      |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **03**| **Authentication & Session  | CRITICAL | Argon2id verification, JWT expiry,    | 100% test coverage. Replayed token    |
|      | Integrity**                 |          | refresh rotation, Redis fail-closed.  | revokes token family immediately.     |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **04**| **Database Integrity & ACID | HIGH     | Alembic migrations, foreign keys,     | 100% executed against real PostgreSQL |
|      | Transactions**              |          | JSONB constraints, UUIDv7 generation. | 16 container. (SQLite PROHIBITED).    |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **05**| **ML Mathematical           | HIGH     | Stratified split checks, XGBoost      | Brier score <= 0.12; ECE <= 0.05.     |
|      | Calibration & Fairness**    |          | calibration, Brier score, sex parity. | Disaggregated subgroup evaluation.    |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **06**| **Prediction-to-Explanation | HIGH     | TreeSHAP efficiency axiom tests:      | Mathematical identity must hold:      |
|      | Consistency**               |          | sum of phi_i + phi_0 == f(x).         | delta < 1e-5 on all test predictions. |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **07**| **Counterfactual Constraint | HIGH     | Optimizer test freezing Age, Sex,     | 100% test pass asserting immutable   |
|      | Invariance**                |          | history; testing physiological floors.| features are never perturbed.         |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **08**| **Accessibility Target     | HIGH     | Automated axe-core scans, keyboard    | Zero critical/serious axe-core flags. |
|      | Conformance (WCAG 2.2 AA)** |          | traversal, contrast, target sizes.    | Screen reader compatibility verified. |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **09**| **Critical Patient User     | MEDIUM   | Playwright automated end-to-end user  | 100% pass on synthetic patient flow   |
|      | Journeys (Synthetic)**      |          | journeys (register -> intake -> PDF). | in multi-browser test harness.        |
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
| **10**| **Disaster Recovery &       | MEDIUM   | Nightly backup decryption drill       | Successful restore of synthetic DB    |
|      | Backup Restoration**        |          | (`restore_encrypted.sh`).             | using AES-256-GCM authenticated cipher.|
+------+-----------------------------+----------+---------------------------------------+---------------------------------------+
```

---

## 3. Database Test Infrastructure & Evidence Reconciliation

### 3.1 Verification of Existing Test Evidence
Inspection of the existing test suite in `backend/tests/` yields the following verified evidence:
- **Test Files Present:**
  - `tests/test_api_health.py` (4 tests)
  - `tests/test_database_models.py` (7 tests)
  - `tests/test_security.py` (4 tests)
- **Execution Command:** `pytest -v` (Python 3.11.9, pytest-9.0.3).
- **Execution Output:** 15 passed, 1 warning (Starlette form parser deprecation) in 4.56s.
- **Fixture Verification:** Line 19 of `backend/tests/conftest.py` declares:
  `TEST_DATABASE_URL = "sqlite:///:memory:"`
- **Reconciliation Finding:** The 15 existing unit tests run against **in-memory SQLite**. They verify model syntax, relationship cascades, password hashing, and JWT encode/decode functions.

### 3.2 Real PostgreSQL 16 Test Container Mandate
SQLite lacks support for native PostgreSQL 16 UUIDv7 generation, native `JSONB` path operators, row-level locks (`SELECT FOR UPDATE`), and PostgreSQL-specific foreign key cascade mechanics.
- **Mandate:** **PostgreSQL 16 integration testing has not yet been executed.**
- **Enforcement Gate:** In Milestone 04, `backend/tests/conftest.py` must be upgraded to spin up an isolated, dedicated **PostgreSQL 16 container** via Docker/testcontainers. Testing against SQLite is strictly prohibited for database integration tests from Milestone 04 onwards.

---

## 4. Test Data Classification Policy in Testing

- **ML Pipeline Testing (Milestones 09-10):** Uses Category A public de-identified research datasets (UCI Cleveland cohort).
- **Application & Integration Testing (Milestones 01-08, 11-20):** Uses strictly **Category B synthetic application data** generated by `scripts/generate_synthetic_patients.py`.
- **Category C Real Patient Information:** **STRICTLY PROHIBITED** from all test environments, test fixtures, CI/CD runners, and test logs.
