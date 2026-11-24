"""HeartXAI 2.0 - Authentication & User Profile Schemas."""

from datetime import date, datetime
from typing import Literal

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema

UserRole = Literal["PATIENT", "CLINICIAN", "ADMINISTRATOR"]
ClinicianStatus = Literal["N/A", "PENDING", "VERIFIED", "REJECTED"]
UnitSystem = Literal["metric", "us_customary"]
BiologicalSex = Literal["female", "male", "other"]


class RegisterRequest(BaseSchema):
    """Payload for new user registration with explicit educational consent."""

    email: EmailStr = Field(..., description="Unique email identifier")
    password: str = Field(..., min_length=12, max_length=128, description="Account passphrase")
    full_name: str = Field(..., min_length=2, max_length=100, description="Display name")
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=7,
        pattern=r"^(?:[A-Z]{2}|DEFAULT)$",
        description="ISO 3166-1 alpha-2 country code or DEFAULT",
    )
    consent_given: Literal[True] = Field(
        ...,
        description="Must explicitly consent to non-diagnostic educational terms",
    )


class LoginRequest(BaseSchema):
    """Payload for password-based authentication."""

    email: EmailStr = Field(..., description="Registered user email")
    password: str = Field(..., min_length=1, description="Account password")


class TokenResponse(BaseSchema):
    """Dual-token authentication response (access JWT + token type metadata)."""

    access_token: str = Field(..., description="Short-lived JWT bearer access token")
    token_type: Literal["bearer"] = Field(default="bearer", description="OAuth2 bearer token type")
    expires_in: int = Field(..., ge=1, description="Access token lifetime in seconds")


class UserProfileResponse(BaseSchema):
    """Public user identity summary returned after authentication or profile fetch."""

    id: str = Field(..., description="UUID identifier")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="RBAC role assignment")
    country_code: str = Field(..., description="Active ISO country profile code")
    clinician_status: ClinicianStatus | None = Field(
        default=None, description="Verification state for clinician accounts"
    )
    created_at: datetime = Field(..., description="Account creation UTC timestamp")


class PatientProfileUpdateDto(BaseSchema):
    """Mutable baseline profile preferences for a patient account."""

    preferred_units: UnitSystem = Field(default="metric", description="Preferred biomarker units")
    date_of_birth: date | None = Field(default=None, description="Optional birth date")
    biological_sex: BiologicalSex | None = Field(
        default=None, description="Optional baseline biological sex"
    )
    emergency_contact_name: str | None = Field(
        default=None, max_length=100, description="Optional emergency contact name"
    )
    emergency_contact_phone: str | None = Field(
        default=None, max_length=20, description="Optional emergency contact phone"
    )
