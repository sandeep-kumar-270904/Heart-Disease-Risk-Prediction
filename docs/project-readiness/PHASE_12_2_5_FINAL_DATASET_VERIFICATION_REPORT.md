# HEARTXAI 2.0 — PHASE 12.2.5 FINAL DATASET, SYNTHETIC DATA & GIT EVIDENCE VERIFICATION REPORT

**Author:** Principal Software Architect, Healthcare AI Research Reviewer, Clinical Safety Consultant, Security Architect & Independent Technical Auditor  
**Date:** 22 November 2026  
**Status:** COMPLETE — STRICTLY GATED PENDING USER GOVERNANCE SELECTIONS (DEC-001 THROUGH DEC-005)  
**Target Repository:** `heartxai-2.0` (`main` branch)  
**Document Reference:** `docs/phase-12-final/PHASE_12_2_5_FINAL_DATASET_VERIFICATION_REPORT.md` (Mirrored to `docs/project-readiness/PHASE_12_2_5_FINAL_DATASET_VERIFICATION_REPORT.md`)

---

## 1. Executive Summary & Verification Scope

Phase 12.2.5 executes a rigorous, empirical verification of the dataset, synthetic patient generator architecture, regulatory portal terminology, and Git synchronization status for HeartXAI 2.0. Rather than relying on previous audit summaries or secondary literature, this phase independently evaluates the underlying data artifacts, codebases, and statutory portals against four strict criteria:

1. **Empirical Dataset Verification:** Programmatic parsing and statistical profiling of the exact 14-attribute UCI Cleveland Clinic Foundation dataset (`processed.cleveland.data`), resolving the discrepancy between 138 and 139 positive events, and establishing mathematically exact null-model Brier scores.
2. **Synthetic Patient Generator Audit:** Verification of `scripts/generate_synthetic_patients.py`, establishing its implementation status, confirming the total absence of formal differential privacy mechanisms, retracting differential privacy claims, and enforcing strict separation between synthetic application fixtures and ML evaluation datasets.
3. **Regulatory Portal Terminology Rectification:** Verifying the official administrative names of the Indian CDSCO medical device submission portals, removing informal references to "SUGAM", and maintaining HeartXAI's regulatory classification as strictly undetermined.
4. **Live Cryptographic Git Verification:** Execution of all mandatory Git verification commands (`git rev-parse HEAD`, `git rev-parse origin/main`, `git ls-remote origin main`, and `git status`), reporting live output and verifying cryptographic parity.

---

## 2. Empirical Dataset Verification & Target Event Resolution

### 2.1 Dataset Profile & Attribute Architecture
The project targets the historical 14-attribute Cleveland Clinic Foundation dataset (`processed.cleveland.data`), contributed to the UCI Machine Learning Repository in 1988 by Dr. Robert Detrano and David Aha:
- **Feature Set:** 13 clinical biomarkers (`age`, `sex`, `cp`, `trestbps`, `chol`, `fbs`, `restecg`, `thalach`, `exang`, `oldpeak`, `slope`, `ca`, `thal`).
- **Target Variable (`num`):** Angiographic coronary artery disease severity (diameter stenosis in major coronary vessels).

### 2.2 Empirical Statistical Findings (Direct Python Execution Output)

The following verification script was executed directly on `processed.cleveland.data`:

```python
import pandas as pd
import numpy as np

col_names = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
    'restecg', 'thalach', 'exang', 'oldpeak', 'slope',
    'ca', 'thal', 'num'
]

raw_df = pd.read_csv('processed.cleveland.data', header=None, names=col_names, na_values='?')
```

