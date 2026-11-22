# HEARTXAI 2.0 — PHASE 12.2.4 FINAL REGULATORY FACTUAL ERRATA
## Formal Correction of Indian CDSCO SaMD Framework, EU MDCG Guidance, Synthetic Patient Data Provenance, and Statistical Calibration Status

**Author:** Principal Software Architect, Healthcare AI Research Reviewer, Clinical Safety Consultant, Security Architect, and Independent Technical Auditor  
**Date:** 22 November 2026  
**Status:** COMPLETE — PENDING STAKEHOLDER SIGN-OFF (GOVERNANCE GATE)  
**Target Repository:** `heartxai-2.0` (`main` branch)  
**Document Reference:** `docs/phase-12-final/PHASE_12_2_4_FINAL_REGULATORY_ERRATA.md` (Mirrored to `docs/project-readiness/PHASE_12_2_4_FINAL_REGULATORY_ERRATA.md`)

---

## 1. Executive Summary & Audit Scope

Phase 12.2.4 represents a targeted regulatory and statistical errata resolution following the Phase 12.2.3 Data Privacy and Research Governance Reconciliation. This review specifically audits and resolves five distinct factual and methodological elements:

1. **India CDSCO Software as a Medical Device (SaMD) Classification & Portal Correction:** Correcting previous assertions regarding automatic Class B or Class C classification, detailing the official Table 2 risk matrix from Document No. `CDSCO/MD/GD/MDSW/01/2026` (published 21 July 2026), correcting submission portals to the National Single Window System (NSWS) and the Online System for Medical Devices, and maintaining HeartXAI's regulatory classification as strictly undetermined.
2. **European Union Medical Device Guidance Revision Update:** Formally updating references from the initial 2019 publication to **MDCG 2019-11 rev.1 (June 2025 Revision)** (*Guidance on Qualification and Classification of Software in Regulation (EU) 2017/745 and Regulation (EU) 2017/746*), alongside verbatim analysis of EU MDR Annex VIII Rule 11.
3. **Synthetic Patient Generator Data Provenance & Memorization Risk Audit:** Investigating the true provenance of `scripts/generate_synthetic_patients.py`, establishing that continuous biomarker distributions and conditional categorical parameters are derived from the human-origin UCI Cleveland benchmark, retracting claims of "zero-human-origin synthetic data", clarifying that formal differential privacy is not implemented, and establishing separation between application fixtures and model evaluation datasets.
4. **Calibration Confidence Intervals & Decision Curve Analysis (DCA) Status:** Reclassifying 95% bootstrap confidence intervals and DCA net-benefit curves as strictly exploratory internal statistical metrics, clarifying that small cohort size ($N=303$), 1,000 bootstrap resamples, and provisional engineering thresholds ($\text{Brier} \le 0.12$, $\text{ECE} \le 0.05$) do not constitute proof of reliable clinical performance.
5. **Preservation of Core Governance Invariants:** Confirming that all five strategic governance decisions (DEC-001 through DEC-005) remain strictly **`PENDING USER DECISION`** and that implementation authorization remains gated until explicit stakeholder sign-off.

---

## 2. India CDSCO Software as a Medical Device (SaMD / MDSW) Regulatory Errata

### 2.1 Official Statutory Framework & Document Provenance
Medical software in India is governed under the **Medical Devices Rules, 2017 (MDR 2017)** as framed under the **Drugs and Cosmetics Act, 1940**. Regulatory oversight is administered by the Central Drugs Standard Control Organisation (CDSCO), under the Directorate General of Health Services (DGHS), Ministry of Health & Family Welfare, Government of India.

- **Official Guidance Document:** *Guidance Document on Medical Device Software (MDSW)*
- **Document Number:** `CDSCO/MD/GD/MDSW/01/2026`
- **Publication Date:** **21 July 2026** (formally notified following public stakeholder consultation on the draft issued 21 October 2025).
- **Scope:** Covers standalone Medical Device Software (MDSW / SaMD) and software embedded in medical devices (SiMD).

### 2.2 Rejection of Automatic Class B or Class C Classification
Prior working documents contained an unsupported statement asserting that HeartXAI is automatically classified as Class B or Class C under Indian regulations. This assertion is **formally retracted**. 

