# PHASE 8 — CHANGELOG
## ShopSmart — E-Commerce Customer Purchase Prediction

**Date:** 2026-11-21  
**Baseline Commit (Historical Reference):** `519d0b7a7ff9ee07ea97bb5a9800a10149d699aa` (Standalone) / `00b1bba2a82adbd3604c8205c0ca186acc75a9e2` (`data-analysis`)

---

## Added
- `src/business_simulator.py`: Pure, validated financial & campaign ROI simulation engine (`validate_simulator_inputs`, `simulate_campaign`, `simulate_scenarios`, `threshold_profit_sweep`).
- `src/phase8_experiments.py`: Reproducible runner for leakage-safe threshold selection (8.1), probability calibration (8.2), 4-model comparison (8.3), and subgroup robustness with minimum-N guardrails (8.5).
- `app/pages/business_impact_simulator.py`: New **Page 8 — Business Impact Simulator** with Deep Navy / White / Blue visual identity, 8 validated user inputs, 10 derived financial metrics, Conservative/Base/Optimistic scenario comparison, threshold profit sweep, budget utilization gauge, and non-causal A/B testing disclaimers.
- `tests/test_phase8.py`: `7` new automated tests covering threshold selection, calibration diagnostics, model comparison integrity, simulator math & edge cases (zero budget, zero selected, negative costs, extreme values), subgroup min-N guardrails, and full 8-page Streamlit `AppTest` navigation.
- `outputs/phase8/`:
  - `phase8_summary.json`
  - `calibration/` (`4` PNG diagnostic charts)
  - `model_comparison/` (`model_comparison.csv` + `4` PNG charts)
  - `robustness/` (`subgroup_metrics.csv` + `2` PNG charts)
- `reports/`:
  - `PHASE8_THRESHOLD_SELECTION_REPORT.md`
  - `PHASE8_CALIBRATION_REPORT.md`
  - `PHASE8_MODEL_COMPARISON_REPORT.md`
  - `PHASE8_ROBUSTNESS_REPORT.md`
  - `PHASE8_REPRODUCIBILITY_REPORT.md`
  - `PHASE8_CHANGELOG.md`
  - `PHASE8_FINAL_QA_REPORT.md`

## Changed
- `app/app.py`: Registered `8. Business Impact Simulator` in sidebar navigation (all 7 original pages preserved untouched).
- `app/pages/model_info.py`: Added `Evaluation Date` and explicit `Selected Features (17 Inputs)` metadata rows.
- `README.md`: Upgraded with Mermaid architecture diagram, 4-model comparison summary, calibration summary, leakage-safe threshold summary, subgroup robustness summary, Page 8 simulator documentation, `16/16` pytest badge, and links to all Phase 8 reports.

## Preserved Untouched
- Existing `models/logistic_regression_pipeline.joblib` (SHA-256 unchanged).
- Existing `outputs/metrics_summary.json` and `reports/MODEL_VALIDATION_REPORT.md` (historical baseline preserved).
- Existing `tests/test_pipeline.py` and `tests/test_app_predictions.py` (`9/9` still passing).
- All 4 other project folders in `data-analysis/` untouched.
