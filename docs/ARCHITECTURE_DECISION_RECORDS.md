# HeartXAI 2.0 — Architecture Decision Records (ADRs)

**Document ID:** HXAI-ARCH-002  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved / Core Architectural Baseline  
**Author:** Principal Software Architect & Lead Systems Analyst  

---

## Index of Architecture Decision Records

| ADR ID | Decision Title | Status | Date |
| :--- | :--- | :--- | :--- |
| **ADR-001** | Macro Architecture: Modular Monolith vs Microservices | **APPROVED** | 2026-11-16 |
| **ADR-002** | Frontend Stack: React 18/19 SPA with Vite vs Next.js Fullstack | **APPROVED** | 2026-11-16 |
| **ADR-003** | Backend Runtime: Python 3.11+ FastAPI vs Node.js / Go | **APPROVED** | 2026-11-16 |
| **ADR-004** | Persistence Engine: PostgreSQL with Dual-Dialect SQLite Fallback | **APPROVED** | 2026-11-16 |
| **ADR-005** | ML Serving Architecture: In-Process Serialized Pipeline vs Model Server | **APPROVED** | 2026-11-16 |
| **ADR-006** | Explainable AI Technique: Exact C++ TreeSHAP vs Model-Agnostic LIME | **APPROVED** | 2026-11-16 |
| **ADR-007** | Session & Security Model: HttpOnly SameSite=Strict Cookies vs LocalStorage | **APPROVED** | 2026-11-16 |
| **ADR-008** | Doctor-Patient Authorization: Explicit Time-Bounded Grants vs Open Browsing | **APPROVED** | 2026-11-16 |
| **ADR-009** | Counterfactual Optimization: Constrained Clinical L1 Step Search vs Unconstrained | **APPROVED** | 2026-11-16 |
| **ADR-010** | Deployment Topology: Multi-Stage Docker Compose vs Distributed Kubernetes | **APPROVED** | 2026-11-16 |

---

### ADR-001: Macro Architecture — Modular Monolith vs. Microservices
- **Context:** HeartXAI 2.0 is being developed by a solo principal engineer. The platform requires high clinical data integrity, strict ACID transactions, and sub-300ms inference latency across multiple interconnected modules (auth, intake, inference, XAI, counterfactuals, audit).
- **Problem:** What overarching architectural style best balances developer velocity, operational reliability, data consistency, and performance?
- **Options Considered:**
  1. *Option A:* Microservices architecture with independent containerized services communicating over HTTP/gRPC or Kafka message broker.
  2. *Option B:* Modular Monolith with strict internal domain boundaries, shared in-process memory, and unified database transactions.
  3. *Option C:* Serverless Functions (AWS Lambda / Cloud Functions).
- **Decision:** **Option B: Modular Monolith**.
- **Reasoning:** Microservices introduce massive operational overhead (service discovery, distributed tracing, event bus management, eventual consistency bugs, multi-repo or complex mono-repo build pipelines). In healthcare, multi-entity mutations (Assessment $\rightarrow$ Inference $\rightarrow$ SHAP $\rightarrow$ Audit) require immediate ACID consistency. A modular monolith allows clean domain boundaries while executing in a single process with zero network IPC serialization latency.
- **Consequences:** Codebase lives in a single repository; fast local execution; sub-second unit test runs; atomic database transactions. If horizontal scaling is required, the entire stateless backend container scales behind Nginx.
- **Risks:** Developers must enforce module boundaries discipline to prevent spaghetti imports.
- **Alternatives Rejected:** Option A (Microservices) rejected due to excessive distributed overhead for a single-engineer project; Option C (Serverless) rejected due to cold-start latency penalties ($> 2.5\text{s}$) on heavy Python ML libraries.

---

### ADR-002: Frontend Architecture — React 18/19 SPA with Vite vs. Next.js Fullstack
- **Context:** The frontend requires complex, interactive client-side widgets: SVG SHAP waterfall plots, real-time debounced what-if sliders, multi-step intake wizards, and responsive time-series charts.
- **Problem:** Should the frontend be built as a decoupled Single-Page Application (SPA) or a Server-Side Rendered (SSR) full-stack framework like Next.js?
- **Options Considered:**
  1. *Option A:* React SPA with TypeScript, Vite, and Tailwind CSS.
  2. *Option B:* Next.js 14/15 App Router with Node.js SSR.
