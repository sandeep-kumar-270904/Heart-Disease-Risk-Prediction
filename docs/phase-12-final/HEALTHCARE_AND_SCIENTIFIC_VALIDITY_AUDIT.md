# HeartXAI 2.0 — Healthcare & Scientific Validity Audit
**Document ID:** HX-PR-004  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Healthcare AI Research Reviewer & Clinical Safety Consultant  
**Status:** Scientifically Reconciled — Task B Removed from MVP Scope  
**Date:** November 2026  

---

## 1. Executive Summary

Healthcare applications integrating machine learning require uncompromising epistemological clarity. Conflating retrospective statistical classification on a small, symptomatic referral cohort with prospective clinical risk prediction or diagnostic decision-making creates severe patient safety hazards and regulatory liability.

This audit establishes the definitive scientific boundaries for HeartXAI 2.0, provides a verified analysis of the UCI Cleveland dataset, evaluates the predictive targets, presents an evidence-based reassessment of prospective cardiovascular risk equations (ACC/AHA PCE vs. AHA PREVENT), defines clinical governance boundaries, and enforces an unambiguous ledger of prohibited clinical claims.

---

## 2. Epistemological Ground Truth: Task A (MVP) vs. Task B (Future Research)

The previous Phase 12 draft discussed both heart disease classification and prospective risk estimation. The Phase 12.1 audit establishes a strict, non-negotiable structural separation:

```
+---------------------------------------------------------------------------------------------------------+
|                                    PREDICTION SCOPE STRUCTURAL SEPARATION                               |
+-------------------------+-------------------------------------------+-----------------------------------+
| Parameter               | Task A: Heart Disease Classification      | Task B: Prospective 10-Yr ASCVD   |
|                         | (Approved Experimental MVP ML Subsystem)  | (REMOVED FROM MVP SCOPE)          |
+-------------------------+-------------------------------------------+-----------------------------------+
| Clinical Question       | "Does the patient's biomarker vector      | "What is the 10-year probability |
|                         | classify into the coronary stenosis group | of an incident hard ASCVD event   |
|                         | within the experimental dataset cohort?"  | (MI or stroke) in primary care?"  |
+-------------------------+-------------------------------------------+-----------------------------------+
| Implementation Status   | **RETAINED FOR MVP (EXPERIMENTAL ONLY)**  | **DEFERRED TO FUTURE ROADMAP**    |
+-------------------------+-------------------------------------------+-----------------------------------+
| Theoretical Foundation  | Supervised learning on retrospective      | Multivariable survival analysis   |
|                         | cross-sectional catheterization cohort.   | on longitudinal cohorts.          |
+-------------------------+-------------------------------------------+-----------------------------------+
| Ground Truth Evidence   | Historical fluoroscopy / catheterization  | Longitudinal adjudicated clinical |
|                         | records (1981–1984).                      | events over 10 to 30 years.       |
+-------------------------+-------------------------------------------+-----------------------------------+
| User-Facing Statement   | "Experimental classification of dataset   | Prohibited in MVP release.        |
|                         | target pattern; non-diagnostic."          | No calculator permitted.          |
+-------------------------+-------------------------------------------+-----------------------------------+
```

---

## 3. Dataset Verification: The UCI Cleveland Catheterization Cohort

### 3.1 Primary Literature and Provenance
- **Primary Citation:** Detrano R, Janosi A, Steinbrunn W, Pfisterer M, Schmid JJ, Sandhu S, Guppy KH, Lee S, Froelicher V. *International application of a new probability algorithm for the diagnosis of coronary artery disease.* American Journal of Cardiology. 1989;64(5):304–310. doi:10.1016/0002-9149(89)90524-9.
- **Data Collection Period:** 1981 through 1984.
- **Principal Investigator / Institution:** Dr. Robert Detrano, MD, PhD, at the Cleveland Clinic Foundation (Cleveland, Ohio, USA).
- **Dataset Extraction:** The raw repository contains 76 raw attributes; the standard clinical subset distributed by UCI Machine Learning Repository consists of **14 attributes** across **303 patient records**.

### 3.2 Target Semantics and Transformation
- **Original Target Attribute (`num`):** Represents the angiographically determined presence and extent of coronary artery disease:
  - `num = 0`: $<50\%$ diameter narrowing in all major coronary vessels (angiographically normal or non-obstructive atherosclerotic wall irregularity).
  - `num = 1`: Significant stenosis ($\ge 50\%$ diameter narrowing) in 1 major coronary vessel.
  - `num = 2`: Significant stenosis in 2 major coronary vessels.
  - `num = 3`: Significant stenosis in 3 major coronary vessels.
  - `num = 4`: Significant stenosis in 4 major vessels (including left main / trifurcations).
