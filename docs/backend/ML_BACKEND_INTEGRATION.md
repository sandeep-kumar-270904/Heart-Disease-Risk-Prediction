# HeartXAI 2.0 — Machine Learning Backend Integration Specification

**Document ID:** `HX2-BE-008`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal ML Systems Architect & Backend Lead  
**Traceability:** FR-020–FR-039, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-ARCH-009  

---

## 1. Machine Learning Integration Architecture

The ML subsystem in HeartXAI 2.0 executes inference, statistical explainability (TreeSHAP), and counterfactual exploration for the Cleveland-cohort XGBoost tree ensemble.

### 1.1 Architectural Guarantees
1. **Mathematical Reproducibility:** Every inference result is cryptographically bound to its model artifact SHA256 checksum, feature vector snapshot, and preprocessing pipeline version.
2. **CPU Isolation via Worker Pool:** Model inference and TreeSHAP calculations are executed within Python's `asyncio.to_thread()` executor to prevent blocking the asynchronous HTTP event loop.
3. **Strict Epistemological Boundaries:** Model probability outputs are strictly framed as **Angiographic CAD Association Likelihood** based on historical observational study cohorts; zero diagnostic certainty is inferred.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ML PIPELINE DATA FLOW                             │
├────────────────────────────────────────────────────────────────────────┤
│ Raw Clinical Inputs (13 Features from AssessmentService)               │
│       │                                                                │
│       ▼                                                                │
│ [ Preprocessor: Feature Order, Imputation (ca/thal), Scaling ]        │
│       │                                                                │
│       ▼                                                                │
│ [ ThreadPoolExecutor (asyncio.to_thread) ]                             │
│       ├──► XGBoost Classifier (cleveland_xgboost_v2.4.1.json)         │
│       │       │                                                        │
│       │       ▼                                                        │
│       │    Continuous Probability (p) + 95% Wilson Confidence Interval │
│       │                                                                │
│       └──► TreeSHAP Explainer (shap.TreeExplainer)                     │
│               │                                                        │
│               ▼                                                        │
│            13 Local Feature Attribution Values (φ_i)                   │
│                                                                        │
│       ▼                                                                │
│ Transactional Persistence via UnitOfWork (assessments, inferences, shap)│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Feature Vector Alignment & Preprocessing Specification

The model was trained on the 13 canonical clinical features of the UCI Cleveland Heart Disease dataset. Input ordering and transformations **must match the training pipeline exactly**:

| Vector Index | Feature Name | Clinical Meaning | Expected Canonical Type / Bounds | Missing Value Strategy |
| :---: | :--- | :--- | :--- | :--- |
| `0` | `age` | Age in years | `float` $[18.0, 100.0]$ | Disallowed (Required) |
| `1` | `sex` | Biological Sex | `int` $\{0 = \text{Female}, 1 = \text{Male}\}$ | Disallowed (Required) |
| `2` | `cp` | Chest Pain Type | `int` $\{0, 1, 2, 3\}$ | Disallowed (Required) |
| `3` | `trestbps` | Resting Blood Pressure | `float` $[70.0, 240.0]\text{ mmHg}$ | Disallowed (Required) |
| `4` | `chol` | Serum Cholesterol | `float` $[100.0, 600.0]\text{ mg/dL}$ | Disallowed (Required) |
| `5` | `fbs` | Fasting Blood Sugar $> 120\text{ mg/dL}$ | `int` $\{0 = \text{False}, 1 = \text{True}\}$ | Disallowed (Required) |
| `6` | `restecg` | Resting ECG Results | `int` $\{0, 1, 2\}$ | Disallowed (Required) |
| `7` | `thalach` | Maximum Heart Rate Achieved | `float` $[60.0, 220.0]\text{ bpm}$ | Disallowed (Required) |
| `8` | `exang` | Exercise Induced Angina | `int` $\{0 = \text{No}, 1 = \text{Yes}\}$ | Disallowed (Required) |
| `9` | `oldpeak` | ST Depression by Exercise | `float` $[0.0, 6.2]\text{ mm}$ | Disallowed (Required) |
| `10` | `slope` | Slope of Peak ST Segment | `int` $\{0, 1, 2\}$ | Disallowed (Required) |
| `11` | `ca` | Fluoroscopy Major Vessels | `float` $\{0.0, 1.0, 2.0, 3.0\}$ | **Median Imputation** ($0.0$) |
| `12` | `thal` | Thallium Scintigraphy | `float` $\{1.0, 2.0, 3.0\}$ | **Median Imputation** ($2.0$) |

