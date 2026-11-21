# HeartXAI 2.0 — Consolidated Product Scope
**Document ID:** HX-PR-003  
**Version:** 2.0.0 (Phase 12.1 Revision)  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Principal Software Architect & Healthcare AI Product Engineer  
**Status:** Approved for Implementation Planning — Task B Removed from MVP Scope  
**Date:** November 2026  

---

## 1. Product Vision

**HeartXAI 2.0** is an explainable, non-diagnostic clinical decision support (CDS) exploration and educational health assessment platform. It bridges the critical divide between predictive artificial intelligence and clinical transparency. 

By combining calibrated machine learning with local attribution explanations (TreeSHAP) and actionable, biologically constrained counterfactual scenarios, HeartXAI demonstrates how explainable AI can assist patients and healthcare professionals in exploring cardiovascular biomarker patterns—without ever providing automated diagnoses or unsubstantiated prospective risk claims.

---

## 2. Target Users & User Personas (100% Synthetic Personas)

All personas and test cases used during development, testing, and demonstration are **100% synthetic constructs** with zero connection to real patient records:

| Persona Name | Role | Profile Summary | Primary Goals in HeartXAI | Key Pain Points Addressed |
| :--- | :--- | :--- | :--- | :--- |
| **Sarah Jenkins** (52) | Synthetic Patient Persona | Executive with family history of premature CAD; elevated cholesterol. | Explore biomarker patterns, review SHAP waterfall chart, export PDF summary. | "Black-box" AI fear, medical jargon confusion, anxiety over uncalibrated online calculators. |
| **Marcus Chen** (44) | Synthetic Patient Persona | Active professional experiencing exertional chest tightness. | Fast symptom intake, emergency indicator screening, directory discovery. | Uncertainty whether symptoms warrant emergency care, lack of trusted directory. |
| **Elena Gomez** (68) | Synthetic Patient Persona | Retiree with hypertension on multiple medications. | Explore biomarker scenarios over time, test sharing with primary physician. | Complex interfaces, inaccessible contrast/fonts, lack of secure physician sharing. |
| **Dr. Aris Thorne, MD** | Clinician Reviewer Persona | Attending cardiologist at regional academic medical center. | Review shared synthetic assessments, inspect SHAP feature drivers, append clinical notes. | Distrust of uncalibrated consumer health apps, lack of transparent feature attribution. |
| **Devon Vance** | Admin / Compliance Officer | Systems administrator & health data privacy specialist. | Monitor system health, review audit logs, verify security controls, manage directories. | Audit trail opacity, unauthorized PHI access risks, drift in ML inference latency. |

---

## 3. User Roles & Permission Matrix

```
+------------------------------------+---------------------------------------------------------------+
| User Role                          | Permitted System Actions & Boundaries                         |
+------------------------------------+---------------------------------------------------------------+
| Unauthenticated Visitor            | - View landing page, product documentation, medical disclaimers|
|                                    | - Access public healthcare educational articles               |
|                                    | - Perform user registration and login                         |
+------------------------------------+---------------------------------------------------------------+
| Registered Patient (`patient`)     | - Complete cardiovascular health assessment intake            |
|                                    | - View calibrated Task A CAD classification output            |
|                                    | - Explore interactive TreeSHAP local explanations             |
|                                    | - Simulate constrained counterfactual lifestyle changes       |
|                                    | - Export signed clinical summary reports (PDF)                |
|                                    | - Search localized doctor and hospital directories            |
|                                    | - Generate time-limited, revocable doctor access grants       |
|                                    | - Access self-service data export and account deletion        |
+------------------------------------+---------------------------------------------------------------+
| Licensed Clinician (`doctor`)      | - Manage verified professional profile (NPI / GMC / NMC)       |
|                                    | - View patient assessments via valid consent grant tokens     |
|                                    | - Add clinical review notes to shared assessments             |
|                                    | - Export clinician-tailored longitudinal summary dossiers     |
+------------------------------------+---------------------------------------------------------------+
| System Administrator (`admin`)     | - Manage user account statuses (suspend, reactivate)          |
|                                    | - Monitor system metrics, API latency, and ML inference logs  |
|                                    | - Review immutable audit trail and security access events     |
|                                    | - Curate verified doctor, hospital, and emergency directories |
+------------------------------------+---------------------------------------------------------------+
```

