"""Phase 8 Experimental Suite:
- 8.1 Leakage-Safe Threshold Selection (Train / Validation / Untouched Test)
- 8.2 Probability Calibration (Uncalibrated vs. Sigmoid vs. Isotonic)
- 8.3 Comparative ML Experimentation (Dummy, Logistic Regression, Random Forest, HistGradientBoosting)
- 8.5 Subgroup & Robustness Analysis (with Minimum Sample-Size Guardrails)

Preserves the existing saved model (`models/logistic_regression_pipeline.joblib`) and
historical metrics (`outputs/metrics_summary.json`) completely untouched.
All Phase 8 artifacts are exported cleanly under `outputs/phase8/`.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import (
    CAP_COLS,
    CAT_COLS,
    DATA_RAW_PATH,
    ID_COL,
    NUM_COLS,
    OUTPUTS_DIR,
    PLAIN_NUM_COLS,
    RANDOM_STATE,
    TARGET_COL,
    TEST_SIZE,
)
from src.preprocessing import IQRCapper, build_pipeline

PHASE8_OUT = OUTPUTS_DIR / "phase8"
CAL_DIR = PHASE8_OUT / "calibration"
COMP_DIR = PHASE8_OUT / "model_comparison"
ROB_DIR = PHASE8_OUT / "robustness"
SUMMARY_PATH = PHASE8_OUT / "phase8_summary.json"

MIN_SUBGROUP_N = 50
MIN_CLASS_N = 10

PALETTE = {
    "navy": "#0F2942",
    "blue": "#1D4ED8",
    "teal": "#0D9488",
    "orange": "#EA580C",
    "red": "#DC2626",
    "slate": "#64748B",
    "grid": "#E2E8F0",
    "surface": "#FCFCFB",
}

plt.rcParams.update(
    {
        "figure.facecolor": PALETTE["surface"],
        "axes.facecolor": PALETTE["surface"],
        "savefig.facecolor": PALETTE["surface"],
        "axes.edgecolor": "#CBD5E1",
        "axes.labelcolor": "#334155",
        "text.color": "#0F172A",
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "font.size": 9.5,
        "figure.dpi": 150,
    }
)


def compute_classification_metrics(y_true: np.ndarray, probs: np.ndarray, threshold: float = 0.50) -> dict[str, Any]:
    y_arr = np.asarray(y_true, dtype=int)
    p_arr = np.clip(np.asarray(probs, dtype=float), 1e-15, 1.0 - 1e-15)
    preds = (p_arr >= threshold).astype(int)
    cm = confusion_matrix(y_arr, preds, labels=[0, 1])
    tn, fp, fn, tp = [int(v) for v in cm.ravel()]
    return {
        "threshold": round(float(threshold), 4),
        "accuracy": round(float(accuracy_score(y_arr, preds)), 4),
        "precision": round(float(precision_score(y_arr, preds, zero_division=0)), 4),
        "recall": round(float(recall_score(y_arr, preds, zero_division=0)), 4),
        "f1": round(float(f1_score(y_arr, preds, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_arr, p_arr)), 4),
        "pr_auc": round(float(average_precision_score(y_arr, p_arr)), 4),
        "log_loss": round(float(log_loss(y_arr, p_arr)), 4),
        "brier_score": round(float(brier_score_loss(y_arr, p_arr)), 4),
        "predicted_positive_count": int(preds.sum()),
        "predicted_positive_rate": round(float(preds.mean()), 4),
        "confusion_matrix": {"TN": tn, "FP": fp, "FN": fn, "TP": tp},
    }


def compute_calibration_diagnostics(y_true: np.ndarray, probs: np.ndarray, n_bins: int = 10) -> dict[str, Any]:
    """Compute Brier, Log-loss, ECE (10 equal-width bins), calibration intercept & slope."""
    y_arr = np.asarray(y_true, dtype=int)
    p_arr = np.clip(np.asarray(probs, dtype=float), 1e-6, 1.0 - 1e-6)

    # Expected Calibration Error (equal-width bins on [0, 1])
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.digitize(p_arr, edges[1:-1], right=False)
    ece = 0.0
    band_rows = []
    n_total = len(y_arr)
    for b in range(n_bins):
        mask = bin_ids == b
        cnt = int(mask.sum())
        lo, hi = float(edges[b]), float(edges[b + 1])
        if cnt > 0:
            mean_p = float(p_arr[mask].mean())
            obs_y = float(y_arr[mask].mean())
            gap = abs(obs_y - mean_p)
            ece += (cnt / n_total) * gap
            band_rows.append(
                {
                    "band": f"{lo:.1f}-{hi:.1f}",
                    "count": cnt,
                    "mean_predicted": round(mean_p, 4),
                    "observed_rate": round(obs_y, 4),
                    "abs_error": round(gap, 4),
                }
            )
        else:
            band_rows.append(
                {
                    "band": f"{lo:.1f}-{hi:.1f}",
                    "count": 0,
                    "mean_predicted": None,
                    "observed_rate": None,
                    "abs_error": None,
                }
            )

    # Logistic recalibration slope & intercept: logit(y) ~ a + b * logit(p)
    logits = np.log(p_arr / (1.0 - p_arr)).reshape(-1, 1)
    cal_lr = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
    cal_lr.fit(logits, y_arr)
    cal_slope = float(cal_lr.coef_[0][0])
    cal_intercept = float(cal_lr.intercept_[0])

    return {
        "brier_score": round(float(brier_score_loss(y_arr, p_arr)), 4),
        "log_loss": round(float(log_loss(y_arr, p_arr)), 4),
        "ece_10bin_uniform": round(float(ece), 4),
        "calibration_intercept": round(cal_intercept, 4),
        "calibration_slope": round(cal_slope, 4),
        "roc_auc": round(float(roc_auc_score(y_arr, p_arr)), 4),
        "pr_auc": round(float(average_precision_score(y_arr, p_arr)), 4),
        "band_breakdown": band_rows,
    }


def build_tree_preprocessor() -> ColumnTransformer:
    """Leakage-free preprocessing for tree/boosting models (dense one-hot, no scaling needed)."""
    return ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), NUM_COLS),
            (
                "cat",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                CAT_COLS,
            ),
        ],
        remainder="drop",
    )


def select_thresholds_on_validation(
    y_val: np.ndarray,
    val_probs: np.ndarray,
    tp_profit: float = 180.0,
    fp_cost: float = 65.0,
) -> dict[str, dict[str, Any]]:
    """Select decision thresholds strictly on validation probabilities (NEVER touches test set).

    Business-cost-sensitive criterion:
      Expected validation utility = TP * tp_profit - FP * fp_cost
      (Illustrative unit economics: ₹180 net contribution on targeted converter vs ₹65 wasted outreach cost.)
    """
    grid = [round(float(t), 2) for t in np.arange(0.15, 0.86, 0.01)]
    rows = []
    for t in grid:
        m = compute_classification_metrics(y_val, val_probs, threshold=t)
        cm = m["confusion_matrix"]
        net_val = cm["TP"] * tp_profit - cm["FP"] * fp_cost
        m["expected_utility_inr"] = round(float(net_val), 2)
        rows.append(m)

    # 1. Default 0.50
    t_default = next(r for r in rows if abs(r["threshold"] - 0.50) < 1e-6)
    # 2. Validation-selected F1 optimal
    t_f1 = max(rows, key=lambda r: (r["f1"], -abs(r["threshold"] - 0.50)))
    # 3. High-recall (Recall >= 0.90, maximizing precision)
    recall_cands = [r for r in rows if r["recall"] >= 0.90]
    t_high_recall = max(recall_cands, key=lambda r: (r["precision"], r["recall"])) if recall_cands else rows[0]
    # 4. High-precision (Precision >= 0.80, maximizing recall)
    prec_cands = [r for r in rows if r["precision"] >= 0.80 and r["predicted_positive_count"] > 0]
    t_high_prec = max(prec_cands, key=lambda r: (r["recall"], r["precision"])) if prec_cands else rows[-1]
    # 5. Business-cost-sensitive (maximizing validation utility)
    t_cost = max(rows, key=lambda r: r["expected_utility_inr"])

    return {
        "default_0.50": {"selected_threshold": t_default["threshold"], "criterion": "Standard probability cutoff (t = 0.50)", "val_metrics": t_default},
        "val_f1_optimal": {"selected_threshold": t_f1["threshold"], "criterion": "Maximize F1-score on validation set", "val_metrics": t_f1},
        "high_recall_ge90": {"selected_threshold": t_high_recall["threshold"], "criterion": "Validation Recall >= 0.90 with maximum precision", "val_metrics": t_high_recall},
        "high_precision_ge80": {"selected_threshold": t_high_prec["threshold"], "criterion": "Validation Precision >= 0.80 with maximum recall", "val_metrics": t_high_prec},
        "cost_sensitive": {
            "selected_threshold": t_cost["threshold"],
            "criterion": f"Maximize validation utility (TP * INR {tp_profit:.0f} - FP * INR {fp_cost:.0f})",
            "val_metrics": t_cost,
        },
    }


def run_subgroup_analysis(
    df_test: pd.DataFrame,
    y_test: np.ndarray,
    probs_test: np.ndarray,
    threshold: float = 0.50,
    min_n: int = MIN_SUBGROUP_N,
    min_class_n: int = MIN_CLASS_N,
) -> pd.DataFrame:
    """Evaluate held-out test reliability across meaningful segments with minimum-N guardrails."""
    work = df_test.copy().reset_index(drop=True)
    work["__y"] = np.asarray(y_test, dtype=int)
    work["__p"] = np.asarray(probs_test, dtype=float)
    work["__pred"] = (work["__p"] >= threshold).astype(int)
    work["Age_Group"] = pd.cut(
        work["Age"],
        bins=[0, 25, 35, 45, 60, 120],
        labels=["18-25", "26-35", "36-45", "46-60", "60+"],
    ).astype(str)
    work.loc[work["Age"].isna(), "Age_Group"] = "Missing"

    segments = [
        ("Device_Type", "Device Type"),
        ("Membership_Type", "Membership Type"),
        ("Traffic_Source", "Traffic Source"),
        ("Age_Group", "Age Group"),
    ]
    rows = []
    for col, label in segments:
        series = work[col].fillna("Missing").astype(str)
        for val, grp in work.groupby(series, observed=False):
            n = len(grp)
            pos = int(grp["__y"].sum())
            neg = n - pos
            low_sample = n < min_n or pos < min_class_n or neg < min_class_n
            warning = ""
            if n < min_n:
                warning = f"Excluded ranking metrics: n={n} < {min_n}"
            elif pos < min_class_n or neg < min_class_n:
                warning = f"Excluded ranking metrics: min class count < {min_class_n} (pos={pos}, neg={neg})"

            row: dict[str, Any] = {
                "Dimension": label,
                "Subgroup": val,
                "Sample_Count": n,
                "Positive_Count": pos,
                "Positive_Rate": round(float(grp["__y"].mean()), 4),
                "Sufficient_Sample": not low_sample,
                "Warning": warning,
            }
            if not low_sample:
                row["Precision"] = round(float(precision_score(grp["__y"], grp["__pred"], zero_division=0)), 4)
                row["Recall"] = round(float(recall_score(grp["__y"], grp["__pred"], zero_division=0)), 4)
                row["F1"] = round(float(f1_score(grp["__y"], grp["__pred"], zero_division=0)), 4)
                row["ROC_AUC"] = round(float(roc_auc_score(grp["__y"], grp["__p"])), 4)
                row["PR_AUC"] = round(float(average_precision_score(grp["__y"], grp["__p"])), 4)
                row["Brier_Score"] = round(float(brier_score_loss(grp["__y"], grp["__p"])), 4)
            else:
                for k in ("Precision", "Recall", "F1", "ROC_AUC", "PR_AUC", "Brier_Score"):
                    row[k] = None
            rows.append(row)

    # Class-level error breakdown (Purchase = 1 vs Purchase = 0)
    for cls_val, cls_name in [(1, "Purchase (1)"), (0, "No Purchase (0)")]:
        grp = work[work["__y"] == cls_val]
        acc_cls = float((grp["__pred"] == grp["__y"]).mean())
        brier_cls = float(np.mean((grp["__p"] - grp["__y"]) ** 2))
        rows.append(
            {
                "Dimension": "Target Class",
                "Subgroup": cls_name,
                "Sample_Count": len(grp),
                "Positive_Count": int(grp["__y"].sum()),
                "Positive_Rate": float(cls_val),
                "Sufficient_Sample": True,
                "Warning": "Single-class slice: Recall=class accuracy; ROC-AUC/PR-AUC not defined for single class",
                "Precision": None,
                "Recall": round(acc_cls, 4),
                "F1": None,
                "ROC_AUC": None,
                "PR_AUC": None,
                "Brier_Score": round(brier_cls, 4),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    CAL_DIR.mkdir(parents=True, exist_ok=True)
    COMP_DIR.mkdir(parents=True, exist_ok=True)
    ROB_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_RAW_PATH)
    X = df.drop(columns=[ID_COL, TARGET_COL])
    y = df[TARGET_COL]

    # Exact untouched 20% final test split matching Phases 1-7
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    # Leakage-safe inner split of training portion: 6,400 train / 1,600 validation
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.20, stratify=y_train_full, random_state=RANDOM_STATE
    )

    # =========================================================================
    # PHASE 8.1 — LEAKAGE-SAFE THRESHOLD SELECTION
    # =========================================================================
    lr_tr = build_pipeline(cap=True, cap_k=1.5, c_val=1.0).fit(X_tr, y_tr)
    val_probs_lr = lr_tr.predict_proba(X_val)[:, 1]

    # Also compute 5-fold OOF probabilities on X_train_full (8,000) to cross-check stability
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    oof_probs_lr = cross_val_predict(
        build_pipeline(cap=True, cap_k=1.5, c_val=1.0),
        X_train_full,
        y_train_full,
        cv=skf,
        method="predict_proba",
    )[:, 1]
    oof_f1_grid = [
        (round(float(t), 2), round(float(f1_score(y_train_full, (oof_probs_lr >= t).astype(int))), 4))
        for t in np.arange(0.15, 0.86, 0.01)
    ]
    oof_best_t, oof_best_f1 = max(oof_f1_grid, key=lambda x: x[1])

    selected_thresholds = select_thresholds_on_validation(y_val.values, val_probs_lr)

    # Refit final model on full 8,000 training set & evaluate LOCKED thresholds once on untouched X_test
    lr_full = build_pipeline(cap=True, cap_k=1.5, c_val=1.0).fit(X_train_full, y_train_full)
    test_probs_lr = lr_full.predict_proba(X_test)[:, 1]

    threshold_results = {}
    for key, info in selected_thresholds.items():
        t_locked = info["selected_threshold"]
        test_m = compute_classification_metrics(y_test.values, test_probs_lr, threshold=t_locked)
        threshold_results[key] = {
            "selected_threshold": t_locked,
            "criterion": info["criterion"],
            "validation_metrics": info["val_metrics"],
            "untouched_test_metrics": test_m,
        }

    # =========================================================================
    # PHASE 8.2 — PROBABILITY CALIBRATION (FIT STRICTLY ON X_tr, SELECT ON X_val)
    # =========================================================================
    cal_models = {
        "uncalibrated_lr": lr_tr,
        "sigmoid_calibrated": CalibratedClassifierCV(
            estimator=build_pipeline(cap=True, cap_k=1.5, c_val=1.0),
            method="sigmoid",
            cv=5,
        ).fit(X_tr, y_tr),
        "isotonic_calibrated": CalibratedClassifierCV(
            estimator=build_pipeline(cap=True, cap_k=1.5, c_val=1.0),
            method="isotonic",
            cv=5,
        ).fit(X_tr, y_tr),
    }

    cal_val_summary = {}
    cal_val_probs = {}
    for name, mdl in cal_models.items():
        vp = mdl.predict_proba(X_val)[:, 1]
        cal_val_probs[name] = vp
        cal_val_summary[name] = compute_calibration_diagnostics(y_val.values, vp, n_bins=10)

    # Select calibration method strictly on validation Brier + Log-loss + ECE
    selected_cal_name = min(
        cal_val_summary.keys(),
        key=lambda k: (cal_val_summary[k]["brier_score"], cal_val_summary[k]["log_loss"], cal_val_summary[k]["ece_10bin_uniform"]),
    )

    # Refit all 3 calibration variants on full 8,000 training set for final untouched test evaluation
    cal_models_full = {
        "uncalibrated_lr": lr_full,
        "sigmoid_calibrated": CalibratedClassifierCV(
            estimator=build_pipeline(cap=True, cap_k=1.5, c_val=1.0),
            method="sigmoid",
            cv=5,
        ).fit(X_train_full, y_train_full),
        "isotonic_calibrated": CalibratedClassifierCV(
            estimator=build_pipeline(cap=True, cap_k=1.5, c_val=1.0),
            method="isotonic",
            cv=5,
        ).fit(X_train_full, y_train_full),
    }
    cal_test_summary = {}
    cal_test_probs = {}
    for name, mdl in cal_models_full.items():
        tp = mdl.predict_proba(X_test)[:, 1]
        cal_test_probs[name] = tp
        cal_test_summary[name] = compute_calibration_diagnostics(y_test.values, tp, n_bins=10)

    # Calibration Figures (4 PNGs)
    # 1. Reliability diagram
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    ax.plot([0, 1], [0, 1], "--", color=PALETTE["slate"], lw=1.3, label="Perfect Calibration")
    for name, color, lbl in [
        ("uncalibrated_lr", PALETTE["blue"], f"Uncalibrated LR (Brier={cal_test_summary['uncalibrated_lr']['brier_score']:.4f})"),
        ("sigmoid_calibrated", PALETTE["teal"], f"Sigmoid Calibrated (Brier={cal_test_summary['sigmoid_calibrated']['brier_score']:.4f})"),
        ("isotonic_calibrated", PALETTE["orange"], f"Isotonic Calibrated (Brier={cal_test_summary['isotonic_calibrated']['brier_score']:.4f})"),
    ]:
        pt, pp = calibration_curve(y_test, cal_test_probs[name], n_bins=10, strategy="uniform")
        ax.plot(pp, pt, "o-", lw=2, color=color, label=lbl)
    ax.set_title("Reliability Diagram — Untouched Held-Out Test Set (n = 2,000)")
    ax.set_xlabel("Mean Predicted Probability (10 Uniform Bins)")
    ax.set_ylabel("Observed Purchase Rate")
    ax.legend(loc="upper left")
    ax.grid(color=PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(CAL_DIR / "01_reliability_diagram.png")
    plt.close()

    # 2. Calibration metric comparison bar plot
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))
    methods = ["uncalibrated_lr", "sigmoid_calibrated", "isotonic_calibrated"]
    short_labels = ["Uncalibrated LR", "Sigmoid", "Isotonic"]
    for ax, metric_key, title in zip(
        axes,
        ["brier_score", "log_loss", "ece_10bin_uniform"],
        ["Brier Score (Lower Better)", "Log-Loss (Lower Better)", "ECE 10-Bin (Lower Better)"],
    ):
        vals = [cal_test_summary[m][metric_key] for m in methods]
        bars = ax.bar(short_labels, vals, color=[PALETTE["blue"], PALETTE["teal"], PALETTE["orange"]], width=0.55)
        ax.set_title(title)
        ax.grid(axis="y", color=PALETTE["grid"])
        ax.set_axisbelow(True)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.02, f"{v:.4f}", ha="center", fontweight="bold", fontsize=8.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(CAL_DIR / "02_calibration_comparison.png")
    plt.close()

    # 3. Predicted probability distribution
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    for name, color, lbl in [
        ("uncalibrated_lr", PALETTE["blue"], "Uncalibrated LR"),
        ("sigmoid_calibrated", PALETTE["teal"], "Sigmoid"),
        ("isotonic_calibrated", PALETTE["orange"], "Isotonic"),
    ]:
        ax.hist(cal_test_probs[name], bins=25, alpha=0.45, color=color, label=lbl, edgecolor="white")
    ax.axvline(0.50, linestyle="--", color=PALETTE["navy"], lw=1.2, label="Threshold = 0.50")
    ax.set_title("Predicted Purchase Probability Distributions (Test Set, n = 2,000)")
    ax.set_xlabel("Predicted Purchase Probability")
    ax.set_ylabel("Customer Count")
    ax.legend()
    ax.grid(axis="y", color=PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(CAL_DIR / "03_probability_distribution.png")
    plt.close()

    # 4. Calibration error by probability band (selected method vs uncalibrated)
    bands = [b for b in cal_test_summary["uncalibrated_lr"]["band_breakdown"] if b["count"] > 0]
    fig, ax = plt.subplots(figsize=(9.0, 4.4))
    x_pos = np.arange(len(bands))
    w = 0.35
    uncal_err = [b["abs_error"] for b in bands]
    sig_map = {b["band"]: (b["abs_error"] or 0.0) for b in cal_test_summary["sigmoid_calibrated"]["band_breakdown"]}
    sig_err = [sig_map[b["band"]] for b in bands]
    ax.bar(x_pos - w / 2, uncal_err, width=w, color=PALETTE["blue"], label="Uncalibrated LR")
    ax.bar(x_pos + w / 2, sig_err, width=w, color=PALETTE["teal"], label="Sigmoid Calibrated")
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"{b['band']}\n(n={b['count']})" for b in bands], fontsize=8)
    ax.set_title("Absolute Calibration Error |Observed - Predicted| by Probability Band (Test Set)")
    ax.set_ylabel("Absolute Calibration Error")
    ax.legend()
    ax.grid(axis="y", color=PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(CAL_DIR / "04_calibration_error_by_band.png")
    plt.close()

    # =========================================================================
    # PHASE 8.3 — COMPARATIVE ML EXPERIMENTATION (4 MODELS, IDENTICAL SPLITS)
    # =========================================================================
    candidates: dict[str, list[tuple[str, Any]]] = {
        "DummyClassifier": [
            ("strategy=prior", Pipeline([("prep", build_tree_preprocessor()), ("model", DummyClassifier(strategy="prior", random_state=RANDOM_STATE))])),
        ],
        "LogisticRegression": [
            (f"C={c}", build_pipeline(cap=True, cap_k=1.5, c_val=c)) for c in (0.1, 1.0, 5.0)
        ],
        "RandomForest": [
            (
                f"depth={d},leaf={leaf}",
                Pipeline(
                    [
                        ("prep", build_tree_preprocessor()),
                        ("model", RandomForestClassifier(n_estimators=200, max_depth=d, min_samples_leaf=leaf, random_state=RANDOM_STATE, n_jobs=1)),
                    ]
                ),
            )
            for d in (6, 10)
            for leaf in (5, 15)
        ],
        "HistGradientBoosting": [
            (
                f"depth={d},lr={lr_v}",
                Pipeline(
                    [
                        ("prep", build_tree_preprocessor()),
                        ("model", HistGradientBoostingClassifier(max_iter=200, max_depth=d, learning_rate=lr_v, l2_regularization=1.0, random_state=RANDOM_STATE)),
                    ]
                ),
            )
            for d in (3, 5)
            for lr_v in (0.05, 0.1)
        ],
    }

    complexity_notes = {
        "DummyClassifier": ("Trivial (1 prior constant)", "High (Baseline only)"),
        "LogisticRegression": ("Low (26 linear weights + intercept)", "High (Exact standardized odds ratios)"),
        "RandomForest": ("High (200 decision trees)", "Medium-Low (Feature importance only)"),
        "HistGradientBoosting": ("Medium-High (Boosted tree ensemble)", "Low (Requires post-hoc SHAP/PDP)"),
    }

    comp_rows = []
    comp_test_probs = {}
    comp_val_details = {}

    for m_name, grid_items in candidates.items():
        best_val_auc = -1.0
        best_cfg = None
        best_pipe_proto = None
        best_val_m = None
        for cfg_label, pipe_proto in grid_items:
            fitted_tr = clone(pipe_proto).fit(X_tr, y_tr)
            vp = fitted_tr.predict_proba(X_val)[:, 1]
            vm = compute_classification_metrics(y_val.values, vp, threshold=0.50)
            score = vm["roc_auc"] if m_name != "DummyClassifier" else -vm["brier_score"]
            if score > best_val_auc:
                best_val_auc = score
                best_cfg = cfg_label
                best_pipe_proto = pipe_proto
                best_val_m = vm

        # Refit best config on full X_train_full (8,000) and evaluate once on untouched X_test (2,000)
        fitted_full = clone(best_pipe_proto).fit(X_train_full, y_train_full)
        t0 = time.perf_counter()
        tp = fitted_full.predict_proba(X_test)[:, 1]
        inf_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        tm = compute_classification_metrics(y_test.values, tp, threshold=0.50)
        cal_m = compute_calibration_diagnostics(y_test.values, tp, n_bins=10)
        comp_test_probs[m_name] = tp
        comp_val_details[m_name] = {"best_config": best_cfg, "val_metrics": best_val_m, "test_metrics": tm, "test_calibration": cal_m}

        comp_rows.append(
            {
                "Model": m_name,
                "Selected_Config_Val": best_cfg,
                "Val_ROC_AUC": best_val_m["roc_auc"],
                "Test_ROC_AUC": tm["roc_auc"],
                "Test_PR_AUC": tm["pr_auc"],
                "Test_Precision": tm["precision"],
                "Test_Recall": tm["recall"],
                "Test_F1": tm["f1"],
                "Test_Accuracy": tm["accuracy"],
                "Test_Log_Loss": tm["log_loss"],
                "Test_Brier": tm["brier_score"],
                "Test_ECE_10Bin": cal_m["ece_10bin_uniform"],
                "Inference_Time_ms_2k": inf_ms,
                "Complexity": complexity_notes[m_name][0],
                "Interpretability": complexity_notes[m_name][1],
            }
        )

    comp_df = pd.DataFrame(comp_rows)
    comp_df.to_csv(COMP_DIR / "model_comparison.csv", index=False)

    # Model Comparison Figures (4 PNGs)
    # 1. Model comparison bar chart
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(comp_df))
    w = 0.25
    ax.bar(x - w, comp_df["Test_ROC_AUC"], width=w, color=PALETTE["blue"], label="ROC-AUC")
    ax.bar(x, comp_df["Test_PR_AUC"], width=w, color=PALETTE["teal"], label="PR-AUC")
    ax.bar(x + w, comp_df["Test_F1"], width=w, color=PALETTE["navy"], label="F1-Score")
    ax.set_xticks(x)
    ax.set_xticklabels(comp_df["Model"])
    ax.set_ylim(0, 1.05)
    ax.set_title("Model Comparison — Held-Out Test Performance (n = 2,000, t = 0.50)")
    ax.set_ylabel("Score")
    ax.legend()
    ax.grid(axis="y", color=PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(COMP_DIR / "01_model_comparison_bar.png")
    plt.close()

    # 2. ROC curve comparison
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    ax.plot([0, 1], [0, 1], "--", color=PALETTE["slate"], lw=1.2, label="Random (AUC = 0.5000)")
    for m_name, color in [
        ("LogisticRegression", PALETTE["blue"]),
        ("RandomForest", PALETTE["teal"]),
        ("HistGradientBoosting", PALETTE["orange"]),
        ("DummyClassifier", PALETTE["slate"]),
    ]:
        fpr, tpr, _ = roc_curve(y_test, comp_test_probs[m_name])
        auc_v = roc_auc_score(y_test, comp_test_probs[m_name])
        ax.plot(fpr, tpr, lw=2, color=color, label=f"{m_name} (AUC = {auc_v:.4f})")
    ax.set_title("ROC Curve Comparison — Untouched Held-Out Test Set (n = 2,000)")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")
    ax.grid(color=PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(COMP_DIR / "02_roc_curve_comparison.png")
    plt.close()

    # 3. PR curve comparison
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    ax.axhline(y_test.mean(), linestyle="--", color=PALETTE["slate"], lw=1.2, label=f"Base Rate ({y_test.mean():.3f})")
    for m_name, color in [
        ("LogisticRegression", PALETTE["blue"]),
        ("RandomForest", PALETTE["teal"]),
        ("HistGradientBoosting", PALETTE["orange"]),
        ("DummyClassifier", PALETTE["slate"]),
    ]:
        pr, rc, _ = precision_recall_curve(y_test, comp_test_probs[m_name])
        ap_v = average_precision_score(y_test, comp_test_probs[m_name])
        ax.plot(rc, pr, lw=2, color=color, label=f"{m_name} (AP = {ap_v:.4f})")
    ax.set_title("Precision-Recall Curve Comparison — Held-Out Test Set (n = 2,000)")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend(loc="lower left")
    ax.grid(color=PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(COMP_DIR / "03_pr_curve_comparison.png")
    plt.close()

    # 4. Metric comparison heatmap
    heat_cols = ["Test_ROC_AUC", "Test_PR_AUC", "Test_Accuracy", "Test_Precision", "Test_Recall", "Test_F1", "Test_Brier", "Test_Log_Loss"]
    heat_mat = comp_df.set_index("Model")[heat_cols].values.astype(float)
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    im = ax.imshow(heat_mat, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(heat_cols)))
    ax.set_xticklabels([c.replace("Test_", "") for c in heat_cols], rotation=25, ha="right")
    ax.set_yticks(range(len(comp_df)))
    ax.set_yticklabels(comp_df["Model"])
    ax.set_title("Model Evaluation Metric Heatmap (Held-Out Test Set, n = 2,000)")
    for i in range(heat_mat.shape[0]):
        for j in range(heat_mat.shape[1]):
            v = heat_mat[i, j]
            ax.text(j, i, f"{v:.4f}", ha="center", va="center", color="white" if v > 0.65 else "#0F172A", fontweight="bold", fontsize=8.5)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    plt.tight_layout()
    plt.savefig(COMP_DIR / "04_metric_comparison_heatmap.png")
    plt.close()

    # =========================================================================
    # PHASE 8.5 — SUBGROUP & ROBUSTNESS ANALYSIS (UNTOUCHED TEST SET)
    # =========================================================================
    sub_df = run_subgroup_analysis(X_test, y_test.values, test_probs_lr, threshold=0.50)
    sub_df.to_csv(ROB_DIR / "subgroup_metrics.csv", index=False)

    plot_sub = sub_df[(sub_df["Sufficient_Sample"]) & (sub_df["Dimension"] != "Target Class")].copy()
    plot_sub["Label"] = plot_sub["Dimension"] + ": " + plot_sub["Subgroup"] + " (n=" + plot_sub["Sample_Count"].astype(str) + ")"

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.0))
    ps_sorted = plot_sub.sort_values("ROC_AUC")
    axes[0].barh(ps_sorted["Label"], ps_sorted["ROC_AUC"], color=PALETTE["blue"])
    axes[0].axvline(0.7411, linestyle="--", color=PALETTE["red"], lw=1.2, label="Overall Test ROC-AUC (0.7411)")
    axes[0].set_title("Subgroup ROC-AUC (n >= 50 & min class >= 10)")
    axes[0].set_xlabel("ROC-AUC")
    axes[0].set_xlim(0.5, 0.90)
    axes[0].legend(loc="lower right")
    axes[0].grid(axis="x", color=PALETTE["grid"])

    axes[1].barh(ps_sorted["Label"], ps_sorted["Brier_Score"], color=PALETTE["teal"])
    axes[1].axvline(0.1903, linestyle="--", color=PALETTE["red"], lw=1.2, label="Overall Test Brier (0.1903)")
    axes[1].set_title("Subgroup Brier Score (Lower Better)")
    axes[1].set_xlabel("Brier Score")
    axes[1].legend(loc="lower right")
    axes[1].grid(axis="x", color=PALETTE["grid"])
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(ROB_DIR / "01_subgroup_roc_brier.png")
    plt.close()

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    y_idx = np.arange(len(ps_sorted))
    h = 0.36
    ax.barh(y_idx - h / 2, ps_sorted["Precision"], height=h, color=PALETTE["navy"], label="Precision")
    ax.barh(y_idx + h / 2, ps_sorted["Recall"], height=h, color=PALETTE["orange"], label="Recall")
    ax.set_yticks(y_idx)
    ax.set_yticklabels(ps_sorted["Label"], fontsize=8.5)
    ax.set_xlim(0, 1.05)
    ax.set_title("Subgroup Precision & Recall Comparison (Held-Out Test Set, t = 0.50)")
    ax.set_xlabel("Score")
    ax.legend(loc="lower right")
    ax.grid(axis="x", color=PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(ROB_DIR / "02_subgroup_precision_recall.png")
    plt.close()

    # Master Phase 8 Summary JSON
    summary = {
        "split_design": {
            "total_rows": int(len(df)),
            "train_inner_rows": int(len(X_tr)),
            "validation_rows": int(len(X_val)),
            "train_full_rows": int(len(X_train_full)),
            "untouched_test_rows": int(len(X_test)),
            "random_state": RANDOM_STATE,
        },
        "phase8_1_threshold_selection": {
            "oof_5fold_best_f1_threshold": oof_best_t,
            "oof_5fold_best_f1": oof_best_f1,
            "strategies": threshold_results,
        },
        "phase8_2_calibration": {
            "selected_on_validation": selected_cal_name,
            "validation_comparison": {
                k: {mk: mv for mk, mv in v.items() if mk != "band_breakdown"}
                for k, v in cal_val_summary.items()
            },
            "untouched_test_comparison": cal_test_summary,
        },
        "phase8_3_model_comparison": comp_rows,
        "phase8_5_subgroup_robustness": {
            "min_subgroup_n": MIN_SUBGROUP_N,
            "min_class_n": MIN_CLASS_N,
            "total_subgroups_evaluated": int(len(sub_df)),
            "flagged_small_subgroups": sub_df[~sub_df["Sufficient_Sample"]][["Dimension", "Subgroup", "Sample_Count", "Warning"]].to_dict(orient="records"),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "SUCCESS", "summary_path": str(SUMMARY_PATH), "selected_cal": selected_cal_name, "models": [r["Model"] for r in comp_rows]}, indent=2))


if __name__ == "__main__":
    main()
