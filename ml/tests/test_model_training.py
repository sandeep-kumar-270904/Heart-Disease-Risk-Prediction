"""Tests for Milestone 10 Task A XGBoost training, calibration, and subgroup checks."""

from pathlib import Path

from ml.pipelines.evaluate_model import evaluate_registered_model
from ml.pipelines.prepare_data import prepare_datasets
from ml.pipelines.train_model import train_and_register_model


def test_task_a_training_and_calibration(tmp_path: Path) -> None:
    """Verify training produces bounded calibrated probabilities & valid subgroup metrics."""
    proc_dir = tmp_path / "processed"
    reg_dir = tmp_path / "registry"
    art_dir = tmp_path / "artifacts"

    prepare_datasets(output_dir=proc_dir, seed=42)
    report = train_and_register_model(
        processed_dir=proc_dir,
        registry_dir=reg_dir,
        backend_artifacts_dir=art_dir,
        seed=42,
    )

    assert (reg_dir / "model.joblib").exists()
    assert (art_dir / "model.joblib").exists()
    assert len(report["artifact_sha256"]) == 64

    metrics = evaluate_registered_model(
        model_path=reg_dir / "model.joblib",
        test_parquet=proc_dir / "test.parquet",
    )
    assert metrics["n_test"] == 61
    # Must outperform null-model Brier score (0.2483) and achieve strong AUROC
    assert metrics["auroc"] >= 0.80
    assert metrics["brier_score"] < 0.20
    assert "female" in report["subgroup_fairness_sex"]
    assert "male" in report["subgroup_fairness_sex"]
