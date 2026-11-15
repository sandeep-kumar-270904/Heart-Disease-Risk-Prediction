# HeartXAI 2.0 — C4 Architecture: Container Diagram

**Document ID:** HXAI-ARCH-004  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved  
**Diagram Source:** [`docs/diagrams/c4_container.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/c4_container.puml)  

---

## 1. Container Architecture Narrative

The Container diagram decomposes the HeartXAI 2.0 system into five executable, deployable architectural units. Each container encapsulates distinct runtime responsibilities, data storage models, and technology stacks.

### Container Inventory
1. **Single-Page Application (SPA):**
   - *Technology:* React 18/19, TypeScript (strict mode), Vite, Tailwind CSS, Lucide Icons, Recharts.
   - *Role:* Delivers the accessible, responsive user interface. Executes client-side routing, Zod schema validation for intake forms, dynamic SVG rendering for TreeSHAP waterfalls, interactive what-if sliders, and longitudinal time-series telemetry charts.
2. **API Application Gateway & Services:**
   - *Technology:* Python 3.11+, FastAPI, Pydantic v2, Starlette, Uvicorn ASGI.
   - *Role:* Serves RESTful endpoints under `/api/v1`, enforces RBAC authorization via `HttpOnly` JWT cookie decoding, validates input biomarker ranges, coordinates ACID transactions, and emits structured JSON audit logs.
3. **ML & Explainability Subsystem (In-Process Runtime):**
   - *Technology:* Scikit-learn 1.3+, XGBoost 3.1+, SHAP (TreeExplainer C++ core), NumPy, SciPy.
   - *Role:* Executes standardized feature transformations (`StandardScaler`), computes calibrated posterior CAD probabilities $P(\text{CAD} \ge 50\%)$, evaluates 2013 ACC/AHA 10-year prospective ASCVD equations, computes exact local TreeSHAP feature attributions, and solves constrained counterfactual lifestyle optimizations.
4. **Relational Database Engine:**
   - *Technology:* PostgreSQL 15+ (with automated SQLite fallback for offline developer agility).
   - *Role:* Provides durable, ACID-compliant relational persistence for user credentials, patient profiles, assessments, inferences, SHAP attributions, doctor grants, clinical notes, directories, and immutable audit logs.
5. **Model Artifact Store:**
   - *Technology:* Local container volume / filesystem mount.
   - *Role:* Stores cryptographically verified serialized pipeline artifacts (`heartxai_model_v2.0.0.joblib`). Verified via SHA-256 hash at backend initialization.

---

## 2. Visual Container Diagram

```mermaid
graph TB
    subgraph Users ["Actors"]
        Patient["Patient [Person]"]
        Doctor["Clinician [Person]"]
        Admin["Administrator [Person]"]
    end

    subgraph SystemBoundary ["HeartXAI 2.0 Platform"]
        SPA["Single-Page Application (SPA)\n[Container: React 18, TypeScript, Vite, Tailwind]\nDelivers accessible clinical UI, SVG SHAP waterfall charts, interactive what-if sliders, and intake wizard."]
        API["API Application & Domain Services\n[Container: Python 3.11, FastAPI, Pydantic v2]\nHandles REST endpoints, RBAC authentication, input validation, transaction boundaries, and audit logging."]
        ML["ML & Explainability Subsystem\n[Container: Scikit-learn, XGBoost, TreeSHAP C++]\nComputes calibrated CAD probabilities, 10-yr ASCVD equations, TreeSHAP attributions, and counterfactuals."]
        DB[("Relational Database\n[Container: PostgreSQL 15+]\nStores users, assessments, inferences, SHAP attributions, consent grants, and immutable audit logs.")]
        ModelStore["Model Artifact Storage\n[Container: Local Volume]\nStores versioned model pipeline (.joblib) verified via SHA-256."]
    end

    Patient -->|Visits app, submits intake, explores what-if sliders| SPA
    Doctor -->|Logs in, reviews authorized charts, signs notes| SPA
    Admin -->|Inspects audit logs, monitors model health| SPA

    SPA -->|HTTPS / JSON / HttpOnly JWT Cookies| API
    API -->|In-Process Python Method Calls (Zero IPC)| ML
    API -->|SQL queries over connection pool (asyncpg/psycopg2)| DB
    ML -->|Loads and verifies artifact via SHA-256 on boot| ModelStore
```

---

## 3. Communication Protocols & Data Envelopes

- **Client-to-API:** Asynchronous HTTP/2 or HTTPS over port 443. All payloads encoded in UTF-8 JSON. Authentication maintained via `HttpOnly`, `Secure`, `SameSite=Strict` cookies.
- **API-to-ML:** In-process function invocation. Input vectors passed as NumPy arrays ($1 \times 13$). Outputs returned as typed Python dataclasses/dictionaries. Zero network overhead ($< 25\text{ms}$ latency).
- **API-to-Database:** Parameterized SQL queries executed over an active SQLAlchemy connection pool (max pool size: 20, overflow: 10) connecting to PostgreSQL port 5432 with TLS encryption.
