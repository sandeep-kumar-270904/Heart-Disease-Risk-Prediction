# HeartXAI 2.0 — Requirements Traceability Matrix (RTM)

**Document ID:** HXAI-REQ-008  
**Version:** 2.0.0  
**Phase:** Phase 2 — Product Requirements & System Scope  
**Status:** Complete / Ready for Review  
**Author:** Principal Systems Analyst & QA Lead  

---

## 1. Traceability Architecture & Objectives

The Requirements Traceability Matrix (RTM) links high-level healthcare business objectives and user needs to specific functional requirements, non-functional quality gates, architectural modules, and automated verification test cases.

This matrix ensures that:
1. Every business objective is fulfilled by at least one testable functional requirement.
2. Every functional requirement maps directly to an automated test case.
3. No scope creep, orphaned code, or dead-end features enter the codebase.

---

## 2. End-to-End Requirements Traceability Matrix

| Business Objective | User Need | Functional Req ID | NFR Mapping | Module | Acceptance Criteria | Future Automated Test Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OBJ-1: Algorithmic Transparency** | Understand which specific biomarkers drove risk score up or down. | **REQ-SHAP-01** | NFR-PERF-02, NFR-DAT-01 | Module 7 (SHAP) | Local Shapley values satisfy additivity error $\le 10^{-5}$. | `test_tree_shap_additivity_invariance` |
| **OBJ-1: Algorithmic Transparency** | Read explanations without confusing mathematical or AI jargon. | **REQ-SHAP-02** | NFR-USE-01, NFR-ACC-01 | Module 7 (SHAP) | Visual waterfall renders with plain-language bullet translation. | `test_shap_waterfall_rendering_e2e` |
| **OBJ-2: Clinical Feasibility** | Explore what lifestyle biomarker adjustments reduce risk safely. | **REQ-CF-01** | NFR-DAT-01, NFR-SEC-01 | Module 8 (Counterfactual) | Immutable attributes (Age, Sex, Anatomy) locked 100% of time. | `test_counterfactual_immutability_invariant` |
| **OBJ-2: Clinical Feasibility** | Real-time interactive feedback when adjusting lifestyle sliders. | **REQ-CF-02** | NFR-PERF-01, NFR-USE-02 | Module 8 (Counterfactual) | Slider drag updates projected risk in $< 150\text{ms}$. | `test_counterfactual_slider_dynamic_update_e2e` |
| **OBJ-3: Dual-Target Separation** | Know difference between current stenosis and future event risk. | **REQ-ML-01**, **REQ-ML-02** | NFR-PERF-02, NFR-REL-01 | Module 5 (ML Engine) | Calibrated CAD probability and 10-yr ASCVD risk segregated. | `test_dual_target_computational_independence` |
| **OBJ-3: Dual-Target Separation** | View risk scores with clear confidence intervals and tiers. | **REQ-UNCERT-01** | NFR-USE-01, NFR-ACC-01 | Module 6 (Uncertainty) | Dials render distinct tiers and OOD warnings when applicable. | `test_uncertainty_dashboard_ood_flag_e2e` |
| **OBJ-4: Enterprise Reliability** | Secure registration, login, and protected personal health data. | **REQ-AUTH-01**, **REQ-AUTH-02** | NFR-SEC-01, NFR-SEC-02 | Module 2 (Auth) | Bcrypt $\ge 12$, HttpOnly SameSite=Strict JWT cookies issued. | `test_auth_registration_and_httponly_session` |
| **OBJ-4: Enterprise Reliability** | Maintain longitudinal health history and track progress over time. | **REQ-HIST-01** | NFR-DAT-01, NFR-PERF-02 | Module 10 (History) | Time-series chart renders multiple checkups with deltas. | `test_longitudinal_trajectory_deltas` |
| **OBJ-4: Enterprise Reliability** | Export 1-page clinical briefing for doctor consultation visits. | **REQ-REP-01** | NFR-USE-01, NFR-PRI-01 | Module 14 (Reports) | Downloadable PDF/JSON contains complete summary on 1 page. | `test_clinical_briefing_pdf_generation` |
| **OBJ-4: Enterprise Reliability** | Enforce patient consent: doctors cannot browse patient records. | **REQ-PRIV-01** | NFR-PRI-02, NFR-SEC-03 | Module 16 (Privacy) | Doctor access blocked with 403 unless active grant exists. | `test_patient_gated_doctor_authorization` |
| **OBJ-4: Enterprise Reliability** | Audit all system, security, and clinical access events immutably. | **REQ-AUD-01** | NFR-OBS-01, NFR-DAT-01 | Module 20 (Audit) | All mutations and views generate immutable append-only rows. | `test_immutable_audit_logging_pipeline` |
| **OBJ-5: Inclusive Usability** | Accessible intake form with real-time range validation. | **REQ-ASSESS-01** | NFR-ACC-01, NFR-ACC-02 | Module 4 (Intake) | Wizard validates 13 biomarkers; full keyboard navigation. | `test_biomarker_intake_validation_and_keyboard` |
| **OBJ-5: Inclusive Usability** | Public educational portal and anonymous explainability sandbox. | **REQ-PUB-01**, **REQ-PUB-02** | NFR-PERF-01, NFR-ACC-01 | Module 1 (Public) | Zero tracking; synthetic sandbox operates without registration. | `test_public_sandbox_stateless_execution_e2e` |

---

## 3. Requirements Conflict, Ambiguity & Gap Analysis

In accordance with Section 9 of Prompt 02, an analysis of potential conflicts, ambiguities, and gaps was conducted:

