"""Page 7: Model Information — Architecture, Preprocessing, Governance & Limitations."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components import render_cart_stage_notice, render_header
from app.utils import MODEL_VERSION, load_metrics


def render() -> None:
    render_header(
        "Model Information & Governance",
        "Technical Architecture, Preprocessing Methodology, Timing Assumptions & Limitations",
    )
    render_cart_stage_notice()

    metrics = load_metrics()
    ds = metrics["dataset"]
    pm = metrics["primary_model"]
    cv = pm["cv_5fold"]

    spec_df = pd.DataFrame(
        [
            ("Model Version", MODEL_VERSION),
            ("Evaluation Date", "2026-11-21 (Phase 8 leakage-safe validation & calibration audit)"),
            ("Selected Features (17 Inputs)", "5 categorical (Gender, Device_Type, Traffic_Source, Membership_Type, Payment_Method) + 12 numeric (Age, Session_Duration_Min, Pages_Viewed, Products_Viewed, Cart_Items, Cart_Value_INR, Discount_Percent, Previous_Orders, Days_Since_Last_Visit, Email_Open_Rate, Customer_Rating, Returns_Last_Year)"),
            ("Algorithm", "L2-Regularized Logistic Regression (C = 1.0, max_iter = 1000, random_state = 42)"),
            ("Training / Test Split", "Stratified 80/20 split: 8,000 training rows / 2,000 held-out test rows"),
            ("Cross-Validation", f"5-Fold Stratified CV (ROC-AUC = {cv['roc_auc_mean']:.4f} ± {cv['roc_auc_std']:.4f})"),
            ("Transformed Feature Space", f"{pm['feature_count_transformed']} features (12 scaled numeric + 14 one-hot indicators)"),
            ("Missing-Value Handling", f"{ds['missing_values']:,} nulls imputed strictly inside pipeline (median numeric / mode categorical)"),
            ("IQR Outlier Treatment", "Training-fold Winsorisation (k = 1.5) on 5 spike columns; empirically validated (+0.0339 Test ROC-AUC vs raw)"),
            ("Prediction Timing Assumption", "Cart-Stage / Pre-Checkout Intent Model (requires active cart metrics; not for landing-page scoring)"),
            ("Model Artifact", "models/logistic_regression_pipeline.joblib (loaded via @st.cache_resource; zero retraining on launch)"),
        ],
        columns=["Specification", "Verified Detail"],
    )
    st.table(spec_df)

    st.subheader("Known Limitations & Responsible Use")
    st.markdown(
        """
        1. **Cart-Stage Scope:** Dropping cart-stage features (`Cart_Items`, `Cart_Value_INR`, `Discount_Percent`, `Payment_Method`) lowers Test ROC-AUC from `0.7411` to `0.6697`. Do not deploy this model prior to cart creation.
        2. **Linear Decision Boundary:** Logistic Regression is chosen for interpretability and well-calibrated probabilities (`Brier = 0.1903`), trading off potential non-linear interactions for transparent odds ratios.
        3. **Non-Causal Outputs:** Feature coefficients capture historical associations, not causal treatment effects.
        4. **Dataset Provenance & Privacy:** Upstream dataset provenance and redistribution rights remain unverified (`DATA_PROVENANCE.md`); raw datasets are excluded from GitHub, and uploaded batch CSVs are scored strictly in memory.
        """
    )
