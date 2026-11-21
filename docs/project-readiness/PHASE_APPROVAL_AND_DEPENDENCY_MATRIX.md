# HeartXAI 2.0 — Phase Approval & Dependency Matrix
**Document ID:** HX-PR-002  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Technical Program Manager & Independent Technical Auditor  
**Status:** Reconciled Matrix — Conditioned on User Governance Selection  
**Date:** November 2026  

---

## 1. Executive Summary

This matrix provides the reconciled, independent evaluation of all prior project phases (Phases 01 through 11) incorporating the rigorous evidentiary audit and clinical scope resolutions established in Phase 12.1.

---

## 2. Comprehensive Phase Status Audit

```
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                             COMPREHENSIVE PHASE STATUS MATRIX                                                                 |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| Phase | Phase Name               | Output Location    | Artifact Count | Audit Classification  | Evidentiary Basis & Conditions Met    | Downstream Impact    |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **01**| Product & Engineering    | `docs/`            | 8 files        | **Approved**          | Comprehensive CDS benchmarking and    | Phase 02, Phase 03   |
|       | Benchmarking             |                    |                |                       | clinical failure mode analysis.       |                      |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **02**| Product Requirements &   | `docs/`            | 10 files       | **Approved**          | PRD, FRD, NFRD, and RTM verified.     | Phase 03, Phase 06,  |
|       | Scope                    |                    |                |                       | Synthetic demonstration scope locked. | Phase 07             |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **03**| System Architecture &    | `docs/`,           | 24 files +     | **Approved**          | Modular monolith (ADR-001), global    | Phase 06, Phase 07,  |
|       | Remediation              | `backend/`         | 15 tests       |                       | adapter (ADR-011), backups (ADR-012). | Phase 08, Phase 09,  |
|       |                          |                    |                |                       | 15 unit tests pass (SQLite fixture).  | Phase 10             |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **04**| Visual Identity, Design  | `docs/design/`     | 16 files       | **Approved Target**   | Design tokens and component specs     | Milestones 03, 07,   |
| /05   | System & UI/UX           |                    |                |                       | complete. WCAG 2.2 AA target set;     | 08, 12, 14, 19       |
|       |                          |                    |                |                       | implementation conformance pending.   |                      |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **06**| Frontend Engineering     | `docs/frontend/`   | 14 files       | **Approved**          | React 18, Vite, TypeScript, TanStack  | Milestones 02, 07,   |
|       | Architecture             |                    |                |                       | Query, and Zustand architecture set.  | 08, 12, 14, 15, 16   |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **07**| Backend Engineering &    | `docs/backend/`    | 18 files       | **Approved**          | FastAPI, Pydantic v2, SQLAlchemy 2.0  | Milestones 04, 05,   |
|       | API Implementation Plan  |                    |                |                       | async, asyncpg, RFC 7807 error model. | 06, 11, 14, 15, 17   |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **08**| ML Research & Model      | `docs/ml/`         | 19 files       | **Approved with Scope | Task A strictly bounded as experimental| Milestones 09, 10,   |
|       | Development Strategy     |                    |                | Corrections**         | Cleveland classifier. Task B removed  | 11, 12, 13           |
|       |                          |                    |                |                       | from MVP and deferred to research.    |                      |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **09**| Security, Privacy &      | `docs/security/`   | 19 files       | **Approved Target**   | STRIDE threat model complete. Argon2id| Milestones 05, 06,   |
|       | Threat Modeling          |                    |                |                       | & JWT designed; penetration tests     | 18                   |
|       |                          |                    |                |                       | and Redis rotation pending build.     |                      |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **10**| DevOps & Deployment      | `docs/devops/`     | 18 files       | **Approved Proposal** | Itemized cost estimation authored     | Milestones 01, 19,   |
|       | Architecture             |                    |                |                       | (Tier A ~$21-$55/mo vs Tier B ~$252); | 20                   |
|       |                          |                    |                |                       | staging execution pending M20.        |                      |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
| **11**| Testing Strategy & QA    | `docs/quality/`    | 21 files       | **Approved**          | Risk-based testing strategy replacing | All Milestones       |
|       | Framework                |                    |                |                       | arbitrary %s; PostgreSQL 16 container | (01–20)              |
|       |                          |                    |                |                       | required for integration testing.     |                      |
+-------+--------------------------+--------------------+----------------+-----------------------+---------------------------------------+----------------------+
```

---

## 3. Phase 12.1 Review Feedback & Remediation Traceability

