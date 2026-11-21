# HeartXAI 2.0 — Project Definition of Done (DoD)
**Document ID:** HX-PR-014  
**Version:** 2.2.0 (Phase 12.2 Revision)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Principal QA Architect, Healthcare Safety Reviewer & Security Lead  
**Status:** Approved for Implementation Planning — Mandatory Invariants & Data Categories  
**Date:** November 2026  

---

## 1. Executive Summary

In healthcare software engineering, a feature is **never complete merely because code compiles, passes basic syntax checks, or renders in a browser**. Software operating in healthcare contexts must satisfy strict safety, accessibility, privacy, and architectural invariants before it can be merged or approved.

This document establishes the binding Definition of Done (DoD) for HeartXAI 2.0. Every pull request, feature branch, and milestone must satisfy these criteria.

---

## 2. The Nine Mandatory Healthcare Safety Invariants

Before any feature involving machine learning, clinical data intake, risk scoring, health information, or patient profile management can be considered **DONE**, it must strictly verify these nine non-negotiable healthcare safety invariants:

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            MANDATORY HEALTHCARE SAFETY INVARIANTS                                             |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| No | Safety Invariant                           | Verification & Enforcement Requirement                                      |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 01 | **No Unsupported Diagnosis Claims**        | All UI text, API responses, and exported reports must clearly state that    |
|    |                                            | HeartXAI provides experimental data classification and CDS, NOT a diagnosis.|
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 02 | **No Unsupported Prospective-Risk Claims** | Zero claims predicting 10-year heart attack risk, survival probability, or  |
|    |                                            | incident stroke events from the Cleveland dataset. Task B is excluded.     |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 03 | **No Uncalibrated Probabilities as         | Raw model margin outputs must never be presented as true probabilities.     |
|    | Validated Probabilities**                  | Platt Scaling / Isotonic calibration verified (Brier <= 0.12, ECE <= 0.05). |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 04 | **No Arbitrary Clinical Risk Categories**  | Score bands (Low, Moderate, Elevated) must be documented with explicit      |
|    |                                            | statistical cutoffs, non-diagnostic guidance, and clinical disclaimer copy. |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 05 | **No SHAP Attribution Described as         | Feature attributions must be explicitly described as statistical model     |
|    | Causation**                                | associations within the dataset, never as direct biological etiology.       |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 06 | **No Counterfactual Described as Medical   | Counterfactual lifestyle targets must be described as exploratory mathematical|
|    | Treatment**                                | scenarios, never as clinical prescriptions or guarantees of risk reduction. |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 07 | **No Cross-Patient Data Access             | Automated anti-IDOR tests must verify that users cannot access records of   |
|    | (Strict Anti-IDOR)**                       | other patients. Unauthorized requests must return 403 or obfuscated 404.    |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 08 | **Strict Category B Synthetic Data Mandate | All development, testing, staging, and demo environments must strictly use  |
|    | in Non-Production Environments**           | **Category B synthetic data**. Category C real patient PHI is PROHIBITED.   |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
| 09 | **No Blanket Claims of Regulatory          | The platform shall make no blanket claims that it is exempt from FDA or     |
|    | Exemption or Compliance**                  | medical device regulation, nor claim formal certification or validation.   |
+----+--------------------------------------------+-----------------------------------------------------------------------------+
```

---

## 3. Universal Engineering Definition of Done

For all general software features (API routes, database models, frontend views, utilities), the following 10 engineering gates must be passed:

```
[ ] 1. Traceability: Direct trace to an approved Requirement ID in the RTM.
[ ] 2. Architectural Fidelity: Full adherence to confirmed ADRs (001–012).
[ ] 3. Strict Input Validation: All inputs validated via Pydantic v2 (backend) and Zod/TypeScript (frontend); invalid inputs rejected with RFC 7807 Problem Details.
[ ] 4. Biomarker Bounds Enforcement: Biologically implausible values (BP < 40 or > 300 mmHg; cholesterol < 50 mg/dL) rejected at the boundary.
[ ] 5. Risk-Based Unit & Integration Testing: Tests written alongside implementation; 100% pass rate in CI.
[ ] 6. Real PostgreSQL Verification: Database integration tests executed against real PostgreSQL 16 container (SQLite prohibited for PostgreSQL-specific features).
[ ] 7. Static Analysis & Linting: Zero errors from Ruff, Mypy (`--strict`), ESLint, and TypeScript (`tsc --noEmit`).
[ ] 8. Security & Dependency Check: Zero high/critical vulnerabilities in `pip-audit`, `npm audit`, or Bandit.
[ ] 9. Structured Logging & Scrubbing: JSON logs with correlation `request_id`; zero plaintext passwords, tokens, or unmasked PHI.
[ ] 10. Peer Code Review & Audit Sign-Off: Independent reviewer sign-off verifying adherence to DoD.
```

---

## 4. Accessibility Conformance Definition of Done (WCAG 2.2 AA Target)

All user-facing views must be:
> *"Designed with WCAG accessibility requirements as a target; implementation and conformance testing pending."*

Specific criteria evaluated for **WCAG 2.2 AA**:
1. **Focus Appearance (2.4.11 / 2.4.13):** Clear, highly visible focus indicator with minimum 2px solid contrast outline on all interactive elements.
2. **Target Size (Minimum) (2.5.8):** All clickable and tappable elements have a minimum target size of $24 \times 24$ CSS pixels (with $44 \times 44$ preferred for mobile).
3. **Accessible Authentication (3.3.8):** Authentication flows do not rely on cognitive function tests (e.g., memorizing complex patterns); password fields support copy-paste and password managers.
4. **Redundant Entry (3.3.7):** Previously entered information (e.g., units, demographic baselines in multi-step wizard) is auto-populated or available for selection.
5. **Dragging Movements (2.5.7):** Any slider or draggable element (e.g., counterfactual sliders) provides an accessible single-pointer click/button alternative.
6. **Consistent Help (3.2.6):** Help mechanisms (clinical guidance, emergency hotline links) appear in a consistent location across all assessment views.
7. **Color Contrast:** Minimum $4.5:1$ contrast ratio for body text; $3:1$ for large text, icons, and chart elements.
8. **Screen Reader Support:** Semantic HTML, ARIA live regions for dynamically computed risk results, and accessible SVG labels on charts.
9. **Automated Audit:** Zero critical or serious accessibility violations reported by `axe-core` test runs.

---

## 5. Milestone Completion & Review Protocol

Before declaring an implementation milestone finished:
1. All milestone tasks must be implemented with passing automated test logs.
2. Evidence must be captured from real terminal execution (never fabricated).
3. The milestone report must document any limitations or deferred edge cases.
4. **Antigravity must pause and await explicit user approval before proceeding to the next milestone.**
