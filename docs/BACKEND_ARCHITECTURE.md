# HeartXAI 2.0 — Backend Architecture Specification

**Document ID:** HXAI-ARCH-008  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved  
**Author:** Senior Backend Architect & Principal Systems Engineer  

---

## 1. Backend Architecture Philosophy & Layered Structure

The HeartXAI 2.0 backend is designed as a **Domain-Driven Modular Monolith** implemented in Python 3.11+ using the FastAPI framework. It enforces a strict **Four-Layer Architecture** where dependencies flow exclusively inward:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. API & Transport Layer (FastAPI APIRouters, Middleware)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Domain Service Layer (Pure Business Logic & Orchestration)│
└──────────────────────────────┬──────────────────────────────┘
                               │ calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ML & Explainability Subsystem (Inference, TreeSHAP, CF)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ calls
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Data Access Layer (SQLAlchemy 2.0 ORM, Repositories, DB) │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Layout & Module Organization

```
backend/
├── alembic/                    # Database migration environment
│   ├── versions/               # Linear, versioned migration scripts
│   ├── env.py                  # Alembic runtime configuration
│   └── script.py.mako          # Migration template
├── app/
│   ├── api/                    # API Transport Layer
│   │   ├── deps.py             # FastAPI dependency injection (get_db, current_user, require_role)
│   │   └── v1/
│   │       ├── api.py          # Top-level v1 router aggregator
│   │       └── routes/         # Modular endpoint routers
│   │           ├── auth.py         # Registration, login, logout, me
│   │           ├── assessments.py  # Intake submission, results, history
│   │           ├── inference.py    # XAI, SHAP attributions, counterfactual simulation
│   │           ├── privacy.py      # Doctor grants, revocation, GDPR export, erasure
│   │           ├── clinician.py    # Cohort review, patient chart access, clinical notes
│   │           ├── directory.py    # Doctors, hospitals, insurance guides
│   │           ├── admin.py        # System telemetry, audit logs, clinician queue
│   │           └── health.py       # /health/live, /health/ready probes
│   ├── core/                   # Cross-Cutting Infrastructure
│   │   ├── config.py           # Pydantic Settings & environment variables
│   │   ├── country_profile.py  # Global Country Profile Registry (IN, US, GB, DEFAULT)
│   │   ├── unit_converter.py   # Deterministic BiomarkerUnitConverter (mg/dL <-> mmol/L)
│   │   ├── database.py         # SQLAlchemy engine, SessionLocal, get_db
│   │   ├── security.py         # Argon2id password hashing, JWT generation & verification
│   │   └── logging.py          # Structured JSON logging configuration
│   ├── models/                 # Data Access Layer (SQLAlchemy 2.0 Declarative Models)
│   │   ├── base.py             # UUID primary key & timestamp mixins
│   │   ├── user.py             # User (with country_code), PatientProfile (with preferred_units)
│   │   ├── assessment.py       # Assessment, InferenceResult, ShapExplanation, CounterfactualProfile
│   │   ├── consent.py          # DoctorGrant, ClinicalNote
│   │   ├── directory.py        # Doctor, Hospital, InsurancePolicy, EducationalResource
│   │   └── audit.py            # AuditLog, ModelRegistry
│   ├── schemas/                # Pydantic v2 Request & Response Data Contracts
│   │   ├── common.py           # Standard error envelopes, pagination models
│   │   ├── user.py             # UserCreate, UserResponse, LoginRequest, ProfileUpdate
│   │   ├── assessment.py       # AssessmentCreate, BiomarkerVector, AssessmentResponse
│   │   ├── inference.py        # PredictionResponse, ShapExplanationSchema, CounterfactualSchema
│   │   ├── privacy.py          # DoctorGrantCreate, DoctorGrantResponse, ConsentRevoke
│   │   └── directory.py        # DoctorResponse, HospitalResponse, InsuranceResponse
│   ├── services/               # Domain Business Logic Layer
│   │   ├── auth_service.py     # Authentication, password verification, registration
│   │   ├── assessment_service.py # Intake orchestration, unit normalization, delta calculations
│   │   ├── privacy_service.py  # Consent verification, doctor grant lifecycle
│   │   ├── report_service.py   # Clinical visit briefing compilation (WeasyPrint)
│   │   ├── audit_service.py    # Immutable append-only audit log writer
│   │   └── adapters/           # Country-Configurable Integration Adapters (ADR-011)
│   │       ├── base.py             # IDoctorDirectoryAdapter, IPhysicianVerificationAdapter
│   │       ├── india_adapter.py    # India PIN codes, PMJAY open data, NMC document queue
│   │       ├── us_adapter.py       # US ZIP codes, CMS hospital data, CMS NPPES API
│   │       └── global_adapter.py   # OSM Overpass, universal document upload queue
│   ├── ml/                     # Machine Learning & Explainability Engine
│   │   ├── artifacts/          # Serialized pipelines (heartxai_model_v2.0.0.joblib)
│   │   ├── preprocessor.py     # Feature scaling & OOD bounds checking
│   │   ├── predictor.py        # Calibrated XGBoost & ACC/AHA ASCVD execution
│   │   ├── explainer.py        # TreeSHAP C++ tree traversal & additivity assertion
│   │   └── counterfactual.py   # Constrained L1-norm optimization solver
│   └── main.py                 # ASGI application factory, CORS, exception handlers
├── tests/                      # Automated Test Suite (Google Testing Pyramid)
│   ├── conftest.py             # In-memory test database, test client, user fixtures
│   ├── test_database_models.py # ORM integrity, constraints, cascades
│   ├── test_security.py        # Bcrypt, JWT lifecycle, token tampering
│   ├── test_api_health.py      # Health probes, OpenAPI schema generation
│   ├── test_auth_workflow.py   # Registration, login, role restrictions
│   ├── test_ml_pipeline.py     # Calibration, determinism, ASCVD equations
│   └── test_xai_invariance.py  # TreeSHAP additivity, counterfactual bounds
├── alembic.ini                 # Alembic configuration
├── pyproject.toml              # Pytest, Ruff, and Python project metadata
└── requirements.txt            # Pinned dependencies
```

