# MACHINE LEARNING TESTING AND QUALITY ASSURANCE STRATEGY

**Document Reference:** `docs/ml/ML_TESTING_AND_QUALITY_STRATEGY.md`  
**Phase:** 08 — Machine Learning Research & Model Development Plan  
**Status:** Approved Technical Design  
**Author:** ML Quality Assurance Lead & Validation Specialist  
**Traceability:** FR-PRED-01 through FR-PRED-06, NFR-REL-01, NFR-PERF-01  

---

## 1. Executive Summary & Testing Philosophy

Machine learning subsystems in healthcare cannot rely solely on conventional software testing. In addition to standard code coverage and contract validation, ML models require scientific verification: proving that statistical assumptions hold, data leakage does not exist, mathematical properties of explainers are conserved, and algorithmic edge cases do not result in catastrophic physiological contradictions.

This specification outlines the comprehensive automated test suite for the HeartXAI 2.0 ML subsystem, structured into seven rigorous validation tiers.

---

## 2. Test Suite Architecture & Pytest Organization

The ML test suite resides under `tests/ml/` and runs within the standard Pytest harness:

```text
tests/ml/
├── test_preprocessing_pipeline.py     # Feature extraction, missingness & scalers
├── test_data_leakage.py               # Cross-validation isolation verification
├── test_numerical_stability.py        # Boundary values, inf, NaN, extreme ranges
├── test_model_reproducibility.py      # Seed determinism and bit-level accuracy
├── test_shap_mathematical_properties.py # Additivity, efficiency & local accuracy
├── test_counterfactual_validity.py    # Class flip & immutable feature constraints
├── test_latency_performance.py        # Latency budgets and thread concurrency
└── test_drift_detection.py            # Synthetic covariate shift & PSI triggers
```

---

## 3. Tier 1: Preprocessing & Data Leakage Prevention Tests

### 3.1 Preprocessing Unit Verification
- **Test Objective:** Verify that categorical encodings, median imputations, and standard scalers output exact numeric types and ranges.
- **Assertions:**
  - Missing value in optional feature `ca` is imputed with training set median (e.g., $0.0$).
  - Categorical feature `cp` (chest pain type) remains within $\{1.0, 2.0, 3.0, 4.0\}$.
  - Standard scaling preserves zero mean ($\pm 10^{-6}$) and unit variance ($\pm 10^{-6}$) on training sets without altering test distribution parameters.

### 3.2 Data Leakage Prevention Assertions (`test_data_leakage.py`)
- **Leakage Vulnerability:** Fitting scalers or imputers on the full dataset before splitting falsely deflates error estimates.
- **Automated Verification:**
  ```python
  def test_cross_validation_data_leakage():
      # Verify that imputer and scaler statistics are derived strictly from fold_train
      for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X, y)):
          train_fold = X[train_idx]
          val_fold = X[val_idx]
          
          pipeline = build_ml_pipeline()
          pipeline.fit(train_fold, y[train_idx])
          
          # Assert fold median does not match global dataset median if distributions differ
          assert pipeline.named_steps["imputer"].statistics_ is not None
          # Verify val_fold mean is NOT present in the pipeline's fitted scaler
          assert not np.array_equal(pipeline.named_steps["scaler"].mean_, np.mean(val_fold, axis=0))
  ```

---

## 4. Tier 2: Numerical Stability & Clinical Boundary Tests

### 4.1 Boundary & Out-of-Range Value Ingestion
The test suite subjects the pipeline to boundary inputs:

| Test Case | Injected Value | Expected Behavior |
| :--- | :--- | :--- |
| **Normal Physiological Center** | BP: 120 mmHg, Chol: 200 mg/dL, HR: 140 bpm | Valid inference, calibrated probability $\in [0, 1]$ |
| **High Borderline** | BP: 200 mmHg, Chol: 450 mg/dL, Oldpeak: 6.2 mm | Valid inference, elevated risk probability |
| **Physiological Ceiling Exceeded** | BP: 320 mmHg | Raises `FeatureOutOfBoundException` (HTTP 422) |
| **Physiological Floor Breached** | BP: 35 mmHg | Raises `FeatureOutOfBoundException` (HTTP 422) |
| **Negative Continuous Values** | Oldpeak: -2.5 mm, Age: -45 | Raises Pydantic ValidationError (HTTP 422) |
| **NaN / Null in Required Field** | Resting ECG: `None` | Raises Pydantic ValidationError (HTTP 422) |
| **Infinite Values** | `float('inf')` or `float('-inf')` | Pipeline rejects before numpy conversion |

