# HeartXAI 2.0 — Explainable Cardiovascular Research & Synthetic Decision-Support Platform

> [!IMPORTANT]
> **Investigational Prototype — Not Clinically Validated & Not Production Ready.**
> HeartXAI 2.0 operates strictly on **Category B synthetic personas and fixtures** (`SYNTHETIC_DATA_ONLY=true`). Real patient health information (Category C) is prohibited across MVP registration, clinical intake, clinician sharing, and exports. Model outputs measure similarity to the historical retrospective UCI Cleveland dataset (`N=303`) and **never constitute a medical diagnosis, risk tier, treatment plan, or prospective 10-year ASCVD risk prediction**.

---

## 1. Project Overview & Current Status

HeartXAI 2.0 pairs a FastAPI backend, in-process calibrated XGBoost inference (`Task A` retrospective CAD binary classification), exact TreeSHAP log-odds feature attributions, constrained hypothetical "what-if" input exploration, and a React + TypeScript + Tailwind SPA.

- **Current Phase:** **Phase 13 — Repository Foundation & Development Environment Implementation** (following Milestone 01–20 scaffolding, Implementation Integrity Audit, Critical Remediation Round 01, Controlled Live PG 16 / Redis 7 Verification, and Frontend Healthcheck Remediation).
- **Governance Baseline (`DEC-001`–`DEC-005` Option A):**
  - `DEC-003`: Strictly **Task A** retrospective UCI Cleveland binary classification (`ten_year_population_risk_percent` is `null` in MVP).
  - `DEC-004`: Configurable country adapter schema (`US`, `IN`, `GB`, `DEFAULT`) for units (`mg/dL` $\leftrightarrow$ `mmol/L`) and synthetic directory demos.
  - `DEC-005`: Synthetic-only MVP enforced server-side (RFC 2606 domains `@example.com`/`@example.org`/`@example.net`, mandatory synthetic attestation flags, and disabled arbitrary clinician free-text notes).
- **Clinical Review Gate (`DEC-002`):** Automated red-flag triage, `30%`/`70%` risk tiering, and country emergency `tel:` quick-dial remain disabled pending physician advisory review. No clinical validation or regulatory clearance is claimed.

---

## 2. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 18 (`^18.3.1`), TypeScript (`^5.4.5`), Vite (`^5.4.11`), Tailwind CSS (`^3.4.15`), Radix UI, Zustand, Zod, React Router v7, Lucide Icons |
| **Backend** | Python 3.11, FastAPI (`0.111.0`), Pydantic v2 (`2.13.4`), SQLAlchemy 2.0 (`2.0.30`), Alembic (`1.17.2`), Argon2id (`argon2-cffi`), PyJWT, ReportLab |
| **Data & Cache** | PostgreSQL 16 (`postgres:16-alpine`), Redis 7.2 (`redis:7.2-alpine`), SQLite fallback for local unit tests |
| **ML & XAI** | Scikit-learn, XGBoost (`3.1.2`), SHAP (`TreeExplainer`), Pandas, NumPy, PyArrow, Joblib |
| **Infrastructure & QA** | Docker, Docker Compose, Nginx (`1.26-alpine`), Pytest, Vitest, `vitest-axe`, Ruff, ESLint, Mypy (`--strict`), Bandit, GitHub Actions |

---

## 3. High-Level Architecture

```text
Browser SPA (React + Vite)
   │  HTTPS / TLS (Nginx :443, :80 -> 301 HTTPS)
   ▼
FastAPI Monolith (/api/v1/* + /health/{live,ready})
   ├── Auth & RBAC (Argon2id + 15m Memory JWT + 7d HttpOnly Refresh Cookie)
   ├── Redis 7.2 TokenStore (Fail-Closed Family Rotation, Replay Wipe & Blacklist)
   ├── In-Process Task A ML Engine (XGBoost + OOF Platt + TreeSHAP + Hypothetical CF)
   ├── 72-Hour Consent Service (Strict UTC Expiry + Revocation Guard)
   ├── ReportLab 2-Page PDF Dossier Export (SHA-256 Content Seal)
   └── PostgreSQL 16 (UUIDv7 Keys, Numeric FBS + UCI fbs Flag, Append-Only Audit Logs)
```

---

## 4. Repository Structure

A full directory breakdown is documented in [`docs/REPOSITORY_STRUCTURE.md`](./docs/REPOSITORY_STRUCTURE.md). Top-level layout:

