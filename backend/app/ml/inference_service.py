"""HeartXAI 2.0 - In-Process Calibrated XGBoost Task A Inference Service (Milestone 11)."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.schemas.assessment import AssessmentCreateDto, RiskStrata

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "model.joblib"

FEATURE_DISPLAY_METADATA: dict[str, tuple[str, str]] = {
    "age": ("Chronological Age", "years"),
    "sex": ("Biological Sex", "category"),
    "cp": ("Chest Pain Presentation", "category"),
    "trestbps": ("Resting Systolic BP", "mmHg"),
    "chol": ("Serum Cholesterol", "mg/dL"),
    "fbs": ("Fasting Blood Sugar >120 mg/dL", "flag"),
    "restecg": ("Resting ECG", "category"),
    "thalach": ("Max Heart Rate", "bpm"),
    "exang": ("Exercise-Induced Angina", "flag"),
    "oldpeak": ("ST Depression (Oldpeak)", "mm"),
    "slope": ("Peak Exercise ST Slope", "category"),
    "ca": ("Major Vessels (Fluoroscopy)", "vessels"),
    "thal": ("Thallium Stress Test", "category"),
}


@dataclass(frozen=True)
class InferenceOutput:
    """Structured result from in-process Task A inference."""

    model_version: str
    probability: float
    likelihood_percent: float
    risk_strata: RiskStrata
    db_risk_tier: str
    raw_margin: float
    base_expected_value: float
    is_out_of_distribution: bool
    emergency_warning_active: bool
    plain_language_summary: str
    feature_vector: np.ndarray


def dto_to_feature_vector(
    dto: AssessmentCreateDto,
    imputers: dict[str, float] | None = None,
) -> np.ndarray:
    """Convert validated AssessmentCreateDto into ordered 13-feature NumPy row.

    Explicitly derives the binary UCI Cleveland fbs feature (> 120 mg/dL -> 1.0)
    in the ML preprocessing layer while preserving exact numeric glucose separately.
    """
    ca_default = float((imputers or {}).get("ca", 0.0))
    thal_default = float((imputers or {}).get("thal", 1.0))
    fbs_binary = 1.0 if dto.fasting_blood_sugar > 120.0 else 0.0
    ca_val = float(dto.major_vessels) if dto.major_vessels is not None else ca_default
    thal_val = float(dto.thallium_stress) if dto.thallium_stress is not None else thal_default

    return np.array(
        [
            [
                float(dto.age),
                float(dto.sex),
                float(dto.chest_pain_type),
                float(dto.resting_bp),
                float(dto.serum_cholesterol),
                fbs_binary,
                float(dto.resting_ecg),
                float(dto.max_heart_rate),
                float(dto.exercise_angina),
                float(dto.st_depression),
                float(dto.st_slope),
                ca_val,
                thal_val,
            ]
        ],
        dtype=float,
    )


class InferenceService:
    """Thread-safe singleton loader and synchronous C-API inference runner (ADR-001)."""

    def __init__(self, model_path: Path = DEFAULT_MODEL_PATH) -> None:
        self._model_path = model_path
        self._lock = threading.Lock()
        self._artifact: dict[str, Any] | None = None

    def _ensure_loaded(self) -> dict[str, Any]:
        if self._artifact is None:
            with self._lock:
                if self._artifact is None:
                    self._artifact = joblib.load(self._model_path)
        return self._artifact

    @property
    def artifact(self) -> dict[str, Any]:
        return self._ensure_loaded()

    def predict(self, dto: AssessmentCreateDto) -> InferenceOutput:
        """Execute sub-20ms calibrated Task A classification in-process."""
        art = self._ensure_loaded()
        imputers = art.get("training_fold_imputers")
        vec = dto_to_feature_vector(dto, imputers=imputers)

        xgb_model = art["xgb_estimator"]
        calibrator = art["platt_calibrator"]
        bounds: dict[str, tuple[float, float]] = art["feature_bounds"]
        feature_cols: list[str] = art["feature_columns"]

        raw_margin = float(xgb_model.predict(vec, output_margin=True)[0])
        prob = float(calibrator.predict_proba(np.array([[raw_margin]], dtype=float))[0, 1])
        prob = min(max(prob, 0.0), 1.0)
        likelihood_pct = round(prob * 100.0, 2)

        # Unsupported 30%/70% clinical risk cutoffs disabled pending DEC-002 clinical review
        risk_strata: RiskStrata = "unstratified"
        db_tier = "UNSTRATIFIED"

        is_ood = any(
            float(vec[0, idx]) < bounds[col][0] or float(vec[0, idx]) > bounds[col][1]
            for idx, col in enumerate(feature_cols)
            if col in bounds
        )

        # Unreviewed automated clinical red-flag triage disabled pending DEC-002 physician sign-off
        emergency_active = False

        summary = (
            f"Experimental Retrospective Task A Model Score: {likelihood_pct:.1f}% "
            "(UCI Cleveland retrospective binary CAD classification model). "
            "Informational model output only — NOT a medical diagnosis, risk tier, or future 10-year risk forecast."
        )

        return InferenceOutput(
            model_version=str(art["model_version"]),
            probability=prob,
            likelihood_percent=likelihood_pct,
            risk_strata=risk_strata,
            db_risk_tier=db_tier,
            raw_margin=raw_margin,
            base_expected_value=0.0,
            is_out_of_distribution=is_ood,
            emergency_warning_active=emergency_active,
            plain_language_summary=summary,
            feature_vector=vec,
        )


_default_inference_service: InferenceService | None = None


def get_inference_service() -> InferenceService:
    """Return global in-process InferenceService singleton."""
    global _default_inference_service
    if _default_inference_service is None:
        _default_inference_service = InferenceService()
    return _default_inference_service
