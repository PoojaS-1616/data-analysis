"""Page 3: Model Performance — Verified Metrics, Curves, Calibration & Thresholds."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components import BLUE, NAVY, TEAL, render_header, render_kpi_card
from app.utils import FIGURES_DIR, load_metrics


def render() -> None:
    render_header(
        "Model Performance",
        "Verified Evaluation Metrics, Cross-Validation Stability, Calibration & Threshold Trade-Offs",
    )

    metrics = load_metrics()
    pm = metrics["primary_model"]
    tm = pm["test_metrics_t50"]
    tr = pm["train_metrics_t50"]
    cv = pm["cv_5fold"]
    cm = pm["confusion_matrix_t50"]

    st.subheader("Verified Held-Out Test Metrics (n = 2,000, Threshold = 0.50)")
    r1 = st.columns(4)
    with r1[0]:
        render_kpi_card("Accuracy", f"{tm['accuracy']:.4f}", f"Train: {tr['accuracy']:.4f} · CV: {cv['accuracy_mean']:.4f}")
    with r1[1]:
        render_kpi_card("Precision (Purchase=1)", f"{tm['precision']:.4f}", f"Train: {tr['precision']:.4f}")
    with r1[2]:
        render_kpi_card("Recall (Purchase=1)", f"{tm['recall']:.4f}", f"Train: {tr['recall']:.4f}")
    with r1[3]:
        render_kpi_card("F1-Score (Purchase=1)", f"{tm['f1']:.4f}", f"CV: {cv['f1_mean']:.4f}")

    r2 = st.columns(4)
    with r2[0]:
        render_kpi_card("ROC-AUC", f"{tm['roc_auc']:.4f}", f"5-Fold CV: {cv['roc_auc_mean']:.4f} ± {cv['roc_auc_std']:.4f}")
    with r2[1]:
        render_kpi_card("PR-AUC (Avg Precision)", f"{tm['pr_auc']:.4f}", f"CV: {cv['pr_auc_mean']:.4f}")
    with r2[2]:
        render_kpi_card("Log-Loss", f"{tm['log_loss']:.4f}", f"CV: {cv['log_loss_mean']:.4f}")
    with r2[3]:
        render_kpi_card("Brier Score", f"{tm['brier_score']:.4f}", "Base-rate Brier: 0.2281")

    st.subheader("ROC, Precision-Recall, Confusion Matrix & Calibration")
    c1, c2 = st.columns(2)
    roc_img = FIGURES_DIR / "02_roc_and_pr_curves.png"
    cal_img = FIGURES_DIR / "03_confusion_matrix_and_calibration.png"
    if roc_img.exists():
        c1.image(str(roc_img), caption="Saved Test-Set ROC & Precision-Recall Curves", width="stretch")
    if cal_img.exists():
        c2.image(str(cal_img), caption=f"Confusion Matrix (TN={cm['TN']}, FP={cm['FP']}, FN={cm['FN']}, TP={cm['TP']}) & Calibration", width="stretch")

    st.subheader("Decision Threshold Trade-Off Analysis")
    tdf = pd.DataFrame(metrics["threshold_tradeoff"])
    fig_t = px.line(
        tdf,
        x="threshold",
        y=["precision", "recall", "f1", "accuracy"],
        markers=True,
        title="Precision, Recall, F1 & Accuracy Across Decision Thresholds (Test Set)",
        labels={"value": "Score", "threshold": "Decision Threshold", "variable": "Metric"},
        color_discrete_sequence=[BLUE, TEAL, "#EA580C", NAVY],
    )
    fig_t.update_layout(height=340, plot_bgcolor="white")
    st.plotly_chart(fig_t, width="stretch")
    st.dataframe(tdf, width="stretch")

    st.subheader("Empirical IQR Outlier Treatment & Leakage Ablation Comparison")
    ab_rows = []
    for k, v in metrics["iqr_ablation"].items():
        ab_rows.append(
            {
                "Experiment": f"IQR: {k}",
                "CV ROC-AUC": f"{v['cv_roc_auc_mean']:.4f} ± {v['cv_roc_auc_std']:.4f}",
                "Test ROC-AUC": v["test_metrics"]["roc_auc"],
                "Test PR-AUC": v["test_metrics"]["pr_auc"],
                "Test Log-Loss": v["test_metrics"]["log_loss"],
                "Test Accuracy": v["test_metrics"]["accuracy"],
            }
        )
    for k, v in metrics["feature_leakage_audit"].items():
        ab_rows.append(
            {
                "Experiment": f"Stage: {k}",
                "CV ROC-AUC": f"{v['cv_roc_auc_mean']:.4f} ± {v['cv_roc_auc_std']:.4f}",
                "Test ROC-AUC": v["test_metrics"]["roc_auc"],
                "Test PR-AUC": v["test_metrics"]["pr_auc"],
                "Test Log-Loss": v["test_metrics"]["log_loss"],
                "Test Accuracy": v["test_metrics"]["accuracy"],
            }
        )
    st.dataframe(pd.DataFrame(ab_rows), width="stretch")
