# HeartXAI 2.0 — Controlled Live Integration & Deployment Verification Report

**Repository:** `heartxai-2.0` (`https://github.com/sandeep-kumar-270904/Heart-Disease-Risk-Prediction.git`)  
**Branch:** `main`  
**Verified Remediation Commits:** `5423e71349824fd05aedf34aa588581ba113c68b`, `67d5e7aebfb45d4563a77df733ecaa581ba113c68b`  
**Verification Date:** 25 November 2026  

---

## Status Legend

- **PASSED** — Executed directly against the real target service with observed passing output.
- **PARTIALLY PASSED** — Some checks passed against real services/scans; others failed or were blocked.
- **FAILED** — An actual runtime or security failure was observed during live execution.
- **BLOCKED** — Prerequisites or local container runtime became unavailable during verification.
- **NOT EXECUTED** — Tooling or prerequisites were absent and the check was not run.

---

## Executive Summary

| Verification Area | Status | Key Observed Result |
| :--- | :--- | :--- |
| **1. Pre-Flight** | **PARTIALLY PASSED** | Git state verified (`67d5e7a`, clean tree); Docker `29.9.3` & Compose `v5.7.0` available in Phase 1, then unavailable after host restart (`com.docker.service Stopped`). |
| **2. PostgreSQL 16 Integration** | **PASSED** | `PostgreSQL 16.16` (`postgres:16-alpine`): Alembic `001->002->003`, rollback/upgrade, FK & unique constraints, UUIDv7, synthetic seeding, FBS `168.75`, consent revocation, and **11/11 pytest DB tests passed**. |
| **3. Redis 7 Integration** | **PASSED** | `Redis 7.2.17` (`redis:7.2-alpine`): real `RedisTokenStore` registration, rotation, replay wipe, 1s TTL expiry, logout JTI blacklist, **live container stop → HTTP 503 fail-closed**, **container restart → HTTP 200 recovery**. |
| **4. Full Docker Compose Stack** | **FAILED** | `infra-backend` built & `healthy`, `db`/`cache`/`proxy` started, **but `heartxai-frontend` failed healthcheck (`unhealthy`)**; subsequent Docker engine loss blocked live proxy/HTTPS calls. |
| **5. Consent Auth Over Live HTTP** | **BLOCKED** | Prepared in scratch `verify_live_http_e2e.py`; blocked when Docker Desktop daemon failed to reconnect after host restart (unit `TestClient` passed `51/51`, not counted as live Compose HTTP). |
| **6. Synthetic Data Boundary** | **BLOCKED** *(Live HTTP)* | Registration/assessment synthetic gates verified against `PG 16` service calls in Section 2 & `TestClient` tests; live proxy HTTP round-trip blocked by Docker outage. |
| **7. Backup & Restore Integration** | **BLOCKED** | AES-256-GCM helper verified in unit tests (`test_priority_5d_*`), but live `backup_encrypted.sh` / `restore_encrypted.sh` against `heartxai-staging-db` blocked by Docker outage. |
| **8. Playwright E2E Testing** | **NOT EXECUTED / BLOCKED** | Neither `@playwright/test` nor Python `playwright` is installed; live stack unavailable. |
| **9. Dependency & Security Validation** | **PARTIALLY PASSED** | Bandit **0 High/0 Medium** (`3,470` LOC), `npm audit --omit=dev` **0 vulns**, `npm audit` (dev) **6 advisories (2 critical)**; `51/51` Python + `24/24` frontend tests pass; `pip-audit` & ZAP **NOT EXECUTED**. |

---

## 1. Pre-Flight — **PARTIALLY PASSED**

- **Commands & Observed Output:**
  - `git branch --show-current` → `main`
  - `git rev-parse HEAD` → `67d5e7aebfb45d4563a77df733ecaa5aff978748`
  - `docker --version` → `Docker version 29.9.3, build 5457199`
  - `docker compose version` → `Docker Compose version v5.7.0`
  - `netstat -ano` → Port `5432` occupied on host by unrelated existing container `ai_reviewer_db` (`ankane/pgvector:latest`); ports `80` and `443` free.
- **Isolation & Secret Handling:**
  - Inspected `.env.example` and `.gitignore`; supplied ephemeral runtime env vars (`SECRET_KEY`, `TLS_CERT_DIR`) in shell memory without printing secret values or modifying `.env`.
  - Generated an isolated local dev self-signed X.509 cert (`localhost`, `127.0.0.1`) solely inside non-repo scratch storage (`<appDataDir>/brain/.../scratch/certs/`) alongside ephemeral port override `compose-ports.override.yml` (`15432:5432`, `16379:6379`) to avoid touching `ai_reviewer_db`.
