"""Page 4: Single Customer Prediction — Cart-Stage / Pre-Checkout Intent Estimator."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from app.components import BLUE, NAVY, TEAL, render_cart_stage_notice, render_header, render_kpi_card
from app.utils import KNOWN_CATEGORIES, predict_single_customer


def render() -> None:
    render_header(
        "Single Customer Prediction",
        "Cart-Stage / Pre-Checkout Purchase Intent Scoring Using the Saved Logistic Regression Pipeline",
    )
    render_cart_stage_notice()

    with st.form("single_customer_form"):
        st.subheader("Customer Profile & Active Cart Session Inputs")
        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.number_input("Age", min_value=18, max_value=90, value=34, step=1)
            gender = st.selectbox("Gender", KNOWN_CATEGORIES["Gender"], index=0)
            membership = st.selectbox("Membership Type", KNOWN_CATEGORIES["Membership_Type"], index=0)
            device = st.selectbox("Device Type", KNOWN_CATEGORIES["Device_Type"], index=0)
            traffic = st.selectbox("Traffic Source", KNOWN_CATEGORIES["Traffic_Source"], index=0)
            payment = st.selectbox("Payment Method", KNOWN_CATEGORIES["Payment_Method"], index=0)

        with col2:
            session_dur = st.number_input("Session Duration (Min)", min_value=0.1, max_value=250.0, value=12.5, step=0.5)
            pages_viewed = st.number_input("Pages Viewed", min_value=1.0, max_value=150.0, value=8.0, step=1.0)
            products_viewed = st.number_input("Products Viewed", min_value=0, max_value=30, value=4, step=1)
            cart_items = st.number_input("Cart Items (Active Cart)", min_value=0, max_value=20, value=2, step=1)
            cart_value = st.number_input("Cart Value (INR)", min_value=0.0, max_value=100000.0, value=1800.0, step=50.0)
            discount_pct = st.slider("Discount Percent (%)", 0.0, 80.0, 12.0, step=0.5)

        with col3:
            prev_orders = st.number_input("Previous Orders", min_value=0, max_value=50, value=3, step=1)
            days_since = st.number_input("Days Since Last Visit", min_value=0.0, max_value=365.0, value=8.0, step=1.0)
            email_open = st.slider("Email Open Rate", 0.0, 1.0, 0.50, step=0.01)
            rating = st.slider("Customer Rating", 1.0, 5.0, 3.8, step=0.1)
            returns = st.number_input("Returns Last Year", min_value=0, max_value=20, value=0, step=1)
            threshold = st.slider("Decision Threshold", 0.20, 0.85, 0.50, step=0.05)

        submitted = st.form_submit_button("Estimate Purchase Intent", type="primary")

    if submitted:
        payload = {
            "Age": age,
            "Gender": gender,
            "Device_Type": device,
            "Traffic_Source": traffic,
            "Membership_Type": membership,
            "Payment_Method": payment,
            "Session_Duration_Min": session_dur,
            "Pages_Viewed": pages_viewed,
            "Products_Viewed": products_viewed,
            "Cart_Items": cart_items,
            "Cart_Value_INR": cart_value,
            "Discount_Percent": discount_pct,
            "Previous_Orders": prev_orders,
            "Days_Since_Last_Visit": days_since,
            "Email_Open_Rate": email_open,
            "Customer_Rating": rating,
            "Returns_Last_Year": returns,
        }
        try:
            res = predict_single_customer(payload, threshold=threshold)
        except Exception as exc:
            st.error(f"Prediction failed: {exc}")
            return

        prob = res["purchase_probability"]
        pred_label = "Likely Purchase (1)" if res["predicted_purchase"] == 1 else "Likely No Purchase (0)"

        r1, r2, r3 = st.columns(3)
        with r1:
            render_kpi_card("Purchase Probability", f"{prob * 100:.2f}%", f"Threshold: {threshold:.2f}")
        with r2:
            render_kpi_card("Predicted Class", pred_label, "Cart-stage classification estimate")
        with r3:
            render_kpi_card("Marketing Segment", res["marketing_segment"], "Probability-tiered intent band")

        fig_g = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={"suffix": "%"},
                title={"text": "Estimated Cart-Stage Purchase Probability"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": BLUE},
                    "steps": [
                        {"range": [0, 30], "color": "#FEE2E2"},
                        {"range": [30, 50], "color": "#FEF3C7"},
                        {"range": [50, 75], "color": "#DBEAFE"},
                        {"range": [75, 100], "color": "#CCFBF1"},
                    ],
                    "threshold": {"line": {"color": NAVY, "width": 3}, "thickness": 0.8, "value": threshold * 100},
                },
            )
        )
        fig_g.update_layout(height=270, margin=dict(t=45, b=10, l=20, r=20))
        st.plotly_chart(fig_g, width="stretch")

        st.info(f"**Recommended Campaign Action:** {res['recommended_action']}")
        st.caption(
            "Disclaimer: This output is a statistical estimate from a cart-stage Logistic Regression model, "
            "not a guaranteed customer purchase outcome."
        )
