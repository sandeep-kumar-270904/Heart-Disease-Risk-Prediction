# HeartXAI 2.0 — Phase 12.2 Final Governance Reconciliation Report
**Document ID:** HX-PR-021  
**Version:** 1.0.0  
**Phase:** 12.2 — Final Governance Resolution & Evidence Reconciliation  
**Author:** Principal Software Architect, Healthcare AI Research Reviewer, Clinical Safety Reviewer & Independent Technical Auditor  
**Status:** Audit & Governance Reconciliation Complete — Pending Stakeholder Decision Selection  
**Date:** November 2026  

---

## 1. Executive Summary

This report establishes the final, authoritative reconciliation of HeartXAI 2.0 governance, scientific research, data classification, regulatory positioning, and technical evidence following the Phase 12.2 independent technical audit.

All seven review findings have been resolved in place:
1. **PREVENT Guideline Research Corrected:** Verified the 2026 ACC/AHA Multisociety Guideline on the Management of Dyslipidemia and Cardiovascular Risk, documenting PREVENT's adoption for applicable primary prevention risk estimation, replacing the 2013 PCE equations, while identifying its geographic limitation to US cohorts. Task B remains strictly excluded from the MVP.
2. **Three-Tier Data Classification Established:** Formalized Category A (Public de-identified research datasets), Category B (Synthetic application data), and Category C (Real patient information — strictly prohibited in MVP).
3. **Clinical Governance Multi-Pillar Framework:** Disambiguated Physician Advisory Review, Clinical Content Review, Institutional Ethics / IRB Determination, and Regulatory Applicability Assessment (incorporating the official FDA January 2026 Clinical Decision Support Software Guidance).
4. **Global Configurability Preserved:** Reasserted the global country-adapter architecture (ADR-011) as an extensible requirement supporting any ISO 3166-1 jurisdiction, using US, India, and UK as initial demonstration configurations without hardcoding or unvalidated clinical claims.
5. **Infrastructure Capacity Claims Corrected:** Replaced unsupported "500+ daily assessments" claims with an explicit **unverified planning estimate** and documented the eight performance variables requiring empirical load testing.
6. **Documentation Inventory Reconciled:** Clarified the mathematical relationship between 190 unique markdown files, 20 identical copies mirrored across directories, and 24 PlantUML diagram source files.
7. **Test Evidence Reconciled:** Verified the 15 passing backend unit tests, explicitly documenting their execution against an in-memory SQLite fixture and establishing the real PostgreSQL 16 test container mandate for Milestone 04.

---

## 2. Reassessment: 2026 ACC/AHA Dyslipidemia Guideline & AHA PREVENT

