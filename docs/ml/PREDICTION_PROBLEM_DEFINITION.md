# HeartXAI 2.0 — Prediction Problem Definition: Classification vs Prospective Risk

**Document ID:** `HX2-ML-002`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal ML Research Scientist & Clinical Epidemiologist  
**Traceability:** FR-020–FR-029, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-REQ-006  

---

## 1. Fundamental Conceptual Disambiguation

A catastrophic error in commercial and academic healthcare AI projects is conflating **cross-sectional disease classification** with **prospective longitudinal risk calculation**.

In HeartXAI 2.0, these two problems are decoupled mathematically, clinically, and linguistically:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   TASK A: HEART DISEASE CLASSIFICATION                 │
├────────────────────────────────────────────────────────────────────────┤
│ • Nature: Cross-sectional anatomical disease detection.                │
│ • Question: "Does this patient currently exhibit significant coronary  │
│   artery narrowing on invasive coronary catheterization?"              │
│ • Ground Truth: Invasive coronary angiography (≥ 50% diameter stenosis)│
│ • Supported by Available Data: YES (Supported by UCI Cleveland cohort).│
│ • User-Facing Phrasing: "Angiographic CAD Association Likelihood".     │
└────────────────────────────────────────────────────────────────────────┘

                                   VS

┌────────────────────────────────────────────────────────────────────────┐
│               TASK B: PROSPECTIVE CARDIOVASCULAR RISK ESTIMATION       │
├────────────────────────────────────────────────────────────────────────┤
│ • Nature: Longitudinal epidemiological survival modeling.              │
│ • Question: "What is the statistical probability that an asymptomatic  │
│   individual will suffer a myocardial infarction or stroke over 10 yrs?│
│ • Ground Truth: Verified time-to-event follow-up over 10 to 30 years.  │
│ • Supported by Available Data: NO (Cleveland dataset has zero follow-up│
│   data, no survival times, and is a symptomatic referral cohort).      │
│ • User-Facing Phrasing: "10-Year Cardiovascular Event Population Risk".│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Deep Dive: Task A — Cross-Sectional Angiographic CAD Classification

### 2.1 The Exact Clinical Target Label
- **Underlying Clinical Ground Truth:** Invasive Coronary Angiography (Cardiac Catheterization).
- **Gold Standard Criterion:** Significant coronary artery disease is anatomically defined as **$\ge 50\%$ diameter stenosis** in at least one of the major epicardial coronary arteries:
  1. Left Anterior Descending (LAD)
  2. Left Circumflex (LCx)
  3. Right Coronary Artery (RCA)
- **Raw Variable in Cleveland Dataset:** `num`
  - `num = 0`: Absence of significant coronary stenosis ($< 50\%$ diameter narrowing).
  - `num = 1`: Single-vessel significant stenosis ($\ge 50\%$).
  - `num = 2`: Two-vessel significant stenosis.
  - `num = 3`: Three-vessel significant stenosis.
  - `num = 4`: Left main / multi-vessel severe stenosis.
- **Binarized Machine Learning Target:**
  $$y = \begin{cases} 0 & \text{if } num = 0 \text{ (Angiographically Negative CAD, } < 50\% \text{ stenosis)} \\ 1 & \text{if } num \in \{1, 2, 3, 4\} \text{ (Angiographically Positive CAD, } \ge 50\% \text{ stenosis)} \end{cases}$$

### 2.2 Mathematical Objective
Train a supervised classification model $f: \mathcal{X} \rightarrow [0, 1]$ to estimate the posterior conditional probability:
$$P(y = 1 \mid \mathbf{x})$$
where $\mathbf{x} \in \mathbb{R}^{13}$ represents the standardized vector of clinical demographics, vitals, laboratory tests, and electrocardiographic findings.

### 2.3 Epistemological Limitations of Task A
1. **Selection & Referral Bias:** The Cleveland cohort consists entirely of patients suspected of heart disease who were referred for diagnostic catheterization in an inpatient tertiary hospital. It **does not represent the general asymptomatic population**.
2. **Anatomical vs Functional:** A $\ge 50\%$ anatomical stenosis does not necessarily imply functional ischemia (hemodynamic compromise measured by Fractional Flow Reserve [FFR]).
3. **Non-Prospective:** A high likelihood score on Task A means the patient's measurements resemble patients who had anatomical plaque in 1984; it **does not forecast a heart attack next week, next month, or in 10 years**.

---

## 3. Deep Dive: Task B — Prospective 10-Year ASCVD Risk Estimation

### 3.1 Definition & Requirements
Prospective risk calculation estimates the probability of experiencing a hard atherosclerotic cardiovascular disease (ASCVD) event (nonfatal myocardial infarction, coronary heart disease death, or fatal/nonfatal stroke) over a defined 10-year horizon.

- **Data Requirements:**
  - True prospective, longitudinal study design.
  - Large population-based cohort (thousands of individuals, e.g., Framingham Heart Study $N > 5,000$, Pooled Cohort Equations $N > 25,000$).
  - Documented follow-up time (person-years) with adjudication of primary clinical endpoints.
  - Censoring methodologies (Cox Proportional Hazards or Fine-Gray sub-distribution models).

### 3.2 Inability of UCI Cleveland Dataset to Support Task B
The UCI Cleveland Heart Disease dataset **cannot** support Task B:
- It contains **zero longitudinal follow-up data**.
- It records only a single cross-sectional snapshot at the time of cardiac catheterization.
- Training an ML algorithm on Cleveland to output "10-year heart attack risk" is scientifically fraudulent.

---

## 4. Architectural Separation in HeartXAI 2.0

HeartXAI 2.0 implements **Two Completely Decoupled Pipelines**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ PIPELINE 1: ML CAD ASSOCIATION CLASSIFIER (Cleveland XGBoost + SHAP)   │
│ - Output: Angiographic CAD Association Likelihood (0% – 100%)          │
│ - Training Base: UCI Cleveland Cohort (Cross-sectional, N=303)         │
│ - Explainability: TreeSHAP Feature Attributions + Counterfactuals      │
│ - Purpose: Educational pattern analysis of submitted clinical vitals   │
├────────────────────────────────────────────────────────────────────────┤
│ PIPELINE 2: EPIDEMIOLOGICAL 10-YEAR ASCVD BENCHMARK (ACC/AHA Equations) │
│ - Output: 10-Year Population Benchmark Risk (0% – 100%)                │
│ - Mathematical Model: 2013 ACC/AHA Pooled Cohort Equations             │
│ - Variables Used: Age, Sex, Total Cholesterol, HDL, Systolic BP, Meds  │
│ - Purpose: Population-level epidemiological reference context          │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Strict Integration Rules
1. **Never Combined:** The probabilities from Pipeline 1 and Pipeline 2 are **never averaged, merged, or summed**.
2. **Independent Visualization:** Displayed side-by-side in `<DualRiskGaugeCard />` with distinct visual containers and explicit explanatory labels.
3. **Explicit Disclaimer:** The interface explicitly informs the user: *"Pipeline 1 reflects how closely your clinical markers resemble historical study patients with coronary artery narrowing. Pipeline 2 reflects standard population-based 10-year epidemiological risk equations."*
