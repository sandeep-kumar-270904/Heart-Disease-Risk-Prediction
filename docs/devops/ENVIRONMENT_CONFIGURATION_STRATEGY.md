# ENVIRONMENT CONFIGURATION AND ISOLATION STRATEGY

**Document Reference:** `docs/devops/ENVIRONMENT_CONFIGURATION_STRATEGY.md`  
**Phase:** 10 — DevOps, Infrastructure, Deployment Architecture & Release Engineering  
**Status:** Approved Technical Design  
**Author:** Environment Governance Specialist & DevOps Architect  
**Traceability:** NFR-SEC-01 through NFR-SEC-09, NFR-PRIV-01, ADR-009, ADR-011  

---

## 1. Executive Summary & Zero Real PHI Policy

In healthcare technology systems, environment contamination—where production patient data leaks into development workstations, test suites, or CI logs—represents an egregious privacy violation and a common source of major security breaches.

HeartXAI 2.0 defines four strictly isolated runtime environments:
1. **Local Development (`development`)**
2. **Automated Testing (`test` / CI)**
3. **Staging & Pre-Production (`staging`)**
4. **Production (`production`)**

> [!CAUTION]
> **MANDATORY DATA RESTRICTION:**  
> Real patient personal health information (PHI) or identifiable credentials must **NEVER** be ingested into development, testing, or staging environments. All non-production environments operate strictly with cryptographically generated synthetic test datasets clearly labeled with synthetic flags.

---

## 2. Multi-Environment Comparison Matrix

| Dimension | Local Development (`development`) | Automated Testing (`test` / CI) | Staging (`staging`) | Production (`production`) |
| :--- | :--- | :--- | :--- | :--- |
| **Purpose** | Feature engineering & rapid debugging | Automated regression, SAST, unit tests | Production parity validation & DAST | Real clinical decision support & user traffic |
| **Runtime Infrastructure** | Local Docker Compose or native Python | Ephemeral GitHub Actions container | Cloud VPS / Staging Docker network | Hardened Production VPC / Container host |
| **Database Isolation** | Local SQLite (`heartxai_dev.db`) or Docker Postgres | Ephemeral in-memory SQLite / test Postgres | Dedicated staging PostgreSQL instance | Dedicated production PostgreSQL with pooling |
| **Secrets Management** | `.env.development` (insecure defaults allowed) | Ephemeral CI environment variables | Cloud Secrets Manager (Staging vault) | Cloud KMS / HashiCorp Vault (Hardware HSM) |
| **External API Access**| Mocked responses / sandbox directories | 100% blocked (Hermetic test runner) | Mock / Public sandbox APIs with timeouts | Verified, TLS-authenticated public directories |
| **Logging Level** | `DEBUG` (verbose console traces) | `WARNING` / test output capture | `INFO` (structured JSON, PII scrubbed) | `INFO` / `WARN` (structured JSON, scrubbed) |
| **Data Restrictions** | 100% Synthetic fixtures only | 100% Synthetic fixtures only | Sanitized, large synthetic datasets | Real patient data (encrypted at rest/transit) |
| **Deployment Permission**| Individual developer | Automated CI runner on PR creation | Automated deploy on merge to `main` | Protected release gate requiring sign-off |
| **Debugging Access** | Interactive debugger (`pdb`, breakpoints) | Test failure stack traces | Remote logs only (no interactive shells) | Remote logs only (Zero interactive shells) |

---

## 3. Environment Specifications & Operating Rules

### 3.1 Local Development Environment (`development`)
- **Configuration:** Activated via `ENVIRONMENT=development` and `DEBUG=True`.
- **Database:** Defaults to SQLite (`sqlite:///./heartxai_dev.db`) or local Docker Compose PostgreSQL (`localhost:5432`).
- **Secrets:** Governed by local `.env.development` containing documented mock development secrets. Git pre-commit hooks verify that real keys are never introduced.
- **Mock External Services:** Country directory lookups (e.g. hospital listings) return pre-seeded static JSON fixtures located in `app/tests/fixtures/directories/`. No network calls to external APIs.
- **Frontend Live Reload:** Vite development server runs with Hot Module Replacement (HMR) on port 5173, proxying `/api` requests to backend port 8000.

---

### 3.2 Automated Testing Environment (`test` / CI)
- **Configuration:** Activated via `ENVIRONMENT=test` and `DEBUG=False`.
- **Database:** Uses a fresh, isolated PostgreSQL test container or in-memory SQLite database initialized and destroyed per test run. Tests run with transactional rollbacks (`db.rollback()`) to maintain test isolation.
- **Hermetic Network Execution:** Test execution is completely hermetic: outbound network calls are intercepted via `pytest-mock` or `respx`. Any unmocked external HTTP call triggers immediate test failure.
- **Deterministic Randomness:** All PRNG seeds across Python `random`, NumPy, and PyTorch/XGBoost are pinned to `seed = 42` to guarantee 100% bit-level test reproducibility.

---

### 3.3 Staging Environment (`staging`)
- **Configuration:** Activated via `ENVIRONMENT=staging` and `DEBUG=False`.
- **Parity Principle:** Identical container architecture, Nginx proxy rules, and PostgreSQL 16 engine as production. Staging acts as the definitive release verification environment.
- **Secrets:** Stored in cloud secrets manager under namespace `heartxai/staging/*`. Distinct cryptographic keys from production.
- **Baseline Security Scans:** Automated DAST scans (OWASP ZAP) and synthetic load tests execute against staging without risking production availability.

---

### 3.4 Production Environment (`production`)
- **Configuration:** Activated via `ENVIRONMENT=production` and `DEBUG=False`.
- **PostgreSQL Database:** Dedicated managed instance (AWS RDS / hardened host) with SSL verification (`sslmode=verify-full`), volume encryption (AES-256-XTS), and automated WAL archiving.
- **Secrets:** Injected via Cloud KMS or HashiCorp Vault. Production keys are inaccessible to developer workstations.
- **Zero Information Leakage:** Stack traces and internal filesystem paths are stripped from all API outputs; centralized error handlers return sanitized RFC 7807 Problem Details.

---

## 4. Synthetic Patient Data Generation Strategy

To ensure robust functional testing, load testing, and clinical validation without ever handling real patient data in non-production environments:

### 4.1 Synthetic Cohort Generator Architecture
- The utility `scripts/generate_synthetic_patients.py` generates realistic, clinically plausible patient records based on empirical multivariate distributions of the UCI Cleveland benchmark.
- Continuous biomarkers (blood pressure, cholesterol, heart rate) are sampled from bounded Gaussian distributions matching clinical cohorts.
- Categorical features (chest pain type, resting ECG, fluoroscopy vessels) are sampled using conditional multinomial probabilities.

### 4.2 Explicit Synthetic Tagging & Quarantine
Every generated record must contain immutable synthetic markers:
```json
{
  "is_synthetic": true,
  "mrn": "SYN-2026-98124",
  "patient_name": "Synthetic Patient Alpha",
  "synthetic_generator_version": "v1.2.0",
  "generation_timestamp": "2026-11-21T00:00:00Z"
}
```
- **Database Constraint:** A database check constraint or backend validator in staging prevents any record with `is_synthetic = False` from being seeded into non-production databases.
- **UI Watermark:** When running in development or staging, the frontend displays a persistent, prominent top banner:  
  `[TEST ENVIRONMENT — SYNTHETIC DATA ONLY — NOT FOR REAL CLINICAL USE]`.
