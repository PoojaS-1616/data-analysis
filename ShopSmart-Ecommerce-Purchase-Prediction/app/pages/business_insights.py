"""Page 6: Business Insights — Model Drivers, Odds Ratios & Non-Causal Interpretation."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components import BLUE, TEAL, render_header
from app.utils import FIGURES_DIR, load_metrics


def render() -> None:
    render_header(
        "Business Insights",
        "Purchase-Associated Drivers, Standardized Odds Ratios & Marketing Intent Opportunities",
    )

    metrics = load_metrics()
    pos_df = pd.DataFrame(metrics["top_positive_drivers"])
    neg_df = pd.DataFrame(metrics["top_negative_drivers"])
    drivers = pd.concat([pos_df, neg_df], ignore_index=True).sort_values("coefficient")
    drivers["Direction"] = drivers["coefficient"].apply(lambda x: "Positive Association" if x > 0 else "Negative Association")

    st.markdown(
        """
        <div class="callout-info">
            <b>Association vs. Causation:</b> Logistic Regression coefficients quantify conditional statistical
            associations in historical cart sessions—they do <b>not</b> prove that changing a feature will causally
            increase sales. Validate campaign interventions with controlled A/B experiments.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([3, 2])
    with c1:
        fig = px.bar(
            drivers,
            x="coefficient",
            y="feature",
            orientation="h",
            color="Direction",
            color_discrete_map={"Positive Association": BLUE, "Negative Association": "#DC2626"},
            title="Top Standardized Log-Odds Coefficients (Primary Model)",
            labels={"coefficient": "Log-Odds Coefficient", "feature": "Feature"},
            hover_data=["odds_ratio"],
        )
        fig.update_layout(height=420, plot_bgcolor="white")
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Coefficient & Odds Ratio Table")
        st.dataframe(
            drivers[["feature", "coefficient", "odds_ratio"]].sort_values("odds_ratio", ascending=False),
            width="stretch",
            height=380,
        )

    st.subheader("Marketing Intent Segments & Experiment Opportunities")
    seg_table = pd.DataFrame(
        [
            {
                "Intent Segment": "High Intent (>= 0.75)",
                "Typical Profile": "Multi-item carts, Premium tier, higher session engagement",
                "Suggested Experiment": "Frictionless checkout reminder; test removing blanket promo codes to protect margin.",
            },
            {
                "Intent Segment": "Medium Intent (0.50 – 0.74)",
                "Typical Profile": "Moderate cart size & session engagement",
                "Suggested Experiment": "A/B test free-shipping threshold cues or subtle cart-abandonment nudges.",
            },
            {
                "Intent Segment": "Low-Medium Intent (0.30 – 0.49)",
                "Typical Profile": "Smaller carts, mobile or social traffic",
                "Suggested Experiment": "Test social proof, shipping transparency, or targeted email follow-up.",
            },
            {
                "Intent Segment": "Low Intent (< 0.30)",
                "Typical Profile": "Minimal cart depth, low engagement",
                "Suggested Experiment": "Cap paid retargeting spend and prioritize organic/low-cost channels.",
            },
        ]
    )
    st.dataframe(seg_table, width="stretch")

    lift_img = FIGURES_DIR / "04_threshold_tradeoff_and_lift.png"
    if lift_img.exists():
        st.image(str(lift_img), caption="Saved Threshold Trade-Off & Predicted Probability Decile Lift", width="stretch")