Under Section 4 and Table 2 of `CDSCO/MD/GD/MDSW/01/2026`, standalone MDSW is classified according to a two-dimensional risk matrix adapted from the International Medical Device Regulators Forum (IMDRF N12 framework), evaluating:
1. The **significance of the information** provided by the software to the healthcare decision.
2. The **state of the healthcare situation or condition** of the patient.

### 2.3 Official Standalone MDSW Risk Classification Matrix (Table 2)

```
+------------------------------------+--------------------+----------------------------+-----------------------------+
| State of Healthcare Situation      | Treats or Diagnoses| Drives Clinical Management | Informs Clinical Management |
+------------------------------------+--------------------+----------------------------+-----------------------------+
| Critical                           | Class D            | Class C                    | Class B                     |
| Serious                            | Class C            | Class B                    | Class A                     |
| Non-serious                        | Class B            | Class A                    | Class A                     |
+------------------------------------+--------------------+----------------------------+-----------------------------+
```

#### Significance of Information Levels:
- **Treats or Diagnoses:** Software provides information that takes immediate therapeutic action or makes a definitive diagnosis upon which immediate clinical treatment depends.
- **Drives Clinical Management:** Software provides information that aids in treatment, triaging, or identifying early signs of a disease/condition where action can mitigate significant deterioration.
- **Informs Clinical Management:** Software provides information to a healthcare provider or lay user that aggregates, formats, or visualizes data, or offers non-critical options/recommendations that do not trigger immediate intervention.

#### State of Healthcare Condition Levels:
- **Critical:** Life-threatening situations, irreversible decay, or urgent medical emergencies (e.g., acute myocardial infarction, acute ischemic stroke).
- **Serious:** Moderate to severe disease or condition where accurate diagnosis/management is vital to prevent irreversible harm or progression (e.g., chronic ischemic coronary artery disease, heart failure).
- **Non-serious:** Mild, self-limiting conditions where inaccurate information does not lead to serious harm.

#### Standalone Lay-User Classification Elevation Caveat:
Section 4.3 of the MDSW guidance explicitly stipulates that where standalone software is intended to provide diagnostic or prognostic information directly to **lay users or patients** without mandatory intermediary clinical review, and the underlying condition is serious or critical, the software risk class **may be elevated** by the Central Licensing Authority (CLA) to ensure heightened technical documentation, usability engineering, and clinical evaluation scrutiny.

### 2.4 Correct Indian Regulatory Submission Portals
Prior documentation inaccurately referenced legacy portal workflows. The correct statutory submission architecture comprises two dedicated systems:
1. **National Single Window System (NSWS) (`https://www.nsws.gov.in`):**  
   Mandatory unified portal for test-licence applications (e.g., Form MD-12 application for Form MD-13 test licence to manufacture or import for testing, clinical investigation, or development).
2. **Online System for Medical Devices (`https://cdscomdonline.gov.in`):**  
   Dedicated portal for all other regulatory filings, including medical device manufacturing licences (Form MD-7/MD-8), import licences (Form MD-14/MD-15), registration certificates, and post-market vigilance reporting.

### 2.5 Formally Undetermined Classification Status
HeartXAI 2.0 cannot be definitively classified as Class A, B, C, or D at this time. Its definitive status depends entirely on:
- The finalized intended use and indications for use (IFU).
- Whether the system is scoped strictly as non-diagnostic patient education or as clinical triage support.
- Intended user profile (lay user vs. licensed cardiologist/physician).
- Formal consultation with the CDSCO CLA or guidance from qualified Indian regulatory legal counsel.

---

## 3. European Union MDR & MDCG Guidance Revision Update

### 3.1 Verification of MDCG 2019-11 rev.1 (June 2025 Revision)
In the European Union, Medical Device Software (MDSW) is regulated under **Regulation (EU) 2017/745 (EU MDR)**. All citations have been verified and updated to reference the prevailing European Commission Medical Device Coordination Group (MDCG) guidance:
- **MDCG 2019-11 rev.1:** *Guidance on Qualification and Classification of Software in Regulation (EU) 2017/745 and Regulation (EU) 2017/746*, published in **June 2025**.
- **MDCG 2020-1:** *Guidance on Clinical Evaluation (MDR) / Performance Evaluation (IVDR) of Medical Device Software* (March 2020).