- **Approved Binary Transformation for Task A:**
  $$y = \begin{cases} 0 & \text{if } num = 0 \text{ (absence of significant stenosis, } <50\%) \\ 1 & \text{if } num \ge 1 \text{ (presence of significant stenosis, } \ge 50\%) \end{cases}$$
  Distribution in Cleveland: 164 negative ($54.1\%$) and 139 positive ($45.9\%$).

### 3.3 Critical Population & Methodology Limitations
1. **Referral Cohort (Severe Selection Bias):** The cohort consists exclusively of symptomatic patients or patients with abnormal non-invasive findings (e.g., severe treadmill stress tests) who were referred for invasive coronary catheterization. The background disease prevalence is $\approx 46\%$, vastly higher than the $2\text{--}6\%$ prevalence in asymptomatic general adult populations.
2. **Small Sample Size ($N=303$):** With only 303 total instances (and 6 records containing missing values in `ca` or `thal`, leaving $N=297$ complete cases), the sample is underpowered for generalizable sub-population modeling.
3. **Demographic Imbalance:** 206 male ($68\%$) and 97 female ($32\%$). The cohort was drawn from a regional US urban clinical population in the early 1980s; it lacks racial, ethnic, and global diversity.
4. **Historical Diagnostic Technology:** Catheterization procedures and laboratory assays reflect 1980s clinical standards. Modern high-sensitivity troponin assays, coronary CT angiography (CCTA), and current lipid fractionation were not available.
5. **Absence of Longitudinal Follow-up:** **The dataset contains zero follow-up data.** It records solely whether a patient had $\ge 50\%$ vessel narrowing on the day of angiography. **It cannot calculate the probability of a future heart attack, stroke, or cardiovascular event.**

### 3.4 Regulatory & Clinical Classification
The model trained on this dataset must be classified strictly as an **Experimental Machine Learning Dataset Classifier**. Its outputs must never be presented as:
- A medical diagnosis.
- A validated future cardiovascular event prediction.
- A clinically validated risk score.
- A replacement for a licensed physician's evaluation.

---

## 4. Reassessment of Prospective Risk: PCE vs. PREVENT (Task B Research)

The Phase 12 dossier proposed implementing the ACC/AHA 2013 Pooled Cohort Equations (PCE) in Milestone 14. This proposal has been **reassessed and rejected for the MVP**. Task B is deferred to the future research roadmap.