#### Verbatim Programmatic Output:
```text
=== 1. ORIGINAL RECORD COUNT ===
Total raw rows: 303

=== 2. TARGET VALUE COUNTS (num = 0, 1, 2, 3, 4) in RAW DATA ===
num = 0: 164 (54.13%)
num = 1: 55 (18.15%)
num = 2: 36 (11.88%)
num = 3: 35 (11.55%)
num = 4: 13 (4.29%)

=== 3. BINARY COUNTS (Raw Data: num == 0 vs num >= 1) ===
Negative (num = 0): 164 (54.13%)
Positive (num >= 1): 139 (45.87%)

=== 4. MISSING VALUE AUDIT ===
Columns with missing values:
  ca: 4 missing
  thal: 2 missing
Total rows with any missing value: 6

Details of rows with missing values (1-based index):
Row 88: age=53.0, sex=0.0, cp=3.0, ca=0.0, thal=nan, num=0
Row 167: age=52.0, sex=1.0, cp=3.0, ca=nan, thal=3.0, num=0
Row 193: age=43.0, sex=1.0, cp=4.0, ca=nan, thal=7.0, num=1
Row 267: age=52.0, sex=1.0, cp=4.0, ca=0.0, thal=nan, num=2
Row 288: age=58.0, sex=1.0, cp=2.0, ca=nan, thal=7.0, num=0
Row 303: age=38.0, sex=1.0, cp=3.0, ca=nan, thal=3.0, num=0

=== 5. PREPROCESSING ANALYSIS ===
--- Cohort 1: Complete-Case Analysis (Drop rows with missing values, N=297) ---
Final Sample Count: 297
Negative (num = 0): 160 (53.8721%)
Positive (num >= 1): 137 (46.1279%)
Positive Prevalence (pi): 0.461279 (46.13%)
Null-Model Brier Score (pi * (1 - pi)): 0.248501

--- Cohort 2: Imputed Cohort (Retain N=303 as per project docs) ---
Final Sample Count: 303
Negative (num = 0): 164 (54.1254%)
Positive (num >= 1): 139 (45.8746%)
Positive Prevalence (pi): 0.458746 (45.87%)
Null-Model Brier Score (pi * (1 - pi)): 0.248298

=== 6. RESOLUTION OF 138 vs 139 DISCREPANCY ===
Positives in missing rows: 2
Negatives in missing rows: 4
Complete-case positives: 137
Imputed cohort positives: 139
```

### 2.3 Comprehensive Data Profile Summary Table

| Metric | Complete-Case Cohort ($N=297$) | Imputed Full Cohort ($N=303$) | Project Policy / Interpretation |
| :--- | :---: | :---: | :--- |
| **Original Raw Records** | 303 | 303 | Primary UCI benchmark file. |
| **Missing Values** | 6 entries dropped (across 6 rows) | 6 entries imputed (median/mode) | `ca`: 4 missing; `thal`: 2 missing. |
| **Final Sample Count** | **297** | **303** | $N=303$ is the documented MVP baseline. |
| **`num = 0` (Negative)** | 160 (53.87%) | 164 (54.13%) | Absence of significant stenosis ($<50\%$). |
| **`num = 1`** | 54 (18.18%) | 55 (18.15%) | 1-vessel disease ($\ge 50\%$). |
| **`num = 2`** | 35 (11.78%) | 36 (11.88%) | 2-vessel disease ($\ge 50\%$). |
| **`num = 3`** | 35 (11.78%) | 35 (11.55%) | 3-vessel disease ($\ge 50\%$). |
| **`num = 4`** | 13 (4.38%) | 13 (4.29%) | Left main / multi-vessel disease ($\ge 50\%$). |
| **Binary Negative ($y=0$)** | **160** | **164** | $num = 0$ |
| **Binary Positive ($y=1$)** | **137** | **139** | $num \in \{1, 2, 3, 4\}$ |
| **Positive Prevalence ($\pi$)** | **0.461279 (46.13%)** | **0.458746 (45.87%)** | $\pi = N_{\text{pos}} / N$ |
| **Null-Model Brier Score** | **0.248501** | **0.248298** | $\text{BS}_{\text{null}} = \pi(1 - \pi)$ |

### 2.4 Definitive Resolution of the 138 vs 139 Discrepancy
- **Mathematical Fact:** In the raw 303-patient Cleveland cohort, there are exactly **164 negative cases** ($num = 0$) and **139 positive cases** ($num \ge 1$), calculated as:
  $$55 + 36 + 35 + 13 = 139$$
