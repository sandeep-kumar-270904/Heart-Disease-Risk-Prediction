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
- **Original Source Target Definition (`num`):** In the primary UCI documentation (`heart-disease.names` by Robert Detrano & David Aha), the target attribute is defined verbatim as:
  ```
  58 num: diagnosis of heart disease (angiographic disease status)
        -- Value 0: < 50% diameter narrowing
        -- Value 1: > 50% diameter narrowing
        (in any major vessel: attributes 59 through 68 are vessels)
  ```
  In the primary research paper (Detrano et al., *Am J Cardiol* 1989;64:304–310), coronary disease is defined as:
  > *"greater than 50% reduction in luminal diameter of at least 1 of the major coronary arteries (left anterior descending, circumflex, or right coronary artery) on selective coronary arteriography."*
- **Precision on the 50% Threshold:** The primary source documentation and paper explicitly define positive CAD as **strictly greater than 50% diameter narrowing** ($>50\%$), NOT $\ge 50\%$. The borderline threshold of exactly $50\%$ narrowing is not categorized as positive in the source documentation. In the processed 14-attribute dataset, `num` takes discrete values 0, 1, 2, 3, 4 indicating the number of major vessels with $>50\%$ diameter narrowing.
- **Approved Binary Transformation for Task A:**
  $$y = \begin{cases} 0 & \text{if } num = 0 \text{ (absence of significant stenosis, } <50\%) \\ 1 & \text{if } num \ge 1 \text{ (presence of significant stenosis, } >50\% \text{ in 1–4 vessels)} \end{cases}$$
  Distribution in Cleveland: 164 negative ($54.1\%$) and 139 positive ($45.9\%$).

### 3.3 Critical Population, Methodology & Privacy Limitations
1. **Referral Cohort (Severe Selection Bias):** The cohort consists exclusively of symptomatic patients or patients with abnormal non-invasive findings (e.g., severe treadmill stress tests) who were referred for invasive coronary catheterization. The background disease prevalence is $\approx 46\%$, vastly higher than the $2\text{--}6\%$ prevalence in asymptomatic general adult populations.
2. **Small Sample Size ($N=303$):** With only 303 total instances (and 6 records containing missing values in `ca` or `thal`, leaving $N=297$ complete cases), the sample is underpowered for generalizable sub-population modeling.
3. **Demographic Imbalance:** 206 male ($68\%$) and 97 female ($32\%$). The cohort was drawn from a regional US urban clinical population in the early 1980s; it lacks racial, ethnic, and global diversity.
4. **Historical Diagnostic Technology:** Catheterization procedures and laboratory assays reflect 1980s clinical standards. Modern high-sensitivity troponin assays, coronary CT angiography (CCTA), and current lipid fractionation were not available.
5. **Absence of Longitudinal Follow-up:** **The dataset contains zero follow-up data.** It records solely whether a patient had $>50\%$ vessel narrowing on the day of angiography. **It cannot calculate the probability of a future heart attack, stroke, or cardiovascular event.**
6. **Privacy, Provenance & Research-Data Reclassification (Known vs. Unknown):**
   - **Formal Reclassification:** The UCI Cleveland dataset is formally reclassified as **public, historical, human-origin health research data with documented privacy limitations**.
   - **Absence of Modern De-Identification Certification:** The dataset pre-dates modern statutory privacy legislation (HIPAA enacted 1996; EU GDPR enacted 2016). It was **never formally evaluated or certified under modern statutory de-identification standards** (such as HIPAA Safe Harbor 45 CFR § 164.514(b) or Expert Determination § 164.514(a), or GDPR Recital 26 / Article 4(1) anonymization). HeartXAI 2.0 makes **no claim of formal anonymization, modern de-identification, or blanket exclusion from privacy laws** without sufficient evidence.
   - **What is Known from Primary Sources:** The dataset was contributed to the UCI Machine Learning Repository in 1988 by Dr. Robert Detrano and David Aha. In the primary documentation file `heart-disease.names`, raw attribute 2 (`ccf: social security number`) is documented as having been replaced by the contributor with a dummy value of 0. In the standardized 14-attribute file (`processed.cleveland.data`), attributes 1 and 2 (`id` and `ccf`) were omitted entirely. The published 14-attribute CSV contains no patient names, home addresses, phone numbers, or social security numbers.
   - **What is Unknown & Unverified:** The primary paper (Detrano et al., *Am J Cardiol* 1989) does not document the specific institutional data extraction protocol, whether informed consent was obtained from the 1981–1984 patients for secondary public open-source distribution, or whether Cleveland Clinic Institutional Review Board approval was formally granted for public web deposition. Whether quasi-identifier combinations (e.g., age, sex, resting ECG patterns, fluoroscopy vessel counts) could present theoretical re-identification risk against historical hospital catheterization logs remains unassessed in modern literature.
   - **Mandatory Pre-Training Assessment (Milestone 09 Gate):** Prior to ingesting Category A data for model training in Milestone 09, a formal, documented assessment of **data provenance, repository licensing terms, permitted research use, and jurisdiction-specific privacy obligations** must be executed and approved.
   - **Retraction of Blanket Exposure Claims & Separation of Data Risks:** Claims that data classification policies "eliminate all PHI/PII exposure or statutory breach-notification liabilities" are unsupported and hereby retracted. Data risks are strictly differentiated:
     - *Category A (Historical Research Data Risks):* Human-origin clinical data ($N=303$) carrying potential re-identification risks in high-dimensional or linkage scenarios, ambiguous historical patient consent/licensing provenance, and potential residual privacy obligations under specific local jurisdictions. Confined strictly to offline model research.
     - *Category B (Synthetic Application Data Provenance & Risks):* The synthetic patient generator (`scripts/generate_synthetic_patients.py`, scheduled for Milestone 02 implementation) is architected to derive continuous biomarker distributions (blood pressure, cholesterol, max heart rate) and conditional multinomial probabilities from empirical multivariate distributions of the **human-origin UCI Cleveland benchmark** (as specified in `ENVIRONMENT_CONFIGURATION_STRATEGY.md` and `TEST_DATA_AND_PRIVACY_STRATEGY.md`). Consequently, Category B is **statistically derived synthetic data parameterized from human-origin clinical reference distributions**, NOT "zero-human-origin" data. **Formal differential privacy is NOT implemented in the generator, and HeartXAI provides no differential privacy guarantee.** The generator serves strictly as statistically derived synthetic application test data with documented limitations (outlier replication and memorization risks). Synthetic fixtures must remain **completely separate from all model training, validation, and evaluation datasets**.
     - *Category C (Real Patient Data):* Real PHI/PII. **Strictly prohibited across all MVP milestones (01–20).**

