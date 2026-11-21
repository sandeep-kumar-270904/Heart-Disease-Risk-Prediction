# HeartXAI 2.0 — Consolidated Product Scope
**Document ID:** HX-PR-003  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal Software Architect & Healthcare AI Product Engineer  
**Status:** Approved for Implementation Planning  
**Date:** November 2026  

---

## 1. Product Vision

**HeartXAI 2.0** is an explainable, non-diagnostic clinical decision support (CDS) and cardiovascular health risk assessment platform. It bridges the critical divide between predictive artificial intelligence and clinical transparency. 

By combining calibrated machine learning with local attribution explanations (TreeSHAP) and actionable, biologically constrained counterfactual guidance, HeartXAI empowers patients to understand their cardiovascular risk factors and facilitates meaningful, informed consultations with licensed medical professionals.

---

## 2. Target Users & User Personas

| Persona Name | Role | Profile Summary | Primary Goals in HeartXAI | Key Pain Points Addressed |
| :--- | :--- | :--- | :--- | :--- |
| **Sarah Jenkins** (52) | Patient / Self-Advocate | Executive with family history of premature CAD; elevated cholesterol. | Understand risk drivers, test lifestyle scenarios, export report for physician. | "Black-box" AI fear, medical jargon confusion, anxiety over uncalibrated online calculators. |
| **Marcus Chen** (44) | Patient / Active Lifestyle | Tech lead experiencing intermittent exertional chest tightness. | Fast symptom assessment, emergency indicator screening, cardiologist discovery. | Uncertainty whether symptoms warrant emergency care, lack of trusted directory. |
| **Elena Gomez** (68) | Patient / Senior Care | Retiree with hypertension and type 2 diabetes on multiple medications. | Track cardiovascular health over time, share assessment history with primary doctor. | Complex interfaces, inaccessible contrast/fonts, lack of secure physician sharing. |
| **Dr. Aris Thorne, MD** | Cardiologist / Clinical Reviewer | Attending cardiologist at regional academic medical center. | Review patient-shared assessments, inspect SHAP feature drivers, validate data integrity. | Distrust of uncalibrated consumer health apps, lack of transparent feature attribution. |
| **Devon Vance** | Administrator / Compliance Officer | Systems administrator & health data privacy specialist. | Monitor system health, review access logs, ensure regulatory compliance, manage directories. | Audit trail opacity, unauthorized PHI access risks, drift in ML inference latency. |

---

## 3. User Roles & Permission Matrix

HeartXAI enforces Role-Based Access Control (RBAC) backed by JWT claims and PostgreSQL row-level checks:

