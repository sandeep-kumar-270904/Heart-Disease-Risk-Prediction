# HeartXAI 2.0 — API Request & Response Schema Specifications

**Document ID:** `HX2-BE-005`  
**Version:** `1.0.0`  
**Phase:** Phase 7 — Backend Engineering Architecture & API Implementation Plan  
**Status:** Approved Architectural Specification  
**Author:** Principal Backend Architect & Pydantic Specialist  
**Traceability:** FR-001–FR-062, NFR-001–NFR-028, ADR-001 through ADR-011, HXAI-ARCH-011  

---

## 1. Schema Design Standards (Pydantic v2)

All request and response data models are defined using **Pydantic v2** (`pydantic.BaseModel`).
- **Strict Parsing:** `extra = "forbid"` is enforced on all input schemas to reject unrecognized fields.
- **Type Coercion & Bounds:** Numeric bounds are enforced via `Field(ge=..., le=...)`.
- **Serialization:** Decimal precision is preserved, and dates are serialized strictly in ISO-8601 UTC format.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PYDANTIC V2 SCHEMA HIERARCHY                         │
├────────────────────────────────────────────────────────────────────────┤
│ BaseModel                                                              │
│   ├── BaseSchema (config: from_attributes = True, extra = "forbid")   │
│   │     ├── RequestDTOs (AssessmentCreateDto, LoginRequest, etc.)      │
│   │     └── ResponseDTOs (AssessmentDetailResponse, etc.)             │
│   └── ErrorEnvelope (Standardized Stripe-style error structure)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication & Profile Schemas

```python
from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

# --- AUTHENTICATION ---
class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    country_code: str = Field(..., min_length=2, max_length=2) # ISO-3166-1 alpha-2
    consent_given: Literal[True] = Field(..., description="Must explicitly consent to non-diagnostic educational terms")

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserProfileResponse(BaseSchema):
    id: str
    email: EmailStr
    full_name: str
    role: Literal["PATIENT", "CLINICIAN", "ADMINISTRATOR"]
    country_code: str
    clinician_status: Optional[Literal["PENDING", "VERIFIED", "REJECTED"]] = None
    created_at: datetime

# --- PATIENT PROFILES ---
class PatientProfileUpdateDto(BaseSchema):
    preferred_units: Literal["metric", "us_customary"] = "metric"
    date_of_birth: Optional[date] = None
    biological_sex: Optional[Literal["female", "male", "other"]] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
```

---

## 3. Clinical Assessment & Prediction Schemas

```python
# --- RAW CLINICAL INPUT DTO ---
class AssessmentCreateDto(BaseSchema):
    # Demographics
    age: float = Field(..., ge=18.0, le=100.0, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="1 = male; 0 = female")
    chest_pain_type: int = Field(..., ge=0, le=3, description="0: typical, 1: atypical, 2: non-anginal, 3: asymptomatic")
    
    # Vitals & Labs (supports metric & customary)
    unit_system: Literal["metric", "us_customary"] = "metric"
    resting_bp: float = Field(..., ge=70.0, le=240.0, description="Resting systolic blood pressure (mmHg)")
    serum_cholesterol: float = Field(..., ge=2.59, le=600.0, description="Serum cholesterol (mg/dL or mmol/L)")
    fasting_blood_sugar: float = Field(..., ge=0.0, le=500.0, description="Fasting blood sugar (mg/dL or mmol/L)")
    
    # Electrocardiography & Stress
    resting_ecg: int = Field(..., ge=0, le=2, description="0: normal, 1: ST-T wave abnormality, 2: LV hypertrophy")
    max_heart_rate: float = Field(..., ge=60.0, le=220.0, description="Maximum heart rate achieved (bpm)")
    exercise_angina: int = Field(..., ge=0, le=1, description="1 = yes; 0 = no")
    st_depression: float = Field(..., ge=0.0, le=6.2, description="ST depression induced by exercise relative to rest (oldpeak)")
    st_slope: int = Field(..., ge=0, le=2, description="Slope of peak exercise ST segment: 0: up, 1: flat, 2: down")
    
    # Advanced Imaging (Optional - imputed if missing)
    major_vessels: Optional[int] = Field(None, ge=0, le=3, description="Number of major vessels (0-3) colored by fluoroscopy")
    thallium_stress: Optional[int] = Field(None, ge=1, le=3, description="1: normal, 2: fixed defect, 3: reversible defect")

    @field_validator("serum_cholesterol")
    @classmethod
    def validate_cholesterol_units(cls, v: float, info) -> float:
        # If mmol/L is passed, normalize to mg/dL for canonical storage
        units = info.data.get("unit_system", "metric")
        if units == "metric" and v < 20.0: # Value was submitted in mmol/L
            return round(v * 38.67, 2)
        return v

# --- ASSESSMENT RESPONSE DTO ---
class AssessmentDetailResponse(BaseSchema):
    id: str
    patient_id: str
    age: float
    sex: int
    chest_pain_type: int
    resting_bp: float
    serum_cholesterol: float
    fasting_blood_sugar: float
    resting_ecg: int
    max_heart_rate: float
    exercise_angina: int
    st_depression: float
    st_slope: int
    major_vessels: Optional[int]
    thallium_stress: Optional[int]
    
    # Model Inferences
    cad_likelihood_percent: float
    confidence_interval: List[float] # [lower, upper]
    risk_strata: Literal["low", "moderate", "elevated"]
    ten_year_population_risk_percent: Optional[float]
    model_version: str
    cohort_name: str
    plain_language_summary: str
    emergency_warning_active: bool
    created_at: datetime
```

