# PHASE 11 QUALITY ASSURANCE DECISIONS AND OPEN GOVERNANCE QUESTIONS

**Document Reference:** `docs/quality/PHASE_11_DECISIONS_AND_OPEN_QUESTIONS.md`  
**Phase:** 11 — Comprehensive Testing Strategy, Quality Assurance & Validation Framework  
**Status:** Approved Technical Ledger  
**Author:** Lead QA Architect & Clinical Quality Lead  
**Traceability:** All Phase 11 Quality Specifications  

---

## 1. Executive Summary

This ledger records all foundational quality assurance, testing methodology, tooling selection, and clinical validation decisions finalized during Phase 11. It also catalogs open quality and clinical governance questions requiring stakeholder and user review prior to test code implementation.

---

## 2. Approved Architectural & Testing Decisions

| Decision ID | Domain | Approved Decision | Rationale & Justification |
| :--- :--- | :--- | :--- | :--- |
| **QA-DEC-01** | **Testing Pyramid** | **70% Unit & Component / 20% Integration & API / 10% End-to-End.** | Inverted pyramids cause brittle CI pipelines and slow feedback loops; balanced distribution maximizes test speed, coverage, and stability. |
| **QA-DEC-02** | **Database Testing Environment** | **Mandatory real PostgreSQL 16 container (Testcontainers); rejection of SQLite for Postgres-specific tests.** | SQLite lacks support for PostgreSQL Row-Level Security (RLS), JSONB indexing, lock timeouts, and trigger semantics; real Postgres guarantees environment parity. |
| **QA-DEC-03** | **API Contract Fuzzing** | **Adopt Schemathesis for property-based OpenAPI 3.1 fuzzing.** | Automatically generates thousands of valid and edge-case request permutations, catching unhandled 500 errors and schema drifts without manual test authoring. |
| **QA-DEC-04** | **ML Target Boundary** | **Strictly evaluate Task A (Angiographic CAD Classification); zero claims of 10-year prospective risk.** | The Cleveland dataset ($N=303$) is cross-sectional without longitudinal follow-up; evaluating it for 10-year risk prediction is scientifically invalid (ADR-009). |
| **QA-DEC-05** | **TreeSHAP Axiom Testing** | **Enforce mathematical Local Accuracy assertion: $\sum \phi_j + \phi_0 = f(x)$ within $\pm 10^{-5}$.** | Proves mathematical integrity of the explainer; guarantees that displayed waterfall feature attributions match the model's raw decision margin. |
| **QA-DEC-06** | **Counterfactual Safety Clamps** | **Hard box constraints: Age, Sex, Fluoroscopy vessels strictly immutable ($\Delta = 0.0$); BP floor $\ge 90\text{ mmHg}$.** | Prevents algorithm from generating absurd or lethal guidance (e.g. telling a patient to become younger or inducing fatal hypotensive shock). |
| **QA-DEC-07** | **Synthetic Data Mandate** | **100% synthetic patient cohorts in non-production environments with mandatory `is_synthetic: true` markers.** | Eradicates patient privacy violation risks under India DPDP Act 2023, EU GDPR Article 9, and US HIPAA. |
| **QA-DEC-08** | **Accessibility Standard** | **WCAG 2.2 Level AA compliance verified via automated axe-core + manual keyboard/screen-reader audits.** | Ensures universal accessibility for visually or motor-impaired patients, including accessible HTML table fallbacks for visual SHAP waterfall charts. |

---

## 3. Open Governance Questions Requiring User Approval

The following items represent operational, clinical, and financial choices requiring explicit stakeholder or user direction:

### Open Question 1: Browser Scope in Automated Pull Request CI
- **Context:** Playwright can execute E2E test suites across all three browser rendering engines (Chromium, Firefox, WebKit) on every pull request, or restrict PR CI to Chromium while running the full multi-browser matrix in nightly runs.
- **Options:**
  - **Option A (Recommended):** Run Chromium in PR CI ($\approx 3\text{ minutes}$ runtime); run full multi-browser matrix (Chromium, Firefox, WebKit, Mobile Safari) in nightly scheduled builds ($\approx 12\text{ minutes}$ runtime).
  - **Option B:** Run all three browser engines on every pull request (higher CI minute consumption; potential developer feedback delay).
- **Recommendation:** Option A. Optimizes developer feedback loops while guaranteeing full cross-browser regression verification nightly.

### Open Question 2: Clinical Content Advisory Sign-off Workflow
- **Context:** Phase 11 specifies a formal Medical Advisory Review before any real-world clinical deployment to verify educational disclaimers and emergency symptom warnings.
- **Options:**
  - **Option A (Academic / Capstone Scope):** Faculty Advisor / Project Review Board acts as the designated clinical review authority for academic evaluation.
  - **Option B (Production Clinical Deployment):** Formal engagement of an independent licensed cardiologist / institutional ethics review board (IRB).
- **Recommendation:** Option A for the current academic defense phase; transition to Option B prior to any future pilot testing with live human patients.

### Open Question 3: Code Coverage Hard Gate Threshold
- **Context:** The master QA strategy proposes minimum line coverage thresholds:
  - Backend (FastAPI + ML): **$\ge 85\%$**
  - Frontend (React components + stores): **$\ge 80\%$**
- **Decision Required:** Should PRs that introduce new code with coverage below these thresholds be blocked automatically by CI, or generate a warning?
- **Recommendation:** Enforce hard blocking CI gate for backend ($\ge 85\%$) and core ML components ($100\%$); allow a transition grace period for non-critical frontend presentation components during initial implementation sprints.

---

## 4. Unresolved Quality Risks & Mitigation

| Quality Risk | Likelihood | Impact | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Small Training Sample Power ($N=303$)** | Medium | High | Enforce shallow tree depths ($\le 3$), strict L2 regularisation, and mandatory nested cross-validation with Brier score $\le 0.14$. |
| **Third-Party Directory Flakiness** | Medium | Medium | Mock Service Worker (MSW) in frontend tests; static JSON fixture fallbacks in backend integration tests. |
| **Flaky Visual Regression Tests** | Low | Low | Avoid brittle pixel-diff testing; prioritize DOM role assertions and accessible tree structure verification. |

---

## 5. Phase Sign-Off Gate

The Phase 11 Comprehensive Testing Strategy, Quality Assurance, and Validation Framework is complete across 21 technical documents in `docs/quality/`. 

**STOP GATE ENGAGED:** In strict accordance with Prompt 11 instructions, **no application code has been implemented, no testing tools have been installed, and no tests have been executed or claimed as passed**. The system is halted awaiting formal review and approval.
