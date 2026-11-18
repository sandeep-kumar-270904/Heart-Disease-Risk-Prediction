# HeartXAI 2.0 — Backend Project Structure & Modular Organization

**Document ID:** `HX2-BE-002`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect & Lead Systems Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001, ADR-011, HXAI-ARCH-008  

---

## 1. Overview & Structural Design Philosophy

The HeartXAI 2.0 backend follows a **Modular Monolith Architecture** organized by both **Domain Feature Modules** and **Clean Layered Boundaries**. 

This structure ensures that:
1. **Domain Isolation:** Each feature slice (`assessments`, `explainability`, `doctors`) encapsulates its own business logic, DTO schemas, and services.
2. **Strict Inward Dependency Flow:** Outer layers (HTTP routing) depend on services, which depend on repositories and domain models. Core utilities and database configurations never depend on high-level route handlers.
3. **Circular Import Prevention:** Clear structural separation between SQLAlchemy ORM entities (`models/`), Pydantic DTO schemas (`schemas/`), and business rules (`services/`) eliminates Python circular reference traps.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   BACKEND LAYERED TOPOLOGY                             │
├────────────────────────────────────────────────────────────────────────┤
│ 1. app/api/          ── HTTP Handlers, Routing, Middleware, Deps       │
│ 2. app/modules/      ── Domain Features (assessments, explainability)  │
│ 3. app/services/     ── Cross-Domain Orchestration & Business Logic    │
│ 4. app/ml/           ── XGBoost Pipeline, TreeSHAP, Median Imputer     │
│ 5. app/repositories/ ── SQLAlchemy 2.0 Data Access & Query Builders   │
│ 6. app/models/       ── Declarative ORM Database Entities              │
│ 7. app/schemas/      ── Pydantic v2 Serialization & Validation Schemas │
│ 8. app/core/         ── Security, Crypto, Config, Exceptions, Database │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Backend File & Directory Hierarchy

