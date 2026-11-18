# HeartXAI 2.0 — SHAP Explainability Subsystem Design & Validation Specification

**Document ID:** `HX2-ML-010`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal ML Research Scientist & XAI Architect  
**Traceability:** FR-030–FR-034, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-REQ-006  

---

## 1. Explainability Philosophy & Epistemological Boundaries

Shapley Additive exPlanations (SHAP), derived from cooperative game theory, provide mathematically rigorous local feature attributions. 

However, in digital cardiology, **SHAP values are frequently misinterpreted as causal biological proof**. HeartXAI 2.0 enforces three strict epistemological distinctions:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE THREE LEVELS OF EXPLANATION                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. MATHEMATICAL MODEL EXPLANATION (WHAT SHAP ACTUALLY IS)              │
│    - Explains how much a specific feature value shifted the tree       │
│      ensemble's output probability away from the cohort baseline.      │
│                                                                        │
│ 2. STATISTICAL ASSOCIATION (WHAT THE COHORT SHOWS)                     │
│    - Measures observed co-occurrence in historical hospital data       │
│      (e.g., patients with higher resting BP had higher CAD rates).     │
│                                                                        │
│ 3. CAUSAL BIOLOGICAL EXPLANATION (WHAT SHAP CAN NEVER PROVE)           │
│    - Proving that lowering this patient's blood pressure today will    │
│      cure or reverse plaque stenosis in their coronary arteries.       │
│    - Requires randomized controlled trials, not observational trees!   │
└────────────────────────────────────────────────────────────────────────┘
```

> **Mandatory Rule:** SHAP attributions **must never** be described as proving that a feature caused the patient's heart condition.

---

## 2. Shapley Axioms & Mathematical Guarantees

TreeSHAP is uniquely selected because it satisfies the four foundational Shapley axioms:

1. **Efficiency (Local Accuracy):** The sum of feature attributions equals the difference between the model output $f(\mathbf{x})$ and the base expected value $E[f(\mathbf{x})]$:
   $$\sum_{i=1}^{13} \phi_i(\mathbf{x}) = f(\mathbf{x}) - E[f(\mathbf{x})]$$
2. **Symmetry:** If two features contribute identically to all possible feature subsets, their SHAP values are equal.
3. **Dummy / Null Player:** If a feature has no impact on predictions across any subset of features, its attribution is strictly zero ($\phi_i = 0$).
4. **Additivity:** When ensembling multiple trees, the ensemble SHAP value is the arithmetic sum of individual tree attributions.

---

## 3. Explainer Selection & Background Baseline

### 3.1 Algorithm-Specific Explainer Mapping
- **For Candidate 1 (XGBoost):** `shap.TreeExplainer(model, data=background_data, feature_perturbation="interventional", model_output="probability")`.
- **For Baseline (Logistic Regression):** `shap.LinearExplainer(model, masker=background_data)`.

### 3.2 Background Dataset Architecture
To compute conditional expectations $E[f(\mathbf{x}) \mid \mathbf{x}_S]$ without reference-point distortion:
- **Baseline Cohort:** The $n = 242$ training development set.
- **Medoid Summarization:** To ensure sub-15ms computation during real-time API requests, `shap.kmeans(X_train, 50)` summarizes the background distribution into 50 weighted medoid centroids.
- **Expected Value:** For the Cleveland training cohort, the baseline expected probability is:
  $$E[f(\mathbf{x})] \approx 0.380 \text{ (38.0\%)}$$

---

## 4. Local Waterfall Attribution Pipeline

For each inference on patient vector $\mathbf{x}$:
1. **Base Expected Likelihood:** $E[f(\mathbf{x})] = 0.380$.
2. **Local Feature Attribution Vector:** $\boldsymbol{\phi} = [\phi_{\text{age}}, \phi_{\text{sex}}, \dots, \phi_{\text{thal}}] \in \mathbb{R}^{13}$.
3. **Final Calibrated Likelihood:** $f(\mathbf{x}) = E[f(\mathbf{x})] + \sum_{i=1}^{13} \phi_i$.

```
Base Expected Likelihood: 38.0%
─────────────────────────────────────────────────────────────────────────
Resting BP (+24 mmHg)         │===================▲ (+14.1%)  [Crimson 500]
Serum Cholesterol (+45 mg/dL) │==========▲          (+8.2%)   [Crimson 500]
Age (54 years)                │===▲                 (+3.4%)   [Crimson 500]
Thallium Stress: Normal       │         ▼========   (-6.1%)   [Blue 500]
Max Heart Rate (168 bpm)      │      ▼===========   (-11.6%)  [Blue 500]
─────────────────────────────────────────────────────────────────────────
Center Baseline: 0.00 Net Impact
Final Model Output Likelihood: 46.0%
```

### 4.1 Directional Phrasing & Visual Token Binding
- **Positive SHAP Value ($\phi_i > 0$):** Pushes predicted likelihood **higher** than the cohort baseline. Bound to semantic Crimson token (`#EF4444`) with symbol `▲`.
- **Negative SHAP Value ($\phi_i < 0$):** Pushes predicted likelihood **lower** than the cohort baseline. Bound to semantic Blue token (`#3B82F6`) with symbol `▼`.
- *Accessibility Rule:* Crimson vs Blue delivers high contrast across all color-blind variants (deuteranopia, protanopia, tritanopia). Red vs Green is strictly banned.

---

## 5. Automated Validation Tests for SHAP Correctness

Every model build must pass automated explainability integrity assertions:

1. **Sum Consistency Test:**
   ```python
   def test_shap_local_accuracy(model, explainer, test_sample):
       shap_values = explainer.shap_values(test_sample)[0]
       expected_val = float(explainer.expected_value)
       predicted_prob = float(model.predict_proba(test_sample)[0][1])
       
       # Assert mathematical equality within numerical precision
       assert abs((expected_val + np.sum(shap_values)) - predicted_prob) < 1e-4
   ```
2. **Monotonicity & Invariance Check:** Increasing resting blood pressure while holding other variables constant must monotonically increase $\phi_{\text{trestbps}}$.
3. **Performance Budget:** Mean SHAP calculation time across 100 requests must measure $< 25\text{ms}$.
