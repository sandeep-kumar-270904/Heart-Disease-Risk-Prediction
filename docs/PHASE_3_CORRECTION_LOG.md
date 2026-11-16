# HeartXAI 2.0 — Phase 3 Architecture Correction Log

| Document Attribute | Details |
| :--- | :--- |
| **Document ID** | `HXAI-ARCH-LOG-001` |
| **Version** | `2.1.0-REVISED` |
| **Log Date** | November 2026 |
| **Log Scope** | Complete audit trace of all corrections applied across Phase 3 architectural documentation |
| **Lead Architect** | Principal Software Architect & Healthcare Security Reviewer |

---

## 1. Executive Purpose

This document provides a line-by-line, itemized audit log of all architectural corrections, terminology rectifications, cryptographic hardening measures, and qualification of claims implemented in response to the **Phase 3 External Architecture Review** (`HXAI-ARCH-AUDIT-001`).

Every modification records the affected document, the original statement, the corrected statement, and the technical or clinical justification.

---

## 2. Itemized Architectural Correction Registry

### 2.1 Geographic Scope & Healthcare Registry Corrections

```
====================================================================================================
CORRECTION ID:    CORR-GEO-001
AFFECTED DOCS:    INTEGRATION_ARCHITECTURE.md (Sec 2, 3.1, 3.2, 5)
                  C4_CONTAINER_DIAGRAM.md, SYSTEM_ARCHITECTURE_DOCUMENT.md
ORIGINAL TEXT:    "EXT-01: CMS NPPES Registry API - Validates medical licenses and NPI numbers
                  during Doctor registration."
                  "Pre-seeded table with 1,500 validated US cardiac centers."
CORRECTED TEXT:   "EXT-01: Physician Verification Provider (Configurable Adapter Pattern).
                  Supports: (a) IndiaManualVerificationAdapter (NMC/State Council registration number
                  + document upload + admin verification queue; optional future ABDM HPR API integration);
                  (b) USCMSVerificationAdapter (CMS NPPES NPI REST API with admin queue fallback);
                  (c) MockVerificationAdapter (local development)."
                  "Facility directory supports 6-digit Indian PIN codes and 5-digit US ZIP codes
                  via IDirectoryProviderAdapter."
JUSTIFICATION:    Target geography was prematurely assumed to be US. Project originates in India
                  (ANITS, Visakhapatnam). NMC in India does not offer an open public REST API;
                  ABDM requires formal partner accreditation. Architecture must be geographically
                  configurable via an Adapter pattern without hardcoded national assumptions.
====================================================================================================
CORRECTION ID:    CORR-GEO-002
AFFECTED DOCS:    ARCHITECTURE_DECISION_RECORDS.md (ADR-008, New ADR-011)
ORIGINAL TEXT:    "HIPAA § 164.508 consent protocol solely referenced for data governance."
CORRECTED TEXT:   "Multi-jurisdictional healthcare compliance: India Digital Personal Data
                  Protection Act, 2023 (DPDP Act 2023), IT (SPDI) Rules 2011, US HIPAA, and EU GDPR.
                  ADR-011 ratified establishing the Geographic Strategy / Adapter Pattern."
JUSTIFICATION:    Ensures regulatory compliance aligns with the target operational jurisdiction.
====================================================================================================
```

---

### 2.2 Clinical Terminology, ML Bounds & Explainability Corrections

