# TEST AUTOMATION FRAMEWORK AND REPORTING SPECIFICATION

**Document Reference:** `docs/quality/TEST_AUTOMATION_AND_REPORTING.md`  
**Phase:** 11 — Comprehensive Testing Strategy, Quality Assurance & Validation Framework  
**Status:** Approved Technical Architecture  
**Author:** Principal QA Architect & Automation Lead  
**Traceability:** NFR-MAINT-01, NFR-REL-01, ADR-001, ADR-007  

---

## 1. Executive Summary & Tooling Rationale

Test automation for HeartXAI 2.0 is designed to provide rapid, high-fidelity developer feedback while executing comprehensive end-to-end and security regression checks in CI/CD pipelines.

### Tool Selection Rationale:
- **Pytest + HTTPX AsyncClient:** Industry-standard Python test runner with native asynchronous support, fixture dependency injection, and clean parameterization for FastAPI.
- **Vitest + React Testing Library:** High-speed ESM-native frontend test runner tightly coupled with Vite, providing instant HMR test execution.
- **Playwright:** Fast, reliable browser automation supporting Chromium, Firefox, and WebKit with native auto-waiting and trace recording.
- **Schemathesis:** Property-based API contract testing that reads OpenAPI 3.1 definitions and autonomously fuzzes endpoints for specification breaches.
- **axe-core Playwright:** Automated accessibility testing engine embedded directly into E2E browser flows.
- **Locust:** Python-based distributed load-testing tool modeling realistic asynchronous patient workflows.

---

## 2. Standardized Test Directory Structure

```text
heartxai-2.0/
├── backend/
│   └── tests/
│       ├── api/                        # REST endpoint integration tests
│       │   ├── test_auth_routes.py
│       │   ├── test_prediction_routes.py
│       │   └── test_user_routes.py
│       ├── database/                   # PostgreSQL schema & migration tests
│       │   ├── test_constraints.py
│       │   └── test_migrations.py
│       ├── ml/                         # ML pipeline & mathematical tests
│       │   ├── test_data_hygiene.py
│       │   ├── test_model_reproducibility.py
│       │   ├── test_shap_properties.py
│       │   └── test_counterfactual_safety.py
│       ├── security/                   # IDOR, auth bypass, rate limit tests
│       │   ├── test_idor.py
│       │   └── test_penetration.py
│       ├── safety/                     # Clinical safety & disclaimer audits
│       │   └── test_healthcare_safety.py
│       ├── fixtures/                   # Static test JSON fixtures
│       └── conftest.py                 # Pytest shared fixtures & DB lifecycle
├── frontend/
│   └── tests/
│       ├── components/                 # Component RTL unit tests
│       │   ├── AssessmentForm.test.tsx
│       │   ├── SHAPWaterfall.test.tsx
│       │   └── RiskScoreCard.test.tsx
│       ├── state/                      # Zustand store tests
│       │   ├── authStore.test.ts
│       │   └── predictionStore.test.ts
│       └── setup.ts                    # Vitest environment setup
├── e2e/                                # Playwright End-to-End Test Suites
│   ├── journeys/
│   │   ├── new_patient_journey.spec.ts
│   │   ├── returning_patient.spec.ts
│   │   └── security_intrusion.spec.ts
│   ├── accessibility/
│   │   └── wcag_audit.spec.ts
│   └── playwright.config.ts
└── performance/                        # Locust load testing scripts
    └── locustfile.py
```

---

## 3. Naming Conventions & Canonical Test ID Grammar

### 3.1 Test ID Grammar
Every test case implements a canonical identifier:
$$\text{TC-}\langle\text{DOMAIN}\rangle\text{-}\langle\text{NUM}\rangle$$
- Domains: `AUTH`, `PRED`, `USER`, `DIR`, `REP`, `ML`, `SHAP`, `CF`, `SEC`, `ACC`, `PERF`, `REL`, `SAFE`.
- Example: `TC-PRED-004` (TreeSHAP local accuracy test).

### 3.2 Method Naming Conventions
- Backend: `def test_<action>_<expected_behavior>_when_<condition>()`  
  *Example:* `def test_predict_returns_422_when_blood_pressure_exceeds_ceiling()`
- Frontend: `it("should render error message when password does not meet complexity", ...)`

---

## 4. Test Execution Lifecycle in CI/CD

```mermaid
graph TD
    Commit[Git Push / Pull Request] --> Stage1[Stage 1: Fast Feedback (< 2 min)]
    subgraph FastFeedback ["Fast Unit & Static Gates"]
        L1[Linters & Type Checkers]
        L2[Backend Unit Tests: Pytest -m unit]
        L3[Frontend Component Tests: Vitest]
    end
    Stage1 --> FastFeedback

    FastFeedback --> Stage2[Stage 2: Integration & Contract (< 5 min)]
    subgraph IntegrationGates ["Integration & Security Gates"]
        I1[Database & API Tests: Pytest -m integration]
        I2[ML Validation & Axiom Tests: Pytest -m ml]
        I3[Schemathesis API Contract Fuzzing]
        I4[Secret & Vulnerability Scans: Gitleaks / Trivy]
    end
    Stage2 --> IntegrationGates

    IntegrationGates --> Stage3[Stage 3: Full End-to-End Suite (< 10 min)]
    subgraph E2EGates ["Playwright Multi-Browser Gates"]
        E1[Chromium, Firefox, WebKit Journeys]
        E2[axe-core Automated Accessibility Scans]
    end
    Stage3 --> E2EGates

    E2EGates --> Pass[All Gates Passed: PR Ready for Merge]
```

---

## 5. Flaky Test Mitigation Strategy

Flaky tests (tests that pass and fail intermittently without code changes) erode developer trust and stall release pipelines:
1. **Root-Cause Policy:** Tests that fail intermittently are **never** merely retried in an infinite loop. They are quarantined immediately using `@pytest.mark.flaky_quarantine` and assigned a high-priority bug ticket.
2. **Deterministic Time & Network:** Time-dependent tests freeze clock state via `freezegun`. Network-dependent tests use hermetic mocking via `respx` or `MSW`.
3. **Playwright Auto-Waiting:** Tests rely on Playwright's built-in web-first assertions (`await expect(locator).toBeVisible()`) rather than arbitrary `sleep()` or timeout statements.
