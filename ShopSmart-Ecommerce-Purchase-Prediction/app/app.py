"""
ShopSmart — Purchase Intelligence Platform
==========================================
Main Streamlit entry point for the E-Commerce Customer Purchase Prediction portfolio project.
Loads the pre-trained scikit-learn Logistic Regression pipeline from models/ without retraining.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.components import inject_theme_css
from app.pages import (
    batch_prediction,
    business_insights,
    customer_analytics,
    executive_overview,
    model_info,
    model_performance,
    single_prediction,
)
from app.utils import MODEL_VERSION, load_metrics, load_model

st.set_page_config(
    page_title="ShopSmart — Purchase Intelligence Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme_css()

PAGES = {
    "1. Executive Overview": executive_overview.render,
    "2. Customer Analytics": customer_analytics.render,
    "3. Model Performance": model_performance.render,
    "4. Single Customer Prediction": single_prediction.render,
    "5. Batch Prediction": batch_prediction.render,
    "6. Business Insights": business_insights.render,
    "7. Model Information": model_info.render,
}

with st.sidebar:
    st.markdown("## ShopSmart")
    st.caption("Purchase Intelligence Platform")
    st.markdown("---")
    selected_page = st.radio("Navigation", list(PAGES.keys()), index=0)
    st.markdown("---")
    st.caption(f"**Model:** {MODEL_VERSION}")
    st.caption("**Scope:** Cart-Stage / Pre-Checkout Intent")
    st.caption("**Privacy:** In-memory scoring only; uploaded files are never saved.")

# Verify saved model and metrics are available before rendering
try:
    load_model()
    load_metrics()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

PAGES[selected_page]()

st.markdown("---")
st.caption("ShopSmart — Purchase Intelligence Platform  ·  Cart-Stage Logistic Regression Portfolio Project  ·  Probabilistic Estimates Only")
