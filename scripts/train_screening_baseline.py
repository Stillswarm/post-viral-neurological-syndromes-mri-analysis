#!/usr/bin/env python3
"""Run an exploratory repeated-CV baseline for concurrent PCC MoCA screening."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

import numpy as np
from openpyxl import load_workbook
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DMI_FEATURES = [
    "total_gm_extra",
    "total_gm_csf",
    "total_gm_intra",
    "total_wm_extra",
    "total_wm_csf",
    "total_wm_intra",
]
DEMOGRAPHIC_FEATURES = ["age", "sex"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_dataset(path: Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    workbook = load_workbook(path, read_only=True, data_only=True)
    if "Combined" not in workbook.sheetnames:
        raise ValueError("Workbook is missing the Combined sheet")
    sheet = workbook["Combined"]
    rows = sheet.iter_rows(values_only=True)
    headers = [str(value).strip() if value is not None else "" for value in next(rows)]
    indices = {name.lower(): index for index, name in enumerate(headers)}
    required = ["group", "moca", *DEMOGRAPHIC_FEATURES, *DMI_FEATURES]
    missing = [name for name in required if name.lower() not in indices]
    if missing:
        workbook.close()
        raise ValueError(f"Required columns are missing: {missing}")

    x_rows: list[list[Any]] = []
    y_values: list[int] = []
    feature_names = [*DEMOGRAPHIC_FEATURES, *DMI_FEATURES]
    for row in rows:
        group = str(row[indices["group"]] or "").strip().upper()
        if group != "PCC":
            continue
        score = row[indices["moca"]]
        if score is None or (isinstance(score, str) and not score.strip()):
            continue
        try:
            score = float(score)
        except (TypeError, ValueError):
            continue
        x_rows.append([row[indices[name.lower()]] for name in feature_names])
        y_values.append(int(score < 26))
    workbook.close()

    x = np.asarray(x_rows, dtype=object)
    y = np.asarray(y_values, dtype=int)
    if len(y) != 88 or int(y.sum()) != 36 or int((y == 0).sum()) != 52:
        raise ValueError(
            "Expected 88 labeled PCC records (36 MoCA<26, 52 MoCA>=26); "
            f"found n={len(y)}, positive={int(y.sum())}, negative={int((y == 0).sum())}. "
            "Review the source version and audit before modeling."
        )
    return x, y, feature_names


def make_estimator(feature_names: list[str], use_demographics: bool) -> Pipeline:
    numeric_indices = [feature_names.index(name) for name in DMI_FEATURES]
    categorical_indices = (
        [feature_names.index(name) for name in DEMOGRAPHIC_FEATURES]
        if use_demographics else []
    )
    transformers = [
        ("dmi", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), numeric_indices),
    ]
    if categorical_indices:
        transformers.append(("demographics", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), categorical_indices))
    preprocess = ColumnTransformer(transformers=transformers, remainder="drop")
    return Pipeline([
        ("preprocess", preprocess),
        ("model", LogisticRegression(C=1.0, solver="liblinear", max_iter=2000)),
    ])


def fold_metrics(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    predictions = (probabilities >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
    return {
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, predictions)),
        "sensitivity": float(recall_score(y_true, predictions, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else 0.0,
        "brier_score": float(brier_score_loss(y_true, probabilities)),
    }


def summarize_cv(
    x: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    n_splits: int,
    n_repeats: int,
    seed: int,
) -> dict[str, Any]:
    splitter = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=seed
    )
    specifications = [
        ("majority_baseline", None, False),
        ("dmi_only", "dmi", False),
        ("dmi_plus_age_sex", "combined", True),
        ("age_sex_only", "demographics", True),
    ]
    results: dict[str, Any] = {}
    for model_name, model_kind, use_demographics in specifications:
        fold_results = []
        for train_index, test_index in splitter.split(x, y):
            if model_kind is None:
                classifier = DummyClassifier(strategy="prior")
            elif model_kind == "demographics":
                # A demographics-only estimator uses one-hot age bins and sex.
                categorical_indices = [feature_names.index(name) for name in DEMOGRAPHIC_FEATURES]
                preprocess = ColumnTransformer(transformers=[
                    ("demographics", Pipeline([
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]), categorical_indices),
                ], remainder="drop")
                classifier = Pipeline([
                    ("preprocess", preprocess),
                    ("model", LogisticRegression(C=1.0, solver="liblinear", max_iter=2000)),
                ])
            else:
                classifier = make_estimator(feature_names, use_demographics)
            classifier.fit(x[train_index], y[train_index])
            probabilities = classifier.predict_proba(x[test_index])[:, 1]
            fold_results.append(fold_metrics(y[test_index], probabilities))

        metric_names = fold_results[0].keys()
        results[model_name] = {
            metric: {
                "mean": round(mean(row[metric] for row in fold_results), 4),
                "sd_across_folds": round(pstdev(row[metric] for row in fold_results), 4),
            }
            for metric in metric_names
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, nargs="?", default=Path("data/raw/Dryad_final.xlsx"))
    parser.add_argument("--splits", type=int, default=5)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--output", type=Path,
        default=Path("reports/generated/screening_baseline.json"),
    )
    args = parser.parse_args()
    if not args.workbook.is_file():
        parser.error(f"Workbook not found: {args.workbook}")
    if args.splits < 2 or args.repeats < 1:
        parser.error("--splits must be >=2 and --repeats must be >=1")

    x, y, feature_names = build_dataset(args.workbook)
    model_results = summarize_cv(
        x, y, feature_names, args.splits, args.repeats, args.seed
    )
    report = {
        "source_doi": "10.5061/dryad.kkwh70s9g",
        "workbook_sha256": sha256(args.workbook),
        "task": "Concurrent MoCA screening among PCC records; positive label is MoCA < 26",
        "cohort": {"n": len(y), "positive": int(y.sum()), "negative": int((y == 0).sum())},
        "features": {
            "dmi": DMI_FEATURES,
            "demographics": DEMOGRAPHIC_FEATURES,
            "target_excluded_from_predictors": "moca",
        },
        "evaluation": {
            "splitter": "RepeatedStratifiedKFold",
            "splits": args.splits,
            "repeats": args.repeats,
            "folds": args.splits * args.repeats,
            "seed": args.seed,
            "threshold": 0.5,
            "summary_note": "Mean and fold SD are descriptive; overlapping CV folds are not independent confidence intervals.",
        },
        "models": model_results,
        "clinical_use_note": "Exploratory research only; not a diagnostic or clinical decision tool.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Completed {args.splits * args.repeats} repeated CV folds; report: {args.output}")
    print(f"PCC labeled cohort: n={len(y)}, positive={int(y.sum())}, negative={int((y == 0).sum())}")
    for model, metrics in model_results.items():
        auc = metrics["roc_auc"]["mean"]
        bal_acc = metrics["balanced_accuracy"]["mean"]
        print(f"- {model}: mean ROC AUC={auc:.3f}; balanced accuracy={bal_acc:.3f}")


if __name__ == "__main__":
    main()
