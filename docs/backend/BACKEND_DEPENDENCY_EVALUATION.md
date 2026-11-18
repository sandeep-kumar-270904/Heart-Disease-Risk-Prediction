# HeartXAI 2.0 — Backend Dependency Evaluation & Technology Selection

**Document ID:** `HX2-BE-003`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect & Python Dependency Specialist  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001 through ADR-011  

---

## 1. Selection Methodology & Governance

Dependencies selected for the **HeartXAI 2.0 Backend** have been evaluated against six strict criteria:
1. **Security & Cryptographic Modernity:** Zero legacy cryptographic algorithms (e.g., standard MD5/SHA1, unhardened SHA256 passwords). Banned deprecated packages (e.g., `python-jose` which has unpatched CVEs).
2. **Asynchronous Concurrency Support:** Must natively integrate with Python's `asyncio` event loop without blocking threads.
3. **Pydantic v2 & SQLAlchemy 2.0 Ecosystem Alignment:** Must support Pydantic v2 core rust engine and SQLAlchemy 2.0 2.0-style declarative mappings.
4. **Minimal Maintenance Overhead:** Must be actively maintained by established open-source foundations or reputable core maintainers with a clear vulnerability disclosure policy.
5. **Simplicity for an Individual Developer:** Avoids over-architecting with distributed message brokers (Kafka/RabbitMQ) when FastAPI's native asynchronous execution and lightweight background tasks satisfy all functional requirements.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   BACKEND DEPENDENCY TOPOLOGY                          │
├────────────────────────────────────────────────────────────────────────┤
│ • CORE: Python 3.11+, FastAPI 0.111+, Pydantic v2.7+, Uvicorn 0.30+    │
│ • DATABASE: SQLAlchemy 2.0.30+, Asyncpg 0.29+, Alembic 1.13+           │
│ • SECURITY: Argon2-cffi 23.1+, PyJWT 2.8+                              │
│ • ML/XAI: XGBoost 2.0+, SHAP 0.45+, Scikit-Learn 1.4+, NumPy 1.26+     │
│ • UTILS: Structlog 24.1+, WeasyPrint 61.2+, Httpx 0.27+                │
│ • TESTS: Pytest 8.2+, Pytest-asyncio 0.23+, Coverage 7.5+              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Framework & Web Server

### 2.1 Web Framework: `fastapi` (`^0.111.0`) & `uvicorn` (`^0.30.1`)
- **Purpose:** High-performance asynchronous HTTP routing, dependency injection, and automatic OpenAPI 3.1 specification generation.
- **Necessity:** Industry standard for Python modern APIs; native asynchronous routing; deep integration with Pydantic v2 serialization.
- **Alternatives Considered:**
  - *Django / DRF:* High boilerplate, heavier memory footprint, synchronous-first legacy ORM.
  - *Flask / Quart:* Lacks integrated dependency injection and native OpenAPI contract generation.
- **Security Considerations:** Built-in validation eliminates malformed payloads before hitting domain logic.
- **Maintenance:** Backed by Tiangolo and a massive global enterprise contributor base.

### 2.2 Data Validation & Serialization: `pydantic` (`^2.7.1`) & `pydantic-settings` (`^2.2.1`)
- **Purpose:** Request deserialization, strict type enforcement, response filtering, and environment variable parsing.
- **Necessity:** Implemented in Rust (`pydantic-core`), delivering $5\times\text{–}15\times$ faster validation than Pydantic v1. Ensures zero untyped data breaches domain boundaries.
- **Alternatives Considered:**
  - *Marshmallow:* Significantly slower; lacks native Python 3.10+ type hint syntax integration.
- **Security Considerations:** Strict parsing strips unrecognized fields by default (`extra = "forbid"`), preventing mass-assignment attacks.

---

## 3. Database & Migration Layer

### 3.1 Asynchronous ORM: `sqlalchemy` (`^2.0.30`)
- **Purpose:** Database abstraction, SQL expression generation, Unit of Work transaction management, and declarative model mapping.
- **Necessity:** SQLAlchemy 2.0 provides fully typed `Mapped[...]` attributes, clean 2.0-style `select()` syntax, and native `AsyncSession` execution.
- **Alternatives Considered:**
  - *Tortoise ORM / Peewee:* Smaller ecosystems, weaker enterprise migration and composite indexing capabilities.
- **Maintenance:** The standard database toolkit for Python; backed by Michael Bayer and Red Hat.

### 3.2 Database Driver: `asyncpg` (`^0.29.0`)
- **Purpose:** Asynchronous PostgreSQL database client and connection pooler.
- **Necessity:** The fastest PostgreSQL driver in the Python ecosystem (up to $3\times$ faster than `psycopg3` async and $5\times$ faster than synchronous `psycopg2`).
- **Compatibility:** Fully supported by SQLAlchemy's `postgresql+asyncpg://` dialect.

### 3.3 Schema Migrations: `alembic` (`^1.13.1`)
- **Purpose:** Version-controlled, reproducible database schema migrations.
- **Necessity:** Generates reversible, linear DDL scripts (`upgrade()` and `downgrade()`) tied to Git commits, ensuring zero schema drift between development, staging, and production.

