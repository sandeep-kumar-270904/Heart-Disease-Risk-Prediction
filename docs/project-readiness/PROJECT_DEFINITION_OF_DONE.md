# HeartXAI 2.0 — Project Definition of Done (DoD)
**Document ID:** HX-PR-014  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal QA Architect & Staff Systems Engineer  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

In healthcare software engineering, a feature is **never complete merely because it renders visually or returns an HTTP 200 response**. Unchecked medical software creates direct patient risk.

This document defines the strict, non-negotiable **Definition of Done (DoD)** that every user story, pull request, and implementation milestone must satisfy before being merged into the master codebase.

---

## 2. Universal Engineering Definition of Done

For any general feature (authentication, navigation, database model, UI layout) to be classified as **DONE**, it must satisfy the following 10 criteria:

```
[ ] 1. Requirement Traceability: Directly traced to an approved requirement ID in the Requirements Traceability Matrix (RTM).
[ ] 2. Architectural Adherence: Conforms to established Architecture Decision Records (ADRs 001–012).
[ ] 3. Strict Input Validation: All inputs validated via Pydantic v2 (backend) and Zod/TypeScript (frontend); invalid inputs rejected with RFC 7807 problem details.
[ ] 4. Authorization & Anti-IDOR: Tenancy, ownership, and role checks verified; unauthorized access returns 403 or obfuscated 404.
[ ] 5. Comprehensive Unit Testing: Core logic covered by unit tests (Pytest/Vitest); meets coverage thresholds (>=90% backend, >=80% frontend).
[ ] 6. Integration Testing: API endpoints verified against a real PostgreSQL 16 test container.
[ ] 7. Static Analysis & Linting: Zero errors from Ruff, Mypy (`--strict`), ESLint, and TypeScript compiler (`tsc --noEmit`).
[ ] 8. Security & Dependency Check: Zero high or critical vulnerabilities reported by Bandit, `pip-audit`, and `npm audit`.
[ ] 9. Logging & Observability: Structured JSON logging with `request_id`; zero plaintext passwords, tokens, or PII.
[ ] 10. Peer Code Review: Formal review and approval by an independent engineering reviewer.
```

---

## 3. Strict Clinical & Healthcare Definition of Done

Any feature involving machine learning, clinical biomarkers, patient health data, risk scoring, or medical information must satisfy these **additional 8 healthcare safety invariants**:

```
+---------------------------------------------------------------------------------------------------------+
|                                    HEALTHCARE & MEDICAL CDS INVARIANTS                                  |
+------------------------------------+--------------------------------------------------------------------+
| Invariant Criterion                | Mandatory Verification Check                                       |
+------------------------------------+--------------------------------------------------------------------+
| **H1. Non-Diagnostic Disclaimer**  | UI screen and exported PDF display the mandatory statutory         |
|                                    | non-diagnostic clinical disclaimer prominently.                    |
+------------------------------------+--------------------------------------------------------------------+
| **H2. Biomarker Plausibility**     | Input validator rejects physiologically impossible biomarker       |
|                                    | values (e.g., BP < 40 or > 300 mmHg; cholesterol < 50 mg/dL).     |
+------------------------------------+--------------------------------------------------------------------+
| **H3. Probability Calibration**    | Risk score is calibrated via Platt Scaling or Isotonic Regression; |
|                                    | uncalibrated raw model margins are NEVER displayed to patients.    |
+------------------------------------+--------------------------------------------------------------------+
| **H4. Risk Categorization Clarity**| Probability output is accompanied by clinical risk tier (Low,      |
|                                    | Moderate, Elevated) and contextual guidance.                       |
+------------------------------------+--------------------------------------------------------------------+
| **H5. TreeSHAP Attribution Truth** | Local feature explanations satisfy efficiency axiom; UI states     |
|                                    | that SHAP values are statistical associations, not causal proofs.  |
+------------------------------------+--------------------------------------------------------------------+
| **H6. Counterfactual Safety**      | Immutable features (Age, Sex, History) are strictly frozen;        |
|                                    | actionable targets enforce physiological floors (BP >= 90).        |
+------------------------------------+--------------------------------------------------------------------+
| **H7. Emergency Red-Flag Tripping**| Entering acute crisis values (resting BP > 180 or exertional chest |
|                                    | pain) immediately renders an emergency hotline warning banner.     |
+------------------------------------+--------------------------------------------------------------------+
| **H8. Complete Audit Trail**       | All risk assessments and PHI access events append an immutable     |
|                                    | entry to the `audit_logs` table with actor and timestamp.          |
+------------------------------------+--------------------------------------------------------------------+
```

---

## 4. Accessibility & UI Definition of Done (WCAG 2.1 AA)

All user interface screens must satisfy:
1. **Contrast Ratio:** Minimum $4.5:1$ for normal text, $3:1$ for large text and interactive components.
2. **Keyboard Navigation:** Full operational capability using Tab, Shift+Tab, Enter, Space, and Arrow keys; visible focus rings.
3. **Screen Reader Compatibility:** Proper ARIA roles, live regions for dynamically loaded assessment scores, and descriptive labels on all form inputs.
4. **Responsive Layout:** Usable without horizontal scrolling across 320px (mobile), 768px (tablet), and 1280px+ (desktop) viewports.
5. **Automated Audit:** Zero critical or serious accessibility violations reported by `axe-core`.

---

## 5. Milestone Completion Protocol

Before declaring an implementation milestone finished:
1. All milestone-specific tasks must have code committed and merged to `develop`.
2. The complete test suite for that milestone must execute with 100% pass rate.
3. A milestone demonstration / test log must be generated.
4. **The agent must pause, present the deliverables, and wait for explicit user approval before proceeding to the next milestone.**
