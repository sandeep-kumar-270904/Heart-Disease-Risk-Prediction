# HeartXAI 2.0 — Probability Calibration Design & Output Specification

**Document ID:** `HX2-ML-009`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal ML Research Scientist & Statistical Calibration Lead  
**Traceability:** FR-020–FR-029, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-REQ-006  

---

## 1. The Necessity of Probability Calibration in Healthcare

In machine learning classification, the raw outputs of tree ensembles (XGBoost, Random Forest) are **uncalibrated scores or distorted margin approximations**. 
- **The Problem with Raw Tree Outputs:** Random forest averages over trees tend to push predicted probabilities away from $0.0$ and $1.0$ toward the cohort base rate, underestimating extreme risks. Conversely, boosted tree ensembles (XGBoost) often output overconfident, polarized margins pushed toward $0$ and $1$.
- **Clinical Consequence:** Presenting an uncalibrated score of $0.78$ to a patient implies that "out of 100 people with this score, 78 have significant coronary artery disease." If the empirical reality is that only 52 have CAD, the patient is severely misinformed.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CALIBRATION ARCHITECTURAL OBJECTIVE                  │
├────────────────────────────────────────────────────────────────────────┤
│ A model is perfectly calibrated if, for all probability levels p:      │
│                                                                        │
│            P( Y = 1  |  P_model(Y = 1 | X) = p ) = p                   │
│                                                                        │
│ In a group of 100 patients predicted to have a 40% CAD likelihood,     │
│ exactly 40 of them must genuinely exhibit ≥ 50% stenosis.             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Calibration Methodologies Evaluated

### Method 1: Platt Scaling (Sigmoid Logistic Calibration) `[RECOMMENDED]`
Platt scaling maps raw model decision margins $s(\mathbf{x})$ to posterior probabilities using a two-parameter univariate logistic sigmoid:
$$\hat{P}(y = 1 \mid s) = \frac{1}{1 + \exp(A \cdot s + B)}$$
where $A$ and $B$ are scalar parameters estimated via maximum likelihood on a holdout calibration split.
- **Why It Is Suitable for HeartXAI:**
  - Parametric & Stable: With only 2 parameters to estimate, it is **highly resistant to overfitting on small datasets ($N = 303$)**.
  - Monotonicity: Preserves the rank-ordering (ROC-AUC) of the underlying tree ensemble.

### Method 2: Isotonic Regression
Isotonic regression fits a non-parametric, monotonic, piecewise-constant step function using the Pool Adjacent Violators Algorithm (PAVA):
$$\min_{m} \sum_{i=1}^n (y_i - m(s_i))^2 \quad \text{subject to } m(s_i) \le m(s_j) \text{ whenever } s_i \le s_j$$
- **Evaluation on $N = 303$:** Isotonic regression is prone to severe overfitting on small sample sizes ($N < 1,000$), creating erratic step plateaus.
- **Verdict:** **Platt Scaling is selected** as the primary calibration method.

---

## 3. Strict Separation of Calibration Data

A critical source of data leakage is fitting a calibration mapping on the same training data used to grow the decision trees:
- **The Risk:** Because tree models overfit their own training leaves, raw scores on training data are artificially extreme. Fitting Platt scaling on the training split produces a corrupted calibrator that fails on unseen data.
- **The Protocol in HeartXAI 2.0:**
  1. Calibration is fit exclusively using **Out-Of-Fold (OOF) cross-validation predictions** generated during the development phase via `sklearn.calibration.CalibratedClassifierCV(method='sigmoid', cv='prefit')`.
  2. The holdout test set ($n = 61$) evaluates the final calibrated probabilities, measuring Brier score and reliability curves on untouched data.

---

## 4. Calibration Evaluation Metrics

### 4.1 Brier Score
The primary quadratic scoring rule:
$$\text{BS} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$
- Benchmark for uninformative baseline (predicting cohort prevalence $0.4587$): $\text{BS}_{\text{base}} \approx 0.248$.
- **Target Acceptance Gate:** Calibrated model $\text{BS} \le 0.140$.

### 4.2 Reliability Diagrams & Expected Calibration Error (ECE)
Predictions are partitioned into $M = 10$ uniform probability bins ($[0.0, 0.1), [0.1, 0.2), \dots, [0.9, 1.0]$). For each bin $B_m$:
$$\text{acc}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} y_i, \quad \text{conf}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} p_i$$
$$\text{ECE} = \sum_{m=1}^{10} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
- **Target Acceptance Gate:** $\text{ECE} \le 0.08$.

---

## 5. Prediction Response Contract & Output Strata Specification

### 5.1 JSON Response Payload Structure
```json
{
  "prediction": {
    "task": "angiographic_cad_association_likelihood",
    "cad_likelihood_percent": 42.4,
    "confidence_interval_95": [38.1, 46.7],
    "output_band": "moderate_association_band",
    "calibration_status": {
      "is_calibrated": true,
      "method": "platt_scaling_sigmoid",
      "brier_score_benchmark": 0.118
    },
    "model_metadata": {
      "model_version": "XGBoost-Cleveland-Production-v2.4.1",
      "artifact_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "training_cohort": "UCI Cleveland Clinic Foundation (1981-1984)"
    },
    "disclaimer": "EDUCATIONAL ESTIMATION: This score reflects statistical association with historical study cohort patterns. It does not constitute a clinical medical diagnosis.",
    "calculated_at": "2026-11-18T05:39:15Z"
  }
}
```

### 5.2 Decoupling Output Bands from Clinical Diagnostic Categories
To support cognitive scannability without making unwarranted clinical claims:
- **Low Association Band ($< 30\%$):** Indicates clinical biomarkers exhibit low resemblance to cohort patients with significant angiographic narrowing.
- **Moderate Association Band ($30\% – 69\%$):** Indicates intermediate pattern resemblance; multiple cardiovascular variables deviate from baseline.
- **Elevated Association Band ($\ge 70\%$):** Indicates high pattern resemblance to study cohort patients with multi-vessel CAD.
- **Mandatory Guardrail:** These bands are explicitly labeled in the UI as **"Model-Output Score Bands"**, never as "Clinical Diagnosis" or "Cardiac Severity Stages".