| Analysis Dimension | Potential Issue Identified | Root Cause | Engineering Resolution in HeartXAI 2.0 |
| :--- | :--- | :--- | :--- |
| **Conflict Analysis** | Conflation between CAD Binary Prediction and 10-Year ASCVD Risk. | Original proposal loosely referred to both as "Heart Disease Risk". | **Strictly Resolved:** Partitioned into `REQ-ML-01` (binary CAD stenosis) and `REQ-ML-02` (ACC/AHA prospective ASCVD risk) with separate UI gauges and clear captions. |
| **Conflict Analysis** | Doctor Access vs Patient Privacy Sovereignty. | Unrestricted doctor browsing violates HIPAA / GDPR principles. | **Strictly Resolved:** Implemented `REQ-PRIV-01` requiring an explicit, time-bounded `patient_doctor_grants` record before any doctor can view a patient's chart. |
| **Ambiguity Analysis** | "Personalized Health Education" risk of generative clinical hallucination. | Using dynamic LLM generation for medical advice can produce unverified recommendations. | **Strictly Resolved:** Mandated in `REQ-EDU-01` that educational content is pulled from vetted, human-curated database records citing ACC/AHA guidelines. |
| **Ambiguity Analysis** | "Counterfactual Optimization" producing biologically impossible advice. | Unconstrained optimization can recommend reducing age or dropping blood pressure to lethal levels. | **Strictly Resolved:** Enforced in `REQ-CF-01` that Age, Sex, and Anatomy are strictly immutable ($\delta=0$) and modifiable markers are bounded by safe clinical floors. |
| **Missing Gap Analysis** | Model Integrity & Tamper Detection. | Original proposal lacked mechanisms to detect if model files were altered or swapped. | **Strictly Resolved:** Added `REQ-MLM-01` verifying model SHA-256 checksum at boot and logging exact model version in every inference record. |
| **Missing Gap Analysis** | Right to Erasure / GDPR Compliance. | Original proposal lacked account deletion and data portability mechanisms. | **Strictly Resolved:** Added `REQ-PRIV-02` providing complete cryptographic account deletion and JSON health data export. |

---

## 4. Review-II Presentation UML & Architecture Traceability Mapping

This section explicitly maps every class, component, and workflow from the official ANITS Review-II presentation (`HXAI-REF-001`) to the production-grade HeartXAI 2.0 architectural entities and functional requirements:

| Review-II Class / Diagram Entity | Review-II Responsibilities | HeartXAI 2.0 Architectural Mapping | Corresponding Functional Req IDs |
| :--- | :--- | :--- | :--- |
| **`Patient` Class** | `patientId`, `name`, `age`, `email`, `password`; `register()`, `login()`, `enterHealthData()`, `viewResults()` | Mapped to `User` entity (`role="PATIENT"`) + `PatientProfile` (demographic baseline) | **REQ-AUTH-01**, **REQ-AUTH-02**, **REQ-PROF-01**, **REQ-ASSESS-01** |
| **`MLModel` Class** | `modelName`, `algorithm`, `version`; `preprocessData()`, `predictRisk()` | Mapped to `model_registry` entity, `StandardScaler` pipeline, and calibrated XGBoost / HistGradientBoosting engine | **REQ-ML-01**, **REQ-ML-02**, **REQ-MLM-01** |
| **`Prediction` Class** | `predictionId`, `riskLevel`, `probability`, `date`; `getRiskLevel()`, `getProbability()` | Mapped to `inference_results` entity, featuring dual-target separation (CAD presence vs 10-Yr ASCVD) | **REQ-ML-01**, **REQ-ML-02**, **REQ-UNCERT-01** |
| **`Explanation` Class** | `explanationId`, `importantFactors`, `shapValues`; `generateSHAPExplanation()`, `getInsights()` | Mapped to `shap_explanations` entity, exact TreeSHAP C++ engine, and deterministic plain-language translation | **REQ-SHAP-01**, **REQ-SHAP-02** |
| **`CounterfactualAnalysis` Class**| `analysisId`, `originalRisk`, `suggestedChanges`, `newRisk`; `generateCounterfactual()`, `compareRisk()` | Mapped to `counterfactual_profiles` entity and constrained L1-norm optimization engine locking immutable traits | **REQ-CF-01**, **REQ-CF-02** |
| **`MedicalAssistance` Class** | `assistanceId`, `dietPlan`, `exerciseTips`, `lifestyleGuidance`; `getDietPlan()`, `getExerciseTips()` | Mapped to `educational_resources` entity with curated, guideline-traceable cardiovascular advice | **REQ-EDU-01** |
| **`DoctorConsultation` Class** | `doctorId`, `doctorName`, `specialization`, `hospitalName`, `contactNumber`, `location`; CRUD methods | Mapped to `doctors` directory entity, patient consent gates (`patient_doctor_grants`), and clinical review notes | **REQ-DOC-01**, **REQ-PRIV-01**, **REQ-REP-01** |
| **`HealthInsurance` Class** | `insuranceId`, `providerName`, `policyName`, `coverage`, `premium`, `waitingPeriod`, `exclusions`; CRUD methods | Mapped to `insurance_guides` entity, ACA preventative coverage rules, and diagnostic cost estimator | **REQ-INS-01**, **REQ-DIR-01** |
| **`AssessmentHistory` Class** | `historyId`, `predictionDate`, `riskLevel`, `notes`; `saveRecord()`, `getHistory()` | Mapped to `assessments` entity, longitudinal time-series analytics, and delta comparison engine | **REQ-HIST-01** |
| **`Admin` Class** | `adminId`, `name`, `email`, `password`; `login()`, `accessDashboard()`, `manageDoctors()`, `manageInsurance()` | Mapped to `User` entity (`role="ADMIN"`), system governance center, and directory CRUD router | **REQ-ADMIN-01**, **REQ-ADMIN-02**, **REQ-DIR-01**, **REQ-AUD-01** |

