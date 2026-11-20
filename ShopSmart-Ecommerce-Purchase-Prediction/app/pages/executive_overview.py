"""Page 1: Executive Overview — Dataset Statistics vs. Model Performance & Findings."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components import BLUE, NAVY, TEAL, render_header, render_kpi_card
from app.utils import load_metrics, load_test_predictions
from src.preprocessing import assign_marketing_segment


def render() -> None:
    render_header(
        "Executive Overview",
        "ShopSmart — Purchase Intelligence Platform  |  Cart-Stage / Pre-Checkout Intent Analytics",
    )

    metrics = load_metrics()
    ds = metrics["dataset"]
    pm = metrics["primary_model"]
    tm = pm["test_metrics_t50"]
    cv = pm["cv_5fold"]
    preds_df = load_test_predictions()

    st.subheader("1. Observed Dataset Statistics (Historical Ground Truth)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Customers", f"{ds['rows']:,}", f"{ds['columns']} source columns · 0 duplicates")
    with c2:
        render_kpi_card(
            "Actual Purchase Rate",
            f"{ds['purchase_positive_rate'] * 100:.2f}%",
            f"{ds['purchase_positive_count']:,} buyers · {ds['purchase_negative_count']:,} non-buyers",
        )
    with c3:
        render_kpi_card("Held-Out Test ROC-AUC", f"{tm['roc_auc']:.4f}", f"5-Fold CV: {cv['roc_auc_mean']:.4f} ± {cv['roc_auc_std']:.4f}")
    with c4:
        render_kpi_card("Held-Out Test F1-Score", f"{tm['f1']:.4f}", f"Accuracy {tm['accuracy']*100:.2f}% @ t = 0.50")

    st.subheader("2. Model Predictions Distribution (Held-Out Test Set, n = 2,000)")
    col_l, col_r = st.columns(2)

    with col_l:
        if preds_df is not None and "Purchase_Probability" in preds_df.columns:
            fig_hist = px.histogram(
                preds_df,
                x="Purchase_Probability",
                nbins=30,
                color_discrete_sequence=[BLUE],
                title="Predicted Purchase Probability Distribution (Test Set)",
                labels={"Purchase_Probability": "Predicted Purchase Probability"},
            )
            fig_hist.add_vline(x=0.50, line_dash="dash", line_color=NAVY, annotation_text="Default Threshold (0.50)")
            fig_hist.update_layout(height=340, margin=dict(t=45, b=20, l=20, r=20), plot_bgcolor="white")
            st.plotly_chart(fig_hist, width="stretch")
        else:
            st.info("Saved test-set predictions CSV not present locally; run `src/train_pipeline.py` to generate.")

    with col_r:
        if preds_df is not None and "Purchase_Probability" in preds_df.columns:
            seg_series = preds_df["Purchase_Probability"].astype(float).map(assign_marketing_segment)
            seg_counts = (
                seg_series
                .value_counts()
                .reindex(
                    [
                        "High Intent (>=0.75)",
                        "Medium Intent (0.50-0.74)",
                        "Low-Medium Intent (0.30-0.49)",
                        "Low Intent (<0.30)",
                    ]
                )
                .fillna(0)
                .reset_index()
            )
            seg_counts.columns = ["Marketing Segment", "Customers"]
            fig_seg = px.bar(
                seg_counts,
                x="Customers",
                y="Marketing Segment",
                orientation="h",
                text="Customers",
                color_discrete_sequence=[TEAL],
                title="Predicted Customer Intent Segments (Held-Out Test Set)",
            )
            fig_seg.update_layout(height=340, margin=dict(t=45, b=20, l=20, r=20), plot_bgcolor="white")
            st.plotly_chart(fig_seg, width="stretch")

    st.subheader("3. Key Business Findings & Model Limitations")
    f_col, l_col = st.columns(2)
    with f_col:
        st.markdown(
            """
            **Key Verified Findings (Associational — Not Causal)**
            - **Cart depth dominates conversion signal:** `Cart_Items` (`OR = 1.84`) and `Cart_Value_INR` (`OR = 1.50`) are the strongest positive predictors of checkout completion.
            - **Premium membership lifts odds:** `Membership_Type = Premium` carries an odds ratio of `1.72` relative to the reference tier.
            - **Empirically validated outlier treatment:** Training-fold IQR capping (`k = 1.5`) raises Test ROC-AUC from `0.7072` to `0.7411` (`+0.0339`).
            - **No `Payment_Method` leakage:** Removing `Payment_Method` changes Test ROC-AUC by only `-0.0002` (`0.7409`).
            """
        )
    with l_col:
        st.markdown(
            """
            **Model Scope & Limitations**
            - **Cart-Stage / Pre-Checkout Only:** Removing cart-stage variables drops Test ROC-AUC to `0.6697`; score sessions only once a cart is active.
            - **Probabilistic Estimates:** Predicted probabilities (`Brier = 0.1903`) support prioritization and testing, not guaranteed revenue or conversion.
            - **Observational Data:** Associations between features and `Purchase` do not prove causation.
            - **Dataset Provenance:** Source dataset redistribution rights remain unverified (`DATA_PROVENANCE.md`).
            """
        )
