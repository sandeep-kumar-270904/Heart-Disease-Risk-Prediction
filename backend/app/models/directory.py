"""HeartXAI 2.0 - Directory & Educational Resource Database Models.

Implements the Review-II UML classes: DoctorConsultation, HealthInsurance, and MedicalAssistance.
"""

from sqlalchemy import Boolean, Column, Float, Index, Integer, String, Text

from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class Doctor(Base, TimestampMixin):
    """Cardiologist & healthcare provider directory listing (maps to Review-II DoctorConsultation)."""

    __tablename__ = "doctors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    doctor_name = Column(String(255), nullable=False)
    specialization = Column(
        String(128), nullable=False
    )  # General Cardiology, Interventional, Preventative, etc.
    hospital_name = Column(String(255), nullable=False)
    contact_number = Column(String(64), nullable=False)
    location = Column(String(255), nullable=False)  # City, State, or Address
    email = Column(String(255), nullable=True)
    telehealth_available = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (Index("ix_doctors_spec_loc", "specialization", "location"),)


class Hospital(Base, TimestampMixin):
    """Accredited cardiac hospital & emergency facility directory listing."""

    __tablename__ = "hospitals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    hospital_name = Column(String(255), nullable=False)
    facility_type = Column(
        String(128), nullable=False
    )  # Comprehensive Cardiac Center, STEMI Center, General Hospital
    emergency_phone = Column(String(64), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(128), nullable=False)
    state = Column(String(64), nullable=False)
    accreditation_details = Column(
        String(255), nullable=False
    )  # e.g. "ACC Accredited Chest Pain Center"
    has_247_cath_lab = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (Index("ix_hospitals_city_type", "city", "facility_type"),)


class InsurancePolicy(Base, TimestampMixin):
    """Preventative cardiovascular insurance policy guide (maps to Review-II HealthInsurance)."""

    __tablename__ = "insurance_policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    provider_name = Column(String(255), nullable=False)  # e.g. Blue Cross, Aetna, Medicare
    policy_name = Column(String(255), nullable=False)
    coverage_summary = Column(Text, nullable=False)  # Details on ACA § 2713 $0 preventative copay
    monthly_premium_est = Column(Float, nullable=True)  # Estimated monthly premium range
    waiting_period_days = Column(Integer, default=0, nullable=False)
    exclusions_summary = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class EducationalResource(Base, TimestampMixin):
    """Evidence-based clinical health guidance (maps to Review-II MedicalAssistance)."""

    __tablename__ = "educational_resources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    biomarker_code = Column(
        String(32), nullable=False, index=True
    )  # e.g. "trestbps", "chol", "general"
    summary = Column(String(512), nullable=False)
    guideline_source = Column(
        String(255), nullable=False
    )  # e.g. "2019 ACC/AHA Primary Prevention Guideline"
    diet_plan_summary = Column(Text, nullable=False)
    exercise_tips_summary = Column(Text, nullable=False)
    lifestyle_guidance = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
