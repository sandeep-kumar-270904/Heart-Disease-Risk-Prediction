"""HeartXAI 2.0 - Clinical Assessment, Explainability & Synthetic Fixture Schemas."""

from datetime import datetime
from typing import Literal

from pydantic import Field, ValidationInfo, field_validator

from app.schemas.auth import UnitSystem
from app.schemas.base import BaseSchema

RiskStrata = Literal["unstratified"]
ShapDirection = Literal["increases_likelihood", "decreases_likelihood"]

CHOLESTEROL_MMOL_TO_MGDL = 38.67
GLUCOSE_MMOL_TO_MGDL = 18.016


class AssessmentCreateDto(BaseSchema):
    """Validated synthetic clinical intake payload covering the 13 UCI Cleveland biomarkers."""

    synthetic_fixture_confirmed: Literal[True] = Field(
        ...,
        description="Explicit confirmation that submission uses Category B synthetic values only (DEC-005)",
    )

    # Demographics
    age: float = Field(..., ge=18.0, le=100.0, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="1 = male; 0 = female")
    chest_pain_type: int = Field(
        ...,
        ge=0,
        le=3,
        description="0: typical angina, 1: atypical angina, 2: non-anginal pain, 3: asymptomatic",
    )

    # Vitals & Labs (supports metric mmol/L & US customary mg/dL normalization)
    unit_system: UnitSystem = Field(default="metric", description="Input measurement unit system")
    resting_bp: float = Field(
        ..., ge=70.0, le=240.0, description="Resting systolic blood pressure (mmHg)"
    )
    serum_cholesterol: float = Field(
        ..., ge=2.59, le=600.0, description="Serum cholesterol (mg/dL or mmol/L)"
    )
    fasting_blood_sugar: float = Field(
        ..., ge=0.0, le=500.0, description="Fasting blood sugar (mg/dL or mmol/L)"
    )

    # Electrocardiography & Exercise Stress
    resting_ecg: int = Field(
        ...,
        ge=0,
        le=2,
        description="0: normal, 1: ST-T wave abnormality, 2: LV hypertrophy",
    )
    max_heart_rate: float = Field(
        ..., ge=60.0, le=220.0, description="Maximum heart rate achieved (bpm)"
    )
    exercise_angina: int = Field(..., ge=0, le=1, description="1 = yes; 0 = no")
    st_depression: float = Field(
        ...,
        ge=0.0,
        le=6.2,
        description="ST depression induced by exercise relative to rest (oldpeak, mm)",
    )
    st_slope: int = Field(
        ...,
        ge=0,
        le=2,
        description="Slope of peak exercise ST segment: 0: upsloping, 1: flat, 2: downsloping",
    )

    # Advanced Cardiac Imaging (Optional - training-fold median/mode imputed if missing)
    major_vessels: int | None = Field(
        default=None,
        ge=0,
        le=3,
        description="Number of major vessels (0-3) colored by fluoroscopy",
    )
    thallium_stress: int | None = Field(
        default=None,
        ge=1,
        le=3,
        description="1: normal, 2: fixed defect, 3: reversible defect",
    )

    @field_validator("serum_cholesterol")
    @classmethod
    def normalize_cholesterol_units(cls, value: float, info: ValidationInfo) -> float:
        """Convert mmol/L cholesterol readings to canonical mg/dL when unit_system is metric."""
        units = info.data.get("unit_system", "metric")
        if units == "metric" and value < 20.0:
            normalized = round(value * CHOLESTEROL_MMOL_TO_MGDL, 2)
            if normalized < 100.0 or normalized > 600.0:
                raise ValueError(
                    "Normalized cholesterol must fall within physiological bounds [100, 600] mg/dL"
                )
            return normalized
        if value < 100.0 or value > 600.0:
            raise ValueError("Cholesterol in mg/dL must be between 100.0 and 600.0")
        return round(value, 2)

    @field_validator("fasting_blood_sugar")
    @classmethod
    def normalize_glucose_units(cls, value: float, info: ValidationInfo) -> float:
        """Convert mmol/L fasting glucose readings to canonical mg/dL when metric is active."""
        units = info.data.get("unit_system", "metric")
        if units == "metric" and 2.0 <= value < 30.0:
            return round(value * GLUCOSE_MMOL_TO_MGDL, 2)
        return round(value, 2)


