# ShopSmart — Two-Minute Project Summary

## 1. Business Problem
E-commerce marketing teams often waste promotional margin discounting high-intent carts that would convert anyway, while missing persuadable mid-intent shoppers. **ShopSmart** estimates **cart-stage / pre-checkout purchase probability** and links model scores to budget-aware campaign ROI scenarios.

## 2. Technical Solution
Built an end-to-end, leak-free Python ML pipeline (`src/`) paired with an **8-page interactive Streamlit platform** (`app/`) supporting executive KPI monitoring, cohort exploration, single-customer scoring, validated in-memory batch CSV scoring, and interactive ROI simulation.

## 3. Dataset and Features
- `10,000` customer sessions × `19` columns (`64.80%` purchase rate; `0` duplicates; `2,514` missing values imputed inside the pipeline).
- `17` model inputs across demographics, browsing behavior, active cart metrics (`Cart_Items`, `Cart_Value_INR`, `Discount_Percent`), and account history. `Customer_ID` is dropped prior to modeling; raw CSV is excluded from GitHub due to unverified redistribution rights.

## 4. Machine-Learning Approach
- Preserved an untouched `2,000`-row held-out test set while splitting the `8,000` training rows into `6,400` train / `1,600` validation for leakage-safe threshold selection, calibration comparison, and model benchmarking (`random_state = 42`).
- Empirically validated training-fold IQR Winsorisation (`k = 1.5`, `+0.0339` Test ROC-AUC vs. raw) and audited feature-timing leakage (`Payment_Method` non-leaking; cart features drive `+0.0714` Test ROC-AUC, defining active-cart scope).

## 5. Evaluation Results (Offline Held-Out Test, `n = 2,000`)
- **Selected Model (L2 Logistic Regression, `C = 1.0`):** `ROC-AUC = 0.7411`, `PR-AUC = 0.8388`, `Accuracy = 0.7045`, `F1 = 0.7921`, `Log-Loss = 0.5594`, `Brier = 0.1903`, `ECE = 0.0236`.
- **4-Model Benchmark:** Logistic Regression (`0.7405` at val-tuned `C = 0.1`) outperformed Random Forest (`0.7344`, `ECE = 0.0603`), HistGradientBoosting (`0.7302`), and DummyClassifier (`0.5000`) on discrimination, calibration, speed (`15.5 ms`), and interpretability.
- **Subgroup Robustness:** Consistent `0.7007–0.7693` ROC-AUC across `15` valid subgroups (`n >= 50`), with `5` small slices suppressed cleanly.

## 6. Business Impact Simulator
Page 8 translates predicted probabilities into budget-capped targeting volume, baseline conversions, scenario-based incremental conversions, net profit, ROI, and break-even uplift across Conservative (`0.5x`), Base (`1.0x`), and Optimistic (`1.5x`) uplift assumptions — explicitly labeled non-causal pending A/B testing.

## 7. Engineering Highlights
- Custom leak-free `IQRCapper` scikit-learn transformer; `@st.cache_resource` inference (zero retraining on launch); in-memory batch CSV validation; `16/16` passing `pytest` + Streamlit `AppTest` tests; clean `.gitignore` governance.

## 8. Limitations
- Strictly cart-stage / pre-checkout (not landing-page prediction); offline historical evaluation only (no live production deployment or causal A/B validation yet); dataset redistribution rights unverified.

## 9. What I Learned
- Why simpler, well-regularized linear models can beat tree ensembles on both discrimination and calibration once right-tail outliers are handled properly.
- Why selecting thresholds or calibration methods on the final test set introduces subtle leakage, and why highest F1 is rarely the optimal business operating point under constrained campaign budgets.
