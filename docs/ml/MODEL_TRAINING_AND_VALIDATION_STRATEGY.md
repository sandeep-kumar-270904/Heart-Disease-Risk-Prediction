# HeartXAI 2.0 — Leakage-Resistant Model Training & Validation Strategy

**Document ID:** `HX2-ML-007`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal ML Validation Specialist & Applied Data Scientist  
**Traceability:** FR-020–FR-029, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-REQ-006  

---

## 1. Validation Philosophy: "Zero Data Leakage"

In clinical machine learning, **data leakage** is the primary cause of falsely optimistic model performance that crashes when deployed in clinical reality. 

Common subtle leakage vectors include:
- Calculating feature means/medians on the full dataset before splitting.
- Fitting standard scalers or one-hot encoders across the entire cohort.
- Optimizing hyperparameters against the test set.
- Applying oversampling (SMOTE) before cross-validation fold splitting.

HeartXAI 2.0 enforces a **Strict Leakage-Proof Validation Architecture**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   LEAKAGE-PROOF PARTITIONING TOPOLOGY                  │
├────────────────────────────────────────────────────────────────────────┤
│ Full Cohort (N = 303)                                                  │
│   ├── Holdout Test Set (20%, n = 61): LOCKED IN VAULT UNTIL FINAL AUDIT│
│   └── Development Set (80%, n = 242):                                  │
│         │                                                              │
│         ▼ (Repeated Stratified 5-Fold Nested Cross-Validation)         │
│       ┌────────────────────────────────────────────────────────┐       │
│       │ Outer Loop (5 Folds): Model Generalization Assessment  │       │
│       │   └── Inner Loop (5 Folds): Hyperparameter Tuning      │       │
│       │         └── Pipeline: Impute -> Scale -> Fit Classifier│       │
│       └────────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Dataset Splitting & Stratification Protocol

### 2.1 The Two-Way Stratified Split
The 303 records are partitioned into an $80/20$ split using **multivariate stratification** on both the target label and biological sex:
1. **Holdout Test Set ($20\%$, $n = 61$ records):**
   - Stratified to preserve $54.1\%$ Class 0 / $45.9\%$ Class 1 and $68\%$ Male / $32\%$ Female.
   - **Vault Rule:** The holdout test set is completely sequestered during development. It is touched **exactly once** during the final sign-off audit.
2. **Development / Training Set ($80\%$, $n = 242$ records):**
   - Used for all feature selection, pipeline construction, cross-validation, and hyperparameter tuning.

### 2.2 Seed Governance
All pseudorandom operations (data splits, cross-validation fold generation, tree initialization) are bound to an explicit, versioned random seed:
```python
RANDOM_SEED = 42
```
This guarantees that any engineer or auditor running the pipeline on identical hardware reproduces identical fold splits and model parameters down to bit-level parity.

---

## 3. Nested Cross-Validation Architecture

To prevent **optimism bias** during hyperparameter selection on $n = 242$ samples, we enforce **Nested Stratified Cross-Validation**:

```
Outer Fold 1 (Eval)  ◄── Inner CV (5 Folds on Outer Train) ──► Tune (Optuna/Grid)
Outer Fold 2 (Eval)  ◄── Inner CV (5 Folds on Outer Train) ──► Tune (Optuna/Grid)
Outer Fold 3 (Eval)  ◄── Inner CV (5 Folds on Outer Train) ──► Tune (Optuna/Grid)
Outer Fold 4 (Eval)  ◄── Inner CV (5 Folds on Outer Train) ──► Tune (Optuna/Grid)
Outer Fold 5 (Eval)  ◄── Inner CV (5 Folds on Outer Train) ──► Tune (Optuna/Grid)
```

1. **Inner Loop (Hyperparameter Tuning):**
   - 5-Fold Stratified CV on the outer training split ($n \approx 193$).
   - Optimizes hyperparameters against mean cross-validated log-loss / ROC-AUC.
2. **Outer Loop (Generalization Estimation):**
   - Evaluates the winning parameter set on the untouched outer test fold ($n \approx 49$).
   - Repeated across 5 outer folds (and 5 repeats with different seeds = 25 outer test evaluations), generating robust empirical performance distributions and confidence intervals.

---

## 4. Leakage-Proof Scikit-Learn Pipeline Specification

All data transformations are encapsulated inside an atomic `sklearn.pipeline.Pipeline`. This ensures that transformers are fitted **strictly on training folds** and only transform validation/test folds:

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

NUMERICAL_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_FEATURES = ["sex", "cp", "fbs", "restecg", "exang", "slope"]
IMPUTED_IMAGING_FEATURES = ["ca", "thal"]

# 1. Preprocessor definition
preprocessor = ColumnTransformer(
    transformers=[
        ("num", Pipeline([
            ("scaler", StandardScaler())
        ]), NUMERICAL_FEATURES),
        
        ("imaging", Pipeline([
            ("median_imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), IMPUTED_IMAGING_FEATURES),
        
        ("cat", "passthrough", CATEGORICAL_FEATURES)
    ]
)

# 2. Complete leakage-proof pipeline
full_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=2.0,
        random_state=RANDOM_SEED,
        eval_metric="logloss"
    ))
])
```

---

## 5. Statistical Limitations of the Small Sample Size ($N = 303$)

A dataset of 303 patients introduces inherent statistical variance that must be honestly recognized:
1. **Wide Confidence Intervals:** A holdout test set of $n = 61$ cases means that a difference of just **2 incorrectly classified patients** alters the measured accuracy or sensitivity by:
   $$\Delta = \frac{2}{61} \approx 3.28\%$$
   Therefore, reporting metrics without $95\%$ confidence intervals is unscientific.
2. **Curse of Dimensionality:** With $p = 13$ features and $n = 242$ training cases, the ratio of samples to features is:
   $$\frac{n}{p} = \frac{242}{13} \approx 18.6 \text{ samples per feature}$$
   This is sufficient for shallow tree ensembles (`max_depth = 3`) and regularized linear models, but strictly prohibits unregularized deep networks or high-cardinality interaction terms.
