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
    confidence_interval: list[float]
    risk_strata: RiskStrata
    db_risk_tier: str
    raw_margin: float
    base_expected_value: float
    is_out_of_distribution: bool
    emergency_warning_active: bool
    plain_language_summary: str
    feature_vector: np.ndarray


def dto_to_feature_vector(dto: AssessmentCreateDto) -> np.ndarray:
    """Convert validated AssessmentCreateDto into ordered 13-feature NumPy row."""
    fbs_binary = 1.0 if dto.fasting_blood_sugar > 120.0 else 0.0
    ca_val = float(dto.major_vessels if dto.major_vessels is not None else 0)
    thal_val = float(dto.thallium_stress if dto.thallium_stress is not None else 1)

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
        vec = dto_to_feature_vector(dto)

        xgb_model = art["xgb_estimator"]
        calibrator = art["platt_calibrator"]
        bounds: dict[str, tuple[float, float]] = art["feature_bounds"]
        feature_cols: list[str] = art["feature_columns"]

        raw_margin = float(xgb_model.predict(vec, output_margin=True)[0])
        prob = float(calibrator.predict_proba(np.array([[raw_margin]], dtype=float))[0, 1])
        prob = min(max(prob, 0.0), 1.0)
        likelihood_pct = round(prob * 100.0, 2)

        if likelihood_pct < 30.0:
            risk_strata: RiskStrata = "low"
            db_tier = "LOW"
        elif likelihood_pct < 70.0:
            risk_strata = "moderate"
            db_tier = "BORDERLINE"
        else:
            risk_strata = "elevated"
            db_tier = "ELEVATED"

        ci_low = round(max(0.0, likelihood_pct - 6.5), 1)
        ci_high = round(min(100.0, likelihood_pct + 6.5), 1)

        is_ood = any(
            float(vec[0, idx]) < bounds[col][0] or float(vec[0, idx]) > bounds[col][1]
            for idx, col in enumerate(feature_cols)
            if col in bounds
        )

        emergency_active = bool(
            dto.resting_bp > 180.0 or (dto.chest_pain_type == 0 and dto.exercise_angina == 1)
        )

        summary = (
            f"Educational Task A Benchmark Association: {likelihood_pct:.1f}% "
            f"({risk_strata} tier, UCI Cleveland retrospective cohort similarity). "
            "Informational model output only — NOT a medical diagnosis or 10-year risk forecast."
        )

        return InferenceOutput(
            model_version=str(art["model_version"]),
            probability=prob,
            likelihood_percent=likelihood_pct,
            confidence_interval=[ci_low, ci_high],
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
