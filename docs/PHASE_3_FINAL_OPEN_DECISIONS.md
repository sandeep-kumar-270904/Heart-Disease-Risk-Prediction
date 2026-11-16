# HeartXAI 2.0 — Phase 3 Final Open Strategic Decisions

| Document Attribute | Details |
| :--- | :--- |
| **Document ID** | `HXAI-ARCH-DEC-003` |
| **Version** | `2.1.0-REVISED` |
| **Review Date** | November 2026 |
| **Governance Scope** | Formal catalog of unresolved business, clinical, and infrastructure strategic decisions submitted for stakeholder approval |
| **Author** | Principal Software Architect & Healthcare Security Reviewer |

---

## 1. Governance Overview & Architectural Guardrails

To prevent silent assumptions and ensure complete alignment between engineering, clinical governance, and executive leadership, this document catalogs all **unresolved strategic decisions** identified during the Phase 3 Architecture Review.

### Architectural Policy on Unresolved Decisions
In accordance with modern software architecture principles:
1. **Zero Silent Assumptions:** No geographic, clinical, or cloud infrastructure assumption is hardcoded into the platform.
2. **Strategy / Adapter Encapsulation:** Any capability dependent on an unresolved strategic decision is architected behind an abstract interface (Strategy/Adapter Pattern), allowing implementation without architectural refactoring.
3. **Formal Stakeholder Ratification:** Decisions listed below require explicit stakeholder review and approval prior to production release.

---

## 2. Approved Strategic Product Direction

### Decision DEC-GEO-01: Target Market — Global Configurable by Country (APPROVED REQUIREMENT)

- **Status:** **APPROVED & RATIFIED PRODUCT REQUIREMENT**
- **Approved Decision:** The primary target market for HeartXAI 2.0 is **GLOBAL — CONFIGURABLE BY COUNTRY**.
- **Governance Mandate:** The architecture must not hard-code the United States, India, or any other country as the only supported market. The system is architected for expansion without claiming worldwide operational coverage. Launch countries represent a separate product decision.
- **Architectural Solution:** Encapsulated across eight (8) country-configurable modules via the **Country Profile Registry** and **Strategy / Adapter Pattern** (detailed in [`GLOBAL_COUNTRY_CONFIGURATION_ARCHITECTURE.md`](./GLOBAL_COUNTRY_CONFIGURATION_ARCHITECTURE.md)):
  1. *Doctor Directories:* Postal code format, verified national practitioner directory.
  2. *Hospital Directories:* National boundary queries, emergency cardiac facility datasets (PMJAY, CMS, OSM).
  3. *Physician Verification:* National licensing workflows (NMC document queue for India; CMS NPPES API for US; document upload for default).
  4. *Insurance Information:* National public/private healthcare policy navigation (India PMJAY/IRDAI, US ACA/Medicare, universal).
  5. *Clinical Guidelines:* National cardiology authorities (India CSI/ICMR, US ACC/AHA, Europe ESC, WHO charts).
  6. *Privacy & Compliance:* National data protection statutes (India DPDP Act 2023, US HIPAA, EU GDPR).
  7. *Languages & Localization:* Unicode UTF-8, i18next strings, ISO 4217 currencies, IANA timezones, UTC storage.
  8. *Measurement Units:* Dynamic bidirectional conversion engine (`BiomarkerUnitConverter`) for $\text{mg/dL} \leftrightarrow \text{mmol/L}$ (cholesterol and glucose) and metric/imperial anthropometrics.

---

## 3. Catalog of Remaining Open Technical Decisions

