# HeartXAI 2.0 — Phase 12.2.3 Final Review
## Data Privacy, Research Governance, Jurisdictional Regulatory Alignment & Calibration Validation

**Document Version:** 1.0.0  
**Phase:** 12.2.3 (Final Data Privacy, Research Governance & Calibration Precision Review)  
**Date:** November 2026  
**Auditor Roles:** Principal Software Architect, Healthcare AI Research Reviewer, Clinical Safety Consultant, Security Architect, and Independent Technical Auditor  
**Project Status:** READY FOR MILESTONE 01 — GOVERNANCE APPROVAL STILL REQUIRED  
**Governance Decisions Status:** ALL FIVE (DEC-001 through DEC-005) ARE **`PENDING USER DECISION`**

---

## 1. Executive Summary

This precision review document resolves the four final governance, research-data privacy, regulatory citation, and calibration methodology findings identified during independent audit of the HeartXAI 2.0 pre-implementation dossier:

1. **Category A Research-Data Privacy & Provenance Reclassification:** Formally reclassifies the UCI Cleveland dataset as public, historical, human-origin health research data with documented privacy limitations. Explicitly rejects unverified claims of formal modern de-identification or exclusion from statutory privacy frameworks. Enforces a mandatory pre-training provenance, license, permitted-use, and privacy risk assessment in Milestone 09. Retracts unsupported claims that Category A/B policies eliminate all PHI/PII exposure or breach notification liabilities, and strictly distinguishes Category A research-data risks from Category B synthetic application-data risks.
2. **Human-Subject Research & Usability Governance:** Replaces categorical claims that all human-participant usability activities require identical IRB/REC approval and informed consent. Clarifies the spectrum of human-participant activities and mandates obtaining a documented determination from the applicable institutional ethics committee (IRB/REC/IEC) or regulatory authority prior to initiating any human-participant activities, applying calibrated review, consent, privacy, and data-protection protocols based on jurisdiction and activity while keeping real patient data strictly prohibited across the MVP.
3. **Jurisdictional Regulatory References:** Cites the verbatim statutory text of EU MDR Annex VIII, Chapter III, Rule 11 and authoritative guidance (MDCG 2019-11 and MDCG 2020-1). Cites the current CDSCO *Guidance Document on Medical Device Software (MDSW)* (Document No. CDSCO/MD/GD/MDSW/01/2026, published July 21, 2026) under the Medical Devices Rules, 2017. Preserves independent jurisdictional assessments for the US, EU, UK, and India, and maintains that regulatory classification remains formally undetermined pending qualified legal counsel review.
4. **Rigorous Calibration Validation Protocol:** Mandates leakage-safe out-of-fold (OOF) cross-validation probability predictions and fitting calibration transformers (Platt scaling / Isotonic regression) strictly on training folds. Requires reporting 95% bootstrap confidence intervals for all calibration metrics (Brier score, ECE, calibration slope, and intercept). Mandates independent external cohort validation before any clinical calibration claim is made. Formally designates Decision Curve Analysis (DCA) as exploratory unless an explicit clinical decision context and threshold range are specified, and maintains Brier ($\le 0.12$) and ECE ($\le 0.05$) as provisional engineering heuristic targets.

---

## 2. Category A Research-Data Privacy & Provenance Reclassification

### 2.1 Formal Reclassification of the UCI Cleveland Dataset
The UCI Cleveland dataset is formally reclassified as:
> **Public, historical, human-origin health research data with documented privacy limitations.**

