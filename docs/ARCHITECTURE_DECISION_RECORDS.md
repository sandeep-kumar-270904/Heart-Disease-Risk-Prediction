# HeartXAI 2.0 — Architecture Decision Records (ADRs)

| Document Attribute | Details |
| :--- | :--- |
| **Document ID** | `HXAI-ARCH-002` |
| **Version** | `3.1.0-REVISED` |
| **Phase** | Phase 3 — System Architecture & Technical Design |
| **Status** | Approved / Core Architectural Baseline (Audited & Remediated) |
| **Author** | Principal Software Architect & Healthcare Security Reviewer |

---

## Index of Architecture Decision Records

| ADR ID | Decision Title | Status | Date | Primary Governance Impact |
| :--- | :--- | :--- | :--- | :--- |
| **ADR-001** | Macro Architecture: Modular Monolith vs Microservices | **APPROVED** | 2026-11-16 | Single-process operational simplicity, sub-300ms ML latency |
| **ADR-002** | Frontend Stack: React 18 SPA with Vite vs Next.js Fullstack | **APPROVED** | 2026-11-16 | Static edge distribution, zero Node.js server overhead |
| **ADR-003** | Backend Runtime: Python 3.11+ FastAPI vs Node.js / Go | **APPROVED** | 2026-11-16 | Native async ASGI, native C++ ML/TreeSHAP interop |
| **ADR-004** | Persistence Engine: PostgreSQL 16 Production with Qualified SQLite Unit-Test Harness | **APPROVED** | 2026-11-16 | PostgreSQL 16 mandatory for prod/CI; SQLite limitations disclaimed |
| **ADR-005** | ML Serving & Clinical Scope: In-Process Retrospective CAD Classifier vs Prospective Risk | **APPROVED** | 2026-11-16 | Strict distinction: retrospective CAD classifier vs 10-yr ASCVD |
| **ADR-006** | Explainable AI Technique: Exact C++ TreeSHAP Mathematical Attribution vs LIME | **APPROVED** | 2026-11-16 | Mathematical feature attribution; disclaimed as causal medical proof |
| **ADR-007** | Session & Security Model: HttpOnly SameSite=Strict Cookies vs LocalStorage | **APPROVED** | 2026-11-16 | OWASP 2024 compliance, zero JavaScript XSS token exposure |
| **ADR-008** | Multi-Jurisdictional Authorization: Explicit Consent Grants vs Open Browsing | **APPROVED** | 2026-11-16 | India DPDP Act 2023, US HIPAA, EU GDPR; patient sovereignty |
| **ADR-009** | Counterfactual Analysis: Constrained Mathematical Perturbation vs Treatment Prescribing | **APPROVED** | 2026-11-16 | Exploratory 'what-if' model perturbations; not medical advice |
| **ADR-010** | Deployment & Infrastructure: Docker Compose with Pinned Nginx 1.26 Stable Alpine | **APPROVED** | 2026-11-16 | Pinned supported Stable release series; weekly vulnerability scan |
| **ADR-011** | Global Geographic Architecture: Configurable by Country via Adapter Pattern | **APPROVED REQUIREMENT** | 2026-11-16 | Zero national hardcoding; 8 country modules; verified sources |
| **ADR-012** | Backup Cryptography: Authenticated AEAD Encryption with Off-Site WORM Storage | **APPROVED** | 2026-11-16 | AES-256-GCM, S3 Object Lock, empirical restoration test mandate |

---

### ADR-001: Macro Architecture — Modular Monolith vs. Microservices
- **Context:** HeartXAI 2.0 is being developed by an individual engineer using Google Antigravity. The platform requires high clinical data integrity, strict ACID transactions, and sub-300ms inference latency across interconnected modules (auth, intake, inference, XAI, counterfactuals, audit).
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

### ADR-002: Frontend Architecture — React 18 SPA with Vite vs. Next.js Fullstack
- **Context:** The frontend requires complex, interactive client-side widgets: SVG SHAP waterfall plots, real-time debounced what-if sliders, multi-step intake wizards, and responsive time-series charts.
- **Problem:** Should the frontend be built as a decoupled Single-Page Application (SPA) or a Server-Side Rendered (SSR) full-stack framework like Next.js?
- **Options Considered:**
  1. *Option A:* React 18 SPA with TypeScript, Vite, and Tailwind CSS.
  2. *Option B:* Next.js 14/15 App Router with Node.js SSR.
- **Decision:** **Option A: React 18 SPA with Vite and Tailwind CSS**.
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