- `frontend/` — React SPA source, Radix UI primitives, Tailwind tokens, Vitest + `vitest-axe` tests, Vite build config
- `backend/` — FastAPI routes, Pydantic schemas, SQLAlchemy 2.0 models, Alembic migrations (`001`–`003`), services, in-process ML runtime, Pytest suite
- `ml/` — Category A UCI Cleveland raw data, leakage-free preparation, Task A training/calibration, evaluation scripts, model registry, ML tests
- `shared/` — Canonical SSOT JSON definitions (`data-dictionary.json`, `country-profiles.json`)
- `scripts/` — Synthetic fixture generator, DB seeder, empirical performance benchmark, AES-256-GCM AEAD backup utility
- `infra/` — Multi-stage Dockerfiles, `infra/docker-compose.yml`, Nginx TLS reverse proxy config, encrypted backup/restore bash scripts, K6 script
- `tests/` — Playwright synthetic patient E2E specification
- `docs/` — Phase 13 operational setup/testing/contributing guides plus archived Phase 1–12 design & governance specifications

---

## 5. Quickstart & Standard Commands

See [`docs/DEVELOPMENT_SETUP.md`](./docs/DEVELOPMENT_SETUP.md) for complete setup instructions (both containerized Postgres/Redis and local non-Docker Python development) and [`docs/ENVIRONMENT_CONFIGURATION.md`](./docs/ENVIRONMENT_CONFIGURATION.md) for variable details.

### Frontend Commands (`cd frontend`)
```bash
npm ci                 # Install dependencies from package-lock.json
npm run dev            # Start Vite dev server
npm run typecheck      # tsc --noEmit
npm run lint           # eslint --max-warnings 0 (includes jsx-a11y)
npm test               # vitest run (unit + vitest-axe a11y checks)
npm run build          # Production tsc --noEmit && vite build
```

### Backend & ML Commands
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS:        source .venv/bin/activate
pip install --upgrade pip && pip install -r requirements-dev.txt

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

From repository root (`heartxai-2.0/`):
```bash
ruff check backend/ ml/ scripts/
ruff format --check backend/ ml/ scripts/
cd backend && mypy --strict app/core app/schemas app/ml app/services app/api/v1/routes app/main.py
cd .. && pytest backend/tests/ ml/tests/ -v
bandit -r backend/app -ll -ii
```

---

## 6. Documentation Index

### Phase 13 Foundation Guides
- [`docs/DEVELOPMENT_SETUP.md`](./docs/DEVELOPMENT_SETUP.md) — Step-by-step prerequisites, installation, migrations, local vs Docker runs, and troubleshooting
- [`docs/ENVIRONMENT_CONFIGURATION.md`](./docs/ENVIRONMENT_CONFIGURATION.md) — Environment variable reference, secret hygiene, and fail-closed validation
- [`docs/REPOSITORY_STRUCTURE.md`](./docs/REPOSITORY_STRUCTURE.md) — Directory-by-directory responsibilities across frontend, backend, ML, and infra
- [`docs/TESTING_GUIDE.md`](./docs/TESTING_GUIDE.md) — Unit, ML reproducibility, accessibility, static security, and live integration test procedures
- [`docs/CONTRIBUTING.md`](./docs/CONTRIBUTING.md) — Branching, Conventional Commits, quality gates, and governance/PHI compliance rules

### Verification & Audit Reports (Root)
- [`IMPLEMENTATION_INTEGRITY_AND_VALIDATION_AUDIT.md`](./IMPLEMENTATION_INTEGRITY_AND_VALIDATION_AUDIT.md)
- [`CRITICAL_REMEDIATION_ROUND_01_REPORT.md`](./CRITICAL_REMEDIATION_ROUND_01_REPORT.md)
- [`CONTROLLED_LIVE_INTEGRATION_VERIFICATION_REPORT.md`](./CONTROLLED_LIVE_INTEGRATION_VERIFICATION_REPORT.md)
- [`FRONTEND_HEALTHCHECK_REMEDIATION_REPORT.md`](./FRONTEND_HEALTHCHECK_REMEDIATION_REPORT.md)
- [`POST_FIX_LIVE_VERIFICATION_REPORT.md`](./POST_FIX_LIVE_VERIFICATION_REPORT.md)

### Phase 1–12 Historical Specifications
- [`docs/phase-12-final/`](./docs/phase-12-final/) — Governance decisions (`PROJECT_DECISION_REGISTER.md`), roadmap (`MASTER_IMPLEMENTATION_ROADMAP.md`), and verification reports.
