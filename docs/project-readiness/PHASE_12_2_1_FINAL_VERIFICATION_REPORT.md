# HeartXAI 2.0 — Phase 12.2.1 Final Claims, Governance & Git Verification Report

**Document ID:** HX-REPORT-P12.2.1-VERIFY  
**Version:** 1.0.0 (Phase 12.2.1 Authoritative Verification Baseline)  
**Phase:** 12.2.1 — Final Claims, Governance and Git Verification  
**Roles Acting:** Principal Software Architect, Healthcare AI Research Reviewer, Clinical Safety Consultant, Security Architect & Independent Technical Auditor  
**Date:** November 2026  
**Status:** Verification Complete — Governance Approval Still Required Before Milestone 01 Execution  
**Traceability:** Follows Phase 12.2; resolves all 8 verification directives from Phase 12.2.1 inspection.

---

## 1. Executive Summary & Verification Purpose

This report represents the definitive, evidence-backed audit and verification review for **HeartXAI 2.0** preceding implementation authorization. In accordance with Phase 12.2.1 instructions, this phase does not restart the audit or commence Milestone 01 engineering.

Instead, it rigorously audits, corrects, and documents:
1. The evidence-based technical status of the project, replacing misleading claims of "zero unresolved technical issues".
2. The exact target definition, primary provenance, and modern privacy/de-identification limitations of the UCI Cleveland dataset.
3. The refined regulatory posture, eliminating any premature claims that HeartXAI 2.0 is non-device, exempt, or definitively educational CDS.
4. The correction of Decision DEC-002, ensuring that Physician Advisory Review, Clinical Content Review, Institutional Ethics / IRB Determination, and Regulatory Applicability Assessment remain distinct, concurrent governance tracks rather than false alternatives.
5. The correction of Decision DEC-005, clarifying that future real patient data requirements depend on jurisdiction and institutional context, while reaffirming that Category C real patient data is strictly prohibited in MVP.
6. The reclassification of the Universal ISO Country Adapter architecture (ADR-011) as an architectural extensibility goal rather than proof of global operational or regulatory readiness.
7. Tangible, command-verified proof of Git synchronization between local HEAD and remote `origin/main`.
8. An exhaustive contradiction audit across all final claims ("completed", "designed", "pending", "not verified").

---

## 2. Issue 1: Evidence-Based Technical Status (Replacing "Zero Unresolved Technical Issues")

The previous summary statement that there were "zero unresolved technical issues" was misleading because it failed to differentiate between documentation readiness and runtime software maturity. 

