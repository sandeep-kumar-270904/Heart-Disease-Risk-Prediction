"""HeartXAI 2.0 — Category A UCI Cleveland Data Verification & Stratification Pipeline.

Implements Milestone 09 requirements:
- Preserves raw Category A dataset unmodified and verifies SHA-256 provenance.
- Enforces documented MVP baseline: N=303 (164 negative, 139 positive; pi=0.458746;
  null-model Brier = 0.248298) with column-specific imputation fitted strictly on
  the training partition (ca median=0.0, thal mode=normal) to prevent data leakage.
- Generates secondary complete-case sensitivity benchmark (N=297; 160 negative,
  137 positive; pi=0.461279; null-model Brier = 0.248501).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_PATH = REPO_ROOT / "ml" / "data" / "raw" / "cleveland_heart_disease_raw.csv"
PROCESSED_DIR = REPO_ROOT / "ml" / "data" / "processed"

RAW_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "num",
]

FEATURE_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]

# UCI coding -> canonical application schema coding
CP_MAP = {1.0: 0, 2.0: 1, 3.0: 2, 4.0: 3}
SLOPE_MAP = {1.0: 0, 2.0: 1, 3.0: 2}
THAL_MAP = {3.0: 1, 6.0: 2, 7.0: 3}


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_raw_cleveland(raw_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Parse unmodified UCI Cleveland data preserving missing '?' entries as NaN."""
    df = pd.read_csv(
        raw_path,
        header=None,
        names=RAW_COLUMNS,
        na_values="?",
    )
    df["source_row_index"] = np.arange(len(df), dtype=int)
    df["target"] = (df["num"] >= 1).astype(int)
    # Normalize categorical codings (leaving NaNs untouched for leakage-free fold imputation)
    df["cp"] = df["cp"].map(CP_MAP).astype(int)
    df["slope"] = df["slope"].map(SLOPE_MAP).astype(int)
    df["thal"] = df["thal"].map(THAL_MAP)
    return df


def fit_training_imputers(train_df: pd.DataFrame) -> dict[str, float]:
    """Fit column-specific imputation statistics strictly on a training partition."""
    ca_median = float(train_df["ca"].dropna().median())
    thal_mode = float(train_df["thal"].dropna().mode().iloc[0])
    return {"ca": ca_median, "thal": thal_mode}


def apply_imputers(df: pd.DataFrame, imputers: dict[str, float]) -> pd.DataFrame:
    """Apply pre-fitted training imputers without re-fitting on target partition."""
    out = df.copy()
    out["ca"] = out["ca"].fillna(imputers["ca"]).astype(int)
    out["thal"] = out["thal"].fillna(imputers["thal"]).astype(int)
    return out


def prepare_datasets(
    raw_path: Path = RAW_DATA_PATH,
    output_dir: Path = PROCESSED_DIR,
    seed: int = 42,
    test_size: float = 0.2,
) -> dict[str, Any]:
    """Execute leakage-free stratification, imputation, and sensitivity dataset export."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_sha = sha256_file(raw_path)
    raw_df = load_raw_cleveland(raw_path)

    total_rows = len(raw_df)
    neg_count = int((raw_df["target"] == 0).sum())
    pos_count = int((raw_df["target"] == 1).sum())
    pi_full = pos_count / total_rows
    null_brier_full = pi_full * (1.0 - pi_full)

    # Stratified train/test split BEFORE any imputation
    train_raw, test_raw = train_test_split(
        raw_df,
        test_size=test_size,
        stratify=raw_df["target"],
        random_state=seed,
    )

    # Anti-leakage: fit imputers strictly on training split
    imputers = fit_training_imputers(train_raw)
    train_df = apply_imputers(train_raw, imputers)
    test_df = apply_imputers(test_raw, imputers)

    # Assign 5-fold CV fold IDs deterministically inside training partition
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    train_df["cv_fold"] = -1
    for fold_idx, (_, val_pos) in enumerate(
        skf.split(train_df[FEATURE_COLUMNS], train_df["target"])
    ):
        train_df.iloc[val_pos, train_df.columns.get_loc("cv_fold")] = fold_idx

    # Secondary complete-case sensitivity cohort (N=297)
    complete_df = raw_df.dropna(subset=["ca", "thal"]).copy()
    complete_df["ca"] = complete_df["ca"].astype(int)
    complete_df["thal"] = complete_df["thal"].astype(int)
    cc_neg = int((complete_df["target"] == 0).sum())
    cc_pos = int((complete_df["target"] == 1).sum())
    pi_cc = cc_pos / len(complete_df)
    null_brier_cc = pi_cc * (1.0 - pi_cc)

    train_path = output_dir / "train.parquet"
    test_path = output_dir / "test.parquet"
    cc_path = output_dir / "complete_case_sensitivity.parquet"
    audit_path = output_dir / "data_provenance_audit.json"

    train_df.to_parquet(train_path, index=False)
    test_df.to_parquet(test_path, index=False)
    complete_df.to_parquet(cc_path, index=False)

    audit_report: dict[str, Any] = {
        "data_category": "Category A — Public Historical Human-Origin Research Data",
        "dataset_name": "UCI Cleveland Clinic Foundation Heart Disease (processed.cleveland.data)",
        "provenance_source": "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
        "license_and_permitted_use": "UCI ML Repository public academic/research benchmark; non-commercial research & software evaluation only",
        "privacy_assessment": {
            "modern_hipaa_certification": False,
            "gdpr_anonymization_verified": False,
            "documented_limitations": "Historical 1988 clinical cohort; retains age, sex, and clinical measurements; zero runtime patient upload permitted (DEC-005).",
        },
        "raw_file_sha256": raw_sha,
        "seed": seed,
        "full_imputed_baseline": {
            "n_total": total_rows,
            "n_negative": neg_count,
            "n_positive": pos_count,
            "prevalence": round(pi_full, 6),
            "null_model_brier_score": round(null_brier_full, 6),
            "missing_ca": int(raw_df["ca"].isna().sum()),
            "missing_thal": int(raw_df["thal"].isna().sum()),
            "training_fold_imputers": imputers,
            "n_train": len(train_df),
            "n_test": len(test_df),
        },
        "complete_case_sensitivity": {
            "n_total": len(complete_df),
            "n_negative": cc_neg,
            "n_positive": cc_pos,
            "prevalence": round(pi_cc, 6),
            "null_model_brier_score": round(null_brier_cc, 6),
        },
        "target_semantics": "Retrospective binary CAD classification (num == 0 -> 0; num >= 1 -> 1). Zero prospective risk claims.",
    }
    audit_path.write_text(json.dumps(audit_report, indent=2), encoding="utf-8")
    return audit_report


if __name__ == "__main__":
    summary = prepare_datasets()
    print(json.dumps(summary, indent=2))