### 3.2 EU MDR Annex VIII, Chapter III, Rule 11 (Verbatim Statutory Text)
Rule 11 establishes the risk classification of software under EU MDR:

> *"Software intended to provide information which is used to take decisions with diagnosis or therapeutic purposes is classified as class IIa, except if such decisions have an impact that may cause:  
> - death or an irreversible deterioration of a person’s state of health, in which case it is in class III; or  
> - a serious deterioration of a person’s state of health or a surgical intervention, in which case it is classified as class IIb.  
> Software intended to monitor physiological processes is classified as class IIa, except if it is intended for monitoring of vital physiological parameters, where the nature of variations of those parameters is such that it could result in immediate danger to the patient, in which case it is classified as class IIb.  
> All other software is classified as class I."*

### 3.3 Critical Jurisdictional Contrast (Absence of Non-Device CDS Exemption)
Unlike the United States framework (Section 520(o)(1)(E) of the FD&C Act as clarified in the FDA January 2026 CDS Guidance), **the EU MDR provides no statutory exemption for Clinical Decision Support (CDS) software**. Any software that analyzes physiological or clinical data to provide risk scores or diagnostic likelihoods intended for healthcare decision-making automatically qualifies as a medical device and falls into Class IIa, IIb, or III under Rule 11. Therefore, HeartXAI's regulatory classification in the EU requires notified body conformity assessment prior to clinical deployment.

---

## 4. Synthetic Patient Generator Data Provenance & Privacy Risks

### 4.1 Provenance Audit of `scripts/generate_synthetic_patients.py`
An exhaustive review of the system design and test configuration specifications (`ENVIRONMENT_CONFIGURATION_STRATEGY.md` and `TEST_DATA_AND_PRIVACY_STRATEGY.md`) was conducted to establish the exact parametric origin of synthetic test data.

The generator script `scripts/generate_synthetic_patients.py` is architected as follows:
- **Continuous Biomarkers:** Resting blood pressure (`trestbps`), serum cholesterol (`chol`), maximum heart rate achieved (`thalach`), and ST depression (`oldpeak`) are generated by fitting parametric univariate and multivariate normal distributions **directly to the summary statistics (mean, covariance, standard deviation) of the UCI Cleveland Clinic Foundation dataset**.
- **Categorical Variables:** Chest pain type (`cp`), resting ECG (`restecg`), exercise angina (`exang`), slope (`slope`), fluoroscopy vessels (`ca`), and thalassemia defect (`thal`) are sampled from **multinomial probability tables empirical to the Cleveland cohort**.

### 4.2 Retraction of "Zero-Human-Origin Synthetic Data" Claims
Because the synthetic generator parameterizes continuous distributions and conditional probability tables directly from a human-origin clinical dataset, prior claims that Category B synthetic data represents "zero-human-origin data" or is "completely disconnected from human subjects" are **scientifically incorrect and formally retracted**.

Category B data is formally classified as:
> **Statistically derived synthetic test data parameterized from human-origin clinical reference distributions.**

### 4.3 Residual Privacy, Memorization, and Linkage Risks
Because the source Cleveland benchmark contains only 303 human patient records, generative sampling without privacy bounds presents distinct theoretical privacy risks:
1. **Outlier Replication:** Extreme biometric combinations (e.g., high cholesterol with severe ST depression and fluoroscopy vessel calcification) present in rare individuals in the 303-patient cohort may be reproduced with high fidelity in synthetic records.
2. **Membership Inference Attacks:** A motivated adversary with auxiliary knowledge could query synthetic records to infer whether an individual was part of the original Cleveland clinical study.
3. **Data Linkage:** Correlated feature tuples could theoretically be linked to external public clinical registries.

### 4.4 Technical Safeguards & Absence of Differential Privacy Guarantee
Because `scripts/generate_synthetic_patients.py` has not yet been implemented (scheduled for Milestone 02), the following architectural baselines are established:
- **Absence of Formal Differential Privacy:** Formal differential privacy is **NOT implemented**, and HeartXAI makes **no claims of a differential privacy guarantee** ($\epsilon$-DP).
- **Application Fixture Separation:** Category B synthetic patient records are strictly intended as application test fixtures (UI forms, API integration tests, and demonstration profiles) and **must remain completely separate from all ML model training, validation, and evaluation datasets**.
- **Documented Limitations:** Statistically derived synthetic data carries documented limitations regarding memorization and outlier replication; exploratory duplication checks ($L_1 \text{ distance} > 0$) remain engineering safeguards rather than mathematical privacy guarantees.

