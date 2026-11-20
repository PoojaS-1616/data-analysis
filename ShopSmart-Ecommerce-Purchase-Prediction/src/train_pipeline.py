"""
End-to-End Training, Validation, IQR Ablation & Leakage Audit Pipeline
======================================================================
Builds, evaluates, and persists the Logistic Regression purchase prediction pipeline,
validates IQR outlier treatment empirically, investigates feature leakage &
prediction-time availability, and exports metrics, predictions, and 5 publication figures.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
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
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

# Ensure project root is importable when run directly as a script
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import (
    CAP_COLS,
    CAT_COLS,
    CV_FOLDS,
    DATA_RAW_PATH,
    FIGURES_DIR,
    ID_COL,
    METRICS_PATH,
    MODEL_DIR,
    MODEL_PATH,
    NUM_COLS,
    OUTPUTS_DIR,
    PLAIN_NUM_COLS,
    PRE_CART_NUM_COLS,
    PRE_CHECKOUT_CAT_COLS,
    PREDICTIONS_PATH,
    RANDOM_STATE,
    TARGET_COL,
    TEST_SIZE,
)
from src.preprocessing import assign_marketing_segment, build_pipeline

PALETTE = {
    "surface": "#fcfcfb",
    "ink": "#0f172a",
    "ink2": "#475569",
    "grid": "#e2e8f0",
    "blue": "#1d4ed8",
    "teal": "#0d9488",
    "orange": "#ea580c",
    "red": "#dc2626",
    "slate": "#64748b",
}

plt.rcParams.update(
    {
        "figure.facecolor": PALETTE["surface"],
        "axes.facecolor": PALETTE["surface"],
        "savefig.facecolor": PALETTE["surface"],
        "axes.edgecolor": "#cbd5e1",
        "axes.labelcolor": PALETTE["ink2"],
        "text.color": PALETTE["ink"],
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "font.size": 9.5,
        "figure.dpi": 150,
    }
)


def compute_metrics(y_true: np.ndarray, proba: np.ndarray, threshold: float = 0.50) -> dict[str, float]:
    pred = (proba >= threshold).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y_true, pred)), 4),
        "precision": round(float(precision_score(y_true, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, proba)), 4),
        "pr_auc": round(float(average_precision_score(y_true, proba)), 4),
        "log_loss": round(float(log_loss(y_true, proba)), 4),
        "brier_score": round(float(brier_score_loss(y_true, proba)), 4),
    }


def run_cv_and_test(
    pipe_factory,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    cv = cross_validate(
        pipe_factory(),
        X_train,
        y_train,
        cv=skf,
        scoring={
            "accuracy": "accuracy",
            "f1": "f1",
            "roc_auc": "roc_auc",
            "pr_auc": "average_precision",
            "neg_log_loss": "neg_log_loss",
        },
    )
    fitted = pipe_factory().fit(X_train, y_train)
    proba_test = fitted.predict_proba(X_test)[:, 1]
    return {
        "cv_roc_auc_mean": round(float(cv["test_roc_auc"].mean()), 4),
        "cv_roc_auc_std": round(float(cv["test_roc_auc"].std()), 4),
        "cv_pr_auc_mean": round(float(cv["test_pr_auc"].mean()), 4),
        "cv_accuracy_mean": round(float(cv["test_accuracy"].mean()), 4),
        "cv_f1_mean": round(float(cv["test_f1"].mean()), 4),
        "cv_log_loss_mean": round(float(-cv["test_neg_log_loss"].mean()), 4),
        "test_metrics": compute_metrics(y_test.values, proba_test, threshold=0.50),
        "fitted_pipeline": fitted,
        "proba_test": proba_test,
    }


def export_figures(
    df: pd.DataFrame,
    y_test: pd.Series,
    proba_test: np.ndarray,
    threshold_rows: list[dict],
    odds_df: pd.DataFrame,
) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Figure 1: Target distribution & missingness
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    vc = df[TARGET_COL].value_counts().sort_index()
    bars = axes[0].bar(["No Purchase (0)", "Purchase (1)"], vc.values, color=[PALETTE["orange"], PALETTE["blue"]], width=0.55)
    axes[0].set_title("Target Distribution (n = 10,000)")
    axes[0].set_ylabel("Customers")
    axes[0].grid(axis="y", color=PALETTE["grid"])
    axes[0].set_axisbelow(True)
    for b, v in zip(bars, vc.values):
        axes[0].text(b.get_x() + b.get_width() / 2, v + 120, f"{v:,}\n({v/len(df)*100:.1f}%)", ha="center", fontweight="bold")

    miss = df.isna().sum()
    miss = miss[miss > 0].sort_values(ascending=True)
    axes[1].barh(miss.index, miss.values, color=PALETTE["teal"])
    axes[1].set_title(f"Missing Values Across {len(miss)} Columns (Total = {int(miss.sum()):,})")
    axes[1].set_xlabel("Missing Rows")
    axes[1].grid(axis="x", color=PALETTE["grid"])
    axes[1].set_axisbelow(True)
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_target_and_missingness.png")
    plt.close()

    # Figure 2: ROC & Precision-Recall curves
    fpr, tpr, _ = roc_curve(y_test, proba_test)
    prec, rec, _ = precision_recall_curve(y_test, proba_test)
    roc_auc = roc_auc_score(y_test, proba_test)
    pr_auc = average_precision_score(y_test, proba_test)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(fpr, tpr, color=PALETTE["blue"], lw=2.2, label=f"Logistic Regression (AUC = {roc_auc:.4f})")
    axes[0].plot([0, 1], [0, 1], "--", color=PALETTE["slate"], lw=1.2, label="Random Baseline (AUC = 0.50)")
    axes[0].set_title("ROC Curve (Held-Out Test Set, n = 2,000)")
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].legend(loc="lower right")
    axes[0].grid(color=PALETTE["grid"])

    axes[1].plot(rec, prec, color=PALETTE["teal"], lw=2.2, label=f"Logistic Regression (AP = {pr_auc:.4f})")
    axes[1].axhline(y_test.mean(), linestyle="--", color=PALETTE["slate"], lw=1.2, label=f"Base Rate ({y_test.mean():.3f})")
    axes[1].set_title("Precision-Recall Curve (Held-Out Test Set)")
    axes[1].set_xlabel("Recall")
    axes[1].set_ylabel("Precision")
    axes[1].legend(loc="lower left")
    axes[1].grid(color=PALETTE["grid"])
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "02_roc_and_pr_curves.png")
    plt.close()

    # Figure 3: Confusion Matrix & Calibration Curve
    cm = confusion_matrix(y_test, (proba_test >= 0.50).astype(int))
    prob_true, prob_pred = calibration_curve(y_test, proba_test, n_bins=10, strategy="quantile")
    brier = brier_score_loss(y_test, proba_test)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    im = axes[0].imshow(cm, cmap="Blues")
    axes[0].set_xticks([0, 1])
    axes[0].set_yticks([0, 1])
    axes[0].set_xticklabels(["Pred 0", "Pred 1"])
    axes[0].set_yticklabels(["Actual 0", "Actual 1"])
    axes[0].set_title("Confusion Matrix (Threshold = 0.50)")
    for i in range(2):
        for j in range(2):
            axes[0].text(j, i, f"{cm[i, j]:,}", ha="center", va="center", color="white" if cm[i, j] > cm.max() / 2 else PALETTE["ink"], fontsize=12, fontweight="bold")
    fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)

    axes[1].plot(prob_pred, prob_true, "o-", color=PALETTE["blue"], lw=2, label=f"Logistic Regression (Brier = {brier:.4f})")
    axes[1].plot([0, 1], [0, 1], "--", color=PALETTE["slate"], lw=1.2, label="Perfect Calibration")
    axes[1].set_title("Probability Calibration Curve (10 Quantile Bins)")
    axes[1].set_xlabel("Mean Predicted Probability")
    axes[1].set_ylabel("Observed Purchase Rate")
    axes[1].legend(loc="upper left")
    axes[1].grid(color=PALETTE["grid"])
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "03_confusion_matrix_and_calibration.png")
    plt.close()

    # Figure 4: Threshold Trade-off & Decile Lift
    tdf = pd.DataFrame(threshold_rows)
    lift_df = pd.DataFrame({"proba": proba_test, "actual": y_test.values}).sort_values("proba", ascending=False).reset_index(drop=True)
    lift_df["decile"] = pd.qcut(lift_df.index, 10, labels=range(1, 11))
    dec = lift_df.groupby("decile", observed=False)["actual"].mean() / y_test.mean()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(tdf["threshold"], tdf["precision"], "o-", color=PALETTE["blue"], label="Precision")
    axes[0].plot(tdf["threshold"], tdf["recall"], "s-", color=PALETTE["teal"], label="Recall")
    axes[0].plot(tdf["threshold"], tdf["f1"], "^-", color=PALETTE["orange"], label="F1-Score")
    axes[0].axvline(0.50, linestyle="--", color=PALETTE["slate"], lw=1.1, label="Default (0.50)")
    axes[0].set_title("Precision / Recall / F1 by Decision Threshold")
    axes[0].set_xlabel("Decision Threshold")
    axes[0].set_ylabel("Score")
    axes[0].legend()
    axes[0].grid(color=PALETTE["grid"])

    axes[1].bar(dec.index.astype(str), dec.values, color=PALETTE["blue"])
    axes[1].axhline(1.0, linestyle="--", color=PALETTE["red"], lw=1.2, label="Random Baseline (1.0x)")
    axes[1].set_title("Purchase Lift by Predicted Probability Decile (1 = Highest)")
    axes[1].set_xlabel("Predicted Probability Decile")
    axes[1].set_ylabel("Lift vs. Base Rate")
    axes[1].legend()
    axes[1].grid(axis="y", color=PALETTE["grid"])
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "04_threshold_tradeoff_and_lift.png")
    plt.close()

    # Figure 5: Top Standardized Coefficients / Odds Ratios
    top_n = pd.concat([odds_df.head(8), odds_df.tail(5)]).drop_duplicates(subset=["feature"]).sort_values("coefficient")
    colors = [PALETTE["blue"] if c > 0 else PALETTE["red"] for c in top_n["coefficient"]]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.barh(top_n["feature"], top_n["coefficient"], color=colors)
    ax.axvline(0, color=PALETTE["ink"], lw=1)
    ax.set_title("Logistic Regression Standardized Log-Odds Coefficients (Top Positive & Negative Drivers)")
    ax.set_xlabel("Log-Odds Coefficient (Standardized Numeric / One-Hot Reference)")
    ax.grid(axis="x", color=PALETTE["grid"])
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "05_odds_ratios_feature_importance.png")
    plt.close()


def main() -> None:
    if not DATA_RAW_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {DATA_RAW_PATH}. "
            "Place Ecommerce_Purchase_Prediction_DataSet.csv into data/raw/ before running."
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_RAW_PATH)
    X = df.drop(columns=[ID_COL, TARGET_COL])
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    print("=" * 80)
    print("E-COMMERCE PURCHASE PREDICTION — MODULAR TRAINING & VALIDATION PIPELINE")
    print("=" * 80)
    print(f"Dataset: {df.shape[0]:,} rows x {df.shape[1]} cols | Train: {len(X_train):,} | Test: {len(X_test):,}")

    # 1. IQR Outlier Treatment Validation (Empirical Ablation)
    iqr_ablation = {}
    for label, kwargs in [
        ("iqr_capped_k1.5", {"cap": True, "cap_k": 1.5}),
        ("uncapped_raw", {"cap": False}),
        ("iqr_capped_k3.0", {"cap": True, "cap_k": 3.0}),
    ]:
        res = run_cv_and_test(lambda kw=kwargs: build_pipeline(**kw), X_train, y_train, X_test, y_test)
        iqr_ablation[label] = {k: v for k, v in res.items() if k not in ("fitted_pipeline", "proba_test")}
        if label == "iqr_capped_k1.5":
            primary_res = res

    print("\n[1] IQR Outlier Treatment Validation (5-Fold CV & Held-Out Test):")
    for lbl, r in iqr_ablation.items():
        tm = r["test_metrics"]
        print(
            f"  {lbl:16s} | CV ROC-AUC={r['cv_roc_auc_mean']:.4f} +/- {r['cv_roc_auc_std']:.4f} | "
            f"Test ROC-AUC={tm['roc_auc']:.4f} | PR-AUC={tm['pr_auc']:.4f} | LogLoss={tm['log_loss']:.4f} | Acc={tm['accuracy']:.4f}"
        )

    # 2. Feature Leakage & Prediction-Time Availability Audit
    leakage_audit = {}
    pre_cart_cap = [c for c in CAP_COLS if c in PRE_CART_NUM_COLS]
    pre_cart_plain = [c for c in PLAIN_NUM_COLS if c in PRE_CART_NUM_COLS]
    for label, kwargs in [
        ("full_checkout_17_features", {"cap": True}),
        ("pre_payment_16_features", {"cap": True, "cat_cols": PRE_CHECKOUT_CAT_COLS}),
        ("pre_cart_browsing_13_features", {"cap": True, "cap_cols": pre_cart_cap, "plain_num_cols": pre_cart_plain, "cat_cols": PRE_CHECKOUT_CAT_COLS}),
    ]:
        res = run_cv_and_test(lambda kw=kwargs: build_pipeline(**kw), X_train, y_train, X_test, y_test)
        leakage_audit[label] = {k: v for k, v in res.items() if k not in ("fitted_pipeline", "proba_test")}

    print("\n[2] Feature Leakage & Prediction-Time Availability Audit:")
    for lbl, r in leakage_audit.items():
        tm = r["test_metrics"]
        print(
            f"  {lbl:30s} | CV ROC-AUC={r['cv_roc_auc_mean']:.4f} | Test ROC-AUC={tm['roc_auc']:.4f} | "
            f"Test Acc={tm['accuracy']:.4f} | Test F1={tm['f1']:.4f}"
        )

    # 3. Primary Model Persistence, Threshold Trade-off & Odds Ratios
    pipe = primary_res["fitted_pipeline"]
    proba_test = primary_res["proba_test"]
    proba_train = pipe.predict_proba(X_train)[:, 1]
    joblib.dump(pipe, MODEL_PATH)

    threshold_rows = []
    for t in [0.30, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80]:
        pred_t = (proba_test >= t).astype(int)
        threshold_rows.append(
            {
                "threshold": t,
                "predicted_buyers": int(pred_t.sum()),
                "pct_targeted": round(float(pred_t.mean() * 100), 2),
                "accuracy": round(float(accuracy_score(y_test, pred_t)), 4),
                "precision": round(float(precision_score(y_test, pred_t, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, pred_t, zero_division=0)), 4),
                "f1": round(float(f1_score(y_test, pred_t, zero_division=0)), 4),
            }
        )

    feature_names = [n.split("__", 1)[-1] for n in pipe.named_steps["prep"].get_feature_names_out()]
    coefs = pipe.named_steps["model"].coef_[0]
    odds_df = pd.DataFrame(
        {"feature": feature_names, "coefficient": coefs, "odds_ratio": np.exp(coefs)}
    ).sort_values("coefficient", ascending=False)

    cm = confusion_matrix(y_test, (proba_test >= 0.50).astype(int))
    tn, fp, fn, tp = [int(x) for x in cm.ravel()]

    # Export test set predictions
    pred_out = df.loc[X_test.index].copy()
    pred_out = pred_out.rename(columns={TARGET_COL: "Actual_Purchase"})
    pred_out["Purchase_Probability"] = np.round(proba_test, 6)
    pred_out["Predicted_Purchase"] = (proba_test >= 0.50).astype(int)
    pred_out["Marketing_Segment"] = [assign_marketing_segment(float(p)) for p in proba_test]
    pred_out.to_csv(PREDICTIONS_PATH, index=False)

    # Export figures
    export_figures(df, y_test, proba_test, threshold_rows, odds_df)

    # Save complete metrics JSON
    summary = {
        "dataset": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "missing_values": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "purchase_positive_count": int(y.sum()),
            "purchase_positive_rate": round(float(y.mean()), 4),
            "purchase_negative_count": int((1 - y).sum()),
            "purchase_negative_rate": round(float(1 - y.mean()), 4),
        },
        "primary_model": {
            "algorithm": "LogisticRegression (L2, C=1.0, IQR k=1.5)",
            "intercept": round(float(pipe.named_steps["model"].intercept_[0]), 4),
            "feature_count_transformed": len(feature_names),
            "train_metrics_t50": compute_metrics(y_train.values, proba_train, 0.50),
            "test_metrics_t50": primary_res["test_metrics"],
            "cv_5fold": {
                "roc_auc_mean": primary_res["cv_roc_auc_mean"],
                "roc_auc_std": primary_res["cv_roc_auc_std"],
                "pr_auc_mean": primary_res["cv_pr_auc_mean"],
                "accuracy_mean": primary_res["cv_accuracy_mean"],
                "f1_mean": primary_res["cv_f1_mean"],
                "log_loss_mean": primary_res["cv_log_loss_mean"],
            },
            "confusion_matrix_t50": {"TN": tn, "FP": fp, "FN": fn, "TP": tp},
        },
        "iqr_ablation": iqr_ablation,
        "feature_leakage_audit": leakage_audit,
        "threshold_tradeoff": threshold_rows,
        "top_positive_drivers": odds_df.head(6).round(4).to_dict(orient="records"),
        "top_negative_drivers": odds_df.tail(5).round(4).to_dict(orient="records"),
    }
    METRICS_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print("\n[3] Artifacts Saved:")
    print(f"  Model       : {MODEL_PATH}")
    print(f"  Metrics JSON: {METRICS_PATH}")
    print(f"  Predictions : {PREDICTIONS_PATH} ({len(pred_out):,} rows)")
    print(f"  Figures     : {FIGURES_DIR} (5 PNG charts)")
    print("PIPELINE COMPLETED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