---

## 4. Feature Taxonomy & Scope Categorization

### 4.1 Core Capabilities (Mandatory for MVP)
1. **Secure Patient Identity Management:** Argon2id hashing, short-lived in-memory JWTs (15 min), HttpOnly refresh cookies with Redis token-family rotation, optional TOTP MFA.
2. **Clinical Intake Questionnaire (14-Feature Canonical Contract):** Structured capture of cardiovascular biomarkers with automated unit conversion ($\text{mg/dL} \leftrightarrow \text{mmol/L}$) and real-time physiological plausibility validation.
3. **Calibrated Machine Learning Risk Scoring (Task A Only):** Experimental classification of coronary stenosis status ($P(\text{stenosis} \ge 50\% \mid \mathbf{x})$) generated via calibrated XGBoost on the retrospective Cleveland cohort, categorized into Low ($<20\%$), Moderate ($20\text{--}60\%$), and Elevated ($\ge 60\%$) tiers.
4. **Local Feature Attribution (TreeSHAP):** Interactive waterfall chart displaying top positive and negative risk contributors with clear statements that SHAP reflects statistical association, not biological causation.
5. **Constrained Actionable Counterfactual Engine:** Optimization algorithm generating realistic lifestyle modification scenarios strictly restricted to actionable variables (blood pressure, cholesterol, fasting glucose), with immutable features strictly frozen.
6. **Statutory Medical Disclaimers & Emergency Banners:** Prominent non-diagnostic clinical boundaries and dynamic emergency warnings when red-flag symptoms are entered.
7. **Clinical Summary Dossier Export:** Downloadable, cryptographically hashed PDF report formatted for physician review.
8. **Localized Healthcare Directory:** Searchable directory of verified cardiac care centers and hospitals across US, IN, and UK launch hubs, with emergency quick-dial contacts.

### 4.2 Supporting Capabilities (Included in MVP)
1. **Longitudinal Assessment History:** Graphical tracking of synthetic patient scores over successive assessments.
2. **Patient-to-Doctor Secure Sharing:** Time-limited (72-hour), revocable cryptographic grant links allowing doctors to view a specific assessment.
3. **Immutable Audit Trail:** Append-only database logging of all system access, authentication events, and ML inference operations.
4. **Global Country Adaptation (ADR-011):** Configurable tenant settings for United States (`US`), India (`IN`), and United Kingdom (`UK`).

### 4.3 Optional & Future Capabilities (Deferred to Post-MVP Research)
1. **Task B Prospective 10-Year ASCVD Risk Engine:** Rigorous prospective risk calculator. **Excluded from MVP.** Relegated to future research pending clinical guideline updates (ACC/AHA PREVENT adoption, UK QRISK3) and formal clinical advisory review.
2. **Direct Electronic Health Record (EHR) Integration:** HL7 FHIR US Core profiles for automated lab value ingestion (Post-MVP).
3. **Live Insurance Formulary & Benefit Verification:** Real-time payer API connectivity (Post-MVP).
4. **Telehealth Video Consultation:** In-app WebRTC video calling between patients and directory doctors (Post-MVP).
5. **Wearable Device Streaming:** Continuous heart rate streaming from Apple Health / Google Health Connect (Post-MVP).

### 4.4 Out-of-Scope Capabilities (Strict Anti-Scope)
- **Primary Diagnostic Medical Device:** HeartXAI shall never declare that a patient "has" heart disease or is having a heart attack.
- **Automated Prescription or Medication Dosage Adjustments:** The system shall never recommend specific drug brand names or dosages.
- **Emergency Dispatch Automation:** The system shall not automatically trigger 911/999/112 calls or dispatch ambulances without user intervention.
- **Real Patient Data Ingestion in Non-Production:** Strict prohibition against real PHI in development or staging.

---

## 5. Scope Stability & Change Control

The scope defined in this document is locked for Milestones 01 through 20. Any proposed feature addition or scope change must undergo formal Architecture Review Board evaluation and approval.
