# Requirement Traceability Matrix — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Repository:** `PoojaS-1616/data-analysis` (`main` @ `a8a2afa`), folder `Supermart-Grocery-Sales-Dashboard`
**Audit Date:** 2026-11-19

## Traceability Matrix

| # | Audit / Business Requirement | Status | Evidence (Exact Workbook / File Locations) | Findings & Gaps |
|---|---|---|---|---|
| 1 | **Overall sales, profit, margin, orders, avg discount, AOV** | **PASS** | `Dashboard!B5:S7` linked to `Analysis!A9:F9`; `README.md` line 29. All 6 KPIs reconcile 100% (`₹1,49,56,982`, `₹37,47,121`, `25.1%`, `9,994`, `22.7%`, `₹1,497`). | Weighted margin (`B9/A9`) correctly used. Currency `₹` is assumed without strong evidence (`M-5`). |
| 2 | **Annual sales & YoY growth (2015–2018)** | **PASS** | `Analysis!A32:E37` (`+5.3%`, `+23.6%`, `+28.6%`); `Dashboard` Chart 8 (`Yearly Sales & Profit`). | Year-level totals are unaffected by day/month swaps. However, `Data!L2:L9995` (`Year`) is hardcoded text, not a formula (`M-1`), and Chart 8 overlaps `K77` (`M-4`). |
| 3 | **Monthly sales & profit trends and seasonality** | **FAIL** | `Analysis!A40:C89` (48 months, `2015-01` to `2018-12`); `Dashboard` Chart 3 (`Monthly Sales & Profit Trend`). | **Critical (`C-1`):** 4,042 dash-format dates were misparsed day-first (`χ²(11) = 1,105.2`), distorting monthly totals by up to +82% (Feb) and −23% (Dec) and reversing the #2/#3 seasonal months (Dec > Sep when corrected). |
| 4 | **Category & sub-category performance + high-sales/low-margin flags** | **PASS** | `Analysis!A12:F20` (7 categories, 13.6%–15.2%), `Analysis!A92:L116` (23 sub-categories, dynamic `RANK.EQ` + `INDEX/MATCH` Top 10); Charts 1, 4, 5. | Numerically accurate (`Spices 23.8%`, `Masalas 24.2%`, `Cakes 24.6%`). Minor: `>=MEDIAN` flags 8 items (including median `Mutton`) vs README wording "above-median" (`m-5`); Chart 1 doughnut duplicates Chart 4 (`M-4`). |
| 5 | **Discount vs profit & margin analysis** | **FAIL** | `Analysis!A152:H161` (5 discount bands + `CORREL` `0.000` & `0.008`); Chart 7 (`Profit Margin by Discount Band`); `README.md` lines 34, 41. | Arithmetic reconciles 100%, **but Critical (`C-2`):** `r = 0.000` is an undisclosed synthetic data artifact (`Profit = Sales × {5%..45%}` independent of `Discount`), and `README.md` line 41 makes a commercially unsafe recommendation to test discounts without costing profit, contradicting `Dashboard!K77` and `Insights!B17`. |
| 6 | **Regional & city geographic performance** | **PARTIAL** | `Analysis!A23:F29` (5 regions), `Analysis!A119:L144` (24 cities, Top 10 ranked), `Analysis!A147:D149` (Tamil Nadu); Charts 2 & 6. | Accurately computed and candidly notes single `North` order and city/region decoupling. Partial because synthetic city/region mismatch makes "West is largest region" non-geographic, and Chart 2 renders `North` as an unreadable sliver (`m-4`). |
| 7 | **Interactive dropdown filters (Year, Region, Category)** | **PASS** | `Dashboard!D3, H3, L3` (Excel `x14` list validations referencing `Lists!$A$2:$C$9`); `Analysis!B3:B5` wildcard criteria. | Verified live in Microsoft Excel 16.0 across 7 test cases (single, combined, single-order North, empty group, reset) with **0 errors**. Minor: `K77` Key Takeaways and `CORREL` are static/unfiltered (`m-1`, `m-3`). |
| 8 | **Data cleaning & reproducibility** | **PARTIAL** | `Data_Cleaning_Process.md` (60 lines); `Data!A1:N9995`. | Candid about mixed dates, North order, and no SKU column; **but** pre-cleaning raw CSV is not retained (**NOT VERIFIED** raw slash/dash counts), `Year`/`Month` are hardcoded (`M-1`), and synthetic structure is omitted (`C-2`). |
| 9 | **Dashboard visual quality & preview** | **PARTIAL** | `Dashboard!B1:S94` (8 charts); `Supermart_Grocery_Dashboard_Preview.png`. | Strong teal theme and Top-10 ordering, **but** Chart 8 clips `KEY TAKEAWAYS` (`M-4`) and preview PNG cuts off 6 of 8 charts with Excel UI chrome (`M-3`). |
| 10 | **GitHub & metadata readiness** | **PASS (with `M-2`, `M-5`)** | Local matches GitHub `main` (`a8a2afa`) byte-for-byte on all 4 files. | Deductions for opening on `Analysis` tab, leaking OneDrive path (`M-2`), and lacking direct `.xlsx` download link in `README.md` (`M-5`). |

## Completion Summary

- **PASS:** 5 (#1, #2, #4, #7, #10)
- **PARTIAL:** 3 (#6, #8, #9)
- **FAIL:** 2 (#3 monthly date validity, #5 discount commercial interpretation)
- **NOT VERIFIED:** 0 requirements (pre-cleaning raw date string counts noted as unverified sub-item)
- **Verified Completion Percentage:** **75%** (accounting for arithmetic pass vs analytical failure on #3 and #5)
