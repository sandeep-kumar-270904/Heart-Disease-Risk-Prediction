# HeartXAI 2.0 — Data Flow Diagrams (DFD) & Information Lifecycle

**Document ID:** HXAI-ARCH-013  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved  
**Diagram Sources:** [`docs/diagrams/dfd_context_level_0.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/dfd_context_level_0.puml), [`docs/diagrams/dfd_level_1.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/dfd_level_1.puml), [`docs/diagrams/dfd_level_2_assessment_ml.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/dfd_level_2_assessment_ml.puml)  

---

## 1. Context-Level Data Flow Diagram (Level 0)

*Editable Source:* [`docs/diagrams/dfd_context_level_0.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/dfd_context_level_0.puml)

```mermaid
graph LR
    Guest["Public Visitor"]
    Patient["Patient"]
    Doctor["Clinician"]
    Admin["Administrator"]

    HeartXAI(("0.0 HeartXAI 2.0 Platform"))

    DB[("PostgreSQL DB")]
    ModelStore["Model File (.joblib)"]

    Guest -->|1. Sandbox Biomarkers| HeartXAI
    HeartXAI -->|2. Educational Content & Sandbox Results| Guest

    Patient -->|3. Registration & 13 Biomarkers| HeartXAI
    HeartXAI -->|4. Risk Scores, SHAP Waterfall & Briefings| Patient

    Doctor -->|5. Credentials & Review Notes| HeartXAI
    HeartXAI -->|6. Authorized Patient Charts| Doctor

    Admin -->|7. Verification & Audit Queries| HeartXAI
    HeartXAI -->|8. System Telemetry & Audit Logs| Admin

    HeartXAI <-->|9. Read/Write ACID Data & Audit Logs| DB
    HeartXAI <--|10. Verified Pipeline Artifact| ModelStore
```

---

## 2. Level 1 Data Flow Diagram (Subsystem Deconstruction)

*Editable Source:* [`docs/diagrams/dfd_level_1.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/dfd_level_1.puml)

```mermaid
graph TD
    User["User (Patient / Doctor / Admin)"]
    Doctor["Clinician"]

    P1(("1.0 Authentication & Sessions"))
    P2(("2.0 Clinical Intake & Validation"))
    P3(("3.0 ML Inference & Stratification"))
    P4(("4.0 Explainability & Counterfactuals"))
    P5(("5.0 Care Consent & Notes"))
    P6(("6.0 Audit Logging Engine"))

    D1[("D1: Users & Profiles")]
    D2[("D2: Assessments")]
    D3[("D3: Inferences & Explanations")]
    D4[("D4: Doctor Grants & Notes")]
    D5[("D5: Immutable Audit Logs")]

    User -->|Credentials| P1
    P1 -->|Hashed User| D1
    P1 -->|Audit Event| P6

    User -->|13 Biomarkers| P2
    P2 -->|Validated Intake| D2
    P2 -->|Feature Vector| P3

    P3 -->|CAD Prob & ASCVD 10-Yr| D3
    P3 -->|Decision Margins| P4
    P4 -->|13 Shapley Values & CF Deltas| D3
    P3 -->|Dual Dials| User
    P4 -->|Waterfall & Sliders| User

    User -->|Grant / Revoke Doctor Access| P5
    P5 -->|Consent Status| D4
    Doctor -->|Request Patient Chart| P5
    P5 -->|Verify Active Grant| D4
    P5 -->|Clinical Telemetry| Doctor
    Doctor -->|Signed Review Note| P5
    P5 -->|Persist Note| D4

    P1 -->|Auth Logs| P6
    P2 -->|Intake Logs| P6
    P5 -->|Consent Logs| P6
    P6 -->|Append-Only| D5
```

---

## 3. Level 2 Data Flow Diagram: Clinical Assessment & ML Pipeline

*Editable Source:* [`docs/diagrams/dfd_level_2_assessment_ml.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/dfd_level_2_assessment_ml.puml)

```mermaid
graph TD
    Patient["Patient Input"] --> P31(("3.1 Range & Enum Validator"))
    P31 -->|Validated Vector| P32(("3.2 OOD Bounds Check"))
    P32 -->|In-Distribution Vector| P33(("3.3 StandardScaler Normalization"))
    P32 -.->|OOD Outlier Flag| D3[("D3: Inferences Store")]

    P33 -->|Normalized Vector z| P34(("3.4 Calibrated XGBoost Inference"))
    P34 -->|P(CAD >= 50%)| D3
    P34 -->|Raw Margin f(x)| P41(("4.1 TreeSHAP C++ Attributor"))

    P31 -->|Demographics & Vitals| P35(("3.5 ACC/AHA 10-Yr ASCVD Equations"))
    P35 -->|10-Year Risk %| D3

    P41 -->|Local Shapley Values phi| P42(("4.2 Invariance Check (<= 10^-5)"))
    P42 -->|Verified 13 Shapley Rows| D3
    P42 -->|Ranked Features| P43(("4.3 Plain-Language Translator"))
    P43 -->|Human-Readable Summary| ResultsView["Patient Results View"]

    Patient -->|What-If Biomarker Slider| P44(("4.4 Constrained Counterfactual Solver"))
    P44 -->|Perturbed Vector (Age/Sex Locked)| P34
    P44 -->|Feasible Target Deltas| D3
```

---

## 4. Clinical Data Lifecycle Architecture

```mermaid
stateDiagram-v2
    [*] --> Ingestion : Patient inputs biomarkers via client wizard
    Ingestion --> Validation : Zod client + Pydantic server range checks
    Validation --> Processing : In-process ML inference & TreeSHAP traversal
    Processing --> Persistence : Atomic commit to PostgreSQL relational tables
    Persistence --> AccessAndAudit : Accessed by patient or authorized doctor (Audit logged)
    AccessAndAudit --> Archival : Retained for longitudinal trend comparison
    Archival --> Erasure : User executes GDPR Right to Erasure
    Erasure --> [*] : Cascading cryptographic purge from database
```
