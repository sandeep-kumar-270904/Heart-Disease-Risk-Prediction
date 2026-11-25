# HeartXAI 2.0 — Environment Configuration & Secret Hygiene

This document defines all environment variables read by the HeartXAI 2.0 backend, Docker Compose stacks, and backup utilities.

---

## 1. Environment Variable Reference

| Variable Name | Purpose | Required | Safe Example / Default | Environment |
| :--- | :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | Controls dev vs fail-closed staging/production validation & cookie `Secure` flag | No (`development`) | `development`, `test`, `staging`, `production` | All |
| `DEBUG` | Toggles verbose debug logging (`DEBUG=true` rejected in staging/production) | No (`true`) | `false` | All |
| `SYNTHETIC_DATA_ONLY` | Governance flag enforcing synthetic-only MVP boundary | Yes (`true`) | `true` | All |
| `PROJECT_NAME` | FastAPI & OpenAPI service display name | No (`"HeartXAI 2.0"`) | `"HeartXAI 2.0"` | All |
| `VERSION` | API semantic version | No (`"2.0.0"`) | `"2.0.0"` | All |
| `API_V1_STR` | Canonical versioned API mount prefix | No (`"/api/v1"`) | `"/api/v1"` | All |
| `SECRET_KEY` | HS256 JWT signing secret (**must be >=32 chars & non-placeholder in staging/prod**) | Yes (`staging`/`prod`) | `<generate 256-bit hex outside repo>` | All |
| `ALGORITHM` | JWT signature algorithm | No (`HS256`) | `HS256` | All |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Short-lived access JWT lifetime (`ADR-004`) | No (`15`) | `15` | All |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token family TTL in Redis & `HttpOnly` cookie | No (`7`) | `7` | All |
| `DATABASE_URL` | SQLAlchemy DB connection URI | Yes (`staging`/`prod`) | `postgresql://heartxai_user:heartxai_password@localhost:5432/heartxai_db` | All |
| `TEST_DATABASE_URL` | Overrides test DB in Pytest (falls back to in-memory SQLite if unset) | No | `postgresql://heartxai_user:heartxai_password@localhost:15432/heartxai_db` | Testing / CI |
| `REDIS_URL` | Redis connection URI for `RedisTokenStore` revocation & family rotation | Yes (live auth) | `redis://localhost:6379/0` | All |
| `CORS_ORIGINS` | JSON array of allowed browser origins for CORS | No | `["http://localhost:5173"]` | All |
| `MODEL_DIR` | Directory containing serialized Task A model artifacts | No (`app/ml/artifacts`) | `app/ml/artifacts` | All |
| `ACTIVE_MODEL_VERSION` | Target Task A model artifact version label | No (`v2.0.0`) | `v2.0.0` | All |
| `POSTGRES_USER` | PostgreSQL container/backup user | Compose / Backup | `heartxai_user` | Compose |
| `POSTGRES_PASSWORD` | PostgreSQL container password | Compose | `<local-dev-or-secret-manager>` | Compose |
| `POSTGRES_DB` | PostgreSQL container database name | Compose / Backup | `heartxai_db` | Compose |
| `POSTGRES_PORT` | Host port mapping in root `docker-compose.yml` | No (`5432`) | `5432` | Local Dev |
| `REDIS_PORT` | Host port mapping in root `docker-compose.yml` | No (`6379`) | `6379` | Local Dev |
| `TLS_CERT_DIR` | Directory mounted read-only to `/etc/nginx/certs` in `infra/docker-compose.yml` | Infra Compose | `<path-to-certs-outside-repo>` | Staging / Prod |
| `BACKUP_ENCRYPTION_KEY` | Passphrase (>=16 chars) for `scripts/backup_aead.py` AES-256-GCM encryption | Backup / Restore | `<passphrase-stored-separate-from-archive>` | Ops / Backup |

---

## 2. Fail-Closed Security Validation (`backend/app/core/config.py`)

When `ENVIRONMENT` is anything other than `development`, `dev`, `test`, or `local`, `Settings.validate_staging_production_security()` raises a startup `ValueError` (failing closed) if:
- `SECRET_KEY` is shorter than `32` characters.
- `SECRET_KEY` matches known development defaults or placeholders (`hxai-insecure`, `hxai-local-dev-only`, `change-in-production`, `change-this`, `replace_with`, `dev-key`, `secret`).
- `DEBUG` is `True`.

Additionally, `infra/docker-compose.yml` enforces `${SECRET_KEY:?SECRET_KEY must be set to a strong >=32 char secret}` so Compose fails closed if invoked without `SECRET_KEY`.

---

## 3. Secret & Repository Hygiene Rules

1. **Never commit `.env`, `.env.*` (except `.env.example`), `*.pem`, `*.key`, `*.crt`, `*.pfx`, `*.gcm`, `backups/`, or `*.sqlite`/`*.db` files.** All patterns are ignored in `.gitignore`.
2. **Never copy `BACKUP_ENCRYPTION_KEY` onto the same storage volume as encrypted `.sql.gz.gcm` archives.**
3. **Structured JSON logging (`backend/app/core/logging.py`)** automatically scrubs inline `password=...`, `secret=...`, `token=...`, `authorization=...`, `cookie=...`, and `email=...` patterns before stdout emission.
