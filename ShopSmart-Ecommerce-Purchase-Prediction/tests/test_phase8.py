"""Phase 8 Automated Test Suite — Validation, Calibration, Model Comparison, Simulator, Robustness & 8-Page App."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils import predict_batch_customers, validate_batch_csv  # noqa: F401
from src.business_simulator import (
    simulate_campaign,
    simulate_scenarios,
    threshold_profit_sweep,
    validate_simulator_inputs,
)
from src.phase8_experiments import (
    COMP_DIR,
    SUMMARY_PATH,
    compute_calibration_diagnostics,
    run_subgroup_analysis,
    select_thresholds_on_validation,
)


def test_leakage_safe_threshold_selection():
    rng = np.random.default_rng(42)
    probs = rng.uniform(0.05, 0.95, size=500)
    y = (rng.uniform(0, 1, size=500) < probs).astype(int)
    res = select_thresholds_on_validation(y, probs)
    assert set(res.keys()) == {
        "default_0.50",
        "val_f1_optimal",
        "high_recall_ge90",
        "high_precision_ge80",
        "cost_sensitive",
    }
    assert res["default_0.50"]["selected_threshold"] == 0.50
    assert res["high_recall_ge90"]["val_metrics"]["recall"] >= 0.90
    assert res["high_precision_ge80"]["val_metrics"]["precision"] >= 0.80


def test_calibration_diagnostics_metrics():
    rng = np.random.default_rng(7)
    probs = rng.uniform(0.1, 0.9, size=600)
    y = (rng.uniform(0, 1, size=600) < probs).astype(int)
    cal = compute_calibration_diagnostics(y, probs, n_bins=10)
    assert 0.0 <= cal["brier_score"] <= 1.0
    assert 0.0 <= cal["ece_10bin_uniform"] <= 1.0
    assert cal["log_loss"] > 0.0
    assert np.isfinite(cal["calibration_slope"]) and np.isfinite(cal["calibration_intercept"])
    assert len(cal["band_breakdown"]) == 10


def test_model_comparison_artifact_present_and_complete():
    csv_path = COMP_DIR / "model_comparison.csv"
    assert csv_path.exists(), "Run src/phase8_experiments.py to generate Phase 8 artifacts."
    assert SUMMARY_PATH.exists()
    df = pd.read_csv(csv_path)
    assert set(df["Model"]) == {"DummyClassifier", "LogisticRegression", "RandomForest", "HistGradientBoosting"}
    lr_auc = float(df.loc[df["Model"] == "LogisticRegression", "Test_ROC_AUC"].iloc[0])
    dummy_auc = float(df.loc[df["Model"] == "DummyClassifier", "Test_ROC_AUC"].iloc[0])
    assert lr_auc > dummy_auc + 0.20


def test_business_simulator_calculations_and_scenarios():
    probs = np.array([0.85, 0.72, 0.60, 0.45, 0.25])
    res = simulate_campaign(
        probabilities=probs,
        campaign_budget_inr=10_000.0,
        cost_per_customer_inr=50.0,
        avg_order_value_inr=2_000.0,
        profit_margin_pct=30.0,
        expected_uplift_pct=10.0,
        effectiveness_pct=100.0,
        decision_threshold=0.50,
        available_customers=100,
    )
    # 3/5 = 60% qualified -> 60 customers selected; cost = 3,000; inc_conv = 6; inc_rev = 12,000; gp = 3,600; net = 600; roi = 20%
    assert res["customers_selected"] == 60
    assert res["campaign_expenditure_inr"] == 3000.0
    assert res["incremental_conversions"] == 6.0
    assert res["incremental_revenue_inr"] == 12000.0
    assert res["incremental_gross_profit_inr"] == 3600.0
    assert res["net_incremental_profit_inr"] == 600.0
    assert res["roi_pct"] == 20.0
    assert res["budget_utilization_pct"] == 30.0

    scen = simulate_scenarios(probs, 10_000.0, 50.0, 2_000.0, 30.0, 10.0, 100.0, 0.50, 100)
    assert len(scen) == 3
    assert scen.iloc[2]["Net_Incremental_Profit_INR"] >= scen.iloc[1]["Net_Incremental_Profit_INR"] >= scen.iloc[0]["Net_Incremental_Profit_INR"]

    sweep = threshold_profit_sweep(probs, 10_000.0, 50.0, 2_000.0, 30.0, 10.0, 100.0, 100)
    assert len(sweep) > 5


def test_business_simulator_edge_cases_and_invalid_inputs():
    probs = np.array([0.80, 0.60, 0.40])

    # Zero campaign budget
    z_budget = simulate_campaign(probs, 0.0, 50.0, 1500.0, 25.0, 5.0, 100.0, 0.50, 100)
    assert z_budget["customers_selected"] == 0
    assert z_budget["campaign_expenditure_inr"] == 0.0
    assert z_budget["roi_pct"] is None

    # Zero selected customers (threshold above all probabilities)
    z_sel = simulate_campaign(probs, 50_000.0, 50.0, 1500.0, 25.0, 5.0, 100.0, 0.95, 100)
    assert z_sel["customers_selected"] == 0
    assert z_sel["incremental_conversions"] == 0.0

    # Zero available customers
    z_avail = simulate_campaign(probs, 50_000.0, 50.0, 1500.0, 25.0, 5.0, 100.0, 0.50, 0)
    assert z_avail["customers_selected"] == 0

    # Extreme values (100% uplift capped at remaining non-converters; very large customer count)
    ext = simulate_campaign(np.array([0.90, 0.95]), 1e9, 1.0, 100_000.0, 50.0, 100.0, 100.0, 0.50, 1_000_000)
    assert ext["incremental_conversions"] <= ext["customers_selected"] - ext["baseline_conversions"] + 1e-6

    # Invalid negative costs & invalid margin/AOV
    errs = validate_simulator_inputs(-100.0, -5.0, 0.0, 120.0, -2.0, 150.0, 0.99, -10)
    assert len(errs) == 8
    with pytest.raises(ValueError):
        simulate_campaign(probs, 10_000.0, -10.0, 1500.0, 25.0, 5.0)


def test_subgroup_minimum_sample_size_guardrail():
    # Create synthetic test frame where Tablet has only 10 rows (< 50)
    df = pd.DataFrame(
        {
            "Device_Type": ["Mobile"] * 80 + ["Tablet"] * 10,
            "Membership_Type": ["Regular"] * 90,
            "Traffic_Source": ["Organic"] * 90,
            "Age": [30] * 90,
        }
    )
    rng = np.random.default_rng(123)
    probs = rng.uniform(0.2, 0.8, size=90)
    y = (rng.uniform(0, 1, size=90) < probs).astype(int)
    sub = run_subgroup_analysis(df, y, probs, threshold=0.50, min_n=50, min_class_n=10)
    tab_row = sub[(sub["Dimension"] == "Device Type") & (sub["Subgroup"] == "Tablet")].iloc[0]
    mob_row = sub[(sub["Dimension"] == "Device Type") & (sub["Subgroup"] == "Mobile")].iloc[0]
    assert bool(tab_row["Sufficient_Sample"]) is False
    assert pd.isna(tab_row["ROC_AUC"])
    assert "n=10 < 50" in str(tab_row["Warning"])
    assert bool(mob_row["Sufficient_Sample"]) is True
    assert pd.notna(mob_row["ROC_AUC"])


def test_streamlit_all_eight_pages_including_business_simulator():
    at = AppTest.from_file(str(PROJECT_ROOT / "app" / "app.py"), default_timeout=45)
    at.run()
    assert len(at.exception) == 0, f"Initial load exception: {at.exception}"

    page_names = [
        "1. Executive Overview",
        "2. Customer Analytics",
        "3. Model Performance",
        "4. Single Customer Prediction",
        "5. Batch Prediction",
        "6. Business Insights",
        "7. Model Information",
        "8. Business Impact Simulator",
    ]
    for pname in page_names:
        at.sidebar.radio[0].set_value(pname).run()
        assert len(at.exception) == 0, f"Exception on '{pname}': {at.exception}"
        assert len(at.error) == 0, f"Unexpected st.error on '{pname}': {at.error}"
