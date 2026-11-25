# HeartXAI 2.0 — Repository Structure & Separation of Responsibilities

This document maps the directory layout of `heartxai-2.0` across Frontend, Backend, ML, Infrastructure, Shared Contracts, Tests, and Documentation.

---

## Top-Level Directory Map

```text
heartxai-2.0/
├── .github/workflows/ci.yml    # GitHub Actions CI (lint, mypy, vitest, bandit, postgres pytest, compose)
├── .editorconfig               # Cross-editor LF line endings, indentation, UTF-8
├── .env.example                # Non-secret environment template
├── .gitignore                  # Excludes venvs, .env, certs, dumps, backups/, build outputs
├── .pre-commit-config.yaml     # Local git hook checks (whitespace, JSON/YAML, private keys, Ruff)
├── docker-compose.yml          # Local PostgreSQL 16 & Redis 7.2 development containers
├── README.md                   # Project overview, boundaries & quickstart
├── shared/                     # Single-source-of-truth canonical JSON contracts
├── frontend/                   # React 18 + TypeScript + Vite + Tailwind SPA
├── backend/                    # FastAPI monolith, SQLAlchemy models, Alembic migrations, ML serving
├── ml/                         # Category A research data, training/evaluation pipelines & model registry
├── infra/                      # Production/staging Dockerfiles, 5-service Compose, Nginx TLS & backup scripts
├── scripts/                    # Synthetic generators, seeders, benchmarks & AES-256-GCM AEAD CLI
├── tests/                      # End-to-end Playwright synthetic journey specification
└── docs/                       # Phase 13 guides & historical Phase 1–12 design/governance records
```

---

## Subsystem Breakdown

### 1. Frontend (`frontend/`)
| Path | Responsibility |
| :--- | :--- |
| `frontend/src/App.tsx`, `main.tsx` | Application entry point and route configuration (`BrowserRouter`, `AppRoutes`) |
| `frontend/src/routes/ProtectedRoute.tsx` | Authenticated route wrapper |
| `frontend/src/components/layout/AppShell.tsx` | Global persistent synthetic-data watermark, skip link, navigation & footer |
| `frontend/src/components/ui/` | Reusable WCAG 2.2 AA Radix UI + Tailwind primitives (`Alert`, `Badge`, `Button`, `Card`, `Input`, `Modal`, `Select`, `Tooltip`) |
| `frontend/src/features/` | Domain feature slices: `auth/`, `intake/`, `assessment/`, `directory/`, `doctor/`, `admin/` |
| `frontend/src/services/apiClient.ts` | Fetch wrapper with single-flight silent refresh on `401` |
| `frontend/src/stores/authStore.ts` | Zustand in-memory access JWT and user session store |
| `frontend/src/types/` | TypeScript DTOs mirroring `backend/app/schemas/` |
| `frontend/src/lib/` | Utility helpers (`cn.ts`, `unitConverter.ts`) |
| `frontend/src/tests/`, `**/__tests__/` | Vitest + Testing Library + `vitest-axe` accessibility and component tests |

### 2. Backend (`backend/`)
| Path | Responsibility |
| :--- | :--- |
| `backend/app/main.py` | FastAPI app factory, correlation-ID middleware, CORS & canonical `/api/v1` + health probe mounts |
| `backend/app/core/` | `config.py` (fail-closed Pydantic settings), `database.py`, `errors.py` (RFC 7807), `logging.py`, `redis_client.py` (`RedisTokenStore`), `security.py` (Argon2id + JWT) |
| `backend/app/api/v1/` | `deps.py` (`get_current_user`, `require_role`) and route modules (`auth.py`, `assessments.py`, `consents.py`, `directory.py`, `admin.py`, `health.py`) |
| `backend/app/models/` | SQLAlchemy 2.0 ORM entities (`base.py` UUIDv7, `user.py`, `assessment.py`, `consent.py`, `directory.py`, `audit.py`) |
| `backend/alembic/versions/` | Database migrations `001_initial_schema.py`, `002_milestone_04_governance_geo.py`, `003_remediation_round_01.py` |
| `backend/app/schemas/` | Strict Pydantic v2 contracts (`extra="forbid"`, unit normalization, RFC 2606 synthetic domain check) |
| `backend/app/services/` | Domain services (`auth_service.py`, `assessment_service.py`, `consent_service.py`, `directory_service.py`, `export_service.py`, `audit_service.py`) |
| `backend/app/ml/` | In-process inference (`inference_service.py`), TreeSHAP (`shap_service.py`), constrained counterfactuals (`counterfactual_service.py`), and `artifacts/` |
| `backend/tests/` | Unit & integration tests (`conftest.py`, auth, security, migrations, ML serving, consent, remediation tests) |

### 3. Machine Learning (`ml/`)
| Path | Responsibility |
| :--- | :--- |
| `ml/data/raw/` | Unmodified Category A UCI Cleveland CSV (`cleveland_heart_disease_raw.csv`) |
| `ml/data/processed/` | Leakage-free stratified splits (`train.parquet`, `test.parquet`, `complete_case_sensitivity.parquet`, `data_provenance_audit.json`) |
| `ml/pipelines/` | `prepare_data.py`, `train_model.py`, `evaluate_model.py` |
| `ml/registry/` | Serialized model artifact (`model.joblib`), `model_card.json`, `evaluation_report.json` |
| `ml/tests/` | Anti-leakage preprocessing & model reproducibility tests |

### 4. Infrastructure & Tooling (`infra/`, `scripts/`, `shared/`)
| Path | Responsibility |
| :--- | :--- |
| `infra/docker/` | `Dockerfile.backend`, `Dockerfile.frontend`, `nginx.frontend.conf` (`try_files` SPA fallback) |
| `infra/docker-compose.yml` | Staging 5-service stack (`proxy`, `frontend`, `backend`, `db`, `cache`) |
| `infra/nginx/nginx.conf` | TLS `:443` proxy, `:80 -> :443` redirect, rate limits, HSTS, CSP & security headers |
| `infra/scripts/` | `backup_encrypted.sh`, `restore_encrypted.sh`, `load_test.js` (K6) |
| `scripts/` | `generate_synthetic_patients.py`, `seed_synthetic_database.py`, `benchmark_performance.py`, `backup_aead.py` |
| `shared/` | Canonical `data-dictionary.json` & `country-profiles.json` |
