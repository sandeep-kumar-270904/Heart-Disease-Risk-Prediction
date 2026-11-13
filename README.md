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

---

## 2. Phase 1 Research & Architecture Documentation

All Phase 1 benchmarking, design research, and architectural specifications are documented in [`docs/`](./docs/):

| Document | Purpose |
| :--- | :--- |
| [`PRODUCT_ENGINEERING_BENCHMARK.md`](./docs/PRODUCT_ENGINEERING_BENCHMARK.md) | Engineering practices across Google, Apple, Meta, Amazon, Netflix, Microsoft, Stripe. |
| [`DESIGN_SYSTEM_RESEARCH.md`](./docs/DESIGN_SYSTEM_RESEARCH.md) | Comparative study of Apple HIG, Material 3, Fluent 2, Polaris, Carbon, and Atlassian. |
| [`HEARTXAI_QUALITY_FRAMEWORK.md`](./docs/HEARTXAI_QUALITY_FRAMEWORK.md) | 14-dimension measurable quality framework with explicit acceptance criteria. |
| [`USER_RESEARCH_AND_PERSONAS.md`](./docs/USER_RESEARCH_AND_PERSONAS.md) | Archetype personas, Jobs-to-be-Done problem statements, and journey maps. |
| [`PRODUCT_EXPERIENCE_STRATEGY.md`](./docs/PRODUCT_EXPERIENCE_STRATEGY.md) | Information architecture and UX strategies across 10 platform subsystems. |
| [`TECHNOLOGY_STACK_EVALUATION.md`](./docs/TECHNOLOGY_STACK_EVALUATION.md) | In-depth trade-off evaluation of React, TypeScript, FastAPI, PostgreSQL, XGBoost, and SHAP. |
| [`PHASE_1_RESEARCH_SUMMARY.md`](./docs/PHASE_1_RESEARCH_SUMMARY.md) | Consolidated findings and 17 primary source citations. |
| [`PHASE_1_OPEN_QUESTIONS.md`](./docs/PHASE_1_OPEN_QUESTIONS.md) | Architectural and clinical decisions catalog for stakeholder review. |

---

## 3. Technology Stack

- **Frontend:** React 18/19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic.
- **Database:** PostgreSQL (with SQLite development/testing fallback).
- **Machine Learning & XAI:** Scikit-learn, XGBoost, SHAP (TreeExplainer).
- **Testing & Verification:** pytest (unit, integration, property invariance), Playwright (E2E).
- **Infrastructure:** Docker, Docker Compose, Git.

---

## 4. Regulatory & Non-Diagnostic Disclaimer

> [!IMPORTANT]
> **HeartXAI 2.0 is an investigational clinical decision-support and cardiovascular health-literacy platform.** It does not provide medical diagnosis, prognosis, or prescriptive treatment plans. All algorithmic inferences and counterfactual projections must be reviewed by a licensed healthcare professional.
