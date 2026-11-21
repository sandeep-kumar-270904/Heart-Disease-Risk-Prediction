# HeartXAI 2.0 — Consolidated Project Risk Register
**Document ID:** HX-PR-015  
**Version:** 2.2.0 (Phase 12.2 Final Governance Resolution)  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Technical Program Manager, Application Security Architect & Clinical Safety Reviewer  
**Status:** Authoritative Reconciled Risk Register — Mitigations Enforced in Roadmap  
**Date:** November 2026  

---

## 1. Executive Summary

This register consolidates all identified technical, clinical, security, and operational risks across HeartXAI 2.0 following the Phase 12.2 governance resolution. Each risk is evaluated using a quantitative Risk Priority Number ($\text{RPN} = \text{Probability} \times \text{Impact}$, scaled 1 to 25), with designated ownership, concrete mitigations, and monitoring protocols.

Phase 12.2 incorporates:
1. **Clinical Risk Updates:** PREVENT 2026 guideline adoption (2026 ACC/AHA multisociety dyslipidemia guideline replacing 2013 PCE for US adults 30–79) while strictly keeping Task B excluded from MVP.
2. **Three-Tier Data Classification:** Separation into Category A (public de-identified research data for ML), Category B (synthetic application data for development, testing, UI, personas), and Category C (real patient information — strictly prohibited in MVP).
3. **Four-Pillar Clinical Governance:** Independent separation of Physician Advisory Review, Clinical Content Review, Institutional Ethics / IRB Determination, and Regulatory Applicability Assessment (incorporating FDA January 2026 Clinical Decision Support Software Guidance), eliminating blanket exemption claims.
4. **Capacity Risk Categorization:** Explicit classification of the VPS "500+ daily assessments" claim as an unverified planning estimate subject to empirical load testing across 8 performance variables in Milestone 19.

---

## 2. Risk Evaluation Matrix

```
Probability Scale: 1 (Very Rare) to 5 (Almost Certain)
Impact Scale:      1 (Negligible) to 5 (Catastrophic / Patient Harm / Major Regulatory Violation)
Severity (RPN):    Low (1-5), Medium (6-12), High (15-20), Critical (25)
```

```
+---------------------------------------------------------------------------------------------------------------------------------------+
|                                              CONSOLIDATED PROJECT RISK REGISTER                                                       |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| ID | Risk Description     | Prob | Imp  | RPN | Concrete Mitigation Strategy                       | Owner            | Status        |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R1 | **Conflation of CAD  |  1   |  5   |  5  | Complete removal of Task B from MVP. Model         | Healthcare AI    | **Mitigated** |
|    | Classification with  |      |      |     | strictly bounded to Task A experimental dataset    | Research Lead    | (Scope Locked)|
|    | 10-Yr Future Risk**  |      |      |     | classification; no 10-year risk calculator in MVP. |                  |               |
|    |                      |      |      |     | Notes PREVENT 2026 replacement of PCE in US only.  |                  |               |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R2 | **Uncalibrated Model |  2   |  4   |  8  | Mandatory Platt Scaling or Isotonic Regression with| Senior ML        | **Mitigated** |
|    | Probabilities**      |      |      |     | Brier score <= 0.12 and ECE <= 0.05 verification.  | Research Sci.    | (Plan Locked) |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R3 | **Biologically       |  2   |  4   |  8  | Freeze immutable features (Age, Sex, History);     | ML Validation    | **Mitigated** |
|    | Absurd Counter-      |      |      |     | enforce directional limits and physiological       | Specialist       | (Constraints  |
|    | factual Scenarios**  |      |      |     | floors (BP >= 90 mmHg, Chol >= 120 mg/dL).         |                  | Defined)      |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R4 | **Insecure Direct    |  2   |  5   | 10  | Automated anti-IDOR dependency on all endpoints:   | AppSec           | **Mitigated** |
|    | Object References    |      |      |     | verify `current_user.id == patient_id` or active   | Architect        | (Dependency   |
|    | (IDOR) PHI Breach**  |      |      |     | signed consent grant before querying DB.           |                  | Pattern Set)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R5 | **In-Memory Token    |  2   |  4   |  8  | Short-lived access tokens (15m) in client memory;  | Staff Backend    | **Mitigated** |
|    | Theft / XSS Attack** |      |      |     | HttpOnly SameSite=Lax refresh cookies; strict CSP  | Engineer         | (Security     |
|    |                      |      |      |     | headers disallowing inline script execution.       |                  | Standardized) |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R6 | **SQLite / PostgreSQL|  2   |  4   |  8  | In-memory SQLite fixture verified for unit tests   | Principal QA     | **Mitigated** |
|    | Semantic Mismatch**  |      |      |     | (15 tests); real PostgreSQL 16 container mandated  | Architect        | (Container    |
|    |                      |      |      |     | for all integration & migration tests in M04.      |                  | Gate in M04)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R7 | **Scope Creep /      |  2   |  3   |  6  | Enforce strict 20-milestone roadmap; defer EHR     | Technical        | **Mitigated** |
|    | Premature Enterprise |      |      |     | FHIR, live insurance APIs, and telehealth to       | Program Manager  | (Roadmap      |
|    | Feature Inclusion**  |      |      |     | post-MVP research releases.                        |                  | Locked)       |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R8 | **Hosting Cost       |  2   |  2   |  4  | Implement dual-profile infrastructure: start on    | DevOps           | **Mitigated** |
|    | Overruns on Cloud**  |      |      |     | Tier A (VPS, ~$21-$55/mo); defer AWS RDS ($252/mo) | Architect        | (Itemized     |
|    |                      |      |      |     | until user demand justifies expenditure.           |                  | Model Built)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R9 | **Unit Conversion    |  1   |  4   |  4  | Centralized, bi-directional unit conversion engine | Staff Backend    | **Mitigated** |
|    | Lab Value Errors**   |      |      |     | with 100% unit test coverage for mmol/L <-> mg/dL. | Engineer         | (ADR-011)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R10| **Disaster Recovery  |  2   |  4   |  8  | Automated nightly AES-256-GCM encrypted database   | DevOps           | **Mitigated** |
|    | Data Loss**          |      |      |     | backups (ADR-012) to offsite storage.              | Engineer         | (ADR-012)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R11| **Real Patient PHI   |  1   |  5   |  5  | Strict Three-Tier Classification: Category A       | Healthcare Safety| **Mitigated** |
|    | Breach in Non-Prod** |      |      |     | (de-identified research), Category B (100%         | Consultant       | (Three-Tier   |
|    |                      |      |      |     | synthetic application data), Category C (real PHI  |                  | Classification|
|    |                      |      |      |     | - strictly prohibited in MVP). Zero live records.  |                  | Enforced)     |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R12| **Accessibility      |  2   |  3   |  6  | Target upgraded to WCAG 2.2 AA; automated axe-core | Frontend Quality | **Mitigated** |
|    | Non-Conformance**    |      |      |     | scans integrated into CI; compliance gates in M19. | Lead             | (Target Set)  |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R13| **Blanket Regulatory |  2   |  4   |  8  | Rejection of blanket non-device exemption claims;  | Regulatory &     | **Mitigated** |
|    | Exemption Claim /    |      |      |     | implementation of 4-pillar clinical governance;    | Compliance Lead  | (4-Pillar     |
|    | Misclassification**  |      |      |     | evaluation under FDA Jan 2026 CDS Software guidance|                  | Framework)    |
|    |                      |      |      |     | and Section 520(o)(1)(E) criteria.                 |                  |               |
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
| R14| **Unverified VPS     |  2   |  3   |  6  | Label '500+ daily assessments' as unverified       | Principal SRE    | **Mitigated** |
|    | Capacity Claims**    |      |      |     | planning estimate; mandate empirical load testing  | & DevOps Lead    | (Milestone 19 |
|    |                      |      |      |     | across 8 performance variables in Milestone 19.    |                  | Empirical Gate)
+----+----------------------+------+------+-----+----------------------------------------------------+------------------+---------------+
```

