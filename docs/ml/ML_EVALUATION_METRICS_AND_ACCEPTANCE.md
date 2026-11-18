# HeartXAI 2.0 — Machine Learning Evaluation Metrics & Model Acceptance Gates

**Document ID:** `HX2-ML-008`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Research Specification  
**Author:** Principal ML Validation Specialist & Healthcare Quality Lead  
**Traceability:** FR-020–FR-029, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-REQ-006  

---

## 1. Evaluation Philosophy: "Beyond Accuracy"

In healthcare machine learning, **accuracy is an inadequate and potentially dangerous evaluation metric**. 

A model achieving $85\%$ accuracy could harbor a $30\%$ false-negative rate among female patients, sending individuals with severe ischemic heart disease home without medical follow-up.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CLINICAL ASYMMETRY OF ERROR COSTS                    │
├───────────────────────────────────┬────────────────────────────────────┤
│ FALSE NEGATIVE (TYPE II ERROR)    │ FALSE POSITIVE (TYPE I ERROR)      │
├───────────────────────────────────┼────────────────────────────────────┤
│ • Model predicts Low Likelihood.  │ • Model predicts High Likelihood.  │
│ • Patient actually has ≥50% CAD.  │ • Patient has <50% CAD (Normal).   │
│ • Real-World Impact: Unaddressed  │ • Real-World Impact: Anxiety, cost │
│   ischemia, myocardial infarction,│   of secondary non-invasive tests, │
│   preventable sudden cardiac death│   unnecessary diagnostic cath.     │
│ • CLINICAL COST: C(FN) >>> C(FP)  │ • CLINICAL COST: Moderate          │
└───────────────────────────────────┴────────────────────────────────────┘
```

---

## 2. Comprehensive Metric Framework

HeartXAI 2.0 evaluates candidate models across a multi-dimensional matrix:

| Metric Category | Specific Metrics | Mathematical Formula | Clinical Meaning & Primary Role |
| :--- | :--- | :--- | :--- |
| **Discriminative Ability** | **ROC-AUC** | $\int_0^1 \text{TPR}(\text{FPR}^{-1}(t)) \, dt$ | Probability that a randomly selected diseased patient receives a higher score than a non-diseased patient. |
| | **PR-AUC** | $\int_0^1 \text{Precision}(\text{Recall}) \, dr$ | Evaluates positive class trade-offs independent of true negatives. |
| **Classification Quality** | **Sensitivity (Recall)**| $\frac{\text{TP}}{\text{TP} + \text{FN}}$ | Proportion of patients with $\ge 50\%$ CAD correctly identified. **Primary clinical safety metric**. |
| | **Specificity** | $\frac{\text{TN}}{\text{TN} + \text{FP}}$ | Proportion of patients without significant CAD correctly ruled out. |
| | **Balanced Accuracy** | $\frac{\text{Sensitivity} + \text{Specificity}}{2}$ | Arithmetic mean of sensitivity and specificity; robust to demographic class skews. |
| | **Precision (PPV)** | $\frac{\text{TP}}{\text{TP} + \text{FP}}$ | Probability that a patient flagged as high likelihood genuinely has $\ge 50\%$ CAD. |
| | **F1-Score** | $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$ | Harmonic mean balancing false positives and false negatives. |
| **Probabilistic Calibration**| **Brier Score** | $\frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$ | Mean squared error of probability predictions. Lower is better ($0.0 = \text{perfect}$, $0.25 = \text{uninformative coin flip}$). |
| | **Expected Calibration Error (ECE)** | $\sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$ | Absolute calibration gap between predicted confidence and empirical accuracy across $M$ probability bins. |

---

## 3. Decision Threshold Selection & Tuning

The standard software default threshold of $\tau = 0.50$ is arbitrary and rarely clinically optimal.

### 3.1 Clinical Cost-Weighted Threshold Optimization
In clinical screening, because $C(\text{FN}) > C(\text{FP})$, the decision threshold $\tau$ should balance sensitivity without flooding outpatient cardiology clinics with false positives:
$$\tau^* = \arg\min_\tau \left[ C(\text{FN}) \cdot \text{FN}(\tau) + C(\text{FP}) \cdot \text{FP}(\tau) \right]$$
- **Baseline Threshold:** $\tau = 0.50$ is retained for baseline reporting.
- **High-Sensitivity Triage Threshold:** $\tau = 0.35$ can be evaluated for flagging individuals who require non-urgent primary care clinical review.
- **Strict Rule:** Any adjusted decision threshold must be tuned **strictly inside the inner cross-validation folds** and validated on the untouched holdout test set.

---

## 4. Confidence Intervals: Wilson Score & Bootstrapping

Given the sample size ($N = 303$), all reported scalar metrics **must** include $95\%$ confidence intervals:

### 4.1 Non-Parametric Bootstrap Intervals for ROC-AUC & Brier Score
For continuous metrics:
1. Resample the evaluation set with replacement $B = 1,000$ times.
2. Compute the metric $\theta^*_b$ on each bootstrap replicate.
3. Determine empirical $95\%$ percentile intervals: $[\theta^*_{2.5\%}, \theta^*_{97.5\%}]$.

### 4.2 Wilson Score Intervals for Proportions (Sensitivity & Specificity)
For binary proportions $\hat{p} = k / n$:
$$\text{CI}_{95\%} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1 - \hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
where $z = 1.96$.

---

## 5. Model Promotion Acceptance Gates (Go / No-Go Criteria)

Prior to promoting any trained model artifact to production staging, it must satisfy **Five Hard Gates**:

- [ ] **Gate 1 (Baseline Superiority):** Candidate model cross-validated mean ROC-AUC must exceed regularized Logistic Regression by $\ge +0.02$ ($\text{ROC-AUC} \ge 0.85$ target threshold).
- [ ] **Gate 2 (Clinical Safety Sensitivity):** Cross-validated mean Sensitivity must exceed $82.0\%$ at the operational threshold.
- [ ] **Gate 3 (Calibration Reliability):** Calibrated Brier Score must not exceed $0.140$ ($0.00$ to $0.140$ target).
- [ ] **Gate 4 (Demographic Parity):** Sensitivity difference between male and female subgroups must satisfy:
  $$|\text{Sensitivity}_{\text{male}} - \text{Sensitivity}_{\text{female}}| \le 0.10$$
- [ ] **Gate 5 (Explainability Soundness):** 100% of test instances must pass the TreeSHAP local accuracy property check ($|\sum \phi_i - (f(x) - E[f(x)])| < 10^{-4}$).

*Note: In accordance with our execution rules, these targets represent gating criteria for future experimental evaluation; no model is claimed to have achieved them until actual training is executed.*
