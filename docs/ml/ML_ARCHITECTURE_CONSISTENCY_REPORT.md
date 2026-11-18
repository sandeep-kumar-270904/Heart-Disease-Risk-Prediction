# MACHINE LEARNING ARCHITECTURE CONSISTENCY AND CROSS-PHASE ALIGNMENT REPORT

**Document Reference:** `docs/ml/ML_ARCHITECTURE_CONSISTENCY_REPORT.md`  
**Phase:** 08 — Machine Learning Research & Model Development Plan  
**Status:** Approved Technical Audit  
**Author:** Principal Software Architect & ML Systems Alignment Lead  
**Traceability:** FR-PRED-01 through FR-PRED-06, NFR-*, ADR-009, ADR-011  

---

## 1. Executive Summary & Verification Objective

This audit verifies end-to-end consistency between the Phase 8 Machine Learning Research & Model Development Plan and the approved upstream engineering specifications from Phase 2 (Requirements), Phase 3 (System Architecture & Global Design), Phase 4/5 (Design System & UI/UX), Phase 6 (Frontend Engineering Architecture), and Phase 7 (Backend Engineering Architecture).

Every data structure, mathematical assumption, API contract, and clinical boundary defined in Phase 8 has been traced against approved architectural documents. Where tensions or minor discrepancies were discovered, formal resolutions are documented herein.

---

## 2. Cross-Phase Traceability Matrix

| Requirement / Architecture Component | Upstream Approved Document | Phase 8 ML Plan Specification | Compliance Status |
| :--- | :--- | :--- | :---: |
| **Prediction Target & Epistemology** | `docs/architecture/ADR_009_DISEASE_CLASSIFICATION_VS_RISK_SCORING.md` | `docs/ml/PREDICTION_PROBLEM_DEFINITION.md` | **ALIGNED (100%)** |
| **Global Country-Configurable Design** | `docs/architecture/ADR_011_GLOBAL_COUNTRY_CONFIGURABLE_ARCHITECTURE.md` | `docs/ml/ML_RESEARCH_AND_DEVELOPMENT_STRATEGY.md` | **ALIGNED (100%)** |
| **Core Prediction Functional Scope** | `docs/requirements/FUNCTIONAL_REQUIREMENTS.md` (FR-PRED-01 to 06) | `docs/ml/ML_MODEL_SELECTION_REPORT.md` & `SHAP_EXPLAINABILITY_DESIGN.md` | **ALIGNED (100%)** |
| **Database Storage & Schema** | `docs/backend/DATABASE_DESIGN_DOCUMENT.md` (`predictions` table) | `docs/ml/ML_BACKEND_INTEGRATION_CONTRACT.md` | **ALIGNED (100%)** |
| **API Endpoints & Contracts** | `docs/backend/API_SPECIFICATION.md` (`POST /api/v1/predictions`) | `docs/ml/ML_BACKEND_INTEGRATION_CONTRACT.md` | **ALIGNED (100%)** |
| **Async Execution & Concurrency** | `docs/backend/BACKEND_ENGINEERING_ARCHITECTURE.md` (Worker Threads) | `docs/ml/ML_BACKEND_INTEGRATION_CONTRACT.md` (`ThreadPoolExecutor`) | **ALIGNED (100%)** |
| **Frontend State & Visualizations** | `docs/frontend/FRONTEND_ENGINEERING_ARCHITECTURE.md` (Zustand + Recharts) | `docs/ml/SHAP_EXPLAINABILITY_DESIGN.md` & `COUNTERFACTUAL_EXPLANATION_DESIGN.md` | **ALIGNED (100%)** |
| **Design Tokens & Accessibility** | `docs/design/DESIGN_TOKENS.md` & `ACCESSIBILITY_SPECIFICATION.md` | `docs/ml/SHAP_EXPLAINABILITY_DESIGN.md` (WCAG AAA Color Contrasts) | **ALIGNED (100%)** |

---

## 3. Detailed Audit by Engineering Subsystem

