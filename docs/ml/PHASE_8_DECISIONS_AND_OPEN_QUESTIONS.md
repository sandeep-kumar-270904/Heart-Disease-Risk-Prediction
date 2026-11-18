# PHASE 8 ML RESEARCH DECISIONS AND OPEN QUESTIONS

**Document Reference:** `docs/ml/PHASE_8_DECISIONS_AND_OPEN_QUESTIONS.md`  
**Phase:** 08 — Machine Learning Research & Model Development Plan  
**Status:** Approved Technical Ledger  
**Author:** Principal Machine Learning Research Scientist  
**Traceability:** FR-PRED-01 through FR-PRED-06, ADR-009, ADR-011  

---

## 1. Executive Summary

This ledger records all methodological, statistical, algorithmic, and architectural decisions finalized during the Phase 8 Machine Learning Research and Model Development planning process. It also catalogs the open questions requiring clinical stakeholder and user review prior to Phase 9 model implementation and training execution.

---

## 2. Approved Methodological & Algorithmic Decisions

| Decision ID | Area | Decision Summary | Rationale & Scientific Justification |
| :---: | :--- | :--- | :--- |
| **ML-DEC-01** | **Target Formulation** | Binary classification of angiographic CAD ($\text{num} \ge 1 \implies \ge 50\%$ vessel stenosis) vs absence ($\text{num} = 0$). | Aligns with standard clinical definition of hemodynamically significant CAD; multiclass ($0, 1, 2, 3, 4$) has insufficient sample sizes in severe classes ($N=13$ for class 4). |
| **ML-DEC-02** | **Primary Dataset** | UCI Cleveland Clinic cohort ($N=303$) selected as primary training data; Hungarian, Swiss, and VA Long Beach cohorts excluded from primary training. | Non-Cleveland cohorts lack $>80\%-98\%$ of values for key predictive imaging features (`ca`, `thal`). Synthetic imputation would distort biological feature relationships. |
| **ML-DEC-03** | **Validation Architecture** | 5-fold Nested Stratified Cross-Validation with repeated outer loops (5 repeats). | Small sample size ($N=303$) makes single train/test splits unreliable. Nested CV provides an unbiased, leak-free estimate of generalizability. |
| **ML-DEC-04** | **Model Benchmark Gate** | L2-regularized Logistic Regression is the mandatory benchmark. Complex tree models (XGBoost) must beat it by $\Delta \text{AUC} \ge +0.02$. | Simpler linear models must be favored unless non-linear interactions provide statistically significant, validated clinical performance gains. |
| **ML-DEC-05** | **Calibration Method** | Platt Scaling (Sigmoid) preferred over Isotonic Regression on small training folds ($N \approx 242$). | Isotonic regression is non-parametric and overfits step functions on small sample sizes ($N < 500$), whereas Platt scaling is monotonic, smooth, and robust. |
| **ML-DEC-06** | **TreeSHAP Background** | 25 medoids computed via K-Medoids on the training set. | Using all 303 background samples increases runtime latency by $12\times$; 25 medoids preserve population feature density while keeping $P95$ latency under $60\text{ ms}$. |
| **ML-DEC-07** | **Counterfactual Bounds** | Hard mathematical clamps: Age, Sex, Fluoroscopy vessels strictly immutable ($\Delta x_j = 0$). Actionable features constrained by physiological safety floors (BP $\ge 90\text{ mmHg}$). | Prevents generating absurd or fatal recommendations (e.g. telling a patient to become younger or lower their blood pressure into circulatory shock). |
| **ML-DEC-08** | **Serialization Security** | XGBoost serialized strictly to JSON; NumPy arrays to `.npy`; joblib preprocessors verified with HMAC-SHA256 signatures before loading. | Eliminates arbitrary Python `pickle` deserialization Remote Code Execution (RCE) vulnerabilities. |
| **ML-DEC-09** | **FastAPI Concurrency** | Synchronous ML inference executed via `asyncio.to_thread` with a dedicated bounded `ThreadPoolExecutor` ($N=4$ workers). | Prevents CPU-bound numerical loops in NumPy and XGBoost from starving the FastAPI asynchronous HTTP event loop. |
| **ML-DEC-10** | **Decoupled Cohort Scope** | Cleveland cohort treated as a specific clinical model adapter; UI and application directory modules remain global and configurable per country (ADR-011). | Prevents conflating historical Ohio hospital data with global population claims. Enables country-specific recalibration when local datasets are added. |

