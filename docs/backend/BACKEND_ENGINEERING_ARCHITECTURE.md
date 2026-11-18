# HeartXAI 2.0 — Backend Engineering Architecture

**Document ID:** `HX2-BE-001`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect, Application Security Architect & Lead Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001 through ADR-011, HXAI-ARCH-008  

---

## 1. Executive Summary & Architectural Vision

The **HeartXAI 2.0 Backend** is a high-performance, asynchronous, domain-driven modular monolith implemented in **Python 3.11+** using **FastAPI**, **Pydantic v2**, and **SQLAlchemy 2.0**.

It delivers explainable cardiovascular machine learning inferences (XGBoost + TreeSHAP + Counterfactuals), manages longitudinal clinical biomarkers, coordinates country-configurable healthcare directories, and enforces strict patient data isolation under a Zero Trust security paradigm.

### 1.1 Core Backend Engineering Tenets
1. **Clinical Epistemological Honesty:** The backend never outputs or persists diagnostic certainty. All inference contracts return and record **Angiographic CAD Association Likelihood**, explicit model version identifiers, training cohort provenance, and mathematical SHAP feature weights.
2. **Four-Layer Inward Dependency Flow:** Dependencies flow strictly inward from Transport $\rightarrow$ Services $\rightarrow$ Domain/ML $\rightarrow$ Repositories. Business logic is strictly isolated from HTTP transport frameworks and database ORM primitives.
3. **Async-First Execution:** Fully asynchronous I/O utilizing FastAPI, `asyncio`, and `asyncpg` for PostgreSQL connection pooling, guaranteeing sub-50ms P95 API response times.
4. **Defense-in-Depth Authorization & Patient Data Sovereignty:** Cryptographically verified JWT sessions stored in `HttpOnly`, `SameSite=Strict` cookies; server-enforced object-level ownership checks (`patient_id == current_user.id`); and strict consent grant validation before clinician data access.
5. **Country-Configurable Modular Adapters (ADR-011):** The backend does not hard-code single-country assumptions. Directory search, clinician verification registries, insurance guidance, emergency hotlines, and measurement unit normalization are orchestrated via country-specific integration adapters.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   HEARTXAI 2.0 BACKEND ARCHITECTURE                   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. TRANSPORT & API LAYER (FastAPI APIRouter, Middlewares, Deps)        │
│    - OpenAPI 3.1 endpoints, CORS, RateLimiter, RequestContextMiddleware│
│    - Cookie Session Auth, CSRF double-submit validation                │
├────────────────────────────────────────────────────────────────────────┤
│ 2. DOMAIN SERVICE LAYER (Pure Business Logic & Unit of Work)           │
│    - AuthService, AssessmentService, ExplainabilityService             │
│    - DirectoryService, ClinicianReviewService, AuditService            │
├────────────────────────────────────────────────────────────────────────┤
│ 3. ML & STATISTICAL EXPLAINABILITY ENGINE (Inference & XAI)            │
│    - XGBoost Model Runner, TreeSHAP Attributor, Counterfactual Engine │
│    - Feature Vector Preprocessor & Median Imputer                      │
├────────────────────────────────────────────────────────────────────────┤
│ 4. DATA ACCESS LAYER (SQLAlchemy 2.0, Asyncpg, PostgreSQL 16)         │
│    - Domain Repositories, Unit of Work, Transaction Context            │
│    - Row-Level Security (RLS) policies & Immutable Audit Logs          │
├────────────────────────────────────────────────────────────────────────┤
│ 5. COUNTRY ADAPTER INTEGRATION SUITE (ADR-011)                         │
│    - India (NMC Registry, NABH Hospitals, 112/102 Emergency)          │
│    - United States (State Boards, CMS, 911 Emergency)                  │
│    - United Kingdom (GMC Registry, NHS 999/111)                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Four-Layer Domain-Driven Architecture

