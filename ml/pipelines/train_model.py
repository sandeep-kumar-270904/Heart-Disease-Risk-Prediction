"""HeartXAI 2.0 — Task A XGBoost Training & Probability Calibration Pipeline (Milestone 10).

Trains a regularized shallow XGBoost classifier on Category A UCI Cleveland training
data and applies post-hoc Platt scaling (sigmoid calibration) via 5-fold cross-validation.
Persists versioned artifacts with SHA-256 integrity digests to ml/registry/ and
backend/app/ml/artifacts/.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

from ml.pipelines.prepare_data import FEATURE_COLUMNS, PROCESSED_DIR

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_DIR = REPO_ROOT / "ml" / "registry"
BACKEND_ARTIFACTS_DIR = REPO_ROOT / "backend" / "app" / "ml" / "artifacts"
MODEL_VERSION = "v2.0.0"


def compute_ece(
    y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
) -> tuple[float, list[dict[str, float]]]:
    """Compute Expected Calibration Error (ECE) and reliability curve bin metrics."""
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    bins_summary: list[dict[str, float]] = []
    n_total = len(y_true)

    for idx in range(n_bins):
        low, high = float(bin_edges[idx]), float(bin_edges[idx + 1])
        if idx == n_bins - 1:
            mask = (y_prob >= low) & (y_prob <= high)
        else:
            mask = (y_prob >= low) & (y_prob < high)
        count = int(mask.sum())
        if count > 0:
            avg_conf = float(y_prob[mask].mean())
            emp_acc = float(y_true[mask].mean())
            ece += (count / n_total) * abs(avg_conf - emp_acc)
            bins_summary.append(
                {
                    "bin_low": round(low, 2),
                    "bin_high": round(high, 2),
                    "count": float(count),
                    "mean_predicted_prob": round(avg_conf, 4),
                    "observed_frequency": round(emp_acc, 4),
                }
            )
    return float(ece), bins_summary


@dataclass
class TaskABundle:
    """Self-contained calibrated Task A model bundle for in-process inference & TreeSHAP."""

    model_version: str
    feature_columns: list[str]
    xgb_estimator: XGBClassifier
    platt_calibrator: LogisticRegression
    cohort_feature_means: dict[str, float]
    feature_bounds: dict[str, tuple[float, float]]
    background_sample: np.ndarray

    def predict_raw_margins(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Compute raw XGBoost log-odds margins f(x) compatible with TreeSHAP."""
        if isinstance(X, pd.DataFrame):
            arr = X[self.feature_columns].to_numpy(dtype=float)
        else:
            arr = np.asarray(X, dtype=float)
        return self.xgb_estimator.predict(arr, output_margin=True)

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Compute Platt-calibrated CAD association probabilities [P(y=0), P(y=1)]."""
        margins = self.predict_raw_margins(X).reshape(-1, 1)
        return self.platt_calibrator.predict_proba(margins)


def train_and_register_model(
    processed_dir: Path = PROCESSED_DIR,
    registry_dir: Path = REGISTRY_DIR,
    backend_artifacts_dir: Path = BACKEND_ARTIFACTS_DIR,
    seed: int = 42,
) -> dict[str, Any]:
    """Train regularized XGBoost + out-of-fold Platt calibration and save artifacts."""
    registry_dir.mkdir(parents=True, exist_ok=True)
    backend_artifacts_dir.mkdir(parents=True, exist_ok=True)

    train_df = pd.read_parquet(processed_dir / "train.parquet")
    test_df = pd.read_parquet(processed_dir / "test.parquet")

    X_train = train_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y_train = train_df["target"].to_numpy(dtype=int)
    X_test = test_df[FEATURE_COLUMNS].to_numpy(dtype=float)
    y_test = test_df["target"].to_numpy(dtype=int)

    xgb_params: dict[str, Any] = {
        "n_estimators": 90,
        "max_depth": 2,
        "learning_rate": 0.05,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "min_child_weight": 3.0,
        "reg_alpha": 0.75,
        "reg_lambda": 3.0,
        "eval_metric": "logloss",
        "random_state": seed,
        "n_jobs": 1,
    }

    # 1. Generate unbiased 5-fold out-of-fold raw margins for Platt calibration
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    oof_margins = np.zeros(len(y_train), dtype=float)
    for train_idx, val_idx in skf.split(X_train, y_train):
        fold_model = XGBClassifier(**xgb_params)
        fold_model.fit(X_train[train_idx], y_train[train_idx])
        oof_margins[val_idx] = fold_model.predict(X_train[val_idx], output_margin=True)

    # Fit Platt logistic calibrator on out-of-fold log-odds margins
    platt_calibrator = LogisticRegression(random_state=seed)
    platt_calibrator.fit(oof_margins.reshape(-1, 1), y_train)
    oof_probs = platt_calibrator.predict_proba(oof_margins.reshape(-1, 1))[:, 1]

    # 2. Fit final XGBoost model on full training partition for inference & TreeSHAP
    final_xgb = XGBClassifier(**xgb_params)
    final_xgb.fit(X_train, y_train)

    # Also compute sklearn CalibratedClassifierCV benchmark for cross-check
    cal_cv = CalibratedClassifierCV(XGBClassifier(**xgb_params), method="sigmoid", cv=5)
    cal_cv.fit(X_train, y_train)

    cohort_means = {
        col: round(float(train_df[col].mean()), 4) for col in FEATURE_COLUMNS
    }
    feature_bounds = {
        col: (float(train_df[col].min()), float(train_df[col].max()))
        for col in FEATURE_COLUMNS
    }
    background_sample = X_train[: min(100, len(X_train))].copy()

    bundle = TaskABundle(
        model_version=MODEL_VERSION,
        feature_columns=list(FEATURE_COLUMNS),
        xgb_estimator=final_xgb,
        platt_calibrator=platt_calibrator,
        cohort_feature_means=cohort_means,
        feature_bounds=feature_bounds,
        background_sample=background_sample,
    )

    # 3. Evaluate on hold-out test split (N=61)
    test_probs = bundle.predict_proba(X_test)[:, 1]
    test_brier = float(brier_score_loss(y_test, test_probs))
    test_auroc = float(roc_auc_score(y_test, test_probs))
    test_ece, reliability_bins = compute_ece(y_test, test_probs, n_bins=10)

    oof_brier = float(brier_score_loss(y_train, oof_probs))
    oof_auroc = float(roc_auc_score(y_train, oof_probs))
    oof_ece, _ = compute_ece(y_train, oof_probs, n_bins=10)

    # Subgroup evaluation across sex (0 = Female, 1 = Male)
    subgroup_metrics: dict[str, dict[str, float]] = {}
    for sex_val, label in ((0, "female"), (1, "male")):
        mask = test_df["sex"].to_numpy(dtype=int) == sex_val
        if int(mask.sum()) > 0 and len(np.unique(y_test[mask])) > 1:
            subgroup_metrics[label] = {
                "n": float(mask.sum()),
                "auroc": round(float(roc_auc_score(y_test[mask], test_probs[mask])), 4),
                "brier_score": round(
                    float(brier_score_loss(y_test[mask], test_probs[mask])), 4
                ),
            }

    # 4. Serialize model artifact dictionary (zero custom class pickle coupling) + SHA-256 hash
    artifact_payload: dict[str, Any] = {
        "model_version": MODEL_VERSION,
        "feature_columns": list(FEATURE_COLUMNS),
        "xgb_estimator": final_xgb,
        "platt_calibrator": platt_calibrator,
        "cohort_feature_means": cohort_means,
        "feature_bounds": feature_bounds,
        "background_sample": background_sample,
    }
    reg_model_path = registry_dir / "model.joblib"
    app_model_path = backend_artifacts_dir / f"heartxai_task_a_{MODEL_VERSION}.joblib"
    latest_app_path = backend_artifacts_dir / "model.joblib"

    joblib.dump(artifact_payload, reg_model_path)
    joblib.dump(artifact_payload, app_model_path)
    joblib.dump(artifact_payload, latest_app_path)

    artifact_sha256 = hashlib.sha256(reg_model_path.read_bytes()).hexdigest()

    evaluation_report: dict[str, Any] = {
        "model_version": MODEL_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "artifact_sha256": artifact_sha256,
        "task_scope": "Task A — Experimental Retrospective UCI Cleveland Binary CAD Classifier (DEC-003 Option A)",
        "non_diagnostic_disclaimer": "Experimental research model evaluated on N=303 retrospective data; not cleared for clinical diagnosis.",
        "training_oof_metrics": {
            "n_samples": len(y_train),
            "auroc": round(oof_auroc, 4),
            "brier_score": round(oof_brier, 4),
            "ece": round(oof_ece, 4),
        },
        "holdout_test_metrics": {
            "n_samples": len(y_test),
            "auroc": round(test_auroc, 4),
            "brier_score": round(test_brier, 4),
            "ece": round(test_ece, 4),
            "provisional_targets_note": "Thresholds (Brier <= 0.12, ECE <= 0.05) are provisional small-N evaluation targets requiring prospective external validation (Phase 12.2.2).",
        },
        "subgroup_fairness_sex": subgroup_metrics,
        "reliability_bins": reliability_bins,
        "hyperparameters": xgb_params,
    }

    (registry_dir / "model_card.json").write_text(
        json.dumps(evaluation_report, indent=2), encoding="utf-8"
    )
    (registry_dir / "evaluation_report.json").write_text(
        json.dumps(evaluation_report, indent=2), encoding="utf-8"
    )
    return evaluation_report


if __name__ == "__main__":
    report = train_and_register_model()
    print(json.dumps(report, indent=2))
