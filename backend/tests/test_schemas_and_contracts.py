"""Contract parity, Pydantic schema validation, and synthetic generator tests."""

import json
import re
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas import (
    AssessmentCreateDto,
    AssessmentDetailResponse,
    CountryProfileDto,
    RegisterRequest,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SHARED_DIR = REPO_ROOT / "shared"
FRONTEND_TYPES_DIR = REPO_ROOT / "frontend" / "src" / "types"
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_synthetic_patients import generate_synthetic_cohort  # noqa: E402


def _extract_ts_interface_fields(ts_file: Path, interface_name: str) -> set[str]:
    """Parse readonly property names from a TypeScript interface definition."""
    content = ts_file.read_text(encoding="utf-8")
    pattern = rf"export interface {interface_name}\s*\{{(.*?)\}}"
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, f"Interface {interface_name} not found in {ts_file}"
    body = match.group(1)
    fields: set[str] = set()
    for line in body.splitlines():
        stripped = line.strip()
        if (
            not stripped
            or stripped.startswith("//")
            or stripped.startswith("/*")
            or stripped.startswith("*")
        ):
            continue
        field_match = re.match(r"^(?:readonly\s+)?([a-zA-Z0-9_]+)\s*:", stripped)
        if field_match:
            fields.add(field_match.group(1))
    return fields


def test_shared_data_dictionary_covers_all_biomarkers() -> None:
    """Ensure canonical data-dictionary.json defines all 13 biomarkers matching AssessmentCreateDto."""
    dd_path = SHARED_DIR / "data-dictionary.json"
    assert dd_path.exists()
    data = json.loads(dd_path.read_text(encoding="utf-8"))
    biomarkers = data["biomarkers"]
    assert len(biomarkers) == 13

    expected_fields = {item["schema_field"] for item in biomarkers}
    schema_fields = set(AssessmentCreateDto.model_fields.keys()) - {"unit_system"}
    assert expected_fields == schema_fields


def test_shared_country_profiles_validate_cleanly() -> None:
    """Verify country-profiles.json parses against CountryProfileDto."""
    cp_path = SHARED_DIR / "country-profiles.json"
    assert cp_path.exists()
    data = json.loads(cp_path.read_text(encoding="utf-8"))
    countries = data["countries"]
    assert {"US", "IN", "GB", "DEFAULT"}.issubset(countries.keys())
    for profile_data in countries.values():
        profile = CountryProfileDto.model_validate(profile_data)
        assert profile.emergency_number


def test_frontend_backend_schema_parity() -> None:
    """Verify 1:1 field-name parity between TypeScript interfaces and Pydantic schemas."""
    assessment_ts = FRONTEND_TYPES_DIR / "assessment.ts"
    auth_ts = FRONTEND_TYPES_DIR / "auth.ts"
    country_ts = FRONTEND_TYPES_DIR / "country.ts"

    ts_create_fields = _extract_ts_interface_fields(assessment_ts, "AssessmentCreateDto")
    assert ts_create_fields == set(AssessmentCreateDto.model_fields.keys())

    ts_detail_fields = _extract_ts_interface_fields(assessment_ts, "AssessmentDetailResponse")
    assert ts_detail_fields == set(AssessmentDetailResponse.model_fields.keys())

    ts_register_fields = _extract_ts_interface_fields(auth_ts, "RegisterRequest")
    assert ts_register_fields == set(RegisterRequest.model_fields.keys())

    ts_country_fields = _extract_ts_interface_fields(country_ts, "CountryProfileDto")
    assert ts_country_fields == set(CountryProfileDto.model_fields.keys())


def test_assessment_dto_unit_normalization_and_strictness() -> None:
    """Verify metric mmol/L conversion to mg/dL and extra='forbid' enforcement."""
    dto = AssessmentCreateDto(
        age=55,
        sex=1,
        chest_pain_type=2,
        unit_system="metric",
        resting_bp=130,
        serum_cholesterol=5.5,  # mmol/L -> ~212.69 mg/dL
        fasting_blood_sugar=6.1,  # mmol/L -> ~109.90 mg/dL
        resting_ecg=0,
        max_heart_rate=150,
        exercise_angina=0,
        st_depression=1.2,
        st_slope=1,
        major_vessels=0,
        thallium_stress=1,
    )
    assert 212.0 <= dto.serum_cholesterol <= 213.0
    assert 109.0 <= dto.fasting_blood_sugar <= 111.0

    # Extra unknown fields must be rejected
    with pytest.raises(ValidationError):
        AssessmentCreateDto(
            age=55,
            sex=1,
            chest_pain_type=2,
            resting_bp=130,
            serum_cholesterol=210,
            fasting_blood_sugar=95,
            resting_ecg=0,
            max_heart_rate=150,
            exercise_angina=0,
            st_depression=1.2,
            st_slope=1,
            unexpected_field="malicious",  # type: ignore[call-arg]
        )


def test_synthetic_patient_generator_produces_valid_category_b_cohort() -> None:
    """Verify generator outputs 50 deterministic Category B fixtures with zero real PHI."""
    cohort_a = generate_synthetic_cohort(count=50, seed=42, unit_system="us_customary")
    cohort_b = generate_synthetic_cohort(count=50, seed=42, unit_system="us_customary")

    assert len(cohort_a) == 50
    mrns = {record.mrn for record in cohort_a}
    assert len(mrns) == 50

    for rec_a, rec_b in zip(cohort_a, cohort_b, strict=True):
        assert rec_a.is_synthetic is True
        assert rec_a.data_category == "Category B — Synthetic Application Fixture"
        assert rec_a.intake.model_dump() == rec_b.intake.model_dump()


def test_synthetic_patient_generator_metric_mode() -> None:
    """Verify generator works cleanly when generating metric mmol/L input payloads."""
    metric_cohort = generate_synthetic_cohort(count=10, seed=99, unit_system="metric")
    assert len(metric_cohort) == 10
    for record in metric_cohort:
        assert record.intake.unit_system == "metric"
        assert 100.0 <= record.intake.serum_cholesterol <= 600.0