class AssessmentDetailResponse(BaseSchema):
    """Complete assessment record combining validated biomarkers and Task A model output."""

    id: str
    patient_id: str
    age: float
    sex: int
    chest_pain_type: int
    resting_bp: float
    serum_cholesterol: float
    fasting_blood_sugar: float | None = Field(
        default=None,
        description="Preserved numeric glucose input (mg/dL); null for legacy binary-only records",
    )
    fasting_blood_sugar_gt_120: bool = Field(
        ...,
        description="UCI binary fasting blood sugar (>120 mg/dL) feature derived in preprocessing",
    )
    resting_ecg: int
    max_heart_rate: float
    exercise_angina: int
    st_depression: float
    st_slope: int
    major_vessels: int | None = None
    thallium_stress: int | None = None

    # Task A Model Outputs (DEC-003 Option A: Retrospective UCI CAD classification only)
    cad_likelihood_percent: float = Field(..., ge=0.0, le=100.0)
    risk_strata: RiskStrata = Field(
        default="unstratified",
        description="Unstratified pending clinical validation & physician review (DEC-002)",
    )
    ten_year_population_risk_percent: float | None = Field(
        default=None,
        description="Reserved for future research; strictly None in MVP per DEC-003 Option A",
    )
    model_version: str
    cohort_name: str
    data_provenance: str
    plain_language_summary: str
    emergency_warning_active: bool
    created_at: datetime


class FeatureImpactDto(BaseSchema):
    """Individual TreeSHAP biomarker attribution."""

    feature_name: str
    raw_patient_value: float
    unit: str
    cohort_average_value: float
    shap_value: float
    direction: ShapDirection
    plain_language_explanation: str


class ShapExplanationResponse(BaseSchema):
    """Complete exact local TreeSHAP explanation envelope."""

    assessment_id: str
    model_version: str
    base_value: float = Field(..., description="Expected cohort margin E[f(x)]")
    final_likelihood: float = Field(..., description="Final model decision margin f(x)")
    features: list[FeatureImpactDto]


class ScenarioSimulationRequest(BaseSchema):
    """Constrained counterfactual 'what-if' modification payload."""

    modified_features: dict[str, float] = Field(
        ...,
        description="Modifiable features: resting_bp, serum_cholesterol, fasting_blood_sugar, max_heart_rate",
    )


class ScenarioResultDto(BaseSchema):
    """Simulated likelihood delta and biological plausibility verification."""

    assessment_id: str
    baseline_likelihood_percent: float
    simulated_likelihood_percent: float
    delta_percent: float
    feasibility_score: float = Field(..., ge=0.0, le=1.0)
    is_biological_clamp_violated: bool
    violation_message: str | None = None


class SyntheticPatientRecord(BaseSchema):
    """Category B synthetic test record generated strictly for application fixtures (no PHI)."""

    is_synthetic: Literal[True] = Field(
        default=True, description="Immutable marker prohibiting clinical confusion"
    )
    mrn: str = Field(..., pattern=r"^SYN-\d{4}-\d{5}$", description="Synthetic test record ID")
    patient_name: str = Field(..., description="Clearly tagged fictional persona label")
    synthetic_generator_version: str = Field(..., description="Generator semantic version")
    generation_timestamp: datetime = Field(..., description="UTC generation timestamp")
    data_category: Literal["Category B — Synthetic Application Fixture"] = (
        "Category B — Synthetic Application Fixture"
    )
    intake: AssessmentCreateDto