The authoritative, evidence-based status of HeartXAI 2.0 is strictly separated into four discrete categories:

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            EVIDENCE-BASED TECHNICAL STATUS MATRIX                                             |
+--------------------------+-----------------------+----------------------------------------------------------------------------+
| Technical Dimension      | Status Classification | Concrete Evidentiary Finding & Operational Boundary                        |
+--------------------------+-----------------------+----------------------------------------------------------------------------+
| **1. Documentation       | **COMPLETE &          | 192 unique markdown specifications and 24 master pre-implementation       |
|    Readiness**           | **AUDITED**           | blueprints exist on disk. Cross-layer naming, biomarker definitions       |
|                          |                       | (`shared/data-dictionary.json`), Pydantic schemas, and SQLAlchemy models   |
|                          |                       | are 100% reconciled on paper.                                              |
+--------------------------+-----------------------+----------------------------------------------------------------------------+
| **2. Implementation      | **MINIMAL BASELINE    | Only baseline scaffolding is implemented in code: FastAPI application      |
|    Status**              | **SCAFFOLDING ONLY**  | factory, health endpoints, database ORM models, and cryptographic helper   |
|                          |                       | primitives. 15 unit tests pass in `backend/tests/`.                        |
|                          |                       | **NOT YET IMPLEMENTED IN CODE:** React frontend, intake form wizard,       |
|                          |                       | in-process ML serving worker, TreeSHAP explainer, counterfactual engine,   |
|                          |                       | PDF generator, localized directory UI, doctor portal, and admin console.   |
+--------------------------+-----------------------+----------------------------------------------------------------------------+
| **3. Runtime Integration | **NOT STARTED /       | Zero runtime communication between the React client, FastAPI ASGI backend, |
|    Status**              | **PENDING BUILD**     | in-process C++ XGBoost worker, Redis token store, and PostgreSQL 16 DB has |
|                          |                       | been executed. All runtime integration is scheduled across Milestones 01–20|
+--------------------------+-----------------------+----------------------------------------------------------------------------+
| **4. Validation Gates    | **PENDING EMPIRICAL   | Crucial empirical validation gates remain pending and strictly enforced:   |
|    Status**              | **EXECUTION**         | - M04: Real PostgreSQL 16 container integration & Alembic migrations.      |
|                          |                       | - M06: Live Redis token-family rotation & fail-closed partition tests.     |
|                          |                       | - M10/11: Calibrated XGBoost Brier score (<=0.12) & ECE (<=0.05).          |
|                          |                       | - M12: TreeSHAP local efficiency mathematical axiom verification.          |
|                          |                       | - M18: OWASP ZAP dynamic penetration testing & automated anti-IDOR tests.  |
|                          |                       | - M19: WCAG 2.2 AA live accessibility scans & Locust empirical load tests. |
|                          |                       | - M20: Staging VPS deployment, Playwright E2E, and AES-256-GCM DR restore. |
+--------------------------+-----------------------+----------------------------------------------------------------------------+
```

---

## 3. Issue 2: Cleveland Dataset Provenance, Exact Target Definition & Privacy Limitations

### 3.1 Primary Documentation and Primary Research Verification
To resolve any ambiguity regarding the target definition, the primary source documentation and primary research literature were inspected:

1. **Primary Research Paper Citation:**  
   *Detrano R, Janosi A, Steinbrunn W, Pfisterer M, Schmid JJ, Sandhu S, Guppy KH, Lee S, Froelicher V. International application of a new probability algorithm for the diagnosis of coronary artery disease. American Journal of Cardiology. 1989;64(5):304–310.*
   - In Section *Methods (Patient Population and Catheterization Protocol)*, Detrano et al. define coronary artery disease verbatim:
     > *"Significant coronary artery disease was defined as the presence of a **greater than 50% reduction in luminal diameter** of at least 1 of the major coronary arteries (left anterior descending, circumflex, or right coronary artery) on selective coronary arteriography."*

2. **Original UCI Machine Learning Repository Documentation:**  
   *`heart-disease.names` (Authored by Robert Detrano, MD, PhD, and David Aha, 1988).*
   - The primary documentation explicitly defines attribute 58 (`num` in the 14-attribute processed subset) verbatim:
     ```
     58 num: diagnosis of heart disease (angiographic disease status)
           -- Value 0: < 50% diameter narrowing
           -- Value 1: > 50% diameter narrowing
           (in any major vessel: attributes 59 through 68 are vessels)
     ```

### 3.2 Key Target Definition Finding
- **Strict Mathematical Inequality:** Both the original UCI documentation and the primary 1989 paper explicitly define positive coronary artery disease as **strictly greater than 50% diameter narrowing** ($>50\%$), NOT $\ge 50\%$.
- **Borderline Ambiguity:** The borderline threshold of exactly $50\%$ stenosis is **not categorized as positive disease** in the primary source documentation. Stating that positive disease is $\ge 50\%$ is a colloquial artifact of subsequent machine learning tutorials that did not verify the primary literature.
- **Approved Binary Target Formulation:**
  $$y = \begin{cases} 0 & \text{if } num = 0 \quad (< 50\% \text{ diameter narrowing; absence of significant CAD}) \\ 1 & \text{if } num \ge 1 \quad (> 50\% \text{ diameter narrowing in 1, 2, 3, or 4 vessels; presence of significant CAD}) \end{cases}$$
  In the Cleveland cohort ($N=303$): Negative ($num=0$): $n=164$ ($54.1\%$); Positive ($num \in \{1,2,3,4\}$): $n=139$ ($45.9\%$).

### 3.3 Privacy & Statutory De-Identification Limitations
The Cleveland dataset carries severe privacy and de-identification limitations under modern legal and regulatory standards:
1. **Pre-Statutory Data Collection (1981–1984):** Data collection occurred between May 1981 and September 1984 at the Cleveland Clinic Foundation. This pre-dates the US Health Insurance Portability and Accountability Act of 1996 (HIPAA), the HIPAA Privacy Rule (2003), and the EU General Data Protection Regulation (GDPR, 2016).
2. **Absence of Modern De-Identification Certification:** While researchers stripped direct patient names, local hospital identification numbers, and social security numbers prior to depositing the data in the UCI repository, the dataset was **never formally certified under modern statutory de-identification standards**:
   - It was not verified under the **HIPAA Safe Harbor standard** (45 CFR § 164.514(b)), which requires the removal of 18 specific identifiers including exact geographic subdivisions and full dates.
   - It was not evaluated under a **HIPAA Statistical Expert Determination** (45 CFR § 164.514(a)) to assess whether small-cell demographics (e.g., a 29-year-old male with atypical angina and specific fluoroscopy markers) present re-identification risk.
   - It was not audited under **GDPR Article 4(1) / Recital 26 criteria** to establish whether the data is truly anonymous or merely pseudonymous research data.
3. **Severe Clinical Selection Bias:** The cohort consists exclusively of symptomatic patients referred for invasive coronary catheterization at a single tertiary cardiac referral center. Background prevalence is $45.9\%$, unrepresentative of primary care populations.
4. **Absence of Longitudinal Event Data:** The dataset contains zero prospective follow-up. It records only anatomical narrowing on the day of catheterization; it cannot predict prospective 10-year heart attack or stroke incidence.

---

## 4. Issue 3: Refined Regulatory Position (Status Undetermined)

Previous draft statements that HeartXAI 2.0 is "non-device", "exempt from FDA regulation", or "definitively educational CDS" under Section 520(o)(1)(E) of the 21st Century Cures Act were legally premature and have been **completely excised**.

### 4.1 Authoritative Regulatory Statement
> **REGULATORY POSTURE: STATUS UNDETERMINED**  
> HeartXAI 2.0 is **NOT** classified as non-device, exempt, or definitively educational Clinical Decision Support (CDS). Its regulatory status under medical device legislation remains **strictly undetermined**.

### 4.2 Legal & Regulatory Basis
Under the US Food, Drug, and Cosmetic Act (FD&C Act), the **FDA January 2026 Final Guidance on Clinical Decision Support Software**, the European Union Medical Device Regulation (EU MDR 2017/745 Rule 11), and the UK Medicines and Healthcare products Regulatory Agency (MHRA) guidance, regulatory classification cannot be established abstractly. It depends on four concrete variables:

1. **Intended Use & Marketing Claims:** Software intended to inform clinical management, screen for pathology, or estimate disease probability is heavily scrutinized. Software providing outputs to patients to guide their care or assess their condition is subject to distinct oversight from software supporting clinician analysis.
2. **Intended Users (Healthcare Professional vs. Patient/Consumer):** Under Criterion 3 & 4 of Section 520(o)(1)(E), software is non-device CDS only if it is intended for healthcare professionals who can independently review the clinical basis of the recommendation without relying primarily on the software output. **Patient-directed or consumer-facing software that outputs personalized disease probability or risk scores is NOT exempt under Criterion 3/4** and is generally regulated as a medical device (Software as a Medical Device - SaMD).
3. **Software Functionality & Complexity:** While TreeSHAP waterfall charts provide local feature attribution, complex non-linear machine learning models (such as gradient boosted decision trees) may not allow a lay user or even a practicing clinician to independently verify the mathematical calculations in real time.
4. **Jurisdictional Frameworks:**
   - *United States:* FDA regulatory classification requires either a formal 513(g) Request for Information, an FDA Pre-Submission (Q-Submission), or formal clearance/approval (510(k), De Novo, or PMA).
   - *European Union:* Under EU MDR 2017/745 Annex VIII Rule 11, software intended to provide information used to take decisions with diagnosis or therapeutic purposes is classified as Class IIa or higher SaMD.
   - *United Kingdom:* Regulated under UK MDR 2002 (as amended) and MHRA Software and AI as a Medical Device guidelines.
   - *India:* Regulated under the Medical Device Rules, 2017, and CDSCO SaMD notifications.

**Conclusion:** HeartXAI 2.0 makes zero claims of regulatory exemption, non-device classification, or statutory clearance. During MVP engineering, it operates strictly as prototype software using Category B synthetic application data. Formal regulatory classification must be determined prior to any clinical pilot, marketing, or real patient deployment.

---

## 5. Issue 4: Correction of Decision DEC-002 (Four Distinct Governance Tracks)

### 5.1 Rationale for Correction
In earlier iterations, DEC-002 presented an Institutional Review Board (IRB) protocol as an "alternative" to Physician Advisory Review (Option A vs. Option B). This was a category error:
- An **Institutional Review Board (IRB)** or **Research Ethics Committee (REC)** evaluates human subjects protections, informed consent, and institutional research risk. An IRB does not review engineering boundary conditions or clinical UX copy.
- A **Physician Advisory Review** provides clinical expertise on whether physiological ranges, contraindications, and emergency red-flag triggers are clinically sound.
- A **Clinical Content Review** verifies health literacy, patient communication, and educational readability against national cardiology guidelines.
- A **Regulatory Applicability Assessment** determines medical device legal classification across jurisdictions.

These four functions are **complementary, distinct tracks**, not mutually exclusive options.

### 5.2 Corrected Decision Specification: DEC-002
```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            CORRECTED GOVERNANCE DECISION: DEC-002                                             |
+--------------------------+----------------------------------------------------------------------------------------------------+
| Decision ID              | **DEC-002: Clinical Governance Implementation Scope (Four Distinct Tracks)**                       |
+--------------------------+----------------------------------------------------------------------------------------------------+
| Status                   | **PENDING USER SELECTION** (Awaiting explicit user choice in chat)                                 |
+--------------------------+----------------------------------------------------------------------------------------------------+
| **Option A**             | **Multi-Track Phased Governance for MVP:**                                                         |
| **(Recommended)**       | Maintain all four governance tracks as distinct workflows:                                         |
|                          | 1. *Physician Advisory Review:* Active during MVP to audit clinical features, boundary conditions, |
|                          |    and emergency triggers.                                                                         |
|                          | 2. *Clinical Content Review:* Active during MVP to verify health literacy, educational copy, and   |
|                          |    patient communication.                                                                          |
|                          | 3. *Institutional Ethics / IRB Protocol:* Formal research protocol drafted in parallel during MVP, |
|                          |    submitted prior to any human subject testing.                                                   |
|                          | 4. *Regulatory Applicability Assessment:* Systematic review under FDA guidance (including Jan 2026 |
|                          |    CDS guidance), EU MDR, UK MHRA, and CDSCO rules; regulatory status remains formally undetermined|
|                          |    during MVP development.                                                                         |
+--------------------------+----------------------------------------------------------------------------------------------------+
| **Option B**             | **Pre-Development Institutional IRB Protocol & Regulatory Pre-Submission:**                        |
|                          | Require formal hospital/university institutional sponsorship, joint IRB ethics approval, and an    |
|                          | official FDA pre-submission (Q-Submission) to be fully approved before any software engineering   |
|                          | begins. (6 to 12-month institutional lead time; high upfront cost).                                |
+--------------------------+----------------------------------------------------------------------------------------------------+
```

---

## 6. Issue 5: Correction of Decision DEC-005 (Context-Dependent Data Governance)

### 6.1 Rationale for Correction
Earlier drafts stated that any future use of real patient data "universally requires signed BAAs, security audits, and formal ethics approval." This was inaccurate:
- A **Business Associate Agreement (BAA)** is a specific contractual instrument under the US HIPAA Privacy Rule (45 CFR § 164.502(e) / § 164.504(e)) governing relationships between HIPAA Covered Entities and Business Associates. It has no legal standing in the United Kingdom, the European Union, India, or other jurisdictions.
- Outside the US, health data transfers are governed by different legal instruments (e.g., GDPR Article 28 Data Processing Agreements and standard contractual clauses in the EU/UK; the Digital Personal Data Protection Act 2023 in India).
- An **Institutional Review Board (IRB)** is a US-specific term under the Common Rule (45 CFR 46); equivalent oversight in the UK is conducted by a Research Ethics Committee (REC) via the Health Research Authority (HRA), in the EU by an Ethics Committee, and in India by an Institutional Ethics Committee (IEC) under CDSCO/ICMR rules.
- Certain uses of real patient data (such as fully anonymized public datasets or secondary quality improvement) may receive waivers or exemptions depending on the governing institutional context.

### 6.2 Corrected Decision Specification: DEC-005
```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            CORRECTED GOVERNANCE DECISION: DEC-005                                             |
+--------------------------+----------------------------------------------------------------------------------------------------+
| Decision ID              | **DEC-005: Data Classification & Real Patient Data Policy**                                        |
+--------------------------+----------------------------------------------------------------------------------------------------+
| Status                   | **PENDING USER SELECTION** (Awaiting explicit user choice in chat)                                 |
+--------------------------+----------------------------------------------------------------------------------------------------+
| **Option A**             | **Three-Tier Data Classification Policy (Category C Strictly Prohibited in MVP):**                 |
| **(Recommended)**       | - Category A (Public Research Data): UCI Cleveland (303 records) used exclusively for offline ML.  |
|                          | - Category B (Synthetic Application Data): 100% synthetically generated personas, UI fixtures, and|
|                          |   test records. Zero real human data. Used for all MVP development, testing, and staging.          |
|                          | - Category C (Real Patient Information): Personally Identifiable Information (PII) or Personal     |
|                          |   Health Information (PHI) from live patients. **STRICTLY PROHIBITED** across all MVP milestones   |
|                          |   (01 through 20).                                                                                 |
+--------------------------+----------------------------------------------------------------------------------------------------+
| **Option B**             | **Authorize Real Patient Pilot Data in Staging (Permit Category C):**                              |
|                          | Permit beta testing with live clinical records during Milestone 20 staging acceptance.             |
|                          | *Governance Requirement:* Requires establishing applicable ethics, privacy, contractual, and       |
|                          | regulatory compliance based on jurisdiction and institutional context (e.g., HIPAA BAAs for US     |
|                          | covered entities, GDPR Article 28 DPAs for EU/UK, DPDP compliance in India, and local IRB/REC/IEC  |
|                          | research ethics approvals). Incurring these legal and administrative burdens prior to verifying    |
|                          | baseline software functionality is not recommended.                                                |
+--------------------------+----------------------------------------------------------------------------------------------------+
```

---

## 7. Issue 6: Reclassification of Universal ISO Country Adapter Architecture

### 7.1 Architectural Extensibility Goal vs. Operational Reality
Earlier text asserted that HeartXAI 2.0 "supports any country in the world" via ADR-011. This claim has been formally reclassified:

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                    COUNTRY ADAPTER ARCHITECTURE (ADR-011) RECLASSIFICATION                                    |
+---------------------------+---------------------------------------------------------------------------------------------------+
| Classification Dimension  | Scope & Operational Definition                                                                    |
+---------------------------+---------------------------------------------------------------------------------------------------+
| **Architectural Status**  | **Extensibility Goal and Software Design Pattern:**                                               |
|                           | The software architecture decouples formatting, units, hotlines, and directory schemas using a    |
|                           | pluggable adapter design pattern (`CountryConfiguration` Pydantic model). This ensures that the   |
|                           | core codebase contains zero hardcoded assumptions (such as imperial units or US-only phone masks)|
|                           | and can accommodate any ISO 3166-1 alpha-2 country profile without modifying business logic.     |
+---------------------------+---------------------------------------------------------------------------------------------------+
| **Operational Reality**  | **NOT Operational in Every Country:**                                                             |
|                           | The presence of an extensible software pattern does NOT mean the platform is operational in all   |
|                           | countries. Full operational support requires locally verified healthcare center directories,      |
|                           | accredited translations, live emergency routing, and jurisdiction-specific data residency.        |
+---------------------------+---------------------------------------------------------------------------------------------------+
| **Regulatory Reality**   | **NOT Cleared or Clinically Validated Globally:**                                                 |
|                           | HeartXAI 2.0 has NOT been clinically validated or cleared by regulatory authorities in the US,   |
|                           | UK, India, or any other country. Demonstrating country adapters tests architectural extensibility |
|                           | using synthetic data only.                                                                        |
+---------------------------+---------------------------------------------------------------------------------------------------+
| **Initial MVP Scope**     | Initial demonstration profiles for the United States (`US`), India (`IN`), and United Kingdom     |
|                           | (`GB`) validate bi-directional unit conversion math (mg/dL <-> mmol/L) and emergency UI routing   |
|                           | using Category B synthetic demonstration records.                                                 |
+---------------------------+---------------------------------------------------------------------------------------------------+
```

