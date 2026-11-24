"""HeartXAI 2.0 - Base Pydantic v2 Schemas & Standardized Error Envelopes."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Canonical base schema enforcing strict validation and ORM compatibility."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")


ErrorType = Literal[
    "validation_error",
    "authentication_error",
    "authorization_error",
    "resource_not_found",
    "conflict_error",
    "rate_limit_exceeded",
    "clinical_boundary_error",
    "internal_server_error",
]


class ApiErrorDetail(BaseSchema):
    """Granular parameter-level error description."""

    param: str | None = Field(default=None, description="Offending request parameter name")
    code: str = Field(..., description="Machine-readable error sub-code")
    message: str = Field(..., description="Human-readable validation or boundary message")


class ApiErrorBody(BaseSchema):
    """Structured error body adhering to standardized API error architecture."""

    type: ErrorType = Field(..., description="Top-level error classification")
    code: str = Field(..., description="Specific domain error identifier")
    param: str | None = Field(default=None, description="Primary offending field, if any")
    message: str = Field(..., description="Actionable summary message")
    details: list[ApiErrorDetail] | None = Field(
        default=None, description="Optional field-level validation breakdowns"
    )


class ApiErrorEnvelope(BaseSchema):
    """Top-level error envelope returned for all non-2xx responses."""

    error: ApiErrorBody
