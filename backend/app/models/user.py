"""HeartXAI 2.0 - User & Patient Profile Database Models."""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    """User account entity for Patients, Clinicians, and Administrators."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(32), default="PATIENT", nullable=False)  # GUEST, PATIENT, CLINICIAN, ADMIN
    country_code = Column(String(7), default="US", nullable=False)
    clinician_status = Column(
        String(32), default="N/A", nullable=False
    )  # N/A, PENDING_VERIFICATION, VERIFIED, REJECTED
    is_active = Column(Boolean, default=True, nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile = relationship(
        "PatientProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    assessments = relationship(
        "Assessment",
        back_populates="patient",
        foreign_keys="Assessment.patient_id",
        cascade="all, delete-orphan",
    )
    doctor_grants_as_patient = relationship(
        "DoctorGrant",
        back_populates="patient",
        foreign_keys="DoctorGrant.patient_id",
        cascade="all, delete-orphan",
    )
    doctor_grants_as_doctor = relationship(
        "DoctorGrant", back_populates="doctor", foreign_keys="DoctorGrant.doctor_id"
    )
    clinical_notes = relationship(
        "ClinicalNote", back_populates="author", foreign_keys="ClinicalNote.author_id"
    )

    __table_args__ = (Index("ix_users_role_status", "role", "clinician_status"),)


class PatientProfile(Base, TimestampMixin):
    """Baseline demographic context and unit preferences for a patient."""

    __tablename__ = "patient_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    date_of_birth = Column(Date, nullable=True)
    biological_sex = Column(String(16), nullable=True)  # FEMALE, MALE
    preferred_units = Column(
        String(16), default="US_STANDARD", nullable=False
    )  # US_STANDARD, METRIC
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(64), nullable=True)

    # Relationship
    user = relationship("User", back_populates="profile")
