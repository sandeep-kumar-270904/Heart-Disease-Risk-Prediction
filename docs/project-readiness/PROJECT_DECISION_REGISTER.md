# HeartXAI 2.0 — Project Decision Register
**Document ID:** HX-PR-016  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal Software Architect & Technical Program Manager  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

This register records all major architectural, scientific, product, and infrastructure decisions across HeartXAI 2.0. To maintain complete transparency, decisions are categorized into **Confirmed Decisions**, **Proposed Decisions**, **Rejected Decisions**, and **Decisions Requiring Explicit User Approval**.

---

## 2. Confirmed Decisions (Approved ADRs 001–012)

```
+---------------------------------------------------------------------------------------------------------+
|                                        CONFIRMED DECISION REGISTER                                      |
+---------+----------------------------------------------+------------------------------------------------+
| Ref ID  | Decision Title & Scope                       | Core Rationale & Impact                        |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-001 | **Modular In-Process Monolith Architecture** | Eliminates microservice serialization overhead |
|         | Single FastAPI deployment with C++ ML worker | and network latency; sub-2ms tabular inference.|
+---------+----------------------------------------------+------------------------------------------------+
| ADR-002 | **PostgreSQL 16 as Primary PHI Store**       | ACID transactions, foreign key cascades, and   |
|         | Native JSONB for ML payloads and audit logs  | relational integrity for patient consent.      |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-003 | **Argon2id for Password Hashing**            | RFC 9106 compliance; superior resistance to    |
|         | 64MB memory cost, 3 iterations, 4 threads    | GPU/ASIC brute-force attacks compared to bcrypt|
+---------+----------------------------------------------+------------------------------------------------+
| ADR-004 | **Dual-Token Session Lifecycle**             | In-memory access JWTs prevent XSS theft;       |
|         | 15-min access JWT + 7-day HttpOnly cookie    | HttpOnly refresh cookies prevent script access.|
+---------+----------------------------------------------+------------------------------------------------+
| ADR-005 | **Redis for Token Blacklisting & Sessions**  | Instant revocation capability for refresh      |
|         | Token family rotation on every refresh call  | tokens and distributed rate limiting.          |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-006 | **TreeSHAP for Local Explainability**        | Exact Shapley values computed efficiently      |
|         | Fast C++ tree-traversal algorithm            | without sampling variance of KernelSHAP.       |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-007 | **Docker Compose Container Orchestration**   | Simple, reproducible deployment without the    |
|         | Multi-container stack (Nginx, API, DB, Redis)| operational overhead of Kubernetes for MVP.    |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-008 | **Strict Non-Diagnostic CDS Boundary**       | Platform classified as educational CDS; avoids |
|         | Statutory disclaimers & physician advisory   | FDA SaMD Class II diagnostic liabilities.      |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-009 | **Mandatory Unit Normalization Layer**       | Transparent bi-directional conversions for     |
|         | mg/dL <-> mmol/L for cholesterol and glucose | international users before ML feature feeding. |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-010 | **Nginx 1.26 as Edge Reverse Proxy**         | Handles TLS 1.3 termination, HSTS, CSP headers,|
|         | Gzip compression and static asset delivery   | and rate limiting before API traffic.          |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-011 | **Global Country Configuration Architecture**| Decouples core logic from localized emergency  |
|         | Pluggable country adapters (US, IN, UK)      | numbers, units, currencies, and directories.   |
+---------+----------------------------------------------+------------------------------------------------+
| ADR-012 | **AES-256-GCM Authenticated Offsite Backups**| Eliminates plaintext database dump risk;       |
|         | Nightly pg_dump piped through OpenSSL AEAD   | guarantees tamper detection and confidentiality|
+---------+----------------------------------------------+------------------------------------------------+
```

---

## 3. Rejected Architectural & Engineering Proposals

The audit verified that the following alternatives were deliberately evaluated and rejected:

1. **Rejected Proposal 1: Microservices Architecture with gRPC / Triton Inference Server**
   - *Reason for Rejection:* Introduced 15–30 ms network latency, multi-service deployment overhead, and complex service mesh requirements for a simple tabular model with 13 features.
2. **Rejected Proposal 2: MongoDB / Document Database for Core Storage**
   - *Reason for Rejection:* Patient consent grants, doctor directories, and audit trails are deeply relational; MongoDB lacks native ACID multi-table foreign key constraints and transactional integrity.
3. **Rejected Proposal 3: Uncalibrated Raw XGBoost Output as Risk Score**
   - *Reason for Rejection:* Raw tree outputs represent uncalibrated log-odds margins; presenting them as probabilities to patients is clinically irresponsible and leads to misinterpretation.
4. **Rejected Proposal 4: In-Memory SQLite for Integration Testing**
   - *Reason for Rejection:* SQLite does not support PostgreSQL UUIDv7 types, JSONB operators, or row-level locking, leading to false-positive test results.
5. **Rejected Proposal 5: Client-Side ML Model Execution (ONNX.js)**
   - *Reason for Rejection:* Exposes proprietary model weights and hyperparameters to client inspection, prevents centralized audit logging, and introduces browser performance inconsistencies.

---

## 4. Unresolved Decisions Requiring Explicit User Approval

The following three decisions remain in **Proposed** status and require explicit stakeholder resolution before Milestone 01 starts:

```
+---------------------------------------------------------------------------------------------------------+
|                               DECISIONS REQUIRING EXPLICIT USER APPROVAL                                |
+----+-----------------------+----------------------------------+-----------------------------------------+
| ID | Decision Title        | Option A (Recommended)           | Option B (Alternative)                  |
+----+-----------------------+----------------------------------+-----------------------------------------+
| D1 | **Production Hosting  | **Tier A: Minimal VPS**          | **Tier B: AWS Managed Cloud**           |
|    | Infrastructure**      | Single VPS (4 vCPU, 8 GB RAM) via| AWS ECS Fargate + RDS PostgreSQL MultiAZ|
|    |                       | Docker Compose (~$20/month).     | + ElastiCache Redis (~$140/month).      |
+----+-----------------------+----------------------------------+-----------------------------------------+
| D2 | **Clinical Advisory   | **Academic / Advisory Review**   | **Formal Independent Review Board**     |
|    | Governance**          | Review by practicing physician   | Formal Institutional Review Board (IRB) |
|    |                       | collaborators for MVP CDS.       | approval prior to public beta.          |
+----+-----------------------+----------------------------------+-----------------------------------------+
| D3 | **Task B Prospective  | **Separate Deterministic Engine**| **Defer Entirely to Post-MVP**          |
|    | 10-Yr Risk Scope**    | Implement ACC/AHA 10-year risk   | Strictly limit platform to Task A       |
|    |                       | equation in Milestone 14.        | (angiographic CAD detection).           |
+----+-----------------------+----------------------------------+-----------------------------------------+
```