### ADR-004: Persistence Engine — PostgreSQL 16 Production with Qualified SQLite Unit-Test Harness
- **Context:** The application stores relational data with parent-child cascades (`users` $\rightarrow$ `assessments` $\rightarrow$ `inference_results` $\rightarrow$ `shap_explanations`).
- **Problem:** What database engine ensures production reliability, and how should testing environments be architected?
- **Options Considered:**
  1. *Option A:* Claim full dual-dialect transparent compatibility between PostgreSQL 16 and SQLite.
  2. *Option B:* Designate PostgreSQL 16 as the sole production and staging database; restrict SQLite strictly to lightweight local developer unit testing; mandate PostgreSQL 16 for CI/CD integration testing.
  3. *Option C:* Mandatory local Dockerized PostgreSQL for all test tiers.
- **Decision:** **Option B: PostgreSQL 16 as sole production/staging database; qualified SQLite for local unit testing; mandatory PostgreSQL 16 in CI/CD integration pipelines**.
- **Reasoning:** Independent review demonstrated that SQLite lacks native binary JSONB indexing (GIN), lacks row-level locking (causing `database is locked` under concurrency), uses dynamic type affinity, ignores foreign keys without explicit pragma configuration, and lacks native `TIMESTAMPTZ` arithmetic. Transparent compatibility is mathematically and technically false.
- **Consequences:** Production and staging environments run PostgreSQL 16 exclusively. Local developer unit tests run on SQLite for rapid sub-second feedback. All release pipelines execute integration tests against ephemeral PostgreSQL 16 containers.
- **Risks:** Dialect-specific migrations must be verified bidirectionally (`upgrade head` $\rightarrow$ `downgrade base` $\rightarrow$ `upgrade head`).
- **Alternatives Rejected:** Option A rejected as technically inaccurate; Option C rejected because it hinders offline developer velocity on machines without running Docker daemons.

---

### ADR-005: ML Serving & Clinical Scope — In-Process Retrospective CAD Classifier vs. Prospective Risk
- **Context:** The system incorporates machine learning for cardiovascular decision support.
- **Problem:** How should the ML model be architecturally scoped, served, and clinically framed?
- **Options Considered:**
  1. *Option A:* Claim that the ML model calculates a 10-year prospective ASCVD risk.
  2. *Option B:* Formally define the ML model as a retrospective Angiographic Coronary Artery Disease (CAD) Association Classifier (predicting $\ge 50\%$ diameter stenosis based on historical Cleveland 1988 data), served in-process via C++ XGBoost; separate it strictly from deterministic prospective risk calculators (ACC/AHA 2013 / WHO chart).
  3. *Option C:* External model serving cluster (Triton / TorchServe).
- **Decision:** **Option B: In-process retrospective CAD association classifier strictly separated from prospective risk calculators**.
- **Reasoning:** Conflating a historical angiographic classifier with a prospective 10-year risk estimator is scientifically false and clinically hazardous. Serving in-process yields sub-20ms inference with zero RPC hops.
- **Consequences:** Model artifact (`heartxai_model_v2.0.0.joblib`) is verified via SHA-256 hash. Clear non-diagnostic educational framing enforced.
- **Risks:** Users must be educated on the distinction between retrospective CAD classification and prospective longitudinal risk.
- **Alternatives Rejected:** Option A rejected for scientific inaccuracy; Option C rejected as an unnecessary operational burden.

---

### ADR-006: Explainable AI Technique — Exact C++ TreeSHAP Mathematical Attribution vs. LIME
- **Context:** Users and clinicians require feature attributions explaining which biomarkers drove the model prediction away from the baseline expectation.
- **Problem:** Which explainability algorithm provides mathematically rigorous, clinically reproducible explanations?
- **Options Considered:**
  1. *Option A:* TreeSHAP (Lundberg et al., *Nature Machine Intelligence* 2020) using optimized C++ tree-traversal.
  2. *Option B:* LIME (Local Interpretable Model-agnostic Explanations).
  3. *Option C:* Permutation Feature Importance.
- **Decision:** **Option A: Exact C++ TreeSHAP**.
- **Reasoning:** TreeSHAP has proven game-theoretic properties: efficiency (additivity), symmetry, and dummy player nullity. The sum of Shapley values is guaranteed to equal $f(x) - \mathbb{E}[f(x)]$. LIME relies on random sampling perturbations and produces non-deterministic explanations that can vary between identical runs on the same patient.
- **Scientific Qualification:** SHAP values represent **mathematical feature attributions of the trained tree model**, NOT causal medical evidence or biological etiology.
- **Consequences:** 100% deterministic explanations; guaranteed mathematical invariance ($\le 10^{-5}$); execution time $< 25\text{ms}$.
- **Risks:** Requires tree-based ensemble models (XGBoost, Random Forest).
- **Alternatives Rejected:** LIME rejected for non-determinism; Permutation Importance rejected because it provides only global explanations.

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