- **Limitation / Blocker:** Following a system/server restart at `14:25 UTC` (`19:55 IST`), `com.docker.service` stopped and `docker desktop status` / `docker info` failed (`open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`), blocking remaining container-dependent checks (Sections 4–8). Also sandbox offline DNS blocked `git ls-remote origin main` in the final check (`Could not resolve host: github.com`).

---

## 2. PostgreSQL 16 Integration — **PASSED**

- **Service Version:** `PostgreSQL 16.16 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit` (`postgres:16-alpine`, container `heartxai-staging-db`, status: `healthy`).
- **Commands Executed:**
  1. `docker compose -f infra/docker-compose.yml -f ".../scratch/compose-ports.override.yml" up -d db cache --wait`
  2. `python ".../scratch/verify_live_db_redis.py"` (`verify_postgres()`)
  3. `$env:TEST_DATABASE_URL="postgresql://heartxai_user:heartxai_password@localhost:15432/heartxai_db"; pytest backend/tests/test_migrations_and_seeding.py backend/tests/test_database_models.py -v`
- **Observed Outputs:**
  - `alembic` ran cleanly on empty schema (`001_initial_schema -> 002_milestone_04_governance_geo -> 003_remediation_round_01`), verified `15` tables (including `alembic_version` and `assessments.fasting_blood_sugar_mgdl`), and completed `downgrade 002 -> upgrade head` (`ALEMBIC_UPGRADE_DOWNGRADE_UPGRADE_OK`).
  - `SEED_COUNTS: {'users_created': 3, 'assessments_created': 5, 'doctors_created': 3, 'hospitals_created': 3, 'policies_created': 2, 'resources_created': 2}`
  - `PG_FOREIGN_KEY_ENFORCED_OK` (orphan `Assessment` rejected with `IntegrityError`)
  - `PG_UNIQUE_CONSTRAINT_ENFORCED_OK` (duplicate `email` rejected with `IntegrityError`)
  - `PG_TRANSACTION_ROLLBACK_OK` (user count preserved after `flush()` + `rollback()`)
  - `PG_UUIDV7_PERSISTED: 01a20f71-86f5-719b-87af-25700c932c6d` (RFC 9562 version `7`)
  - `PG_ASSESSMENT_ROUNDTRIP_FBS_OK: 01a20f71-8ac7-7647-9403-dc2f9ee6ad21 168.75`
  - `PG_CONSENT_GRANT_REVOCATION_OK: 01a20f71-8b11-75fe-9c94-30ac4bafd3ca REVOKED`
  - `pytest` live PostgreSQL run: **`11 passed in 6.52s`** (`test_migrations_and_seeding.py`: 4 tests, `test_database_models.py`: 7 tests).
- **Evidence Location:** `.system_generated/steps/3203/output.txt`, `.system_generated/steps/3215/output.txt`.

---

## 3. Redis 7 Integration — **PASSED**

- **Service Version:** `Redis server v=7.2.17 sha=00000000:0 malloc=jemalloc-5.3.0 bits=64 build=78143de4b56fc5bb` (`redis:7.2-alpine`, container `heartxai-staging-cache`, status: `healthy`).
- **Implementation Tested:** Real `app.core.redis_client.RedisTokenStore` (`redis://localhost:16379/0`), **zero** `InMemoryTokenStore` substitution.
- **Command Executed:** `python ".../scratch/verify_live_db_redis.py"` (`verify_redis()`)
- **Observed Outputs:**
  - `REDIS_VERSION: 7.2.17`
  - `REDIS_REGISTER_FAMILY_OK` (`auth:family:{id}:active` stored with TTL > 0)
  - `REDIS_ROTATE_OK` (atomic rotation from `jti-1` to `jti-2`)
  - `REDIS_REPLAY_WIPED_FAMILY_OK: Refresh token reuse detected. Session token family invalidated.` (reusing `jti-1` deleted family key from Redis)
  - `REDIS_TTL_EXPIRY_REJECTED_OK` (`ttl_seconds=1` expired in Redis after `1.3s`, raising `AuthenticationError`)
  - `REDIS_HTTP_ROTATE_LOGOUT_BLACKLIST_OK` (`/api/v1/auth/login` → `/refresh` → `/logout` blacklisted access JTI in Redis, rejecting subsequent `/api/v1/auth/me` with `401`)
  - **`REDIS_OUTAGE_FAIL_CLOSED_503_OK`** (`docker stop heartxai-staging-cache` → `/api/v1/auth/me` failed closed with **HTTP 503**)
  - **`REDIS_RECONNECT_RECOVERY_200_OK`** (`docker start heartxai-staging-cache` → `/api/v1/auth/me` recovered **HTTP 200**)
