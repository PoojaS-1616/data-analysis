# ShopSmart — Automated Application & Prediction Test Results

**Test Date:** 2026-11-21  
**Python Environment:** `.venv\Scripts\python.exe` (`Python 3.14.8`)  
**Framework Versions:** `Streamlit 1.67.0` · `Plotly 7.1.0` · `pytest 9.2.0`  
**Overall Result:** **`9 / 9` PASSED** (`4.79s`) + Live Streamlit Health Check **`HTTP 200 (ok)`**

---

## Automated Test Matrix (`pytest tests/ -v`)

| # | Test Case | Scope Verified | Status |
|---|---|---|---|
| 1 | `test_single_customer_prediction_outputs` | Probability bounds `[0, 1]`, class consistency (`>= 0.50`), marketing segment, recommended campaign action | **PASS** |
| 2 | `test_single_customer_missing_feature_raises` | Explicit `ValueError` raised when required cart/profile features are missing | **PASS** |
| 3 | `test_batch_validation_missing_columns_and_bad_types` | Rejects empty CSV, missing required columns, and non-numeric values in numeric columns | **PASS** |
| 4 | `test_batch_validation_warnings_and_scoring_export` | Warns cleanly on missing values, unseen categories, and duplicate `Customer_ID`s; scores in memory; generates valid CSV export bytes | **PASS** |
| 5 | `test_streamlit_all_seven_pages_and_single_prediction_form` | `AppTest` loads `app/app.py` without retraining, navigates across all **7** pages with `0` exceptions, submits Single Customer Prediction form and verifies campaign action output | **PASS** |
| 6 | `test_dataset_schema_and_balance` | Verifies `10,000 × 19` schema, `0` duplicates, `6,480` (`64.80%`) positive target | **PASS** |
| 7 | `test_iqr_capper_no_leakage` | Verifies `IQRCapper` learns bounds strictly from training array | **PASS** |
| 8 | `test_saved_model_and_reproducibility` | Verifies saved `joblib` pipeline determinism and metric thresholds | **PASS** |
| 9 | `test_pipeline_handles_missing_and_unseen_categories` | Verifies finite probabilities on missing numeric values & unseen categorical levels | **PASS** |

## Live Server & Screenshot Check

- **Live Streamlit Server Launch (`--server.headless true`):** **PASS** — `/_stcore/health` returned `HTTP 200 (ok)`.
- **Headless Browser Screenshot Capture:** **BLOCKED (Non-Interactive Session)** — `msedge.exe --headless=new --screenshot` did not produce a PNG in the non-interactive Windows session. Zero screenshots were fabricated.