### ADR-008: Multi-Jurisdictional Authorization — Explicit Consent Grants vs. Open Browsing
- **Context:** Doctors registered on HeartXAI 2.0 need to review patient assessments and append clinical notes.
- **Problem:** What authorization model ensures doctors can access patient charts without violating healthcare data protection laws?
- **Options Considered:**
  1. *Option A:* Role-based open directory: any verified clinician can search and view all patient records.
  2. *Option B:* Patient-gated time-bounded consent grants (`patient_doctor_grants`).
  3. *Option C:* Static clinic organization assignment.
- **Decision:** **Option B: Explicit, patient-gated time-bounded consent grants**.
- **Reasoning:** India's Digital Personal Data Protection Act, 2023 (DPDP Act) and the US HIPAA Privacy Rule mandate explicit, purpose-limited patient consent for sharing health information. Gating doctor access behind an explicit, time-bounded grant (with instant patient revocation rights) establishes multi-jurisdictional legal compliance and patient sovereignty.
- **Consequences:** Backend authorization middleware verifies grant validity on every clinician request; clinicians only see patients who have explicitly granted them access.
- **Risks:** If a patient's grant expires during a consultation, the doctor cannot view the chart until re-authorized.
- **Alternatives Rejected:** Open browsing strictly rejected as an egregious legal violation.

---

### ADR-009: Counterfactual Analysis — Constrained Mathematical Perturbation vs. Treatment Prescribing
- **Context:** The system evaluates hypothetical biomarker modifications that reduce model output scores.
- **Problem:** How should counterfactual optimization be formulated and clinically framed?
- **Options Considered:**
  1. *Option A:* Frame counterfactuals as personalized medical treatment recommendations.
  2. *Option B:* Constrained discrete L1 step search with locked biological immutability (Age, Sex, Anatomy) and safe physiological boundaries, framed strictly as exploratory model perturbations.
  3. *Option C:* Unconstrained gradient descent.
- **Decision:** **Option B: Constrained discrete clinical step search framed strictly as exploratory model perturbations**.
- **Reasoning:** Unconstrained optimization produces absurd suggestions (e.g. "become 20 years younger"). Software cannot prescribe clinical treatment without medical device certification. Framing counterfactuals as hypothetical model "what-if" perturbations preserves scientific rigor and patient safety.
- **Consequences:** 100% of counterfactual solutions are physiologically bounded; executes in $< 15\text{ms}$. Non-diagnostic medical disclaimer rendered prominently.
- **Risks:** In severe anatomical disease, target scores may be mathematically unreachable; system gracefully communicates this boundary.
- **Alternatives Rejected:** Option A rejected for regulatory liability; Option C rejected as physiologically impossible.

---

### ADR-010: Deployment & Infrastructure — Docker Compose with Pinned Nginx 1.26 Stable Alpine
- **Context:** Packaging and orchestrating the frontend, backend, and PostgreSQL database for development, staging, and initial production.
- **Problem:** What container orchestration framework matches the needs of a solo-developer project, and how should edge proxy versions be maintained?
- **Options Considered:**
  1. *Option A:* Docker Compose with floating or outdated mainline Nginx images (e.g. `nginx:1.25-alpine`).
  2. *Option B:* Docker Compose pinning to active **Nginx Stable branch (`nginx:1.26-alpine`)** with documented vulnerability scanning and patching lifecycle.
  3. *Option C:* Kubernetes (K8s) with Helm charts and ingress controllers.
- **Decision:** **Option B: Multi-Stage Docker Compose with pinned Nginx 1.26 Stable Alpine**.
- **Reasoning:** Nginx 1.25 was a mainline development release retired in April 2024. Production stability requires pinning to the supported Stable branch (`1.26.x`). Docker Compose provides reproducible environments with single-command boot (`docker-compose up -d --build`). Kubernetes introduces immense operational complexity with zero benefit for a modular monolith.
- **Consequences:** Lean, multi-stage Dockerfiles; weekly Trivy vulnerability scanning; Dependabot automated container updates; zero-downtime hot reloading (`nginx -s reload`).
- **Risks:** Single-node deployment; failover requires automated snapshot restore.
- **Alternatives Rejected:** Option A rejected for unmaintained mainline risk; Option C rejected as excessive DevOps overhead.

---

