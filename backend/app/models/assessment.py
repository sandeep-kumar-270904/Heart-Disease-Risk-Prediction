"""HeartXAI 2.0 - Assessment, Inference, SHAP & Counterfactual Database Models."""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid, utc_now


class Assessment(Base, TimestampMixin):
    """Clinical biomarker intake record submitted by or for a patient."""

    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    clinician_id = Column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status = Column(String(32), default="COMPLETED", nullable=False)  # DRAFT, COMPLETED, REVIEWED

    # The 13 Benchmark Clinical Biomarkers
    age = Column(Integer, nullable=False)  # 18 - 100
    sex = Column(Integer, nullable=False)  # 0 = Female, 1 = Male
    cp = Column(
        Integer, nullable=False
    )  # Chest pain type: 0 = Typical, 1 = Atypical, 2 = Non-anginal, 3 = Asymptomatic
    trestbps = Column(Integer, nullable=False)  # Resting blood pressure (mm Hg)
    chol = Column(Integer, nullable=False)  # Serum cholesterol (mg/dL)
    fbs = Column(Integer, nullable=False)  # Fasting blood sugar > 120 mg/dL: 0 = No, 1 = Yes
    restecg = Column(
        Integer, nullable=False
    )  # Resting ECG: 0 = Normal, 1 = ST-T Abnormality, 2 = LV Hypertrophy
    thalach = Column(Integer, nullable=False)  # Maximum heart rate achieved (bpm)
    exang = Column(Integer, nullable=False)  # Exercise-induced angina: 0 = No, 1 = Yes
    oldpeak = Column(Float, nullable=False)  # ST depression induced by exercise (mm)
    slope = Column(
        Integer, nullable=False
    )  # Slope of peak exercise ST segment: 0 = Upsloping, 1 = Flat, 2 = Downsloping
    ca = Column(Integer, nullable=False)  # Major vessels colored by fluoroscopy: 0, 1, 2, 3
    thal = Column(
        Integer, nullable=False
    )  # Thallium stress defect: 1 = Normal, 2 = Fixed, 3 = Reversible

    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="assessments")
    clinician = relationship("User", foreign_keys=[clinician_id])
    inference_result = relationship(
        "InferenceResult", back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )
    clinical_notes = relationship(
        "ClinicalNote", back_populates="assessment", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_assessments_patient_created", "patient_id", "created_at"),)


class InferenceResult(Base):
    """Machine learning prediction outputs for CAD presence and prospective 10-year ASCVD risk."""

    __tablename__ = "inference_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(
        String(36),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    model_version = Column(String(32), nullable=False)  # e.g. "v2.0.0"

    # Target 1: Calibrated Coronary Artery Disease (CAD) Presence (Stenosis >= 50%)
    cad_probability = Column(Float, nullable=False)  # 0.0 - 1.0
    cad_risk_tier = Column(String(32), nullable=False)  # LOW, BORDERLINE, ELEVATED
    confidence_interval_low = Column(Float, nullable=False)
    confidence_interval_high = Column(Float, nullable=False)

    # Target 2: Prospective 10-Year ASCVD Risk (ACC/AHA Guidelines)
    ascvd_10yr_risk = Column(Float, nullable=False)  # 0.0 - 100.0%
    ascvd_risk_tier = Column(String(32), nullable=False)  # LOW, BORDERLINE, INTERMEDIATE, HIGH

    # Mathematical Baseline & Uncertainty
    base_expected_value = Column(Float, nullable=False)  # E[f(x)]
    raw_decision_margin = Column(Float, nullable=False)  # f(x)
    is_out_of_distribution = Column(Boolean, default=False, nullable=False)
    computed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    assessment = relationship("Assessment", back_populates="inference_result")
    shap_explanations = relationship(
        "ShapExplanation", back_populates="inference_result", cascade="all, delete-orphan"
    )
    counterfactual_profiles = relationship(
        "CounterfactualProfile", back_populates="inference_result", cascade="all, delete-orphan"
    )


class ShapExplanation(Base):
    """Exact local TreeSHAP feature attributions explaining the model's prediction."""

    __tablename__ = "shap_explanations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inference_id = Column(
        String(36),
        ForeignKey("inference_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_name = Column(String(32), nullable=False)  # e.g. "trestbps", "thalach"
    feature_value = Column(Float, nullable=False)
    shap_value = Column(Float, nullable=False)  # phi_i in log-odds units
    rank_importance = Column(Integer, nullable=False)  # 1 to 13
    directional_impact = Column(String(32), nullable=False)  # RISK_INCREASING, PROTECTIVE
    clinical_interpretation = Column(String(512), nullable=False)

    # Relationship
    inference_result = relationship("InferenceResult", back_populates="shap_explanations")

    __table_args__ = (Index("ix_shap_inference_rank", "inference_id", "rank_importance"),)


class CounterfactualProfile(Base):
    """Plausible, constrained lifestyle optimization targets locking immutable attributes."""

    __tablename__ = "counterfactual_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inference_id = Column(
        String(36),
        ForeignKey("inference_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_risk_threshold = Column(Float, nullable=False)
    achieved_risk_probability = Column(Float, nullable=False)
    modified_biomarkers = Column(
        JSON, nullable=False
    )  # Dict of modifiable features and target values
    immutable_biomarkers = Column(
        JSON, nullable=False
    )  # Dict of locked traits (age, sex, ca, thal)
    l1_normalized_distance = Column(Float, nullable=False)
    feasibility_rating = Column(String(32), nullable=False)  # HIGH, MODERATE, CHALLENGING
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationship
    inference_result = relationship("InferenceResult", back_populates="counterfactual_profiles")
