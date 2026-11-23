# HeartXAI 2.0 — Project Decision Register
**Document ID:** HX-PR-016  
**Version:** 2.2.0 (Phase 12.2 Final Governance Resolution)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Principal Software Architect, Technical Program Manager & Clinical Safety Reviewer  
**Status:** Authoritative Reconciled Register — Governance Decisions Pending User Selection  
**Date:** November 2026  

---

## 1. Executive Summary

This register serves as the authoritative single source of truth for all architectural, clinical, security, and governance decisions across HeartXAI 2.0.

In accordance with Phase 12.2 requirements:
- **Confirmed Architectural Decisions (ADRs 001–012):** Locked technical decisions confirmed during architectural design.
- **Rejected Proposals Register (REJ 001–006):** Proposals evaluated and explicitly rejected with documented technical rationale.
- **Authoritative Governance Decisions (DEC-001–005):** Core strategic decisions requiring explicit user selection and approval prior to Milestone 01 authorization. Each is strictly marked **PENDING USER DECISION** (never falsely marked approved).

---

## 2. Confirmed Architectural Decisions (ADRs 001–012)

```
+---------------------------------------------------------------------------------------------------------+
|                                        CONFIRMED ARCHITECTURAL DECISIONS                                |
+---------+----------------------------------------------+------------------------------------------------+
| Ref ID  | Decision Title & Scope                       | Core Technical Rationale & Impact              |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-001 | **Modular In-Process Monolith**              | Single FastAPI deployment with in-process C++  |
|         | In-process XGBoost C-API inference           | ML worker. Sub-2ms inference; eliminates gRPC  |
|         |                                              | network overhead and microservices complexity. |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-002 | **PostgreSQL 16 as Relational PHI Store**    | ACID transactions, foreign key cascades, and   |
|         | Native JSONB for ML payloads and audit logs  | row-level locks for patient consent grants.    |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-003 | **Argon2id for Password Hashing**            | RFC 9106 compliance. 64 MB memory cost, 3 time |
|         | Superior resistance to GPU brute-force       | iterations, 4 parallel threads.                |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-004 | **Dual-Token Session Lifecycle**             | 15-min in-memory access JWTs prevent XSS theft;|
|         | Memory JWT + 7-day HttpOnly refresh cookie   | HttpOnly SameSite=Lax cookie prevents script.  |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-005 | **Redis Token Blacklisting & Rotation**      | Cryptographic token family rotation on refresh |
|         | Automatic revocation upon reuse detection    | with strict fail-closed security behavior.     |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-006 | **TreeSHAP for Local Feature Attribution**   | Exact Shapley values computed via fast C++ tree|
|         | Explains model margins, not biological cause | traversal without KernelSHAP sampling error.   |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-007 | **Docker Compose Container Orchestration**   | Simple, reproducible multi-container stack     |
|         | Nginx, FastAPI, PostgreSQL 16, Redis 7.2     | without premature Kubernetes overhead for MVP. |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-008 | **Strict Non-Diagnostic CDS Boundary**       | Educational clinical decision support under    |
|         | Mandatory disclaimers & 4-pillar governance  | FDA 21st Century Cures Act Sec 520(o)(1)(E) &  |
|         |                                              | FDA January 2026 CDS Software Guidance.        |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-009 | **Mandatory Unit Normalization Layer**       | Transparent bi-directional conversions for     |
|         | mg/dL <-> mmol/L before ML feature injection | international users; audited via unit tests.   |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-010 | **Nginx 1.26 as Edge Reverse Proxy**         | Handles TLS 1.3 termination, HSTS, CSP headers,|
|         | SSL, rate limiting, and static file delivery | and upstream routing to FastAPI backend.       |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-011 | **Universal Country Configuration Adapter**  | Extensible adapter pattern supporting any ISO  |
|         | Pluggable adapters; initial US, IN, UK demos | 3166-1 country; units, hotlines, directories.  |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-012 | **AES-256-GCM Authenticated Offsite Backups**| Nightly pg_dump piped through OpenSSL AEAD     |
|         | Encrypted at rest before cloud object push   | with SHA-256 integrity checksums (ADR-012).    |
+---------+----------------------------------------------+------------------------------------------------+
```

---

## 3. Rejected Proposals Register

```
+---------------------------------------------------------------------------------------------------------+
|                                           REJECTED PROPOSALS REGISTER                                   |
+---------+-----------------------------------+-----------------------------------------------------------+
| Ref ID  | Rejected Proposal                 | Concrete Rejection Rationale                              |
+---------+-----------------------------------+-----------------------------------------------------------+
| REJ-001 | Microservices with Triton/gRPC    | Adds 15–30 ms network latency and multi-container failure |
|         |                                   | modes for a simple 13-feature tabular inference model.    |
+---------+-----------------------------------+-----------------------------------------------------------+
| REJ-002 | MongoDB / Document Database       | Patient consent grants, doctor directories, and audit     |
|         |                                   | trails require relational ACID foreign key integrity.     |
+---------+-----------------------------------+-----------------------------------------------------------+
| REJ-003 | Uncalibrated Raw XGBoost Output   | Raw log-odds margins presented as probabilities mislead   |
|         |                                   | patients and clinicians. Calibration is mandatory.        |
+---------+-----------------------------------+-----------------------------------------------------------+
| REJ-004 | SQLite for Integration Testing    | SQLite lacks PostgreSQL UUIDv7, JSONB operators, and row  |
|         |                                   | locks; real PostgreSQL 16 container is required in M04.   |
+---------+-----------------------------------+-----------------------------------------------------------+
| REJ-005 | Client-Side Model Execution (JS)  | Exposes model weights, prevents centralized audit logging,|
|         |                                   | and creates browser compatibility variance.               |
+---------+-----------------------------------+-----------------------------------------------------------+
| REJ-006 | Deterministic Task B in MVP       | Conflates cross-sectional classification with prospective |
|         | (ACC/AHA PCE or PREVENT in MVP)   | risk; guidelines transitioning; deferred to research.     |
+---------+-----------------------------------+-----------------------------------------------------------+
```

