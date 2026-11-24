"""HeartXAI 2.0 — Task A Model Evaluation & Reliability Audit Utility."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

from ml.pipelines.prepare_data import FEATURE_COLUMNS, PROCESSED_DIR
from ml.pipelines.train_model import REGISTRY_DIR, TaskABundle, compute_ece


def evaluate_registered_model(
    model_path: Path = REGISTRY_DIR / "model.joblib",
    test_parquet: Path = PROCESSED_DIR / "test.parquet",
) -> dict[str, Any]:
    """Load serialized Task A artifact dictionary and recompute discrimination & calibration metrics."""
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

    probs = bundle.predict_proba(X_test)[:, 1]
    ece, bins = compute_ece(y_test, probs, n_bins=10)
    return {
        "model_version": bundle.model_version,
        "n_test": len(y_test),
        "auroc": round(float(roc_auc_score(y_test, probs)), 4),
        "brier_score": round(float(brier_score_loss(y_test, probs)), 4),
        "ece": round(ece, 4),
        "reliability_bins": bins,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_registered_model(), indent=2))
