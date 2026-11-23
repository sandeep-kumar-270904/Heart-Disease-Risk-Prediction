"""HeartXAI 2.0 - Patient Consent & Clinical Notes Database Models.

Enforces patient sovereignty and time-bounded clinician access grants.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid, utc_now


class DoctorGrant(Base, TimestampMixin):
    """Time-bounded patient authorization grant permitting a doctor to view health records."""

    __tablename__ = "patient_doctor_grants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    access_code = Column(String(64), nullable=True)  # Optional single-use 6-digit consultation code
    status = Column(String(32), default="ACTIVE", nullable=False)  # ACTIVE, REVOKED, EXPIRED
    granted_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    patient = relationship(
        "User", foreign_keys=[patient_id], back_populates="doctor_grants_as_patient"
    )
    doctor = relationship(
        "User", foreign_keys=[doctor_id], back_populates="doctor_grants_as_doctor"
    )

    __table_args__ = (
        Index("ix_grants_patient_doctor_status", "patient_id", "doctor_id", "status"),
    )


class ClinicalNote(Base, TimestampMixin):
    """Clinician review notes, lifestyle recommendations, and countersignatures on an assessment."""

    __tablename__ = "clinical_notes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(
        String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    note_content = Column(Text, nullable=False)
    signoff_status = Column(String(32), default="DRAFT", nullable=False)  # DRAFT, FINAL_SIGNOFF
    signed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    assessment = relationship("Assessment", back_populates="clinical_notes")
    author = relationship("User", foreign_keys=[author_id], back_populates="clinical_notes")
