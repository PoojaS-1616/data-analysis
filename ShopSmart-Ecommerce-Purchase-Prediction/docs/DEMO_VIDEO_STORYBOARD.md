# ShopSmart — 2–3 Minute Demo Video Storyboard

> **Status:** Storyboard prepared for recording. No video has been recorded or published yet.

| Time | Segment | On-Screen Visual | Key Talking Points |
|---|---|---|---|
| **0:00 – 0:20** | **Business Problem & Overview** | GitHub README Hero & Page 1 (`01_executive_overview.png`) | Introduce ShopSmart: predicting **cart-stage / pre-checkout** purchase intent across 10,000 sessions so CRM teams target persuadable carts without eroding margin on high-intent buyers. |
| **0:20 – 0:45** | **Dataset & Architecture** | Mermaid Architecture Diagram & Page 7 (`07_model_information.png`) | Walk through the 17 features, leak-free `ColumnTransformer` (`IQRCapper` + scaling + OHE), strict `6,400 / 1,600 / 2,000` split, and why raw CSVs stay excluded from GitHub (`DATA_PROVENANCE.md`). |
| **0:45 – 1:15** | **Model Performance, Calibration & Thresholds** | Page 3 (`03_model_performance.png`), `01_model_comparison_bar.png`, `01_reliability_diagram.png` | Show Logistic Regression beating Random Forest and HistGradientBoosting on ROC-AUC (`0.7411`), Brier (`0.1903`), speed, and native calibration; contrast F1-optimal (`t=0.40`) vs. High-Precision (`t=0.67`). |
| **1:15 – 1:50** | **Single Customer Prediction** | Page 4 (`04_single_prediction.png`) | Adjust active cart inputs (`Cart_Items`, `Membership_Type`, `Cart_Value_INR`), click **Estimate Purchase Intent**, and show live probability gauge (`78.36%`), intent band, and non-guarantee disclaimer. |
| **1:50 – 2:25** | **Business Impact Simulator** | Page 8 (`08_business_impact_simulator.png`) | Adjust campaign budget, outreach cost, AOV, margin, and threshold; walk through Conservative/Base/Optimistic ROI scenarios and break-even uplift — stressing that uplift requires A/B testing. |
| **2:25 – 2:50** | **Testing, Limitations & Wrap-Up** | PowerShell `pytest tests/ -v` (`16/16` passed) & GitHub repo | Highlight automated `AppTest` + simulator edge-case tests, subgroup `min_n=50` guardrails, honest limitations, and quickstart reproducibility. |