```
+----------------------------------------------------------------------------------------------------+
|                         CLEVELAND DATASET PRIVACY & RESEARCH-DATA STATUS                           |
+------------------------------------+---------------------------------------------------------------+
| Dimension                          | Authoritative Audit Finding                                   |
+------------------------------------+---------------------------------------------------------------+
| **Data Nature & Origin**           | Historical human-origin clinical data ($N=303$ catheterization |
|                                    | patients, 1981–1984, Cleveland Clinic Foundation).            |
+------------------------------------+---------------------------------------------------------------+
| **De-Identification Status**       | Field-level redaction performed historically (dummy 0 for SSN |
|                                    | attribute `ccf`; patient ID omitted). **NO formal modern      |
|                                    | statutory de-identification certification** (HIPAA Safe Harbor |
|                                    | § 164.514(b), Expert Method § 164.514(a), or GDPR Art 4(1)).  |
+------------------------------------+---------------------------------------------------------------+
| **Statutory Privacy Exemption**    | **Unverified.** HeartXAI makes NO claim of blanket statutory   |
|                                    | exclusion from data protection laws without specific evidence.|
+------------------------------------+---------------------------------------------------------------+
| **Pre-Training Governance Gate**   | Formal documented assessment of data provenance, repository    |
|                                    | licensing terms, permitted research use, and privacy risk     |
|                                    | **mandated prior to model training in Milestone 09**.         |
+------------------------------------+---------------------------------------------------------------+
```

### 2.2 Retraction of Blanket Exposure Claims
Previous statements asserting that the Three-Tier Data Classification Policy *"eliminates all PHI/PII exposure or statutory breach-notification liabilities"* were technically overbroad and unsupported. They are hereby formally retracted. 

While prohibiting live patient health information (Category C) in the application eliminates patient PHI/PII ingestion into the web platform and relieves the application of clinical breach-notification duties under HIPAA/GDPR during development, historical human-origin research data (Category A) carries distinct, non-zero research-data risks.

### 2.3 Distinct Risk Profiles: Category A vs. Category B

```
+----------------------------------------------------------------------------------------------------+
|                         RESEARCH-DATA vs. SYNTHETIC-DATA RISK TAXONOMY                             |
+-----------------------------------------+----------------------------------------------------------+
| CATEGORY A: HISTORICAL RESEARCH DATA    | CATEGORY B: SYNTHETIC APPLICATION DATA                   |
| (UCI Cleveland Dataset, N=303)          | (Algorithmically Generated Personas & Records)           |
+-----------------------------------------+----------------------------------------------------------+
| 1. **Human Origin:** Real biological    | 1. **Zero Human Origin:** Generated purely via Python    |
|    measurements from human patients.    |    distributions (`scripts/generate_synthetic_patients.py`).|
| 2. **Linkage / Re-identification Risk:**| 2. **Zero Re-identification Risk:** Mock personas        |
|    Theoretical risk if quasi-identifiers|    (Sarah, Marcus, Elena) correspond to no living person.|
|    are linked against historical logs.  | 3. **Application Vulnerabilities:** Subject to standard  |
| 3. **Consent & Licensing Ambiguity:**   |    web and database security risks (SQLi, IDOR, XSS,     |
|    Historical 1980s collection lacks    |    session hijacking, credential stuffing).              |
|    explicit digital open-source consent.| 4. **Distributional Limits:** Synthetic fixtures may    |
| 4. **Residual Statutory Obligations:**  |    exhibit physiological artifacts or covariate shifts   |
|    Potential jurisdictional rules on    |    not representative of real populations.               |
|    secondary research data processing.  | 5. **Scope:** Powers all UI staging, demonstrations,     |
| 5. **Scope:** Restricted strictly to    |    E2E testing, and integration test suites.             |
|    offline model research (M09–M10).    |                                                          |
+-----------------------------------------+----------------------------------------------------------+
```

### 2.4 Milestone 09 Pre-Training Governance Gate
Before ingesting Category A data into the training pipeline in Milestone 09, the engineering and clinical governance team must execute and archive a formal **Research Data Provenance and Privacy Risk Evaluation**:
1. **Provenance & Custody Chain:** Trace the historical repository accession from UCI ML Repository (1988) and subsequent mirrors.
2. **Licensing & Permitted Research Use:** Review terms under Creative Commons Attribution 4.0 International (CC BY 4.0) or legacy repository terms to ensure commercial/academic evaluation permissions.
3. **Quasi-Identifier Linkage Risk Assessment:** Verify that no demographic or clinical feature combinations (Age, Sex, Resting BP, Cholesterol, Thalassemia status) can be linked to identifiable living or deceased individuals.
4. **Jurisdiction-Specific Obligations:** Confirm that offline research processing complies with applicable secondary health research regulations in the project's development jurisdiction.

