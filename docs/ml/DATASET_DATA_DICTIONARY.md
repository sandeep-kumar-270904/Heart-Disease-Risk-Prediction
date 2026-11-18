# HeartXAI 2.0 — Dataset Data Dictionary (UCI Cleveland Cohort)

**Document ID:** `HX2-ML-004`  
**Version:** `1.0.0`  
**Phase:** Phase 8 — Machine Learning Research, Dataset Verification & Model Development Plan  
**Status:** Approved Research Specification  
**Author:** Clinical Data Architect & Lead ML Engineer  
**Traceability:** FR-020–FR-029, NFR-001–NFR-028, ADR-001, ADR-003, HXAI-REQ-006  

---

## 1. Overview & Data Architecture

This document defines the complete clinical data dictionary for the **UCI Cleveland Heart Disease Dataset ($N = 303$)** utilized by HeartXAI 2.0. 

In accordance with our strict data engineering standards:
- Every feature is defined by its clinical measurement methodology, canonical units, allowed mathematical domains, and missingness topology.
- Feature availability at runtime is explicitly assessed to prevent data leakage.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   FEATURE CATEGORY DISTRIBUTION                        │
├────────────────────────────────────────────────────────────────────────┤
│ • Demographic & Baseline: age, sex (2 features)                        │
│ • Symptom & Physical Examination: cp, trestbps, thalach, exang (4 feat)│
│ • Metabolic Blood Biomarkers: chol, fbs (2 features)                   │
│ • Electrocardiography (ECG): restecg, oldpeak, slope (3 features)      │
│ • Advanced Cardiac Imaging: ca, thal (2 features, optional at triage)  │
│ • Clinical Outcome Target: num -> binarized target (1 target)          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Clinical Feature Specifications

### 1. `age` — Chronological Age
- **Original Dataset Name:** `age`
- **Clinical Meaning:** Patient age at the time of cardiac catheterization.
- **Data Type:** Continuous Numeric (`float` / `int`).
- **Units:** Years.
- **Allowed Range:** $[18.0, 100.0]$ (Cleveland cohort range: $29.0\text{ – }77.0$, Mean: $54.4$, SD: $9.0$).
- **Missing Representation:** None (100% complete).
- **Leakage Concern:** None. Available at initial patient intake.

### 2. `sex` — Biological Sex
- **Original Dataset Name:** `sex`
- **Clinical Meaning:** Biological sex assigned at birth.
- **Data Type:** Binary Categorical (`int`).
- **Allowed Values:**
  - `0`: Female ($n = 97$, $32.0\%$).
  - `1`: Male ($n = 206$, $68.0\%$).
- **Missing Representation:** None (100% complete).
- **Leakage Concern:** None.

### 3. `cp` — Chest Pain Type
- **Original Dataset Name:** `cp`
- **Clinical Meaning:** Subjective chest discomfort reported during symptom history.
- **Data Type:** Nominal Categorical (`int`).
- **Allowed Values (Original UCI Cleveland Coding):**
  - `1`: Typical Angina (Substernal chest pressure provoked by exertion/stress, relieved by rest or nitroglycerin; $n = 23$, $7.6\%$).
  - `2`: Atypical Angina (Discomfort meeting 2 of the 3 classic angina criteria; $n = 50$, $16.5\%$).
  - `3`: Non-Anginal Pain (Meeting 1 or none of classic criteria, often sharp/pleuritic; $n = 86$, $28.4\%$).
  - `4`: Asymptomatic (Absence of subjective chest pain; $n = 144$, $47.5\%$).
- *Note:* In standardized 0-indexed preprocessing: $\{1 \rightarrow 0, 2 \rightarrow 1, 3 \rightarrow 2, 4 \rightarrow 3\}$.
- **Missing Representation:** None (100% complete).

### 4. `trestbps` — Resting Blood Pressure
- **Original Dataset Name:** `trestbps`
- **Clinical Meaning:** Resting systolic arterial blood pressure measured in the clinical exam room prior to exercise stress.
- **Data Type:** Continuous Numeric (`float`).
- **Units:** Millimeters of mercury ($\text{mmHg}$).
- **Allowed Range:** $[70.0, 240.0]\text{ mmHg}$ (Cleveland cohort range: $94\text{ – }200$, Mean: $131.7$, SD: $17.8$).
- **Missing Representation:** None (100% complete).

### 5. `chol` — Serum Cholesterol
- **Original Dataset Name:** `chol`
- **Clinical Meaning:** Total fasting serum cholesterol concentration.
- **Data Type:** Continuous Numeric (`float`).
- **Units:** Milligrams per deciliter ($\text{mg/dL}$); converts to $\text{mmol/L}$ via factor $38.67$.
- **Allowed Range:** $[100.0, 600.0]\text{ mg/dL}$ (Cleveland cohort range: $126\text{ – }564$, Mean: $246.7$, SD: $51.8$).
- *Note on Row 153:* One outlier patient has cholesterol of $564\text{ mg/dL}$ (clinically consistent with severe familial hypercholesterolemia).
- **Missing Representation:** None (100% complete).

### 6. `fbs` — Fasting Blood Sugar
- **Original Dataset Name:** `fbs`
- **Clinical Meaning:** Binary indicator of elevated fasting blood glucose ($> 120\text{ mg/dL}$ / $> 6.66\text{ mmol/L}$), signaling impaired glucose tolerance or diabetes mellitus.
- **Data Type:** Binary Categorical (`int`).
- **Allowed Values:**
  - `0`: $\le 120\text{ mg/dL}$ ($n = 258$, $85.1\%$).
  - `1`: $> 120\text{ mg/dL}$ ($n = 45$, $14.9\%$).
- **Missing Representation:** None (100% complete).