- **Evidence Location:** `.system_generated/steps/3215/output.txt`.

---

## 4. Full Docker Application Startup — **FAILED**

- **Command Executed:** `docker compose -f infra/docker-compose.yml -f ".../scratch/compose-ports.override.yml" up -d --build --wait`
- **Observed Results (`docker compose ps`):**
  - `infra-backend`: Built cleanly (`python:3.11-slim` + pip deps + `shared` + `ml/registry`); container `heartxai-backend` reached `Up 45 seconds (healthy)`.
  - `infra-frontend`: Built cleanly (`node:20-alpine` Vite build → `nginxinc/nginx-unprivileged:1.26-alpine`); container `heartxai-frontend` reached `Up 46 seconds (unhealthy)` → Compose exited with code `1`: **`container heartxai-frontend is unhealthy`**.
  - `heartxai-proxy` (`nginx:1.26-alpine`): `Up 40 seconds` (`0.0.0.0:80->80`, `0.0.0.0:443->443`).
  - `heartxai-staging-db` (`postgres:16-alpine`): `healthy` (`15432->5432`).
  - `heartxai-staging-cache` (`redis:7.2-alpine`): `healthy` (`16379->6379`).
- **Root Cause Identified for `heartxai-frontend` Unhealthy Status:**
  - [Dockerfile.frontend](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/docker/Dockerfile.frontend#L16-L17) probes `wget -qO- http://localhost:8080/`, while [nginx.frontend.conf](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/infra/docker/nginx.frontend.conf#L2) configures `listen 8080;` (IPv4 only, missing `listen [::]:8080;`). On Alpine Linux, `localhost` resolves to IPv6 `::1`, causing the healthcheck probe to fail. (Fix deferred to next remediation round: bind `[::]:8080` or probe `http://127.0.0.1:8080/`.)
- **Blocked Sub-Checks (due to subsequent Docker daemon outage after host restart):** Live HTTP calls to `https://localhost/health/ready`, `proxy` `:80->:443` redirect, `HSTS`/`Secure` cookie flags, and SPA deep-link `/dashboard` refresh (`scratch/verify_live_http_e2e.py`) were **NOT EXECUTED** (`BLOCKED`).
- **Evidence Location:** `.system_generated/steps/3224/output.txt`.

---

## 5. Consent Authorization Regression (Live HTTP) — **BLOCKED**

- **Live Compose HTTP Status:** **BLOCKED** (`verify_live_http_e2e.py` against `https://localhost/api/v1/*` could not run because `heartxai-frontend` failed startup and Docker Desktop pipe became unavailable after host restart).
- **Non-Substitute Context (Unit/Integration `TestClient` + SQLite only):** All 51 tests in `pytest backend/ ml/tests/` (including `test_priority_1_authoritative_consent_blocks_expired_revoked_and_exact_boundary`) passed locally after this session, covering active, expired, revoked, exact-expiry boundary, wrong clinician, wrong patient, and cross-tenant `403` isolation, but those use `TestClient` + SQLite + `InMemoryTokenStore`, **not** live HTTP through Nginx + Postgres 16 + Redis 7.

---

## 6. Synthetic Data Boundary (Live Endpoints) — **BLOCKED** *(Live HTTP)* / **PARTIALLY PASSED** *(PG Service)*

- **Verified Against Live PostgreSQL 16 (Section 2):** `create_and_score_assessment` succeeded for `patient.demo@example.com` with `synthetic_fixture_confirmed=True` and preserved `168.75 mg/dL`.
- **Blocked Over Live Docker HTTP:** Live HTTP verification of `/api/v1/auth/register` RFC 2606 domain rejection (`@gmail.com` → `422`), missing `synthetic_persona_acknowledged` (`422`), disabled `/notes` (`422`), and assessment attestation over Nginx HTTPS (`verify_live_http_e2e.py`) was **BLOCKED** by Docker daemon unavailability.
- **Residual Boundary Observations for Review:**
  - Seeded demo accounts (`patient.demo@example.com`, `clinician.demo@example.com`, `admin.demo@example.com`) remain active synthetic fixtures in `seed_synthetic_database.py` with documented demo passwords (`SYNTHETIC_DATA_ONLY=true`); any account registered under `@example.com` / `@example.org` / `@example.net` can submit numeric clinical inputs up to Pydantic physiological bounds.

---

## 7. Backup and Restore Integration — **BLOCKED**

- **Live Container Execution:** **BLOCKED** (`infra/scripts/backup_encrypted.sh` and `infra/scripts/restore_encrypted.sh` could not execute `docker exec heartxai-staging-db pg_dump` / `psql` because Docker daemon became unreachable after host restart).
- **Unit Verification Context (Not Counted as Live DB DR Readiness):** `test_priority_5d_backup_aes256_gcm_roundtrip_wrong_key_and_tamper` passed on `scripts/backup_aead.py` (`AES-256-GCM` encryption, restore, wrong-key `InvalidTag`, 1-byte tamper detection, zero temp files), but end-to-end `pg_dump | gzip | backup_aead.py` and `psql` restoration of real PostgreSQL 16 tables/rows remain **unverified live**.

---

## 8. Playwright End-to-End Testing — **NOT EXECUTED** (`BLOCKED`)

- **Command Checked:** `npx --no-install playwright --version` & `python -m pip show playwright` → failed offline DNS / `WARNING: Package(s) not found: pip-audit, playwright`.
- **Status:** **NOT EXECUTED**. [synthetic_patient_journey.spec.ts](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/tests/e2e/synthetic_patient_journey.spec.ts) could not run due to absent Playwright installation and stopped/unhealthy Docker stack.

---

## 9. Dependency and Security Validation — **PARTIALLY PASSED**

| Check | Command | Outcome | Status |
| :--- | :--- | :--- | :--- |
| **Bandit SAST** | `bandit -r backend/app -ll -ii` | **0 High, 0 Medium**, 6 Low, `0 #nosec`, `3,470` LOC | **PASSED** |
| **Backend & ML Suite** *(SQLite/InMemory)* | `pytest backend/ ml/tests/` | **51 passed, 0 failed** in `16.81s` | **PASSED** *(Mock/SQLite scope)* |
| **Python Lint** | `ruff check backend/ ml/ scripts/` | **All checks passed!** | **PASSED** |
| **Frontend Suite & Build** | `npm run typecheck`, `npm run lint`, `vitest run`, `vite build` | `0` TS errors, `0` ESLint warnings, **5 files / 24 tests passed** (`15.36s`), bundle built | **PASSED** *(jsdom scope)* |
| **`npm audit` (Production Runtime)** | `npm audit --omit=dev` *(via `task-3249`)* | `found 0 vulnerabilities` | **PASSED** |
| **`npm audit` (Full incl. DevDeps)** | `npm audit` *(via `task-3249`)* | **6 vulnerabilities (3 moderate, 1 high, 2 critical)** in `@vitest/mocker <=4.1.11`, `esbuild <=0.24.2`, `tinypool <=2.1.1` (transitive in `vitest`/`vite` dev toolchain; requires major `vite@8` / `vitest@5` bump) | **FAILED / ADVISORIES PRESENT** |
| **`pip-audit`** | `python -m pip show pip-audit` | Package not installed | **NOT EXECUTED** |
| **OWASP ZAP Baseline** | `where.exe zap.sh` | Binary not installed & Docker daemon unavailable | **NOT EXECUTED** |

*(Evidence locations: `.system_generated/steps/3249/output.txt`, `.system_generated/steps/3259/output.txt`, `.system_generated/steps/3209/output.txt`.)*

---

## 10. Actionable Blockers & Required Next Steps Before Acceptance

1. **Fix `heartxai-frontend` Healthcheck (`infra/docker/nginx.frontend.conf` / `Dockerfile.frontend`):** Add `listen [::]:8080;` or probe `http://127.0.0.1:8080/` so `heartxai-frontend` passes Docker health checks cleanly.
2. **Start Docker Desktop Service & Execute Blocked Live Tests:** Ensure `com.docker.service` / Docker Desktop GUI is running cleanly, bring up all 5 containers (`--wait`), and execute:
   - `verify_live_http_e2e.py` (Sections 4, 5 & 6 over live Nginx HTTPS + PostgreSQL 16 + Redis 7.2)
   - Live `infra/scripts/backup_encrypted.sh` + wrong-key/tamper + `restore_encrypted.sh` against `heartxai-staging-db` (Section 7)
3. **Install & Execute Missing Verification Tooling:** Run Playwright against the healthy 5-container stack (Section 8), install/run `pip-audit` in a staging/CI Python environment, execute OWASP ZAP baseline against Nginx, and assess upgrading `vitest`/`vite` devDependencies to clear the 6 dev advisories.