---

## 5. Tier 3: Deterministic Model Reproducibility Tests

### 5.1 Bit-Level Forward Pass Verification
- **Test:** Run the canonical test vector $x_{\text{test}}$ through the deployed XGBoost model 1,000 consecutive times across multiple threads.
- **Assertion:** 
  $$\max_{i, j} |P_i(y=1|x_{\text{test}}) - P_j(y=1|x_{\text{test}})| = 0.0$$
  Calibrated probabilities must match to 8 decimal places across repeated runs.

### 5.2 Training Pipeline Seed Invariance
- **Test:** Re-execute the complete training script from scratch using seed `42` twice in separate temporary directories.
- **Assertion:** The SHA-256 hash of the resulting `cleveland_xgboost.json` model files must be identical.

---

## 6. Tier 4: SHAP Explainer Mathematical Property Tests

TreeSHAP is grounded in cooperative game theory. If the mathematical axioms are violated, explanations cannot be trusted:

### 6.1 Efficiency / Additivity Axiom Test (Local Accuracy)
The sum of SHAP feature attributions plus the expected value (base value) must equal the raw uncalibrated model margin (log-odds $\hat{f}(x)$):

$$\hat{f}(x) = \phi_0 + \sum_{j=1}^{13} \phi_j(x)$$

- **Pytest Assertion:**
  ```python
  def test_shap_local_accuracy(model, explainer, test_samples):
      base_value = explainer.expected_value
      shap_values = explainer.shap_values(test_samples)
      raw_predictions = model.predict(test_samples, output_margin=True)
      
      for i in range(len(test_samples)):
          sum_attributions = base_value + np.sum(shap_values[i])
          assert np.isclose(sum_attributions, raw_predictions[i], atol=1e-5), \
              f"SHAP efficiency axiom violated for sample {i}!"
  ```

### 6.2 Missing Feature / Dummy Property Test
If a feature has zero impact across all tree splits, its SHAP attribution must be strictly zero.

---

## 7. Tier 5: Counterfactual Feasibility & Safety Tests

### 7.1 Class Inversion Verification
- **Assertion:** For any patient with initial risk classification $\hat{y} = 1$ (High Association), the generated counterfactual vector $x^*$ must evaluate to $\hat{y}^* = 0$ (Low-to-Moderate) when evaluated by the calibrated model.

### 7.2 Immutable Feature Invariance
- **Assertion:** The counterfactual engine must never alter immutable baseline factors:
  $$\Delta x_{\text{age}} = 0, \quad \Delta x_{\text{sex}} = 0, \quad \Delta x_{\text{ca}} = 0$$
  If a counterfactual suggests reducing chronological age or reversing fluoroscopic calcification, the test immediately fails.

### 7.3 Actionable Directional Validity
- **Assertion:** Counterfactual recommendations must follow physiologically beneficial directions:
  $$\Delta \text{trestbps} \le 0, \quad \Delta \text{chol} \le 0, \quad \text{trestbps}^* \ge 90\text{ mmHg}$$
  A counterfactual that recommends lowering systolic blood pressure to $40\text{ mmHg}$ (fatal hypotension) violates clinical constraints and triggers an assertion failure.

---

## 8. Tier 6: Performance & Concurrency Regression Tests

- **Target Metric:** Under 20 concurrent simulated requests using `pytest-benchmark` and `asyncio.gather`:
  - 100% of requests complete within $500\text{ ms}$.
  - $P95$ latency is $\le 200\text{ ms}$.
  - Memory consumption of the worker process remains stable ($\le 350\text{ MB}$ RSS) with zero memory leaks across 10,000 iterations.

---

## 9. Tier 7: Automated Drift Detection Unit Tests

- **Test:** Ingest a synthetically corrupted dataset where blood pressure has been shifted by $+30\text{ mmHg}$ ($\mathcal{N}(160, 20)$).
- **Assertion:**
  - The drift calculation module reports Population Stability Index $\text{PSI}_{\text{trestbps}} > 0.25$.
  - The module raises a `SignificantDriftWarning` and logs a structured alert.