### 7. `restecg` — Resting Electrocardiographic Results
- **Original Dataset Name:** `restecg`
- **Clinical Meaning:** Resting 12-lead baseline electrocardiogram findings.
- **Data Type:** Nominal Categorical (`int`).
- **Allowed Values:**
  - `0`: Normal ($n = 151$, $49.8\%$).
  - `1`: ST-T Wave Abnormality (T-wave inversions and/or ST elevation or depression of $> 0.05\text{ mV}$; $n = 4$, $1.3\%$).
  - `2`: Probable or Definite Left Ventricular Hypertrophy (by Estes' criteria; $n = 148$, $48.8\%$).
- **Missing Representation:** None (100% complete).

### 8. `thalach` — Maximum Heart Rate Achieved
- **Original Dataset Name:** `thalach`
- **Clinical Meaning:** Peak heart rate achieved during maximal treadmill Bruce protocol exercise testing.
- **Data Type:** Continuous Numeric (`float`).
- **Units:** Beats per minute ($\text{bpm}$).
- **Allowed Range:** $[60.0, 220.0]\text{ bpm}$ (Cleveland cohort range: $71\text{ – }202$, Mean: $149.6$, SD: $22.9$).
- **Missing Representation:** None (100% complete).

### 9. `exang` — Exercise-Induced Angina
- **Original Dataset Name:** `exang`
- **Clinical Meaning:** Precipitation of characteristic anginal symptoms during exercise stress testing.
- **Data Type:** Binary Categorical (`int`).
- **Allowed Values:**
  - `0`: No ($n = 204$, $67.3\%$).
  - `1`: Yes ($n = 99$, $32.7\%$).
- **Missing Representation:** None (100% complete).

### 10. `oldpeak` — ST Depression (Oldpeak)
- **Original Dataset Name:** `oldpeak`
- **Clinical Meaning:** Magnitude of horizontal or downsloping ST-segment depression induced by exercise stress relative to resting baseline ECG.
- **Data Type:** Continuous Numeric (`float`).
- **Units:** Millimeters ($\text{mm}$, where $1.0\text{ mm} = 0.1\text{ mV}$).
- **Allowed Range:** $[0.0, 6.2]\text{ mm}$ (Cleveland cohort range: $0.0\text{ – }6.2$, Mean: $1.04$, SD: $1.16$).
- **Missing Representation:** None (100% complete).

### 11. `slope` — Slope of Peak Exercise ST Segment
- **Original Dataset Name:** `slope`
- **Clinical Meaning:** Geometric vector of the ST segment at peak exercise stress.
- **Data Type:** Ordinal Categorical (`int`).
- **Allowed Values (Original UCI Cleveland Coding):**
  - `1`: Upsloping ($n = 142$, $46.9\%$).
  - `2`: Flat ($n = 140$, $46.2\%$).
  - `3`: Downsloping ($n = 21$, $6.9\%$).
- *Standard Preprocessing:* Shifted to $\{0: \text{Upsloping}, 1: \text{Flat}, 2: \text{Downsloping}\}$.
- **Missing Representation:** None (100% complete).

### 12. `ca` — Major Vessels Colored by Fluoroscopy
- **Original Dataset Name:** `ca`
- **Clinical Meaning:** Number of major epicardial coronary vessels ($0\text{–}3$) exhibiting significant calcification under coronary fluoroscopy.
- **Data Type:** Ordinal / Discrete Numeric (`float`).
- **Allowed Values:** `0.0` ($n = 176$), `1.0` ($n = 65$), `2.0` ($n = 38$), `3.0` ($n = 20$).
- **Missing Representation:** `?` in raw file ($n = 4$ rows: rows 166, 192, 287, 302).
- **Imputation Strategy:** Cohort median ($0.0$).
- **Availability & Actionability:** Available only if fluoroscopy is performed. **Strictly immutable** ($\delta = 0$) in counterfactual modeling.

### 13. `thal` — Thallium Scintigraphy Defect
- **Original Dataset Name:** `thal`
- **Clinical Meaning:** Myocardial perfusion status evaluated by thallium-201 nuclear scintigraphy stress imaging.
- **Data Type:** Nominal Categorical (`float`).
- **Allowed Values (Original UCI Cleveland Coding):**
  - `3.0`: Normal myocardial perfusion ($n = 166$, $54.8\%$).
  - `6.0`: Fixed defect (non-reversible scar indicating prior myocardial infarction; $n = 18$, $5.9\%$).
  - `7.0`: Reversible defect (stress-induced myocardial ischemia; $n = 117$, $38.6\%$).
- **Missing Representation:** `?` in raw file ($n = 2$ rows: rows 87, 266).
- **Imputation Strategy:** Cohort mode/median ($3.0 = \text{Normal}$).
- **Availability & Actionability:** Diagnostic imaging marker. **Strictly immutable** ($\delta = 0$) in counterfactual modeling.

### 14. `num` / `target` — Angiographic CAD Diagnosis (Target Variable)
- **Original Dataset Name:** `num`
- **Clinical Meaning:** Quantitative count of major epicardial vessels with $\ge 50\%$ diameter stenosis on coronary catheterization.
- **Data Type:** Discrete Integer (`int`).
- **Allowed Values in Raw Data:** `0` ($n=164$), `1` ($n=55$), `2` ($n=36$), `3` ($n=35$), `4` ($n=13$).
- **Binarized Operational Target:**
  - `target = 0`: Negative CAD ($< 50\%$ stenosis, $n = 164$, $54.13\%$).
  - `target = 1`: Positive CAD ($\ge 50\%$ stenosis, $n = 139$, $45.87\%$).
- **Leakage Analysis:** Target variable is strictly isolated during training; excluded from input feature tensors.