---

## 3. High-Priority Risk Deep Dives & Action Plans

### 3.1 Risk R1: Conflation of CAD Detection with 10-Year Heart Attack Risk (RPN = 5 - Mitigated)
- **Root Cause:** Amateur data science repositories frequently misrepresent the Cleveland catheterization dataset as a prospective cardiovascular risk predictor. Furthermore, clinical guidelines are actively transitioning: the **2026 ACC/AHA Multisociety Dyslipidemia Guideline** formally adopted the **AHA PREVENT equations** (published late 2023 / early 2024) to replace the 2013 Pooled Cohort Equations (PCE) for primary prevention in US adults aged 30–79. However, PREVENT is US-derived, and other nations use their own validated risk scores (UK NICE uses QRISK3, Europe uses SCORE2, India uses WHO/CSI charts).
- **Action Plan:** Task B has been completely excised from the MVP scope. Task A is strictly labeled as an experimental dataset classification model. The UI enforces prominent non-diagnostic disclaimers.

### 3.2 Risk R11: Real Patient Health Data Exposure (RPN = 5 - Mitigated)
- **Root Cause:** Ingestion of live patient clinical records into development, staging, or test environments without comprehensive data governance and institutional IRB protocol.
- **Action Plan:** Strict enforcement of the Three-Tier Data Classification Policy:
  - **Category A (Public Research Datasets):** Publicly available de-identified datasets (UCI Cleveland, 303 records) used exclusively for model training, offline validation, and calibration.
  - **Category B (Synthetic Application Data):** 100% synthetically generated personas, UI fixtures, and mock clinical records (`scripts/generate_synthetic_patients.py`). Plausible physiological distributions with zero link to real individuals.
  - **Category C (Real Patient Information):** Real PHI/PII. **Strictly prohibited** across all MVP milestones (01–20).

### 3.3 Risk R13: Blanket Regulatory Exemption Claim / Regulatory Misclassification (RPN = 8 - Mitigated)
- **Root Cause:** Incorrectly asserting that HeartXAI 2.0 is automatically exempt from medical device regulation under Section 520(o)(1)(E) without assessing the FDA's updated January 2026 Clinical Decision Support Software Guidance.
- **Action Plan:** Elimination of blanket exemption language. Establishment of the Four-Pillar Clinical Governance Framework:
  1. *Physician Advisory Review:* Independent clinicians audit clinical logic, contraindications, and threshold plausibility.
  2. *Clinical Content Review:* Qualified medical reviewers audit patient-facing educational language, lifestyle tips, and emergency triggers.
  3. *Institutional Ethics / IRB Determination:* Research ethics determination for human subjects evaluation.
  4. *Regulatory Applicability Assessment:* Explicit legal/regulatory mapping against FDA January 2026 CDS guidance, EU MDR (2017/745), UK MHRA, and India CDSCO rules.

### 3.4 Risk R14: Unverified Infrastructure Capacity Over-Estimation (RPN = 6 - Mitigated)
- **Root Cause:** Stating that a single 4 vCPU / 8 GB RAM VPS will comfortably handle "500+ daily assessments" without empirical load testing.
- **Action Plan:** Reclassify throughput figures as an unverified planning estimate. Gate final capacity claims behind empirical Locust load testing in Milestone 19 evaluating all 8 performance variables (concurrent users, TreeSHAP CPU latency, connection pool limits, Redis memory overhead, TLS handshake latency, report PDF generation spikes, database write concurrency, and network bandwidth).
