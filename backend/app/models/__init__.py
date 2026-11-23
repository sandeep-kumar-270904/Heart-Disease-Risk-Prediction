"""HeartXAI 2.0 - Centralized Model Registry Package.

Exports all SQLAlchemy 2.0 declarative models for Alembic discovery and ORM operations.
"""

from app.core.database import Base
from app.models.assessment import (
    Assessment,
    CounterfactualProfile,
    InferenceResult,
    ShapExplanation,
)
from app.models.audit import AuditLog, ModelRegistry
from app.models.base import TimestampMixin
from app.models.consent import ClinicalNote, DoctorGrant
from app.models.directory import (
    Doctor,
    EducationalResource,
    Hospital,
    InsurancePolicy,
)
from app.models.user import PatientProfile, User

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
