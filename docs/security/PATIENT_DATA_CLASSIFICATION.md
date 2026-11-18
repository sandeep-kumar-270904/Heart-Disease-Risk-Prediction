# PATIENT DATA CLASSIFICATION AND PROTECTION SPECIFICATION

**Document Reference:** `docs/security/PATIENT_DATA_CLASSIFICATION.md`  
**Phase:** 09 — Security, Privacy, Data Protection & Threat Modelling  
**Status:** Approved Technical Design  
**Author:** Healthcare Data Protection Specialist & Privacy Officer  
**Traceability:** FR-USER-*, FR-PRED-*, NFR-PRIV-01, ADR-009, ADR-011  

---

## 1. Executive Summary & Data Protection Principles

HeartXAI 2.0 processes diverse data categories ranging from public healthcare facility directories to highly sensitive physiological biomarkers and algorithmic cardiovascular risk assessments. 

Under global data protection standards (including India's Digital Personal Data Protection Act 2023, EU GDPR Article 9 special category health data, and US HIPAA standards), all data processed by HeartXAI is categorized across four defined sensitivity tiers:
1. **Tier 1: Public Data (Unrestricted)** — Public directory information, hospital names, doctor specialties, general medical guidelines.
2. **Tier 2: Internal Operational Data (Confidential)** — Aggregated system metrics, anonymized performance indicators, model hyperparameters.
3. **Tier 3: Personally Identifiable Information (PII - Confidential)** — Full names, email addresses, phone numbers, account identifiers, authentication hashes.
4. **Tier 4: Protected Health Information & Biomarkers (PHI - Highly Confidential / Restricted)** — Blood pressure, cholesterol, resting ECG readings, calculated CAD probability scores, SHAP explanations, counterfactuals, uploaded medical reports.

---

## 2. Comprehensive Data Taxonomy & Protection Matrix

| Data Category | Specific Attributes | Sensitivity Tier | Purpose of Collection | Access Permissions | Storage Location | Encryption Standard | Retention Period | Deletion Policy | Necessity Check | Secondary ML Training Permitted? |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **Identity Information** | Full Name, Preferred Name | **Tier 3 (PII)** | Account personalization, clinical report labeling | Patient, Consented Clinician | PostgreSQL `users` table | AES-256 at rest (DB Volume) | Duration of active account | Hard delete on account erasure | **Mandatory** | **STRICTLY PROHIBITED** |
| **Contact Information** | Email Address, Phone (Optional) | **Tier 3 (PII)** | Authentication, password reset, security notifications | Patient, Admin (contact only) | PostgreSQL `users` table | AES-256 at rest; Column-level index hash | Duration of active account | Hard delete on account erasure | **Mandatory** | **STRICTLY PROHIBITED** |
| **Demographic Information** | Chronological Age, Biological Sex | **Tier 4 (PHI)** | Core ML inference features for CAD classifier | Patient, Consented Clinician | PostgreSQL `predictions` table | AES-256 at rest | Duration of account or user record deletion | Hard delete on user request | **Mandatory** | Only if de-identified & explicitly consented |
| **Health Measurements** | Blood Pressure, Cholesterol, Fasting Glucose, Max HR | **Tier 4 (PHI)** | Core clinical biomarkers required for CAD risk evaluation | Patient, Consented Clinician | PostgreSQL `predictions` table | AES-256 at rest | Duration of account or record deletion | Hard delete on record deletion | **Mandatory** | Only if de-identified & explicitly consented |
| **Medical History** | Chest Pain Type, Angina, ST Depression, Fluoroscopy | **Tier 4 (PHI)** | Clinical diagnostic symptoms for ML model forward pass | Patient, Consented Clinician | PostgreSQL `predictions` table | AES-256 at rest | Duration of account or record deletion | Hard delete on record deletion | **Mandatory** | Only if de-identified & explicitly consented |
| **Prediction Results** | Calibrated Probability, Risk Classification, Brier score | **Tier 4 (PHI)** | Providing clinical risk assessment to patient | Patient, Consented Clinician | PostgreSQL `predictions` table | AES-256 at rest | Retained with prediction history | Hard delete on user request | **Mandatory** | Only aggregated validation metrics |
| **SHAP Explanations** | Feature attributions, Base value, Waterfall vectors | **Tier 4 (PHI)** | Explainable AI rationale and biomarker contributions | Patient, Consented Clinician | PostgreSQL `predictions.shap_values` (JSONB) | AES-256 at rest | Retained with prediction history | Hard delete on user request | **Mandatory** | Only aggregated feature rankings |
| **Counterfactual Outputs** | Target biomarker goals, delta recommendations | **Tier 4 (PHI)** | Lifestyle and medical sensitivity exploration | Patient, Consented Clinician | PostgreSQL `predictions.counterfactuals` (JSONB) | AES-256 at rest | Retained with prediction history | Hard delete on user request | **Mandatory** | Only aggregated sensitivity metrics |
| **Uploaded Documents** | ECG PDF tracings, Lab test reports | **Tier 4 (PHI)** | Supplemental medical context for clinician review | Patient, Consented Clinician | Encrypted S3 / Private Storage Bucket | AES-256-GCM Server-Side Encryption | Until patient deletes file or closes account | Instant deletion from bucket | **Optional** | **STRICTLY PROHIBITED** |
| **Generated Reports** | Exported PDF clinical summary sheets | **Tier 4 (PHI)** | Patient offline review, sharing with external doctors | Patient, Consented Clinician | Ephemeral cache / Private Bucket | AES-256-GCM Server-Side Encryption | 24 hours ephemeral; re-generated on demand | Auto-purged after 24 hours | **Optional** | **STRICTLY PROHIBITED** |
| **Authentication Data** | Argon2id password hash, TOTP secrets, Refresh tokens | **Tier 3 (PII)** | Identity verification and session management | System internal only (No user/admin read) | PostgreSQL `users` & Redis token store | Argon2id hash; AES-256-GCM for TOTP secrets | Duration of active account | Hard delete on account erasure | **Mandatory** | **STRICTLY PROHIBITED** |
| **Audit Records** | Timestamp, IP address, Action, User ID, Target Entity | **Tier 2 (Internal)** | Security compliance, forensic investigation, legal proof | Admin (Auditors) only; No clinical data | PostgreSQL `audit_logs` table (Append-only) | AES-256 at rest; Column hashing | 7 years (statutory requirement) | Anonymized after account deletion | **Mandatory** | **STRICTLY PROHIBITED** |

---

## 3. Data Minimization & Boundary Rules

To protect patient privacy, HeartXAI strictly adheres to the principle of **Data Minimization**:
1. **Uncollected Data (Strictly Prohibited):**
   - National Identification Numbers (US SSN, Indian Aadhaar, European National ID).
   - Exact Residential Street Addresses or GPS Coordinates (only Country and City/Region stored).
   - Payment Card Numbers / Bank Accounts (any future billing handled by third-party PCI-DSS Level 1 gateways).
   - Genomic raw sequencing data or full electronic health record (EHR) dumps.
2. **Separation of PII from Analytical Records:**
   - The user identity table (`users`) stores identity and credentials.
   - The clinical prediction table (`predictions`) stores clinical tensors and outputs, joined strictly via foreign key `user_id`.
   - Analytical and audit exports strip the `user_id` and replace it with a cryptographically salted one-way pseudonym (`SHA256(user_id + daily_salt)`), ensuring data analysts never view patient identities.

---

## 4. Secondary Use for Machine Learning Development Policy

A common failure in healthcare AI startups is silently training new models on live patient data without consent. HeartXAI establishes an explicit policy:

```text
STRICT ML TRAINING RE-USE POLICY:
Live production patient data is NEVER automatically piped into ML training pipelines.
Secondary model retraining or research using patient data is permitted ONLY IF:
  1. The patient has provided explicit, unbundled, opt-in consent for research use.
  2. Data is completely de-identified via the HIPAA Safe Harbor / GDPR anonymization protocol 
     (stripping all names, contact info, IP addresses, dates transformed to year-only).
  3. The research protocol is reviewed by an Institutional Review Board (IRB) or Ethics Committee.
```
