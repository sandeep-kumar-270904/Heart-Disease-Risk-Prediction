"""HeartXAI 2.0 - Constrained Counterfactual Scenario Engine (Milestone 13).

Strictly locks immutable attributes (age, sex, clinical/ECG/imaging history) and
enforces physiological safety floors (resting_bp >= 90 mmHg, serum_cholesterol >= 120 mg/dL).
Outputs are strictly exploratory model scenarios, never medical prescriptions.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ml.inference_service import InferenceService, get_inference_service
from app.schemas.assessment import AssessmentCreateDto, ScenarioResultDto

IMMUTABLE_FIELDS = frozenset(
    {
        "age",
        "sex",
        "chest_pain_type",
        "resting_ecg",
        "exercise_angina",
        "st_depression",
        "st_slope",
        "major_vessels",
        "thallium_stress",
    }
)

MODIFIABLE_BOUNDS: dict[str, tuple[float, float, float]] = {
    # field: (physiological_floor, physiological_ceiling, scale_normalizer)
    "resting_bp": (90.0, 220.0, 30.0),
    "serum_cholesterol": (120.0, 500.0, 60.0),
    "fasting_blood_sugar": (70.0, 350.0, 40.0),
    "max_heart_rate": (60.0, 210.0, 30.0),
}


@dataclass(frozen=True)
class OptimalCounterfactual:
    """Constrained optimization target keeping immutable attributes unchanged."""

    target_threshold: float
    achieved_probability: float
    modified_biomarkers: dict[str, float]
    immutable_biomarkers: dict[str, float | int | None]
    l1_normalized_distance: float
    feasibility_rating: str


class CounterfactualService:
    """Evaluates constrained 'what-if' lifestyle scenarios with biological guardrails."""

    def __init__(self, inference_service: InferenceService | None = None) -> None:
        self._inference = inference_service or get_inference_service()

    def simulate(
        self,
        assessment_id: str,
        baseline: AssessmentCreateDto,
        modified_features: dict[str, float],
    ) -> ScenarioResultDto:
        """Simulate a user-requested modification while enforcing biological clamps."""
        baseline_pred = self._inference.predict(baseline)

        for field_name, proposed_val in modified_features.items():
            if field_name in IMMUTABLE_FIELDS:
                return ScenarioResultDto(
                    assessment_id=assessment_id,
                    baseline_likelihood_percent=baseline_pred.likelihood_percent,
                    simulated_likelihood_percent=baseline_pred.likelihood_percent,
                    delta_percent=0.0,
                    feasibility_score=0.0,
                    is_biological_clamp_violated=True,
                    violation_message=(
                        f"Attribute '{field_name}' is biologically/historically immutable and "
                        "cannot be altered in counterfactual exploration."
                    ),
                )
            if field_name not in MODIFIABLE_BOUNDS:
                return ScenarioResultDto(
                    assessment_id=assessment_id,
                    baseline_likelihood_percent=baseline_pred.likelihood_percent,
                    simulated_likelihood_percent=baseline_pred.likelihood_percent,
                    delta_percent=0.0,
                    feasibility_score=0.0,
                    is_biological_clamp_violated=True,
                    violation_message=f"Unsupported counterfactual feature: '{field_name}'.",
                )
            low, high, _ = MODIFIABLE_BOUNDS[field_name]
            if proposed_val < low or proposed_val > high:
                return ScenarioResultDto(
                    assessment_id=assessment_id,
                    baseline_likelihood_percent=baseline_pred.likelihood_percent,
                    simulated_likelihood_percent=baseline_pred.likelihood_percent,
                    delta_percent=0.0,
                    feasibility_score=0.0,
                    is_biological_clamp_violated=True,
                    violation_message=(
                        f"Proposed '{field_name}' ({proposed_val}) violates physiological safety "
                        f"floor/ceiling [{low}, {high}]."
                    ),
                )

        updated_data = baseline.model_dump()
        updated_data["unit_system"] = "us_customary"
        for field_name, val in modified_features.items():
            updated_data[field_name] = float(val)

        simulated_dto = AssessmentCreateDto.model_validate(updated_data)
        sim_pred = self._inference.predict(simulated_dto)

        l1_dist = 0.0
        for field_name, val in modified_features.items():
            _, _, scale = MODIFIABLE_BOUNDS[field_name]
            base_val = float(getattr(baseline, field_name))
            l1_dist += abs(float(val) - base_val) / scale

        feasibility = round(max(0.0, min(1.0, 1.0 / (1.0 + l1_dist))), 3)
        delta_pct = round(sim_pred.likelihood_percent - baseline_pred.likelihood_percent, 2)

        return ScenarioResultDto(
            assessment_id=assessment_id,
            baseline_likelihood_percent=baseline_pred.likelihood_percent,
            simulated_likelihood_percent=sim_pred.likelihood_percent,
            delta_percent=delta_pct,
            feasibility_score=feasibility,
            is_biological_clamp_violated=False,
            violation_message=None,
        )

    def generate_optimal(
        self, baseline: AssessmentCreateDto, target_probability: float = 0.30
    ) -> OptimalCounterfactual:
        """Grid-search actionable modifiable hyperplanes while keeping immutable fields frozen."""
        bp_candidates = sorted(
            {max(90.0, min(float(baseline.resting_bp), v)) for v in (115.0, 120.0, 130.0)}
        )
        chol_candidates = sorted(
            {max(120.0, min(float(baseline.serum_cholesterol), v)) for v in (170.0, 190.0, 210.0)}
        )
        fbs_candidates = [min(float(baseline.fasting_blood_sugar), 100.0)]

        best_candidate: OptimalCounterfactual | None = None
        immutable_snapshot = {field: getattr(baseline, field) for field in sorted(IMMUTABLE_FIELDS)}

        for bp in bp_candidates:
            for chol in chol_candidates:
                for fbs in fbs_candidates:
                    updated = baseline.model_dump()
                    updated["unit_system"] = "us_customary"
                    updated["resting_bp"] = bp
                    updated["serum_cholesterol"] = chol
                    updated["fasting_blood_sugar"] = fbs

                    candidate_dto = AssessmentCreateDto.model_validate(updated)
                    pred = self._inference.predict(candidate_dto)

                    l1 = (
                        abs(bp - float(baseline.resting_bp)) / 30.0
                        + abs(chol - float(baseline.serum_cholesterol)) / 60.0
                        + abs(fbs - float(baseline.fasting_blood_sugar)) / 40.0
                    )
                    rating = "HIGH" if l1 < 1.0 else ("MODERATE" if l1 < 2.2 else "CHALLENGING")
                    cf = OptimalCounterfactual(
                        target_threshold=target_probability,
                        achieved_probability=round(pred.probability, 4),
                        modified_biomarkers={
                            "resting_bp": bp,
                            "serum_cholesterol": chol,
                            "fasting_blood_sugar": fbs,
                        },
                        immutable_biomarkers=immutable_snapshot,
                        l1_normalized_distance=round(l1, 3),
                        feasibility_rating=rating,
                    )
                    if best_candidate is None or (
                        cf.achieved_probability < best_candidate.achieved_probability
                        or (
                            cf.achieved_probability == best_candidate.achieved_probability
                            and cf.l1_normalized_distance < best_candidate.l1_normalized_distance
                        )
                    ):
                        best_candidate = cf

        assert best_candidate is not None
        return best_candidate


_default_cf_service: CounterfactualService | None = None


def get_counterfactual_service() -> CounterfactualService:
    """Return global constrained CounterfactualService singleton."""
    global _default_cf_service
    if _default_cf_service is None:
        _default_cf_service = CounterfactualService()
    return _default_cf_service