- **Decision:** **Option A: React 18/19 SPA with Vite and Tailwind CSS**.
- **Reasoning:** HeartXAI 2.0 is a highly interactive, authenticated medical application. Core prediction and explanation logic runs on a Python FastAPI backend. Using Next.js would require running and deploying two separate backend runtimes (Node.js for SSR + Python for ML), doubling deployment complexity. A pure static SPA compiled by Vite can be served directly from Nginx with sub-50ms caching, letting the browser handle interactive rendering.
- **Consequences:** Eliminates Node.js production runtime; lightning-fast Vite Hot Module Replacement (HMR); frontend builds to pure static HTML/JS/CSS assets.
- **Risks:** Initial bundle load must be optimized with code-splitting (`React.lazy`) to prevent slow first contentful paint on mobile.
- **Alternatives Rejected:** Next.js rejected because SSR provides minimal benefit for an authenticated clinical application while introducing multi-runtime deployment friction.

---

### ADR-003: Backend Runtime — Python 3.11+ FastAPI vs. Node.js / Go
- **Context:** The backend serves REST APIs, enforces RBAC, coordinates database transactions, and executes machine learning inference pipelines (Scikit-Learn, XGBoost, SHAP).
- **Problem:** Which backend language and framework provides the highest performance while natively executing Python-based ML and XAI libraries?
- **Options Considered:**
  1. *Option A:* Python 3.11+ with FastAPI, Starlette, and Pydantic v2.
  2. *Option B:* Node.js / NestJS calling a separate Python ML service over HTTP/gRPC.
  3. *Option C:* Go (Golang) calling Python over IPC.
- **Decision:** **Option A: Python 3.11+ with FastAPI**.
- **Reasoning:** Scikit-learn, XGBoost, and SHAP are fundamentally Python-native ecosystems with optimized C/C++ backend bindings. FastAPI is built on Starlette and Pydantic v2 (compiled in Rust), delivering throughput competitive with Node.js and Go while allowing zero-IPC, in-process execution of ML models.
- **Consequences:** Single runtime for web API, data persistence, and ML inference. Automatic OpenAPI 3.1 interactive documentation generation.
- **Risks:** CPU-bound ML computations must be kept efficient ($< 30\text{ms}$) to avoid blocking the asyncio event loop.
- **Alternatives Rejected:** Node.js and Go rejected because separating the API from the ML pipeline introduces redundant network serialization and doubles container footprint.

---

### ADR-004: Persistence Engine — PostgreSQL with Dual-Dialect SQLite Fallback
- **Context:** The application stores relational data with strict parent-child constraints (`users` $\rightarrow$ `assessments` $\rightarrow$ `inference_results` $\rightarrow$ `shap_explanations`).
- **Problem:** What database engine ensures production reliability while permitting frictionless local developer agility?
- **Options Considered:**
  1. *Option A:* PostgreSQL 15+ exclusively.
  2. *Option B:* Dual-Dialect SQLAlchemy 2.0 architecture: PostgreSQL default for Docker/production, automated SQLite fallback for local developer testing.
  3. *Option C:* MongoDB / Document Store.
- **Decision:** **Option B: Dual-Dialect SQLAlchemy 2.0 with PostgreSQL production default and SQLite fallback**.
- **Reasoning:** Standardizing on standard SQL datatypes via SQLAlchemy 2.0 and Alembic allows the system to target PostgreSQL 15+ for containerized deployments while executing unit tests and offline development on local SQLite with zero setup friction.
- **Consequences:** Developers can run the entire backend and test suite offline without Docker running; production deployments leverage PostgreSQL's robust indexing and ACID concurrency.
- **Risks:** Dialect-specific SQL features (e.g. Postgres-specific array types) must be avoided in favor of standard SQL and JSON columns.
- **Alternatives Rejected:** MongoDB rejected due to absence of relational foreign key cascades, risking orphaned clinical records.