### 3.4 Operational & Research Classification
The model trained on this dataset must be classified strictly as an **Experimental Machine Learning Dataset Classifier**. Its outputs must never be presented as:
- A medical diagnosis.
- A validated future cardiovascular event prediction.
- A clinically validated risk score.
- A replacement for a licensed physician's evaluation.

### 3.5 Methodological Review of Calibration Metrics: Brier Score & ECE
In earlier planning documents, numerical thresholds were proposed for probability calibration: **Brier score $\le 0.12$** and **Expected Calibration Error (ECE) $\le 0.05$**.

#### Methodological Justification & Limitations
1. **Brier Score Sensitivity to Disease Prevalence:**
   $$\text{Brier} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$
   The Brier score measures the mean squared error between predicted probabilities $p_i \in [0, 1]$ and actual binary outcomes $y_i \in \{0, 1\}$. It is a strictly proper scoring rule combining discrimination and calibration. However, its value is directly dependent on baseline disease prevalence ($\bar{y}$). In the Cleveland cohort ($\bar{y} \approx 0.4587$), an uninformative model predicting the sample mean has a baseline Brier score of $\text{Brier}_{\text{ref}} = \bar{y}(1 - \bar{y}) \approx 0.2483$. A threshold of $\le 0.12$ represents a Brier Skill Score ($\text{BSS} = 1 - \frac{0.12}{0.2483} \approx 51.7\%$) improvement over baseline. While $\le 0.12$ represents a strong engineering benchmark, it does NOT guarantee clinical calibration because a model with high discrimination could mask poor calibration in low-risk patients.
2. **Expected Calibration Error (ECE) Vulnerabilities:**
   $$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
   ECE groups predictions into $M$ bins (typically $M=10$). In a small test fold ($N \approx 60$ in 5-fold CV), each bin contains only 4 to 8 patients, making ECE highly volatile; a single patient outcome shifts a bin's empirical accuracy by $12\text{--}25\%$. Furthermore, ECE weights all bins equally, whereas clinical utility depends disproportionately on calibration around clinical decision thresholds ($10\%\text{--}30\%$).
