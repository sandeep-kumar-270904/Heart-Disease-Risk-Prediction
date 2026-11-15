# HeartXAI 2.0 — C4 Architecture: Component Diagram

**Document ID:** HXAI-ARCH-005  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved  
**Diagram Source:** [`docs/diagrams/c4_component_backend.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/c4_component_backend.puml)  

---

## 1. Backend Component Architecture Narrative

The Component diagram breaks down the **API Application Container** into its constituent software modules. It illustrates the strict separation of concerns across the **Routing Layer**, **Domain Service Layer**, **ML & Explainability Subsystem**, and **Data Access Layer**.

### Component Specifications
1. **Security & Auth Middleware:**
   - Extracts and cryptographically verifies `access_token` cookies.
   - Enforces Role-Based Access Control (RBAC) route guards (`require_role(["PATIENT"])`, `require_role(["CLINICIAN"])`, `require_role(["ADMIN"])`).
   - Applies per-IP rate limiting to thwart credential brute-forcing.
2. **APIRouter Controllers (`api/v1/routes/`):**
   - `auth`: Registration, login, logout, password resets.
   - `assessments`: 13-biomarker intake submission, validation, and historical time-series queries.
   - `inference`: Dual-target risk retrieval, TreeSHAP attributions, and counterfactual simulation.
   - `privacy`: Doctor consent grants, revocation, GDPR export, and account deletion.
   - `clinician`: Cohort review, granted patient chart access, and clinical note sign-off.
   - `admin`: Model telemetry, clinician credential queue, directory management, and audit log exploration.
   - `health`: Liveness (`/health/live`) and readiness (`/health/ready`) probes.
3. **Domain Service Layer (`services/`):**
   - Encapsulates pure business rules, transaction orchestration, and audit event dispatch.
   - Ensures controllers remain lean HTTP serialization wrappers.
4. **Machine Learning & Explainability Subsystem (`ml/`):**
   - Coordinates `StandardScaler` transformations, calibrated XGBoost inference, ACC/AHA ASCVD equations, TreeSHAP local attributions, and constrained L1-norm counterfactual solving.
5. **Data Access & Persistence Layer (`models/` & `core/database.py`):**
   - SQLAlchemy 2.0 ORM models defining foreign keys, indexes, cascades, and connection pooling.

---

## 2. Visual Component Diagram

```mermaid
graph TB
    subgraph SPAClient ["Single-Page Application"]
        SPA["React 18 / TypeScript SPA"]
    end

    subgraph BackendContainer ["FastAPI Backend Application Container"]
        Security["Security & Auth Middleware\n(Cookie Decoding, RBAC, Rate Limiting)"]

        subgraph Controllers ["Controllers (APIRouter Layer)"]
            C_Auth["Auth Controller\n(/api/v1/auth)"]
            C_Assess["Assessment Controller\n(/api/v1/assessments)"]
            C_XAI["Explainability Controller\n(/api/v1/inference)"]
            C_Privacy["Privacy & Consent Controller\n(/api/v1/privacy)"]
            C_Clinician["Clinician Controller\n(/api/v1/clinician)"]
            C_Admin["Governance Controller\n(/api/v1/admin)"]
        end

        subgraph Services ["Domain Service Layer"]
            S_Auth["Auth Service\n(Bcrypt, Token Generation)"]
            S_Assess["Assessment Service\n(Intake Orchestration, History Deltas)"]
            S_Privacy["Privacy Service\n(Grant Validation, Revocation)"]
            S_Audit["Audit Logging Service\n(Append-Only Log Writer)"]
        end

        subgraph MLSubsystem ["ML & Explainability Subsystem"]
            ML_Engine["Calibrated XGBoost & ASCVD Engine"]
            SHAP_Engine["TreeSHAP Explainer (C++ Core)"]
            CF_Solver["Constrained Counterfactual Solver"]
        end

        subgraph DataLayer ["Data Access & ORM Layer"]
            ORM["SQLAlchemy 2.0 Declarative Models"]
            Engine["Engine & Connection Pool"]
        end
    end

    subgraph ExternalResources ["Persistent Storage & Artifacts"]
        DB[("PostgreSQL Database")]
        ModelFile["Model Artifact (.joblib)"]
    end

    SPA -->|HTTPS / JSON / Cookies| Security
    Security --> Controllers

    C_Auth --> S_Auth
    C_Assess --> S_Assess
    C_XAI --> MLSubsystem
    C_Privacy --> S_Privacy
    C_Clinician --> S_Privacy
    C_Admin --> S_Audit

    S_Assess --> ML_Engine
    S_Assess --> SHAP_Engine
    C_XAI --> CF_Solver

    S_Auth --> ORM
    S_Assess --> ORM
    S_Privacy --> ORM
    S_Audit --> ORM
    ORM --> Engine
    Engine --> DB

    ML_Engine --> ModelFile
    SHAP_Engine --> ModelFile
```

---

## 3. Component Interaction & Transaction Isolation

- **ACID Transaction Isolation:** `AssessmentService` initiates a database transaction, persists the `assessments` record, executes `ML_Engine` and `SHAP_Engine` in-memory, writes the derived `inference_results` and `shap_explanations` rows, and commits the transaction atomically. If an exception occurs, the transaction rolls back cleanly, leaving zero dangling records.
- **Asynchronous Audit Decoupling:** Critical audit log rows are written within the transaction or flushed immediately following successful commit, ensuring comprehensive forensic traceability.
