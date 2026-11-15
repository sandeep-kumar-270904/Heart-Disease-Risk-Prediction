# HeartXAI 2.0 — Phase 3 Architectural Decisions & Open Questions

| Document Attribute | Details |
| :--- | :--- |
| **Document ID** | `HXAI-ARCH-DEC-002` |
| **Version** | `2.0.0-PROD` |
| **System State** | System Technical Architecture & Decision Governance |
| **Traceability** | `ARCHITECTURE_DECISION_RECORDS.md`, `ARCHITECTURE_CONSISTENCY_REPORT.md` |
| **Author** | Principal Software Architect, Lead Systems Architect |

---

## 1. Executive Summary & Purpose

This document catalogs the **10 Architectural Decision Records (ADRs)** ratified during Phase 3 and presents **6 targeted architectural decisions and trade-offs** submitted to stakeholders and the product team for formal review and sign-off prior to beginning Phase 4 (Visual Identity, Design System Tokens & Component Specifications).

All recommended options have been thoroughly evaluated to maximize operational reliability, security, maintainability, and implementation velocity for an individual engineer working with Google Antigravity.

---

## 2. Summary of Ratified Architecture Decision Records (ADRs)

| ADR ID | Decision Title | Selected Technical Choice | Architectural Justification |
| :--- | :--- | :--- | :--- |
| **ADR-001** | System Macro-Architecture | **Modular Monolith** over Microservices | Eliminates distributed transaction failures, network serialization overhead, and multi-service operational toil. Allows in-process C++ ML inference. |
| **ADR-002** | Frontend Architectural Framework | **React 18 + Vite SPA** with Tailwind & React Router 6 | High developer productivity, strict component encapsulation, deterministic bundle tree-shaking, sub-second HMR. |
| **ADR-003** | Backend Architectural Framework | **FastAPI + Python 3.11** with SQLAlchemy 2.0 Async | Native asynchronous I/O (`uvloop`), automatic OpenAPI 3.1 schema generation, native Python ML/C++ interop. |
| **ADR-004** | ML Inference & SHAP Architecture | **In-Process Calibrated XGBoost + TreeSHAP C++** | Zero inter-service latency ($p95 \le 300\text{ ms}$), exact mathematical local explanations with additive invariance. |
| **ADR-005** | Counterfactual Search Algorithm | **Discrete L1 Clinical Step Search** | Enforces clinical plausibility: locks immutable traits (age, sex, thal) and respects physiological floors (BP $\ge 110$, Chol $\ge 140$). |
| **ADR-006** | Primary Relational Database | **PostgreSQL 16** with Dual-Dialect SQLite Fallback | Robust ACID guarantees, JSONB for SHAP vectors, PostGIS for spatial queries, seamless SQLite fallback for zero-dependency tests. |
| **ADR-007** | Infrastructure & Orchestration | **Docker Compose** for Dev and Single-Node Prod | Guarantees 100% environment parity without the multi-cluster overhead of Kubernetes. Single command boot. |
| **ADR-008** | Authentication & Security Boundaries | **Argon2id + JWT + Consent-First RBAC** | OWASP 2024 compliance; strictly isolates doctor access behind explicit, patient-controlled time-bounded grants. |
| **ADR-009** | Clinical Target Stratification | **Dual-Target Distinction (CAD vs ASCVD)** | Disentangles binary coronary stenosis ($\ge 50\%$) from 10-year prospective cardiovascular risk (ACC/AHA 2013). |
| **ADR-010** | External Integration Resilience | **Circuit Breaker + Outbox Pattern** | Protects core clinical workflows from external network outages (CMS NPPES, OSM Overpass, Transactional Email). |

---

## 3. Open Architectural Decisions for Stakeholder Review

### Decision 1: Transactional Email Delivery Service
- **Context:** User registration verification (`FR-02`), password reset tokens (`FR-17`), and critical security alerts require transactional email delivery.
- **Option A (Recommended): Resend API via HTTPS REST with Persistent DB Outbox**
  - *Pros:* Modern developer-friendly REST API, high deliverability rate, built-in domain verification (DKIM/SPF), instant testing with test API keys, seamless integration with our persistent outbox pattern.
  - *Cons:* Third-party SaaS dependency (free tier covers 3,000 emails/month, well above prototype/pilot needs).
- **Option B: Generic SMTP Gateway (SendGrid / Postmark / Standard SMTP)**
  - *Pros:* Standardized protocol supported by any email server.
  - *Cons:* Slower handshake times, requires complex socket configuration, prone to port 25/587 blocking on cloud hosting providers.
- **Architect's Recommendation:** **Option A (Resend API)** with the persistent DB outbox pattern.

---

### Decision 2: Hospital & Cardiac Facility Directory Strategy
- **Context:** `FR-12` requires displaying nearby hospitals, emergency cardiac centers, and cath labs based on patient postal code or city.
- **Option A (Recommended): Pre-Seeded Spatial SQLite/PostGIS Table + Overpass OSM Live Fallback**
  - *Pros:* Instant response time ($\le 15\text{ ms}$), 100% offline functionality, pre-loaded with ~1,500 validated US cardiac centers, immune to OSM rate limits (1 req/sec). Overpass API is queried only if a user searches outside the pre-seeded zone.
  - *Cons:* Requires one-time generation of the pre-seeded geographic dataset (~2 MB JSON/SQL file).