---

## 4. Cryptography, Authentication & Security

### 4.1 Password Hashing: `argon2-cffi` (`^23.1.0`)
- **Purpose:** Irreversible cryptographic hashing of user passwords.
- **Necessity:** **Argon2id** is the winner of the Password Hashing Competition (PHC) and the official recommendation of OWASP and NIST. It provides mathematically proven resistance against both GPU brute-force attacks and ASIC/FPGA side-channel attacks.
- **Alternatives Considered:**
  - *bcrypt:* Historically standard, but vulnerable to GPU parallelized cracking and enforces an arbitrary 72-byte password truncation limit.
  - *PBKDF2:* Significantly less memory-hard than Argon2id.
- **Configuration:** Default parameters: `time_cost=3`, `memory_cost=65536` ($64\text{ MB}$ RAM), `parallelism=4`.

### 4.2 Cryptographic Tokens: `pyjwt` (`^2.8.0`)
- **Purpose:** Encoding, signing, decoding, and cryptographically verifying JSON Web Tokens (JWT) for user sessions.
- **Necessity:** Lightweight, secure, actively maintained.
- **Alternatives Considered:**
  - *python-jose:* **REJECTED.** Contains known unpatched security vulnerabilities and has had no active maintenance since 2021.
- **Security Considerations:** Enforces explicit algorithm pinning (`algorithms=["HS256"]` or `RS256`), preventing algorithm confusion attacks (`alg: "none"`).

---

## 5. Machine Learning & Explainability Subsystem

### 5.1 Gradient Boosting Engine: `xgboost` (`^2.0.3`)
- **Purpose:** Execution of the validated Cleveland-cohort tree-ensemble classifier for CAD likelihood prediction.
- **Necessity:** High inference velocity ($< 5\text{ms}$ per evaluation); serializable into lightweight JSON model formats.

### 5.2 Tree Explainability Engine: `shap` (`^0.45.1`)
- **Purpose:** Exact polynomial-time computation of TreeSHAP local feature attribution values ($\phi_i$).
- **Necessity:** `shap.TreeExplainer` delivers mathematical consistency and local accuracy, guaranteeing that $\sum \phi_i = f(x) - E[f(x)]$.

### 5.3 Scientific Computing: `numpy` (`^1.26.4`) & `scikit-learn` (`^1.4.2`)
- **Purpose:** Input array manipulation, feature scaling, and median imputation of missing optional parameters (`ca`, `thal`).

---

## 6. Utilities, Observability & Testing

### 6.1 Structured Logging: `structlog` (`^24.1.0`)
- **Purpose:** Structured JSON logging with automated correlation ID binding.
- **Necessity:** Emits machine-readable JSON logs in production for Datadog / CloudWatch / ELK, with automated scrubbing of sensitive keys (`password`, `access_token`, `national_id`).

### 6.2 HTTP Client for Integrations: `httpx` (`^0.27.0`)
- **Purpose:** Asynchronous HTTP client for communicating with external country healthcare registries (e.g., NMC India API, CMS Open Data).
- **Necessity:** Native `async/await` client supporting connection pooling, timeout budgets, and retry logic.

### 6.3 PDF Document Generation: `weasyprint` (`^61.2`)
- **Purpose:** Server-side compilation of HTML/CSS clinical templates into pixel-perfect PDF consultation aids.
- **Necessity:** Supports full CSS Paged Media specifications, web fonts (`Inter`), and vector SVG graphics. Saves $> 150\text{ KB}$ of browser bundle weight by rendering server-side.

### 6.4 Testing Suite: `pytest` (`^8.2.0`), `pytest-asyncio` (`^0.23.6`), `coverage` (`^7.5.1`)
- **Purpose:** Comprehensive automated testing across unit, integration, and security domains.

---

## 7. Recommended Dependency Manifest (`pyproject.toml`)

```toml
[tool.poetry]
name = "heartxai-backend"
version = "2.0.0"
description = "Explainable AI-Based Cardiovascular Platform API"
authors = ["HeartXAI Engineering Team <engineering@heartxai.org>"]
readme = "README.md"
python = "^3.11"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.111.0"
uvicorn = {extras = ["standard"], version = "^0.30.1"}
pydantic = {extras = ["email"], version = "^2.7.1"}
pydantic-settings = "^2.2.1"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.30"}
asyncpg = "^0.29.0"
alembic = "^1.13.1"
argon2-cffi = "^23.1.0"
pyjwt = "^2.8.0"
xgboost = "^2.0.3"
shap = "^0.45.1"
scikit-learn = "^1.4.2"
numpy = "^1.26.4"
structlog = "^24.1.0"
httpx = "^0.27.0"
weasyprint = "^61.2"
python-multipart = "^0.0.9"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2.0"
pytest-asyncio = "^0.23.6"
pytest-cov = "^5.0.0"
httpx = "^0.27.0"
faker = "^25.1.0"
ruff = "^0.4.4"
mypy = "^1.10.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

> **Evaluation Conclusion:** The backend dependency footprint is tightly curated to **17 core production packages**. Zero overlapping frameworks or unmaintained libraries are included, guaranteeing high stability and rapid installation.