### 3.1 Alignment with Phase 2 (Functional & Non-Functional Requirements)
- **FR-PRED-01 (13 Clinical Biomarkers):** Phase 8 specifies the exact 13 features matching the Cleveland schema, with explicit units and physiological bounds.
- **FR-PRED-02 (Calibrated Probability):** Phase 8 provides dedicated Platt Scaling and Isotonic calibration designs (`docs/ml/PROBABILITY_CALIBRATION_DESIGN.md`), satisfying the Brier score ($\le 0.14$) and ECE ($\le 0.06$) requirements.
- **FR-PRED-03 (Feature Attributions):** TreeSHAP integration satisfies the local accuracy and efficiency requirements with exact waterfall and summary visualization data contracts.
- **FR-PRED-04 (Counterfactuals):** Bounded optimization algorithm ensures actionable lifestyle factors can be perturbed while immutable factors (Age, Sex, Vessel count) are strictly locked.
- **NFR-PERF-01 (Inference Latency):** The ML engine defines a $P95$ budget of $150\text{ ms}$ (under the system-wide $200\text{ ms}$ API SLA).

### 3.2 Alignment with Phase 3 & ADR-011 (Country-Configurable Architecture)
- **The Challenge:** The primary training dataset (Cleveland Clinic) was collected in Ohio, USA. A naive implementation would hard-code US imperial units (mg/dL) and US population baselines.
- **Resolution in Phase 8:**
  - Feature inputs accept localized units via the backend country adapter (`CountryContext`), converting mmol/L blood sugar or cholesterol to standard canonical float tensors.
  - The model does not claim global validation. It explicitly documents that while the model engine is universal, local calibration intercepts (Platt parameter $B$) can be adjusted per country adapter when local validation datasets become available.

### 3.3 Alignment with Phase 4/5 (Design System) & Phase 6 (Frontend)
- **Feature Name Labeling:** Machine learning feature keys (`trestbps`, `thalach`, `oldpeak`) are mapped directly to human-readable clinical labels specified in the design system (`Resting Blood Pressure`, `Maximum Heart Rate Achieved`, `ST Depression`).
- **Color Token Compliance:** SHAP waterfall charts use design system tokens (`--color-risk-high` / `crimson-600` for risk-increasing attributions and `--color-risk-low` / `teal-600` for risk-decreasing attributions), maintaining WCAG AAA 7:1 contrast ratios on dark backgrounds.
- **Zustand State Hydration:** The output schema of `MLInferenceResult` directly hydrates the frontend `predictionStore` without intermediate client-side mapping.

### 3.4 Alignment with Phase 7 (Backend Architecture & Database Schema)
- **Database Column Alignment:** The PostgreSQL `predictions` table defines:
  - `model_version VARCHAR(50)` $\rightarrow$ matched by `cleveland_xgboost_v1.0.0`
  - `calibrated_probability NUMERIC(5,4)` $\rightarrow$ matched by `float32` calibrated output
  - `shap_values JSONB` $\rightarrow$ matched by list of `SHAPFeatureContribution` objects
  - `counterfactuals JSONB` $\rightarrow$ matched by list of `CounterfactualRecommendation` objects
- **FastAPI Thread Safety:** The ML pipeline runs synchronously inside an isolated `ThreadPoolExecutor`, preventing CPU-bound tree traversals from blocking FastAPI's `uvicorn` asyncio event loop.

---

## 4. Discrepancies Identified and Approved Resolutions

During the architectural audit, two minor discrepancies were identified between early requirements notes and the formal ML design:

| ID | Initial Note / Assumption | Phase 8 Rigorous ML Design | Rationale & Resolution |
| :---: | :--- | :--- | :--- |
| **DISC-01** | Early notes mentioned "Predicting 10-year heart attack risk" using Cleveland dataset. | Clarified as **Task A (Angiographic CAD Association)** vs **Task B (Prospective 10-Year ASCVD Risk)**. | The Cleveland dataset is cross-sectional without longitudinal follow-up. It is scientifically impossible to predict 10-year prospective risk from it. Aligned strictly with ADR-009. |
| **DISC-02** | Early draft suggested pooling Cleveland ($N=303$), Hungarian ($N=294$), VA Long Beach ($N=200$), and Swiss ($N=123$). | **Restricted primary training to Cleveland cohort ($N=303$)**. Other cohorts reserved for secondary cross-cohort evaluation. | Hungarian, VA, and Swiss cohorts have $>80\%-98\%$ missing values on fluoroscopy (`ca`) and thallium scintigraphy (`thal`). Imputing 98% missingness introduces severe synthetic artifacts. |

---

## 5. Architectural Consistency Sign-off

The Phase 8 Machine Learning Research and Model Development Plan is **fully consistent and compliant** with all upstream architectural specifications, database schemas, frontend data stores, and regulatory boundaries of HeartXAI 2.0.
