# DEVOPS AND OPERATIONAL ACCEPTANCE CHECKLIST

**Document Reference:** `docs/devops/DEVOPS_ACCEPTANCE_CHECKLIST.md`  
**Phase:** 10 — DevOps, Infrastructure, Deployment Architecture & Release Engineering  
**Status:** Approved Technical Checklist & Operational Gate  
**Author:** Lead Site Reliability Engineer & Release Manager  
**Traceability:** All Phase 10 DevOps Specifications  

---

## 1. Executive Summary & Release Sign-Off Rule

Before any version of HeartXAI 2.0 can transition from development/staging to production, it must be evaluated against this comprehensive 50-point operational acceptance checklist. 

> [!CRITICAL]
> **Zero Critical Exception Rule:**  
> A release candidate failing any item marked **[BLOCKER]** is rejected immediately. No production traffic may be routed to an unverified build.

---

## 2. The 50-Point DevOps Acceptance Checklist

### Domain 1: Container Hardening & Packaging
- [ ] **01 [BLOCKER]** Containers execute strictly under unprivileged non-root users (`USER appuser:10001` in backend; `nginx:101` in frontend).
- [ ] **02 [BLOCKER]** Container base images are pinned to minimal distributions (`python:3.11-slim`, `nginx:1.26-alpine`).
- [ ] **03 [BLOCKER]** Multi-stage builds ensure zero compilers, build tools (`gcc`, `make`), or test libraries exist in production images.
- [ ] **04 [BLOCKER]** Trivy vulnerability scan reports **zero** unresolved Critical or High CVEs in container base images.
- [ ] **05 [BLOCKER]** Root filesystem is mounted read-only (`read_only: true`), with ephemeral writes restricted to in-memory `tmpfs`.
- [ ] **06** Image tags are tied to immutable Git commit SHAs (`sha-8d58df7`); the `:latest` tag is prohibited.
- [ ] **07** Docker resource limits (`cpus`, `memory`) are enforced for every container service in compose manifests.

### Domain 2: CI/CD Pipeline & Quality Gates
- [ ] **08 [BLOCKER]** GitHub Actions CI runs on all pull requests; direct pushes to `main` are blocked by branch protection.
- [ ] **09 [BLOCKER]** Code formatting passes with 100% compliance (`black --check .`, `prettier --check`).
- [ ] **10 [BLOCKER]** Static linting passes with zero warnings or errors (`ruff check .`, `eslint src/`).
- [ ] **11 [BLOCKER]** Static type checking passes in strict mode (`mypy --strict app/`, `tsc --noEmit`).
- [ ] **12 [BLOCKER]** Automated secret scanner (`gitleaks`) reports zero committed credentials, tokens, or keys.
- [ ] **13 [BLOCKER]** Security SAST scans (`bandit`, `semgrep`) report zero High/Critical security flaws.
- [ ] **14 [BLOCKER]** Dependency vulnerability scans (`pip-audit`, `npm audit`) report zero High/Critical CVEs.
- [ ] **15 [BLOCKER]** Pytest automated test suite achieves $\ge 80\%$ code coverage with 100% passing tests.
- [ ] **16** Staging deployment is automated on merge to `main`; production deployment requires manual approval.

### Domain 3: Database Deployment & Migration Safety
- [ ] **17 [BLOCKER]** PostgreSQL connection strings use TLS with root CA validation (`sslmode=verify-full`).
- [ ] **18 [BLOCKER]** Port 5432 is bound strictly to private VPC/bridge interfaces; zero public exposure (`0.0.0.0`).
- [ ] **19 [BLOCKER]** Database user `heartxai_app` operates with least privilege (DML only, zero DDL permissions).
- [ ] **20 [BLOCKER]** Alembic migrations enforce `SET lock_timeout = '5s'` to prevent exclusive table lock pileups.
- [ ] **21 [BLOCKER]** Schema migrations follow the Expand-Contract pattern, maintaining backward compatibility with running app versions.
- [ ] **22 [BLOCKER]** Automated point-in-time database snapshot is captured immediately before running DDL migrations.
- [ ] **23** Connection pooling configured with `pool_size=20`, `max_overflow=10`, `pool_pre_ping=True`.
- [ ] **24** Append-only audit logging trigger is verified active on `predictions` and `user_consents`.

