"""Page 8: Business Impact Simulator — Interactive Campaign ROI & Scenario Modeling."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.components import BLUE, NAVY, TEAL, render_cart_stage_notice, render_header, render_kpi_card
from app.utils import load_test_predictions
from src.business_simulator import (
    simulate_campaign,
    simulate_scenarios,
    threshold_profit_sweep,
    validate_simulator_inputs,
)


def render() -> None:
    render_header(
        "Business Impact Simulator",
        "Scenario-Based Campaign ROI, Budget Utilization & Break-Even Analysis",
    )
    render_cart_stage_notice()

    st.markdown(
        """
        <div class="callout-info">
            <b>Important Distinction — Predictions vs. Scenario Assumptions:</b>
            <ul>
                <li><b>Observed Model Predictions:</b> Purchase probabilities from the validated cart-stage Logistic Regression model (held-out test distribution, <code>n = 2,000</code>).</li>
                <li><b>User-Defined Scenario Assumptions:</b> Campaign budget, outreach cost, AOV, profit margin, expected incremental uplift, and intervention effectiveness.</li>
                <li><b>Derived Financial Estimates:</b> Illustrative projections only. Assumed campaign uplift is <b>not</b> proven causal model performance and must be validated via randomized controlled A/B testing.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preds_df = load_test_predictions()
    if preds_df is not None and "Purchase_Probability" in preds_df.columns:
        base_probs = preds_df["Purchase_Probability"].dropna().to_numpy(dtype=float)
        default_avail = len(base_probs)
        prob_source = f"Held-out test-set predicted probabilities (`n = {len(base_probs):,}`)"
    else:
        # Fallback illustrative probability distribution when local CSV is excluded (e.g., fresh GitHub clone)
        rng = np.random.default_rng(42)
        base_probs = np.clip(rng.beta(2.6, 1.4, size=2000), 0.02, 0.98)
        default_avail = 2000
        prob_source = "Illustrative synthetic probability distribution (`n = 2,000`; run `src/train_pipeline.py` locally to use held-out test probabilities)"

    st.caption(f"Probability Distribution Source: {prob_source}")

    with st.expander("Campaign & Unit Economics Inputs (User-Defined Scenario Assumptions)", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            budget = st.number_input("Campaign Budget (INR)", min_value=0.0, max_value=50_000_000.0, value=100_000.0, step=5_000.0)
            cost_per_cust = st.number_input("Cost per Targeted Customer (INR)", min_value=0.0, max_value=10_000.0, value=50.0, step=5.0)
        with c2:
            aov = st.number_input("Average Order Value — AOV (INR)", min_value=1.0, max_value=500_000.0, value=1_800.0, step=100.0)
            margin_pct = st.slider("Profit Margin (%)", min_value=1.0, max_value=95.0, value=30.0, step=1.0)
        with c3:
            uplift_pct = st.slider("Expected Incremental Uplift (% pts)", min_value=0.0, max_value=30.0, value=4.0, step=0.5)
            effectiveness_pct = st.slider("Intervention Effectiveness (%)", min_value=0.0, max_value=100.0, value=80.0, step=5.0)
        with c4:
            threshold = st.slider("Model Decision Threshold", min_value=0.15, max_value=0.90, value=0.50, step=0.05)
            avail_customers = st.number_input("Available Customers to Score", min_value=0, max_value=1_000_000, value=default_avail, step=500)

    errors = validate_simulator_inputs(
        campaign_budget_inr=budget,
        cost_per_customer_inr=cost_per_cust,
        avg_order_value_inr=aov,
        profit_margin_pct=margin_pct,
        expected_uplift_pct=uplift_pct,
        effectiveness_pct=effectiveness_pct,
        decision_threshold=threshold,
        available_customers=int(avail_customers),
    )
    if errors:
        for err in errors:
            st.error(err)
        return

    res = simulate_campaign(
        probabilities=base_probs,
        campaign_budget_inr=budget,
        cost_per_customer_inr=cost_per_cust,
        avg_order_value_inr=aov,
        profit_margin_pct=margin_pct,
        expected_uplift_pct=uplift_pct,
        effectiveness_pct=effectiveness_pct,
        decision_threshold=threshold,
        available_customers=int(avail_customers),
    )

    if res["customers_selected"] == 0:
        st.warning(
            "Zero customers are selected under the current threshold, budget, or available customer count. "
            "Adjust inputs to simulate campaign economics."
        )

    if res["budget_capped"]:
        st.info(
            f"Budget cap active: model qualified `{res['model_qualified_customers']:,}` sessions at `t = {threshold:.2f}`, "
            f"and the top `{res['customers_selected']:,}` highest-intent sessions fit within the ₹{budget:,.0f} budget."
        )

    st.subheader("1. Derived Financial Estimates (Base Scenario)")
    r1 = st.columns(4)
    with r1[0]:
        render_kpi_card("Customers Selected", f"{res['customers_selected']:,}", f"Qualified: {res['model_qualified_customers']:,} @ t={threshold:.2f}")
    with r1[1]:
        render_kpi_card("Campaign Expenditure", f"₹{res['campaign_expenditure_inr']:,.0f}", f"Budget utilization: {res['budget_utilization_pct']:.1f}%")
    with r1[2]:
        render_kpi_card("Baseline Conversions", f"{res['baseline_conversions']:,.1f}", f"Mean pred. prob: {res['mean_predicted_prob_targeted']*100:.1f}%")
    with r1[3]:
        render_kpi_card("Incremental Conversions", f"{res['incremental_conversions']:,.1f}", f"Effective uplift: {res['effective_uplift_pct']:.2f}% pts")

    r2 = st.columns(4)
    with r2[0]:
        render_kpi_card("Incremental Revenue", f"₹{res['incremental_revenue_inr']:,.0f}", f"AOV: ₹{aov:,.0f}")
    with r2[1]:
        render_kpi_card("Incremental Gross Profit", f"₹{res['incremental_gross_profit_inr']:,.0f}", f"Margin: {margin_pct:.1f}%")
    with r2[2]:
        render_kpi_card("Net Incremental Profit", f"₹{res['net_incremental_profit_inr']:,.0f}", "Gross profit minus campaign cost")
    with r2[3]:
        roi_str = f"{res['roi_pct']:.1f}%" if res["roi_pct"] is not None else "N/A"
        cpic_str = (
            f"Cost/Inc. Conv: ₹{res['cost_per_incremental_conversion_inr']:,.0f}"
            if res["cost_per_incremental_conversion_inr"] is not None
            else "Cost/Inc. Conv: N/A"
        )
        render_kpi_card("Estimated Campaign ROI", roi_str, cpic_str)

    # Scenario comparison & Break-even
    st.subheader("2. Scenario Comparison (Conservative · Base · Optimistic)")
    scen_df = simulate_scenarios(
        probabilities=base_probs,
        campaign_budget_inr=budget,
        cost_per_customer_inr=cost_per_cust,
        avg_order_value_inr=aov,
        profit_margin_pct=margin_pct,
        expected_uplift_pct=uplift_pct,
        effectiveness_pct=effectiveness_pct,
        decision_threshold=threshold,
        available_customers=int(avail_customers),
    )

    c_left, c_right = st.columns(2)
    with c_left:
        fig_scen = go.Figure()
        fig_scen.add_trace(go.Bar(name="Incremental Revenue", x=scen_df["Scenario"], y=scen_df["Incremental_Revenue_INR"], marker_color=BLUE))
        fig_scen.add_trace(go.Bar(name="Incremental Gross Profit", x=scen_df["Scenario"], y=scen_df["Incremental_Gross_Profit_INR"], marker_color=TEAL))
        fig_scen.add_trace(go.Bar(name="Net Incremental Profit", x=scen_df["Scenario"], y=scen_df["Net_Incremental_Profit_INR"], marker_color=NAVY))
        fig_scen.update_layout(
            barmode="group",
            title="Revenue, Gross Profit & Net Profit by Uplift Scenario (INR)",
            yaxis_title="INR",
            height=360,
            plot_bgcolor="white",
        )
        st.plotly_chart(fig_scen, width="stretch")

    with c_right:
        sweep_df = threshold_profit_sweep(
            probabilities=base_probs,
            campaign_budget_inr=budget,
            cost_per_customer_inr=cost_per_cust,
            avg_order_value_inr=aov,
            profit_margin_pct=margin_pct,
            expected_uplift_pct=uplift_pct,
            effectiveness_pct=effectiveness_pct,
            available_customers=int(avail_customers),
        )
        fig_thr = px.line(
            sweep_df,
            x="Threshold",
            y=["Net_Incremental_Profit_INR", "Campaign_Cost_INR"],
            markers=True,
            title="Decision Threshold Impact on Net Profit & Campaign Cost (INR)",
            labels={"value": "INR", "variable": "Metric"},
            color_discrete_sequence=[TEAL, "#EA580C"],
        )
        fig_thr.add_vline(x=threshold, line_dash="dash", line_color=NAVY, annotation_text=f"Selected ({threshold:.2f})")
        fig_thr.update_layout(height=360, plot_bgcolor="white")
        st.plotly_chart(fig_thr, width="stretch")

    st.dataframe(scen_df, width="stretch")

    st.subheader("3. Break-Even & Budget Utilization Summary")
    b1, b2 = st.columns(2)
    with b1:
        be = res["breakeven_uplift_pct"]
        if be is not None:
            status_msg = (
                "Above break-even under current scenario assumptions."
                if res["effective_uplift_pct"] >= be
                else "Below break-even — campaign would lose money unless uplift rises or unit cost drops."
            )
            st.markdown(
                f"- **Required Break-Even Effective Uplift:** `{be:.2f}%` percentage points\n"
                f"- **Current Scenario Effective Uplift:** `{res['effective_uplift_pct']:.2f}%` percentage points\n"
                f"- **Status:** {status_msg}"
            )
    with b2:
        util_fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=res["budget_utilization_pct"],
                number={"suffix": "%"},
                title={"text": "Campaign Budget Utilization"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": BLUE},
                    "steps": [
                        {"range": [0, 50], "color": "#DBEAFE"},
                        {"range": [50, 90], "color": "#CCFBF1"},
                        {"range": [90, 100], "color": "#FEF3C7"},
                    ],
                },
            )
        )
        util_fig.update_layout(height=230, margin=dict(t=40, b=10, l=20, r=20))
        st.plotly_chart(util_fig, width="stretch")

    st.caption(
        "Disclaimer: All incremental conversions, revenues, profits, and ROI values above depend on user-supplied "
        "scenario assumptions. Actual campaign lift must be established through randomized controlled A/B testing."
    )