### 2.1 Imputation Policy for Advanced Imaging
If a patient has not undergone fluoroscopy or stress scintigraphy, `ca` and `thal` are omitted in the input DTO. The preprocessor imputes cohort median values and writes an explicit flag: `has_imputed_features: True` into the `inference_results` record.

---

## 3. TreeSHAP Attribution Computation

```python
import shap
import numpy as np

class ExplainabilityEngine:
    def __init__(self, model, background_data):
        self.model = model
        self.explainer = shap.TreeExplainer(
            model=self.model,
            data=background_data,
            feature_perturbation="interventional",
            model_output="probability"
        )
        self.expected_value = float(self.explainer.expected_value)

    def explain_instance(self, feature_vector: np.ndarray) -> dict:
        # feature_vector shape: (1, 13)
        shap_values = self.explainer.shap_values(feature_vector)[0]
        
        # Verify Local Accuracy Property: sum(phi_i) == f(x) - E[f(x)]
        prediction_prob = float(self.model.predict_proba(feature_vector)[0][1])
        sum_shap = float(np.sum(shap_values))
        assert abs((self.expected_value + sum_shap) - prediction_prob) < 1e-4

        return {
            "base_value": self.expected_value,
            "prediction": prediction_prob,
            "shap_attributions": shap_values.tolist()
        }
```

---

## 4. Counterfactual "What-If" Scenario Simulator

The counterfactual engine performs **constrained local perturbation** of modifiable clinical variables:

```python
MODIFIABLE_BOUNDS = {
    "trestbps": (90.0, 200.0),    # Resting BP (mmHg)
    "chol": (120.0, 350.0),       # Serum Cholesterol (mg/dL)
    "fbs": (0, 1),                # Fasting Blood Sugar
    "thalach": (90.0, 200.0)      # Exercise Tolerance (bpm)
}

NON_MODIFIABLE_FEATURES = {"age", "sex", "ca", "thal"}

def simulate_counterfactual(
    base_features: np.ndarray, 
    modifications: dict[str, float], 
    pipeline
) -> dict:
    # 1. Reject modification of immutable biological baseline features
    for key in modifications:
        if key in NON_MODIFIABLE_FEATURES:
            raise ClinicalBoundaryException(f"Feature '{key}' is a biological baseline and cannot be modified.")

    # 2. Check physiological feasibility bounds
    simulated_vector = base_features.copy()
    for feature_name, value in modifications.items():
        min_val, max_val = MODIFIABLE_BOUNDS[feature_name]
        if not (min_val <= value <= max_val):
            raise PhysiologicalClampException(
                f"Simulated value {value} for {feature_name} violates outpatient viability limits ({min_val}-{max_val})."
            )
        feature_idx = FEATURE_NAMES.index(feature_name)
        simulated_vector[0][feature_idx] = value

    # 3. Compute simulated prediction
    simulated_prob = float(pipeline.predict_proba(simulated_vector)[0][1])
    baseline_prob = float(pipeline.predict_proba(base_features)[0][1])

    return {
        "baseline_likelihood": baseline_prob,
        "simulated_likelihood": simulated_prob,
        "delta_percent": (simulated_prob - baseline_prob) * 100,
        "feasibility_score": 0.95
    }
```

---

## 5. Model Integrity & Lifecycle Verification

1. **Artifact Verification at Startup:** Upon application initialization (`main.py` lifespan), the `InferencePipeline` calculates the SHA256 checksum of `cleveland_xgboost_v2.4.1.json` and compares it against `checksums.sha256`. If the checksum fails, the application aborts startup immediately, preventing execution of corrupted models.
2. **Execution Time Budget:** A timeout of $500\text{ms}$ is allocated for inference and SHAP calculation combined. If computation exceeds this budget, the task is terminated and an alert logged to Sentry.
