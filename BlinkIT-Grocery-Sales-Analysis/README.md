# 🛒 BlinkIT Grocery Pricing & Catalogue Architecture Analysis

![Project](https://img.shields.io/badge/Project-Data%20Analytics-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![SQLite](https://img.shields.io/badge/SQL-Star%20Schema-003B57?style=for-the-badge&logo=sqlite)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20App-FF4B4B?style=for-the-badge&logo=streamlit)

**An end-to-end Python, SQL (SQLite Star Schema), and Streamlit analytics project examining product pricing structure, store-format assortment breadth, Simpson's Paradox confounding, and SKU-level variance decomposition across 8,523 product-outlet catalogue records.**

> **Transparency & Units Notice:** Currency units are **not specified** in the source dataset, so all values are reported in original dataset units without currency conversion. Variance decomposition ($R^2 = 99.97\%$) demonstrates that the `Sales` field behaves like a **SKU-level unit price / catalogue value**, not verified transaction revenue. See [Data Provenance & Limitations](#-data-provenance--limitations) below.

---

## 🖥️ Live Streamlit Dashboard Preview

![BlinkIT Catalogue Pricing & Assortment Explorer](./dashboard_live_screenshot.png)

---

## 📊 Dataset at a Glance

| Metric | Verified Value |
|---|---:|
| Product-outlet records | `8,523` (`0` nulls, `0` duplicates) |
| Unique SKUs (`Item Identifier`) | `1,559` |
| Outlets (`Outlet Identifier`) | `10` (`8` Supermarkets · `2` Grocery Stores) |
| Product categories (`Item Type`) | `16` |
| Sum of Recorded `Sales` Metric | `1,201,681.49` *(dataset units)* |
| Mean / Median Recorded `Sales` Value | `140.99` / `143.01` *(min `31.29`, max `266.89`, SD `62.28`)* |
| Average Rating | `3.97 / 5` (`39.18%` rated exactly `4.0`) |

---

## 🔍 Key Analytical Findings

1. **Variance Decomposition — `Sales` Is SKU-Driven ($R^2 = 99.97\%$):** One-way ANOVA decomposition shows `Item Identifier` alone explains **99.97%** of the variance in `Sales` (Adjusted $R^2 = 0.9996$; average within-SKU SD = `1.15` vs `62.28` overall; max cross-store spread = `4.00`). Outlet identity explains only `0.03%`. Store-level sums of `Sales` therefore track **assortment breadth (SKU count)** rather than demand velocity.
2. **Store-Format Composition Audit (Simpson's Paradox):** Naive tier averages make Tier 2 (`131,050` per store) appear ahead of Tier 1 (`112,133`) and Tier 3 (`118,033`). Controlling for store format (Supermarkets only) collapses the tier spread to **0.2%** (`Tier 1: 131,295`, `Tier 2: 131,050`, `Tier 3: 131,334`). The naive gap is purely a **composition effect**—Tier 2 contains zero Grocery Stores, whereas Tier 1 (`OUT019`) and Tier 3 (`OUT010`) each contain one.
3. **Outlet Assortment Breadth Gap:** Supermarkets average **930.0 SKUs** vs **541.5 SKUs** in Grocery Stores (a **388.5 SKU/store** gap). Using the Supermarket mean Recorded Sales value (`141.09`), closing this listing gap across both Grocery Stores corresponds to a hypothetical catalogue-value addition of **+109,630.35 units (+9.12%)**—an illustrative catalogue scenario, **not** a revenue forecast.
4. **Category Concentration (Pareto):** The top 5 of 16 categories (`Fruits and Vegetables`, `Snack Foods`, `Household`, `Frozen Foods`, `Dairy`) account for **59.03%** (`709,369.87`) of the summed Recorded Sales metric, closely mirroring their **57.26%** listing-count share.
5. **Data Quality Engineering:** Imputed `1,463` missing `Item Weight` values via SKU mean (constant per SKU) with category-median fallback for 4 all-null SKUs; imputed `526` zero `Item Visibility` entries; harmonized `Item Fat Content` into `Low Fat`, `Regular`, and `Non-Edible`; and flagged 3 outlets with contradictory raw `Outlet Size` labels (`OUT010`, `OUT017`, `OUT045`) as `Unknown` while preserving `Outlet Size (Original)`.

---

## 🗂️ Project Structure

```text
BlinkIT-Grocery-Sales-Analysis/
├── app.py                                   # Interactive 5-tab Streamlit app (read-only SQLite + scenario explorer)
├── blinkit_warehouse.sql                    # SQLite Star Schema DDL (UNIQUE grain, FK enforcement) + 5 analytical views
├── build_warehouse.py                       # CWD-independent, repeatable SQLite ETL builder & view verifier
├── run_analysis.py                          # Standalone cleaning, statistical testing & 10-chart export pipeline
├── BlinkIT_Grocery_Sales_Analysis_v2.ipynb  # Canonical Jupyter analysis notebook (33 code cells, verified clean run)
├── dashboard_live_screenshot.png            # Current live Streamlit application screenshot
├── requirements.txt                         # Python dependencies
├── REMEDIATION_CHANGELOG.md                 # Full post-audit engineering changelog
├── .gitignore                               # Excludes restricted datasets (*.xlsx/*.csv), local *.db, caches
└── visuals/                                 # 12 unique high-resolution figures (10 pipeline + 2 cohort decomposition)
```

> **Note on excluded data files:** `BlinkIT Grocery Data.xlsx` and `BlinkIT_Grocery_Data_Cleaned.csv` are excluded via `.gitignore` and are **not redistributed** in this repository. Place your locally obtained workbook in `BlinkIT-Grocery-Sales-Analysis/` before running the pipeline (see setup steps below).

---

## 🗄️ SQL Star Schema & Analytical Views (`blinkit_warehouse.sql`)

- **Tables:** `dim_products` (`1,559` SKUs), `dim_outlets` (`10` outlets), `fact_inventory_pricing` (`8,523` rows, `UNIQUE(product_key, outlet_key)`, `PRAGMA foreign_keys = ON`).
- **Views:**
  1. `vw_sku_pricing_variance` — cross-store mean/min/max/spread of `sales_mrp` per SKU
  2. `vw_outlet_assortment_gap` — store SKU counts, `total_catalogue_value`, and gap vs Supermarket benchmark
  3. `vw_format_controlled_tiers` — `total_catalogue_value` and `catalogue_value_per_store` by Tier × Format
  4. `vw_category_pareto` — `category_sales_metric`, `sales_metric_share_pct`, and cumulative Pareto curve
  5. `vw_missing_sku_prioritization` — 658 SKUs stocked in 1–8 Supermarkets and absent from Grocery Stores

---

## 🚀 Reproducible Setup & Execution

Because the source dataset is **not redistributed** in this repository, obtain the dataset through its authorized source first:

1. **Obtain the source dataset:** Download the **BigMart Sales** practice dataset through your authorized Analytics Vidhya DataHack account (under Analytics Vidhya's platform terms of use), or place your locally obtained `BlinkIT Grocery Data.xlsx` (or `BlinkIT_Grocery_Data.xlsx`) workbook into `BlinkIT-Grocery-Sales-Analysis/`.
2. **Install dependencies:**
   ```bash
   pip install -r BlinkIT-Grocery-Sales-Analysis/requirements.txt
   ```
3. **Generate the cleaned CSV (`BlinkIT_Grocery_Data_Cleaned.csv`) and 10 core visuals locally:**
   ```bash
   python BlinkIT-Grocery-Sales-Analysis/run_analysis.py
   ```
4. **Build & verify the SQLite Star Schema warehouse (`blinkit_warehouse.db`):**
   ```bash
   python BlinkIT-Grocery-Sales-Analysis/build_warehouse.py
   ```
5. **Launch the interactive Streamlit dashboard (auto-builds DB if missing; connects read-only):**
   ```bash
   streamlit run BlinkIT-Grocery-Sales-Analysis/app.py
   ```

---

## ⚠️ Data Provenance & Limitations

- **Attribution & Non-Redistribution:** Forensic inspection indicates the source workbook (`8,523` rows, `1,559` SKUs, `OUT010`–`OUT049`, `Item_MRP` range `31.29–266.89`) is derived from the **Analytics Vidhya BigMart Sales** practice dataset. Analytics Vidhya classifies this dataset as proprietary and restricts public third-party redistribution; accordingly, **neither the source workbook nor the derived cleaned CSV is redistributed in this repository**, and no open license is claimed.
- **No Transaction Volume or Timestamps:** The dataset has no units-sold column, no transaction dates, and no COGS. Actual revenue, demand elasticity, seasonality, and gross profit cannot be established from these records alone.
- **Hypothetical Scenarios:** The Tab 1 scenario calculator in `app.py` separates observed catalogue listings from user-controlled velocity/margin sliders and is strictly illustrative.

---

## 🧰 Tools & Technologies

- **Python (`pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `openpyxl`)** — data cleaning, variance decomposition, hypothesis testing, static visual pipeline
- **SQL / SQLite** — Star Schema dimensional modeling, window-function Pareto views, FK/UNIQUE integrity
- **Streamlit & Plotly** — interactive 5-tab decision-support explorer with read-only SQL sandbox
- **Jupyter Notebook** — canonical end-to-end analytical narrative (`BlinkIT_Grocery_Sales_Analysis_v2.ipynb`)

---

## 👩‍💻 Author

**Pooja Singh** · [GitHub Profile](https://github.com/PoojaS-1616)