---

## 4. Authoritative Governance Decisions Approved by User

The table below records the authoritative decisions approved by the user on 23 November 2026, officially unlocking Milestone 01:

```
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                     GOVERNANCE DECISIONS APPROVED BY USER                                                                      |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| ID      | Decision Description     | Available Options     | Selected Option       | Selection Rationale     | Primary Risks      | Dependencies  | Status    |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Hosting Profile &      | A: Tier A Minimal VPS | **Option A: Tier A    | Lowest cost baseline for| VPS single point   | Milestone 01, | **APPROVED|
| 001**   | Infrastructure Budget**  |    (~$25-$55/mo)      | Minimal VPS**         | dev, testing, synthetic | of failure; manual | Milestone 20  | BY USER** |
|         |                          | B: Tier B AWS Cloud   |                       | demos; capacity sizing  | failover during    |               |           |
|         |                          |    (~$250/mo)         |                       | ('500+ assessments') is | hardware outage.   |               |           |
|         |                          |                       |                       | unverified estimate.    |                    |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Clinical Governance    | A: Multi-Track Phased | **Option A: Multi-    | Enables synthetic-data  | Requires strict    | Milestones    | **APPROVED|
| 002**   | Implementation Scope**   |    Governance for MVP | Track Phased          | prototyping with active | enforcement of     | 08, 14, 16    | BY USER** |
|         | (4 Distinct Tracks)      |    (Advisory/Content  | Governance**          | clinical review; docu-  | prohibited clinical|               |           |
|         |                          |    active in MVP;     |                       | mented ethics/reg deter-| claims ledger;     |               |           |
|         |                          |    ethics/reg deter-  |                       | mination required before| Category C strictly|               |           |
|         |                          |    mination gate)     |                       | human-participant study.| prohibited.        |               |           |
|         |                          | B: Institutional Gate |                       |                         |                    |               |           |
|         |                          |    Prior to Coding    |                       |                         |                    |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Cardiovascular         | A: Task A MVP only    | **Option A: Task A    | Preserves scientific    | Users cannot get   | Milestones    | **APPROVED|
| 003**   | Prediction Scope**       |    (Task B to research| MVP Only**            | integrity; eliminates   | 10-year risk % in  | 09, 10, 11,   | BY USER** |
|         |                          | B: Implement Task B   |                       | confusion between CAD   | MVP; must wait for | 14            |           |
|         |                          |    calculator in MVP  |                       | detection & future risk.| future research.   |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Geographic Adapter     | A: Adapter Pattern as | **Option A: Adapter   | Proves architectural    | Operational and    | Milestones    | **APPROVED|
| 004**   | Extensibility Goal &     |    Extensibility Goal | Pattern Extensibility | decoupling for units    | regulatory readiness| 08, 15       | BY USER** |
|         | Localization Scope**     |    (US/IN/UK Synth)   | Goal (US/IN/UK Synth)*| without claiming global | must be verified per|              |           |
|         |                          | B: US-Only Baseline   |                       | operational readiness.  | jurisdiction.      |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Data Classification &  | A: Three-Tier Class-  | **Option A: Three-    | Prohibits Category C in | Cat A research data| All           | **APPROVED|
| 005**   | Patient Data Policy**    |    ification (Cat A/B;| Tier Classification   | MVP; distinguishes Cat A| carries historical | Milestones    | BY USER** |
|         |                          |    Cat C Prohibited)  | (Cat C Prohibited)**  | human research risk from| privacy risks;     | (01–20)       |           |
|         |                          | B: Real PHI Pilot     |                       | Cat B synthetic data;   | Option B outside   |               |           |
|         |                          |    (Outside MVP Scope)|                       | mandates M09 review.    | MVP scope.         |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
```

---

## 5. Approval Tracking Log

In accordance with strict project rules:
- Antigravity shall never mark decisions DEC-001 through DEC-005 as "Approved" until the user explicitly inputs their choice.
- **Approval Timestamp:** 23 November 2026.
- **User Selection:** The user explicitly selected and approved all architectural recommendations:
  - **DEC-001:** Option A (Tier A Minimal VPS, ~$25–$55/mo).
  - **DEC-002:** Option A (Multi-Track Phased Governance).
  - **DEC-003:** Option A (Task A MVP Only).
  - **DEC-004:** Option A (Universal Country Adapter Extensibility Goal).
  - **DEC-005:** Option A (Three-Tier Data Classification; Category C Strictly Prohibited in MVP).
- **Milestone 01 Authorization:** Granted by user on 23 November 2026. All gates for Milestone 01 initiation are fully satisfied.
