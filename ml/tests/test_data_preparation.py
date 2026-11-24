"""Tests for Milestone 09 ML data preparation, provenance, and anti-leakage guarantees."""

from pathlib import Path

import pandas as pd
from ml.pipelines.prepare_data import (
    FEATURE_COLUMNS,
    apply_imputers,
    fit_training_imputers,
    prepare_datasets,
)


def test_prepare_datasets_baseline_and_anti_leakage(tmp_path: Path) -> None:
    """Verify exact N=303 baseline, N=297 sensitivity, zero split overlap, and determinism."""
    report_a = prepare_datasets(output_dir=tmp_path / "run_a", seed=42)
    prepare_datasets(output_dir=tmp_path / "run_b", seed=42)

    assert report_a["full_imputed_baseline"]["n_total"] == 303
    assert report_a["full_imputed_baseline"]["n_negative"] == 164
    assert report_a["full_imputed_baseline"]["n_positive"] == 139
    assert report_a["full_imputed_baseline"]["missing_ca"] == 4
    assert report_a["full_imputed_baseline"]["missing_thal"] == 2
    assert report_a["full_imputed_baseline"]["null_model_brier_score"] == 0.248298

    assert report_a["complete_case_sensitivity"]["n_total"] == 297
    assert report_a["complete_case_sensitivity"]["n_negative"] == 160
    assert report_a["complete_case_sensitivity"]["n_positive"] == 137
    assert report_a["complete_case_sensitivity"]["null_model_brier_score"] == 0.248501

    train_a = pd.read_parquet(tmp_path / "run_a" / "train.parquet")
    test_a = pd.read_parquet(tmp_path / "run_a" / "test.parquet")
    train_b = pd.read_parquet(tmp_path / "run_b" / "train.parquet")

    # Zero index overlap between train and test partitions
    assert set(train_a["source_row_index"]).isdisjoint(set(test_a["source_row_index"]))
    assert len(train_a) + len(test_a) == 303
    assert not train_a[FEATURE_COLUMNS].isna().any().any()
    assert not test_a[FEATURE_COLUMNS].isna().any().any()

    # 100% deterministic split across identical seeds
    pd.testing.assert_frame_equal(train_a, train_b)


def test_imputers_fit_strictly_on_training_partition() -> None:
    """Verify imputer statistics ignore validation/test rows."""
    train_df = pd.DataFrame({"ca": [0.0, 0.0, 1.0, None], "thal": [1.0, 1.0, 3.0, None]})
    test_df = pd.DataFrame({"ca": [3.0, 3.0, None], "thal": [3.0, 3.0, None]})

    imputers = fit_training_imputers(train_df)
    assert imputers == {"ca": 0.0, "thal": 1.0}

    transformed_test = apply_imputers(test_df, imputers)
    assert int(transformed_test["ca"].iloc[2]) == 0
    assert int(transformed_test["thal"].iloc[2]) == 1
