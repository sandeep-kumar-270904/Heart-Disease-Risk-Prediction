"""HeartXAI 2.0 — Task A Model Evaluation, Calibration Diagnostics & Reproducibility Audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

from ml.pipelines.prepare_data import FEATURE_COLUMNS, PROCESSED_DIR
from ml.pipelines.train_model import REGISTRY_DIR, TaskABundle, compute_ece


def compute_adaptive_quantile_ece(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> float:
    """Compute equal-mass (quantile) Expected Calibration Error diagnostic."""
    order = np.argsort(y_prob)
    y_t_sorted = y_true[order]
    y_p_sorted = y_prob[order]
    splits = np.array_split(np.arange(len(y_t_sorted)), n_bins)
    total = len(y_true)
    ece = 0.0
    for idx_arr in splits:
        if len(idx_arr) == 0:
            continue
        ece += (len(idx_arr) / total) * abs(
            float(y_p_sorted[idx_arr].mean()) - float(y_t_sorted[idx_arr].mean())
        )
    return float(ece)


def evaluate_registered_model(
    model_path: Path = REGISTRY_DIR / "model.joblib",
    test_parquet: Path = PROCESSED_DIR / "test.parquet",
) -> dict[str, Any]:
    """Load serialized Task A artifact dictionary and recompute discrimination & calibration."""
    artifact: dict[str, Any] = joblib.load(model_path)
    bundle = TaskABundle(
        model_version=artifact["model_version"],
        feature_columns=artifact["feature_columns"],
        xgb_estimator=artifact["xgb_estimator"],
        platt_calibrator=artifact["platt_calibrator"],
        cohort_feature_means=artifact["cohort_feature_means"],
        feature_bounds=artifact["feature_bounds"],
        background_sample=artifact["background_sample"],
    )
    test_df = pd.read_parquet(test_parquet)

    X_test = test_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y_test = test_df["target"].to_numpy(dtype=int)

    raw_margins = bundle.predict_raw_margins(X_test)
    uncalibrated_sigmoid = 1.0 / (1.0 + np.exp(-raw_margins))
    probs = bundle.predict_proba(X_test)[:, 1]

    ece_10, bins_10 = compute_ece(y_test, probs, n_bins=10)
    ece_5, _ = compute_ece(y_test, probs, n_bins=5)
    adaptive_ece_10 = compute_adaptive_quantile_ece(y_test, probs, n_bins=10)
    raw_brier = float(brier_score_loss(y_test, uncalibrated_sigmoid))
    raw_ece_10, _ = compute_ece(y_test, uncalibrated_sigmoid, n_bins=10)

    return {
        "model_version": bundle.model_version,
        "artifact_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "feature_order_matches_contract": bundle.feature_columns == FEATURE_COLUMNS,
        "n_test": len(y_test),
        "auroc": round(float(roc_auc_score(y_test, probs)), 4),
        "brier_score": round(float(brier_score_loss(y_test, probs)), 4),
        "ece": round(ece_10, 4),
        "diagnostic_ece_5_bins": round(ece_5, 4),
        "diagnostic_adaptive_quantile_ece_10": round(adaptive_ece_10, 4),
        "raw_margin_sigmoid_brier": round(raw_brier, 4),
        "raw_margin_sigmoid_ece_10": round(raw_ece_10, 4),
        "reliability_bins": bins_10,
        "calibration_limitation_note": (
            "Holdout n=61 leaves 2-4 samples in several uniform probability bins, making "
            "10-bin ECE (0.1120) sensitive to single-sample quantization variance. Platt "
            "scaling fits 80%-fold OOF margins and pairs with the 100%-train XGBoost model; "
            "provisional target (ECE <= 0.05) requires larger external validation cohorts."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_registered_model(), indent=2))
