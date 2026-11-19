# Requirement Traceability Matrix

**Project:** Amazon India Business Performance Dashboard
**Audit date:** 2026-11-19
**Repository:** `PoojaS-1616/data-analysis` (`main` @ `d4cb3cb`), folder `amazon-indian-business-dashboard-main`

## Classification Key

- **PASS:** Fully answered in the workbook and dashboard with accurate, traceable calculations and clear visuals.
- **PARTIAL:** Addressed in part, but missing supporting calculations, visuals, segment depth, or workbook traceability.
- **FAIL:** Not answered or materially incorrect.
- **NOT VERIFIED:** Cannot be verified from available artifacts.

## Traceability Matrix (10 Core Business Requirements)

| # | Business Requirement | Status | Evidence (Exact Workbook / File Locations) | Gaps & Audit Findings |
|---|---|---|---|---|
| 1 | **What is the overall business performance?** | **PASS** | `Dashboard!A7:P9` (6 KPI cards: Recorded Sales Value `A8`, Recorded Profit `D8`, Total Orders `G8`, Ordered Quantity `J8`, Avg Order Value `L8`, Recorded Profit Margin % `N8`); `README.md` lines 11–13, 31. All 6 KPIs reconcile 100% against `RawData` (`A1:N10001`). | Minor: 23.67% margin (excluding Returned & Cancelled) is cited in `README.md` line 31 but not calculated in the workbook (`M-1`); `Dashboard!A2` subtitle is static text (`m-6`). |
| 2 | **What are the monthly sales and profit trends?** | **PARTIAL** | `Monthly_KPIs!A1:G33` (32 months, `2024-01` to `2026-08`, using `SUMIFS`/`COUNTIFS` on `RawData[Order_Month]`); `Dashboard` Chart 1 (`A11:T28`, dual-axis line chart: Sales & Profit). | Monthly trends are accurate and charted, **but**: (a) Annual 2024 vs 2025 comparison (+0.73%) cited in `README.md` line 41 has no formula or summary table in the workbook (`M-1`); (b) Like-for-like Jan–Aug 2026 vs 2025 (+7.51% YoY) is omitted (`M-5`); (c) Dual-axis scaling on Chart 1 plots the Profit line above the Sales line in most months (`M-4`). |
| 3 | **Which product categories contribute the most?** | **PASS** | `Category_Analysis!A1:D6` (5 categories: Sales, Profit, Units_Sold via `SUMIFS`); `Dashboard` Chart 2 (`A32:J49`, clustered column: Sales & Profit by Category) and Chart 3 (`K32:T49`, pie chart: Ordered Quantity by Category). | Minor: Percentage share of sales (79.32% Electronics) is cited in `README.md` line 33 but not calculated in `Category_Analysis` (`M-1`); column `D1` is labelled `Units_Sold` despite including Returned/Cancelled rows (`m-7`). |
| 4 | **Which products generate the highest sales?** | **PASS** | `Product_Summary!A1:D11` (PivotTable `PivotTable1` on `RawData`, Top 10 filter on `Sum of Total_Sales_INR`, descending); `Top_Products!A1:E11` (links to `Product_Summary` + `INDEX/MATCH` for Category); `Dashboard` Chart 4 (`A50:T68`, horizontal bar chart). Live refresh verified in Excel 16.0. | Major visual/credibility caveats: Chart 4 displays #1 product (`Laptop Backpack`, ₹2.65 Cr) at the **bottom** instead of top (`M-4`), and synthetic pricing (`Laptop Backpack` median ₹17,815, max ₹34,965) is undisclosed (`C-1`). |
| 5 | **What is the order-status distribution?** | **PASS** | `Order_Status!A1:C5` (`COUNTIFS` for Delivered 8,147 / Shipped 868 / Returned 485 / Cancelled 500 and `%` share of `COUNTA(RawData[Order_ID])`); `Dashboard!A73:P75` (6 KPI cards) and Chart 5 (`A77:I94`, pie chart). | Minor: Chart 5 breaks the dashboard's custom Amazon color palette and typography (`M-4`). |
| 6 | **What are the return and cancellation patterns?** | **PARTIAL** | `Category_Returns_Cancellations!A1:E6` (Returned count, Cancelled count, Category Orders, and `Returned + Cancelled %` ranging 8.81%–10.61%); `Dashboard` Chart 6 (`J77:S94`, stacked column of counts by category). | Gaps: (a) Chart 6 plots raw **counts** rather than **rates** (`E2:E6` is calculated but never visualized), visually exaggerating Electronics; (b) Combined 9.85% rate and ₹1.56 Cr associated sales value in `README.md` lines 35–37 do not exist in the workbook (`M-1`); (c) No return/cancellation breakdown by Payment Method, Fulfilment Method, State, or Month (`M-5`). |
| 7 | **How do payment methods affect recorded business performance?** | **PARTIAL** | `Payment_Analysis!A1:C6` (`SUMIFS` for Sales and Profit across 5 payment methods); `Dashboard` Chart 7 (`A98:J115`, clustered column). | Shows volume/value distribution (UPI ~50.4% sales) accurately, but omits order counts, AOV, profit margin %, and return/cancellation rates by payment method (`M-5`), and does not compute % share in the workbook (`M-1`). |
| 8 | **How does fulfilment method relate to business performance?** | **PARTIAL** | `Fulfillment_Analysis!A1:C4` (`SUMIFS` for Sales and Profit across Amazon FBA, Seller Flex, Merchant FBM); `Dashboard` Chart 8 (`K97:T114`, clustered column). | Shows FBA dominance (~69.0% sales), but omits order counts, margin %, and return/cancellation rates by fulfilment channel (e.g., Seller Flex 11.24% vs FBA 9.31%, `M-5`). Chart 8 is misaligned by 1 row vs Chart 7 (`M-4`). |
| 9 | **Which states contribute the most?** | **PASS** | `State_Analysis!A1:D11` (`SUMIFS` Sales & Profit + `COUNTIFS` Orders across all 10 states, sorted descending by sales); `Dashboard` Chart 9 (`A116:T136`, horizontal bar chart of Sales & Profit). | Minor: Orders (`D2:D11`) are not shown on the dashboard; top-3 state share (49.0% MH+KA+DL) is not calculated in the workbook (`M-1`); Chart 9 plots #1 `Maharashtra` at the bottom (`M-4`). |
| 10 | **What business recommendations can be derived from the analysis?** | **PASS** | `README.md` lines 47–55 (4 structured recommendations: category concentration pilots, separate return/cancellation reason tracking, segment hypothesis validation, slow-growth decomposition). | Recommendations are notably disciplined and avoid unsupported causal claims. Minor gap: Recommendation 4 asks to decompose 2024→2025 growth into volume/AOV/mix and compare equivalent 2026 periods, even though both analyses are straightforward to perform on the existing dataset (`M-5`). Also lacks a synthetic-data caveat (`C-1`). |

## Requirement Completion Summary

| Status | Count | Requirements |
|---|---:|---|
| **PASS** | 6 | #1, #3, #4, #5, #9, #10 |
| **PARTIAL** | 4 | #2, #6, #7, #8 |
| **FAIL** | 0 | — |
| **NOT VERIFIED** | 0 | — |

**Verified Completion Percentage:** **80%** (6 PASS × 10% + 4 PARTIAL × 5% = 80%; all 10 requirements directly verified against workbook XML, Python recalculation, and Excel 16.0 COM execution).

## Recommended Actions

1. Add an `Annual_Summary` and `KPI_Audit` block (or extend existing analysis sheets) to compute the 6 untraceable README metrics and Jan–Aug YoY growth inside the workbook.
2. Add return/cancellation rate columns (`%`) to `Payment_Analysis`, `Fulfillment_Analysis`, and `State_Analysis`, and plot the `Returned + Cancelled %` rate alongside or instead of raw counts in Section 3.
3. Disclose the synthetic nature of the dataset so product and recommendation interpretations are properly framed.