### Layer 1: API & Transport Layer (`app/api/`)
- **Responsibilities:** HTTP protocol handling, route definition, request deserialization, dependency injection (`app/api/deps.py`), rate-limit enforcement, and standardized Stripe-style error formatting.
- **Constraints:** Zero business logic; routes merely parse inputs, call service methods, and return serialized Pydantic responses.

### Layer 2: Domain Service Layer (`app/services/` & `app/modules/*/services/`)
- **Responsibilities:** Core application rules, transaction orchestration, permission enforcement, multi-entity workflows (e.g., creating an assessment, computing inference, generating SHAP, and writing audit logs in a single transactional Unit of Work).
- **Constraints:** Completely independent of HTTP request/response objects; methods accept typed domain parameters and return domain models or exceptions.

### Layer 3: Machine Learning Subsystem (`app/ml/`)
- **Responsibilities:** Model artifact loading, version verification, preprocessing pipelines, inference execution, TreeSHAP contribution generation, and constrained counterfactual optimization.
- **Constraints:** Stateless execution; operations are strictly reproducible given the model artifact checksum and raw clinical feature vectors.

### Layer 4: Data Access & Repositories (`app/repositories/` & `app/database/`)
- **Responsibilities:** Database session lifecycle, query generation via SQLAlchemy 2.0 select statements, connection pool management, and relational integrity enforcement.
- **Constraints:** Encapsulates all raw database queries; domain services interact exclusively with repository abstractions.

---

## 3. Transaction Management & Unit of Work Pattern

To guarantee ACID compliance across complex operations (such as submitting an assessment, persisting the 13 raw clinical inputs, recording the model inference score, inserting 13 SHAP feature attributions, and logging an audit event), HeartXAI 2.0 utilizes an **Asynchronous Unit of Work (UoW)** pattern:

```python
class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.assessments = AssessmentRepository(self.session)
        self.inferences = InferenceRepository(self.session)
        self.audit_logs = AuditLogRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
```

* **Outcome:** If an exception occurs while persisting SHAP feature vectors, the entire database transaction rolls back, preventing partial assessment entries or orphaned prediction records.

---

## 4. Asynchronous Concurrency & Resource Governance

- **Runtime Engine:** Python 3.11 `asyncio` event loop running under `uvicorn` with `httptools` and `uvloop`.
- **Database Driver:** `asyncpg` — the highest performance asynchronous PostgreSQL driver in Python.
- **Connection Pool Configuration:**
  - `pool_size = 20` persistent connections.
  - `max_overflow = 10` burst connections.
  - `pool_timeout = 30` seconds.
  - `pool_recycle = 1800` seconds (30 minutes) to eliminate stale connections.
- **CPU-Bound ML Isolation:** Model inference and SHAP attribution tasks that consume sustained CPU cycles are executed in an `asyncio.to_thread()` worker pool, ensuring the main async event loop remains responsive to incoming HTTP requests ($< 50\text{ms}$ latency).

---

## 5. Global Country-Configurable Architecture (ADR-011)

In strict accordance with approved architecture requirement **ADR-011**, all external healthcare dependencies are decoupled via the **Country Adapter Pattern**:

```
                              [ DirectoryService ]
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   ICountryAdapter (ABC)   │
                         └─────────────┬─────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
  [ IndiaAdapter ]              [ USAAdapter ]                [ UKAdapter ]
  • NMC Registry API            • State Boards / NPI          • GMC Register
  • NABH Facilities             • CMS Hospital Compare        • NHS England Directory
  • Emergency: 112 / 102        • Emergency: 911              • Emergency: 999 / 111
  • Default: mg/dL, mmHg        • Default: mg/dL, mmHg        • Default: mmol/L, mmHg
```

- Each country adapter implements a shared interface defining:
  - `search_doctors(query, city, specialty)`
  - `search_hospitals(city, has_cardiac_emergency)`
  - `verify_physician_license(license_number, authority)`
  - `get_insurance_guidance()`
  - `get_emergency_hotlines()`
- If a country registry is offline or unverified, the adapter gracefully falls back to a verified static directory cache without crashing the service.