- **Status:** **UNRESOLVED — PENDING REGIONAL POLICY APPROVAL**
- **Context:** `FR-11` requires verifying medical credentials when a user registers with the role `doctor`.
- **Evaluated Options:**
  - **Option 1: Administrative Document Verification Queue (Universal / India Baseline)**
    - *Mechanism:* The applicant submits their State Medical Council Registration Number (e.g., APMC/12345, KMC/67890) and uploads their registration certificate (PDF/JPEG).
    - *Security State:* Account is created in `PENDING_VERIF` state with view-only permissions. Platform administrators verify against the public NMC portal (`nmc.org.in`) and approve via the Admin Portal (`FR-20`).
    - *Pros:* 100% reliable; requires zero external third-party API dependencies or paid contracts; works immediately in India.
    - *Cons:* Requires human administrative action (SLA: 24–48 hours).
  - **Option 2: Automated ABDM Healthcare Professionals Registry (HPR) API (India Future)**
    - *Mechanism:* Programmatic lookup against National Health Authority (NHA) ABDM HPR sandbox/production gateway.
    - *Pros:* Fully automated, instant verification in India.
    - *Cons:* Requires formal NHA entity registration, sandbox milestone certification (M1, M2), security audits, and institutional MoU. Unobtainable for individual development.
  - **Option 3: Automated CMS NPPES API (US Scope Only)**
    - *Mechanism:* Real-time REST lookup against `https://npiregistry.cms.hhs.gov/api/`.
    - *Pros:* Free public API, no authentication token required.
    - *Cons:* Valid strictly for US NPI holders; useless for Indian medical practitioners.
- **Architect's Recommendation:** **Option 1 (Administrative Document Queue)** as the universal foundation, with pluggable API adapters when operational jurisdiction and accreditation are established.

---

### Decision DEC-CLIN-03: Clinical Risk Communication & Scoring Scope

- **Status:** **UNRESOLVED — PENDING CLINICAL ADVISORY BOARD APPROVAL**
- **Context:** The system must communicate health metrics without overstepping regulatory boundaries (FDA SaMD, CDSCO India, or EU MDR).
- **Evaluated Options:**
  - **Option 1: Retrospective CAD Likelihood Only (Conservative SaMD Stance)**
    - *Presentation:* Clearly labeled as **"Angiographic CAD Association Likelihood (Educational Model)"**.
    - *Details:* Displays the ML model's statistical likelihood of $\ge 50\%$ coronary artery stenosis based on the retrospective 1988 Cleveland cohort.
    - *Pros:* Zero risk of misleading patients regarding prospective 10-year risk; strictly compliant with non-diagnostic disclaimers.
    - *Cons:* Patients may expect a familiar 10-year risk percentage.
  - **Option 2 (Recommended): Dual-Display with Strict Metric Disentanglement**
    - *Presentation:* Two visually and conceptually distinct cards:
      1. **Retrospective CAD Association Likelihood** (ML Model): Statistical pattern recognition on historical angiographic findings.
      2. **Prospective 10-Year ASCVD Risk Estimate** (Deterministic Clinical Formula): Computed via the ACC/AHA 2013 Pooled Cohort Equations or WHO/ISH South Asia charts using standard lipid and demographic values.
    - *Disclaimers:* Prominent, non-dismissible advisory stating that neither score constitutes a medical diagnosis, medical device output, or treatment prescription.
- **Architect's Recommendation:** **Option 2 (Dual-Display with Strict Disentanglement)**.

---

### Decision DEC-DB-04: CI/CD Test Pipeline Database Engine

- **Status:** **UNRESOLVED — PENDING CI/CD RUNNER INFRASTRUCTURE APPROVAL**
- **Context:** Architecture review finding A3 proved that SQLite cannot replace PostgreSQL 16 for integration testing due to JSONB, locking, and type differences.
- **Evaluated Options:**
  - **Option 1 (Recommended): Dual-Engine Staged Testing Strategy**
    - *Local Development Unit Tests:* SQLite in-memory for sub-second developer feedback on basic logic, security functions, and schema compilation (`pytest backend/tests/`).
    - *CI/CD Integration & End-to-End Tests:* Automated GitHub Actions / GitLab CI pipeline spinning up an ephemeral `postgres:16-alpine` service container, running Alembic migrations, and executing comprehensive integration suites.
    - *Pros:* Maximizes local developer agility while guaranteeing 100% production engine verification before merge.
    - *Cons:* Developers must push or run local Docker Compose to execute full PostgreSQL integration tests.
  - **Option 2: Mandatory Local Dockerized PostgreSQL for All Tests**
    - *Mechanism:* Developers cannot run tests without a running PostgreSQL container.
    - *Pros:* Absolute database engine uniformity across all test tiers.
    - *Cons:* Slower local test runs; breaks testing on machines without Docker daemon running.
- **Architect's Recommendation:** **Option 1 (Dual-Engine Staged Testing Strategy)**.

---

