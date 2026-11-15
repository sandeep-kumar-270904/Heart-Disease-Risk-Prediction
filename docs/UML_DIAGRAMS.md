# HeartXAI 2.0 — UML Architecture & System Design Models (UML 2.5.1)

**Document ID:** HXAI-ARCH-012  
**Version:** 3.0.0  
**Phase:** Phase 3 — System Architecture & Technical Design  
**Status:** Approved  
**Diagram Directory:** [`docs/diagrams/`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/)  

---

## 1. Overview of UML Specification Models

This document compiles the formal Unified Modeling Language (UML 2.5.1) models for **HeartXAI 2.0**. Each model bridges conceptual requirements to physical implementation, providing both inline renderable diagrams and links to editable PlantUML (`.puml`) source files.

---

## 2. Structural Models

### 2.1 Domain Class Diagram
*Editable Source:* [`docs/diagrams/uml_class_diagram.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_class_diagram.puml)  
*Description:* Defines all core domain entities, attributes, methods, and cardinalities, incorporating the 10 original ANITS Review-II classes.

```mermaid
classDiagram
    class User {
        +String id
        +String email
        +String role
        +String clinicianStatus
        +Boolean isActive
        +register()
        +login()
        +logout()
    }
    class PatientProfile {
        +String id
        +Date dateOfBirth
        +String biologicalSex
        +String preferredUnits
        +getAge()
    }
    class Assessment {
        +String id
        +Integer trestbps
        +Integer chol
        +Integer thalach
        +validateBiomarkers()
        +getFeatureVector()
    }
    class InferenceResult {
        +String id
        +Float cadProbability
        +String cadRiskTier
        +Float ascvd10yrRisk
        +String ascvdRiskTier
        +Float baseExpectedValue
    }
    class ShapExplanation {
        +String id
        +String featureName
        +Float shapValue
        +Integer rankImportance
        +String directionalImpact
    }
    class CounterfactualProfile {
        +String id
        +Float targetRiskThreshold
        +Float achievedRiskProbability
        +JSON modifiedBiomarkers
        +JSON immutableBiomarkers
    }
    class DoctorGrant {
        +String id
        +String status
        +DateTime expiresAt
        +isValid()
        +revoke()
    }
    class ClinicalNote {
        +String id
        +String noteContent
        +String signoffStatus
        +signoff()
    }

    User "1" *-- "0..1" PatientProfile : owns
    User "1" o-- "0..*" Assessment : creates
    User "1" o-- "0..*" DoctorGrant : grants_as_patient
    User "1" o-- "0..*" DoctorGrant : receives_as_doctor
    Assessment "1" *-- "1" InferenceResult : produces
    Assessment "1" *-- "0..*" ClinicalNote : receives
    InferenceResult "1" *-- "13" ShapExplanation : decomposes_into
    InferenceResult "1" *-- "0..*" CounterfactualProfile : derives
```

---

### 2.2 Package Diagram
*Editable Source:* [`docs/diagrams/uml_package_diagram.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_package_diagram.puml)  
*Description:* Defines the architectural layer boundaries and dependencies between frontend views, backend APIs, domain services, ML subsystems, and database models.

---

## 3. Behavioral Models

### 3.1 Use Case Diagram
*Editable Source:* [`docs/diagrams/uml_use_case.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_use_case.puml)  
*Description:* Maps system interactions across Guest, Patient, Doctor, and Administrator actors.

---

### 3.2 Sequence Diagrams for Core Workflows

#### Sequence 1: User Registration & Login
*Editable Source:* [`docs/diagrams/uml_sequence_registration_login.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_sequence_registration_login.puml)

#### Sequence 2: Assessment Intake, ML Prediction & TreeSHAP Attribution
*Editable Source:* [`docs/diagrams/uml_sequence_assessment_prediction_shap.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_sequence_assessment_prediction_shap.puml)

```mermaid
sequenceDiagram
    autonumber
    actor Patient
    participant SPA as SPA (React/TS)
    participant API as FastAPI Gateway
    participant ML as ML & ASCVD Engine
    participant SHAP as TreeSHAP Engine
    participant DB as PostgreSQL DB

    Patient->>SPA: Submits 13 Biomarkers
    SPA->>API: POST /api/v1/assessments
    API->>DB: Begin ACID Transaction
    API->>DB: INSERT INTO assessments
    API->>ML: predict_cad_and_ascvd(vector)
    ML-->>API: CAD Prob (0.44), ASCVD 10-Yr (9.8%)
    API->>DB: INSERT INTO inference_results
    API->>SHAP: compute_local_shap(vector)
    SHAP-->>API: 13 Shapley Attributions (Invariance <= 10^-5)
    API->>DB: INSERT INTO shap_explanations (13 rows)
    API->>DB: Commit Transaction
    API-->>SPA: HTTP 201 Created (Dual Dials, Waterfall Data)
    SPA-->>Patient: Displays Results Dashboard & Plain-Language Summary
```

#### Sequence 3: Counterfactual What-If Simulation
*Editable Source:* [`docs/diagrams/uml_sequence_counterfactual.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_sequence_counterfactual.puml)

#### Sequence 4: Longitudinal History & Delta Calculation
*Editable Source:* [`docs/diagrams/uml_sequence_history.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_sequence_history.puml)

#### Sequence 5: Clinical Briefing Report Generation
*Editable Source:* [`docs/diagrams/uml_sequence_report_generation.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_sequence_report_generation.puml)

#### Sequence 6: Administrator Governance & Clinician Approval
*Editable Source:* [`docs/diagrams/uml_sequence_admin_management.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_sequence_admin_management.puml)

---

### 3.3 Activity Diagrams
*Patient Activity Swimlane:* [`docs/diagrams/uml_activity_patient.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_activity_patient.puml)  
*Administrator Activity Swimlane:* [`docs/diagrams/uml_activity_admin.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_activity_admin.puml)

---

### 3.4 State Machine Diagram (Assessment Lifecycle)
*Editable Source:* [`docs/diagrams/uml_state_machine_assessment.puml`](file:///c:/Users/edhub/Desktop/Anti%20Gravity%20Projects/heartxai-2.0/docs/diagrams/uml_state_machine_assessment.puml)  
*States:* `DRAFT` $\rightarrow$ `VALIDATING` $\rightarrow$ `PROCESSING` $\rightarrow$ `COMPLETED` $\rightarrow$ `GRANTED_TO_DOCTOR` $\rightarrow$ `REVIEWED` $\rightarrow$ `PURGED (GDPR)`.
