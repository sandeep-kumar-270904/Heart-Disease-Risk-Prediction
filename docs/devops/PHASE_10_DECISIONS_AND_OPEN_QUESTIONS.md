# PHASE 10 DEVOPS DECISIONS AND OPEN GOVERNANCE QUESTIONS

**Document Reference:** `docs/devops/PHASE_10_DECISIONS_AND_OPEN_QUESTIONS.md`  
**Phase:** 10 — DevOps, Infrastructure, Deployment Architecture & Release Engineering  
**Status:** Approved Technical Ledger  
**Author:** Lead DevOps Architect & SRE Lead  
**Traceability:** All Phase 10 DevOps Specifications  

---

## 1. Executive Summary

This ledger records all foundational infrastructure, deployment, containerization, observability, and release engineering decisions finalized during Phase 10. It also catalogs open operational questions requiring stakeholder review before physical deployment scripts or cloud resources are provisioned.

---

## 2. Approved Architectural & Operational Decisions

| Decision ID | Domain | Approved Decision | Rationale & Justification |
| :--- :--- | :--- | :--- | :--- |
| **OPS-DEC-01** | **Orchestration** | **Docker Compose on a single hardened Linux cloud host (ADR-007).** | Kubernetes introduces immense operational complexity and failure modes unsuited for an individual developer or small team; Docker Compose guarantees environment parity with minimal maintenance. |
| **OPS-DEC-02** | **ML Runtime Boundary** | **In-process ML execution within FastAPI worker threads (ADR-001).** | Tabular XGBoost and TreeSHAP on 13 features execute in $< 115\text{ ms}$; separate microservices introduce network latency and distributed failure states without performance benefits. |
| **OPS-DEC-03** | **Container Base OS** | **`python:3.11-slim` for backend; `nginx:1.26-alpine` for frontend.** | Python wheels with C++ extensions (XGBoost, SciPy) link reliably with Debian `glibc`, avoiding Alpine `musl` compilation failures. |
| **OPS-DEC-04** | **Deployment Strategy** | **Blue-Green / Canary deployment with automated 15-minute rollback triggers.** | Reverts traffic to stable build if HTTP 5xx error rates exceed $1\%$ or latency exceeds $500\text{ ms}$, ensuring clinical system stability. |
| **OPS-DEC-05** | **Database Migrations** | **Expand-Contract forward-only pattern with pre-migration automated snapshots.** | Destructive rollbacks cause irreversible data loss; Expand-Contract guarantees backward compatibility and zero downtime. |
| **OPS-DEC-06** | **Backup Security** | **Nightly `pg_dump` with authenticated AES-256-GCM encryption to WORM storage (ADR-012).** | Guarantees ciphertext confidentiality and integrity; quarterly restore drills verify data recoverability. |
| **OPS-DEC-07** | **Log Privacy** | **Centralized regex scrubbing pipeline in `app/core/logging.py`.** | Strictly scrubs passwords, JWTs, and clinical vitals from log streams before disk or stdout emission. |
| **OPS-DEC-08** | **Country Localization**| **Standardized global container image; regional parameters injected via environment variables (ADR-011).** | Eliminates code branching per country; allows regional sovereign stacks to spin up in minutes. |

---

## 3. Open Governance Questions Requiring User Approval

The following items represent operational and financial choices requiring explicit stakeholder or user direction:

### Open Question 1: Hosting Provider & Budget Selection
- **Context:** Phase 10 provides two verified hosting profiles:
  - **Profile A (Minimal Budget / Showcase):** Single cloud VPS (DigitalOcean Droplet or Hetzner CPX31) with containerized PostgreSQL and Cloudflare Free Tier ($\approx \$17 - \$26 / \text{month}$).
  - **Profile B (Production Healthcare):** AWS EC2 `t4g.large` + AWS RDS PostgreSQL `db.t4g.medium` Multi-AZ + S3 with SSE-KMS ($\approx \$140 / \text{month}$).
- **Decision Required:** Which hosting profile should be selected for the initial project deployment?
- **Recommendation:** Profile A for academic defense, review demos, and prototype testing; upgrade to Profile B when onboarding real clinical users or executing formal healthcare pilots.

### Open Question 2: Cloudflare Edge Proxy Mode (Strict SSL vs DNS-Only)
- **Context:** Cloudflare provides global DDoS mitigation, WAF rules, and universal TLS termination. Operating in "Full (Strict)" proxy mode decrypts and re-encrypts traffic at Cloudflare's edge.
- **Decision Required:** Should Cloudflare proxy mode be enabled for all traffic, or should Cloudflare operate purely as an authoritative DNS provider with direct TLS termination at the host Nginx proxy?
- **Recommendation:** Cloudflare Proxy with Full (Strict) SSL enabled. Provides superior Layer 3/4 and Layer 7 DDoS mitigation and static asset caching while maintaining encrypted transport to the origin server.

### Open Question 3: Container Registry Provider
- **Context:** Immutable container images must be stored in an authenticated private container registry.
- **Options:**
  - Option 1: GitHub Container Registry (`ghcr.io`) — tightly integrated with GitHub Actions CI/CD; generous free tier for public/private repositories.
  - Option 2: AWS Elastic Container Registry (ECR) — native integration with AWS IAM.
- **Recommendation:** Option 1 (`ghcr.io`). Simplifies CI/CD pipelines, minimizes external dependencies, and eliminates cross-cloud credential hops.

---

## 4. Unresolved Operational Risks & Mitigation

| Operational Risk | Likelihood | Impact | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Single-Host Compute Outage (Tier A)** | Low | High | Automated nightly backups to offsite S3; codified Docker Compose and setup scripts enable re-provisioning on a fresh host in $< 45\text{ minutes}$. |
| **External Directory API Rate Limiting** | Medium | Medium | Country directory adapters implement Redis caching (24-hour TTL) and local static JSON fixture fallbacks. |
| **Third-Party Dependency Upstream Drift** | Low | High | All Python wheels pinned via `requirements.lock`; npm packages pinned via `package-lock.json`; container base images pinned to explicit digest tags. |

---

## 5. Phase Sign-Off Gate

The Phase 10 DevOps, Infrastructure, Deployment Architecture, and Release Engineering blueprint is complete across 18 technical documents in `docs/devops/`. 

**STOP GATE ENGAGED:** In accordance with Prompt 10 instructions, **no deployment code, Dockerfiles, Compose files, or cloud resources have been provisioned**. The system is halted awaiting formal review and approval.