### 2.1 The 2026 Clinical Practice Transition
In 2026, the American College of Cardiology (ACC), American Heart Association (AHA), and collaborating multisociety organizations released the **2026 Guideline on the Management of Dyslipidemia and Cardiovascular Risk**. This guideline formally evaluated and adopted the **AHA PREVENT equations** (Khan et al., *Circulation* 2024;149:430–449) as the recommended cardiovascular disease risk estimation tool for primary prevention clinical decision-making, officially superseding the 2013 Pooled Cohort Equations (PCE) for those applicable decisions.

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            2026 ACC/AHA PREVENT CLINICAL SUMMARY                                              |
+---------------------+---------------------------------------------------------------------------------------------------------+
| Parameter           | Verified Clinical Specification                                                                         |
+---------------------+---------------------------------------------------------------------------------------------------------+
| **Guideline Title** | 2026 ACC/AHA Multisociety Guideline on the Management of Dyslipidemia and Cardiovascular Risk           |
| **Release Date**    | 2026 (ACC/AHA/Multisociety Practice Guidelines)                                                        |
| **Primary Sources** | 1. Khan SS, et al. *Development & Validation of PREVENT Equations.* Circulation. 2024;149(6):430–449.     |
|                     | 2. Khan SS, et al. *Novel Risk Equations for CVD Prevention.* Circulation. 2024;149(6):e260–e288.        |
| **Intended Cohort** | Asymptomatic primary prevention adults aged **30 to 79 years** without established clinical ASCVD or HF.|
| **Eligibility**     | Total cholesterol, HDL-C, systolic BP, diabetes, current smoking, and eGFR (CKD-EPI 2021).             |
|                     | Enhanced model (optional): urine albumin-to-creatinine ratio (uACR), HbA1c, Social Deprivation Index.   |
| **Outcomes**        | 10-year and 30-year risk of: (1) Total CVD (ASCVD + Heart Failure), (2) ASCVD alone, (3) HF alone.    |
| **Treatment of Race**| **Deliberately removes race coefficients** to avoid race-based medicine; substitutes eGFR and SDI.      |
| **Clinical Role**   | Guides patient-clinician risk discussions regarding lifestyle changes, statin therapy, and BP control.  |
+---------------------+---------------------------------------------------------------------------------------------------------+
```

### 2.2 Geographic Limitations & International Non-Applicability
While PREVENT represents the current clinical standard in the United States:
- **United States:** Formally adopted in the 2026 ACC/AHA multisociety guideline for applicable primary prevention decisions.
- **United Kingdom:** The National Institute for Health and Care Excellence (NICE) officially mandates **QRISK3** (NICE CG181 / NG238) for NHS cardiovascular risk assessment. PREVENT is neither adopted nor validated for NHS clinical pathways.
- **Europe:** The European Society of Cardiology (ESC) mandates **SCORE2** and **SCORE2-OP** (stratified by European regional risk tiers).
- **India / LMIC:** The Cardiological Society of India (CSI) and Indian Council of Medical Research (ICMR) reference the **WHO CVD risk charts (South Asia)** or recalibrated clinical scores due to premature CAD onset in South Asian populations.

### 2.3 Task B Policy Confirmation
**Task B remains strictly excluded from the HeartXAI 2.0 MVP.** No prospective risk calculator (PCE, PREVENT, QRISK3, or SCORE2) shall be implemented during Milestones 01–20. Reconsidering Task B post-MVP requires formal clinical advisory review, country-specific guideline evaluation, and institutional ethics determinations.

---

## 3. Authoritative Three-Category Data Classification Policy

To eliminate ambiguity regarding data sources, privacy obligations, and compliance, HeartXAI 2.0 establishes three strictly mutually exclusive data categories:

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

## 4. Multi-Pillar Clinical Governance & Regulatory Boundaries

Clinical governance is not an informal advisory checkbox. HeartXAI 2.0 separates four distinct, independent governance considerations:

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

---

## 5. Global Country-Adapter Architecture (ADR-011)

The approved architectural requirement is that HeartXAI 2.0 is **globally configurable by country**. 

The Country Adapter system is an extensible declarative framework:
- **Core Abstraction:** The platform core is completely decoupled from national conventions via strongly typed configuration schemas (`CountryConfiguration`).
- **Initial Demonstration Profiles:** Pre-configured adapters are provided for the United States (`US`), India (`IN`), and United Kingdom (`GB`) to demonstrate multi-currency, multi-unit ($\text{mg/dL} \leftrightarrow \text{mmol/L}$), and multi-emergency hotline (911/112/999) capabilities.
- **Universal Extensibility:** Any ISO 3166-1 alpha-2 country can be added via declarative configuration without code modifications to core business or ML serving logic.
- **Evidence Boundary:** Initial deployment demonstrates architectural extensibility using Category B synthetic personas. **No claims of clinical validation or regulatory authorization are made for any country.**

---

## 6. Corrected Infrastructure Capacity Planning

### 6.1 Removal of Unverified 500+ Daily Assessment Claims
Previous documentation stated that the minimal VPS could handle "500+ daily assessments." Because no empirical load testing has been conducted, this claim has been **corrected and labeled strictly as an unverified planning estimate**.

### 6.2 Performance Variables Requiring Empirical Load Testing
Before making definitive capacity or throughput claims, the following eight performance variables must be measured during Milestone 19 performance testing:
1. **Concurrent Active Users:** Maximum concurrent HTTP connections before request queueing occurs.
2. **API Request Throughput:** Sustained requests per second (RPS) across CPU-bound and I/O-bound endpoints.
3. **Database Workload:** PostgreSQL connection pool saturation, query latency under connection contention, and disk I/O.
4. **ML Inference Latency:** Wall-clock time ($p50$, $p95$, $p99$) for in-process XGBoost prediction execution.
5. **TreeSHAP Overhead:** Memory allocation spikes and CPU time during local TreeSHAP tree traversal.
6. **Counterfactual Optimization Search:** Execution duration of DiCE-ML or constrained gradient search.
7. **Report Generation Spikes:** CPU and memory utilization during WeasyPrint / headless PDF compilation.
8. **Host Resource Headroom:** Idle vs. peak RAM and CPU utilization of Docker containers on a 4 vCPU / 8 GB RAM instance.

---

## 7. Reconciled Documentation Inventory

### Exact Physical File & Content Accounting
- **Total Markdown Files Physically Present on Disk:** **210 files** (as of commit `dbfe4f2`).
- **Content Hash Analysis (SHA-256):**
  - **167 Unique Supporting Specifications:** Distributed across `docs/` root (42), `backend/` (18), `design/` (16), `devops/` (18), `frontend/` (14), `ml/` (19), `quality/` (21), and `security/` (19).
  - **20 Duplicate Readiness Blueprints:** 20 files in `docs/project-readiness/` mirrored identically into `docs/phase-12-final/` for final handover packaging (20 unique contents, 40 physical paths).
  - **3 Master Final Handover Deliverables:** `HEARTXAI_PHASE_12_FINAL_DOSSIER_v1.1.md`, `DOCUMENTATION_INVENTORY.md`, and `TRACEABILITY_AND_EVIDENCE_INDEX.md` in `docs/phase-12-final/`.
  - **Sum of Unique Markdown Contents:** $167 + 20 + 3 = 190$ unique files.
  - **Physical Paths on Disk:** $190 + 20 \text{ (mirrored duplicates)} = 210$ markdown files.
- **PlantUML Diagram Source Files:** **24 editable source files** in `docs/phase-12-final/diagrams/` (plus 21 original files in `docs/diagrams/`).

---

## 8. Test Evidence Verification Summary

- **Actual Test Files Checked:**
  - `backend/tests/test_api_health.py` (4 tests)
  - `backend/tests/test_database_models.py` (7 tests)
  - `backend/tests/test_security.py` (4 tests)
- **Execution Command:** `pytest -v` in `backend/` (executed on Python 3.11.9, pytest-9.0.3).
- **Execution Result:** 15 passed in 4.56 seconds.
- **Database Fixture Verified:** Line 19 of `backend/tests/conftest.py` declares `TEST_DATABASE_URL = "sqlite:///:memory:"`.
- **Accurate Evidentiary Statement:** The 15 existing unit tests pass against an **in-memory SQLite fixture**. They verify model relationship declarations, password hashing, and JWT token claims. **PostgreSQL 16 integration testing has not yet been executed** and remains an explicit deliverable and gate of Milestone 04.

---

## 9. Reconciled Governance Decision Register (DEC-001 through DEC-005)

```
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| ID      | Decision Description     | Available Options     | Recommended Option      | Selection Rationale| Dependencies  | Status    |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Hosting Profile &      | A: Tier A Minimal VPS | **Option A: Tier A      | Lowest cost for    | Milestone 01, | **PENDING |
| 001**   | Infrastructure Budget**  |    (~$21-$55/mo)      | Minimal VPS**           | dev/synthetic demo;| Milestone 20  | USER      |
|         |                          | B: Tier B AWS Cloud   |                         | no cloud lock-in.  |               | CHOICE**  |
|         |                          |    (~$252/mo)         |                         | Capacity unverified|               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Clinical Governance &  | A: 4-Pillar Governance| **Option A: 4-Pillar    | Separates advisory,| Milestones    | **PENDING |
| 002**   | Regulatory Assessment**  |    Framework          | Governance (Advisory,   | content, ethics,   | 08, 14, 16    | USER      |
|         |                          | B: Informal Advisory  | Content, IRB, FDA CDS)  | and FDA 2026 CDS.  |               | CHOICE**  |
|         |                          |    Only               |                         | No exemption claim.|               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Cardiovascular         | A: Task A MVP Only    | **Option A: Task A      | Preserves clinical | Milestones    | **PENDING |
| 003**   | Prediction Scope**       |    (Task B to research| MVP Only**              | integrity; avoids  | 09, 10, 11,   | USER      |
|         |                          | B: Implement Task B   |                         | risk conflation.   | 14            | CHOICE**  |
|         |                          |    calculator in MVP  |                         | Task B in research.|               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Geographic Launch &    | A: Globally Configured| **Option A: Globally    | Extensible adapter | Milestones    | **PENDING |
| 004**   | Extensibility Scope**    |    Architecture       | Configurable via        | framework; US/IN/UK| 08, 15        | USER      |
|         |                          | B: Hardcoded 3-Country| Country Adapters**      | initial demo only; |               | CHOICE**  |
|         |                          |                       |                         | no clinical claim. |               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Data Classification &  | A: 3-Category Data    | **Option A: 3-Category  | Category A research| All           | **PENDING |
| 005**   | Patient Data Policy**    |    Classification     | Data Policy (Category C | only; Category B   | Milestones    | USER      |
|         |                          | B: Permit Live Pilot  | real PHI strictly       | synthetic demo;    | (01–20)       | CHOICE**  |
|         |                          |    Patient PHI        | PROHIBITED in MVP)**    | Category C banned. |               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
```
