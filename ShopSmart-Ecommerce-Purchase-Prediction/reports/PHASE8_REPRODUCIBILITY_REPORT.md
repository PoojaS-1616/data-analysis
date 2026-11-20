# PHASE 8 — REPRODUCIBILITY REPORT & GUIDE
## ShopSmart — E-Commerce Customer Purchase Prediction

**Verified Date:** 2026-11-21  
**Operating System:** Windows 11 (Windows Smart App Control preserved untouched)  
**Python Runtime:** Python `3.14.8` (isolated local `.venv\Scripts\python.exe`)

---

## 1. Verified Dependency Versions (`pip check` = `No broken requirements found.`)

| Package | Verified Version | Purpose |
|---|---:|---|
| `pandas` | `3.1.1` | Tabular data processing |
| `numpy` | `2.5.5` | Numerical arrays & metrics |
| `scikit-learn` | `1.9.1` | Pipelines, Logistic Regression, RF, HistGB, Calibration |
| `scipy` | `1.18.1` | Statistical utilities |
| `matplotlib` | `3.11.2` | Publication diagnostic figures |
| `seaborn` | `0.13.2` | Statistical visualization |
| `joblib` | `1.6.0` | Local pipeline serialization |
| `streamlit` | `1.67.0` | 8-page interactive web platform |
| `plotly` | `7.1.0` | Interactive dashboard charts |
| `pytest` | `9.2.0` | Automated test suite (`16/16` passing) |
| `nbformat` / `nbclient` | `5.11.1` / `0.11.0` | Notebook validation & execution |

---

## 2. Determinism & Random Seeds

- Global split & model seed: `RANDOM_STATE = 42` (`src/config.py`).
- Stratified outer split: `80%` train (`8,000`) / `20%` untouched test (`2,000`), `random_state = 42`.
- Stratified inner split (Phase 8): `80%` inner train (`6,400`) / `20%` validation (`1,600`), `random_state = 42`.
- 5-fold Stratified CV: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`.
- RandomForest (`n_jobs=1`, `random_state=42`) and HistGradientBoosting (`random_state=42`) run deterministically.

---

## 3. Dataset Requirements

Place your authorized local copy of `Ecommerce_Purchase_Prediction_DataSet.csv` at:
`data/raw/Ecommerce_Purchase_Prediction_DataSet.csv`
- Expected shape: `10,000` rows × `19` columns (`0` duplicates).
- Verified SHA-256: `6D8A176EEDA1CCB01840D04F2172457F4E2E83782D079762888B544AA202FF05`.
- Excluded from GitHub via `.gitignore` (`data/raw/*.csv`).

---

## 4. Exact Reproducibility Commands (Windows PowerShell)

```powershell
# 1. Create isolated Python 3.14 environment
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Train primary model & generate historical baseline outputs
.\.venv\Scripts\python.exe src\train_pipeline.py

# 3. Run Phase 8 leakage-safe threshold, calibration, 4-model & subgroup experiments
.\.venv\Scripts\python.exe src\phase8_experiments.py

# 4. Run full automated test suite (16 tests)
.\.venv\Scripts\python.exe -m pytest tests/ -v

# 5. Launch 8-page Streamlit platform
.\.venv\Scripts\python.exe -m streamlit run app\app.py
```
