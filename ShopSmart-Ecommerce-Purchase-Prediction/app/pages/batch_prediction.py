"""Page 5: Batch Prediction — Validated In-Memory CSV Scoring & Export."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components import BLUE, TEAL, render_cart_stage_notice, render_header, render_kpi_card
from app.utils import (
    REQUIRED_FEATURE_COLS,
    get_blank_template_csv,
    predict_batch_customers,
    validate_batch_csv,
)


def render() -> None:
    render_header(
        "Batch Customer Prediction",
        "Upload New Unlabelled Cart-Stage Customer Records for Validated In-Memory Scoring",
    )
    render_cart_stage_notice()

    st.caption(
        "Privacy & Storage Policy: Uploaded CSV files are validated and scored strictly in memory. "
        "Customer data is never written to disk by this application."
    )

    c_tmpl, c_thr = st.columns([1, 1])
    with c_tmpl:
        st.download_button(
            label="Download Unlabelled CSV Template (2 Example Rows)",
            data=get_blank_template_csv(),
            file_name="shopsmart_batch_template.csv",
            mime="text/csv",
            help="Use this schema for new customer records (do not substitute labelled test-set files).",
        )
    with c_thr:
        threshold = st.slider("Batch Decision Threshold", 0.20, 0.85, 0.50, step=0.05)

    uploaded = st.file_uploader("Upload New Customer CSV", type=["csv"])
    if uploaded is None:
        with st.expander("Required Input Columns (17 Features + Optional Customer_ID)"):
            st.code(", ".join(REQUIRED_FEATURE_COLS), language="text")
        return

    try:
        raw_df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Could not parse uploaded CSV file: {exc}")
        return

    report = validate_batch_csv(raw_df)
    for warn in report["warnings"]:
        st.warning(warn)

    if not report["valid"]:
        for err in report["errors"]:
            st.error(err)
        return

    try:
        scored_df = predict_batch_customers(raw_df, threshold=threshold)
    except Exception as exc:
        st.error(f"Batch scoring failed: {exc}")
        return

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Records Scored", f"{len(scored_df):,}", "Processed in memory")
    with k2:
        pred_buyers = int(scored_df["Predicted_Purchase"].sum())
        render_kpi_card("Predicted Buyers", f"{pred_buyers:,}", f"{pred_buyers/len(scored_df)*100:.1f}% @ t={threshold:.2f}")
    with k3:
        render_kpi_card("Mean Probability", f"{scored_df['Purchase_Probability'].mean()*100:.2f}%", "Average intent score")
    with k4:
        hi = int((scored_df["Marketing_Segment"] == "High Intent (>=0.75)").sum())
        render_kpi_card("High Intent Segment", f"{hi:,}", f"{hi/len(scored_df)*100:.1f}% of upload")

    seg_df = scored_df["Marketing_Segment"].value_counts().reset_index()
    seg_df.columns = ["Marketing Segment", "Customers"]
    fig = px.bar(
        seg_df,
        x="Marketing Segment",
        y="Customers",
        text="Customers",
        color_discrete_sequence=[TEAL],
        title="Uploaded Batch — Predicted Marketing Intent Segments",
    )
    fig.update_layout(height=300, plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")

    st.subheader("Scored Output Preview (First 100 Rows)")
    st.dataframe(scored_df.head(100), width="stretch")

    csv_bytes = scored_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Export Scored Predictions CSV",
        data=csv_bytes,
        file_name="shopsmart_batch_predictions.csv",
        mime="text/csv",
        type="primary",
        disabled=scored_df.empty,
    )