- **Missing Value Impact:** Among the 6 rows containing missing values, 4 rows have $num = 0$ and 2 rows have $num > 0$ (Row 193 has $num = 1$; Row 267 has $num = 2$). If complete-case analysis is performed, the positive count drops to **137**.
- **Source of "138":** Neither the raw cohort ($N=303$, 139 positives) nor the complete-case cohort ($N=297$, 137 positives) contains 138 events. The number 138 was an isolated typographical and rounding erratum introduced in the Phase 12.2.4 text ($303 \times 0.455 \approx 138$). All core Phase 8 and Phase 11 ML blueprints (`DATASET_DATA_DICTIONARY.md`, `DATASET_RESEARCH_AND_COMPARISON.md`, `DATA_QUALITY_AND_BIAS_ASSESSMENT.md`, `MASTER_IMPLEMENTATION_ROADMAP.md`, `PHASE_12_2_1_FINAL_VERIFICATION_REPORT.md`) consistently documented **139 positive cases** ($45.87\%$).
- **Authoritative Resolution:** The authoritative, verified baseline for the $N=303$ Cleveland cohort is **139 positive events ($45.87\%$)**, yielding an exact null-model Brier score of **$0.248298$**.

---

## 3. Synthetic Generator Verification & Privacy Status

### 3.1 Implementation Status in Repository
An exhaustive inspection of the repository confirms that:
- **File Status:** `scripts/generate_synthetic_patients.py` **does not yet exist in the codebase**.
- **Roadmap Alignment:** As established in `MASTER_IMPLEMENTATION_ROADMAP.md:68` and `HEARTXAI_PHASE_12_FINAL_DOSSIER_v1.1.md:249`, the synthetic generator is an explicit **Milestone 02 deliverable** (`Milestone 02: Core Scaffolding, Types & Synthetic Generator`). Because the project is currently in the pre-implementation audit phase, no synthetic generator script has been executed or committed to application code.

### 3.2 Parametric Derivation & Absence of Record Copying
- **Intended Parametric Source:** Specifications (`ENVIRONMENT_CONFIGURATION_STRATEGY.md`, `TEST_DATA_AND_PRIVACY_STRATEGY.md`) state that `scripts/generate_synthetic_patients.py` will fit continuous parametric univariate and multivariate normal distributions (mean, covariance, standard deviation) and empirical multinomial probability tables to the summary statistics of the UCI Cleveland benchmark.
- **No Row Copying:** The architecture prohibits verbatim copying or duplication of historical patient records.

### 3.3 Explicit Retraction of Differential Privacy Claims
- **Absence of DP Mechanism:** There is **no complete, tested differential privacy mechanism** implemented in the codebase.
- **Formal Retraction:** HeartXAI **explicitly retracts all claims that the generator provides a differential privacy guarantee ($\epsilon, \delta$-DP)**. Simply documenting theoretical privacy parameters or verifying that generated records differ from training rows does not constitute mathematical differential privacy.
- **Formal Classification:** Category B data is classified strictly as **statistically derived synthetic application test data with documented privacy limitations** (specifically, potential memorization and outlier disclosure risks associated with small source reference distributions).

### 3.4 Strict Application Fixture Boundary
- Category B synthetic patient records are strictly restricted to **application-level development and testing fixtures**:
  1. Frontend UI form state verification (Clinical Intake Wizard).
  2. Backend REST API request/response schema integration testing.
  3. Staging and demo environment seeding.
- **Evaluation Dataset Separation Invariant:** Synthetic patient records **must remain completely separate from all ML model training, validation, cross-validation, and test evaluation datasets**. All ML evaluation must rely strictly on validated clinical benchmarks (Category A) under documented research governance.

---

## 4. Regulatory Terminology Rectification

### 4.1 CDSCO Medical Device Submission Portals
Under the *Guidance Document on Medical Device Software (MDSW)*, Document No. **`CDSCO/MD/GD/MDSW/01/2026`** (published 21 July 2026 by CDSCO, Ministry of Health & Family Welfare, Government of India), the statutory online portals are designated as follows:

1. **National Single Window System (NSWS) (`https://www.nsws.gov.in`):**  
   The mandatory unified governmental portal for medical device test-licence applications (e.g., Form MD-12 application for Form MD-13 test licence to manufacture or import for testing, clinical investigation, or development).
2. **Online System for Medical Devices (`https://cdscomdonline.gov.in`):**  
   The dedicated, official regulatory portal for medical device manufacturing licences (Form MD-7/MD-8), import licences (Form MD-14/MD-15), registration certificates, and vigilance reporting.

### 4.2 Rejection of "SUGAM" Terminology
Prior documentation informally referred to the medical devices portal as "SUGAM". This terminology is **imprecise and eliminated**:
- "SUGAM" (`cdscoonline.gov.in`) is historically and administratively designated for pharmaceuticals, cosmetics, and clinical trials for new drugs.
- The dedicated statutory portal for medical devices and SaMD under MDR 2017 is the **Online System for Medical Devices** (`cdscomdonline.gov.in`).
- All references have been updated to use the official title **Online System for Medical Devices**.