```
+---------------------------------------------------------------------------------------------------------+
|                                    PHASE 12.1 REMEDIATION TRACEABILITY                                  |
+---------------------------------------------+-----------------------------------------------------------+
| Review Finding / Audit Feedback             | Concrete Remediation in Phase 12.1 Deliverables           |
+---------------------------------------------+-----------------------------------------------------------+
| 1. Conflation of Task A and Task B          | Remediated in `HEALTHCARE_AND_SCIENTIFIC_VALIDITY_AUDIT.md`|
|    - Proposed 10-year risk calculator in MVP| and `MASTER_IMPLEMENTATION_ROADMAP.md`. Task B removed    |
|      created clinical confusion.            | completely from MVP; Task A bounded as experimental.      |
+---------------------------------------------+-----------------------------------------------------------+
| 2. Reassessment of PCE vs. PREVENT          | Remediated in `HEALTHCARE_AND_SCIENTIFIC_VALIDITY_AUDIT.md`|
|    - Needed current primary clinical lit.   | Evaluated Goff 2014 vs Khan 2024. Excluded both from MVP; |
|                                             | established guidelines-review prerequisites for research. |
+---------------------------------------------+-----------------------------------------------------------+
| 3. Advisory Review vs. IRB Ethics Confusion | Remediated in `HEALTHCARE_AND_SCIENTIFIC_VALIDITY_AUDIT.md`|
|    - Advisory review treated as ethics pass.| Separated physician advisory review from formal human     |
|                                             | subjects research IRB determination.                      |
+---------------------------------------------+-----------------------------------------------------------+
| 4. Premature WCAG Compliance Claims         | Remediated in `PROJECT_DEFINITION_OF_DONE.md`. Replaced   |
|    - Stated "WCAG 2.1 AA compliant" before  | "compliant" with "designed as target; testing pending".   |
|      frontend implementation.               | Upgraded target to WCAG 2.2 AA.                           |
+---------------------------------------------+-----------------------------------------------------------+
| 5. Unqualified "Zero Security Blockers"     | Remediated in `SECURITY_AND_PRIVACY_READINESS_AUDIT.md`    |
|    - Stated zero vulnerabilities existed.   | Clarified: designed controls have zero blockers; runtime  |
|                                             | penetration testing remains an implementation gate.       |
+---------------------------------------------+-----------------------------------------------------------+
| 6. SQLite in Baseline Test Fixture          | Remediated in `PHASE_12_1_CORRECTION_AND_EVIDENCE_REPORT`  |
|    - 15 tests executed against SQLite.      | Documented SQLite fixture usage in `tests/conftest.py`;   |
|                                             | confirmed real PostgreSQL 16 migration in Milestone 04.   |
+---------------------------------------------+-----------------------------------------------------------+
| 7. Arbitrary Testing Pyramid Percentages    | Remediated in `TESTING_READINESS_AUDIT.md`. Decommissioned|
|    - 65/25/10 pyramid lacked risk weighting.| rigid percentages; instituted risk-based testing strategy.|
+---------------------------------------------+-----------------------------------------------------------+
| 8. Vague Hosting Cost Estimates             | Remediated in `OPERATIONAL_COST_ESTIMATION.md`. Authored  |
|    - Lacked itemized service pricing.       | itemized pricing breakdown for Tier A ($21-$55) and B.    |
+---------------------------------------------+-----------------------------------------------------------+
| 9. Governance Register Discrepancies        | Remediated in `PROJECT_DECISION_REGISTER.md` and          |
|    - 3 decisions in dossier vs 5 questions. | `PHASE_12_FINAL_OPEN_QUESTIONS.md`. Reconciled 5 questions|
|                                             | marked strictly `PENDING USER DECISION`.                  |
+---------------------------------------------+-----------------------------------------------------------+
| 10. Real Patient Data Liability             | Remediated across all deliverables. Codified strict       |
|     - Needed explicit data boundaries.      | **100% synthetic demonstration data mandate**.            |
+---------------------------------------------+-----------------------------------------------------------+
```

---

## 4. Phase-to-Milestone Cross-Reference Map

```
PHASE 01 (Research)        --> Foundational Context
PHASE 02 (Requirements)    --> Milestones 02, 08, 14, 15, 16, 17
PHASE 03 (Architecture)    --> Milestones 01, 04, 05, 06, 11
PHASE 04/05 (Design/UX)    --> Milestones 03, 07, 08, 12, 14, 15, 19 (WCAG 2.2 AA Target)
PHASE 06 (Frontend Eng)    --> Milestones 02, 07, 08, 12, 14, 15, 19
PHASE 07 (Backend Eng)     --> Milestones 04, 05, 06, 11, 14, 15, 16, 17
PHASE 08 (ML Research)     --> Milestones 09, 10, 11, 12, 13 (Task A Only)
PHASE 09 (Security)        --> Milestones 05, 06, 18
PHASE 10 (DevOps)          --> Milestones 01, 20 (Operational Cost Tier A)
PHASE 11 (Testing & QA)    --> Enforced continuously via Risk-Based Testing
```

---

## 5. Conditions Precedent to Milestone 01 Execution

Before implementation commences with Milestone 01, the user must explicitly select options for the five strategic governance decisions:
1. **DEC-001 (Hosting Profile):** Tier A Minimal VPS (~$25–$55/mo) vs. Tier B AWS Cloud (~$250/mo).
2. **DEC-002 (Clinical Governance):** Physician Advisory Review vs. Formal Institutional IRB Protocol.
3. **DEC-003 (Cardiovascular Scope):** Task A Experimental ML Only (Task B to Research) vs. Task B in MVP.
4. **DEC-004 (Geographic Launch):** Tri-Country Architecture (US/IN/UK) with Synthetic Demo vs. US-Only.
5. **DEC-005 (Data Classification):** 100% Synthetic Data Mandate vs. Real Patient Data Pilot.
