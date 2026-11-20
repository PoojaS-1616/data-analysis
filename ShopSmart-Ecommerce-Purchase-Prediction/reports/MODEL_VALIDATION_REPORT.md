# Model Validation & Technical Audit Report
## E-Commerce Customer Purchase Prediction (Logistic Regression)

**Validation Date:** 2026-11-21  
**Verified Environment:** Windows 11 · Python `3.14.8` (`.venv\Scripts\python.exe`) · `scikit-learn` · `pandas` · `pytest`  
**Source Metrics Artifact:** `outputs/metrics_summary.json`

---

## 1. Dataset & Split Integrity

- **Dimensions:** `10,000` rows × `19` columns (`0` exact duplicates, `10,000` unique `Customer_ID` dropped prior to modeling).
- **Target (`Purchase`):** `Purchase = 1`: `6,480` (`64.80%`); `Purchase = 0`: `3,520` (`35.20%`).
- **Missing Values:** `2,514` nulls across `11` columns — imputed strictly inside `ColumnTransformer` (median for numeric, mode for categorical, fit on training folds only).
- **Split:** Stratified 80/20 split (`8,000` train / `2,000` held-out test, `random_state = 42`).

---

## 2. Primary Model Performance (`LogisticRegression`, L2, `C = 1.0`, IQR `k = 1.5`)

| Split / Evaluation | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Log-Loss | Brier Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Train (`n = 8,000`, t=0.50)** | `0.7009` | `0.7267` | `0.8630` | `0.7890` | `0.7320` | `0.8264` | `0.5678` | `0.1932` |
| **5-Fold Stratified CV (Mean)** | `0.6983` | — | — | `0.7868` | `0.7281` (±`0.0071`) | `0.8236` | `0.5706` | — |
| **Held-Out Test (`n = 2,000`, t=0.50)** | **`0.7045`** | **`0.7279`** | **`0.8688`** | **`0.7921`** | **`0.7411`** | **`0.8388`** | **`0.5594`** | **`0.1903`** |

- **Confusion Matrix (Test, `t = 0.50`):** `TN = 283` · `FP = 421` · `FN = 170` · `TP = 1,126` (`1,409 / 2,000` correct).
- **Generalization:** Zero overfitting — held-out Test ROC-AUC (`0.7411`) and Log-Loss (`0.5594`) track 5-fold CV (`0.7281 ± 0.0071`, `0.5706`) closely.
- **Calibration:** Brier Score `0.1903` (below naive base-rate Brier `0.648 × 0.352 = 0.2281`), indicating well-calibrated probabilities suitable for probability-tiered marketing segmentation.

---

## 3. Empirical IQR Outlier Treatment Validation (Ablation Study)

Rather than applying Winsorisation blindly, three preprocessing configurations were evaluated on identical 5-fold CV folds and the held-out test split:

| Variant | 5-Fold CV ROC-AUC | Test ROC-AUC | Test PR-AUC | Test Log-Loss | Test Brier | Test Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| **`iqr_capped_k1.5` (Selected)** | **`0.7281 ± 0.0071`** | **`0.7411`** | **`0.8388`** | **`0.5594`** | **`0.1903`** | **`0.7045`** |
| `iqr_capped_k3.0` (Extreme-only) | `0.7279 ± 0.0071` | `0.7384` | `0.8359` | `0.5615` | `0.1911` | `0.7040` |
| `uncapped_raw` (No capping) | `0.7033 ± 0.0077` | `0.7072` | `0.7994` | `0.5927` | `0.2012` | `0.6920` |

**Finding:** Training-fold IQR capping (`k = 1.5`) on the 5 spike-affected continuous features (`Session_Duration_Min`, `Pages_Viewed`, `Cart_Value_INR`, `Discount_Percent`, `Days_Since_Last_Visit`) improves CV ROC-AUC by **`+0.0248`**, Test ROC-AUC by **`+0.0339`**, PR-AUC by **`+0.0394`**, and reduces Log-Loss by **`-0.0333`**. Extreme right-tail spikes distort standardized linear slopes; Winsorisation is empirically justified.