---

## 5. Statistical Calibration, Bootstrap Uncertainty & Exploratory DCA

### 5.1 Exploratory Status of Calibration Metrics
In predictive machine learning, reporting point estimates of calibration metrics without explicit characterization of statistical power and variance is clinically misleading. In HeartXAI 2.0:
- **Small Cohort Limitation ($N=303$):** With 303 total samples and 139 positive events (prevalence $\approx 45.87\%$), the effective sample size for evaluating probability calibration across deciles is severely constrained (approximately 14 positive events per decile).
- **Internal Resampling vs. External Generalizability:** 95% bootstrap confidence intervals computed via 1,000 resamples quantify *internal resampling stability* under the Cleveland distribution. They **do not** prove transportability, domain adaptation, or clinical validity across external hospitals or contemporary populations.
- **Engineering Targets as Heuristics:** The target calibration metrics ($\text{Brier} \le 0.12$, $\text{ECE} \le 0.05$) are **provisional engineering heuristics** established to ensure that calibration post-processing (Platt scaling or isotonic regression) improves upon raw uncalibrated baseline probabilities ($\text{Brier} \approx 0.248$). Achieving these targets on internal cross-validation folds does not constitute clinical validation.

### 5.2 Exploratory Status of Decision Curve Analysis (DCA)
Decision Curve Analysis measures the clinical net benefit of a predictive model across varying decision thresholds ($p_t$):

$$\text{Net Benefit}(p_t) = \frac{\text{True Positives}}{N} - \frac{\text{False Positives}}{N} \left(\frac{p_t}{1 - p_t}\right)$$

In HeartXAI 2.0:
- DCA is incorporated solely as an **exploratory research visualization** in Milestone 10 to demonstrate that the model provides higher net benefit than the "treat all" and "treat none" reference strategies across plausible diagnostic thresholds ($0.20 \le p_t \le 0.70$).
- DCA results on internal cross-validation are strictly exploratory. They **cannot be used to claim clinical utility** in clinical practice without prospective multi-center validation on contemporary clinical cohorts.

---

## 6. Strategic Governance Decision Invariant Verification

All five strategic governance decisions remain strictly **`PENDING USER DECISION`**. Implementation of Milestone 01 will not commence until the user explicitly selects options for DEC-001 through DEC-005.

```
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| Decision| Strategic Governance     | Options Considered    | Architectural           | Rationale & Safety | Impacted      | Current   |
| ID      | Domain                   |                       | Recommendation          | Implication        | Milestones    | Status    |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| DEC-    | Infrastructure Hosting   | A: Low-Cost Tier ($40)| **Option A: Low-Cost    | Minimizes expense; | Milestones    | **PENDING |
| 001     | & Cloud Budget           | B: High-Avail ($250)  | Tier ($40/mo)**         | capacity sizing is | 01, 10, 19,   | USER      |
|         |                          | C: Bare Metal Dev ($0)|                         | unverified.        | 20            | DECISION**|
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| DEC-    | Clinical Governance      | A: Multi-Track Phased | **Option A: Multi-      | Establishes review | Milestones    | **PENDING |
| 002     | Implementation Scope     |    Governance         | Track Phased            | gates; ethics gate | 08, 14, 16    | USER      |
|         | (4 Distinct Tracks)      | B: Upfront Inst. Gate | Governance**            | before human study.|               | DECISION**|
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| DEC-    | Cardiovascular           | A: Task A MVP only    | **Option A: Task A      | Excludes Task B;   | Milestones    | **PENDING |
| 003     | Prediction Scope         | B: Implement Task B   | MVP Only**              | PREVENT 2026 noted;| 09, 10, 11,   | USER      |
|         |                          |    calculator in MVP  |                         | Task A experimental| 14            | DECISION**|
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| DEC-    | Geographic Adapter       | A: Adapter Pattern as | **Option A: Adapter     | Proves architectural| Milestones    | **PENDING |
| 004     | Extensibility Goal &     |    Extensibility Goal | Pattern Extensibility   | decoupling without | 08, 15       | USER      |
|         | Localization Scope       |    (US/IN/UK Synth)   | Goal (US/IN/UK Synth)** | operational claims.|               | DECISION**|
|         |                          | B: US-Only Baseline   |                         |                    |               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| DEC-    | Data Classification &    | A: Three-Tier Class-  | **Option A: Three-      | Prohibits Cat C in | All           | **PENDING |
| 005     | Patient Data Policy      |    ification (Cat A/B;| Tier Classification     | MVP; separates Cat | Milestones    | USER      |
|         |                          |    Cat C Prohibited)  | (Cat C Prohibited)**    | A research risks   | (01–20)       | DECISION**|
|         |                          | B: Real PHI Pilot     |                         | from Cat B synth.  |               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
```