---

### ADR-005: ML Serving Architecture — In-Process Serialized Pipeline vs. External Model Server
- **Context:** Models must return calibrated CAD probabilities, 10-year ASCVD risk, and exact TreeSHAP attributions in $< 300\text{ms}$.
- **Problem:** Should ML models be served in-process within the FastAPI worker or via an external model serving infrastructure (e.g. Triton, TorchServe, TF Serving)?
- **Options Considered:**
  1. *Option A:* In-process loading of serialized Scikit-learn/XGBoost pipelines via `joblib`.
  2. *Option B:* External Model Server (Triton / Seldon Core).
  3. *Option C:* Microservice executing FastAPI ML worker.
- **Decision:** **Option A: In-process serialized pipeline loaded at startup**.
- **Reasoning:** For tabular models with 13 features, XGBoost and TreeSHAP execute in $< 20\text{ms}$ in-process. Deploying an external model server adds network latency, serialization overhead, infrastructure cost, and container orchestration complexity with zero accuracy or throughput benefit.
- **Consequences:** Model artifact (`heartxai_model_v2.0.0.joblib`) is verified via SHA-256 hash and pre-warmed in memory at startup. Stateless workers scale trivially.
- **Risks:** Memory footprint increases slightly ($\sim 80\text{MB}$ per worker).
- **Alternatives Rejected:** External model servers rejected as over-engineered for small-to-medium tabular ensemble models.

---

### ADR-006: Explainable AI Technique — Exact C++ TreeSHAP vs. Model-Agnostic LIME
- **Context:** Users and clinicians require feature attributions explaining which biomarkers drove the prediction away from the baseline expectation.
- **Problem:** Which explainability algorithm provides mathematically rigorous, clinically reproducible explanations?
- **Options Considered:**
  1. *Option A:* TreeSHAP (Lundberg et al., *Nature Machine Intelligence* 2020) using optimized C++ tree-traversal.
  2. *Option B:* LIME (Local Interpretable Model-agnostic Explanations).
  3. *Option C:* Permutation Feature Importance.
- **Decision:** **Option A: Exact C++ TreeSHAP**.
- **Reasoning:** TreeSHAP has proven game-theoretic properties: efficiency (additivity), symmetry, and dummy player nullity. The sum of Shapley values is guaranteed to equal $f(x) - \mathbb{E}[f(x)]$. LIME relies on random sampling perturbations and produces non-deterministic explanations that can vary between identical runs on the same patient, which is clinically unacceptable.
- **Consequences:** 100% deterministic explanations; guaranteed mathematical invariance ($\le 10^{-5}$); execution time $< 25\text{ms}$.
- **Risks:** Requires tree-based ensemble models (XGBoost, Random Forest).
- **Alternatives Rejected:** LIME rejected for non-determinism; Permutation Importance rejected because it provides only global, not local patient-specific explanations.

---

### ADR-007: Session Security — HttpOnly SameSite=Strict Cookies vs. LocalStorage
- **Context:** Secure session tokens must be stored on client browsers without vulnerability to Cross-Site Scripting (XSS) token exfiltration.
- **Problem:** Where and how should JWT authentication tokens be persisted on the client?
- **Options Considered:**
  1. *Option A:* `HttpOnly`, `Secure`, `SameSite=Strict` cookies.
  2. *Option B:* Browser `localStorage` with `Authorization: Bearer <token>` headers.
  3. *Option C:* In-memory JavaScript variable with refresh token cookie.
- **Decision:** **Option A: HttpOnly, Secure, SameSite=Strict cookies**.
- **Reasoning:** In healthcare applications handling clinical biomarkers, eliminating XSS token theft is non-negotiable. Cookies marked `HttpOnly` cannot be read or exfiltrated by any malicious client-side JavaScript. `SameSite=Strict` completely prevents Cross-Site Request Forgery (CSRF).
- **Consequences:** Client JavaScript cannot inspect token internals; tokens are automatically attached by the browser on same-origin requests; zero client token storage code required.
- **Risks:** Requires proper CORS and cookie configuration in development environments.
- **Alternatives Rejected:** `localStorage` rejected because any third-party script or XSS vulnerability can read and steal patient authentication tokens.