```
====================================================================================================
CORRECTION ID:    CORR-CLIN-001
AFFECTED DOCS:    ML_SYSTEM_ARCHITECTURE.md (Sec 1, 2, 4, 6)
                  SYSTEM_ARCHITECTURE_DOCUMENT.md (Sec 1, 3)
                  FUNCTIONAL_REQUIREMENTS.md (FR-07, FR-08)
ORIGINAL TEXT:    "HeartXAI 2.0 provides clinical risk stratification and calculates 10-year
                  ASCVD risk using an XGBoost ML model."
CORRECTED TEXT:   "HeartXAI 2.0 provides a retrospective Angiographic Coronary Artery Disease (CAD)
                  Association Classifier. The ML model predicts binary presence of angiographically
                  significant CAD (>= 50% diameter stenosis in >= 1 major vessel, based on historical
                  1988 Cleveland Clinic tabular data).
                  The ML model is NOT a prospective 10-year cardiovascular risk calculator.
                  If prospective risk is displayed, it must use established deterministic formulas
                  (e.g., ACC/AHA 2013 Pooled Cohort Equations or WHO/ISH charts) computed separately."
JUSTIFICATION:    Conflating a retrospective tabular angiographic classifier with a prospective
                  longitudinal cohort risk estimator is scientifically and medically invalid.
====================================================================================================
CORRECTION ID:    CORR-CLIN-002
AFFECTED DOCS:    ML_SYSTEM_ARCHITECTURE.md (Sec 7, 8)
                  BACKEND_ARCHITECTURE.md (Sec 3)
ORIGINAL TEXT:    "TreeSHAP provides causal medical evidence and identifies biological biomarkers
                  causing heart disease."
CORRECTED TEXT:   "TreeSHAP provides mathematical feature attributions indicating how individual
                  input features shifted the log-odds prediction of this specific tree ensemble.
                  SHAP values represent model explanations, NOT causal medical evidence or biological
                  etiology."
JUSTIFICATION:    Post-hoc feature attributions quantify model behavior, not human pathology or causation.
====================================================================================================
CORRECTION ID:    CORR-CLIN-003
AFFECTED DOCS:    ML_SYSTEM_ARCHITECTURE.md (Sec 9, 10)
                  FUNCTIONAL_REQUIREMENTS.md (FR-10)
ORIGINAL TEXT:    "Counterfactual analysis provides physiologically feasible personalized lifestyle
                  guidance and actionable treatment recommendations."
CORRECTED TEXT:   "Counterfactual analysis provides hypothetical mathematical feature perturbation
                  scenarios indicating the minimum input changes required to cross the model's decision
                  threshold. Counterfactuals are exploratory 'what-if' simulations, NOT clinical
                  treatment recommendations, medical prescriptions, or clinical lifestyle advice.
                  All interventions require evaluation by a licensed healthcare professional."
JUSTIFICATION:    Software algorithms cannot prescribe medical treatment or clinical therapy without
                  physician diagnosis and regulatory medical device clearance.
====================================================================================================
CORRECTION ID:    CORR-CLIN-004
AFFECTED DOCS:    ML_SYSTEM_ARCHITECTURE.md (Sec 2.3)
ORIGINAL TEXT:    "Model demonstrates high clinical validity across diverse patient cohorts."
CORRECTED TEXT:   "Model is subject to severe dataset limitations: trained on historical 1988
                  Cleveland Clinic data (N=303), characterized by severe hospital referral bias
                  (all patients underwent invasive catheterization), male demographic skew (~68%),
                  historical diagnostic standards (thallium-201, fluoroscopy), and complete absence
                  of South Asian / Indian population representation."
JUSTIFICATION:    Scientific integrity requires transparent disclosure of dataset provenance,
                  referral bias, and demographic limitations.
====================================================================================================
```

---

### 2.3 Database Parity, SQLite Boundaries & Testing Corrections

```
====================================================================================================
CORRECTION ID:    CORR-DB-001
AFFECTED DOCS:    DATABASE_ARCHITECTURE.md (Sec 1, 3, 5)
                  ARCHITECTURE_DECISION_RECORDS.md (ADR-006)
ORIGINAL TEXT:    "PostgreSQL 16 and SQLite fallback offer seamless, transparent dual-dialect
                  database compatibility."
CORRECTED TEXT:   "PostgreSQL 16 is the sole production and staging database.
                  SQLite is restricted strictly to lightweight local developer unit tests.
                  SQLite lacks native JSONB binary indexing, lacks row-level locking (causing
                  'database is locked' errors under concurrency), uses loose type affinity, ignores
                  foreign keys without PRAGMA foreign_keys=ON, and lacks native TIMESTAMPTZ arithmetic.
                  Full compatibility is explicitly disclaimed.
                  All integration and end-to-end test suites must be executed against PostgreSQL 16."
JUSTIFICATION:    PostgreSQL and SQLite possess fundamentally different concurrency models, storage
                  engines, and JSON indexing mechanisms.
====================================================================================================
CORRECTION ID:    CORR-DB-002
AFFECTED DOCS:    DATABASE_ARCHITECTURE.md (Sec 6)
ORIGINAL TEXT:    "Migrations are applied with Alembic."
CORRECTED TEXT:   "Alembic migration strategy requires bidirectional verification for every revision:
                  'alembic upgrade head' followed by 'alembic downgrade base' and re-upgrade.
                  Zero-downtime expand/contract schema evolution guidelines enforced."
JUSTIFICATION:    Ensures schema changes are safe, repeatable, and completely rollback-capable.
====================================================================================================
```

---

### 2.4 Backup Cryptography, Key Rotation & Restoration Corrections

```
====================================================================================================
CORRECTION ID:    CORR-SEC-001
AFFECTED DOCS:    DEPLOYMENT_ARCHITECTURE.md (Sec 7)
                  SECURITY_ARCHITECTURE_AND_THREAT_MODEL.md (Sec 4)
                  ARCHITECTURE_DECISION_RECORDS.md (ADR-007, New ADR-012)
ORIGINAL TEXT:    "openssl enc -aes-256-cbc -salt -pbkdf2 ...
                  Backups stored in local /backups volume."
CORRECTED TEXT:   "Backups use Authenticated Encryption with Associated Data (AEAD) via AES-256-GCM.
                  Primary backup destination is off-site S3-compatible cloud storage configured with
                  Object Lock in Compliance Mode (WORM - Write Once, Read Many).
                  Dedicated backup IAM role with PutObject permission only (no DeleteObject).
                  Annual key rotation schedule via Cloud KMS or PBKDF2-HMAC-SHA256 (100,000 iter)."
JUSTIFICATION:    AES-256-CBC is unauthenticated and vulnerable to padding oracle and ciphertext
                  tampering attacks. Local-only backups fail disaster recovery standards. WORM storage
                  prevents ransomware destruction of backup archives.
====================================================================================================
CORRECTION ID:    CORR-SEC-002
AFFECTED DOCS:    DEPLOYMENT_ARCHITECTURE.md (Sec 7.3)
ORIGINAL TEXT:    "System recoverability guaranteed: RPO <= 24h, RTO <= 30m."
CORRECTED TEXT:   "RPO target <= 24h (snapshots) / <= 1h (WAL archiving); RTO target <= 30m.
                  CRITICAL RULE: System recoverability cannot be claimed until restoration has been
                  empirically tested and verified.
                  Automated monthly restoration testing script ('restore_verify.sh') tests restore
                  into an isolated ephemeral database container, validates table counts, and logs audit."
JUSTIFICATION:    Untested backups do not provide verifiable disaster recovery capability.
====================================================================================================
```