3. **Rigorous Calibration Validation Framework (Milestone 10/11 Requirements):**
   - **Leakage-Safe Out-of-Fold (OOF) Probability Predictions:** All calibration evaluation and metric computation (Brier score, ECE, calibration curves) must be performed strictly using **out-of-fold (OOF) cross-validation predictions** or a held-out test split, completely isolated from in-sample training data.
   - **Training-Only Fitting of Calibration Transformers:** Post-hoc calibration methods (e.g., Platt scaling / logistic calibration, Isotonic regression) must be **fitted strictly on the training folds/sets only**. Applying or fitting calibration transformers across full datasets or test folds constitutes data leakage and is strictly prohibited.
   - **Confidence Intervals & Statistical Uncertainty (Exploratory Nature):** All reported calibration metrics (Brier score, ECE, calibration slope, calibration intercept) must be accompanied by 95% bootstrap confidence intervals (1,000 stratified resamples). However, because $N=303$ is small, bootstrap resamples capture internal sampling variability only; **neither the proposed sample size, bootstrap count, nor numerical thresholds may be treated as proof of reliable clinical performance**. Confidence intervals remain **strictly exploratory statistical estimates**.
   - **External Validation Prerequisite:** Internal cross-validation calibration does not prove generalizability. **External validation on an independent, contemporary clinical cohort is strictly required before asserting any clinical calibration claim.**
   - **Exploratory Status of Decision Curve Analysis (DCA):** Decision Curve Analysis (DCA; Vickers et al.) must be formally labeled as **exploratory** unless an explicit, defensible clinical decision context (e.g., referral for non-invasive imaging vs. outpatient monitoring) and an explicit harm-to-benefit threshold probability range ($p_t$) are clinically established and justified.
   - **Provisional Status of Numerical Thresholds:** The thresholds $\text{Brier} \le 0.12$ and $\text{ECE} \le 0.05$ remain **provisional engineering heuristic targets** until methodologically justified against empirical out-of-fold distributions and clinical context. Meeting these numerical targets does NOT warrant claiming that the model is clinically calibrated.

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
| **Category A**        | Public, historical, human-origin health       | - Permitted **only** for offline ML research, training|
| **Public Research**   | research data with documented privacy          |   and calibration (Milestones 09-10).                 |
| **Data**              | limitations (UCI Cleveland, $N=303$, 1981-1984)| - Requires documented provenance, license, permitted-  |
|                       | Historical public repository deposition.       |   use, and privacy risk assessment prior to training. |
|                       | Lacks modern HIPAA/GDPR certification.         | - Limitations: human-origin data, potential linkage    |
|                       |                                               |   risks, referral bias, zero longitudinal follow-up.  |
+-----------------------+-----------------------------------------------+-------------------------------------------------------+
| **Category B**        | Artificially generated test fixtures, mock    | - Used for **all** frontend UI demonstrations, test   |
| **Synthetic**         | patient personas (Sarah, Marcus, Elena), and  |   fixtures, intake form tests, and integration tests. |
| **Application Data**  | integration testing records.                  | - Generated via `scripts/generate_synthetic_patients`|
|                       | Parameterized distributions derived from      | - Statistically derived from clinical reference data; |
|                       | empirical multivariate clinical benchmark data.|   carries residual memorization & outlier risks.      |
|                       | Not direct real records; subject to DP checks.| - Standard application & infrastructure cyber defense.|
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
| **3. Institutional Ethics / IRB    | Formal determination by an Institutional Review Board (IRB),       |
|    Determination**                 | Research Ethics Committee (REC), or applicable institutional       |
|                                    | ethics authority. Mandatory documented determination before        |
|                                    | initiating any human-participant usability or research activities, |
|                                    | or processing Category C real PHI.                                 |
+------------------------------------+--------------------------------------------------------------------+
| **4. Regulatory Applicability      | Formal legal and regulatory assessment under medical device rules. |
|    Assessment**                    | *US Reference:* FDA Section 520(o)(1)(E) and **FDA January 2026**   |
|                                    | **Clinical Decision Support (CDS) Software Guidance**; EU MDR       |
|                                    | 2017/745 Rule 11 & MDCG 2019-11 / 2020-1; UK MHRA; India CDSCO     |
|                                    | MDR 2017 & **CDSCO MDSW Guidance (July 2026)**.                    |
|                                    | *Boundary:* HeartXAI makes **no claims of exemption**, no claims of  |
|                                    | non-device status, and no claims of regulatory clearance.          |
+------------------------------------+--------------------------------------------------------------------+
```

### 6.1 Independent Jurisdictional Regulatory Analysis

> [!WARNING]
> **MANDATORY LEGAL DISCLAIMER & SPECIALIST REVIEW REQUIREMENT**  
> The regulatory analyses below represent technical architectural assessments based on published statutes and agency guidance. They do NOT constitute formal legal advice. **Specialist review by qualified healthcare regulatory legal counsel in each target jurisdiction is strictly required** before drawing definitive legal conclusions regarding device qualification, risk classification, or marketing authorization. HeartXAI 2.0 makes no claim of exemption, non-device status, or regulatory clearance in any jurisdiction.

#### 1. United States — Food and Drug Administration (FDA)
- **Governing Framework:** Federal Food, Drug, and Cosmetic Act (FD&C Act) § 520(o)(1)(E), amended by the 21st Century Cures Act; **FDA January 2026 Final Guidance on Clinical Decision Support Software**.
- **The Four Statutory Criteria (US Only):** Under § 520(o)(1)(E), software is excluded from the definition of a medical device ONLY if it meets all four cumulative criteria:
  1. *Criterion 1:* Not intended to acquire, process, or analyze medical images or signals from IVDs or pattern recognition.
  2. *Criterion 2:* Intended to display, analyze, or print medical information about a patient or other medical information.
  3. *Criterion 3:* Intended to support or provide recommendations to a **healthcare professional (HCP)** about prevention, diagnosis, or treatment.
  4. *Criterion 4:* Intended to enable such HCP to **independently review the basis** for the recommendations so that the HCP does not rely primarily on the software to make a clinical decision.
- **Critical US Analysis:**
  - The four statutory criteria apply **strictly to US FDA jurisdiction**; they do not apply in the EU, UK, or India.
  - While HeartXAI 2.0 incorporates TreeSHAP feature attributions, complex gradient-boosted decision trees may not permit an HCP to independently verify the mathematical calculations in real time.
  - Crucially, patient-facing risk estimators or clinical likelihood tools intended for direct consumer use **fail Criterion 3 & 4** and are generally regulated as medical devices (Software as a Medical Device - SaMD).
  - *Status:* **Undetermined.** Formal 513(g) determination or Pre-Submission (Q-Submission) required prior to clinical deployment.

#### 2. European Union — European Medicines Agency & Notified Bodies
- **Governing Framework:** Regulation (EU) 2017/745 on Medical Devices (**EU MDR**); Medical Device Coordination Group guidance documents:
  - **MDCG 2019-11 rev.1:** *Guidance on Qualification and Classification of Software in Regulation (EU) 2017/745 and Regulation (EU) 2017/746* (**June 2025 Revision**).
  - **MDCG 2020-1:** *Guidance on Clinical Evaluation (MDR) / Performance Evaluation (IVDR) of Medical Device Software* (March 2020).
- **Classification Rules (Annex VIII, Chapter III, Rule 11 Verbatim Text):**
  > *"Software intended to provide information which is used to take decisions with diagnosis or therapeutic purposes is classified as class IIa, except if such decisions have an impact that may cause:*
  > *- death or an irreversible deterioration of a person’s state of health, in which case it is in class III; or*
  > *- a serious deterioration of a person’s state of health or a surgical intervention, in which case it is classified as class IIb.*
  > *Software intended to monitor physiological processes is classified as class IIa, except if it is intended for monitoring of vital physiological parameters, where the nature of variations of those parameters is such that it could result in immediate danger to the patient, in which case it is classified as class IIb.*
  > *All other software is classified as class I."*
- **Critical EU Analysis:**
  - *Absence of Non-Device CDS Exemption:* The EU MDR contains **no statutory non-device exemption analogous to US Section 520(o)(1)(E)**. If software processes clinical parameters to provide information used to take decisions with diagnostic or therapeutic purposes, it qualifies as medical device software.
  - *Rule 11 Impact:* Because HeartXAI 2.0 calculates coronary disease likelihood to inform clinical discussion, under EU MDR Rule 11 it defaults to **Class IIa or higher** (Class IIb if misclassification could lead to serious clinical deterioration). This requires a notified body conformity assessment, quality management system (ISO 13485), and clinical evaluation report (CER) prior to CE marking.

#### 3. United Kingdom — Medicines and Healthcare products Regulatory Agency (MHRA)
- **Governing Framework:** UK Medical Devices Regulations 2002 (SI 2002 No 618, as amended); **MHRA Software and AI as a Medical Device Change Programme**.
- **Critical UK Analysis:**
  - Software intended to analyze patient data to provide diagnostic information, calculate disease probability, or guide clinical management is regulated as a medical device requiring a **UKCA mark** (or recognized CE mark under transitional extension arrangements).
  - MHRA evaluates whether software performs an automated calculation that influences clinical decisions. Patient-facing symptom and risk checkers are closely scrutinized for Class IIa/IIb classification under UK MDR Part II.

#### 4. India — Central Drugs Standard Control Organisation (CDSCO)
- **Governing Framework:** Medical Devices Rules, 2017 (MDR 2017), framed under the Drugs and Cosmetics Act, 1940; Central Licensing Authority (CLA).
- **Current CDSCO Guidance Document on Medical Device Software:**
  - **Title:** *Guidance Document on Medical Device Software (MDSW)*
  - **Document Number:** **CDSCO/MD/GD/MDSW/01/2026**
  - **Publication Date:** **21 July 2026** (finalized following public stakeholder consultation on the draft issued 21 October 2025)
  - **Issuing Authority:** Central Drugs Standard Control Organisation (CDSCO), Directorate General of Health Services, Ministry of Health & Family Welfare, Government of India.
- **Classification Principles (Table 2: Risk Classification Matrix for Standalone MDSW / SaMD):**
  Under Section 4 and Table 2 of the MDSW 2026 guidance, standalone software classification is not automated, but is determined strictly by evaluating:
  1. The **significance of the information** provided by the software to the healthcare decision (*Treats or Diagnoses*, *Drives Clinical Management*, or *Informs Clinical Management*).
  2. The **state of the healthcare situation or condition** (*Critical*, *Serious*, or *Non-serious*).

```
+-----------------------------------+--------------------+----------------------------+-----------------------------+
| State of Healthcare Situation     | Treats or Diagnoses| Drives Clinical Management | Informs Clinical Management |
+-----------------------------------+--------------------+----------------------------+-----------------------------+
| Critical (e.g. life-threatening)  | Class D            | Class C                    | Class B                     |
| Serious (e.g. major impairment)   | Class C            | Class B                    | Class A                     |
| Non-serious (e.g. mild/transient) | Class B            | Class A                    | Class A                     |
+-----------------------------------+--------------------+----------------------------+-----------------------------+
```

  - *Non-Clinical / Lay User Caveat:* Standalone MDSW intended to be used directly by lay persons or consumers in a serious situation or condition without the oversight of specialized healthcare professionals may be elevated into a higher risk category.
  - *No Definitive Classification Assigned:* HeartXAI 2.0 is NOT automatically assigned to Class B or Class C. Its risk tier depends on formal legal review of its intended user (lay person vs. physician), intended use (educational vs. clinical management), and diagnostic autonomy. Status remains formally **undetermined**.
- **Submission & Licensing Portals:**
  - **National Single Window System (NSWS)** (`nsws.gov.in`): Mandated for test-licence applications (e.g., Form MD-12 / MD-13 for testing, clinical investigation, or evaluation).
  - **Online System for Medical Devices** (`cdscomdonline.gov.in`): Mandated for other relevant regulatory permissions, manufacturing licences, and import licences under MDR 2017 (e.g., Form MD-7, MD-8, MD-14, MD-15).

#### 5. Cross-Jurisdictional Synthesis
```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            JURISDICTIONAL REGULATORY COMPARISON MATRIX                                        |
+---------------------+-------------------------------+-----------------------------------+-------------------------------------+
| Jurisdiction        | Governing Regulation          | Primary Software Classification   | Key SaMD Threshold                  |
+---------------------+-------------------------------+-----------------------------------+-------------------------------------+
| **United States**   | FDA / FD&C Act § 520(o)(1)(E) | Evaluated against 4 CDS criteria; | Patient-facing risk prediction fails|
|                     | Jan 2026 CDS Final Guidance   | SaMD Class II if non-exempt.      | Criteria 3/4; device status likely. |
+---------------------+-------------------------------+-----------------------------------+-------------------------------------+
| **European Union**  | EU MDR 2017/745               | Annex VIII Rule 11 (Class IIa+);  | No non-device CDS exemption; Rule 11|
|                     | MDCG 2019-11 rev.1 (June 2025)| Class IIa default for CDS.        | classifies diagnostic CDS as IIa+.  |
+---------------------+-------------------------------+-----------------------------------+-------------------------------------+
| **United Kingdom**  | UK MDR 2002 (as amended)      | MHRA SaMD framework;              | Software interpreting health data to|
|                     | MHRA AI/Software Programme    | UKCA Class IIa/IIb.               | guide decisions requires UKCA mark. |
+---------------------+-------------------------------+-----------------------------------+-------------------------------------+
| **India**           | CDSCO / MDR 2017 &            | Standalone MDSW Table 2 Matrix;   | Classification per Table 2 matrix;  |
|                     | MDSW Guidance (21 July 2026)  | Class A, B, C, or D (Undetermined)| NSWS for test-licences; Online Sys. |
+---------------------+-------------------------------+-----------------------------------+-------------------------------------+
```

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
