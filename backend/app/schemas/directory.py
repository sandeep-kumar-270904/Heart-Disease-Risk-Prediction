"""HeartXAI 2.0 - Healthcare Directory & Educational Guidance Schemas."""

from pydantic import Field

from app.schemas.base import BaseSchema


class DoctorProfileDto(BaseSchema):
    """Cardiologist directory listing profile."""

    id: str
    full_name: str
    specialization: str
    qualification: str
    medical_license_number: str
    license_issuing_authority: str
    is_license_verified: bool
    hospital_affiliation: str
    city: str
    country_code: str
    contact_phone: str | None = None
    booking_url: str | None = None


class HospitalFacilityDto(BaseSchema):
    """Accredited cardiac facility and emergency department profile."""

    id: str
    name: str
    accreditation: str
    has_cardiac_emergency_24_7: bool
    has_catheterization_lab: bool
    emergency_phone: str
    address: str
    city: str
    country_code: str


class InsuranceGuidanceDto(BaseSchema):
    """Preventative cardiovascular insurance guidance metadata."""

    country_code: str
    regulatory_authority: str
    diagnostic_coverage_summary: str
    claims_checklist: list[str] = Field(default_factory=list)
    authorized_helpline: str


class EducationalResourceDto(BaseSchema):
    """Evidence-based cardiovascular lifestyle and dietary resource."""

    id: str
    title: str
    biomarker_code: str
    summary: str
    guideline_source: str
    diet_plan_summary: str
    exercise_tips_summary: str
    lifestyle_guidance: str
