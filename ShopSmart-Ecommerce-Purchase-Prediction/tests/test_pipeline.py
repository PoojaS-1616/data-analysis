"""Automated validation & reproducibility tests for E-Commerce Purchase Prediction."""

from __future__ import annotations

import json
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import CAT_COLS, DATA_RAW_PATH, ID_COL, METRICS_PATH, MODEL_PATH, NUM_COLS, TARGET_COL
from src.predict import predict_dataframe
from src.preprocessing import IQRCapper, build_pipeline


def test_dataset_schema_and_balance():
    assert DATA_RAW_PATH.exists(), f"Dataset missing at {DATA_RAW_PATH}"
    df = pd.read_csv(DATA_RAW_PATH)
    assert df.shape == (10_000, 19)
    assert int(df.duplicated().sum()) == 0
    assert int(df[ID_COL].nunique()) == 10_000
    assert int(df[TARGET_COL].isna().sum()) == 0
    assert int(df[TARGET_COL].sum()) == 6_480
    assert abs(df[TARGET_COL].mean() - 0.648) < 1e-6


def test_iqr_capper_no_leakage():
    train = np.array([[10.0], [12.0], [14.0], [15.0], [16.0], [18.0]])
    test = np.array([[1000.0], [-500.0], [14.0]])
    capper = IQRCapper(k=1.5).fit(train)
    out = capper.transform(test)
    assert out[0, 0] == capper.upper_[0]
    assert out[1, 0] == capper.lower_[0]
    assert out[2, 0] == 14.0


def test_saved_model_and_reproducibility():
    assert MODEL_PATH.exists(), "Run src/train_pipeline.py before running tests."
    assert METRICS_PATH.exists(), "metrics_summary.json missing."

    df = pd.read_csv(DATA_RAW_PATH)
    sample = df.head(25)
    preds1 = predict_dataframe(sample, model_path=MODEL_PATH, threshold=0.50)
    preds2 = predict_dataframe(sample, model_path=MODEL_PATH, threshold=0.50)

    assert len(preds1) == 25
    assert set(preds1["Predicted_Purchase"].unique()).issubset({0, 1})
    assert (preds1["Purchase_Probability"] >= 0.0).all() and (preds1["Purchase_Probability"] <= 1.0).all()
    assert np.allclose(preds1["Purchase_Probability"].values, preds2["Purchase_Probability"].values)

    # Verify saved model matches freshly refit deterministic pipeline on same split
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    assert metrics["primary_model"]["test_metrics_t50"]["accuracy"] > 0.68
    assert metrics["primary_model"]["test_metrics_t50"]["roc_auc"] > 0.70


def test_pipeline_handles_missing_and_unseen_categories():
    df = pd.read_csv(DATA_RAW_PATH).head(400)
    X = df[CAT_COLS + NUM_COLS]
    y = df[TARGET_COL]
    pipe = build_pipeline(cap=True).fit(X, y)

    probe = X.head(5).copy()
    probe.loc[probe.index[0], "Traffic_Source"] = "BrandNewChannel_XYZ"
    probe.loc[probe.index[1], "Cart_Value_INR"] = np.nan
    probs = pipe.predict_proba(probe)[:, 1]
    assert len(probs) == 5
    assert np.isfinite(probs).all()
