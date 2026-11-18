# MACHINE LEARNING BACKEND INTEGRATION CONTRACT

**Document Reference:** `docs/ml/ML_BACKEND_INTEGRATION_CONTRACT.md`  
**Phase:** 08 — Machine Learning Research & Model Development Plan  
**Status:** Approved Technical Design  
**Author:** ML Integration Specialist & Backend Systems Architect  
**Traceability:** FR-PRED-01 through FR-PRED-06, NFR-PERF-01, NFR-SEC-03, ADR-009, ADR-011  

---

## 1. Executive Summary & Architectural Alignment

This contract establishes the formal engineering interface between the HeartXAI 2.0 Machine Learning subsystem (`app/ml/`) and the FastAPI backend service tier (`app/services/prediction_service.py`). 

To avoid the common anti-pattern where ML models execute unconstrained within asynchronous event loops (causing CPU starvation and blocking concurrent HTTP request handling), this specification defines:
1. Strict input tensor ordering and validation types.
2. An asynchronous, non-blocking worker execution model utilizing `asyncio.to_thread` with an isolated bounded thread pool.
3. Formal input/output data contracts matching Pydantic V2 schemas.
4. Latency performance budgets ($P50 < 80\text{ ms}, P95 < 200\text{ ms}$).
5. Deterministic error hierarchies and graceful degradation modes.

---

## 2. Subsystem Layout & Code Boundaries

The backend ML subsystem is structured within `app/ml/` as follows:

```text
app/ml/
├── __init__.py
├── engine.py                  # Core inference runtime and artifact manager
├── pipeline.py                # Preprocessing, imputation, and feature alignment
├── explainer.py               # TreeSHAP computation engine
├── counterfactual.py          # Feasible counterfactual generation engine
├── schemas.py                 # Internal ML DTOs and tensor contracts
└── exceptions.py              # ML-specific domain exceptions
```

`app/services/prediction_service.py` is the only external caller permitted to interface directly with `app/ml/engine.py`. Routers (`app/api/v1/endpoints/predictions.py`) never import ML internals directly.

---

## 3. Input Feature Tensor Specification

### 3.1 Strict Tensor Ordering & Canonical Dtypes

The ML inference engine requires a contiguous 2D NumPy array of shape $(N, 13)$ where $N=1$ for online transactions. The 13 features must arrive in exact canonical order:

| Index | Feature Key | Canonical Type | Accepted Units | Range / Permitted Values |
| :---: | :--- | :---: | :---: | :---: |
| 0 | `age` | `float32` | Years | $20.0 - 100.0$ |
| 1 | `sex` | `float32` | Binary code | $0.0$ (Female), $1.0$ (Male) |
| 2 | `cp` | `float32` | Categorical code | $1.0$ (Typical), $2.0$ (Atypical), $3.0$ (Non-anginal), $4.0$ (Asympt.) |
| 3 | `trestbps` | `float32` | mmHg | $80.0 - 240.0$ |
| 4 | `chol` | `float32` | mg/dL | $100.0 - 600.0$ |
| 5 | `fbs` | `float32` | Binary code | $0.0$ ($\le 120$), $1.0$ ($> 120$ mg/dL) |
| 6 | `restecg` | `float32` | Categorical code | $0.0$ (Normal), $1.0$ (ST-T wave abn.), $2.0$ (LVH) |
| 7 | `thalach` | `float32` | bpm | $60.0 - 220.0$ |
| 8 | `exang` | `float32` | Binary code | $0.0$ (No), $1.0$ (Yes) |
| 9 | `oldpeak` | `float32` | mm depression | $0.0 - 10.0$ |
| 10 | `slope` | `float32` | Categorical code | $1.0$ (Upsloping), $2.0$ (Flat), $3.0$ (Downsloping) |
| 11 | `ca` | `float32` | Vessel count | $0.0, 1.0, 2.0, 3.0$ |
| 12 | `thal` | `float32` | Categorical code | $3.0$ (Normal), $6.0$ (Fixed defect), $7.0$ (Reversible defect) |

### 3.2 Preprocessing Contract
1. **Unit Conversion:** If the client submits blood pressure or cholesterol in alternative international units (e.g., mmol/L for cholesterol via country localization headers), `prediction_service.py` performs deterministic conversion to standard units before constructing the ML feature vector.
2. **Missing Clinical Values:** If non-essential optional fields (`ca` or `thal`) are omitted in client input, the pipeline applies the serialised training median imputer (`cleveland_imputer_v1.0.0.joblib`). All other 11 features are strictly mandatory; missing values trigger HTTP 422 Unprocessable Entity.

---

## 4. Output Contract & Schema Definition

The ML engine produces a strongly-typed `MLInferenceResult` dataclass, which the prediction service maps into the public API response schema (`PredictionResponse`):

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class SHAPFeatureContribution:
    feature_name: str
    feature_value: float
    shap_value: float
    direction: str            # "INCREASES_RISK" | "DECREASES_RISK"
    clinical_label: str
    display_unit: str

@dataclass(frozen=True)
class CounterfactualRecommendation:
    feature_name: str
    current_value: float
    target_value: float
    delta: float
    unit: str
    clinical_guideline_note: str

