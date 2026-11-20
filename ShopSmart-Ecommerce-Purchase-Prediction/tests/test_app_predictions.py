"""Automated unit & Streamlit AppTest suite for ShopSmart — Purchase Intelligence Platform."""

from __future__ import annotations

import io
import sys
from pathlib import Path
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils import (
    get_blank_template_csv,
    predict_batch_customers,
    predict_single_customer,
    validate_batch_csv,
)


def _sample_record() -> dict:
    return {
        "Age": 34,
        "Gender": "Female",
        "Device_Type": "Desktop",
        "Traffic_Source": "Email",
        "Membership_Type": "Premium",
        "Payment_Method": "Credit Card",
        "Session_Duration_Min": 15.0,
        "Pages_Viewed": 9.0,
        "Products_Viewed": 5,
        "Cart_Items": 3,
        "Cart_Value_INR": 2600.0,
        "Discount_Percent": 12.0,
        "Previous_Orders": 4,
        "Days_Since_Last_Visit": 6.0,
        "Email_Open_Rate": 0.60,
        "Customer_Rating": 4.2,
        "Returns_Last_Year": 0,
    }


def test_single_customer_prediction_outputs():
    res = predict_single_customer(_sample_record(), threshold=0.50)
    assert 0.0 <= res["purchase_probability"] <= 1.0
    assert res["predicted_purchase"] in (0, 1)
    assert res["predicted_purchase"] == int(res["purchase_probability"] >= 0.50)
    assert isinstance(res["marketing_segment"], str) and len(res["marketing_segment"]) > 0
    assert isinstance(res["recommended_action"], str) and len(res["recommended_action"]) > 0


def test_single_customer_missing_feature_raises():
    bad = _sample_record()
    del bad["Cart_Items"]
    with pytest.raises(ValueError, match="Missing required features"):
        predict_single_customer(bad)


def test_batch_validation_missing_columns_and_bad_types():
    # Empty CSV
    empty_rep = validate_batch_csv(pd.DataFrame())
    assert empty_rep["valid"] is False

    # Missing required columns
    miss_df = pd.DataFrame([{"Age": 30, "Gender": "Male"}])
    miss_rep = validate_batch_csv(miss_df)
    assert miss_rep["valid"] is False
    assert any("Missing required feature columns" in e for e in miss_rep["errors"])

    # Invalid non-numeric data
    tmpl = pd.read_csv(io.BytesIO(get_blank_template_csv()))
    bad_num = tmpl.copy()
    bad_num["Cart_Value_INR"] = bad_num["Cart_Value_INR"].astype(object)
    bad_num.loc[0, "Cart_Value_INR"] = "NOT_A_NUMBER"
    num_rep = validate_batch_csv(bad_num)
    assert num_rep["valid"] is False
    assert any("Invalid numeric values" in e for e in num_rep["errors"])


def test_batch_validation_warnings_and_scoring_export():
    tmpl = pd.read_csv(io.BytesIO(get_blank_template_csv()))
    # Introduce missing value, unseen category, and duplicate ID
    mod = pd.concat([tmpl, tmpl.iloc[[0]]], ignore_index=True)
    mod.loc[0, "Age"] = None
    mod.loc[1, "Traffic_Source"] = "PodcastAd_New"

    rep = validate_batch_csv(mod)
    assert rep["valid"] is True
    assert any("missing feature values" in w for w in rep["warnings"])
    assert any("Unexpected categories" in w for w in rep["warnings"])
    assert any("duplicate `Customer_ID`" in w for w in rep["warnings"])

    scored = predict_batch_customers(mod, threshold=0.50)
    assert len(scored) == 3
    assert set(["Customer_ID", "Purchase_Probability", "Predicted_Purchase", "Marketing_Segment", "Recommended_Action"]).issubset(scored.columns)
    assert (scored["Purchase_Probability"] >= 0.0).all() and (scored["Purchase_Probability"] <= 1.0).all()
    csv_bytes = scored.to_csv(index=False).encode("utf-8")
    reloaded = pd.read_csv(io.BytesIO(csv_bytes))
    assert len(reloaded) == 3


def test_streamlit_all_seven_pages_and_single_prediction_form():
    at = AppTest.from_file(str(PROJECT_ROOT / "app" / "app.py"), default_timeout=45)
    at.run()
    assert len(at.exception) == 0, f"Page 1 exception: {at.exception}"

    page_names = [
        "1. Executive Overview",
        "2. Customer Analytics",
        "3. Model Performance",
        "4. Single Customer Prediction",
        "5. Batch Prediction",
        "6. Business Insights",
        "7. Model Information",
    ]
    for pname in page_names:
        at.sidebar.radio[0].set_value(pname).run()
        assert len(at.exception) == 0, f"Exception on '{pname}': {at.exception}"

        if pname == "2. Customer Analytics":
            # Regression check (DEF-06): clearing Gender multiselect must yield 0 rows and empty-filter notice
            at.multiselect[0].set_value([]).run()
            assert len(at.exception) == 0, f"Empty Gender filter exception: {at.exception}"
            assert len(at.metric) == 0, "Expected 0 metric widgets when Gender filter is cleared"
            assert any("No customer records match the selected filters" in i.value for i in at.info)
            # Restore normal selection
            at.multiselect[0].set_value(["Female", "Male", "Other"]).run()
            assert len(at.exception) == 0
            assert len(at.metric) == 4

        if pname == "4. Single Customer Prediction":
            at.button[0].click().run()
            assert len(at.exception) == 0, f"Form submit exception: {at.exception}"
            assert any("Recommended Campaign Action" in i.value for i in at.info)