---

### ADR-008: Doctor-Patient Authorization — Explicit Time-Bounded Grants vs. Open Browsing
- **Context:** Doctors registered on HeartXAI 2.0 need to review patient assessments and append clinical notes.
- **Problem:** What authorization model ensures doctors can access patient charts without violating HIPAA Privacy rules or patient sovereignty?
- **Options Considered:**
  1. *Option A:* Role-based open directory: any verified clinician can search and view all patient records.
  2. *Option B:* Patient-gated time-bounded consent grants (`patient_doctor_grants`).
  3. *Option C:* Static clinic organization assignment.
- **Decision:** **Option B: Explicit, patient-gated time-bounded consent grants**.
- **Reasoning:** The HIPAA Privacy Rule (45 CFR § 164.508) mandates explicit patient authorization for disclosing protected health information. Gating doctor access behind an explicit, time-bounded grant (with instant patient revocation rights) completely prevents unauthorized medical snooping and establishes clear legal compliance.
- **Consequences:** Backend authorization middleware verifies grant validity on every clinician request; clinicians only see patients who have explicitly granted them access.
- **Risks:** If a patient's grant expires during a consultation, the doctor cannot view the chart until re-authorized.
- **Alternatives Rejected:** Open browsing strictly rejected as an egregious HIPAA violation.

---

### ADR-009: Counterfactual Optimization — Constrained Clinical L1 Step Search vs. Unconstrained
- **Context:** The system must compute realistic lifestyle biomarker modifications that reduce predicted risk.
- **Problem:** How should counterfactual optimization be formulated to guarantee medically plausible advice?
- **Options Considered:**
  1. *Option A:* Unconstrained gradient or boundary descent.
  2. *Option B:* Constrained discrete clinical step search with locked biological immutability (Age, Sex, Anatomy) and safe physiological boundaries.
  3. *Option C:* External library (DiCE) with deep neural network backend.
- **Decision:** **Option B: Constrained discrete clinical step search with locked biological immutability**.
- **Reasoning:** Unconstrained optimization can produce absurd advice (e.g. "become 20 years younger" or "reduce systolic BP to 40 mmHg"). Constraining perturbations to modifiable features and evaluating discrete clinical steps (e.g. 5, 10, 15 mmHg BP reductions) guarantees that every recommendation represents actionable, safe lifestyle targets.
- **Consequences:** 100% of counterfactual solutions are physiologically safe; runs in $< 15\text{ms}$.
- **Risks:** In extreme cases (advanced age with multiple blocked vessels), target risk may be unreachable. The system must report this gracefully.
- **Alternatives Rejected:** Unconstrained optimization rejected as clinically hazardous.

---

### ADR-010: Deployment Topology — Multi-Stage Docker Compose vs. Kubernetes
- **Context:** Packaging and orchestrating the frontend, backend, and PostgreSQL database for development, staging, and initial production.
- **Problem:** What container orchestration framework matches the needs of a solo-developer project?
- **Options Considered:**
  1. *Option A:* Docker Compose with multi-stage Dockerfiles.
  2. *Option B:* Kubernetes (K8s) with Helm charts and ingress controllers.
  3. *Option C:* Bare metal / non-containerized virtual machine scripts.
- **Decision:** **Option A: Multi-Stage Docker Compose**.
- **Reasoning:** Docker Compose provides reproducible, zero-drift environments with a single command (`docker-compose up -d --build`). Kubernetes introduces immense operational complexity (etcd, kubelet, ingress, CNI) that requires dedicated DevOps staff and provides zero benefit for a modular monolith deployment.
- **Consequences:** Lean, multi-stage Dockerfiles ($< 250\text{MB}$ frontend, $< 550\text{MB}$ backend); internal isolated network bridge; straightforward persistent volume backups.
- **Risks:** Single-node deployment; failover requires automated VM snapshotting.
- **Alternatives Rejected:** Kubernetes rejected as massive overkill and maintenance liability.
