"""Leakage-free preprocessing transformers and Logistic Regression pipeline builder."""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import CAP_COLS, CAT_COLS, PLAIN_NUM_COLS, RANDOM_STATE


class IQRCapper(BaseEstimator, TransformerMixin):
    """Winsorise numeric features outside [Q1 - k*IQR, Q3 + k*IQR] using training-fold bounds only."""

    def __init__(self, k: float = 1.5) -> None:
        self.k = k

    def fit(self, X, y=None):
        arr = np.asarray(X, dtype=float)
        q1, q3 = np.nanpercentile(arr, [25, 75], axis=0)
        iqr = q3 - q1
        self.lower_ = q1 - self.k * iqr
        self.upper_ = q3 + self.k * iqr
        return self

    def transform(self, X):
        arr = np.asarray(X, dtype=float)
        return np.clip(arr, self.lower_, self.upper_)

    def get_feature_names_out(self, input_features=None):
        return np.asarray(input_features, dtype=object)


def build_pipeline(
    cap: bool = True,
    cap_k: float = 1.5,
    class_weight: str | dict | None = None,
    c_val: float = 1.0,
    cap_cols: list[str] | None = None,
    plain_num_cols: list[str] | None = None,
    cat_cols: list[str] | None = None,
) -> Pipeline:
    """Build a leakage-free preprocessing + Logistic Regression scikit-learn Pipeline."""
    use_cap_cols = CAP_COLS if cap_cols is None else cap_cols
    use_plain_cols = PLAIN_NUM_COLS if plain_num_cols is None else plain_num_cols
    use_cat_cols = CAT_COLS if cat_cols is None else cat_cols

    transformers = []

    if use_cap_cols:
        capped_steps = [("impute", SimpleImputer(strategy="median"))]
        if cap:
            capped_steps.append(("cap", IQRCapper(k=cap_k)))
        capped_steps.append(("scale", StandardScaler()))
        transformers.append(("cap_num", Pipeline(capped_steps), use_cap_cols))

    if use_plain_cols:
        transformers.append(
            (
                "num",
                Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]),
                use_plain_cols,
            )
        )

    if use_cat_cols:
        transformers.append(
            (
                "cat",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore")),
                    ]
                ),
                use_cat_cols,
            )
        )

    prep = ColumnTransformer(transformers=transformers, remainder="drop")
    model = LogisticRegression(
        C=c_val,
        max_iter=1000,
        class_weight=class_weight,
        random_state=RANDOM_STATE,
    )
    return Pipeline([("prep", prep), ("model", model)])


def assign_marketing_segment(prob: float) -> str:
    """Map predicted purchase probability into actionable marketing intent tiers."""
    if prob >= 0.75:
        return "High Intent (>=0.75)"
    if prob >= 0.50:
        return "Medium Intent (0.50-0.74)"
    if prob >= 0.30:
        return "Low-Medium Intent (0.30-0.49)"
    return "Low Intent (<0.30)"
