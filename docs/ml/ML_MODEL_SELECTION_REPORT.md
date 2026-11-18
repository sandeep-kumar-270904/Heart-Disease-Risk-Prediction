# HeartXAI 2.0 — Machine Learning Model Selection & Algorithmic Benchmarking

**Document ID:** `HX2-ML-006`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal ML Research Scientist & Statistical Learning Specialist  
**Traceability:** FR-020–FR-029, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-REQ-006  

---

## 1. Algorithmic Selection Philosophy: "Baseline-First Discipline"

In clinical machine learning on small-to-moderate sample sizes ($N = 303$), complex deep neural networks and exotic ensembles frequently overfit, memorizing noise while failing to generalize to external cohorts.

HeartXAI 2.0 enforces a **Baseline-First Strategy**:
1. **Mandatory Linear Baseline:** A regularized **Logistic Regression** model serves as the ground truth benchmark. Every complex model must demonstrate statistically significant improvement over Logistic Regression to justify adoption.
2. **Three Curated Candidate Architectures:** Evaluation is restricted to three distinct mathematical paradigms:
   - *Linear Model:* L2-Regularized Logistic Regression.
   - *Bagging Ensemble:* Random Forest Classifier.
   - *Gradient Boosted Ensemble:* Extreme Gradient Boosting (XGBoost).
3. **No Gratuitous Complexity:** Multi-Layer Perceptrons (MLPs), Support Vector Machines (SVMs), and Deep Learning architectures are rejected due to excessive parameterization relative to $N=303$, opaque decision boundaries, and poor TreeSHAP explainability compatibility.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ALGORITHMIC BENCHMARKING HIERARCHY                   │
├────────────────────────────────────────────────────────────────────────┤
│ LEVEL 1: Logistic Regression (Interpretable Linear Baseline)           │
│   │                                                                    │
│   ▼ (Must outperform on cross-validated ROC-AUC and Brier Score)       │
│ LEVEL 2: Random Forest (Non-linear Bagging Benchmark)                  │
│   │                                                                    │
│   ▼ (Must justify gradient boosting via TreeSHAP & inference latency) │
│ LEVEL 3: XGBoost (Regularized Gradient Boosted Candidate)              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. In-Depth Algorithmic Candidate Audits

---

### Candidate 01: L2-Regularized Logistic Regression (`LogisticRegression`)

#### 1. Why It Is Suitable
Logistic regression directly models the log-odds of angiographic CAD as a linear combination of clinical predictors:
$$\log \left( \frac{p}{1 - p} \right) = \beta_0 + \sum_{j=1}^{13} \beta_j x_j$$
It is the standard statistical benchmark in clinical epidemiology and medicine.

#### 2. Strengths & Weaknesses
- **Strengths:**
  - Convex optimization: Guarantees convergence to a global minimum without local optima traps.
  - Natural probability calibration: Minimizes logarithmic loss directly, producing well-calibrated probabilities without post-hoc scaling.
  - Transparent interpretability: Exponentiated coefficients ($\exp(\beta_j)$) represent standard clinical odds ratios (OR).
  - Extremely fast inference: Single dot product ($< 0.1\text{ms}$).
- **Weaknesses:**
  - Inability to automatically model complex non-linear thresholds (e.g., U-shaped mortality curves with cholesterol) or high-order feature interactions (e.g., ST depression modulated by max heart rate).

#### 3. Overfitting Risk & Role
- **Overfitting Risk:** Low on $N=303$ with $p=13$, especially when constrained by L2 Ridge penalty ($\lambda \|w\|_2^2$).
- **Architectural Role:** **Mandatory Baseline Benchmark**.

---

### Candidate 02: Random Forest Classifier (`RandomForestClassifier`)

#### 1. Why It Is Suitable
Random Forest constructs a diverse ensemble of $B$ de-correlated decision trees, each trained on a bootstrap sample of the training data with random feature subspace sampling ($\sqrt{p}$ features per split).

#### 2. Strengths & Weaknesses
- **Strengths:**
  - Non-parametric: Naturally captures non-linear thresholds and complex multi-feature interactions without manual engineering.
  - Robust to monotonic outliers (e.g., cholesterol $= 564\text{ mg/dL}$).
  - Reduces variance through bagging: $\text{Var}(\bar{X}) = \rho \sigma^2 + \frac{1 - \rho}{B} \sigma^2$.