@dataclass(frozen=True)
class MLInferenceResult:
    prediction_id: str
    model_version: str
    calibrated_probability: float    # Range: [0.0, 1.0]
    binary_classification: int       # 0: Low-to-Moderate, 1: High Association
    risk_category: str               # "LOW_TO_MODERATE" | "HIGH_ASSOCIATION"
    brier_score_expected: float      # Model calibration baseline (e.g. 0.128)
    shap_base_value: float           # Expected log-odds across background
    shap_contributions: List[SHAPFeatureContribution]
    counterfactuals: List[CounterfactualRecommendation]
    inference_time_ms: float
    calibration_method: str          # "Platt Scaling (Sigmoid)"
```

---

## 5. Concurrency Model & Async Execution Architecture

### 5.1 The CPU-Starvation Challenge
Python's Global Interpreter Lock (GIL) and heavy numerical libraries (NumPy, XGBoost, TreeSHAP) execute CPU-bound loops. If invoked directly in an async route handler:
```python
# ANTI-PATTERN - BLOCKS FASTAPI EVENT LOOP
@router.post("/predict")
async def predict(data: PredictionRequest):
    result = ml_engine.predict(data) # CPU loop blocks all incoming network requests!
    return result
```

### 5.2 Thread Pool Worker Offloading
HeartXAI 2.0 uses a dedicated, bounded `ThreadPoolExecutor` isolated from standard I/O threads:

```python
# APPROVED ARCHITECTURAL PATTERN
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MLInferenceEngine:
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="heartxai_ml_worker"
        )

    async def run_inference_pipeline_async(self, raw_features: dict) -> MLInferenceResult:
        loop = asyncio.get_running_loop()
        # Offload synchronous ML computation to thread pool
        return await loop.run_in_executor(
            self._executor,
            self._execute_sync_pipeline,
            raw_features
        )

    def _execute_sync_pipeline(self, raw_features: dict) -> MLInferenceResult:
        # 1. Transform dict to tensor
        # 2. Impute & scale
        # 3. Model forward pass (XGBoost)
        # 4. Platt calibration sigmoid
        # 5. TreeSHAP computation
        # 6. Counterfactual generation
        ...
```

---

## 6. Performance & Latency Budgets

Under production workload (10 concurrent requests/sec per worker container):

| Pipeline Stage | Target P50 | Target P95 | Upper Bound P99 | Strategy / Constraints |
| :--- | :---: | :---: | :---: | :--- |
| **Input Parsing & Validation** | $1\text{ ms}$ | $3\text{ ms}$ | $5\text{ ms}$ | Pydantic V2 native C-validation |
| **Preprocessing & Imputation** | $1\text{ ms}$ | $2\text{ ms}$ | $4\text{ ms}$ | Pre-warmed vectorized NumPy |
| **XGBoost Inference Pass** | $3\text{ ms}$ | $8\text{ ms}$ | $15\text{ ms}$ | JSON booster in C++ engine |
| **Platt Scaling Calibration** | $<1\text{ ms}$ | $1\text{ ms}$ | $2\text{ ms}$ | Logistic sigmoid computation |
| **TreeSHAP Contribution** | $25\text{ ms}$ | $60\text{ ms}$ | $110\text{ ms}$ | Pre-computed 25-medoid background |
| **Counterfactual Optimization** | $30\text{ ms}$ | $75\text{ ms}$ | $140\text{ ms}$ | Scipy L-BFGS-B bounded $\le 50$ iters |
| **Total ML Pipeline** | **$60\text{ ms}$** | **$150\text{ ms}$** | **$280\text{ ms}$** | Strict timeout set at $500\text{ ms}$ |

---

## 7. Error Handling, Timeouts & Fallback Hierarchy

### 7.1 Domain Exceptions

```python
class MLException(Exception):
    """Base domain exception for all ML operations."""

class ModelIntegrityException(MLException):
    """Raised when artifact SHA-256 hash or signature verification fails."""

class FeatureOutOfBoundException(MLException):
    """Raised when continuous inputs exceed physiologically plausible limits."""

class MLInferenceTimeoutException(MLException):
    """Raised when inference + explanation execution exceeds 500ms budget."""
```

### 7.2 Graceful Degradation Strategy
If the full pipeline encounters a timeout or transient failure in secondary explanation generation:
1. **Primary Prediction Preserved:** If XGBoost prediction and calibration succeed, the risk score is immediately returned.
2. **Partial Explanation Fallback:** If TreeSHAP completes but counterfactual generation times out ($>200\text{ ms}$), the system returns the SHAP values and an empty counterfactual list with a metadata notice: `"counterfactual_status": "TIMEOUT_DEGRADED"`.
3. **Model Fallback:** If XGBoost fails to load or raises an execution exception, the engine falls back to the pre-loaded L2-regularized Logistic Regression model, logging a severity `CRITICAL` alert to Sentry.

---

## 8. Cold-Start Handling & Warmup Protocols

To eliminate first-request latency spikes (JIT compilation and tree structure allocation):
1. **Application Lifespan Event:** During FastAPI startup (`lifespan`), `MLInferenceEngine` initializes:
   - Loads model JSON, calibrator, scaler, and SHAP explainer into process memory.
   - Executes a dummy synthetic inference vector through the full pipeline (`_execute_sync_pipeline`).
   - Validates that dummy output matches expected test bounds.
2. **Readiness Probe (`/health/ready`):** Returns HTTP 200 only after the warmup pass completes successfully. If warmup fails, the container fails its Kubernetes/Docker readiness probe and does not receive live user traffic.
