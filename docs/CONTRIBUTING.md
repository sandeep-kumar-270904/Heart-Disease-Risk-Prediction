# Contributing to HeartXAI 2.0

Thank you for contributing carefully and transparently to HeartXAI 2.0. Because this project handles healthcare research concepts and strict synthetic-data boundaries, contributors must follow both technical quality standards and project governance constraints.

---

## 1. Mandatory Project & Governance Rules

1. **No Real Patient Data (DEC-005):** Never introduce, paste, seed, or test with real patient health information (Category C). All test accounts must use RFC 2606 non-routable synthetic domains (`@example.com`, `@example.org`, `@example.net`).
2. **Task A Scope Only in MVP (DEC-003):** Do not add prospective 10-year cardiovascular risk calculations (`Task B`) or diagnostic/treatment claims to MVP endpoints, UI, or PDF exports.
3. **Preserve Approved Clinical Boundaries (`DEC-002`):** Do not re-enable disabled clinical risk strata (`30%`/`70%`), automated emergency triage alerts, arbitrary clinician free-text notes, or invented uncertainty intervals without documented physician advisory approval.
4. **No Secrets or Runtime Artifacts in Git:** Never commit `.env`, API keys, TLS certificates (`*.pem`, `*.key`), encrypted/unencrypted DB dumps (`*.gcm`, `*.sql.gz`), SQLite files (`*.db`), or `backups/`.
5. **Preserve ML Artifacts & Provenance:** Do not alter `ml/data/raw/cleveland_heart_disease_raw.csv` or retrain/modify `ml/registry/model.joblib` without explicit research authorization.

---

## 2. Branching & Conventional Commits

Work cleanly on small, single-scope branches or approved PRs targeting `main`. Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat(<scope>): ...` — new approved milestone functionality
- `fix(<scope>): ...` — defect or security remediation
- `docs(<scope>): ...` — documentation updates
- `test(<scope>): ...` — regression or integration tests
- `ci(<scope>): ...` — CI/CD workflow updates

Never force-push or rewrite shared `main` history.

---

## 3. Code Quality & Pre-Commit Workflow

Optional pre-commit hooks are configured in `.pre-commit-config.yaml`:
```bash
pip install pre-commit
pre-commit install
```

Before opening a pull request or committing changes, run all applicable local checks:

1. **Python Quality & Typing:**
   ```bash
   ruff format --check backend/ ml/ scripts/
   ruff check backend/ ml/ scripts/
   cd backend && mypy --strict app/core app/schemas app/ml app/services app/api/v1/routes app/main.py
   ```
2. **Backend, ML & SAST:**
   ```bash
   pytest -c backend/pyproject.toml backend/tests/ ml/tests/ -v
   bandit -r backend/app -ll -ii
   ```
3. **Frontend Quality, A11y & Build:**
   ```bash
   cd frontend
   npm run typecheck
   npm run lint
   npm test
   npm run build
   ```
4. **Repository Hygiene:** Verify `git status` and `git diff` contain only intended changes and zero sensitive data.
