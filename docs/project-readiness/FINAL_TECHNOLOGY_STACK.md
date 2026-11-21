# HeartXAI 2.0 — Final Technology Stack
**Document ID:** HX-PR-009  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal Software Architect & Staff Systems Engineer  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Executive Summary

This document specifies the authoritative, consolidated technology stack for HeartXAI 2.0. Every library, framework, runtime, and database engine has been evaluated against strict architectural criteria: performance, maintainability, community support, security profile, and alignment with healthcare data integrity standards.

---

## 2. Complete Technology Stack Specification

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                                HEARTXAI 2.0 TECHNOLOGY STACK                                                  |
+---------------------+-------------------+---------------------------------------------+---------------------------------------+
| Domain              | Technology        | Version / Release                           | Core Purpose & Role                   |
+---------------------+-------------------+---------------------------------------------+---------------------------------------+
| **Frontend Core**   | React             | 18.3.1                                      | Declarative UI component tree.        |
|                     | TypeScript        | 5.4.5                                       | End-to-end compile-time type safety.  |
|                     | Vite              | 5.2.11                                      | Ultra-fast ESM bundler and dev server.|
|                     | Tailwind CSS      | 3.4.3                                       | Utility-first CSS & design tokens.    |
|                     | React Router      | 6.23.0                                      | Client-side declarative routing.      |
|                     | TanStack Query    | 5.35.1                                      | Server-state caching & deduplication. |
|                     | Zustand           | 4.5.2                                       | Lightweight client UI state.          |
|                     | Radix UI / shadcn | Latest accessible primitives                | WCAG 2.1 AA accessible UI components. |
|                     | Recharts          | 2.12.7                                      | Responsive SVG charts (SHAP, trends). |
+---------------------+-------------------+---------------------------------------------+---------------------------------------+
| **Backend Core**    | Python            | 3.11.9                                      | High-performance asynchronous runtime.|
|                     | FastAPI           | 0.111.0                                     | High-speed asynchronous REST API.     |
|                     | Pydantic          | 2.7.1                                       | Rust-powered data validation & schemas|
|                     | SQLAlchemy        | 2.0.29 (Async)                              | Type-safe asynchronous ORM.           |
|                     | Alembic           | 1.13.1                                      | Declarative DB schema migrations.     |
|                     | asyncpg           | 0.29.0                                      | High-speed PostgreSQL async driver.   |
|                     | Redis-py          | 5.0.4                                       | In-memory session & rate-limit store. |
+---------------------+-------------------+---------------------------------------------+---------------------------------------+
| **Database**        | PostgreSQL        | 16.2                                        | Relational PHI store with JSONB.      |
|                     | UUIDv7 Extension  | `pgcrypto` / native UUID                    | Time-ordered sortable primary keys.   |
|                     | Redis             | 7.2 (Alpine)                                | Session store & token rotation cache. |
+---------------------+-------------------+---------------------------------------------+---------------------------------------+
| **Machine Learning**| Scikit-learn      | 1.4.2                                       | Preprocessing, pipelines, metrics.    |
|                     | XGBoost           | 2.0.3                                       | Calibrated gradient boosted trees.    |
|                     | SHAP              | 0.45.0                                      | TreeSHAP exact local attributions.    |
|                     | DiCE-ML           | 0.11.0                                      | Constrained counterfactual scenarios. |
|                     | Joblib            | 1.4.0                                       | Serialized model artifact management. |
+---------------------+-------------------+---------------------------------------------+---------------------------------------+
| **Testing & QA**    | Pytest            | 8.2.0 + pytest-asyncio                      | Backend async unit & integration tests|
|                     | Vitest            | 1.6.0                                       | Frontend lightning-fast unit tests.   |
|                     | Playwright        | 1.44.0                                      | Multi-browser end-to-end testing.     |
|                     | axe-core          | 4.9.0                                       | Automated WCAG 2.1 AA accessibility.  |
|                     | Bandit / Ruff     | Latest                                      | Static security and code linting.     |
+---------------------+-------------------+---------------------------------------------+---------------------------------------+
| **Infrastructure**  | Docker            | 26.1                                        | OCI-compliant container runtime.      |
|                     | Docker Compose    | v2.27                                       | Multi-container service orchestration.|
|                     | Nginx             | 1.26 (Alpine)                               | Reverse proxy, SSL, and CSP headers.  |
|                     | GitHub Actions    | Standard Linux Runners                      | Automated CI/CD build & test pipeline.|
|                     | Prometheus        | 2.51                                        | System metrics & API latency scraping.|
|                     | Grafana           | 10.4                                        | Operational dashboards & monitoring.  |
+---------------------+-------------------+---------------------------------------------+---------------------------------------+
```

---

## 3. Technology Evaluation & Selection Rationale

### 3.1 Backend: FastAPI + Pydantic v2 vs. Django REST Framework
- **Selected:** FastAPI 0.111 + Pydantic v2.
- **Rationale:** Native asynchronous ASGI concurrency (`async`/`await`), automatic OpenAPI/Swagger documentation, and Pydantic v2's Rust-based validation core (providing a 5x to 10x throughput advantage over Django serialization).
- **Alternatives Rejected:** Django REST Framework was rejected due to heavy synchronous ORM baggage and microsecond serialization bottlenecks during batch ML inference.

### 3.2 Database: PostgreSQL 16 vs. MongoDB / Multi-Model
- **Selected:** PostgreSQL 16.
- **Rationale:** Strict ACID guarantees, row-level locking, foreign key integrity, and superior relational modeling for patient identity, consents, and clinical history. PostgreSQL’s native `JSONB` support allows seamless caching of unstructured ML feature arrays, TreeSHAP explanation trees, and counterfactual vectors within the same atomic transaction.
- **Alternatives Rejected:** MongoDB was rejected because healthcare audit trails and relational patient-doctor consent grants require strict foreign key constraints and transactional integrity.

### 3.3 ML Subsystem: In-Process XGBoost + TreeSHAP vs. External Microservice (Triton / TorchServe)
- **Selected:** In-process C++ inference via XGBoost C-API.
- **Rationale:** Tabular tabular risk models on 13 features execute in $<2\text{ ms}$. Calling an external microservice over gRPC/HTTP introduces 15–30 ms of network serialization, socket management, and multi-service failure modes. In-process execution satisfies ADR-001 (Modular Monolith) with zero network overhead.
- **Alternatives Rejected:** Triton Inference Server was rejected as premature infrastructure complexity for a tabular model.

### 3.4 Frontend State: TanStack Query v5 + Zustand vs. Redux Toolkit
- **Selected:** TanStack Query v5 (server state) + Zustand (client UI state).
- **Rationale:** Separates server caching (deduplication, background refetching, cache invalidation) from purely transient UI state (modal open/closed, active wizard step) without boilerplate action-reducers.
- **Alternatives Rejected:** Redux Toolkit was rejected due to excessive boilerplate and conflation of server cache with client state.

---

## 4. Maintenance & Security Considerations

- **Long-Term Support (LTS):** All chosen foundation layers (Python 3.11, PostgreSQL 16, React 18, Nginx 1.26) have verified multi-year support lifecycles.
- **Automated Dependency Auditing:** CI pipelines run `pip-audit` for Python packages and `npm audit` for JavaScript packages on every pull request to detect known CVEs.
- **Minimal Docker Images:** Production Dockerfiles utilize Alpine Linux or Debian slim bases, with non-root runtime users (`USER 10001:10001`) to minimize the container attack surface.
