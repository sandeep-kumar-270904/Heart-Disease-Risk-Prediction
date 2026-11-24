"""HeartXAI 2.0 - Country Configuration & Adapter Profile Schemas (ADR-011 / DEC-004)."""

from pydantic import Field

from app.schemas.auth import UnitSystem
from app.schemas.base import BaseSchema


class CountryProfileDto(BaseSchema):
    """Regional localization, unit convention, and statutory guidance profile."""

    country_code: str = Field(..., min_length=2, max_length=7)
    country_name: str
    default_unit_system: UnitSystem
    cholesterol_unit: str
    glucose_unit: str
    emergency_number: str
    emergency_label: str
    currency_code: str = Field(..., min_length=3, max_length=3)
    postal_code_regex: str
    clinical_guideline_reference: str
    privacy_framework: str
    regulatory_note: str


class CountryListResponse(BaseSchema):
    """Response container listing configured synthetic demonstration country adapters."""

    governance_decision: str
    profiles: list[CountryProfileDto]