---

## 3. Human-Subject Research & Usability Governance

### 3.1 Replacing Categorical Claims with Activity-Based Governance
Previous drafts asserted a single, blanket rule: that *all* human-participant activities universally mandate a full IRB/REC protocol, clinical trial registration, and formal clinical informed consent. This categorical assertion failed to distinguish the regulatory spectrum of human-computer interaction (HCI) evaluation.

Human-participant activities exist across distinct tiers:
- **Tier 1: Formative Usability & Internal UX Evaluation:** Testing UI ergonomics, design system contrast, navigation flows, and accessibility with healthy adult volunteers or internal colleagues using 100% Category B synthetic personas. In many academic and institutional jurisdictions (e.g., US 45 CFR § 46.104(d)), such activities qualify as quality improvement or exempt usability evaluation rather than regulated human-subject clinical research.
- **Tier 2: Cognitive Walkthroughs & Clinician Comprehension Testing:** Evaluating whether healthcare professionals correctly interpret TreeSHAP feature attributions and counterfactuals using synthetic clinical dossiers.
- **Tier 3: Clinical Usability Studies with Patients:** Evaluating the software in active clinical workflows with individuals experiencing cardiovascular symptoms.
- **Tier 4: Interventional & Prospective Diagnostic Trials:** Evaluating whether software recommendations influence diagnostic decisions or clinical patient outcomes.

```
+----------------------------------------------------------------------------------------------------+
|                         HUMAN-PARTICIPANT ACTIVITY GOVERNANCE SPECTRUM                             |
+----------------------+--------------------+---------------------+----------------------------------+
| Activity Level       | Participant Type   | Data Processed      | Institutional Ethics Mandate     |
+----------------------+--------------------+---------------------+----------------------------------+
| **Formative UX /     | Internal staff /   | Category B          | Documented institutional         |
| Usability Testing**  | Design volunteers  | Synthetic Only      | determination (often exempt / QI)|
+----------------------+--------------------+---------------------+----------------------------------+
| **Cognitive Explan-  | Practicing         | Category B          | Documented IRB/REC determination |
| ability Walkthrough**| Clinicians         | Synthetic Dossiers  | (expedited review or exemption)  |
+----------------------+--------------------+---------------------+----------------------------------+
| **Clinical Usability | Patients /         | Category B/C        | Formal IRB/REC approval, written |
| Evaluation**         | Hospital Patients  | (Prohibited in MVP) | informed consent & privacy review|
+----------------------+--------------------+---------------------+----------------------------------+
| **Diagnostic Trial / | Clinical Patient   | Category C          | Full IRB/REC approval, GCP, IDE, |
| Clinical Study**     | Cohorts            | (Prohibited in MVP) | clinical trial registration      |
+----------------------+--------------------+---------------------+----------------------------------+
```

### 3.2 Documented Determination Requirement
Rather than asserting an arbitrary assumption of exemption or imposing an inappropriate clinical trial protocol on formative UI testing:
> **GOVERNANCE INVARIANT:** Prior to initiating any human-participant usability or research activities, the project team must submit an activity protocol and obtain a **documented determination from the applicable Institutional Review Board (IRB), Research Ethics Committee (REC), or institutional research governance authority**.

The determination specifies whether the planned activity constitutes:
1. Not Human Subjects Research (NHSR) / Quality Improvement (QI),
2. Exempt Human Subjects Research (e.g., under 45 CFR § 46.104(d)),
3. Expedited Review Protocol, or
4. Full Board Review requiring prospective written informed consent.

### 3.3 Protection of Real Patient Data in MVP
Regardless of the ethics determination tier, **Category C real patient health information remains strictly prohibited across all MVP milestones (01–20)**. All formative usability, accessibility, and clinician walkthrough activities in the MVP shall utilize exclusively **Category B synthetic data fixtures**.

---

## 4. Jurisdictional Regulatory Alignment & Authoritative Citations

### 4.1 European Union: EU MDR 2017/745 & MDCG Guidance

