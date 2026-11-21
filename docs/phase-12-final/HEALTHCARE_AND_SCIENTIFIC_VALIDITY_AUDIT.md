# HeartXAI 2.0 — Healthcare & Scientific Validity Audit
**Document ID:** HX-PR-004  
**Version:** 2.2.0 (Phase 12.2 Revision)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Healthcare AI Research Reviewer & Clinical Safety Reviewer  
**Status:** Scientifically Reconciled — 2026 ACC/AHA PREVENT Guidelines & Data Categories Formalized  
**Date:** November 2026  

---

## 1. Executive Summary

Healthcare software integrating machine learning requires strict scientific and epistemological validity. Conflating retrospective statistical classification on a small, symptomatic referral cohort with prospective clinical risk prediction or diagnostic decision-making creates severe clinical hazards and regulatory non-compliance.

This audit establishes the definitive scientific boundaries for HeartXAI 2.0, provides a verified analysis of the UCI Cleveland dataset, formally evaluates the **2026 ACC/AHA Multisociety Dyslipidemia Guideline** and the **AHA PREVENT equations**, codifies the **Three-Category Data Classification Policy**, establishes a **Four-Pillar Clinical Governance Framework** incorporating the **FDA January 2026 Clinical Decision Support (CDS) Software Guidance**, and enforces an unambiguous ledger of prohibited clinical claims.

---

## 2. Epistemological Ground Truth: Task A (MVP) vs. Task B (Future Research)

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

## 3. Dataset Verification: The UCI Cleveland Catheterization Cohort (Category A Data)

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

## 4. Reassessment: 2026 ACC/AHA Dyslipidemia Guideline & AHA PREVENT

