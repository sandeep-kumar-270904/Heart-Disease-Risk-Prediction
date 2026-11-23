"""HeartXAI 2.0 - Audit Trail & Model Registry Database Models."""

from sqlalchemy import Column, DateTime, Float, Index, Integer, String

from app.core.database import Base
from app.models.base import generate_uuid, utc_now


class AuditLog(Base):
    """Immutable, append-only security and clinical data access audit trail."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    role = Column(String(32), default="ANONYMOUS", nullable=False)
    action_type = Column(
        String(64), nullable=False, index=True
    )  # LOGIN, ASSESSMENT_SUBMITTED, RECORD_VIEWED, etc.
    resource_id = Column(String(64), nullable=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(16), nullable=False)
    ip_address = Column(String(64), nullable=False)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=False)

    __table_args__ = (
        Index("ix_audit_user_action", "user_id", "action_type"),
        Index("ix_audit_time_action", "timestamp", "action_type"),
    )


class ModelRegistry(Base):
    """Auditable machine learning model artifact registry tracking versions and metrics."""

    __tablename__ = "model_registry"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    version = Column(String(32), unique=True, nullable=False, index=True)  # e.g. "v2.0.0"
    algorithm = Column(String(128), nullable=False)  # Calibrated XGBoost + HistGradient
    training_cohort = Column(String(255), nullable=False)  # UCI Cleveland Benchmark N=297
    test_auroc = Column(Float, nullable=False)
    brier_score = Column(Float, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    deployed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = Active, 0 = Archived
