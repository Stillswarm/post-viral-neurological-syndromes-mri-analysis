#!/usr/bin/env python3
"""Nested CV for an exploratory sensitivity-targeted PCC screening threshold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev

import numpy as np
from sklearn.metrics import (
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, cross_val_predict

from train_screening_baseline import build_dataset, make_estimator, sha256


def metrics_at_threshold(
    y_true: np.ndarray, probabilities: np.ndarray, threshold: float
) -> dict[str, float]:
    predictions = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
    return {
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, predictions)),
        "sensitivity": float(recall_score(y_true, predictions, zero_division=0)),
        "specificity": float(tn / (tn + fp)) if tn + fp else 0.0,
        "brier_score": float(brier_score_loss(y_true, probabilities)),
    }


def select_threshold(
    y_true: np.ndarray, probabilities: np.ndarray, target_sensitivity: float
) -> tuple[float, float, float]:
    candidates = np.unique(np.concatenate(([0.0], probabilities)))
    selected = 0.0
    selected_sensitivity = 1.0
    selected_specificity = 0.0
    for threshold in candidates:
        predictions = probabilities >= threshold
        tp = int(np.sum((y_true == 1) & predictions))
        fn = int(np.sum((y_true == 1) & ~predictions))
        tn = int(np.sum((y_true == 0) & ~predictions))
        fp = int(np.sum((y_true == 0) & predictions))
        sensitivity = tp / (tp + fn) if tp + fn else 0.0
        specificity = tn / (tn + fp) if tn + fp else 0.0
        if sensitivity >= target_sensitivity:
            selected = float(threshold)
            selected_sensitivity = sensitivity
            selected_specificity = specificity
    return selected, selected_sensitivity, selected_specificity


def calibration_summary(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    order = np.argsort(probabilities)
    bins = [indices for indices in np.array_split(order, 4) if len(indices)]
    ece = 0.0
    for indices in bins:
        observed = float(np.mean(y_true[indices]))
        predicted = float(np.mean(probabilities[indices]))
        ece += len(indices) / len(y_true) * abs(observed - predicted)
    return {
        "brier_score": float(brier_score_loss(y_true, probabilities)),
        "mean_predicted_minus_observed_rate": float(np.mean(probabilities) - np.mean(y_true)),
        "four_bin_expected_calibration_error": float(ece),
    }


def summarize(rows: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    names = rows[0].keys()
    return {
        name: {
            "mean": round(mean(row[name] for row in rows), 4),
            "sd": round(pstdev(row[name] for row in rows), 4),
        }
        for name in names
    }


def run_nested_cv(
    x: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    n_splits: int,
    n_repeats: int,
    inner_splits: int,
    target_sensitivity: float,
    seed: int,
) -> dict[str, Any]:
    outer = RepeatedStratifiedKFold(
        n_splits=n_splits, n_repeats=n_repeats, random_state=seed
    )
    estimator = make_estimator(feature_names, use_demographics=False)
    predictions_by_repeat = np.full((n_repeats, len(y)), np.nan, dtype=float)
    fold_metrics: list[dict[str, float]] = []
    selected_thresholds = []
    inner_operating_points = []

    for split_index, (train_index, test_index) in enumerate(outer.split(x, y)):
        x_train, y_train = x[train_index], y[train_index]
        inner = StratifiedKFold(
            n_splits=inner_splits,
            shuffle=True,
            random_state=seed + split_index + 1,
        )
        inner_probabilities = cross_val_predict(
            estimator,
            x_train,
            y_train,
            cv=inner,
            method="predict_proba",
        )[:, 1]
        threshold, inner_sensitivity, inner_specificity = select_threshold(
            y_train, inner_probabilities, target_sensitivity
        )
        fitted = make_estimator(feature_names, use_demographics=False)
        fitted.fit(x_train, y_train)
        test_probabilities = fitted.predict_proba(x[test_index])[:, 1]
        fold_metrics.append(metrics_at_threshold(y[test_index], test_probabilities, threshold))
        selected_thresholds.append(threshold)
        inner_operating_points.append({
            "sensitivity": inner_sensitivity,
            "specificity": inner_specificity,
        })
        repeat_index = split_index // n_splits
        predictions_by_repeat[repeat_index, test_index] = test_probabilities

    repeat_calibration = []
    for repeat_index in range(n_repeats):
        probabilities = predictions_by_repeat[repeat_index]
        if np.isnan(probabilities).any():
            raise RuntimeError(f"Missing outer-fold predictions in repeat {repeat_index + 1}")
        repeat_calibration.append(calibration_summary(y, probabilities))

    inner_summary = summarize(inner_operating_points)
    threshold_summary = {
        "mean": round(mean(selected_thresholds), 4),
        "sd": round(pstdev(selected_thresholds), 4),
        "minimum": round(float(min(selected_thresholds)), 4),
        "maximum": round(float(max(selected_thresholds)), 4),
    }
    return {
        "outer_fold_metrics_at_selected_threshold": summarize(fold_metrics),
        "selected_threshold": threshold_summary,
        "inner_training_operating_point": inner_summary,
        "calibration_per_repeat": summarize(repeat_calibration),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, nargs="?", default=Path("data/raw/Dryad_final.xlsx"))
    parser.add_argument("--splits", type=int, default=5)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--inner-splits", type=int, default=4)
    parser.add_argument("--target-sensitivity", type=float, default=0.80)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--output", type=Path,
        default=Path("reports/generated/threshold_calibration.json"),
    )
    args = parser.parse_args()
    if not args.workbook.is_file():
        parser.error(f"Workbook not found: {args.workbook}")
    if args.splits < 2 or args.inner_splits < 2 or args.repeats < 1:
        parser.error("splits and inner-splits must be >=2; repeats must be >=1")
    if not 0.5 <= args.target_sensitivity < 1:
        parser.error("target-sensitivity must be >=0.5 and <1")

    x, y, feature_names = build_dataset(args.workbook)
    result = run_nested_cv(
        x,
        y,
        feature_names,
        args.splits,
        args.repeats,
        args.inner_splits,
        args.target_sensitivity,
        args.seed,
    )
    report = {
        "source_doi": "10.5061/dryad.kkwh70s9g",
        "workbook_sha256": sha256(args.workbook),
        "cohort": {"n": len(y), "positive": int(y.sum()), "negative": int((y == 0).sum())},
        "model": "L2 logistic regression on six prespecified whole-brain DMI measures",
        "target": "Concurrent MoCA < 26 screening label among PCC records",
        "threshold_selection": {
            "method": "Inner cross-validated probabilities on each outer training set; choose the highest threshold attaining the target sensitivity",
            "target_sensitivity": args.target_sensitivity,
            "outer_splitter": "RepeatedStratifiedKFold",
            "outer_splits": args.splits,
            "outer_repeats": args.repeats,
            "inner_splitter": "StratifiedKFold",
            "inner_splits": args.inner_splits,
            "seed": args.seed,
            "note": "The 0.80 default is an exploratory analysis target, not a clinically selected operating point.",
        },
        "results": result,
        "limitations": [
            "Repeated folds overlap; reported SDs are descriptive and are not confidence intervals.",
            "The workbook has no participant ID, so subject-level split independence cannot be independently verified.",
            "No independent validation cohort was evaluated.",
            "Exploratory research only; not a diagnostic or clinical decision tool.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Completed nested evaluation: {args.splits * args.repeats} outer folds")
    print(f"Target sensitivity: {args.target_sensitivity:.2f}; mean selected threshold: "
          f"{result['selected_threshold']['mean']:.3f} mean")
    operating = result["outer_fold_metrics_at_selected_threshold"]
    print(f"Outer mean sensitivity={operating['sensitivity']['mean']:.3f}; "
          f"specificity={operating['specificity']['mean']:.3f}; "
          f"ROC AUC={operating['roc_auc']['mean']:.3f}")
    print(f"Aggregate report: {args.output}")


if __name__ == "__main__":
    main()
