# HeartXAI 2.0 — Post-Fix Live Stack Verification Report

**Repository:** `heartxai-2.0` (`https://github.com/sandeep-kumar-270904/Heart-Disease-Risk-Prediction.git`)  
**Branch:** `main`  
**Audited Commit:** `18419e7ae71a3ac968129f22c0cc8d2f17c1e722` (`HEAD` == `origin/main` == `refs/heads/main`)  
**Verification Date:** 25 November 2026  

---

## Executive Summary

| Verification Step | Status | Summary |
| :--- | :--- | :--- |
| **Step 1 — Repository State** | **PASSED** | `HEAD`, `origin/main`, and `git ls-remote origin main` all match `18419e7ae71a3ac968129f22c0cc8d2f17c1e722`. `infra/docker/Dockerfile.frontend` confirms `http://127.0.0.1:8080/`. |
| **Step 2 — Docker Desktop Availability** | **BLOCKED** | Docker Desktop Linux engine named pipe (`//./pipe/dockerDesktopLinuxEngine`) does not exist (`Test-Path` = `False`); `docker info` & `docker ps` failed to connect. Execution stopped per protocol without repeated restarts. |
| **Step 3 — Complete Compose Stack Rebuild & Health** | **NOT EXECUTED** | Blocked by Step 2 Docker Desktop daemon unavailability. |
| **Step 4 — Application Routing, TLS & Probes** | **NOT EXECUTED** | Blocked by Step 2 Docker Desktop daemon unavailability. |
| **Step 5 — Live Consent & Synthetic Boundaries** | **NOT EXECUTED** | Blocked by Step 2 Docker Desktop daemon unavailability. |
| **Step 6 — Encrypted Backup & Restore Integration** | **NOT EXECUTED** | Blocked by Step 2 Docker Desktop daemon unavailability. |

**Overall Deployment Readiness:** **NOT VERIFIED / BLOCKED** — Full-stack runtime, frontend healthcheck pass, TLS reverse-proxy routing, and live PostgreSQL backup/restore remain unverified until Docker Desktop's Linux engine is running on the host.

---

## Step 1 — Repository State (`PASSED`)

- **Command Executed:**
  ```powershell
  git rev-parse HEAD
  git rev-parse origin/main
  git ls-remote origin main
  git status -s
  Select-String -Path infra/docker/Dockerfile.frontend -Pattern "HEALTHCHECK|127.0.0.1"
  ```
- **Observed Output:**
  ```text
  18419e7ae71a3ac968129f22c0cc8d2f17c1e722
  18419e7ae71a3ac968129f22c0cc8d2f17c1e722
  18419e7ae71a3ac968129f22c0cc8d2f17c1e722	refs/heads/main
  ?? CONTROLLED_LIVE_INTEGRATION_VERIFICATION_REPORT.md
  ?? FRONTEND_HEALTHCHECK_REMEDIATION_REPORT.md

  infra\docker\Dockerfile.frontend:17:HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  infra\docker\Dockerfile.frontend:18:  CMD wget -qO- http://127.0.0.1:8080/ || exit 1
  ```
- **Findings:** Commit synchronization across local `HEAD`, `origin/main`, and remote `refs/heads/main` passed; existing reports and remediation changes are preserved untouched; no secrets are exposed.

---

## Step 2 — Docker Desktop Availability (`BLOCKED`)

- **Commands Executed:**
  ```powershell
  docker info --format "{{.ServerVersion}} ({{.OSType}})"
  docker ps -a --filter "name=heartxai"
  Test-Path "\\.\pipe\dockerDesktopLinuxEngine"
  ```
- **Observed Output:**
  ```text
  docker : failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.

  False
  ```
- **Blocker Diagnosis:** Docker Desktop's Linux engine daemon is not running (`\\.\pipe\dockerDesktopLinuxEngine` is absent; prior diagnostic showed `com.docker.service` stopped and no active `Docker` processes). Per Step 2 protocol, execution stopped here without performing repeated restart loops.

---

## Steps 3–6 — Runtime Checks Not Executed (`NOT EXECUTED`)

Because the Docker daemon is unavailable, all runtime verification steps requiring live containers remain **NOT EXECUTED** (`BLOCKED` on Step 2):

- **Step 3 (Complete Compose Stack Build & Health):** `infra/docker-compose.yml` rebuild of `frontend`, `backend`, `db`, `cache`, `proxy`, container health inspection (`heartxai-frontend` with `127.0.0.1:8080` fix), and container log review.
- **Step 4 (Application Routing & TLS):** Root `/`, `/dashboard` SPA deep-link fallback (`try_files`), frontend-to-backend Compose network connectivity, Nginx `:80 -> :443` HTTPS redirect, local dev TLS cert handling, `/health/live`, `/health/ready`, and HTTP status vs application auth separation.
- **Step 5 (Live Consent & Synthetic Data Boundaries):** Live HTTP tests for active/expired/revoked/wrong-doctor/wrong-patient grants, RFC 2606 synthetic registration domains, disabled clinician free-text notes, and synthetic boundary residual exposure analysis. *(Note: prior PostgreSQL 16 service and Redis 7.2 live checks from `CONTROLLED_LIVE_INTEGRATION_VERIFICATION_REPORT.md` ran before commit `18419e7` and before Docker Desktop stopped; live 5-container HTTP checks remain unexecuted.)*
- **Step 6 (Disposable Encrypted Backup & Restore):** Live `infra/scripts/backup_encrypted.sh` against synthetic PostgreSQL 16 DB, restore into a separate disposable DB, schema/row comparison, wrong-key rejection, ciphertext tamper check, and zero-plaintext-dump verification.

---

## Remaining Risks & Operator Action Required

1. **Docker Desktop Linux Engine Offline:** Start **Docker Desktop** interactively on Windows until `docker info --format "{{.ServerVersion}} ({{.OSType}})"` reports `linux` cleanly (ensuring WSL2 backend / `com.docker.service` is healthy).
2. **Untested `127.0.0.1:8080` Container Health Fix in Runtime:** Although `18419e7ae71a3ac968129f22c0cc8d2f17c1e722` changed the probe target to `http://127.0.0.1:8080/`, `heartxai-frontend` has not yet been rebuilt or observed transitioning to `healthy`.
3. **Working Tree Status:** `CONTROLLED_LIVE_INTEGRATION_VERIFICATION_REPORT.md`, `FRONTEND_HEALTHCHECK_REMEDIATION_REPORT.md`, and `POST_FIX_LIVE_VERIFICATION_REPORT.md` remain untracked deliverables (`??`) on disk.

### Verification Commands Ready Once Docker Desktop Is Running

```powershell
cd "c:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0"
docker info --format "{{.ServerVersion}} ({{.OSType}})"

# Set ephemeral isolated test variables in memory (never commit)
$env:SECRET_KEY = "replace_with_non_placeholder_test_secret_at_least_32_chars"
$env:TLS_CERT_DIR = "C:\Users\edhub\.gemini\antigravity\brain\34b3f633-16fc-42c5-a675-1321c2fbb04f\scratch\certs"

# Rebuild & verify all 5 services healthy
docker compose -f infra/docker-compose.yml up -d --build --wait
docker compose -f infra/docker-compose.yml ps
docker inspect --format "{{json .State.Health}}" heartxai-frontend
```
