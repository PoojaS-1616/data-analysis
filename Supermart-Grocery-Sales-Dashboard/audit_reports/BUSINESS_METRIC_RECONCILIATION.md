# Business Metric Reconciliation — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Audit Date:** 2026-11-19
**Source Audited:** `Data!A1:N9995` in `Supermart_Grocery_Sales_Dashboard.xlsx` (git blob `e9dd348e...`)

## Method

1. Independently recalculated all 18 reported metrics in Python (`openpyxl`) directly from the 9,994 rows in `Data`.
2. Opened an isolated copy in **Microsoft Excel 16.0**, ran `CalculateFull()`, and verified all `Analysis` and `Dashboard` outputs (original file SHA-256 confirmed unchanged).
3. Verified whether profit margins use weighted `SUM(Profit) / SUM(Sales)` rather than unweighted row-level averages (**PASS** across all summary tables; weighted = `25.0527%`, unweighted = `25.0228%`).

## Reconciliation Table (18 Metrics)

| # | Metric (README) | Independent Value | Formula / Denominator | Workbook Location | Status |
|---|---|---:|---|---|---|
| 1 | ≈ ₹1.50 crore total sales | ₹1,49,56,982 (₹1.4957 Cr) | `SUM(Data!I2:I9995)` | `Analysis!A9` → `Dashboard!B6` | **PASS** |
| 2 | ≈ ₹37.5 lakh total profit | ₹37,47,121.20 (₹37.47 L) | `SUM(Data!K2:K9995)` | `Analysis!B9` → `Dashboard!E6` | **PASS** |
| 3 | ≈ 25% profit margin (25.1%) | 25.0527% | `SUM(Profit) / SUM(Sales)` (weighted) | `Analysis!C9` → `Dashboard!H6` | **PASS** |
| 4 | 9,994 total orders | 9,994 | `COUNTIFS(Data!L2:L9995,"*",...)` | `Analysis!D9` → `Dashboard!K6` | **PASS** |
| 5 | 2016 YoY sales growth: +5.3% | +5.2547% | `(31,31,959 / 29,75,599) - 1` | `Analysis!E35` | **PASS** |
| 6 | 2017 YoY sales growth: +23.6% | +23.6259% | `(38,71,912 / 31,31,959) - 1` | `Analysis!E36` | **PASS** |
| 7 | 2018 YoY sales growth: +28.6% | +28.5544% | `(49,77,512 / 38,71,912) - 1` | `Analysis!E37` | **PASS** |
| 8 | Category shares: 13.6%–15.2% | 13.63% (`Oil & Masala`) to 15.16% (`Eggs, Meat & Fish`) | `Category Sales / SUM(All Categories)` | `Analysis!D14:D20` | **PASS** |
| 9 | West region contribution: ≈ 32% | 32.08% (₹47,98,743; 3,203 orders) | `West Sales / Total Sales` | `Analysis!D25` | **PASS** |
| 10 | South region contribution: ≈ 16% | 16.32% (₹24,40,461; 1,619 orders) | `South Sales / Total Sales` | `Analysis!D28` | **PASS** |
| 11 | South regional margin: ≈ 25.6% | 25.5510% (₹6,23,563 / ₹24,40,461) | `South Profit / South Sales` (excl. 1-order North 32.0%) | `Analysis!E28` | **PASS** |
| 12 | November seasonal strength (top-2 every year) | #1 in 2015, 2016, 2017; #2 in 2018 (₹17.95 L total) | Monthly `SUMIFS` on stored `Month` | `Analysis!B52, B64, B76, B88` | **PARTIAL (`C-1`)** *(Matches stored data; true Nov is ₹21.94 L under MM-DD)* |
| 13 | September top-3 in 2015, 2016, 2018; 2018-09 ≈ ₹5.9 lakh | 2015 #3, 2016 #2, 2018 #1 (`2018-09` = ₹5,89,384) | Monthly `SUMIFS` on stored `Month` | `Analysis!B50, B62, B86` | **PARTIAL (`C-1`)** *(Matches stored data; true `2018-09` is ₹7.06 L and Dec > Sep overall)* |
| 14 | Discount / profit correlation ≈ 0.000 | `0.000017` (`t = 0.0017`) | `CORREL(Data!J2:J9995, Data!K2:K9995)` | `Analysis!D160` | **PASS (Math)** / **Caveat (`C-2`)** |
| 15 | Discount / margin correlation ≈ 0.008 | `0.008282` (`t = 0.8279`) | `CORREL(Data!J2:J9995, Data!N2:N9995)` | `Analysis!D161` | **PASS (Math)** / **Caveat (`C-2`)** |
| 16 | Discount-band margin range: 24.8%–25.7% | `24.82%` (20–25%) to `25.71%` (25–30%) | Weighted `SUM(Profit)/SUM(Sales)` per band | `Analysis!G154:G158` | **PASS** |
| 17 | Spices margin ≈ 23.8% | `23.8235%` (Sales ₹6,72,876; Profit ₹1,60,303) | `Sub-Cat Profit / Sub-Cat Sales` | `Analysis!E103` | **PASS** |
| 18 | Masalas ≈ 24.2%; Cakes ≈ 24.6% | Masalas `24.2300%` (₹6,97,480); Cakes `24.5618%` (₹6,85,612) | `Sub-Cat Profit / Sub-Cat Sales` | `Analysis!E100`, `E101` | **PASS** |

**Summary:** **18 of 18 metrics reconcile arithmetically** against the stored `Data` sheet (0 calculation discrepancies). However, metrics #12–13 are materially affected by the dash-date parsing error (`C-1`), and metrics #14–16 reflect an undisclosed synthetic independence artifact (`C-2`).