### Domain 4: Machine Learning Artifact Governance
- [ ] **25 [BLOCKER]** Production model artifacts are serialized strictly in native JSON format (zero raw Python pickle loading).
- [ ] **26 [BLOCKER]** Application startup verifies SHA-256 digests and detached HMAC-SHA256 signatures before loading models.
- [ ] **27 [BLOCKER]** Candidate model has passed the 6-gate readiness checklist, beating L2-Logistic Regression on out-of-fold AUC.
- [ ] **28 [BLOCKER]** Startup lifespan warmup passes synthetic inference vector before opening container traffic.
- [ ] **29** TreeSHAP explainer background dataset uses verified 25 K-Medoids centroids.
- [ ] **30** Hot-rollback pointer (`HEARTXAI_ACTIVE_MODEL_VERSION`) tested and verified for instant model reversion.

### Domain 5: Network & Infrastructure Security
- [ ] **31 [BLOCKER]** Reverse proxy terminates TLS 1.3 exclusively with forward secrecy ciphers (`curve X25519`).
- [ ] **32 [BLOCKER]** HSTS header enforced with `max-age=63072000; includeSubDomains; preload`.
- [ ] **33 [BLOCKER]** Content Security Policy (CSP Level 3) active on all HTML deliveries.
- [ ] **34 [BLOCKER]** Perimeter rate limiting active on `/api/v1/auth/login` (5 req/min) and `/predictions` (10 req/min).
- [ ] **35 [BLOCKER]** Host firewall (UFW) drops all unsolicited inbound traffic; SSH permitted strictly via VPN bastion.
- [ ] **36** SSH configured with key-only auth (passwords disabled, root login disabled).
- [ ] **37** Automated unattended security upgrades (`unattended-upgrades`) active on host OS.

### Domain 6: Observability, Logging & Health Checks
- [ ] **38 [BLOCKER]** Automated logging filter verifies zero passwords, JWTs, or clinical vitals in log streams.
- [ ] **39 [BLOCKER]** Every HTTP request traces with unique `X-Correlation-ID` across proxy, backend, and database logs.
- [ ] **40 [BLOCKER]** `/health/live` probe verified responding in $< 1\text{ ms}$.
- [ ] **41 [BLOCKER]** `/health/ready` probe verifies PostgreSQL, Redis, and ML model warmup before returning HTTP 200.
- [ ] **42** Prometheus metrics endpoint (`/metrics`) active and scrapable by internal monitoring only.
- [ ] **43** Automated alert rules configured for error rate spikes ($> 1\%$) and latency breaches ($P95 > 200\text{ ms}$).

### Domain 7: Backup, Disaster Recovery & BCP
- [ ] **44 [BLOCKER]** Nightly PostgreSQL logical backups encrypted via authenticated AES-256-GCM.
- [ ] **45 [BLOCKER]** Backup archives replicate to an offsite, immutable WORM storage bucket with 30-day retention lock.
- [ ] **46 [BLOCKER]** Continuous WAL archiving enabled, supporting point-in-time recovery with $\text{RPO} \le 1.0\text{ hour}$.
- [ ] **47 [BLOCKER]** Automated restoration rehearsal executed within the last 90 days, confirming $\text{RTO} \le 4.0\text{ hours}$.
- [ ] **48** Master encryption keys replicated across multi-region KMS with offline paper escrow backup.

### Domain 8: Global Configuration & Documentation
- [ ] **49 [BLOCKER]** Country configuration parameters injected via runtime environment variables (ADR-011).
- [ ] **50 [BLOCKER]** Runbooks documented for deployment, rollback, disaster recovery, and SSL renewal.

---

## 3. Operational Sign-Off Protocol

A release candidate is approved for production deployment **only** upon completion of this sign-off ledger:

| Role | Name | Digital Signature / Approval Token | Date (UTC) |
| :--- | :--- | :--- | :--- |
| **Lead DevOps / SRE Architect** | ____________________ | `SRE-SIGNOFF-VERIFIED` | ____________________ |
| **Lead Software Architect** | ____________________ | `ARCH-SIGNOFF-VERIFIED` | ____________________ |
| **Security & Privacy Lead** | ____________________ | `SECOPS-SIGNOFF-VERIFIED` | ____________________ |