#### Governing Legislation
**Regulation (EU) 2017/745 of the European Parliament and of the Council of 5 April 2017 on medical devices (EU MDR)**, amending Directive 2001/83/EC, Regulation (EC) No 178/2002 and Regulation (EC) No 1223/2009 and repealing Council Directives 90/385/EEC and 93/42/EEC.

#### Classification Rule: Annex VIII, Chapter III, Rule 11 (Verbatim Statutory Text)
> *"Software intended to provide information which is used to take decisions with diagnosis or therapeutic purposes is classified as class IIa, except if such decisions have an impact that may cause:*
> *- death or an irreversible deterioration of a person’s state of health, in which case it is in class III; or*
> *- a serious deterioration of a person’s state of health or a surgical intervention, in which case it is classified as class IIb.*
> 
> *Software intended to monitor physiological processes is classified as class IIa, except if it is intended for monitoring of vital physiological parameters, where the nature of variations of those parameters is such that it could result in immediate danger to the patient, in which case it is classified as class IIb.*
> 
> *All other software is classified as class I."*

#### Authoritative MDCG Guidance Citations
- **MDCG 2019-11:** *Guidance on Qualification and Classification of Software in Regulation (EU) 2017/745 and Regulation (EU) 2017/746* (Medical Device Coordination Group, October 2019). Establishes the decision tree for qualification of software as a medical device (MDSW) and applies IMDRF risk-categorization principles to Rule 11.
- **MDCG 2020-1:** *Guidance on Clinical Evaluation (MDR) / Performance Evaluation (IVDR) of Medical Device Software* (Medical Device Coordination Group, March 2020). Defines the three pillars of software clinical evaluation: valid clinical association, technical performance, and clinical performance.

#### Architectural Assessment
Because HeartXAI 2.0 analyzes physiological and clinical biomarkers to provide coronary artery disease likelihood information intended to inform clinical decisions, under EU MDR Rule 11 it would default to **Class IIa or higher**. The EU MDR contains **no non-device CDS exemption** equivalent to US law.

---

### 4.2 India: CDSCO Medical Device Software (MDSW) Guidance (July 2026)

#### Governing Legislation
**Medical Devices Rules, 2017 (MDR 2017)**, framed under Section 12 and Section 33 of the Drugs and Cosmetics Act, 1940 (23 of 1940), administered by the Central Drugs Standard Control Organisation (CDSCO), Directorate General of Health Services, Ministry of Health & Family Welfare, Government of India.

#### Current CDSCO Guidance Document
- **Document Title:** *Guidance Document on Medical Device Software (MDSW)*
- **Document Number:** **CDSCO/MD/GD/MDSW/01/2026**
- **Date of Publication:** **July 21, 2026** (following public stakeholder consultation on the draft issued October 21, 2025)
- **Issuing Body:** Medical Device Division, Central Drugs Standard Control Organisation (CDSCO), FDA Bhawan, New Delhi, India.

#### Regulatory Architecture under MDSW 2026
The CDSCO MDSW 2026 guidance regulates both **Software as a Medical Device (SaMD)** and **Software in a Medical Device (SiMD)** under MDR 2017:
1. **Risk-Based Classification Framework:** Software is classified into four risk classes (Class A, Class B, Class C, Class D) based on a two-dimensional matrix combining:
   - *State of Healthcare Situation:* Critical, Serious, or Non-serious.
   - *Significance of Information Provided:* To treat or diagnose, to drive clinical management, or to inform clinical management.
2. **Cardiovascular Risk Assessment Classification:** Software intended to inform clinical management or assist in risk stratification for serious conditions such as coronary artery disease is categorized under **Class B (low-moderate risk) or Class C (moderate-high risk)** depending on the autonomy of the recommendation and potential delay in definitive care.
3. **Statutory Obligations:** Requires manufacturing/import licensing via the CDSCO online portal (SUGAM), compliance with ISO 13485 quality management systems, verification of software lifecycle processes (IEC 62304), and clinical performance evaluation approved by the Central Licensing Authority (CLA).
4. **Absence of CDS Carve-Out:** Indian law contains **no statutory non-device exemption** for AI-based clinical decision support algorithms.

---

### 4.3 United States: FDA Section 520(o) & January 2026 CDS Guidance

