"""Shared data loading, caching, validation, and prediction utilities for ShopSmart."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CAT_COLS,
    DATA_RAW_PATH,
    FIGURES_DIR,
    ID_COL,
    METRICS_PATH,
    MODEL_PATH,
    NUM_COLS,
    PREDICTIONS_PATH,
    TARGET_COL,
)
from src.preprocessing import assign_marketing_segment

MODEL_VERSION = "v1.0.0 (Logistic Regression L2, C=1.0, IQR k=1.5)"
REQUIRED_FEATURE_COLS = CAT_COLS + NUM_COLS

KNOWN_CATEGORIES: dict[str, list[str]] = {
    "Gender": ["Female", "Male", "Other"],
    "Device_Type": ["Mobile", "Desktop", "Tablet"],
    "Traffic_Source": ["Organic", "Paid Ads", "Social Media", "Email", "Referral"],
    "Membership_Type": ["Regular", "New", "Premium"],
    "Payment_Method": ["UPI", "Credit Card", "Debit Card", "Wallet", "Cash on Delivery"],
}


def recommended_campaign_action(segment: str) -> str:
    """Return a concise, non-guaranteed marketing action recommendation per intent tier."""
    mapping = {
        "High Intent (>=0.75)": "Frictionless checkout reminder; avoid unnecessary margin-eroding discounts.",
        "Medium Intent (0.50-0.74)": "Targeted cart nudge (free-shipping cue or time-bound small incentive).",
        "Low-Medium Intent (0.30-0.49)": "Social proof, product comparison, or modest discount test via email/push.",
        "Low Intent (<0.30)": "Low-cost retargeting or suppress paid spend to protect campaign ROI.",
    }
    return mapping.get(segment, "Monitor session behavior.")


@st.cache_resource
def load_model(model_path: Path = MODEL_PATH):
    """Load the pre-trained scikit-learn Pipeline without retraining."""
    if not model_path.exists():
        raise FileNotFoundError(
            f"Saved model not found at `{model_path}`. Run `.\\.venv\\Scripts\\python.exe src\\train_pipeline.py` first."
        )
    return joblib.load(model_path)


@st.cache_data
def load_metrics(metrics_path: Path = METRICS_PATH) -> dict[str, Any]:
    """Load verified model evaluation metrics JSON."""
    if not metrics_path.exists():
        raise FileNotFoundError(
            f"Metrics file not found at `{metrics_path}`. Run `.\\.venv\\Scripts\\python.exe src\\train_pipeline.py` first."
        )
    return json.loads(metrics_path.read_text(encoding="utf-8"))


@st.cache_data
def load_raw_dataset(csv_path: Path = DATA_RAW_PATH) -> pd.DataFrame | None:
    """Load local dataset if available (returns None gracefully when absent)."""
    if not csv_path.exists():
        return None
    return pd.read_csv(csv_path)


@st.cache_data
def load_test_predictions(pred_path: Path = PREDICTIONS_PATH) -> pd.DataFrame | None:
    """Load saved held-out test-set predictions if available."""
    if not pred_path.exists():
        return None
    return pd.read_csv(pred_path)


def predict_single_customer(
    features: dict[str, Any],
    model=None,
    threshold: float = 0.50,
) -> dict[str, Any]:
    """Score one customer cart-stage record and return probability, class, segment, and action."""
    missing = [c for c in REQUIRED_FEATURE_COLS if c not in features]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    pipe = model if model is not None else load_model()
    row_df = pd.DataFrame([{c: features[c] for c in REQUIRED_FEATURE_COLS}])
    for col in NUM_COLS:
        row_df[col] = pd.to_numeric(row_df[col], errors="raise")

    prob = float(pipe.predict_proba(row_df)[:, 1][0])
    pred_class = int(prob >= threshold)
    segment = assign_marketing_segment(prob)
    action = recommended_campaign_action(segment)
    return {
        "purchase_probability": round(prob, 6),
        "predicted_purchase": pred_class,
        "marketing_segment": segment,
        "recommended_action": action,
        "threshold": threshold,
    }


def validate_batch_csv(df: pd.DataFrame) -> dict[str, Any]:
    """Validate an uploaded batch CSV without mutating or saving it to disk."""
    errors: list[str] = []
    warnings: list[str] = []

    if df is None or df.empty:
        return {"valid": False, "errors": ["Uploaded CSV contains 0 rows."], "warnings": []}

    missing_cols = [c for c in REQUIRED_FEATURE_COLS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required feature columns ({len(missing_cols)}): {', '.join(missing_cols)}")

    if TARGET_COL in df.columns or "Actual_Purchase" in df.columns:
        warnings.append(
            "Uploaded file contains a target/label column (`Purchase` or `Actual_Purchase`). "
            "Label columns are ignored during scoring; use unlabelled new customer records for production batch inference."
        )

    # Check numeric type coercibility
    bad_num_cols: list[str] = []
    for col in NUM_COLS:
        if col in df.columns:
            non_null = df[col].dropna()
            coerced = pd.to_numeric(non_null, errors="coerce")
            bad_cnt = int(coerced.isna().sum())
            if bad_cnt > 0:
                bad_num_cols.append(f"{col} ({bad_cnt} non-numeric values)")
    if bad_num_cols:
        errors.append("Invalid numeric values detected in: " + "; ".join(bad_num_cols))

    # Missing value summary (pipeline imputes automatically, so warn rather than block)
    present_feats = [c for c in REQUIRED_FEATURE_COLS if c in df.columns]
    if present_feats:
        total_missing = int(df[present_feats].isna().sum().sum())
        if total_missing > 0:
            warnings.append(
                f"{total_missing:,} missing feature values detected — the pipeline will impute them using training medians/modes."
            )

    # Unseen category check (OneHotEncoder handles_unknown='ignore', so warn)
    unseen_msgs: list[str] = []
    for col, known in KNOWN_CATEGORIES.items():
        if col in df.columns:
            vals = set(df[col].dropna().astype(str).unique())
            unseen = sorted(vals - set(known))
            if unseen:
                unseen_msgs.append(f"{col}: {unseen[:5]}")
    if unseen_msgs:
        warnings.append(
            "Unexpected categories detected (encoded as zero indicators by OneHotEncoder): " + "; ".join(unseen_msgs)
        )

    # Duplicate Customer_ID check
    if ID_COL in df.columns:
        dup_ids = int(df[ID_COL].duplicated().sum())
        if dup_ids > 0:
            warnings.append(f"{dup_ids:,} duplicate `{ID_COL}` values detected in upload.")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def predict_batch_customers(
    df: pd.DataFrame,
    model=None,
    threshold: float = 0.50,
) -> pd.DataFrame:
    """Validate and score a batch DataFrame in memory (never writes uploaded data to disk)."""
    report = validate_batch_csv(df)
    if not report["valid"]:
        raise ValueError(" | ".join(report["errors"]))

    pipe = model if model is not None else load_model()
    X = df[REQUIRED_FEATURE_COLS].copy()
    for col in NUM_COLS:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    probs = pipe.predict_proba(X)[:, 1]
    preds = (probs >= threshold).astype(int)
    segments = [assign_marketing_segment(float(p)) for p in probs]
    actions = [recommended_campaign_action(s) for s in segments]

    out = pd.DataFrame(index=df.index)
    if ID_COL in df.columns:
        out[ID_COL] = df[ID_COL]
    else:
        out["Row_Index"] = np.arange(1, len(df) + 1)
    out["Purchase_Probability"] = np.round(probs, 6)
    out["Predicted_Purchase"] = preds
    out["Marketing_Segment"] = segments
    out["Recommended_Action"] = actions
    return out


def get_blank_template_csv() -> bytes:
    """Generate a clean unlabelled 2-row sample CSV template for batch scoring."""
    sample = pd.DataFrame(
        [
            {
                "Customer_ID": "NEW_001",
                "Age": 32,
                "Gender": "Female",
                "Device_Type": "Desktop",
                "Traffic_Source": "Email",
                "Membership_Type": "Premium",
                "Payment_Method": "Credit Card",
                "Session_Duration_Min": 16.5,
                "Pages_Viewed": 9,
                "Products_Viewed": 5,
                "Cart_Items": 3,
                "Cart_Value_INR": 2450.0,
                "Discount_Percent": 15.0,
                "Previous_Orders": 4,
                "Days_Since_Last_Visit": 5.0,
                "Email_Open_Rate": 0.65,
                "Customer_Rating": 4.3,
                "Returns_Last_Year": 0,
            },
            {
                "Customer_ID": "NEW_002",
                "Age": 26,
                "Gender": "Male",
                "Device_Type": "Mobile",
                "Traffic_Source": "Social Media",
                "Membership_Type": "New",
                "Payment_Method": "UPI",
                "Session_Duration_Min": 4.2,
                "Pages_Viewed": 3,
                "Products_Viewed": 2,
                "Cart_Items": 1,
                "Cart_Value_INR": 480.0,
                "Discount_Percent": 5.0,
                "Previous_Orders": 0,
                "Days_Since_Last_Visit": 25.0,
                "Email_Open_Rate": 0.20,
                "Customer_Rating": 3.2,
                "Returns_Last_Year": 1,
            },
        ]
    )
    return sample.to_csv(index=False).encode("utf-8")