---

## 4. Feature Leakage & Prediction-Time Availability Audit

To verify whether checkout-stage variables introduce target leakage or restrict deployment timing, three realistic prediction-time feature sets were evaluated:

| Feature Stage | Features Included | 5-Fold CV ROC-AUC | Test ROC-AUC | Test Accuracy | Test F1 |
|---|---|---:|---:|---:|---:|
| **Full Checkout (`17` features)** | All behavioral, demographic, cart & `Payment_Method` | `0.7281` | `0.7411` | `0.7045` | `0.7921` |
| **Pre-Payment (`16` features)** | Excludes `Payment_Method` | **`0.7290`** | `0.7409` | `0.7030` | `0.7914` |
| **Pre-Cart Browsing (`13` features)** | Excludes `Payment_Method`, `Cart_Items`, `Cart_Value_INR`, `Discount_Percent` | `0.6444` | `0.6697` | `0.6780` | `0.7898` |

**Findings:**
1. **No `Payment_Method` Leakage:** Dropping `Payment_Method` changes Test ROC-AUC by only `-0.0002` (and slightly improves CV ROC-AUC from `0.7281` to `0.7290`). `Payment_Method` does not leak post-checkout outcomes.
2. **Cart-Stage Dependency (`+0.0714` Test ROC-AUC):** `Cart_Items` (`OR = 1.84`) and `Cart_Value_INR` (`OR = 1.50`) drive a substantial share of discriminative lift. In production, the full 17-feature model must be scored **at cart / pre-checkout** (once cart contents exist); landing-page scoring requires the 13-feature pre-cart model (`Test ROC-AUC = 0.6697`).

---

## 5. Top Standardized Log-Odds Drivers & Threshold Trade-Offs

- **Top Positive Drivers:** `Cart_Items` (`coef = +0.6073`, `OR = 1.8355`), `Membership_Type_Premium` (`+0.5395`, `OR = 1.7151`), `Cart_Value_INR` (`+0.4081`, `OR = 1.5039`), `Session_Duration_Min` (`+0.2735`, `OR = 1.3145`), `Pages_Viewed` (`+0.2622`, `OR = 1.2998`), `Products_Viewed` (`+0.2586`, `OR = 1.2951`).
- **Top Negative Drivers (vs. reference categories):** `Traffic_Source_Social Media` (`-0.3502`, `OR = 0.7046`), `Traffic_Source_Organic` (`-0.3259`, `OR = 0.7219`), `Traffic_Source_Referral` (`-0.3219`, `OR = 0.7248`), `Traffic_Source_Paid Ads` (`-0.2554`, `OR = 0.7746`), `Device_Type_Mobile` (`-0.2210`, `OR = 0.8017`).
- **Decision Threshold Trade-Offs (Test `n = 2,000`):**
  - `t = 0.40`: Targets `89.25%` · Recall `95.45%` · Precision `69.30%` · F1 **`80.30%`** (maximum F1 / high-recall nudge).
  - `t = 0.50`: Targets `77.35%` · Recall `86.88%` · Precision `72.79%` · Accuracy **`70.45%`**.
  - `t = 0.75`: Targets `34.35%` · Recall `45.14%` · Precision **`85.15%`** (high-precision VIP targeting).

---

## 6. Automated Validation & Reproducibility Results

- **`pytest tests/test_pipeline.py -v`:** **`4 / 4` PASSED** (`test_dataset_schema_and_balance`, `test_iqr_capper_no_leakage`, `test_saved_model_and_reproducibility`, `test_pipeline_handles_missing_and_unseen_categories`).
- **Canonical 32-Cell Notebook Execution (`notebooks/ecommerce_purchase_prediction.ipynb`):** Executed cleanly top-to-bottom under Python `3.14.8` `.venv` (`32` cells, `20` code cells, **`0` error outputs**).