To guide future Task B research, the two primary prospective methodologies were evaluated against official clinical sources:

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            ACC/AHA PCE vs. AHA PREVENT METHODOLOGICAL COMPARISON                              |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| Dimension           | ACC/AHA Pooled Cohort Equations (PCE)             | AHA PREVENT Equations                               |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Primary Source**  | Goff DC Jr, et al. *2013 ACC/AHA Risk Guideline.* | Khan SS, et al. *Development & Validation of PREVENT|
|                     | Circulation. 2014;129(suppl 2):S49–S73.           | Equations.* Circulation. 2024;149:430–449.          |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Derivation Base** | 4 historical US cohorts (ARIC, CHS, CARDIA, FHS). | 25+ contemporary datasets (EHR, Optum, health sys); |
|                     | Total $N \approx 24,000$ participants.            | Total $N > 6.6\text{ million}$ diverse US adults.   |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Target Population**| Primary prevention adults aged **40 to 79 years** | Primary prevention adults aged **30 to 79 years**   |
|                     | without preexisting clinical ASCVD.               | without established ASCVD or heart failure.         |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Outcomes & Horizon**| 10-year risk of first "hard" ASCVD (nonfatal MI, | 10-year and 30-year risk of:                        |
|                     | coronary heart disease death, fatal/nonfatal CVA).| 1. Total CVD (ASCVD + Heart Failure)                |
|                     |                                                   | 2. ASCVD (CHD death, nonfatal MI, stroke)           |
|                     |                                                   | 3. Heart Failure (HF)                               |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Predictor Matrix**| Age, sex, race (White vs African American),       | Base: Age, sex, total chol, HDL, systolic BP,       |
|                     | total cholesterol, HDL-C, treated/untreated SBP,  | antihypertensive meds, statin use, diabetes,        |
|                     | diabetes (binary), current smoking (binary).      | smoking, eGFR (CKD-EPI 2021).                       |
|                     |                                                   | Enhanced (optional): uACR, HbA1c, SDI (deprivation).|
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Treatment of Race**| Includes explicit race coefficients (White/Black);| **Deliberately removes race coefficients** to avoid |
|                     | unvalidated for Asian, Hispanic, global cohorts.  | race-based medicine; substitutes eGFR and SDI.      |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Known Limitations**| Systematic risk overestimation (20% to 50%+) in   | Calibrated lower than PCE, potentially reclassifying|
|                     | contemporary cohorts; omits renal function;       | millions below statin thresholds before guidelines  |
|                     | dichotomizes diabetes without glycemic context.   | update clinical cutoffs; derived primarily from US. |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Clinical Guideline| Formally codified in 2018 AHA/ACC Cholesterol and | Released by AHA in late 2023 / early 2024; formal   |
| Status**            | 2019 Prevention Guidelines (current standards).   | multi-society clinical practice guideline updates   |
|                     |                                                   | incorporating PREVENT are currently in development. |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
```

### Recommendation for Future Task B Research:
1. **Exclude from MVP:** Neither PCE nor PREVENT shall be implemented in the initial release. Implementing unvalidated calculators creates clinical confusion.
2. **Future Research Prerequisites:** Before reconsidering Task B, the team must:
   - Define the specific target population and clinical setting (primary care vs. specialist).
   - Review the forthcoming official joint ACC/AHA guideline updates that will establish validated clinical decision thresholds for PREVENT.
   - Investigate jurisdiction-specific calculators (e.g., QRISK3 in the UK under NICE CG181/NG238; WHO cardiovascular risk charts for India/LMIC).
   - Obtain formal clinical advisory board review and establish institutional review board (IRB) determinations.

---

## 5. Clinical Governance Boundaries: Advisory vs. Ethics Review

To ensure legal, regulatory, and ethical integrity, HeartXAI 2.0 establishes a strict distinction between two separate governance mechanisms:

```
+---------------------------------------------------------------------------------------------------------+
|                                    CLINICAL GOVERNANCE BOUNDARIES                                       |
+------------------------------------+--------------------------------------------------------------------+
| Physician Advisory Review          | Institutional Ethics / IRB Determination                           |
+------------------------------------+--------------------------------------------------------------------+
| - Expert review of medical language| - Formal determination by an Institutional Review Board (IRB) or   |
|   and educational copy.            |   Research Ethics Committee (REC).                                 |
| - Review of symptom guidance and   | - Legally required if conducting human subjects research, clinical |
|   emergency red-flag rules.        |   interventions, or processing identifiable private health data.   |
| - Review of stated scientific and  | - Determines whether formal protocol review, informed consent, or |
|   clinical limitations.            |   an official waiver of oversight applies.                         |
| - Recommendations for future clinical| - Cannot be substituted by an informal advisory relationship.      |
|   research and evaluation.         | - Must be obtained prior to any real-world patient pilot.          |
+------------------------------------+--------------------------------------------------------------------+
```

### 5.1 Non-Diagnostic Product Positioning
HeartXAI 2.0 is positioned exclusively as an **informational, educational clinical decision support (CDS) exploration tool** under Section 520(o)(1)(E) of the US FDA 21st Century Cures Act. It does not provide medical diagnoses, treatment decisions, or automated prescriptions.

### 5.2 Mandatory Medical Disclaimer (Required on All Assessment Views)
> **MANDATORY CLINICAL NOTICE:** HeartXAI 2.0 is an experimental educational tool designed to demonstrate explainable machine learning concepts using retrospective research data. It **DOES NOT** provide medical diagnoses, clinical prognoses, or treatment recommendations. The assessment reflects statistical patterns observed in historical research datasets and cannot substitute for an evaluation by a licensed healthcare professional. If you are experiencing chest pain, tightness, shortness of breath, radiating arm or jaw pain, or acute discomfort, **IMMEDIATELY CALL EMERGENCY SERVICES (911 in the US, 999 in the UK, 112 in India)** or visit the nearest hospital emergency room.

---

## 6. Prohibited & Unsupported Clinical Claims Ledger

The following claims are strictly **PROHIBITED** across all user interfaces, API responses, PDF exports, and documentation:

1. ❌ *"HeartXAI diagnoses coronary artery disease, heart attacks, or cardiovascular conditions."*
2. ❌ *"The system calculates your exact 10-year risk of having a heart attack."*
3. ❌ *"HeartXAI replaces the need for a cardiologist, physician consultation, or angiogram."*
4. ❌ *"The model detects whether you are currently having a heart attack."*
5. ❌ *"You can adjust, start, or stop prescribed medications based on these results."*
6. ❌ *"HeartXAI is an FDA-approved or CE-marked diagnostic medical device."*
7. ❌ *"SHAP values prove the exact biological cause of your cardiovascular condition."*
8. ❌ *"Achieving the counterfactual values guarantees you will not develop heart disease."*
