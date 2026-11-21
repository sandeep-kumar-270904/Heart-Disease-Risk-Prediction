# HeartXAI 2.0 — Testing Readiness Audit
**Document ID:** HX-PR-008  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Principal QA Architect & Healthcare Reliability Lead  
**Status:** Risk-Based Quality Strategy Approved — Execution Pending Implementation  
**Date:** November 2026  

---

## 1. Executive Summary

In healthcare software, arbitrary percentage distributions (such as 65% unit / 25% integration / 10% E2E) do not guarantee software safety. A system can achieve 90% unit test coverage while remaining vulnerable to cross-patient data leaks, mathematical calculation errors, or database dialect failures.

In accordance with Phase 12.1 requirements, HeartXAI 2.0 decommissions rigid testing pyramid percentages and institutes an **authoritative, Risk-Based Testing Strategy**. Testing effort is distributed based on clinical risk, security exposure, and data integrity.

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

## 3. Database Integration Test Infrastructure Mandate

### Strict Prohibition of SQLite for Integration Testing
During the Phase 12.1 audit, inspection of `backend/tests/conftest.py` revealed that the 15 baseline unit tests currently execute against an in-memory SQLite database (`sqlite:///:memory:`). While acceptable for rapid unit verification of pure Pydantic/SQLAlchemy logic:
- SQLite does **NOT** support native PostgreSQL 16 UUIDv7 generation, native `JSONB` path operators, row-level locks (`SELECT FOR UPDATE`), or PostgreSQL foreign key cascade mechanics.
- **Mandatory Policy for Milestone 04 Onwards:** All integration, repository, and migration tests must run against a dedicated, isolated **PostgreSQL 16 container** managed via Docker or testcontainers. Testing against SQLite is strictly prohibited for database integration tests.

---

## 4. Evidentiary Test Reporting Rule

In accordance with strict project rules:
1. No test shall ever be reported as "passing" without real terminal execution evidence.
2. Every milestone completion report must include:
   - The exact test execution command (e.g., `pytest tests/test_security.py -v`).
   - The test runner platform and Python/Node version.
   - The duration and total passed/failed count.
   - Any warnings or deprecation notices observed.
3. Fabricating terminal outputs, mock test logs, or synthetic passing commits is strictly prohibited.
