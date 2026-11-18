# HeartXAI 2.0 — Machine Learning Research & Development Strategy

**Document ID:** `HX2-ML-001`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Research Specification  
**Author:** Principal ML Research Scientist, Applied Data Scientist & ML Validation Specialist  
**Traceability:** FR-020–FR-039, NFR-001–NFR-028, ADR-001, ADR-003, ADR-011, HXAI-REQ-006  

---

## 1. Executive Scientific Stance & Epistemological Mandate

In healthcare technology and clinical machine learning, **scientific restraint, mathematical rigor, and epistemological honesty** are mandatory. Fabricating clinical performance, confusing cross-sectional disease classification with prospective cardiovascular risk calculation, or presenting algorithmic feature sensitivity as biological causation constitutes a dangerous breach of clinical ethics.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE FIVE CARDINAL SCIENTIFIC RULES                   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Classification ≠ Prospective Risk: Binarized angiographic CAD       │
│    stenosis is not a prospective 10-year cardiovascular event forecast.│
│ 2. Strict Leakage-Free Evaluation: Preprocessing, imputation, and      │
│    scaling must strictly occur inside cross-validation folds.          │
│ 3. Calibrated Probabilities Only: Raw decision margins or uncalibrated │
│    sigmoid outputs must never be presented as empirical probabilities. │
│ 4. SHAP is Mathematical, Not Causal: Shapley values explain model      │
│    weighting, not biological etiology or physiological causation.      │
│ 5. Counterfactuals are Hypothetical Simulations: Projecting model      │
│    behavior is not clinical prescribing or medical advice.             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Research Scope & Subsystem Objectives

The HeartXAI 2.0 Machine Learning Subsystem is designed as an **Explainable AI (XAI) Educational and Awareness Component**. It operates under strict non-diagnostic regulatory boundaries:

1. **Prediction Target:** Estimate the statistical likelihood that a patient's submitted clinical profile matches historical observational cohort patterns of angiographically confirmed coronary artery disease ($\ge 50\%$ diameter stenosis).
2. **Explainability by Default:** No likelihood score is presented in isolation. Every inference is accompanied by local feature attributions via **TreeSHAP** ($\phi_i$) and constrained **Counterfactual "What-If" Simulations**.
3. **Reproducibility & Traceability:** Every inference is cryptographically linked to the specific model version, artifact SHA256 checksum, training cohort metadata, and preprocessing pipeline.
4. **Global Decoupling (ADR-011):** The model's training provenance (Cleveland Clinic Foundation, USA, 1980s referral cohort) is explicitly surfaced to the user. Model outputs are completely separated from country-specific clinical presentation layers and directory registries.

---

## 3. High-Level ML Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ML SUBSYSTEM ARCHITECTURAL TOPOLOGY                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Ingestion & Unit Normalization (mg/dL <-> mmol/L, mmHg)             │
│    - Validates physiological bounds; converts to canonical metric      │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Leakage-Proof Preprocessing & Imputation Pipeline                   │
│    - Standardizes feature order; imputes missing ca/thal with median   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Model Inference Engine (FastAPI -> asyncio.to_thread)               │
│    - XGBoost / Random Forest candidate; Platt Scaling / Isotonic Calib │
│    - Computes continuous probability + 95% Wilson confidence intervals │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Explainability & Simulation Subsystems                              │
│    - TreeSHAP polynomial-time feature attribution calculator           │
│    - Constrained counterfactual optimizer with biological clamps       │
├────────────────────────────────────────────────────────────────────────┤
│ 5. Audit & Governance Logging                                          │
│    - Binds inference to model hash; checks drift via PSI/KS monitoring │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Phased Model Development & Research Roadmap

The development of the ML subsystem progresses through four disciplined phases:
- **Phase A — Dataset Verification & Preprocessing:** Primary source provenance verification, audit of duplicate/invalid records in UCI Cleveland, and leak-proof pipeline construction.
- **Phase B — Baseline & Candidate Benchmarking:** Training of baseline Logistic Regression against Random Forest and XGBoost using Stratified 5-Fold Nested Cross-Validation.
- **Phase C — Probability Calibration & XAI Integration:** Evaluating Platt Scaling and Isotonic Regression via Brier scores and ECE; integrating `shap.TreeExplainer` with verified local accuracy.
- **Phase D — Constrained Counterfactuals & Quality Sign-Off:** Developing biological feasibility clamps for modifiable vitals and verifying that no immutable factors (Age, Sex) are modified.