### ADR-011: Global Geographic Architecture — Configurable by Country via Adapter Pattern (APPROVED REQUIREMENT)
- **Status:** **APPROVED PRODUCT REQUIREMENT** (Governing Product Direction).
- **Context:** The approved target market for HeartXAI 2.0 is **GLOBAL — CONFIGURABLE BY COUNTRY**. The architecture must not hard-code the United States, India, or any other country as the only supported market. Furthermore, the architecture must avoid claiming worldwide operational coverage or fabricating non-existent global healthcare databases. Launch countries represent a separate product decision.
- **Problem:** How should the platform architecture accommodate varying national registries, directories, insurance systems, clinical guidelines, privacy laws, and measurement units without embedding country-specific assumptions across the core application?
- **Options Considered:**
  1. *Option A:* Hardcode single-country assumptions (e.g. US CMS NPPES or India NMC) throughout services and schemas.
  2. *Option B:* Global Country-Configurable Architecture via Country Profile Registry and Strategy/Adapter Pattern.
  3. *Option C:* Multiple fork repositories for each target country.
- **Decision:** **Option B: Global Country-Configurable Architecture via Country Profile Registry and Strategy/Adapter Pattern**.
- **Reasoning:** Encapsulating all national variations behind strongly typed country profiles and pluggable adapter interfaces satisfies the approved requirement. Core clinical inference, TreeSHAP explanation, and counterfactual solvers remain universal, while 8 country-configurable modules handle regional specifics:
  1. *Doctor Directories:* Local postal code regex (6-digit PIN, 5-digit ZIP), verified local clinician roster.
  2. *Hospital Directories:* National boundary queries (PMJAY open data, CMS open data, OSM Overpass with ODbL licensing and rate boundaries).
  3. *Physician Verification:* Regional licensing workflows (India State Council review queue; US CMS NPPES API; generic document upload queue).
  4. *Health Insurance Guides:* Country policy navigation (India PMJAY & IRDAI; US ACA § 2713 & Medicare; universal reimbursement checklist).
  5. *Healthcare Sources & Guidelines:* Authoritative national clinical bodies (India CSI/ICMR; US ACC/AHA; Europe ESC; WHO South Asia charts).
  6. *Privacy & Regulations:* Jurisdictional data governance (India DPDP Act 2023; US HIPAA; EU GDPR; baseline zero-trust).
  7. *Languages, Currencies & Dates:* Unicode UTF-8, i18next translation keys, ISO 4217 currencies, IANA timezones, and UTC database storage.
  8. *Measurement Units & Biomarkers:* Bidirectional conversion engine (`BiomarkerUnitConverter`) supporting $\text{mg/dL} \leftrightarrow \text{mmol/L}$ for cholesterol and fasting glucose, and metric/imperial anthropometrics, while maintaining model-native normalization invariance.
- **Consequences:** Zero national hardcoding. New countries are onboarded via configuration and adapter plugins without touching core ML or assessment code.
- **Risks:** Each country profile requires verified external data sources with documented licensing, availability, and failure fallbacks. Full specification detailed in `docs/GLOBAL_COUNTRY_CONFIGURATION_ARCHITECTURE.md`.
- **Alternatives Rejected:** Option A rejected for violating approved global direction; Option C rejected for creating an unmaintainable multi-codebase maintenance nightmare.

---

### ADR-012: Backup Cryptography — Authenticated AEAD Encryption with Off-Site WORM Storage
- **Context:** HeartXAI handles clinical and assessment data requiring disaster recovery protection.
- **Problem:** What cryptographic cipher, key management, and replication strategy ensures backup integrity, confidentiality, and recoverability?
- **Options Considered:**
  1. *Option A:* Unauthenticated AES-256-CBC stored on local Docker volumes.
  2. *Option B:* Authenticated Encryption with Associated Data (AEAD) via AES-256-GCM, automated key rotation, off-site S3 Object Lock (WORM) replication, and mandatory monthly restoration testing drills.
  3. *Option C:* Unencrypted pg_dump scripts.
- **Decision:** **Option B: Authenticated AES-256-GCM with off-site S3 WORM replication and empirical restoration test mandate**.
- **Reasoning:** Independent review proved that unauthenticated AES-256-CBC is vulnerable to padding oracle and ciphertext tampering attacks. Storing backups solely on the host risks total loss during disk failure or ransomware. S3 Object Lock in Compliance Mode prevents backup deletion. Crucially, recoverability cannot be claimed without regular restoration testing.
- **Consequences:** Backups carry 128-bit authentication tags; immutable off-site archive; dedicated backup IAM role with `PutObject` permission only; automated monthly restoration test script (`restore_verify.sh`).
- **Risks:** Requires secure off-site credentials and KMS key management.
- **Alternatives Rejected:** Option A rejected for cryptographic and disaster recovery vulnerabilities; Option C rejected as an egregious HIPAA/DPDP violation.

---

*Certified and sealed by Principal Software Architect & Healthcare Security Reviewer.*
