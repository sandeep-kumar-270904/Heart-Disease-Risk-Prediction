# HeartXAI 2.0 — Phase 7 Backend Open Decisions & Technical Questions

**Document ID:** `HX2-BE-018`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Catalog of Open Engineering Decisions  
**Author:** Principal Backend Architect & Lead Systems Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001 through ADR-011  

---

## 1. Overview

While the backend engineering architecture, project structure, endpoint specifications, authentication model, ML integration, and testing strategies have been formally specified in `docs/backend/`, five technical decisions remain open for final architectural ratification prior to beginning implementation.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PHASE 7 OPEN TECHNICAL DECISIONS                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Database Connection Pooling: Native Asyncpg vs External PgBouncer   │
│ 2. PDF Rendering Engine: WeasyPrint (HTML/CSS) vs Headless Chromium    │
│ 3. Session Revocation: Monotonic Token Version vs Redis Blocklist      │
│ 4. Country Directory Caching: In-Memory TTLCache vs Redis Cluster      │
│ 5. ML Model Packaging: Docker Container Bundling vs S3 Artifact Bucket │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Open Technical Decisions & Trade-Off Analyses

### Decision 01: Database Connection Pooling Architecture
- **Context:** FastAPI utilizes `asyncpg` for PostgreSQL connection management. Should an external connection pooler (PgBouncer) be introduced?
- **Option A (Recommended for Initial Launch): Native Asyncpg Connection Pool**
  - *Architecture:* FastAPI maintains an internal pool of 20 connections per worker process (`max_overflow=10`).
  - *Pros:* Zero additional infrastructure daemons to configure or monitor; native asyncpg performance is exceptionally fast.
  - *Cons:* If the backend scales horizontally across $> 5$ container replicas, total connections could exceed PostgreSQL defaults (100 connections).
- **Option B: PgBouncer Middleware Pooler**
  - *Cons:* Adds another proxy hop and connection management layer for an individual developer to operate.
- **Status:** *Approved Architecture Recommendation: Adopt Option A for initial launch; deploy PgBouncer when scaling beyond 3 container replicas.*

---

### Decision 02: Clinical Consultation PDF Rendering Engine
- **Context:** Server-side generation of the 1-page printable physician discussion summary.
- **Option A (Recommended): WeasyPrint (HTML/CSS to PDF Engine)**
  - *Pros:* Lightweight Python library; uses standard HTML/CSS templates; requires no headless browser process; compiles in $< 800\text{ms}$; produces highly accessible PDF tags.
  - *Cons:* Requires native system cairo/pango libraries installed in container image.
- **Option B: Headless Chromium via Playwright**
  - *Cons:* Heavy container footprint (adds $> 400\text{ MB}$ to Docker image); consumes significant RAM ($> 200\text{ MB}$ per print worker).
- **Status:** *Approved Architecture Recommendation: Option A (WeasyPrint).*

---

### Decision 03: Session Token Revocation Architecture
- **Context:** When a user logs out or changes their password, how are existing refresh tokens invalidated?
- **Option A (Recommended): Monotonic `token_version` on User Model**
  - *Mechanism:* Each User record has an integer `token_version`. The refresh JWT includes `token_version` in its payload. Password reset or global logout increments `token_version` in the database. Any token presenting an older version is rejected immediately.
  - *Pros:* 100% database-backed; requires zero Redis infrastructure; instant invalidation across all devices.
  - *Cons:* Fast validation on refresh requests requires a single database index lookup.
- **Option B: Distributed Redis Token Blocklist**
  - *Cons:* Introduces Redis dependency solely for token blocklisting.
- **Status:** *Approved Architecture Recommendation: Option A (`token_version`).*

---

### Decision 04: Country Directory Adapter Caching Architecture
- **Context:** Country directories (NMC India, CMS USA) require caching to ensure sub-50ms query responses and provide offline resilience.
- **Option A (Recommended): In-Memory Cachetools with TTL**
  - *Mechanism:* Utilizes Python's `cachetools.TTLCache` (max 5,000 entries, 30-minute TTL) per worker process.
  - *Pros:* Microsecond-level lookups; zero external network hops; self-contained within backend process.
  - *Cons:* Each worker process maintains its own cache instance.
- **Option B: Distributed Redis Cache**
  - *Cons:* Adds network latency and infrastructure operational burden.
- **Status:** *Approved Architecture Recommendation: Option A.*

---

### Decision 05: Machine Learning Model Artifact Packaging
- **Context:** How should the validated XGBoost model artifact (`cleveland_xgboost_v2.4.1.json`) and TreeSHAP background summary be delivered to the application?
- **Option A (Recommended): Bundled Inside Application Container Image**
  - *Mechanism:* The model artifact is checked into Git under `app/ml/artifacts/` with a verified `checksums.sha256` manifest and baked directly into the Docker image.
  - *Pros:* 100% immutable and reproducible; zero startup network dependencies; cannot fail due to S3 outages; verified at container boot.
  - *Cons:* Model updates require deploying a new container version (which is desirable for audit traceability).
- **Option B: Dynamic Download from Cloud Storage (S3 / GCS)**
  - *Cons:* Introduces startup failure risks if cloud storage credentials fail or network partitions occur.
- **Status:** *Approved Architecture Recommendation: Option A (Container Image Bundling).*