- **Weaknesses:**
  - Can overfit on small datasets if tree depth (`max_depth`) is unconstrained.
  - Uncalibrated probabilities: Bagged tree averages tend to push probabilities away from $0$ and $1$ toward the sample mean, requiring post-hoc calibration (Platt scaling).
  - Moderate memory footprint ($100\text{–}300$ trees).

#### 3. Overfitting Risk & Role
- **Overfitting Risk:** Moderate; mitigated by setting `max_depth <= 5`, `min_samples_split >= 10`, `min_samples_leaf >= 4`.
- **Architectural Role:** **Secondary Non-Linear Candidate**.

---

### Candidate 03: Extreme Gradient Boosting (`XGBoostClassifier`)

#### 1. Why It Is Suitable
XGBoost builds trees sequentially, with each new tree minimizing the second-order Taylor expansion of the loss function relative to the pseudo-residuals of the previous ensemble:
$$\mathcal{L}^{(t)} \approx \sum_{i=1}^n \left[ l(y_i, \hat{y}^{(t-1)}) + g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i) \right] + \Omega(f_t)$$
where $\Omega(f_t) = \gamma T + \frac{1}{2} \lambda \|w\|^2$ enforces strict structural regularization.

#### 2. Strengths & Weaknesses
- **Strengths:**
  - State-of-the-art predictive performance on tabular clinical data.
  - Advanced regularization: Built-in L1 ($\alpha$) and L2 ($\lambda$) penalties, column subsampling (`colsample_bytree`), and tree shrinkage (`learning_rate <= 0.05`).
  - Native missing value routing: Automatically learns optimal default branch direction for missing fluoroscopy (`ca`) and scintigraphy (`thal`).
  - Seamless TreeSHAP integration: `shap.TreeExplainer` executes in $O(T L D^2)$ polynomial time on XGBoost trees, enabling instantaneous real-time explainability.
- **Weaknesses:**
  - High risk of memorization if hyperparameter tuning is sloppy. Shallow trees (`max_depth = 3`) are mandatory on $N=303$.

#### 3. Overfitting Risk & Role
- **Overfitting Risk:** High if unregularized; Low-to-Moderate under conservative hyperparameters (`max_depth=3`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_lambda=2.0`).
- **Architectural Role:** **Primary Production Candidate (Subject to Cross-Validation Superiority)**.

---

## 3. Systematic Algorithmic Comparison Matrix

| Evaluation Dimension | Logistic Regression | Random Forest | XGBoost | Deep Neural Network (MLP) |
| :--- | :---: | :---: | :---: | :---: |
| **Mathematical Paradigm** | Generalized Linear Model | Bagging Decision Trees | Gradient Boosted Trees | Multi-Layer Perceptron |
| **Suitability for $N=303$** | **Exceptional** | **Good (Constrained)** | **Good (Regularized)**| **Extremely Poor (Overfits)** |
| **Captures Non-Linearity** | No (Linear Only) | **Yes** | **Yes** | Yes |
| **Probability Calibration**| **Naturally Calibrated**| Requires Calibration | Requires Calibration | Requires Calibration |
| **TreeSHAP Compatibility** | N/A (Linear SHAP) | Good ($O(T L D^2)$) | **Optimal (Native C++)**| KernelSHAP Only ($O(2^M)$, Slow)|
| **Inference Latency** | $< 0.1\text{ms}$ | $\approx 2.0\text{ms}$ | **$\approx 1.5\text{ms}$** | $> 10.0\text{ms}$ |
| **Missing Value Handling** | Requires Imputation | Requires Imputation | **Native Learned Routing**| Requires Imputation |
| **Selection Verdict** | **Baseline Benchmark** | **Candidate 2** | **Candidate 1 (Primary)**| **REJECTED** |

---

## 4. Final Recommendation & Promotion Gate

1. **Mandatory Baseline Evaluation:** During Phase B experimentation, Logistic Regression must be trained alongside Random Forest and XGBoost using Stratified 5-Fold Nested Cross-Validation.
2. **Promotion Threshold:** XGBoost will be promoted to production **only if** it demonstrates:
   - A statistically significant increase in cross-validated **ROC-AUC ($\ge +0.03$)** over regularized Logistic Regression.
   - An equal or superior **Brier score ($\le 0.14$)** after probability calibration.
3. If XGBoost fails to outperform Logistic Regression on cross-validated Brier score and ROC-AUC, **Logistic Regression will be selected for production deployment** in accordance with the principle of Occam's Razor.
