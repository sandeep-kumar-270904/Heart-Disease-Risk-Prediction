# HeartXAI 2.0 — Backend Service Layer Design & Business Logic

**Document ID:** `HX2-BE-007`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect & Lead Systems Engineer  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001 through ADR-011, HXAI-ARCH-008  

---

## 1. Service Layer Philosophy & Boundaries

In HeartXAI 2.0, the **Domain Service Layer** encapsulates all business logic, clinical calculations, authorization boundaries, and transactional coordination.

### 1.1 Architectural Invariants
1. **Zero HTTP Coupling:** Service methods accept strictly typed Pydantic DTOs or Python primitives; they never receive FastAPI `Request`, `Response`, or `Header` objects.
2. **Repository Abstraction:** Services do not construct raw SQL or interact directly with database cursors; all persistence operations route through Unit of Work (`UnitOfWork`) and domain repositories.
3. **Discrete Transaction Boundaries:** A single service method execution corresponds to an atomic database transaction. If any sub-operation fails (e.g., TreeSHAP calculation), the entire transaction rolls back.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      SERVICE TRANSACTION ORCHESTRATION                 │
├────────────────────────────────────────────────────────────────────────┤
│ [ HTTP Route Handler ]                                                 │
│       │                                                                │
│       ▼ (Invokes Domain Service Method)                                │
│ [ AssessmentService.submit_assessment(patient_id, data) ]              │
│       │                                                                │
│       ├── 1. Validate physiological boundaries & normalize units       │
│       ├── 2. Evaluate acute symptoms (Emergency alert check)           │
│       ├── 3. Execute ML Inference (InferenceService -> XGBoost)        │
│       ├── 4. Execute TreeSHAP Attribution (ExplainabilityService)      │
│       ├── 5. Persist Assessment, Inference, SHAP via UnitOfWork        │
│       └── 6. Record Audit Event (AuditService)                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Domain Services Specification

---

### Service 01: `AssessmentService`
- **Location:** `app/services/assessment_service.py`
- **Core Responsibilities:**
  - Ingestion, validation, and normalization of the 13 clinical biomarkers.
  - Unit conversion ($\text{mmol/L} \rightarrow \text{mg/dL}$ for canonical storage).
  - Identification of acute emergency symptoms (resting typical angina + severe hypertension).
  - Orchestration of inference and explainability pipelines within an atomic Unit of Work.
- **Key Operations:**
  - `submit_assessment(patient_id: str, data: AssessmentCreateDto) -> AssessmentDetailResponse`
  - `get_assessment_by_id(assessment_id: str, requesting_user: User) -> AssessmentDetailResponse`
  - `get_patient_assessment_history(patient_id: str, params: PaginationParams) -> PaginatedResponse[AssessmentSummaryDto]`
  - `get_longitudinal_trends(patient_id: str, range_filter: str) -> TrendDataResponse`
- **Business Rules:**
  - Enforces `patient_id` matches `requesting_user.id` (or valid clinician grant).
  - Flags median-imputed features if optional imaging variables (`ca`, `thal`) are omitted.
  - Automatically raises `AcuteEmergencyFlag` if systolic BP $> 180\text{ mmHg}$ with resting angina.
- **Transaction Boundary:** Enclosed in single `UnitOfWork` session; commits assessment, inference, and SHAP vectors simultaneously.

---

### Service 02: `InferenceService`
- **Location:** `app/services/inference_service.py`
- **Core Responsibilities:**
  - Loads, verifies, and executes the active production model artifact (`cleveland_xgboost_v2.4.1.json`).
  - Preprocesses feature arrays (scaling, categorical encoding).
  - Computes continuous probability and 95% Wilson score confidence interval.
  - Maps probability to calibrated categorical risk strata (`Low < 30%`, `Moderate 30%–69%`, `Elevated ≥ 70%`).
