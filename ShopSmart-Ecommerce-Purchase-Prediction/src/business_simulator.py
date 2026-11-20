"""Phase 8.4 — Campaign & Profitability Business Impact Simulator for ShopSmart.

Clearly separates:
1. Observed model predictions (calibrated purchase probabilities from the saved pipeline).
2. User-defined scenario assumptions (budget, unit cost, AOV, margin, assumed uplift, effectiveness).
3. Derived financial estimates (illustrative scenario projections; NOT proven causal effects).
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def validate_simulator_inputs(
    campaign_budget_inr: float,
    cost_per_customer_inr: float,
    avg_order_value_inr: float,
    profit_margin_pct: float,
    expected_uplift_pct: float,
    effectiveness_pct: float,
    decision_threshold: float,
    available_customers: int,
) -> list[str]:
    """Validate simulator inputs and return a list of human-readable error messages."""
    errors: list[str] = []
    if campaign_budget_inr < 0:
        errors.append("Campaign budget (INR) cannot be negative.")
    if cost_per_customer_inr < 0:
        errors.append("Cost per targeted customer (INR) cannot be negative.")
    if avg_order_value_inr <= 0:
        errors.append("Average order value (INR) must be greater than 0.")
    if not (0.0 < profit_margin_pct <= 100.0):
        errors.append("Profit margin (%) must be between 0 (exclusive) and 100 (inclusive).")
    if not (0.0 <= expected_uplift_pct <= 100.0):
        errors.append("Expected incremental conversion uplift (%) must be between 0 and 100.")
    if not (0.0 <= effectiveness_pct <= 100.0):
        errors.append("Intervention effectiveness (%) must be between 0 and 100.")
    if not (0.05 <= decision_threshold <= 0.95):
        errors.append("Decision threshold must be between 0.05 and 0.95.")
    if available_customers < 0:
        errors.append("Number of available customers cannot be negative.")
    return errors


def simulate_campaign(
    probabilities: np.ndarray | list[float],
    campaign_budget_inr: float,
    cost_per_customer_inr: float,
    avg_order_value_inr: float,
    profit_margin_pct: float,
    expected_uplift_pct: float,
    effectiveness_pct: float = 100.0,
    decision_threshold: float = 0.50,
    available_customers: int | None = None,
) -> dict[str, Any]:
    """Compute scenario-based campaign economics from predicted purchase probabilities.

    Probabilities are treated as observed model predictions; uplift and effectiveness are
    user-defined scenario assumptions that require randomized A/B testing to validate causally.
    """
    probs = np.asarray(probabilities, dtype=float)
    probs = probs[np.isfinite(probs)]
    probs = np.clip(probs, 0.0, 1.0)

    n_avail = len(probs) if available_customers is None else int(available_customers)
    errors = validate_simulator_inputs(
        campaign_budget_inr=campaign_budget_inr,
        cost_per_customer_inr=cost_per_customer_inr,
        avg_order_value_inr=avg_order_value_inr,
        profit_margin_pct=profit_margin_pct,
        expected_uplift_pct=expected_uplift_pct,
        effectiveness_pct=effectiveness_pct,
        decision_threshold=decision_threshold,
        available_customers=n_avail,
    )
    if errors:
        raise ValueError(" | ".join(errors))

    margin_rate = profit_margin_pct / 100.0
    effective_uplift_rate = (expected_uplift_pct / 100.0) * (effectiveness_pct / 100.0)
    gross_profit_per_order = avg_order_value_inr * margin_rate
    breakeven_uplift_pct = (
        (cost_per_customer_inr / gross_profit_per_order) * 100.0
        if gross_profit_per_order > 0
        else None
    )

    if len(probs) == 0 or n_avail == 0:
        return {
            "available_customers": n_avail,
            "model_qualified_customers": 0,
            "customers_selected": 0,
            "budget_capped": False,
            "campaign_expenditure_inr": 0.0,
            "budget_utilization_pct": 0.0,
            "mean_predicted_prob_targeted": 0.0,
            "baseline_conversions": 0.0,
            "incremental_conversions": 0.0,
            "incremental_revenue_inr": 0.0,
            "incremental_gross_profit_inr": 0.0,
            "net_incremental_profit_inr": 0.0,
            "roi_pct": None,
            "cost_per_incremental_conversion_inr": None,
            "breakeven_uplift_pct": round(breakeven_uplift_pct, 4) if breakeven_uplift_pct is not None else None,
            "effective_uplift_pct": round(effective_uplift_rate * 100.0, 4),
        }

    # Model-qualified share & average probability above threshold (scaled cleanly to available_customers)
    qualified_mask = probs >= decision_threshold
    qualified_share = float(qualified_mask.mean())
    model_qualified = int(round(n_avail * qualified_share))

    if cost_per_customer_inr > 0:
        max_affordable = int(math.floor(campaign_budget_inr / cost_per_customer_inr))
    else:
        max_affordable = model_qualified

    customers_selected = min(model_qualified, max_affordable)
    budget_capped = customers_selected < model_qualified

    if customers_selected == 0 or not qualified_mask.any():
        mean_prob_targeted = 0.0
    else:
        # If budget-capped, prioritize highest-probability qualified customers first
        qual_probs = np.sort(probs[qualified_mask])[::-1]
        if budget_capped and model_qualified > 0:
            keep_frac = customers_selected / model_qualified
            keep_k = max(1, int(round(len(qual_probs) * keep_frac)))
            mean_prob_targeted = float(qual_probs[:keep_k].mean())
        else:
            mean_prob_targeted = float(qual_probs.mean())

    campaign_expenditure = customers_selected * cost_per_customer_inr
    budget_utilization = (
        (campaign_expenditure / campaign_budget_inr) * 100.0
        if campaign_budget_inr > 0
        else 0.0
    )

    baseline_conversions = customers_selected * mean_prob_targeted
    # Incremental conversions cannot exceed the remaining non-converting targeted customers
    max_possible_incremental = max(0.0, customers_selected - baseline_conversions)
    incremental_conversions = min(customers_selected * effective_uplift_rate, max_possible_incremental)

    incremental_revenue = incremental_conversions * avg_order_value_inr
    incremental_gross_profit = incremental_revenue * margin_rate
    net_incremental_profit = incremental_gross_profit - campaign_expenditure

    roi_pct = (
        (net_incremental_profit / campaign_expenditure) * 100.0
        if campaign_expenditure > 0
        else None
    )
    cost_per_inc_conv = (
        (campaign_expenditure / incremental_conversions)
        if incremental_conversions > 0
        else None
    )

    return {
        "available_customers": n_avail,
        "model_qualified_customers": model_qualified,
        "customers_selected": customers_selected,
        "budget_capped": budget_capped,
        "campaign_expenditure_inr": round(campaign_expenditure, 2),
        "budget_utilization_pct": round(budget_utilization, 2),
        "mean_predicted_prob_targeted": round(mean_prob_targeted, 4),
        "baseline_conversions": round(baseline_conversions, 2),
        "incremental_conversions": round(incremental_conversions, 2),
        "incremental_revenue_inr": round(incremental_revenue, 2),
        "incremental_gross_profit_inr": round(incremental_gross_profit, 2),
        "net_incremental_profit_inr": round(net_incremental_profit, 2),
        "roi_pct": round(roi_pct, 2) if roi_pct is not None else None,
        "cost_per_incremental_conversion_inr": round(cost_per_inc_conv, 2) if cost_per_inc_conv is not None else None,
        "breakeven_uplift_pct": round(breakeven_uplift_pct, 4) if breakeven_uplift_pct is not None else None,
        "effective_uplift_pct": round(effective_uplift_rate * 100.0, 4),
    }


def simulate_scenarios(
    probabilities: np.ndarray | list[float],
    campaign_budget_inr: float,
    cost_per_customer_inr: float,
    avg_order_value_inr: float,
    profit_margin_pct: float,
    expected_uplift_pct: float,
    effectiveness_pct: float = 100.0,
    decision_threshold: float = 0.50,
    available_customers: int | None = None,
) -> pd.DataFrame:
    """Compare Conservative (0.5x), Base (1.0x), and Optimistic (1.5x) uplift scenarios."""
    rows = []
    for label, mult in [("Conservative (0.5x Uplift)", 0.5), ("Base (1.0x Uplift)", 1.0), ("Optimistic (1.5x Uplift)", 1.5)]:
        uplift_s = min(100.0, expected_uplift_pct * mult)
        res = simulate_campaign(
            probabilities=probabilities,
            campaign_budget_inr=campaign_budget_inr,
            cost_per_customer_inr=cost_per_customer_inr,
            avg_order_value_inr=avg_order_value_inr,
            profit_margin_pct=profit_margin_pct,
            expected_uplift_pct=uplift_s,
            effectiveness_pct=effectiveness_pct,
            decision_threshold=decision_threshold,
            available_customers=available_customers,
        )
        rows.append(
            {
                "Scenario": label,
                "Assumed_Uplift_Pct": round(uplift_s, 2),
                "Customers_Selected": res["customers_selected"],
                "Campaign_Cost_INR": res["campaign_expenditure_inr"],
                "Baseline_Conversions": res["baseline_conversions"],
                "Incremental_Conversions": res["incremental_conversions"],
                "Incremental_Revenue_INR": res["incremental_revenue_inr"],
                "Incremental_Gross_Profit_INR": res["incremental_gross_profit_inr"],
                "Net_Incremental_Profit_INR": res["net_incremental_profit_inr"],
                "ROI_Pct": res["roi_pct"],
            }
        )
    return pd.DataFrame(rows)


def threshold_profit_sweep(
    probabilities: np.ndarray | list[float],
    campaign_budget_inr: float,
    cost_per_customer_inr: float,
    avg_order_value_inr: float,
    profit_margin_pct: float,
    expected_uplift_pct: float,
    effectiveness_pct: float = 100.0,
    available_customers: int | None = None,
    thresholds: list[float] | None = None,
) -> pd.DataFrame:
    """Evaluate derived net profit, ROI, and targeting volume across decision thresholds."""
    grid = thresholds if thresholds is not None else [round(x, 2) for x in np.arange(0.20, 0.90, 0.05)]
    rows = []
    for t in grid:
        res = simulate_campaign(
            probabilities=probabilities,
            campaign_budget_inr=campaign_budget_inr,
            cost_per_customer_inr=cost_per_customer_inr,
            avg_order_value_inr=avg_order_value_inr,
            profit_margin_pct=profit_margin_pct,
            expected_uplift_pct=expected_uplift_pct,
            effectiveness_pct=effectiveness_pct,
            decision_threshold=t,
            available_customers=available_customers,
        )
        rows.append(
            {
                "Threshold": t,
                "Customers_Selected": res["customers_selected"],
                "Campaign_Cost_INR": res["campaign_expenditure_inr"],
                "Incremental_Revenue_INR": res["incremental_revenue_inr"],
                "Net_Incremental_Profit_INR": res["net_incremental_profit_inr"],
                "ROI_Pct": res["roi_pct"],
            }
        )
    return pd.DataFrame(rows)
