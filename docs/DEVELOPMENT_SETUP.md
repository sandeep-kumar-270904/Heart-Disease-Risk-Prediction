# HeartXAI 2.0 — Development Environment Setup Guide

This guide documents reproducible local development setup for **HeartXAI 2.0**, covering both containerized PostgreSQL 16 + Redis 7.2 workflows and the supported non-Docker local SQLite development path.

> [!WARNING]
> **Synthetic Data Only (`DEC-005`):** Never configure or ingest real patient health information (Category C) into any local or staging environment. Always keep `SYNTHETIC_DATA_ONLY=true`.

---

## 1. Required Software & Verified Versions

Verified local toolchain baseline on Windows / Linux:

| Tool | Minimum Required | Verified Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Python** | `3.11+` | `3.11.9` | FastAPI backend, ML pipelines, Pytest, Ruff, Mypy, Bandit |
| **Node.js** | `20 LTS+` | `v26.13.1` (`CI: 20`) | Frontend tooling & Vite bundler |
| **npm** | `10+` | `11.20.0` | Frontend dependency lockfile (`package-lock.json`) |
| **Git** | `2.40+` | `2.56.1` | Version control & hooks |
| **Docker & Compose** *(optional for native mode)* | Docker `26+`, Compose `v2.20+` | Docker `29.9.3`, Compose `v5.7.0` | PostgreSQL 16, Redis 7.2, and full 5-container stack |

---

## 2. Repository Setup

```bash
git clone https://github.com/sandeep-kumar-270904/Heart-Disease-Risk-Prediction.git heartxai-2.0
cd heartxai-2.0
git status
```

---

## 3. Frontend Installation

```bash
cd frontend
npm ci
```

---

## 4. Python Virtual Environment Setup & Backend/ML Installation

From `heartxai-2.0/`:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:
- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

Install dependencies:
- **Full Development, ML & QA Toolchain (recommended locally):**
  ```bash
  pip install --upgrade pip
  pip install -r requirements-dev.txt
  ```
- **Production Runtime Subset Only (`requirements.txt`):**
  ```bash
  pip install -r requirements.txt
  ```

---

## 5. Environment Variable Configuration

Copy `.env.example` to `.env` in the repository root (`.env` is gitignored and must never be committed):

```bash
cp .env.example .env
```

See [`docs/ENVIRONMENT_CONFIGURATION.md`](./ENVIRONMENT_CONFIGURATION.md) for every variable's purpose, requirement, and fail-closed rules.

---

## 6. Database Configuration (`PostgreSQL 16` or Non-Docker `SQLite`)

### Option A — Containerized PostgreSQL 16 + Redis 7.2 (Recommended)
Start local database and cache services defined in `docker-compose.yml`:
```bash
docker compose up -d
docker compose ps
```
*(Note: Ensure host ports `5432` and `6379` are free, or override `POSTGRES_PORT` / `REDIS_PORT` in `.env`.)*

### Option B — Non-Docker Local Development Path (SQLite Fallback)
If Docker Desktop is unavailable on your workstation:
1. In `backend/.env` or your shell environment, set:
   ```bash
   DATABASE_URL=sqlite:///./heartxai_dev.db
   ENVIRONMENT=development
   DEBUG=true
   SYNTHETIC_DATA_ONLY=true
   ```
2. **Important Limitation:** Automated test suites substitute `InMemoryTokenStore` for Redis (`test_auth.py`), whereas live `uvicorn` runtime routes (`/api/v1/auth/login`, `/refresh`, `/logout`, authenticated `/me`) require a reachable Redis server configured via `REDIS_URL` and fail closed with HTTP `503` when Redis is unreachable. Non-authenticated health probes (`/health/live`, `/health/ready`) and offline ML pipelines (`ml/pipelines/*.py`) run cleanly without Redis.

---

## 7. Redis Configuration

- Default local URL: `REDIS_URL=redis://localhost:6379/0` (Container-to-container inside `infra/docker-compose.yml`: `redis://cache:6379/0`).
- `RedisTokenStore` (`backend/app/core/redis_client.py`) strictly fails closed (raising HTTP `503 ServiceUnavailableError`) whenever Redis cannot be reached.

---

## 8. Database Migrations & Synthetic Seeding

From `backend/` (with your virtual environment activated and `DATABASE_URL` pointing to PostgreSQL 16 or SQLite):

```bash
cd backend
alembic upgrade head
```

Populate controlled Category B synthetic fixtures (RFC 2606 `@example.com` demo users, assessments, and regional directory entries):
```bash
python ../scripts/seed_synthetic_database.py --assessments 10 --seed 42
```

---

## 9. Running the Backend

From `backend/`:
```bash
uvicorn app.main:app --reload --port 8000
```

Verify probes:
- Root metadata: `http://localhost:8000/`
- Liveness: `http://localhost:8000/health/live`
- Readiness: `http://localhost:8000/health/ready`
- OpenAPI docs: `http://localhost:8000/docs`

---

## 10. Running the Frontend

From `frontend/`:
```bash
npm run dev
```
The Vite server proxies/calls `/api/v1/*` and renders on `http://localhost:5173`.

---

## 11. Running Automated Tests

See [`docs/TESTING_GUIDE.md`](./docs/TESTING_GUIDE.md) for the complete verification matrix. Quick commands:

```bash
# Backend & ML tests (runs against SQLite unless TEST_DATABASE_URL points to PostgreSQL)
pytest -c backend/pyproject.toml backend/tests/ ml/tests/ -v

# Frontend unit + axe-core WCAG accessibility tests
cd frontend && npm test
```

---

## 12. Common Setup Troubleshooting

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified` | Docker Desktop Windows service / WSL2 Linux engine is stopped | Start **Docker Desktop** GUI until `docker info` connects, or use non-Docker SQLite mode for unit tests / ML pipelines |
| `bind: Only one usage of each socket address` on port `5432` | Another local Postgres instance is already listening on `5432` | Set `POSTGRES_PORT=15432` in `.env` and update `DATABASE_URL` port accordingly |
| `ValueError: SECURITY CONFIG ERROR: SECRET_KEY...` on startup | `ENVIRONMENT` set to `staging` or `production` with default/short `SECRET_KEY` or `DEBUG=true` | Inject a strong `>=32` character random secret (not containing placeholder strings) and set `DEBUG=false` |
| HTTP `503 Session revocation store unavailable` during login | `RedisTokenStore` cannot reach `REDIS_URL` (intentional fail-closed behavior) | Start `redis` container (`docker compose up -d cache`) or run unit suite which uses `InMemoryTokenStore` |
| `Registration restricted to authorized RFC 2606 synthetic domains` (`422`) | Real email domain submitted to `/api/v1/auth/register` | Use `@example.com`, `@example.org`, or `@example.net` synthetic demo addresses only |