- **Key Operations:**
  - `predict_cad_likelihood(features: RawFeatureVector) -> PredictionOutput`
  - `get_model_metadata() -> ModelVersionInfo`
- **Failure Scenarios:**
  - Missing model artifact or checksum mismatch raises `ModelIntegrityException` at startup.
  - Inference timeout ($> 500\text{ms}$) terminates execution safely, returning `MLInferenceTimeoutException`.

---

### Service 03: `ExplainabilityService`
- **Location:** `app/services/explainability_service.py`
- **Core Responsibilities:**
  - Instantiates `shap.TreeExplainer` for the active tree ensemble.
  - Calculates local Shapley values ($\phi_i$) for all 13 features.
  - Generates plain-language educational explanations for each feature's directional impact.
- **Key Operations:**
  - `compute_shap_attributions(model, feature_array) -> List[FeatureImpactDto]`
  - `get_shap_for_assessment(assessment_id: str, requesting_user: User) -> ShapExplanationResponse`
- **Business Rules:**
  - Enforces that $\sum \phi_i = f(x) - E[f(x)]$ within float tolerance ($10^{-5}$).
  - Strictly maps directional symbols (`▲` crimson increases risk, `▼` blue decreases risk).

---

### Service 04: `CounterfactualService`
- **Location:** `app/services/counterfactual_service.py`
- **Core Responsibilities:**
  - Simulates hypothetical "what-if" modifications to modifiable variables (`resting_bp`, `serum_cholesterol`, `fasting_blood_sugar`, `max_heart_rate`).
  - Evaluates biological feasibility bounds.
  - Computes simulated likelihood delta relative to baseline assessment.
- **Key Operations:**
  - `simulate_scenario(assessment_id: str, modifications: dict, user: User) -> ScenarioResultDto`
- **Business Rules:**
  - Rejects attempts to modify non-modifiable biological variables (Age, Biological Sex).
  - Flags violation if simulated value is outside biologically viable outpatient human ranges (e.g., BP $< 60\text{ mmHg}$).

---

### Service 05: `DirectoryService`
- **Location:** `app/services/directory_service.py`
- **Core Responsibilities:**
  - Routes healthcare provider and facility queries through the active country adapter (ADR-011).
  - Handles caching, pagination, and external registry fallbacks.
- **Key Operations:**
  - `search_doctors(country: str, filters: DoctorSearchParams) -> PaginatedResponse[DoctorProfileDto]`
  - `search_hospitals(country: str, filters: HospitalSearchParams) -> PaginatedResponse[HospitalFacilityDto]`
  - `get_insurance_guidance(country: str) -> InsuranceGuidanceDto`
  - `get_emergency_hotline(country: str) -> EmergencyHotlineDto`
- **External Integration Fallback:**
  - If a country registry API (e.g., India NMC) suffers a network timeout, returns cached directory data with `is_cached_result: true`.

---

### Service 06: `ReportService`
- **Location:** `app/services/report_service.py`
- **Core Responsibilities:**
  - Compiles structured HTML/CSS templates for clinical consultation summaries.
  - Generates pixel-perfect PDF binaries using `weasyprint`.
  - Enforces ownership authorization prior to report streaming.
- **Key Operations:**
  - `generate_consultation_pdf(assessment_id: str, user: User) -> bytes`
- **Security Rules:**
  - Disallows caching of sensitive PDF binaries in public static directories; streams directly from memory with `Content-Disposition: attachment; filename="..."`.

---

### Service 07: `AuditService`
- **Location:** `app/services/audit_service.py`
- **Core Responsibilities:**
  - Writes immutable security, access, and governance audit events.
  - Hashes previous event records to ensure cryptographic append-only integrity.
- **Key Operations:**
  - `log_event(actor_id: str, role: str, action: str, resource: str, ip: str, status: str, details: dict)`
  - `query_logs(filters: AuditFilterParams) -> PaginatedResponse[AuditLogItemDto]`