- **Option B: Pure Live Overpass OSM API Queries Without Pre-Seeded Data**
  - *Pros:* Zero static asset maintenance.
  - *Cons:* Query latency 1,500ms - 4,000ms; vulnerable to public Overpass server throttling (`429 Too Many Requests`); fails completely if external network is unavailable.
- **Architect's Recommendation:** **Option A (Pre-Seeded Spatial Table + Live Fallback)**.

---

### Decision 3: Clinical PDF Report Generation Engine
- **Context:** `FR-14` requires generating downloadable, HIPAA-compliant clinical assessment summary PDFs for patients to share with their physicians.
- **Option A (Recommended): WeasyPrint (HTML5 + CSS Paged Media to PDF)**
  - *Pros:* Translates standard semantic HTML5 and CSS directly into print-quality vector PDFs. Allows reusing design tokens (typography, colors, tables) directly from the web application.
  - *Cons:* Requires `cairo` and `pango` native system libraries in the backend container (~45 MB image increase).
- **Option B: ReportLab (Pure Python Imperative PDF Canvas)**
  - *Pros:* Lightweight, pure Python, zero native C library dependencies.
  - *Cons:* Extremely tedious imperative coordinate layout (`canvas.drawString(x, y)`); difficult to maintain, style, or adjust responsive healthcare layouts.
- **Option C: Headless Chrome / Puppeteer**
  - *Pros:* Identical rendering to Google Chrome.
  - *Cons:* Adds 300+ MB to container image, requires 500+ MB idle RAM, slow cold-boot rendering times.
- **Architect's Recommendation:** **Option A (WeasyPrint)** for superior visual fidelity and maintainability.

---

### Decision 4: Physician NPI Verification Strictness
- **Context:** When a doctor registers on HeartXAI, their 10-digit NPI must be verified against the CMS NPPES registry (`FR-11`).
- **Option A (Recommended): Resilient Dual-Mode (Live CMS API Check with Fallback to Admin Review Queue)**
  - *Pros:* If CMS NPPES API responds, verification is instant. If the external CMS API is down or times out, the registration succeeds in `PENDING_VERIF` status, an admin alert is generated, and the doctor is restricted to view-only until confirmed.
  - *Cons:* Requires an administrative review dashboard interface.
- **Option B: Strict Synchronous Blocking**
  - *Pros:* Simpler logic; no pending queue needed.
  - *Cons:* If CMS NPPES has maintenance downtime, legitimate cardiologists are blocked from registering.
- **Architect's Recommendation:** **Option A (Dual-Mode with Fallback Queue)**.

---

### Decision 5: Reverse Proxy & TLS Termination Technology
- **Context:** The perimeter reverse proxy terminates HTTPS, enforces HSTS, applies rate limiting, and routes traffic between frontend and backend (`DEPLOYMENT_ARCHITECTURE.md`).
- **Option A (Recommended): Nginx 1.25 Alpine**
  - *Pros:* Battle-tested, industry standard, minimal footprint (15 MB RAM), highly configurable rate-limiting zones (`limit_req_zone`), deterministic behavior.
  - *Cons:* Requires manual or Certbot ACME certificate configuration.
- **Option B: Caddy 2 Alpine**
  - *Pros:* Automatic zero-configuration Let's Encrypt TLS issuance out-of-the-box.
  - *Cons:* Slightly larger runtime footprint, non-standard configuration syntax (`Caddyfile`).
- **Architect's Recommendation:** **Option A (Nginx 1.25 Alpine)** for maximum stability and fine-grained HTTP header security.

---

### Decision 6: Automated Database Backup Destination
- **Context:** Regulatory requirement `NFR-08` mandates daily encrypted database backups with a 14-day retention cycle.
- **Option A (Recommended): Local Encrypted Docker Volume (`/backups`) + Automated Cron with AES-256-CBC**
  - *Pros:* Self-contained, works out of the box in any development or single-node environment without cloud credentials, zero external hosting costs.
  - *Cons:* Host-level disk failure requires secondary off-host sync.
- **Option B: AWS S3 / Cloud Object Storage Backup Sync**
  - *Pros:* Geographically redundant off-site disaster recovery.
  - *Cons:* Requires active AWS IAM credentials and cloud billing configuration.
- **Architect's Recommendation:** **Option A as Default Base**, with an optional S3 sync hook when cloud credentials are provided.

---

## 4. Next Steps Following Approval

Upon user review and confirmation of these architectural recommendations:
1. Complete formal sign-off of Phase 3 Architecture.
2. Advance to **Phase 4: Visual Identity, Design Tokens & Design System Specification** (establishing HeartXAI's bespoke typography, color scales, spacing tokens, and component specifications in adherence to `DESIGN_SYSTEM_RESEARCH.md`).

---

*Submitted for review by Principal Software Architect & Technical Lead.*