### 4.3 Classification Status
HeartXAI 2.0 cannot be definitively classified under Indian CDSCO rules at this time. Classification depends upon the finalized intended purpose, indications for use, user qualification (lay user vs. licensed clinician), and the official Table 2 risk classification matrix. Its regulatory status remains formally **undetermined**.

---

## 5. Live Cryptographic Git Verification Evidence

The four mandatory verification commands were executed directly on the repository:

### Command 1: Local HEAD Commit Hash
```powershell
PS C:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0> git rev-parse HEAD
1b0c1c1e81169c32b550418845310587a343b94d
```

### Command 2: Remote Tracking Branch Commit Hash
```powershell
PS C:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0> git rev-parse origin/main
1b0c1c1e81169c32b550418845310587a343b94d
```

### Command 3: Live Remote GitHub Repository Commit Hash
```powershell
PS C:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0> git ls-remote origin main
1b0c1c1e81169c32b550418845310587a343b94d	refs/heads/main
```

### Command 4: Working Tree & Staging Status
```powershell
PS C:\Users\edhub\Desktop\Anti Gravity Projects\heartxai-2.0> git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

### Cryptographic Synchronisation Verification Matrix
- **Local HEAD SHA-1:** `1b0c1c1e81169c32b550418845310587a343b94d`
- **Tracking Branch (`origin/main`):** `1b0c1c1e81169c32b550418845310587a343b94d`
- **Live Remote (`refs/heads/main`):** `1b0c1c1e81169c32b550418845310587a343b94d`
- **Working Tree:** Clean (0 unstaged changes, 0 untracked files).
- **Parity Verdict:** **100% CRYPTOGRAPHIC SYNCHRONISATION VERIFIED**. All commit hashes match identically.

---

## 6. Authoritative Governance Invariants & Unresolved Issues

### 6.1 Unresolved Issues (Strategic Governance Decisions Pending Selection)
The following five strategic decisions remain strictly **`PENDING USER DECISION`**. Implementation of Milestone 01 will not commence until explicit user selections are recorded:

1. **DEC-001 (Hosting Budget & Infrastructure Profile):**  
   - *Options:* Option A (Low-Cost VPS, ~$25–$55/mo), Option B (AWS Multi-AZ Cloud, ~$250/mo), Option C (Bare Metal Local, $0).  
   - *Status:* **PENDING USER DECISION** (Architectural recommendation: Option A).
2. **DEC-002 (Clinical Governance Implementation Scope):**  
   - *Options:* Option A (Multi-Track Phased Governance: physician/content reviews in MVP; ethics/regulatory determination gate before human studies), Option B (Upfront Institutional Gate: formal IRB/Q-Sub clearance before code).  
   - *Status:* **PENDING USER DECISION** (Architectural recommendation: Option A).
3. **DEC-003 (Cardiovascular Prediction Scope):**  
   - *Options:* Option A (Task A MVP Only: cross-sectional CAD classification on Cleveland benchmark; Task B excluded), Option B (Implement Task B 10-year risk calculator in MVP).  
   - *Status:* **PENDING USER DECISION** (Architectural recommendation: Option A).
4. **DEC-004 (Geographic Adapter Extensibility Scope):**  
   - *Options:* Option A (Universal Country Adapter Pattern Extensibility Goal with US/IN/UK synthetic demonstration profiles), Option B (US-Only Baseline).  
   - *Status:* **PENDING USER DECISION** (Architectural recommendation: Option A).
5. **DEC-005 (Data Classification & Patient Data Policy):**  
   - *Options:* Option A (Three-Tier Classification: Category A research data reviewed in M09; Category B synthetic test data with documented privacy limitations and no DP claim; Category C real patient data strictly prohibited), Option B (Real PHI Pilot).  
   - *Status:* **PENDING USER DECISION** (Architectural recommendation: Option A).

### 6.2 Pre-Implementation Invariants
- Application code implementation remains blocked.
- Model training, validation, and deployment remain blocked.
- Real patient health information remains strictly prohibited across all milestones.
- Milestone 01 authorization remains strictly conditioned on stakeholder governance selections.