```
+------------------------------------+---------------------------------------------------------------+
| User Role                          | Permitted System Actions & Boundaries                         |
+------------------------------------+---------------------------------------------------------------+
| Unauthenticated Visitor            | - View landing page, product documentation, medical disclaimers|
|                                    | - Access public healthcare educational articles               |
|                                    | - Perform user registration and login                         |
+------------------------------------+---------------------------------------------------------------+
| Registered Patient (`patient`)     | - Complete cardiovascular health assessment intake            |
|                                    | - View calibrated CAD risk score and confidence interval      |
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
1. **Secure Patient Authentication & Identity Management:** Argon2id hashing, short-lived in-memory JWTs (15 min), HttpOnly refresh cookies with Redis rotation, optional TOTP MFA.
2. **Clinical Intake Questionnaire (14-Feature Canonical Contract):** Structured capture of cardiovascular biomarkers with automated unit conversion ($\text{mg/dL} \leftrightarrow \text{mmol/L}$) and real-time biological plausibility validation.
3. **Calibrated Machine Learning Risk Scoring (Task A):** Angiographic CAD classification ($P(\text{stenosis} \ge 50\% \mid \mathbf{x})$) generated via calibrated XGBoost, categorized into Low ($<20\%$), Moderate ($20\text{--}60\%$), and Elevated ($\ge 60\%$) tiers.
4. **Local Feature Attribution (TreeSHAP):** Interactive waterfall chart displaying top positive and negative risk contributors in plain clinical language.
5. **Constrained Actionable Counterfactual Engine:** Optimization algorithm generating realistic lifestyle modification scenarios strictly restricted to actionable variables (blood pressure, cholesterol, fasting glucose).
6. **Statutory Medical Disclaimers & Emergency Banners:** Prominent non-diagnostic clinical boundaries and dynamic emergency warnings when red-flag symptoms are indicated.
7. **Clinical Summary Dossier Export:** Downloadable, cryptographically hashed PDF report formatted for primary care physician review.
8. **Localized Healthcare Directory:** Searchable directory of verified cardiologists and cardiac hospitals filtered by country, city, and specialty.

### 4.2 Supporting Capabilities (Included in MVP)
1. **Longitudinal Assessment History:** Graphical tracking of patient risk scores, blood pressure, and cholesterol over successive assessments.
2. **Patient-to-Doctor Secure Sharing:** Time-limited (e.g., 72-hour), revocable cryptographic grant links allowing doctors to view a specific assessment without full patient account access.
3. **Immutable Audit Trail:** Append-only database logging of all PHI access, authentication events, and ML inference operations.
4. **Global Country Adaptation (ADR-011):** Configurable tenant settings for United States (`US`), India (`IN`), and United Kingdom (`UK`).

### 4.3 Optional & Future Capabilities (Deferred to Post-MVP)
1. **Task B Prospective 10-Year ASCVD Engine:** Deterministic calculation using the ACC/AHA 2013 Pooled Cohort Equations, kept strictly distinct from the ML model (Deferred to Phase 13 / Milestone 14 rule engine).
2. **Direct Electronic Health Record (EHR) Integration:** HL7 FHIR US Core profiles for automated lab value ingestion (Post-MVP / Enterprise tier).
3. **Live Insurance Formulary & Benefit Verification:** Real-time payer API connectivity (Post-MVP).
4. **Telehealth Video Consultation:** In-app WebRTC video calling between patients and directory doctors (Post-MVP).
5. **Wearable Device Integration:** Live streaming of continuous heart rate from Apple Health / Google Health Connect (Post-MVP).

### 4.4 Out-of-Scope Capabilities (Strict Anti-Scope)
- **Primary Diagnostic Medical Device:** HeartXAI shall never declare that a patient "has" coronary artery disease or a myocardial infarction.
- **Automated Prescription or Medication Dosage Adjustments:** The system shall never recommend specific drug brand names or dosages (e.g., "Take 20mg Atorvastatin").
- **Emergency Dispatch Automation:** The system shall not automatically trigger 911/999/112 calls or dispatch ambulances without user intervention.
- **Direct Monetization / Payment Processing:** Payment gateway integration is excluded from the initial open-access clinical release.

---

## 5. Reconciliation with Original Proposal (Review II Presentation)

The original HeartXAI presentation proposed an intelligent cardiovascular risk predictor. The audit verified that all core intentions of the original proposal have been preserved while elevating the engineering and scientific rigor:

| Original Review II Concept | HeartXAI 2.0 Engineering Implementation | Audit Status |
| :--- | :--- | :---: |
| ML-based Heart Disease Prediction | Calibrated XGBoost with Platt Scaling on Cleveland Catheterization Cohort | **Retained & Hardened** |
| Explainable Predictions | Local TreeSHAP Waterfall Charts & Interactive Attribution | **Retained & Enhanced** |
| Lifestyle Recommendations | Biologically Constrained Counterfactual Engine (DiCE) | **Retained & Constrained** |
| Doctor & Hospital Finder | Geo-filtered Directory with Emergency Hotline Integration | **Retained & Localized** |
| Medical Chatbot Assistant | Rule-Governed Clinical Guidance Module (Strict Medical Disclaimers) | **Refined for Safety** |
| General Heart Attack Risk Claim | Corrected to Angiographic Coronary Artery Disease Classification ($\ge 50\%$ stenosis) | **Scientifically Corrected** |

---

## 6. Scope Stability & Change Control

The scope defined in this document is locked for Milestones 01 through 20. Any proposed feature addition or modification must undergo formal Architecture Review Board evaluation and approval.