### 4.1 The 2026 Clinical Practice Guideline Transition
In 2026, the American College of Cardiology (ACC), American Heart Association (AHA), and collaborating multisociety organizations published the **2026 Guideline on the Management of Dyslipidemia and Cardiovascular Risk**. This guideline formally evaluated and adopted the **AHA PREVENT equations** (Khan et al., *Circulation* 2024;149:430–449) as the recommended cardiovascular disease risk estimation tool for primary prevention clinical decision-making, officially superseding the 2013 Pooled Cohort Equations (PCE) for those applicable decisions.

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            ACC/AHA PCE vs. AHA PREVENT METHODOLOGICAL COMPARISON                              |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| Dimension           | ACC/AHA Pooled Cohort Equations (PCE)             | AHA PREVENT Equations                               |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Primary Sources** | Goff DC Jr, et al. *2013 ACC/AHA Risk Guideline.* | 1. Khan SS, et al. *Development & Validation of     |
|                     | Circulation. 2014;129(suppl 2):S49–S73.           |    PREVENT.* Circulation. 2024;149:430–449.         |
|                     |                                                   | 2. 2026 ACC/AHA Multisociety Dyslipidemia Guideline.|
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Derivation Base** | 4 historical US cohorts (ARIC, CHS, CARDIA, FHS). | 25+ contemporary datasets (EHR, Optum, health sys); |
|                     | Total $N \approx 24,000$ participants.            | Total $N > 6.6\text{ million}$ diverse US adults.   |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Target Population**| Primary prevention adults aged **40 to 79 years** | Primary prevention adults aged **30 to 79 years**   |
|                     | without preexisting clinical ASCVD.               | without established ASCVD or heart failure.         |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Outcomes & Horizon**| 10-year risk of first "hard" ASCVD (nonfatal MI, | 10-year and 30-year risk of:                        |
|                     | coronary heart disease death, fatal/nonfatal CVA).| 1. Total CVD (ASCVD + Heart Failure)                |
|                     |                                                   | 2. ASCVD alone (CHD death, nonfatal MI, stroke)     |
|                     |                                                   | 3. Heart Failure (HF) alone                         |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Predictor Matrix**| Age, sex, race (White vs African American),       | Base: Age, sex, total chol, HDL, systolic BP,       |
|                     | total cholesterol, HDL-C, treated/untreated SBP,  | antihypertensive meds, statin use, diabetes,        |
|                     | diabetes (binary), current smoking (binary).      | smoking, eGFR (CKD-EPI 2021).                       |
|                     |                                                   | Enhanced (optional): uACR, HbA1c, SDI (deprivation).|
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Treatment of Race**| Includes explicit race coefficients (White/Black);| **Deliberately removes race coefficients** to avoid |
|                     | unvalidated for Asian, Hispanic, global cohorts.  | race-based medicine; substitutes eGFR and SDI.      |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Known Limitations**| Systematic risk overestimation (20% to 50%+) in   | Calibrated lower than PCE; derived exclusively from |
|                     | contemporary cohorts; omits renal function;       | US health systems and claims data; uncalibrated for |
|                     | dichotomizes diabetes without glycemic context.   | non-US populations and international health systems.|
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Guideline Status**| Replaced by PREVENT in 2026 ACC/AHA Multisociety  | Adopted in 2026 ACC/AHA Dyslipidemia Guideline for  |
|                     | Dyslipidemia Guideline for primary prevention.    | applicable primary prevention risk decisions.       |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
```

### 4.2 International Guideline Specificity & Non-Applicability of PREVENT Outside the US
While PREVENT represents the current clinical standard in the United States under the 2026 ACC/AHA guideline:
- **United Kingdom:** The National Institute for Health and Care Excellence (NICE) officially mandates **QRISK3** (NICE Clinical Guideline CG181 / NG238) for NHS cardiovascular risk assessment. PREVENT is neither approved nor calibrated for NHS clinical pathways.
- **Europe:** The European Society of Cardiology (ESC) mandates **SCORE2** and **SCORE2-OP** (stratified across 4 European cardiovascular risk regions).
- **India / LMIC:** The Cardiological Society of India (CSI) and Indian Council of Medical Research (ICMR) reference the **WHO CVD risk charts (South Asia)** or recalibrated risk scores due to the premature onset and distinct phenotype of CAD in South Asians.

### 4.3 Task B Policy Confirmation
**Task B remains strictly excluded from the HeartXAI 2.0 MVP.** No prospective risk calculator (PCE, PREVENT, QRISK3, or SCORE2) shall be implemented during Milestones 01–20. Reconsidering Task B post-MVP requires formal clinical advisory review, country-specific guideline evaluation, and institutional ethics determinations.

---

## 5. Authoritative Three-Category Data Classification Policy

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            HEARTXAI 2.0 DATA CLASSIFICATION POLICY                                            |
+-----------------------+-----------------------------------------------+-------------------------------------------------------+
| Category              | Scope, Definition & Source                    | Permitted System Usage & Mandatory Safeguards         |
+-----------------------+-----------------------------------------------+-------------------------------------------------------+
| **Category A**        | Retrospective, open-access, de-identified     | - Permitted **only** for offline ML research, training|
| **Public Research**   | academic clinical datasets.                   |   and calibration (Milestones 09-10).                 |
| **Datasets**          | *Primary Source:* UCI Cleveland Heart Disease | - Subject to explicit dataset provenance verification.|
|                       | Catheterization Cohort ($N=303$, 1981-1984).  | - Documented limitations: symptomatic referral bias,  |
|                       | Open-access research license.                 |   small sample size, zero longitudinal follow-up.     |
+-----------------------+-----------------------------------------------+-------------------------------------------------------+
| **Category B**        | Artificially generated test fixtures, mock    | - Used for **all** frontend UI demonstrations, test   |
| **Synthetic**         | patient personas (Sarah, Marcus, Elena), and  |   fixtures, intake form tests, and integration tests. |
| **Application Data**  | integration testing records.                  | - Generated via `scripts/generate_synthetic_patients`|
|                       | Derived from parameterized distributions.      | - Contains **zero real human data**; zero PHI/PII.    |
+-----------------------+-----------------------------------------------+-------------------------------------------------------+
| **Category C**        | Personally Identifiable Information (PII) or  | - **STRICTLY PROHIBITED** during initial development, |
| **Real Patient**      | Personal Health Information (PHI) collected   |   demonstration, testing, and staging (Milestones 01- |
| **Information**       | from live human users or clinical systems.    |   20).                                                |
|                       |                                               | - Requires separate authorization, security review,   |
|                       |                                               |   privacy assessment, and applicable ethics review    |
|                       |                                               |   prior to any future collection or processing.       |
+-----------------------+-----------------------------------------------+-------------------------------------------------------+
```

---

## 6. Four-Pillar Clinical Governance & Regulatory Boundaries

Clinical governance is not an informal advisory checkbox. HeartXAI 2.0 establishes four independent governance pillars:

