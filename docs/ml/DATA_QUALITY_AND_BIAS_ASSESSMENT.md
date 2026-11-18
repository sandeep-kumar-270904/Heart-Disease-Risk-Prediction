# HeartXAI 2.0 — Data Quality, Missingness & Epidemiological Bias Assessment

**Document ID:** `HX2-ML-005`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Research Specification  
**Author:** Principal ML Research Scientist & Healthcare Bias Auditor  
**Traceability:** FR-020–FR-029, NFR-001–NFR-028, ADR-001, ADR-003, ADR-011  

---

## 1. Data Quality & Missingness Audit

A comprehensive quality audit of the **UCI Cleveland Heart Disease Cohort ($N = 303$)** reveals that the dataset exhibits exceptionally high structural integrity compared to other clinical cohorts, but possesses distinct epidemiological characteristics that require rigorous accounting.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DATA QUALITY SUMMARY AT A GLANCE                     │
├────────────────────────────────────────────────────────────────────────┤
│ • Total Patient Records: 303                                           │
│ • Fully Complete Rows: 297 (98.02%)                                    │
│ • Rows with Missing Values: Exactly 6 rows (1.98%)                     │
│ • Duplicate Rows: 0 exact duplicates                                   │
│ • Outliers: Serum Cholesterol = 564 mg/dL (Clinically valid)           │
│ • Class Balance: 164 Negative (54.1%) vs 139 Positive (45.9%)          │
│ • Demographic Skew: 68.0% Male vs 32.0% Female                         │
│ • Temporal Provenance: 1981–1984 (Cleveland Clinic Foundation, USA)    │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Missing Value Topology & Location
The dataset contains exactly **6 missing values** across 2 specific features, encoded as `'?'` in raw files:
1. `ca` (Major vessels colored by fluoroscopy): Missing in **4 records**:
   - Row 166 (Age 52, Male, cp=3, trestbps=138, chol=223)
   - Row 192 (Age 58, Female, cp=2, trestbps=120, chol=340)
   - Row 287 (Age 58, Female, cp=4, trestbps=170, chol=225)
   - Row 302 (Age 38, Male, cp=3, trestbps=138, chol=175)
2. `thal` (Thallium scintigraphy defect): Missing in **2 records**:
   - Row 87 (Age 53, Female, cp=3, trestbps=128, chol=216)
   - Row 266 (Age 52, Male, cp=4, trestbps=128, chol=204)

#### Imputation Policy
Because missingness affects $< 2\%$ of the cohort and is concentrated in advanced imaging procedures, **Cohort Median Imputation** (`ca = 0.0`, `thal = 3.0`) is statistically sound and preserves sample size without distorting variance. In the live production pipeline, imputation parameters must be calculated exclusively on the training split.

### 1.2 Outlier & Extreme Value Clinical Audit
- **Serum Cholesterol Outlier (`Row 153`):** Total cholesterol recorded as $564\text{ mg/dL}$ ($14.58\text{ mmol/L}$) in a 67-year-old female. While mathematically $> 6\text{ SD}$ above the mean, this is clinically plausible in patients with severe familial hypercholesterolemia. It is retained to teach the tree ensemble real-world clinical extremes.
- **Oldpeak ST Depression (`Row 91`):** Recorded as $6.2\text{ mm}$ ($0.62\text{ mV}$) in a 58-year-old male. This indicates profound exercise-induced myocardial ischemia and is clinically legitimate.
- **Zero Blood Pressure / Zero Heart Rate:** Audited. Exactly 0 rows contain zero or negative vital values.

---

## 2. Demographic & Epidemiological Representation Biases

### 2.1 Sex Representation Bias
- **The Imbalance:** The cohort contains **$206$ men ($68.0\%$)** and **$97$ women ($32.0\%$)**.
- **Clinical Consequence:** Coronary artery disease manifests differently in women (higher frequency of microvascular dysfunction, atypical anginal presentations, and lower peak ST depression).
- **Model Risk:** An uncalibrated model risks exhibiting lower sensitivity or higher false-negative rates in female patients due to male-dominant training weight. Subgroup performance evaluation must be explicitly tracked.

### 2.2 Age Distribution Bias
- **Range:** $29$ to $77$ years (Mean: $54.4$, Median: $56.0$, $\text{SD} = 9.0$).
- **Under-Represented Demographics:**
  - Young adults ($< 35$ years): Only $3$ patients ($0.99\%$).
  - Geriatric population ($> 75$ years): Only $1$ patient ($0.33\%$).
- **Clinical Guardrail:** The model **cannot** reliably predict CAD likelihood in individuals younger than 30 or older than 75. A physiological warning is rendered if inputs fall outside the $[30, 75]$ window.

### 2.3 Ethnic & Geographic Bias
- **Data Absence:** Race and ethnicity were not documented in the 1989 Detrano et al. publication.
- **Geographic Reality:** Collected from inpatient referrals at the Cleveland Clinic Foundation in Northeast Ohio between 1981 and 1984.
- **Generalizability Limit:** The baseline incidence of CAD, dietary lipid profiles, and genetic polymorphisms in 1980s Northeast Ohio differ markedly from populations in contemporary South Asia (India), East Asia, or Africa.

---

## 3. Systematic Clinical Selection & Referral Biases

### 3.1 Catheterization Referral Bias (Berkson's Bias)
Every individual in the Cleveland dataset was symptomatic or had abnormal non-invasive screening that justified invasive cardiac catheterization. 
- **The Consequence:** The cohort has a baseline disease prevalence of **$45.87\%$** ($\ge 50\%$ stenosis). In the general outpatient screening population, true CAD prevalence is typically between $5\%\text{ and }15\%$.
- **Model Output Effect:** A raw, uncalibrated classifier trained on Cleveland will systematically **overestimate** the risk of disease if applied directly to an unselected, asymptomatic screening population.

### 3.2 Historical Temporal Shift (1984 vs 2026)
- The dataset was collected prior to the widespread clinical adoption of high-intensity statin therapy (HMG-CoA reductase inhibitors), modern antiplatelet regimens (P2Y12 inhibitors), and contemporary troponin assays.
- Diagnostic thresholds for cardiac catheterization in 1984 were significantly higher than modern outpatient protocols.

---

## 4. Target Leakage & Feature Independence Verification

1. **Target Isolation:** The target attribute `num` (and its binarized representation) was verified to be strictly absent from the input feature matrix.
2. **Imaging Feature Timing:** `ca` (fluoroscopy) and `thal` (scintigraphy) are diagnostic imaging tests often performed concurrently with catheterization. When evaluated in an initial outpatient triage setting where imaging has not yet occurred, these two features must be treated as optional and median-imputed, ensuring the model does not fail in screening scenarios.
