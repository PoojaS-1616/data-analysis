"""Reusable UI components and Deep Navy / White / Blue visual identity for ShopSmart."""

from __future__ import annotations

import streamlit as st

NAVY = "#0F2942"
BLUE = "#1D4ED8"
TEAL = "#0D9488"
SLATE = "#475569"
SURFACE = "#F8FAFC"


def inject_theme_css() -> None:
    """Apply clean Deep Navy & White visual styling with restrained blue accents."""
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #F8FAFC;
                color: #0F172A;
            }
            section[data-testid="stSidebar"] {
                background-color: #0F2942;
                color: #F8FAFC;
            }
            section[data-testid="stSidebar"] * {
                color: #F8FAFC !important;
            }
            section[data-testid="stSidebar"] .stRadio label {
                padding: 4px 2px;
                font-weight: 500;
            }
            .shopsmart-banner {
                background: linear-gradient(90deg, #0F2942 0%, #1E3A5F 100%);
                color: #FFFFFF;
                padding: 18px 24px;
                border-radius: 10px;
                margin-bottom: 18px;
                border-left: 6px solid #2563EB;
            }
            .shopsmart-banner h1 {
                margin: 0;
                font-size: 1.55rem;
                color: #FFFFFF !important;
                font-weight: 700;
            }
            .shopsmart-banner p {
                margin: 4px 0 0 0;
                font-size: 0.92rem;
                color: #CBD5E1 !important;
            }
            .kpi-card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-top: 4px solid #1D4ED8;
                border-radius: 8px;
                padding: 14px 16px;
                margin-bottom: 8px;
            }
            .kpi-label {
                font-size: 0.80rem;
                color: #475569;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.03em;
            }
            .kpi-value {
                font-size: 1.65rem;
                font-weight: 700;
                color: #0F2942;
                margin-top: 4px;
            }
            .kpi-sub {
                font-size: 0.78rem;
                color: #64748B;
                margin-top: 2px;
            }
            .callout-info {
                background-color: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-left: 5px solid #1D4ED8;
                border-radius: 8px;
                padding: 12px 16px;
                margin: 10px 0 16px 0;
                color: #1E3A8A;
                font-size: 0.92rem;
            }
            .callout-warn {
                background-color: #FFFBEB;
                border: 1px solid #FDE68A;
                border-left: 5px solid #D97706;
                border-radius: 8px;
                padding: 12px 16px;
                margin: 10px 0 16px 0;
                color: #78350F;
                font-size: 0.92rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="shopsmart-banner">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cart_stage_notice() -> None:
    st.markdown(
        """
        <div class="callout-warn">
            <b>Cart-Stage / Pre-Checkout Intent Model:</b> Predictions rely on active cart features
            (<code>Cart_Items</code>, <code>Cart_Value_INR</code>, <code>Discount_Percent</code>) alongside session
            and profile attributes. Outputs are <b>probabilistic estimates, not purchase guarantees</b>, and are not
            designed for pre-shopping / landing-page prediction.
        </div>
        """,
        unsafe_allow_html=True,
    )
