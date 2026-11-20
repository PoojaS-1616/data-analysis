# ShopSmart — First-Time User Quickstart Guide (Windows PowerShell)

Follow these 11 steps to clone, configure, train, test, and run **ShopSmart — Purchase Intelligence Platform** locally using an isolated **Python 3.14** virtual environment.

---

## 1. Prerequisites
- **Windows 10/11** with PowerShell
- **Official signed Python 3.14** (`py -3.14 --version` — verified on `Python 3.14.8`)
- **Git** (`git --version`)
- An authorized local copy of `Ecommerce_Purchase_Prediction_DataSet.csv` (`10,000` rows × `19` columns)

> **Windows Smart App Control Note:** Do **not** use pre-release Python builds (such as Python 3.15), which can trigger Windows Application Control blocks on compiled `pandas` extensions. Always use an official signed Python `3.14` release inside a local `.venv`.

## 2. Clone the Repository
```powershell
git clone https://github.com/PoojaS-1616/data-analysis.git
```

## 3. Navigate to the ShopSmart Project Folder
```powershell
Set-Location data-analysis\ShopSmart-Ecommerce-Purchase-Prediction
```

## 4. Create an Isolated Python 3.14 Virtual Environment
```powershell
py -3.14 -m venv .venv
```

## 5. Install Dependencies
```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```
Expected `pip check` output: `No broken requirements found.`

## 6. Place Your Authorized Local Dataset Copy
Because upstream dataset provenance and redistribution rights are unverified (see [DATA_PROVENANCE.md](../DATA_PROVENANCE.md)), the raw CSV is excluded from GitHub. Create `data\raw\` and place your local CSV at:
```text
data/raw/Ecommerce_Purchase_Prediction_DataSet.csv
```

## 7. Train the Primary Model Artifact
```powershell
.\.venv\Scripts\python.exe src\train_pipeline.py
```
This regenerates `models/logistic_regression_pipeline.joblib`, `outputs/metrics_summary.json`, `outputs/test_set_predictions.csv`, and the 5 baseline charts in `outputs/figures/`.

## 8. Run the Phase 8 Experimental Suite
```powershell
.\.venv\Scripts\python.exe src\phase8_experiments.py
```
This reproduces leakage-safe threshold selection, probability calibration diagnostics, the 4-model benchmark, and subgroup robustness tables/charts under `outputs/phase8/`.

## 9. Launch the 8-Page Streamlit Application
```powershell
.\.venv\Scripts\python.exe -m streamlit run app\app.py
```
Open the local URL displayed in PowerShell (typically `http://localhost:8501`). Press `Ctrl+C` in PowerShell to stop the server cleanly.

## 10. Run the Automated Test Suite (`16` Tests)
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```
All `16` tests across `test_pipeline.py`, `test_app_predictions.py`, and `test_phase8.py` should pass.

## 11. Troubleshooting Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| `FileNotFoundError: Saved model not found` | Local `.joblib` is gitignored and not yet trained | Run `.\.venv\Scripts\python.exe src\train_pipeline.py` after placing `data/raw/Ecommerce_Purchase_Prediction_DataSet.csv`. |
| Windows Application Control / DLL load failure on `import pandas` | Global Python `3.15` pre-release invoked instead of `.venv` | Invoke `.\.venv\Scripts\python.exe` explicitly (never bare `python`). |
| PowerShell `Activate.ps1` execution policy blocked | Restricted PowerShell script policy | Do not weaken execution policy; call `.\.venv\Scripts\python.exe` directly as shown above. |
| `ModuleNotFoundError: No module named 'src'` | Running scripts from outside project root | Run commands from `ShopSmart-Ecommerce-Purchase-Prediction\` root directory. |
