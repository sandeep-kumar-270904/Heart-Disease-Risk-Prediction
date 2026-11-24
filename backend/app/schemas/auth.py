"""HeartXAI 2.0 - Authentication & User Profile Schemas."""

from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import BaseSchema

UserRole = Literal["PATIENT", "CLINICIAN", "ADMINISTRATOR"]
ClinicianStatus = Literal["N/A", "PENDING", "VERIFIED", "REJECTED"]
UnitSystem = Literal["metric", "us_customary"]
BiologicalSex = Literal["female", "male", "other"]

ALLOWED_SYNTHETIC_DOMAINS = frozenset({"example.com", "example.org", "example.net"})


class RegisterRequest(BaseSchema):
    """Payload for controlled synthetic-demo persona registration (Category C prohibited)."""

    email: EmailStr = Field(..., description="Synthetic demo email identifier")
    password: str = Field(..., min_length=12, max_length=128, description="Account passphrase")
    full_name: str = Field(..., min_length=2, max_length=100, description="Synthetic persona label")
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
    synthetic_persona_acknowledged: Literal[True] = Field(
        ...,
        description="Explicit server-verified attestation that account is strictly synthetic (DEC-005)",
    )

    @field_validator("email")
    @classmethod
    def enforce_synthetic_email_domain(cls, value: EmailStr) -> EmailStr:
        domain = str(value).rsplit("@", 1)[-1].lower()
        if domain not in ALLOWED_SYNTHETIC_DOMAINS:
            raise ValueError(
                "Synthetic-only MVP boundary: email must use an authorized RFC 2606 synthetic domain "
                "(@example.com, @example.org, or @example.net)."
            )
        return value


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
    """Minimized synthetic profile preferences (real PII DOB/emergency contacts removed in MVP)."""

    preferred_units: UnitSystem = Field(default="metric", description="Preferred biomarker units")
    biological_sex: BiologicalSex | None = Field(
        default=None, description="Optional baseline biological sex"
    )