---

## 3. Layered Communication & Architectural Contracts

### 3.1 API Transport Layer
- **Responsibility:** Parses incoming HTTP requests, extracts cookies/headers, invokes Pydantic schema validation, and delegates business execution to domain services.
- **Rules:** Controllers contain **zero database query logic** and **zero machine learning code**. Controllers only receive dependencies via FastAPI's `Depends()` injection.

### 3.2 Domain Service Layer
- **Responsibility:** Encapsulates business logic, enforces business invariants (e.g. verifying patient ownership before granting doctor access), coordinates multi-step database mutations, and dispatches audit events.
- **Rules:** Services operate on domain models and Pydantic schemas. They do not know about HTTP status codes, request cookies, or client transport details.

### 3.3 Data Access Layer
- **Responsibility:** Manages database sessions, constructs parameterized SQL queries, enforces relational constraints, and manages connection pooling.
- **Rules:** All database queries utilize SQLAlchemy 2.0 select syntax (`select(User).where(...)`). Direct raw SQL execution is prohibited to eliminate SQL injection vulnerabilities.

---

## 4. Authentication, Authorization & Security Architecture

### 4.1 Dependency-Injected Authentication (`deps.py`)
```
Request Ingress
  │
  ▼
get_current_user Dependency
  ├──► Extract "access_token" cookie
  ├──► Decode JWT via decode_access_token()
  ├──► Validate signature & expiration (HS256)
  ├──► Query User from database by sub (UUID)
  └──► Return User object OR raise HTTPException(401)
```

### 4.2 Role-Based Access Control (RBAC)
Role authorization is enforced via parametric dependencies:
- `require_role(["PATIENT"])`: Permits Patient accounts.
- `require_role(["CLINICIAN"])`: Permits Clinicians whose `clinician_status == "VERIFIED"`.
- `require_role(["ADMIN"])`: Permits verified Administrator accounts.
- Violation triggers an immediate HTTP 403 Forbidden with security logging.

---

## 5. Centralized Error Handling & Structured Logging

### 5.1 Stripe-Modeled Structured Error Envelopes
All API errors return a standard, machine-readable JSON structure:
- **Validation Errors (HTTP 422):** Returns specific parameter names (`param`), validation failure codes (`code`), and clear clinical guidance (`message`).
- **Authorization Errors (HTTP 403):** Returns machine-readable error type `forbidden_error` with actionable user explanation.
- **Resource Not Found (HTTP 404):** Returns clean entity not found descriptors.
- **Internal Errors (HTTP 500):** Generic user-safe message; full exception stack trace logged internally with correlation `request_id`.

### 5.2 Request Correlation & Structured Logging
1. Application middleware generates a UUIDv4 `request_id` for every incoming HTTP request.
2. `request_id` is injected into the logging context (`structlog` / logging filter) and returned to the client in the `X-Request-ID` response header.
3. Every log entry contains `timestamp`, `level`, `request_id`, `endpoint`, `duration_ms`, and `message`.

---

## 6. Background Task Processing

For operations that should not block the synchronous HTTP response cycle (such as flushing non-critical security audit trails or sending transactional email notifications), the backend utilizes FastAPI's native `BackgroundTasks` framework.

Because workers are stateless and in-process, `BackgroundTasks` execute immediately upon response delivery without requiring external Celery / Redis worker clusters, preserving our low-complexity operational footprint.