```
backend/
├── alembic/                         # Database schema migrations
│   ├── env.py                       # Alembic migration runner (imports Base & async engine)
│   ├── script.py.mako               # Template for versioned migrations
│   └── versions/                    # Linear, immutable migration scripts
│       ├── 001_initial_schema.py
│       ├── 002_add_audit_indexes.py
│       └── 003_add_country_adapters.py
│
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application factory, lifespan, middleware
│   │
│   ├── config/                      # Application configuration & environment parsing
│   │   ├── __init__.py
│   │   ├── settings.py              # Pydantic Settings (DATABASE_URL, JWT_SECRET, etc.)
│   │   └── constants.py             # Global constants (model version, units, thresholds)
│   │
│   ├── core/                        # Cross-cutting foundational infrastructure
│   │   ├── __init__.py
│   │   ├── database.py              # Async SQLAlchemy engine & sessionmaker
│   │   ├── security.py              # Argon2id password hashing, JWT encode/decode, CSRF
│   │   ├── exceptions.py            # Domain exceptions (EntityNotFound, UnauthorizedAccess)
│   │   ├── logging.py               # Structured JSON logging (correlation ID injection)
│   │   └── unit_of_work.py          # Asynchronous Unit of Work context manager
│   │
│   ├── middleware/                  # HTTP request/response pipeline middlewares
│   │   ├── __init__.py
│   │   ├── correlation.py           # Injects X-Correlation-ID into context and response
│   │   ├── security_headers.py      # HSTS, CSP, X-Frame-Options, X-Content-Type-Options
│   │   ├── rate_limiter.py          # Sliding-window in-memory / Redis rate limit middleware
│   │   └── error_handler.py         # Catches unhandled exceptions and returns Stripe envelope
│   │
│   ├── api/                         # Transport layer & HTTP routing
│   │   ├── __init__.py
│   │   ├── deps.py                  # FastAPI dependency injection (get_db, current_user, etc.)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py               # Aggregates all v1 feature routers
│   │       └── routes/              # Route controllers
│   │           ├── auth.py          # POST /auth/login, /register, /logout, /refresh
│   │           ├── patients.py      # GET/PUT /patients/me, /vitals, /consent
│   │           ├── assessments.py   # POST /assessments, GET /assessments, GET /:id
│   │           ├── inference.py     # GET /assessments/:id/shap, POST /scenarios
│   │           ├── clinician.py     # GET /clinician/cohort, POST /notes
│   │           ├── directory.py     # GET /directory/doctors, /hospitals, /insurance
│   │           ├── reports.py       # GET /reports/assessments/:id/pdf
│   │           ├── admin.py         # GET /admin/telemetry, /audit-logs, /models
│   │           └── health.py        # GET /health/live, GET /health/ready
│   │
│   ├── models/                      # SQLAlchemy 2.0 ORM Entities
│   │   ├── __init__.py
│   │   ├── base.py                  # DeclarativeBase with UUID PK & timestamp mixins
│   │   ├── user.py                  # User entity (roles: PATIENT, CLINICIAN, ADMIN)
│   │   ├── patient_profile.py       # Patient demographics, baseline history, emergency contact
│   │   ├── assessment.py            # Assessment entity storing 13 raw clinical inputs
│   │   ├── inference_result.py      # Prediction likelihood, CI, model hash, cohort metadata
│   │   ├── shap_explanation.py      # Individual feature attribution weights and directions
│   │   ├── counterfactual.py        # Derived hypothetical scenario parameter sets
│   │   ├── clinician_grant.py       # Patient-to-doctor consent authorization grants
│   │   ├── clinical_note.py         # Verified clinician consultation notes
│   │   └── audit_log.py             # Immutable append-only security and access audit log
│   │
│   ├── schemas/                     # Pydantic v2 DTOs (Request / Response validation)
│   │   ├── __init__.py
│   │   ├── common.py                # Envelope, PaginationParams, PaginatedResponse
│   │   ├── auth.py                  # LoginRequest, RegisterRequest, UserProfileResponse
│   │   ├── assessment.py            # AssessmentCreateDto, AssessmentDetailResponse
│   │   ├── explainability.py        # ShapExplanationResponse, FeatureImpactDto
│   │   ├── counterfactual.py        # ScenarioSimulationRequest, ScenarioResultDto
│   │   ├── directory.py             # DoctorDto, HospitalDto, InsuranceGuideDto
│   │   ├── admin.py                 # TelemetryResponse, ClinicianVerificationDto, ModelDto
│   │   └── errors.py                # Standardized Stripe-style error schemas
│   │
│   ├── repositories/                # Data access layer (SQLAlchemy query abstractions)
│   │   ├── __init__.py
│   │   ├── base.py                  # Generic repository (CRUD, pagination, exists)
│   │   ├── user_repo.py             # User lookup by email, session updates
│   │   ├── assessment_repo.py       # Filtered assessment history, latest by patient
│   │   ├── inference_repo.py        # Inference result & SHAP joins
│   │   ├── grant_repo.py            # Consent grant verification and expiry checks
│   │   └── audit_repo.py            # Append-only audit trail logging
│   │
│   ├── services/                    # Domain business logic & orchestration
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Registration, password verify, session management
│   │   ├── assessment_service.py    # Clinical validation, unit conversion, intake orchestration
│   │   ├── inference_service.py     # Coordinates ML runner, SHAP attribution, and persistence
│   │   ├── counterfactual_service.py# Biological clamping & "what-if" delta simulation
│   │   ├── directory_service.py     # Routes queries through active country adapter
│   │   ├── report_service.py        # Compiles and streams PDF consultation aids
│   │   ├── clinician_service.py     # Licensure verification, chart review authorization
│   │   └── audit_service.py         # Logs immutable security events
│   │
│   ├── integrations/                # Country-specific directory & verification adapters
│   │   ├── __init__.py
│   │   ├── base.py                  # ICountryAdapter abstract base class
│   │   ├── india_adapter.py         # NMC registry, NABH hospitals, PM-JAY guides
│   │   ├── usa_adapter.py           # State boards, CMS hospital data, 911 hotlines
│   │   └── uk_adapter.py            # GMC register, NHS England directories
│   │
│   ├── ml/                          # Machine Learning & Explainability Engine
│   │   ├── __init__.py
│   │   ├── pipeline.py              # Model artifact loader, checksum validator, inference runner
│   │   ├── preprocessor.py          # Feature normalization, median imputation for missing ca/thal
│   │   ├── explainer.py             # TreeSHAP explainer instance & attribution parser
│   │   ├── counterfactual_engine.py # Constrained optimization solver for what-if scenarios
│   │   └── artifacts/               # Serialized model artifacts (.joblib / .json)
│   │       ├── cleveland_xgboost_v2.4.1.json
│   │       ├── shap_background_summary.joblib
│   │       └── checksums.sha256     # Cryptographic verification manifest
│   │
│   └── tasks/                       # Asynchronous background tasks
│       ├── __init__.py
│       ├── email_tasks.py           # Verification and password reset delivery
│       └── audit_tasks.py           # Batch log archiving and integrity checksum checks
│
├── tests/                           # Automated testing suites
│   ├── conftest.py                  # Pytest fixtures (async client, test DB session, test models)
│   ├── unit/                        # Fast isolated unit tests (converters, validators, schemas)
│   ├── integration/                 # End-to-end API tests against real database
│   ├── security/                    # Cross-user authorization tests, OWASP injections, CSRF
│   └── contract/                    # OpenAPI 3.1 schema consistency assertions
│
├── scripts/                         # Operational & maintenance utilities
│   ├── seed_dev_data.py             # Generates synthetic local development test data
│   ├── verify_model_artifacts.py    # Validates SHA256 hashes of model files
│   └── export_openapi_schema.py     # Generates openapi.json for frontend contract sync
│
├── pyproject.toml                   # Poetry / Pip project dependencies and tool configs
└── alembic.ini                      # Alembic CLI configuration
```

---

## 3. Module Boundaries & Dependency Flow Rules

1. **Inward-Only Import Rule:**
   - Routes (`api/v1/routes/*`) may import from `services/`, `schemas/`, `api/deps.py`.
   - Services (`services/*`) may import from `repositories/`, `models/`, `schemas/`, `ml/`, `integrations/`, `core/`.
   - Repositories (`repositories/*`) may import from `models/`, `core/database.py`.
   - Models (`models/*`) **must never** import from services, schemas, or routes.
2. **Feature Encapsulation:**
   - Business rules governing cardiovascular risk assessment reside strictly in `services/assessment_service.py` and `services/inference_service.py`. The HTTP route controller simply delegates execution and handles status code mappings.
3. **No Database Access in Route Handlers:**
   - Route handlers **never** execute raw SQLAlchemy queries (`db.execute(...)` or `db.scalars(...)`). All database reads and writes are encapsulated behind named repository methods.