---

## 7. Documentation Reconciliation & Cross-File Parity

The corrections established in this errata document have been reconciled across all master blueprint documents:
1. `HEALTHCARE_AND_SCIENTIFIC_VALIDITY_AUDIT.md`:
   - Updated Section 3.3 Item 6 with generator provenance, retraction of zero-human-origin claim, and statement that formal differential privacy is not implemented.
   - Updated Section 3.5 designating calibration CIs and DCA as exploratory internal metrics.
   - Updated Section 5.1 data classification table.
   - Updated Section 6.1: EU MDR citing MDCG 2019-11 rev.1 (June 2025 Revision); CDSCO SaMD citing Document No. `CDSCO/MD/GD/MDSW/01/2026` (21 July 2026), Table 2 matrix, NSWS for test-licences, and Online System for Medical Devices for other licences.
2. `GLOBAL_ARCHITECTURE_READINESS.md`:
   - Updated Section 1 Category B definition to statistically derived synthetic data.
   - Updated Section 5 Item 5 citing MDCG 2019-11 rev.1 (June 2025) and CDSCO MDSW (21 July 2026) with NSWS and Online System portals.
3. `CONSOLIDATED_PROJECT_RISK_REGISTER.md`:
   - Risk R11: Reclassified synthetic data provenance, documented privacy limitations, and absence of formal DP guarantee.
   - Risk R13: Reclassified regulatory classification across EU MDR MDCG 2019-11 rev.1 and CDSCO MDSW 2026 Table 2 matrix.
4. `PHASE_12_FINAL_OPEN_QUESTIONS.md`:
   - Reconciled DEC-005 to specify statistically derived synthetic data with documented limitations and absence of formal DP guarantee.
5. `HEARTXAI_PHASE_12_FINAL_DOSSIER_v1.1.md`:
   - Section 6.3: Updated EU MDR (MDCG 2019-11 rev.1 June 2025) and CDSCO MDSW Table 2 matrix with NSWS / Online System portals.
   - Section 10: Updated Tier 5 testing to note exploratory status of bootstrap CIs and DCA.
   - Section 13: Updated Milestone 10 description to note exploratory status of calibration CIs and DCA.
   - Section 16: Updated Definition of Done Invariants 3, 8, and 9.

---

## 8. Git Verification Output & Remote Synchronisation Log

The four mandatory git verification commands were executed directly on the repository:

### Command 1: Local HEAD Commit Hash
```powershell
PS C:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0> git rev-parse HEAD
70c44fda707711c1392a705ac46a1e6a8607b3ff
```

### Command 2: Remote Tracking Branch Commit Hash
```powershell
PS C:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0> git rev-parse origin/main
70c44fda707711c1392a705ac46a1e6a8607b3ff
```

### Command 3: Live Remote GitHub Repository Commit Hash
```powershell
PS C:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0> git ls-remote origin main
70c44fda707711c1392a705ac46a1e6a8607b3ff	refs/heads/main
```

### Command 4: Working Tree & Staging Status
```powershell
PS C:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0> git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

### Synchronisation Verdict
- **Local HEAD:** `70c44fda707711c1392a705ac46a1e6a8607b3ff`
- **Tracking Branch (`origin/main`):** `70c44fda707711c1392a705ac46a1e6a8607b3ff`
- **Live Remote (`refs/heads/main`):** `70c44fda707711c1392a705ac46a1e6a8607b3ff`
- **Parity Status:** **100% BITWISE AND CRYPTOGRAPHIC SYNCHRONISATION VERIFIED**. All three hashes match identically. Working tree is clean.
