"""Page 2: Customer Analytics — Interactive Exploration of Behavioral & Profile Features."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components import BLUE, NAVY, TEAL, render_header
from app.utils import load_raw_dataset

CAT_EXPLORE = ["Membership_Type", "Device_Type", "Traffic_Source", "Gender", "Payment_Method"]
NUM_EXPLORE = [
    "Age",
    "Session_Duration_Min",
    "Pages_Viewed",
    "Products_Viewed",
    "Cart_Items",
    "Cart_Value_INR",
    "Discount_Percent",
    "Previous_Orders",
    "Days_Since_Last_Visit",
    "Email_Open_Rate",
    "Customer_Rating",
    "Returns_Last_Year",
]


def render() -> None:
    render_header(
        "Customer Analytics",
        "Interactive Exploration of Observed Customer Profile, Session, Cart & Purchase Patterns",
    )

    df = load_raw_dataset()
    if df is None:
        st.warning(
            "Local dataset `data/raw/Ecommerce_Purchase_Prediction_DataSet.csv` is not present. "
            "Place your authorized local CSV in `data/raw/` to enable interactive dataset exploration."
        )
        return

    st.caption(
        "Note: Geographic `Location` is not a column in the source schema (`19` columns). "
        "All available profile, session, cart, and behavioral features are interactive below."
    )

    with st.expander("Interactive Cohort Filters", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        genders = sorted(df["Gender"].dropna().unique().tolist())
        memberships = sorted(df["Membership_Type"].dropna().unique().tolist())
        devices = sorted(df["Device_Type"].dropna().unique().tolist())
        sources = sorted(df["Traffic_Source"].dropna().unique().tolist())

        sel_gender = fc1.multiselect("Gender", genders, default=genders)
        sel_mem = fc2.multiselect("Membership Type", memberships, default=memberships)
        sel_dev = fc3.multiselect("Device Type", devices, default=devices)
        sel_src = fc4.multiselect("Traffic Source", sources, default=sources)

        age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
        age_range = st.slider("Age Range", age_min, age_max, (age_min, age_max))

    gender_mask = (
        (df["Gender"].isin(sel_gender) | df["Gender"].isna())
        if sel_gender
        else pd.Series(False, index=df.index)
    )
    filtered = df[
        gender_mask
        & (df["Membership_Type"].isin(sel_mem) | df["Membership_Type"].isna())
        & (df["Device_Type"].isin(sel_dev) | df["Device_Type"].isna())
        & (df["Traffic_Source"].isin(sel_src) | df["Traffic_Source"].isna())
        & ((df["Age"].between(age_range[0], age_range[1])) | df["Age"].isna())
    ]

    if filtered.empty:
        st.info("No customer records match the selected filters. Broaden filter criteria to inspect analytics.")
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filtered Sessions", f"{len(filtered):,}", f"{len(filtered)/len(df)*100:.1f}% of dataset")
    m2.metric("Observed Purchase Rate", f"{filtered['Purchase'].mean()*100:.2f}%")
    m3.metric("Median Cart Value (INR)", f"{filtered['Cart_Value_INR'].median():,.0f}")
    m4.metric("Mean Cart Items", f"{filtered['Cart_Items'].mean():.2f}")

    c_left, c_right = st.columns(2)
    with c_left:
        cat_col = st.selectbox("Categorical Dimension (Conversion Rate)", CAT_EXPLORE, index=0)
        cat_agg = (
            filtered.dropna(subset=[cat_col])
            .groupby(cat_col, as_index=False)
            .agg(Sessions=("Purchase", "count"), Purchase_Rate=("Purchase", "mean"))
        )
        cat_agg["Purchase_Rate_Pct"] = (cat_agg["Purchase_Rate"] * 100).round(2)
        fig_cat = px.bar(
            cat_agg.sort_values("Purchase_Rate_Pct", ascending=False),
            x=cat_col,
            y="Purchase_Rate_Pct",
            text="Purchase_Rate_Pct",
            color_discrete_sequence=[BLUE],
            title=f"Observed Purchase Rate (%) by {cat_col.replace('_', ' ')}",
            labels={"Purchase_Rate_Pct": "Purchase Rate (%)"},
            hover_data=["Sessions"],
        )
        fig_cat.update_layout(height=360, plot_bgcolor="white")
        st.plotly_chart(fig_cat, width="stretch")

    with c_right:
        num_col = st.selectbox("Numeric Feature Distribution by Purchase", NUM_EXPLORE, index=4)
        plot_df = filtered[[num_col, "Purchase"]].dropna().copy()
        plot_df["Outcome"] = plot_df["Purchase"].map({0: "No Purchase (0)", 1: "Purchase (1)"})
        # Clip top 1% visually for readability of right-tail spike columns while noting it clearly
        p99 = float(plot_df[num_col].quantile(0.99))
        clipped = plot_df[plot_df[num_col] <= p99]
        fig_num = px.box(
            clipped,
            x="Outcome",
            y=num_col,
            color="Outcome",
            color_discrete_map={"No Purchase (0)": "#EA580C", "Purchase (1)": TEAL},
            title=f"{num_col.replace('_', ' ')} by Purchase Outcome (<= 99th pct)",
        )
        fig_num.update_layout(height=360, showlegend=False, plot_bgcolor="white")
        st.plotly_chart(fig_num, width="stretch")

    st.subheader("Cart Items vs. Observed Conversion Rate")
    cart_agg = (
        filtered.groupby("Cart_Items", as_index=False)
        .agg(Sessions=("Purchase", "count"), Purchase_Rate=("Purchase", "mean"))
    )
    cart_agg["Purchase_Rate_Pct"] = (cart_agg["Purchase_Rate"] * 100).round(2)
    fig_cart = px.line(
        cart_agg,
        x="Cart_Items",
        y="Purchase_Rate_Pct",
        markers=True,
        color_discrete_sequence=[NAVY],
        title="Observed Purchase Rate (%) Across Cart Item Counts",
        labels={"Purchase_Rate_Pct": "Observed Purchase Rate (%)", "Cart_Items": "Cart Items"},
        hover_data=["Sessions"],
    )
    fig_cart.update_layout(height=300, plot_bgcolor="white")
    st.plotly_chart(fig_cart, width="stretch")