#### Governing Framework
- **Statute:** Section 520(o)(1)(E) of the Federal Food, Drug, and Cosmetic Act (21 U.S.C. § 360j(o)(1)(E)), enacted via Section 3060 of the 21st Century Cures Act.
- **Guidance:** FDA CDRH Final Guidance: *Clinical Decision Support Software: Guidance for Industry and Food and Drug Administration Staff* (January 2026).

#### The Four Statutory Criteria
Software is excluded from device regulation if and only if it meets all four criteria:
1. Does not acquire/process/analyze medical images, signals from IVDs, or pattern recognition.
2. Intended for displaying, analyzing, or printing medical information.
3. Intended for supporting or providing recommendations to a **healthcare professional (HCP)**.
4. Intended to enable the HCP to **independently review the basis** for the recommendations.

#### Architectural Assessment
Because HeartXAI 2.0 incorporates patient-facing risk likelihood displays and counterfactual lifestyle simulations, it **fails Criterion 3 and Criterion 4**, indicating medical device classification (SaMD) if deployed commercially in the United States.

---

### 4.4 United Kingdom: MHRA Regulatory Framework

#### Governing Framework
- **Statute:** UK Medical Devices Regulations 2002 (SI 2002 No 618, as amended).
- **Agency:** Medicines and Healthcare products Regulatory Agency (MHRA).
- **Policy:** *Software and AI as a Medical Device Change Programme* (Work Package 1: Qualification, Work Package 2: Classification, Work Package 3: Premarket Requirements).

#### Architectural Assessment
Software intended to interpret physiological data to calculate disease likelihood falls under SaMD rules requiring **UKCA marking** (or recognized CE mark under extension provisions), classified under UK MDR Part II (Class IIa/IIb).

---

### 4.5 Mandatory Legal Disclaimer
> [!IMPORTANT]
> **MANDATORY LEGAL DISCLAIMER:**  
> The regulatory applicability of medical device legislation to HeartXAI 2.0 remains **strictly undetermined**. HeartXAI 2.0 makes NO claim of non-device status, statutory CDS exemption, or regulatory clearance in the United States, European Union, United Kingdom, or India.  
> All cross-jurisdictional analyses in HeartXAI 2.0 technical documentation represent architectural engineering risk evaluations only. **Definitive legal classification, regulatory strategy, and marketing authorization requirements require formal review and determination by qualified healthcare regulatory legal counsel in each respective target jurisdiction.**

---

## 5. Rigorous Calibration Validation Protocol

### 5.1 Leakage-Safe Out-of-Fold Probability Predictions
A critical vulnerability in machine learning calibration is evaluating models on in-sample training data or allowing calibration models to see validation/test labels during fitting.

HeartXAI 2.0 enforces a **strictly isolated nested cross-validation protocol** in Milestone 10:

```
+----------------------------------------------------------------------------------------------------+
|                         LEAKAGE-SAFE CALIBRATION VALIDATION WORKFLOW                               |
+----------------------------------------------------------------------------------------------------+
|                                  Full Ingested Dataset (N=303)                                     |
+-------------------------------------------------+--------------------------------------------------+
                                                  │
                                 Stratified 5-Fold Split (Leakage-Free)
                                                  │
                ┌─────────────────────────────────┴─────────────────────────────────┐
                ▼                                                                   ▼
       Training Folds (4/5, ~242 records)                              Validation Fold (1/5, ~61 records)
  ┌───────────────────────────────────────────────┐                   ┌───────────────────────────────┐
  │ 1. Train base XGBoost classifier              │                   │ Held completely untouched     │
  │    $f(\mathbf{x}) \to \text{raw log-odds}$    │                   │ during model & calibrator fit │
  │ 2. Generate internal OOF predictions or split │                   └───────────────┬───────────────┘
  │    training fold for calibration fitting      │                                   │
  │ 3. Fit Platt Scaler (logistic) or Isotonic    │                                   │
  │    regression ONLY on training predictions:   │                                   │
  │    $g: \text{raw} \to \hat{p}_{\text{cal}}    │                                   │
  └───────────────────────┬───────────────────────┘                                   │
                          │                                                           │
                          └───────────────────────┬───────────────────────────────────┘
                                                  ▼
                               Apply $f$ and $g$ to Validation Fold
                                                  │
                                                  ▼
                        Out-of-Fold (OOF) Calibrated Predictions ($\hat{p}_i$)
                                                  │
                                                  ▼
                       Compute Brier Score, ECE, Slope, Intercept, & CIs
```

