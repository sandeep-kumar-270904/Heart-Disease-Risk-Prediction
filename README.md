# HeartXAI 2.0 — Production-Grade Explainable AI Cardiovascular Platform

> **HeartXAI 2.0** is an enterprise-grade, clinical decision-support and cardiovascular health-awareness platform combining calibrated machine learning, exact TreeSHAP feature attributions, constrained counterfactual "what-if" simulations, and longitudinal risk tracking.

---

## 1. Project Mission & Quality Philosophy

HeartXAI 2.0 is built to professional engineering standards demonstrated by leading technology companies (Google, Apple, Meta, Amazon, Netflix, Microsoft, Stripe). It is explicitly designed to eliminate "black-box" clinical anxiety, prevent the conflation of diagnostic targets, and provide mathematically grounded, actionable lifestyle pathways.

### Key Pillars
- **Dual Clinical Targets:** Explicit separation of binary coronary artery disease (CAD) presence ($\ge 50\%$ stenosis) from prospective 10-year ASCVD risk (ACC/AHA pooled cohort equations).
- **Exact Explainability (TreeSHAP):** Mathematically consistent local feature attributions ($\sum \phi_i = f(x) - \mathbb{E}[f(x)]$).
- **Constrained Counterfactuals:** Plausible optimization locking immutable traits (Age, Sex, Anatomical fluoroscopy) while exploring modifiable lifestyle biomarkers (Blood Pressure, Cholesterol, Blood Sugar).
- **Longitudinal Tracking:** Persistent PostgreSQL storage with trend analytics and checkup delta comparisons.
- **Role-Based Access Control:** Dedicated workflows for Patients, Clinicians, and Compliance Auditors.
- **Strict Data Governance (DEC-005):** Category C real patient health information is **strictly prohibited in MVP**. Operates strictly with `SYNTHETIC_DATA_ONLY=true`.

---

## 2. Implementation Roadmap & Project Status

The engineering roadmap follows 20 modular, test-driven milestones:

| Milestone | Scope | Status |
| :---: | :--- | :---: |
| **M01** | **Repository & Development Environment Foundation** | **Completed** |
| M02 | Core Scaffolding, Canonical Types & Synthetic Data Generator | Next |
| M03 | Design System & UI Component Library (WCAG 2.2 AA Target) | Planned |
| M04 | Database Engine & Schema Migrations (PostgreSQL 16, Alembic) | Planned |
| M05 | Backend Core Services & API Framework (FastAPI, RFC 7807) | Planned |
| M06–M20 | Full-Stack Features, ML Serving, XAI, Security, and Staging UAT | Planned |

---

## 3. Quickstart & Local Development

### Prerequisites
- **Docker & Docker Compose:** Docker Engine 26+ / Compose v2.20+
- **Python:** 3.11+
- **Node.js:** 20+ (LTS)

### Step 1: Environment Configuration
Copy the documented environment template:
```bash
cp .env.example .env
```
Ensure `SYNTHETIC_DATA_ONLY=true` is set.

### Step 2: Start Containerized Infrastructure
Start local PostgreSQL 16 and Redis 7.2 containers via Docker Compose:
```bash
docker compose up -d
```
Verify container health:
```bash
docker compose ps
```

### Step 3: Backend Setup & Native Execution
Create and activate a Python virtual environment:
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

Run the backend API development server:
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Readiness Probe: `http://localhost:8000/health/ready`

### Step 4: Testing & Code Hygiene
Run unit and integration test suite:
```bash
cd backend
pytest
```
Run Ruff linting and formatting verification:
```bash
cd backend
ruff check .
ruff format --check .
```

---

## 4. Architecture & Governance Documentation

All 12 foundational engineering and governance audit phases are fully documented in [`docs/`](./docs/):

- **Master Pre-Implementation Blueprints:** [`docs/phase-12-final/`](./docs/phase-12-final/)
- **Approved Project Decision Register:** [`PROJECT_DECISION_REGISTER.md`](./docs/phase-12-final/PROJECT_DECISION_REGISTER.md)
- **Master Implementation Roadmap:** [`MASTER_IMPLEMENTATION_ROADMAP.md`](./docs/phase-12-final/MASTER_IMPLEMENTATION_ROADMAP.md)
- **Comprehensive Documentation Inventory:** [`DOCUMENTATION_INVENTORY.md`](./docs/phase-12-final/DOCUMENTATION_INVENTORY.md)
- **Antigravity Execution Rules:** [`ANTIGRAVITY_EXECUTION_RULES.md`](./docs/phase-12-final/ANTIGRAVITY_EXECUTION_RULES.md)

---

## 5. Technology Stack

- **Frontend:** React 18/19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic.
- **Database & Cache:** PostgreSQL 16 (relational store), Redis 7.2 (token blacklisting & rate limiting).
- **Machine Learning & XAI:** Scikit-learn, XGBoost, TreeSHAP (TreeExplainer).
- **Code Hygiene & CI/CD:** Ruff, pre-commit, GitHub Actions, Docker Compose.

---

## 6. Regulatory & Non-Diagnostic Disclaimer

> [!IMPORTANT]
> **HeartXAI 2.0 is an investigational clinical decision-support and cardiovascular health-literacy platform.** It does not provide medical diagnosis, prognosis, or prescriptive treatment plans. All algorithmic inferences and counterfactual projections must be reviewed by a licensed healthcare professional.