---

## 4. Explainability (SHAP) & Counterfactual Schemas

```python
class FeatureImpactDto(BaseSchema):
    feature_name: str
    raw_patient_value: float
    unit: str
    cohort_average_value: float
    shap_value: float
    direction: Literal["increases_likelihood", "decreases_likelihood"]
    plain_language_explanation: str

class ShapExplanationResponse(BaseSchema):
    assessment_id: str
    model_version: str
    base_value: float # Expected cohort value E[f(x)]
    final_likelihood: float # f(x)
    features: List[FeatureImpactDto]

class ScenarioSimulationRequest(BaseSchema):
    modified_features: dict[str, float] = Field(
        ..., 
        description="Key-value pairs of modifiable features: resting_bp, serum_cholesterol, fasting_blood_sugar, max_heart_rate"
    )

class ScenarioResultDto(BaseSchema):
    assessment_id: str
    baseline_likelihood_percent: float
    simulated_likelihood_percent: float
    delta_percent: float
    feasibility_score: float
    is_biological_clamp_violated: bool
    violation_message: Optional[str] = None
```

---

## 5. Healthcare Directory & Country Guidance Schemas

```python
class DoctorProfileDto(BaseSchema):
    id: str
    full_name: str
    specialization: str
    qualification: str
    medical_license_number: str
    license_issuing_authority: str # e.g., "National Medical Commission (India)"
    is_license_verified: bool
    hospital_affiliation: str
    city: str
    country_code: str
    contact_phone: Optional[str]
    booking_url: Optional[str]

class HospitalFacilityDto(BaseSchema):
    id: str
    name: str
    accreditation: str # e.g., "NABH Accredited"
    has_cardiac_emergency_24_7: bool
    has_catheterization_lab: bool
    emergency_phone: str
    address: str
    city: str
    country_code: str

class InsuranceGuidanceDto(BaseSchema):
    country_code: str
    regulatory_authority: str # e.g., "IRDAI (India)"
    diagnostic_coverage_summary: str
    claims_checklist: List[str]
    authorized_helpline: str
```

---

## 6. Standardized Error Response Schemas (Stripe Model)

```python
class ApiErrorDetail(BaseSchema):
    param: Optional[str] = None
    code: str
    message: str

class ApiErrorBody(BaseSchema):
    type: Literal[
        "validation_error", 
        "authentication_error", 
        "authorization_error", 
        "resource_not_found", 
        "conflict_error", 
        "rate_limit_exceeded", 
        "clinical_boundary_error", 
        "internal_server_error"
    ]
    code: str
    param: Optional[str] = None
    message: str
    details: Optional[List[ApiErrorDetail]] = None

class ApiErrorEnvelope(BaseSchema):
    error: ApiErrorBody
```