### 5.2 Training-Only Fitting of Calibration Transformers
- **Platt Scaling (Logistic Calibration):**
  $$P(Y=1 \mid f(\mathbf{x})) = \frac{1}{1 + \exp(A \cdot f(\mathbf{x}) + B)}$$
  The scalar parameters $A$ and $B$ must be fitted **strictly on the training partition** of each cross-validation fold.
- **Isotonic Regression:**
  $$\min \sum_{i=1}^{N_{\text{train}}} (y_i - \hat{p}_i)^2 \quad \text{subject to } \hat{p}_i \le \hat{p}_j \text{ whenever } f(\mathbf{x}_i) \le f(\mathbf{x}_j)$$
  The non-parametric monotonic step function must be fitted **strictly on the training partition**. Fitting isotonic regression on the evaluation fold or full dataset constitutes catastrophic data leakage.

### 5.3 Confidence Intervals & Statistical Uncertainty
Because the Cleveland cohort is small ($N=303$), point estimates of calibration metrics are subject to high sampling variance. Milestone 10 mandates computing **95% bootstrap confidence intervals** across 1,000 stratified resamples for every reported calibration metric:

```
+----------------------------------------------------------------------------------------------------+
|                               CALIBRATION METRICS REPORTING FRAMEWORK                              |
+-----------------------+------------------------+-------------------+-------------------------------+
| Calibration Metric    | Mathematical Target    | Evaluation Mode   | Statistical Uncertainty Gate  |
+-----------------------+------------------------+-------------------+-------------------------------+
| **Brier Score**       | $\le 0.12$ (Heuristic) | Out-of-Fold (OOF) | 95% Bootstrap CI must be      |
|                       | (Baseline: $0.2483$)   | Predictions       | reported: $[\text{BS}_{0.025}, \text{BS}_{0.975}]$. |
+-----------------------+------------------------+-------------------+-------------------------------+
| **Expected Calibration| $\le 0.05$ (Heuristic) | Out-of-Fold (OOF) | 95% Bootstrap CI must be      |
| Error (ECE)**         | ($M=10$ bins)          | Predictions       | reported: $[\text{ECE}_{0.025}, \text{ECE}_{0.975}]$.|
+-----------------------+------------------------+-------------------+-------------------------------+
| **Calibration Slope** | $\beta = 1.0$ (Ideal)  | Logistic Recalib- | 95% CI reported; evaluates    |
|                       |                        | ration on Logits  | under/over-confidence spread. |
+-----------------------+------------------------+-------------------+-------------------------------+
| **Calibration Inter-  | $\alpha = 0.0$ (Ideal) | Calibration-in-   | 95% CI reported; evaluates    |
| cept**                |                        | the-Large         | systematic over/under-predict.|
+-----------------------+------------------------+-------------------+-------------------------------+
```

### 5.4 External Validation Prerequisite
Internal cross-validation (even with strict leakage-safe OOF predictions) cannot establish generalizable clinical validity due to regional and historical referral bias at the Cleveland Clinic (1981–1984).
> **METHODOLOGICAL REQUIREMENT:** **External validation on an independent clinical cohort is strictly required before making any clinical calibration claim.** Internal cross-validation performance must be reported strictly as *cross-validated retrospective dataset performance*.

### 5.5 Exploratory Status of Decision Curve Analysis (DCA)
Decision Curve Analysis (Vickers & Elkin, 2006) evaluates the clinical net benefit of a predictive model:

$$\text{Net Benefit}(p_t) = \frac{\text{True Positives}}{N} - \frac{\text{False Positives}}{N} \left( \frac{p_t}{1 - p_t} \right)$$