### Decision DEC-BACKUP-05: Off-Site Backup Cloud Storage & Key Management

- **Status:** **UNRESOLVED — PENDING INFRASTRUCTURE BUDGET APPROVAL**
- **Context:** Automated backups require authenticated encryption (AES-256-GCM) and off-site immutable replication (WORM).
- **Evaluated Options:**
  - **Option 1: AWS S3 with Object Lock (Compliance Mode) + AWS KMS**
    - *Pros:* Industry-standard WORM immutability; hardware-backed KMS master key rotation; guaranteed regulatory compliance.
    - *Cons:* Requires active AWS account, IAM configuration, and cloud storage billing (~$5–$15/month).
  - **Option 2: S3-Compatible Storage (Cloudflare R2 / Backblaze B2 / MinIO Off-Site) + PBKDF2 Key**
    - *Pros:* Extremely cost-effective; zero egress fees (Cloudflare R2); master backup key derived via PBKDF2-HMAC-SHA256 (100,000 iterations) from an environment secret.
    - *Cons:* Object Lock compliance configuration varies across providers.
- **Architect's Recommendation:** **Option 2 as baseline for lean development**, upgrading to **Option 1 for enterprise production deployment**.

---

### Decision DEC-HOST-06: Production Hosting Architecture & Orchestration

- **Status:** **UNRESOLVED — PENDING HOSTING ENVIRONMENT SELECTION**
- **Context:** The production topology must balance operational simplicity, uptime, and cost.
- **Evaluated Options:**
  - **Option 1: Single-Node Cloud Virtual Machine with Docker Compose (Recommended)**
    - *Host:* Ubuntu 22.04 LTS (AWS EC2 t3.xlarge, GCP Compute Engine e2-standard-4, or Hetzner Dedicated).
    - *Stack:* Docker Compose running Nginx 1.26 perimeter proxy, Frontend container, FastAPI backend, and PostgreSQL 16 container with local persistent volumes.
    - *Pros:* Complete architectural parity with development; zero Kubernetes management toil; fixed, predictable monthly cost ($20–$60/month).
    - *Cons:* Vertical scaling limits; host failover requires automated snapshot restore.
  - **Option 2: Managed Container PaaS (AWS ECS / Render / Railway) + Managed RDS**
    - *Stack:* Containerized frontend/backend on managed PaaS; managed PostgreSQL database.
    - *Pros:* Automatic host patching, managed DB failover.
    - *Cons:* Higher recurring costs ($100–$300/month); vendor-specific networking and secret management abstractions.
- **Architect's Recommendation:** **Option 1 (Single-Node Docker Compose)** for initial rollout, with clear modular boundaries enabling straightforward migration to Option 2 when traffic scales.

---

## 4. Summary of Strategic Decisions Status

| Decision ID | Area | Status | Adopted Architecture / Recommendation | Impact |
| :--- | :--- | :--- | :--- | :--- |
| **DEC-GEO-01** | Geography | **APPROVED** | **GLOBAL — CONFIGURABLE BY COUNTRY** via Country Profile Registry & Adapters | Zero national hardcoding; 8 country modules; expansion runbook |
| **DEC-VERIF-02** | Provider Verification | PENDING CONFIRMATION | **Two-Tier: Admin Document Queue + Regional API Adapters** | Eliminates blocking on unaccredited external registries |
| **DEC-CLIN-03** | Clinical Framing | PENDING CONFIRMATION | **Dual-Display: Retrospective CAD + Separate ASCVD** | Scientifically honest; educational non-diagnostic disclaimers |
| **DEC-DB-04** | DB Testing | PENDING CONFIRMATION | **Staged: SQLite Local Unit + PostgreSQL 16 CI** | Blends developer speed with production parity |
| **DEC-BACKUP-05** | Backup Crypto | PENDING CONFIRMATION | **AES-256-GCM + S3-Compatible WORM Off-Site** | Guarantees ransomware and tamper immunity |
| **DEC-HOST-06** | Hosting | PENDING CONFIRMATION | **Single-Node Docker Compose (Nginx 1.26 + Postgres 16)**| Minimizes operational complexity and infrastructure costs |

---

*Submitted for executive and clinical stakeholder review by Principal Software Architect & Healthcare Security Reviewer.*