```
+---------------------------------------------------------------------------------------------------------+
|                                  FOUR-PILLAR CLINICAL GOVERNANCE FRAMEWORK                              |
+------------------------------------+--------------------------------------------------------------------+
| Governance Pillar                  | Mandate, Authority & Operational Boundaries                        |
+------------------------------------+--------------------------------------------------------------------+
| **1. Physician Advisory Review**   | Independent review by practicing physicians of patient-facing      |
|                                    | language, clinical limitations, educational context, and safety copy.|
|                                    | *Boundary:* Does NOT constitute regulatory clearance or ethics pass.|
+------------------------------------+--------------------------------------------------------------------+
| **2. Clinical Content Review**     | Systematic review and verification of clinical educational content,|
|                                    | emergency red-flag thresholds (e.g., SBP > 180), and directory listings|
|                                    | against published national cardiology society guidelines.          |
+------------------------------------+--------------------------------------------------------------------+
| **3. Institutional Ethics / IRB    | Formal determination by an Institutional Review Board (IRB) or     |
|    Determination**                 | Research Ethics Committee (REC). Mandatory if conducting research  |
|                                    | involving human participants or processing Category C real PHI.    |
+------------------------------------+--------------------------------------------------------------------+
| **4. Regulatory Applicability      | Formal legal and regulatory assessment under medical device rules. |
|    Assessment**                    | *US Reference:* **FDA January 2026 Clinical Decision Support (CDS)**|
|                                    | **Software Guidance** and Section 520(o)(1)(E) of the FD&C Act.    |
|                                    | *Boundary:* Software generating patient-facing predictive outputs is|
|                                    | scrutinized; HeartXAI makes **no blanket claims of exemption**     |
|                                    | and **no claims of formal certification or clinical validation**.  |
+------------------------------------+--------------------------------------------------------------------+
```

### 6.1 Regulatory Applicability under FDA January 2026 CDS Guidance
Under the FDA January 2026 Final Guidance on Clinical Decision Support Software:
- Non-device CDS status under Section 520(o)(1)(E) requires that the software be intended for healthcare professionals (HCPs) who can independently review the basis for the recommendations.
- **Patient-directed or consumer-facing software** that analyzes patient-specific medical data to predict risk or output clinical classifications is **not exempt** under Criterion 3/4 and may be regulated as a device (Software as a Medical Device - SaMD).
- **HeartXAI 2.0 Posture:** HeartXAI 2.0 does NOT claim an automatic statutory exemption from medical device oversight. For MVP, it is developed strictly as an educational technology demonstration operating on synthetic data. Formal regulatory classification (513(g) or pre-market submission) will be required before any clinical or commercial deployment.

### 6.2 Mandatory Medical Disclaimer (Required on All Assessment Views)
> **MANDATORY CLINICAL NOTICE:** HeartXAI 2.0 is an experimental educational tool designed to demonstrate explainable machine learning concepts using historical research data. It **DOES NOT** provide medical diagnoses, clinical prognoses, or treatment recommendations. The assessment reflects statistical patterns observed in historical research datasets and cannot substitute for an evaluation by a licensed healthcare professional. If you are experiencing chest pain, tightness, shortness of breath, radiating arm or jaw pain, or acute discomfort, **IMMEDIATELY CALL EMERGENCY SERVICES (911 in the US, 999 in the UK, 112 in India)** or visit the nearest hospital emergency room.

---

## 7. Prohibited & Unsupported Clinical Claims Ledger

The following claims are strictly **PROHIBITED** across all user interfaces, API responses, PDF exports, and documentation:

1. ❌ *"HeartXAI diagnoses coronary artery disease, heart attacks, or cardiovascular conditions."*
2. ❌ *"The system calculates your exact 10-year risk of having a heart attack."*
3. ❌ *"HeartXAI is exempt from FDA or medical device regulation."*
4. ❌ *"HeartXAI replaces the need for a cardiologist, physician consultation, or angiogram."*
5. ❌ *"The model detects whether you are currently having a heart attack."*
6. ❌ *"You can adjust, start, or stop prescribed medications based on these results."*
7. ❌ *"HeartXAI is an FDA-approved or CE-marked diagnostic medical device."*
8. ❌ *"SHAP values prove the exact biological cause of your cardiovascular condition."*
9. ❌ *"Achieving the counterfactual values guarantees you will not develop heart disease."*
10. ❌ *"HeartXAI has been clinically validated in the US, UK, India, or any other country."*
