"""HeartXAI 2.0 - Exact TreeSHAP Local Feature Attribution Service (Milestone 12)."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any

import numpy as np
import shap

from app.ml.inference_service import (
    FEATURE_DISPLAY_METADATA,
    InferenceService,
    dto_to_feature_vector,
    get_inference_service,
)
from app.schemas.assessment import AssessmentCreateDto, FeatureImpactDto, ShapDirection


@dataclass(frozen=True)
class ShapComputationOutput:
    """Verified local TreeSHAP output satisfying exact additivity."""

    model_version: str
    base_value: float
    final_margin: float
    features: list[FeatureImpactDto]


class ShapService:
    """Pre-initialized TreeSHAP explainer computing exact log-odds attributions."""

    def __init__(self, inference_service: InferenceService | None = None) -> None:
        self._inference_service = inference_service or get_inference_service()
        self._lock = threading.Lock()
        self._explainer: Any | None = None

    def _get_explainer(self) -> Any:
        if self._explainer is None:
            with self._lock:
                if self._explainer is None:
                    xgb_model = self._inference_service.artifact["xgb_estimator"]
                    self._explainer = shap.TreeExplainer(xgb_model)
        return self._explainer

    def explain(self, dto: AssessmentCreateDto) -> ShapComputationOutput:
        """Compute exact local TreeSHAP attributions sorted by absolute impact."""
        art = self._inference_service.artifact
        explainer = self._get_explainer()
        vec = dto_to_feature_vector(dto)

        shap_vals = explainer.shap_values(vec)
        if isinstance(shap_vals, list):
            phi_row = np.asarray(shap_vals[1][0], dtype=float)
        else:
            arr = np.asarray(shap_vals, dtype=float)
            phi_row = arr[0] if arr.ndim == 2 else arr[0, :, 1]

        expected_raw = explainer.expected_value
        if isinstance(expected_raw, (list, np.ndarray)):
            base_val = float(np.asarray(expected_raw, dtype=float).ravel()[-1])
        else:
            base_val = float(expected_raw)

        feature_cols: list[str] = art["feature_columns"]
        cohort_means: dict[str, float] = art["cohort_feature_means"]
        final_margin = base_val + float(phi_row.sum())

        impacts: list[FeatureImpactDto] = []
        for idx, col in enumerate(feature_cols):
            phi = float(phi_row[idx])
            raw_val = float(vec[0, idx])
            avg_val = float(cohort_means.get(col, 0.0))
            display_name, unit = FEATURE_DISPLAY_METADATA.get(col, (col, "units"))
            direction: ShapDirection = (
                "increases_likelihood" if phi >= 0.0 else "decreases_likelihood"
            )
            verb = "positively associated with" if phi >= 0.0 else "negatively associated with"
            explanation = (
                f"{display_name} ({raw_val:g} {unit} vs. cohort mean {avg_val:g}) is "
                f"statistically {verb} higher model output (SHAP {phi:+.4f}; statistical "
                "association only, not biological causation)."
            )
            impacts.append(
                FeatureImpactDto(
                    feature_name=col,
                    raw_patient_value=round(raw_val, 3),
                    unit=unit,
                    cohort_average_value=round(avg_val, 3),
                    shap_value=round(phi, 6),
                    direction=direction,
                    plain_language_explanation=explanation,
                )
            )

        impacts.sort(key=lambda item: abs(item.shap_value), reverse=True)
        return ShapComputationOutput(
            model_version=str(art["model_version"]),
            base_value=round(base_val, 6),
            final_margin=round(final_margin, 6),
            features=impacts,
        )


_default_shap_service: ShapService | None = None


def get_shap_service() -> ShapService:
    """Return global TreeSHAP explanation service singleton."""
    global _default_shap_service
    if _default_shap_service is None:
        _default_shap_service = ShapService()
    return _default_shap_service
