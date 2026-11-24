"""HeartXAI 2.0 — Empirical Performance & Latency Benchmark Suite (Milestone 19).

Measures empirical local latency across backend, ML inference, TreeSHAP, constrained
counterfactual optimization, ReportLab PDF export, and 4-thread concurrency.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.ml.counterfactual_service import get_counterfactual_service  # noqa: E402
from app.ml.inference_service import get_inference_service  # noqa: E402
from app.ml.shap_service import get_shap_service  # noqa: E402
from app.schemas.assessment import AssessmentCreateDto  # noqa: E402
from app.services.export_service import generate_assessment_pdf_bytes  # noqa: E402


def _percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((pct / 100.0) * (len(ordered) - 1)))))
    return round(ordered[idx], 3)


def _summarize(values_ms: list[float]) -> dict[str, float]:
    return {
        "n": float(len(values_ms)),
        "mean_ms": round(statistics.mean(values_ms), 3),
        "p50_ms": _percentile(values_ms, 50),
        "p95_ms": _percentile(values_ms, 95),
        "max_ms": round(max(values_ms), 3),
    }


def run_benchmarks() -> dict[str, object]:
    """Execute empirical performance benchmarks and return structured scorecard."""
    dto = AssessmentCreateDto(
        synthetic_fixture_confirmed=True,
        age=57.0,
        sex=1,
        chest_pain_type=3,
        unit_system="us_customary",
        resting_bp=158.0,
        serum_cholesterol=268.0,
        fasting_blood_sugar=135.0,
        resting_ecg=2,
        max_heart_rate=138.0,
        exercise_angina=1,
        st_depression=2.2,
        st_slope=1,
        major_vessels=2,
        thallium_stress=3,
    )

    inf_svc = get_inference_service()
    shap_svc = get_shap_service()
    cf_svc = get_counterfactual_service()

    # Warmup
    inf_out = inf_svc.predict(dto)
    shap_out = shap_svc.explain(dto)

    # 1. XGBoost Task A In-Process Inference (200 iterations)
    inf_lat: list[float] = []
    for _ in range(200):
        t0 = time.perf_counter()
        inf_svc.predict(dto)
        inf_lat.append((time.perf_counter() - t0) * 1000.0)

    # 2. TreeSHAP Attribution Latency (50 iterations)
    shap_lat: list[float] = []
    for _ in range(50):
        t0 = time.perf_counter()
        shap_svc.explain(dto)
        shap_lat.append((time.perf_counter() - t0) * 1000.0)

    # 3. Counterfactual Grid Search Latency (30 iterations)
    cf_lat: list[float] = []
    for _ in range(30):
        t0 = time.perf_counter()
        cf_svc.generate_optimal(dto)
        cf_lat.append((time.perf_counter() - t0) * 1000.0)

    # 4. ReportLab 2-page PDF Export Latency (15 iterations)
    from app.schemas.assessment import AssessmentDetailResponse, ShapExplanationResponse

    detail_dto = AssessmentDetailResponse(
        id="bench-001",
        patient_id="usr-bench",
        age=dto.age,
        sex=dto.sex,
        chest_pain_type=dto.chest_pain_type,
        resting_bp=dto.resting_bp,
        serum_cholesterol=dto.serum_cholesterol,
        fasting_blood_sugar=dto.fasting_blood_sugar,
        fasting_blood_sugar_gt_120=dto.fasting_blood_sugar > 120.0,
        resting_ecg=dto.resting_ecg,
        max_heart_rate=dto.max_heart_rate,
        exercise_angina=dto.exercise_angina,
        st_depression=dto.st_depression,
        st_slope=dto.st_slope,
        major_vessels=dto.major_vessels,
        thallium_stress=dto.thallium_stress,
        cad_likelihood_percent=inf_out.likelihood_percent,
        risk_strata=inf_out.risk_strata,
        ten_year_population_risk_percent=None,
        model_version=inf_out.model_version,
        cohort_name="UCI Cleveland Benchmark (N=303)",
        data_provenance="Category B — Benchmark Synthetic Fixture",
        plain_language_summary=inf_out.plain_language_summary,
        emergency_warning_active=inf_out.emergency_warning_active,
        created_at=datetime.now(UTC),
    )
    shap_dto = ShapExplanationResponse(
        assessment_id="bench-001",
        model_version=shap_out.model_version,
        base_value=shap_out.base_value,
        final_likelihood=shap_out.final_margin,
        features=shap_out.features,
    )
    pdf_lat: list[float] = []
    for _ in range(15):
        t0 = time.perf_counter()
        generate_assessment_pdf_bytes(detail_dto, shap_dto)
        pdf_lat.append((time.perf_counter() - t0) * 1000.0)

    # 5. Argon2id Hash Latency (5 iterations)
    argon_lat: list[float] = []
    for _ in range(5):
        t0 = time.perf_counter()
        hash_password("BenchmarkPass!2026")
        argon_lat.append((time.perf_counter() - t0) * 1000.0)

    # 6. FastAPI Health Probe Throughput via TestClient (100 calls)
    client = TestClient(app)
    health_lat: list[float] = []
    t_start = time.perf_counter()
    for _ in range(100):
        t0 = time.perf_counter()
        resp = client.get("/health/live")
        assert resp.status_code == 200
        health_lat.append((time.perf_counter() - t0) * 1000.0)
    total_health_sec = time.perf_counter() - t_start

    # 7. Concurrent 4-Thread Inference Burst (100 predictions)
    t_conc_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: inf_svc.predict(dto), range(100)))
    conc_total_ms = round((time.perf_counter() - t_conc_start) * 1000.0, 2)

    report = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "environment": "local-windows-python-3.11",
        "variables_measured": {
            "in_process_xgboost_inference_ms": _summarize(inf_lat),
            "treeshap_attribution_ms": _summarize(shap_lat),
            "counterfactual_grid_search_ms": _summarize(cf_lat),
            "pdf_dossier_generation_ms": _summarize(pdf_lat),
            "argon2id_hashing_ms": _summarize(argon_lat),
            "fastapi_health_probe_ms": _summarize(health_lat),
            "fastapi_health_rps": round(100.0 / total_health_sec, 1),
            "concurrent_4_workers_100_inferences_total_ms": conc_total_ms,
        },
    }
    return report


if __name__ == "__main__":
    results = run_benchmarks()
    out_path = REPO_ROOT / "docs" / "performance_benchmark_report.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