---

### 2.5 Reverse Proxy & Infrastructure Version Corrections

```
====================================================================================================
CORRECTION ID:    CORR-INFRA-001
AFFECTED DOCS:    DEPLOYMENT_ARCHITECTURE.md (Sec 2, 3.2, 4, 5)
                  C4_CONTAINER_DIAGRAM.md
ORIGINAL TEXT:    "image: nginx:1.25-alpine"
CORRECTED TEXT:   "image: nginx:1.26-alpine (Pin to active Stable release branch).
                  Documented version lifecycle: track Stable series, weekly Trivy vulnerability
                  scanning, Dependabot container updates, and zero-downtime 'nginx -s reload'."
JUSTIFICATION:    Nginx 1.25 was a mainline development branch that reached End-of-Life in April 2024
                  when Nginx 1.26 was released as the current Stable branch. Production must pin to
                  supported Stable releases.
====================================================================================================
```

---

### 2.6 Implementation Verification & Claim Accuracy Corrections

```
====================================================================================================
CORRECTION ID:    CORR-VERIF-001
AFFECTED DOCS:    ARCHITECTURE_CONSISTENCY_REPORT.md (Sec 1, 2, 7)
                  PHASE_3_FINAL_SIGNOFF_REPORT.md
ORIGINAL TEXT:    "Database scaffolding, migrations, and 15 tests are completed and verified."
CORRECTED TEXT:   "Implementation status explicitly qualified using a 5-Tier Taxonomy:
                  - Tier 1 (Designed): All 18 architecture specs and 21 diagrams.
                  - Tier 2 (Generated): Project skeletons, Alembic boilerplate.
                  - Tier 3 (Implemented): SQLAlchemy 2.0 ORM models, Alembic initial migration,
                    Argon2id hashing, JWT token issuer, health routes.
                  - Tier 4 (Tested): 15 unit/component tests in backend/tests/ passing on SQLite (2.63s).
                  - Tier 5 (Independently Verified): PENDING. No staging deployment or live PostgreSQL
                    CI/CD execution has been conducted yet."
JUSTIFICATION:    Distinguishes verified automated test output from conceptual design, preventing
                  misrepresentation of production completeness.
====================================================================================================
```

---

## 3. Summary of Document Modifications

| Document Name | Modification Description | Status |
| :--- | :--- | :--- |
| `PHASE_3_EXTERNAL_ARCHITECTURE_REVIEW.md` | Formal audit response and defect remediation analysis | **CREATED** |
| `PHASE_3_CORRECTION_LOG.md` | Comprehensive line-by-line audit trail of all changes | **CREATED** |
| `PHASE_3_FINAL_OPEN_DECISIONS.md` | Catalog of unresolved strategic decisions (Geography, Verification, Hosting, CI/CD) | **CREATED** |
| `PHASE_3_FINAL_SIGNOFF_REPORT.md` | Final authoritative sign-off presentation for stakeholder review | **CREATED** |
| `ARCHITECTURE_DECISION_RECORDS.md` | Updated ADRs 001..010; added ADR-011 (Geographic Adapter) and ADR-012 (AEAD Backup) | **UPDATED** |
| `ML_SYSTEM_ARCHITECTURE.md` | Redefined as retrospective CAD classifier; clarified SHAP and counterfactual bounds | **UPDATED** |
| `DATABASE_ARCHITECTURE.md` | Documented SQLite limitations, PostgreSQL production requirement, migration rollback | **UPDATED** |
| `INTEGRATION_ARCHITECTURE.md` | Added Geographic Adapter Pattern, India NMC/ABDM analysis, PIN codes | **UPDATED** |
| `DEPLOYMENT_ARCHITECTURE.md` | Updated to `nginx:1.26-alpine`, AES-256-GCM AEAD, offsite WORM S3, restoration drills | **UPDATED** |
| `ARCHITECTURE_CONSISTENCY_REPORT.md` | Updated traceability, corrected clinical claims, applied 5-tier implementation taxonomy | **UPDATED** |

---

*Verified and sealed by Principal Software Architect & Healthcare Security Reviewer.*
