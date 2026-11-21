# HeartXAI 2.0 — Project Decision Register
**Document ID:** HX-PR-016  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Principal Software Architect & Technical Program Manager  
**Status:** Authoritative Reconciled Register — Governance Decisions Pending User Selection  
**Date:** November 2026  

---

## 1. Executive Summary

This register serves as the authoritative single source of truth for all architectural, clinical, security, and governance decisions across HeartXAI 2.0.

In accordance with Phase 12.1 requirements, all discrepancies between prior question lists and summary dossiers have been resolved. Decisions are strictly categorized into:
- **Confirmed Decisions:** Architectural Decision Records (ADRs 001–012) confirmed during technical architecture design.
- **Rejected Decisions:** Proposals evaluated and explicitly rejected with documented rationale.
- **Governance Decisions Awaiting User Selection:** Core strategic decisions required prior to implementation, marked strictly as **PENDING USER DECISION** (never falsely marked approved).

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
|         | Mandatory disclaimers & physician advisory   | FDA 21st Century Cures Act Sec 520(o)(1)(E).   |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-009 | **Mandatory Unit Normalization Layer**       | Transparent bi-directional conversions for     |
|         | mg/dL <-> mmol/L before ML feature injection | international users; audited via unit tests.   |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-010 | **Nginx 1.26 as Edge Reverse Proxy**         | Handles TLS 1.3 termination, HSTS, CSP headers,|
|         | SSL, rate limiting, and static file delivery | and upstream routing to FastAPI backend.       |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-011 | **Global Country Configuration Architecture**| Decouples core platform from localized units,  |
|         | Pluggable adapters for US, IN, and UK        | emergency hotlines (911/112/999), directories. |
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
|         |                                   | locks; real PostgreSQL 16 container is required.          |
+---------+-----------------------------------+-----------------------------------------------------------+
| REJ-005 | Client-Side Model Execution (JS)  | Exposes model weights, prevents centralized audit logging,|
|         |                                   | and creates browser compatibility variance.               |
+---------+-----------------------------------+-----------------------------------------------------------+
| REJ-006 | Deterministic Task B in MVP       | Conflates cross-sectional classification with prospective |
|         | (ACC/AHA PCE or PREVENT in MVP)   | risk; guidelines are transitioning; deferred to research. |
+---------+-----------------------------------+-----------------------------------------------------------+
```

---

## 4. Authoritative Governance Decisions Awaiting User Selection

The table below reconciles all open governance questions into a single authoritative register. Every decision is pending explicit user selection and approval:

```
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                     GOVERNANCE DECISIONS REQUIRING USER SELECTION                                                             |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| ID      | Decision Description     | Available Options     | Recommended Option    | Selection Rationale     | Primary Risks      | Dependencies  | Status    |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Hosting Profile &      | A: Tier A Minimal VPS | **Option A: Tier A    | Lowest cost for dev and | VPS single point   | Milestone 01, | **PENDING |
| 001**   | Infrastructure Budget**  |    (~$25-$55/mo)      | Minimal VPS**         | synthetic testing; no   | of failure; manual | Milestone 20  | USER      |
|         |                          | B: Tier B AWS Cloud   |                       | cloud lock-in; handles  | failover during    |               | DECISION**|
|         |                          |    (~$250/mo)         |                       | 500+ daily assessments. | hardware outage.   |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Clinical Governance &  | A: Physician Advisory | **Option A: Physician | Appropriate for non-    | Requires strict    | Milestones    | **PENDING |
| 002**   | Review Framework**       |    Review & Disclaimers| Advisory Review**     | diagnostic educational  | enforcement of     | 08, 14, 16    | USER      |
|         |                          | B: Institutional IRB  |                       | CDS under FDA 21st      | prohibited clinical|               | DECISION**|
|         |                          |    Ethics Protocol    |                       | Century Cures Act.      | claims ledger.     |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Cardiovascular         | A: Task A MVP only    | **Option A: Task A    | Preserves scientific    | Users cannot get   | Milestones    | **PENDING |
| 003**   | Prediction Scope**       |    (Task B to research| MVP Only**            | integrity; eliminates   | 10-year risk % in  | 09, 10, 11,   | USER      |
|         |                          | B: Implement Task B   |                       | confusion between CAD   | MVP; must wait for | 14            | DECISION**|
|         |                          |    calculator in MVP  |                       | detection & future risk.| future research.   |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Geographic Launch &    | A: Tri-Country US/IN/ | **Option A: Tri-      | Validates global unit   | Requires seeding   | Milestones    | **PENDING |
| 004**   | Localization Scope**     |    UK Architecture    | Country Architecture  | conversions (mg/dL <->  | emergency contacts | 08, 15        | USER      |
|         |                          | B: US-Only Launch     | with Synthetic Demo** | mmol/L) and emergency   | across three       |               | DECISION**|
|         |                          |                       |                       | hotlines in MVP.        | national regions.  |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Data Classification &  | A: 100% Synthetic Data| **Option A: 100%      | Eliminates HIPAA/GDPR   | Demonstrations use | All           | **PENDING |
| 005**   | Patient Data Policy**    | B: Real Patient PHI   | Synthetic Data**      | breach liability during | synthetic patient  | Milestones    | USER      |
|         |                          |    Pilot              |                       | development; protects   | personas rather    | (01–20)       | DECISION**|
|         |                          |                       |                       | patient confidentiality.| than live records. |               |           |
+---------+--------------------------+-----------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
```

---

## 5. Approval Tracking Policy

In accordance with strict project rules:
- Antigravity shall **never mark decisions DEC-001 through DEC-005 as "Approved"** until the user explicitly inputs their choice in chat.
- Implementation shall not proceed on assumed defaults.