---

## 3. Open Questions for User & Clinical Stakeholder Approval

The following items are documented as open decisions requiring user or institutional review before launching implementation in Phase 9:

### Open Question 1: Implementation of Prospective Risk Engine (Task B)
- **Context:** The Cleveland ML model performs cross-sectional angiographic CAD classification (Task A). In Phase 2 requirements, a prospective 10-year cardiovascular risk calculator (Task B, such as Framingham Risk Score or ACC/AHA ASCVD Pooled Cohort Equations) was also discussed.
- **Decision Required:** Should Phase 9 implement Task B as an analytical, rule-based algorithmic module alongside the Cleveland ML model, or should HeartXAI 2.0 focus exclusively on the Cleveland CAD ML classifier first?
- **Recommendation:** Implement Task B as an analytical, deterministic clinical calculator using validated ACC/AHA equations in `app/services/ascvd_calculator.py`, clearly visually segregated from the Cleveland ML model in the UI.

### Open Question 2: Subgroup Disparity Tolerance & Decision Threshold
- **Context:** Females in the Cleveland cohort have a lower CAD prevalence ($25.8\%$) and a smaller sample size ($N=97$).
- **Decision Required:** Should the production model use a single global decision threshold ($p = 0.50$) across all users, or should a sex-stratified threshold be evaluated to achieve exact Equal Opportunity (equal true positive rates) between sexes?
- **Recommendation:** Use a single global probability output ($P(y=1|x)$) displayed to clinicians, but flag predictions for female patients with a note: *"Assessed against cohort with lower female representation; clinical correlation advised."* Do not manipulate binary thresholds artificially without clinical trial validation.

### Open Question 3: Missing Value Behavior in Production Inference
- **Context:** 11 of the 13 clinical features are routinely gathered in standard clinical assessments, but `ca` (fluoroscopic vessel count) and `thal` (nuclear stress scintigraphy) require specialized non-invasive/invasive imaging.
- **Decision Required:** If an outpatient user does not have `ca` or `thal` test results:
  - Option A: Refuse prediction and require complete clinical workup.
  - Option B: Impute missing imaging features using the median training value and flag the prediction as "Incomplete Diagnostic Data (Estimated)".
- **Recommendation:** Option B. Allow inference with median imputation for `ca` and `thal` only, but explicitly display a prominent UI badge indicating that imaging biomarkers were estimated and display a wider confidence interval.

---

## 4. Research Dependencies & Risk Management

| Risk | Probability | Impact | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Overfitting on Small $N=303$ Sample** | Medium | High | Enforce shallow tree depths ($\le 3$), strict L2 regularization, and mandatory comparison against regularized Logistic Regression. |
| **SHAP Latency Spikes under Load** | Low | Medium | Pre-compute and cache 25 background medoids; set strict $200\text{ ms}$ timeout with graceful fallback. |
| **Algorithmic Misinterpretation by Patients** | Medium | Critical | Prominent emergency disclaimers; frame counterfactuals as sensitivity analysis; mandatory clinical consultation warnings. |
| **Environment Discrepancies** | Low | High | Pin exact wheel versions via `requirements-ml.lock` and enforce bit-level seed determinism across runtime containers. |

---

## 5. Next Steps & Phase Sign-Off Gate

All research, mathematical models, validation pipelines, backend contracts, quality strategies, and ethical boundaries have been fully specified across 19 technical documents in `docs/ml/`. 

**STOP GATE ACTIVE:** The ML subsystem design is complete. In accordance with Prompt 08 instructions, no code implementation, package installation, or model training will occur until explicit review and approval are granted by the user.