where $p_t$ represents the clinical threshold probability at which a clinician or patient would opt for an actionable clinical intervention (e.g., invasive angiography vs. outpatient stress test).

- **Exploratory Designation:** In the absence of a prospectively defined clinical pathway with agreed-upon harm-to-benefit weighting for false positives vs. false negatives, **Decision Curve Analysis (DCA) is formally classified as EXPLORATORY**.
- **Conditions for Clinical DCA:** DCA may only be upgraded to a validated decision tool when an explicit clinical decision context (e.g., referral for coronary CT angiography) and a justified threshold probability range ($p_t \in [0.15, 0.35]$) are clinically specified and approved by the Physician Advisory Review board.

---

## 6. Governance Decision Register (All Pending Decision)

In accordance with strict project governance invariants, **all five strategic decisions remain PENDING USER DECISION**:

```
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| ID      | Decision Description     | Available Options     | Recommended Option      | Selection Rationale| Dependencies  | Status    |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Hosting Profile &      | A: Tier A Minimal VPS | **Option A: Tier A      | Lowest cost; no    | Milestone 01, | **PENDING |
| 001**   | Infrastructure Budget**  |    (~$25-$55/mo)      | Minimal VPS**           | vendor lock-in;    | Milestone 20  | USER      |
|         |                          | B: Tier B AWS Cloud   |                         | capacity estimate. |               | DECISION**|
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Clinical Governance    | A: Multi-Track Phased | **Option A: Multi-    | Establishes distinct    | Requires strict    | Milestones    | **PENDING |
| 002**   | Implementation Scope**   |    Governance (MVP     | Track Phased          | physician and content   | enforcement of     | 08, 14, 16    | USER      |
|         | (4 Distinct Tracks)      |    Advisory/Content;   | Governance**          | review in MVP; ethics/  | prohibited clinical|               | DECISION**|
|         |                          |    Ethics/Reg in par.) |                       | regulatory determ-      | claims ledger;     |               |           |
|         |                          | B: Upfront Inst. Gate |                       | ination gate before     | Cat C prohibited.  |               |           |
|         |                          |    (pre-dev IRB/Q-Sub) |                       | human-participant study.|                    |               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Cardiovascular         | A: Task A MVP only    | **Option A: Task A      | Preserves clinical | Milestones    | **PENDING |
| 003**   | Prediction Scope**       | B: Implement Task B   | MVP Only**              | integrity; PREVENT | 09, 10, 11,   | USER      |
|         |                          |    calculator in MVP  |                         | 2026 noted; B out. | 14            | DECISION**|
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Geographic Adapter     | A: Adapter Pattern as | **Option A: Adapter   | Proves architectural    | Operational and    | Milestones    | **PENDING |
| 004**   | Extensibility Goal &     |    Extensibility Goal | Pattern Extensibility | decoupling for units    | regulatory readiness| 08, 15       | USER      |
|         | Localization Scope**     |    (US/IN/UK Synth)   | Goal (US/IN/UK Synth)*| without claiming global | must be verified per|              | DECISION**|
|         |                          | B: US-Only Baseline   |                       | operational readiness.  | jurisdiction.      |               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Data Classification &  | A: Three-Tier Class-  | **Option A: Three-    | Prohibits Category C in | Cat A carries      | All           | **PENDING |
| 005**   | Patient Data Policy**    |    ification (Cat A/B;| Tier Classification   | MVP; separates Cat A    | historical research| Milestones    | USER      |
|         |                          |    Cat C Prohibited)  | (Cat C Prohibited)**  | human research risk from| risks; Cat B synth | (01–20)       | DECISION**|
|         |                          | B: Real PHI Pilot     |                       | Cat B synthetic data;   | requires AppSec;   |               |           |
|         |                          |                       |                       | mandates M09 review.    | cyber risks managed|               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
```

---

## 7. Master Pre-Implementation Authorization Checklist

Before Milestone 01 engineering can be initiated:
1. Provide your selections for decisions **DEC-001 through DEC-005** (e.g., *"Approve Recommendations: 1A, 2A, 3A, 4A, 5A"* or state custom choices).
2. Authorize commencement of **Milestone 01: Repository & Development Environment Foundation**.
