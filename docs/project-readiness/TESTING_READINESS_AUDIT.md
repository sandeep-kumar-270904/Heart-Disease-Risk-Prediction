# HeartXAI 2.0 — Testing Readiness Audit
**Document ID:** HX-PR-008  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal QA Architect & Application Reliability Engineer  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

Quality assurance in healthcare applications is not merely about finding software bugs; it is about verifying clinical boundaries, guaranteeing mathematical reproducibility, safeguarding patient privacy, and preventing algorithmic bias.

This audit evaluates the testing strategy established in Phase 11. It verifies that every functional, non-functional, security, and machine learning requirement is paired with a concrete, automated verification harness.

---

## 2. The Comprehensive Testing Pyramid

The testing framework establishes a balanced distribution of testing effort, maximizing automated verification speed while minimizing brittle end-to-end overhead:

```
                  / \
                 /   \
                / E2E \       --> 10% (Playwright automated user journeys)
               /-------\
              / Integr. \     --> 25% (FastAPI TestClient + Real PostgreSQL 16)
             /-----------\
            / Unit Tests  \   --> 65% (Pytest isolated logic + Vitest UI components)
           /---------------\
```

---

## 3. Requirement-to-Test Verification Matrix

| Requirement Area | Critical Acceptance Criteria | Automated Verification Harness | Target Coverage |
| :--- | :--- | :--- | :---: |
| **User Authentication** | Argon2id verification; JWT expiration (15m); token refresh rotation; Redis revocation. | `tests/backend/test_security.py` | **100%** |
| **Anti-IDOR Isolation** | Non-owners and unauthorized doctors receive 404/403 when requesting foreign assessment IDs. | `tests/backend/test_patient_isolation.py` | **100%** |
| **Biomarker Input Parsing** | Unit conversions ($\text{mg/dL} \leftrightarrow \text{mmol/L}$) accurate to 4 decimal places; reject physiologically impossible values. | `tests/backend/test_unit_conversions.py` | **100%** |
| **PostgreSQL Schema Integrity** | Enforce UUIDv7 primary keys, UTC timestamps, JSONB constraints, cascading deletes. | `tests/backend/test_database_models.py` *(15 passing)* | **95%** |
| **ML Inference & Serving** | In-process C++ inference latency $<20\text{ ms}$; outputs bounded in $[0, 1]$; zero memory leaks. | `tests/ml/test_inference_pipeline.py` | **95%** |
| **Probability Calibration** | Brier score $\le 0.12$; Expected Calibration Error (ECE) $\le 0.05$ across 10 reliability bins. | `tests/ml/test_model_calibration.py` | **100%** |
| **TreeSHAP Explainability** | Sum of local SHAP attributions plus expected value equals model margin ($\sum \phi_i + \phi_0 = f(\mathbf{x})$). | `tests/ml/test_shap_axioms.py` | **100%** |
| **Counterfactual Realism** | Age and Sex remain strictly immutable; BP/cholesterol changes are non-increasing and bounded. | `tests/ml/test_counterfactual_bounds.py` | **100%** |
| **Emergency Safety Gate** | Entering resting $\text{BP} > 180\text{ mmHg}$ or chest pain with severe shortness triggers emergency red-flag UI banner. | `tests/frontend/emergency_banner.test.tsx` | **100%** |
| **Accessibility (a11y)** | Zero axe-core critical or serious violations; full keyboard navigation; WCAG 2.1 AA compliance. | `tests/frontend/accessibility.test.ts` | **100%** |
| **End-to-End User Flow** | Patient completes registration, fills clinical intake, views SHAP chart, generates PDF report. | `tests/e2e/patient_journey.spec.ts` | **100%** |

---

## 4. Test Infrastructure Mandates

### 4.1 Prohibition of SQLite for Database Integration Tests
A historical flaw in testing PostgreSQL applications is using SQLite in memory for test speed. SQLite lacks support for PostgreSQL-specific types (`UUID`, `JSONB`, `TIMESTAMPTZ`, row-level locks, and table partitioning).
- **Mandate:** All integration tests must execute against a dedicated, isolated PostgreSQL 16 container spun up via Docker or testcontainers. SQLite is strictly forbidden for integration testing.

### 4.2 Machine Learning Invariance & Robustness Testing
To ensure clinical safety, the ML subsystem must pass automated stress-testing before deployment:
- **Perturbation Testing:** Adding Gaussian noise ($\epsilon \sim \mathcal{N}(0, 0.01)$) to continuous biomarkers must not cause abrupt risk score discontinuities ($|\Delta P| < 0.05$).
- **Fairness & Disaggregated Evaluation:** Model recall and specificity must not diverge by more than $10\%$ between male and female sub-cohorts.

---

## 5. Definition of Test Pass for CI/CD Gates

Before any pull request can be merged into `main` during implementation:
1. All unit and integration test suites must pass (100% pass rate).
2. Code coverage must meet or exceed defined thresholds:
   - Backend Core & Security: $\ge 90\%$
   - ML Inference & Calibration: $\ge 95\%$
   - Frontend Presentation: $\ge 80\%$
3. Zero static analysis errors reported by Ruff, ESLint, TypeScript compiler (`tsc --noEmit`), and Bandit security scanner.
4. Total test execution time in GitHub Actions CI must remain under 8 minutes.
