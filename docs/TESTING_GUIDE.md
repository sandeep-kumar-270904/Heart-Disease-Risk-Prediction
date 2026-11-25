# HeartXAI 2.0 — Testing & Verification Guide

This guide documents all automated verification suites, exact commands, and the critical distinction between local unit/mock tests and live infrastructure integration tests.

---

## 1. Frontend Checks (`cd frontend`)

| Check | Command | Scope & Notes |
| :--- | :--- | :--- |
| **Type Check** | `npm run typecheck` | Runs `tsc --noEmit` strictly across `src/` |
| **Linting & A11y AST** | `npm run lint` | Runs `eslint` with `--max-warnings 0` including `eslint-plugin-jsx-a11y` |
| **Unit & Axe A11y Tests** | `npm test` | Runs `vitest run` (`ui-primitives`, `shell-and-auth`, `intake-wizard`, `assessment-results`, 7-route `vitest-axe` audit in `jsdom`) |
| **Production Bundle** | `npm run build` | Verifies `tsc --noEmit && vite build` asset bundling into `dist/` |
| **Runtime Dep Audit** | `npm audit --omit=dev` | Checks production runtime bundle dependencies (`0` advisories) |
| **Full Dep Audit** | `npm audit` | Checks devDependencies too (currently reports 6 dev-only advisories in `vitest`/`vite` chain) |

> [!NOTE]
> `vitest-axe` inside `jsdom` checks DOM accessibility rules against mocked `fetch` responses; it does **not** prove full WCAG 2.2 AA conformance across real Chromium rendering, keyboard navigation, zoom reflow, or screen readers.

---

## 2. Backend & ML Checks

Run Python checks with the `backend/.venv` virtual environment active (`requirements-dev.txt` installed):

| Check | Command | Scope & Notes |
| :--- | :--- | :--- |
| **Full Backend + ML Suite** | `pytest -c backend/pyproject.toml backend/tests/ ml/tests/ -v` | Runs 51 tests using SQLite (`PRAGMA foreign_keys=ON`) + `InMemoryTokenStore` by default unless `TEST_DATABASE_URL` is set |
| **Ruff Format & Lint** | `ruff format --check backend/ ml/ scripts/` && `ruff check backend/ ml/ scripts/` | Enforces formatting, imports, bugbear, pyupgrade & simplify rules |
| **Strict Type Checking** | `cd backend && mypy --strict app/core app/schemas app/ml app/services app/api/v1/routes app/main.py` | Strict type validation across 29 backend modules |
| **Bandit SAST** | `bandit -r backend/app -ll -ii` | Static Python security scan (reports Medium/High findings) |
| **ML Reproducibility Audit** | `python -m ml.pipelines.evaluate_model` | Recomputes holdout metrics (`AUROC`, `Brier`, 10-bin/5-bin/quantile `ECE`, artifact SHA-256) against `test.parquet` |

---

## 3. Live PostgreSQL 16 & Redis 7.2 Integration vs Local Mocks

**Never cite SQLite + `InMemoryTokenStore` runs as live PostgreSQL or Redis verification.** When Docker containers are running:

```bash
# 1. Start PostgreSQL 16 and Redis 7.2
docker compose up -d --wait

# 2. Run Alembic migration cycle & DB tests directly against PostgreSQL 16
export TEST_DATABASE_URL="postgresql://heartxai_user:heartxai_password@localhost:5432/heartxai_db"
pytest -c backend/pyproject.toml backend/tests/test_migrations_and_seeding.py backend/tests/test_database_models.py -v
```

*(Note: Live 5-container `infra/docker-compose.yml` builds, frontend healthcheck pass after `18419e7`, Playwright E2E `tests/e2e/synthetic_patient_journey.spec.ts`, OWASP ZAP scans, and live `backup_encrypted.sh`/`restore_encrypted.sh` drills remain contingent on a running Docker Desktop Linux engine.)*

---

## 4. Infrastructure Config & Cipher Checks

```bash
# Validate local Compose YAML
docker compose config -q

# Validate staging infra Compose YAML (requires non-empty SECRET_KEY >= 32 chars)
SECRET_KEY="ci-validation-non-placeholder-key-at-least-32-chars" docker compose -f infra/docker-compose.yml config -q

# AES-256-GCM AEAD encryption/tamper/wrong-key regression test
pytest -c backend/pyproject.toml backend/tests/test_remediation_round_01.py -k backup -v
```
