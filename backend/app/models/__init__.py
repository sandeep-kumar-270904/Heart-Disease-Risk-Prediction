"""HeartXAI 2.0 - Centralized Model Registry Package.

Exports all SQLAlchemy 2.0 declarative models for Alembic discovery and ORM operations.
"""

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.user import User, PatientProfile
from app.models.assessment import (
    Assessment,
    InferenceResult,
    ShapExplanation,
    CounterfactualProfile,
)
from app.models.consent import DoctorGrant, ClinicalNote
from app.models.directory import (
    Doctor,
    Hospital,
    InsurancePolicy,
    EducationalResource,
)
from app.models.audit import AuditLog, ModelRegistry

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "PatientProfile",
    "Assessment",
    "InferenceResult",
    "ShapExplanation",
    "CounterfactualProfile",
    "DoctorGrant",
    "ClinicalNote",
    "Doctor",
    "Hospital",
    "InsurancePolicy",
    "EducationalResource",
    "AuditLog",
    "ModelRegistry",
]