---

## 8. Issue 7: Tangible Git Synchronization Verification

### 8.1 Empirical Verification Log
In accordance with Issue 7, Git status and synchronization were verified directly on the repository via terminal commands:

```
Command 1: git rev-parse HEAD
Output:    19b20f279f5281015a591ac042428962a3204c58

Command 2: git rev-parse origin/main
Output:    19b20f279f5281015a591ac042428962a3204c58

Command 3: git ls-remote origin main (Unsandboxed network inspection)
Output:    19b20f279f5281015a591ac042428962a3204c58    refs/heads/main

Command 4: git log -1 --stat
Output:
commit 19b20f279f5281015a591ac042428962a3204c58
Author: sandeep-kumar-270904 <trailmail123456@gmail.com>
Date:   Sat Nov 21 23:16:31 2026 +0530

    docs(phase-12.2): resolve final governance, evidence reconciliation, and data classification

 30 files changed, 2380 insertions(+), 793 deletions(-)

Command 5: git status
Output:
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

### 8.2 Synchronization Confirmation & Honest Network Incident Reporting
- **Commit Parity:** Local `HEAD` (`19b20f279f5281015a591ac042428962a3204c58`) and remote `origin/main` (`19b20f279f5281015a591ac042428962a3204c58`) are **100% bitwise identical**.
- **Transparent Network Report:** During Phase 12.2 execution, an initial sandboxed push attempt failed with `fatal: unable to access ... Could not resolve host: github.com` due to standard sandbox network isolation. The push was re-executed unsandboxed (`BypassSandbox: true`) with user authorization, successfully delivering all commits (`dbfe4f2..19b20f2`) to the remote repository. Synchronization is verified via live remote reference query (`git ls-remote`), not assumed based solely on a clean local tree.

---

## 9. Issue 8: Contradiction Audit Across All Final Claims

An exhaustive audit of all documentation deliverables was conducted to eliminate semantic contradictions between **completed**, **designed**, **pending**, and **not verified**:

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                                FINAL CLAIMS CONTRADICTION AUDIT                                               |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| Project Item         | Former Contradiction| Reconciled Authoritative Status           | Supporting Deliverables               |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| **Specifications &   | Stated as complete | **COMPLETED & AUDITED DESIGN**            | 192 unique markdown files in `docs/`  |
| Documentation**      | (accurate)         | All architecture documents exist on disk. | Reconciled in `DOCUMENTATION_INVENTORY|
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| **Application Code   | Described as "zero | **MINIMAL BASELINE SCAFFOLDING ONLY**     | Backend scaffolding in `backend/app/` |
| Maturity"            | technical issues"  | Frontend, ML inference, and UI are not yet| 15 unit tests pass on SQLite fixture  |
|                      |                    | implemented in code.                      | (conftest.py:19).                     |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| **PostgreSQL 16      | Described as       | **DESIGNED AS TARGET; LIVE PENDING M04**  | Alembic migration scripts authored;   |
| Database Engine**    | validated in tests | Tests currently execute on SQLite fixture;| live PostgreSQL 16 container testing  |
|                      |                    | live PostgreSQL container gated in M04.   | is an explicit gate in Milestone 04.  |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| **Runtime Cross-Layer| Described as       | **PENDING INTEGRATION (M01-M20)**         | Cross-layer contracts documented on   |
| Integration**        | integrated         | Runtime communication between services has| paper; runtime end-to-end integration |
|                      |                    | not been executed.                        | is pending milestone implementation.  |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| **Accessibility      | Described as       | **DESIGNED AS TARGET (WCAG 2.2 AA)**      | Tokens and guidelines in `design/`;   |
| Compliance**         | compliant          | No UI implemented yet. Live axe-core CI   | automated and manual audits gated     |
|                      |                    | compliance testing is gated in M19.       | in Milestone 19.                      |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| **VPS Throughput     | Described as       | **UNVERIFIED PLANNING ESTIMATE**          | Sizing model in `OPERATIONAL_COST_`;  |
| Capacity**           | verified 500+/day  | Theoretical model; empirical load testing | Locust load testing across 8 variables|
|                      |                    | across 8 performance variables in M19.    | gated in Milestone 19.                |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| **Regulatory CDS     | Described as       | **STATUS UNDETERMINED**                   | Evaluated under FDA Jan 2026 guidance;|
| Status**             | exempt / CDS       | No claims of exemption or non-device;     | 4-pillar governance enforces oversight|
|                      |                    | formal legal determination required.      | without premature regulatory claims.  |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
| **Universal Country  | Described as       | **ARCHITECTURAL EXTENSIBILITY GOAL**      | ADR-011 decoupled adapter pattern;    |
| Adapters**           | supporting all     | Adapter pattern supports localization; no | initial US, IN, UK synthetic profiles;|
|                      | countries          | claim of global operational readiness.    | global clearance must be established. |
+----------------------+--------------------+-------------------------------------------+---------------------------------------+
```

---

## 10. Summary Governance Register (Decisions Awaiting User Action)

In strict accordance with project rules, decisions DEC-001 through DEC-005 remain **`PENDING USER DECISION`**:

```
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| ID      | Decision Description     | Available Options     | Recommended Option      | Selection Rationale| Dependencies  | Status    |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Hosting Profile &      | A: Tier A Minimal VPS | **Option A: Tier A      | Lowest cost; no    | Milestone 01, | **PENDING |
| 001**   | Infrastructure Budget**  |    (~$25-$55/mo)      | Minimal VPS**           | vendor lock-in;    | Milestone 20  | USER      |
|         |                          | B: Tier B AWS Cloud   |                         | capacity estimate. |               | DECISION**|
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Clinical Governance    | A: Multi-Track Phased | **Option A: Multi-Track | Distinct clinical  | Milestones    | **PENDING |
| 002**   | Implementation Scope**   |    Governance for MVP | Phased Governance**     | review during MVP; | 08, 14, 16    | USER      |
|         | (4 Distinct Tracks)      | B: Pre-Dev IRB &      |                         | ethics/reg prepared|               | DECISION**|
|         |                          |    Regulatory Pre-Sub |                         | in parallel; no alt|               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Cardiovascular         | A: Task A MVP only    | **Option A: Task A      | Preserves clinical | Milestones    | **PENDING |
| 003**   | Prediction Scope**       | B: Implement Task B   | MVP Only**              | integrity; PREVENT | 09, 10, 11,   | USER      |
|         |                          |    calculator in MVP  |                         | 2026 noted; B out. | 14            | DECISION**|
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Geographic Adapter     | A: Adapter Pattern as | **Option A: Adapter     | Proves multi-unit  | Milestones    | **PENDING |
| 004**   | Extensibility Goal &     |    Extensibility Goal | Pattern Extensibility   | architecture without| 08, 15       | USER      |
|         | Localization Scope**     |    (US/IN/UK Synth)   | Goal (US/IN/UK Synth)** | claiming global    |               | DECISION**|
|         |                          | B: US-Only Baseline   |                         | operational status.|               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
| **DEC-  | **Data Classification &  | A: Three-Tier Class-  | **Option A: Three-Tier  | Zero breach risk;  | All           | **PENDING |
| 005**   | Patient Data Policy**    |    ification (Cat A/B;| Classification (Cat C   | contextual ethics &| Milestones    | USER      |
|         |                          |    Cat C Prohibited)  | Strictly Prohibited)**  | privacy laws noted;| (01–20)       | DECISION**|
|         |                          | B: Real PHI Pilot     |                         | Cat C prohibited.  |               |           |
+---------+--------------------------+-----------------------+-------------------------+--------------------+---------------+-----------+
```

---

## 11. Final Implementation Readiness Verdict

```
========================================================================================
                          FINAL READINESS VERDICT:
             READY FOR MILESTONE 01 — GOVERNANCE APPROVAL STILL REQUIRED
========================================================================================
```

### Action Required from Stakeholder
1. Provide your choices for decisions DEC-001 through DEC-005 (e.g., *"Approve Recommendations: 1A, 2A, 3A, 4A, 5A"* or state your specific preferences).
2. Authorize commencement of **Milestone 01: Repository & Development Environment Foundation**.

*(Antigravity is paused and awaiting your strategic selections above before proceeding to Milestone 01).*
