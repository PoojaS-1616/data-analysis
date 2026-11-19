# Critical Issues and Recommendations

**Project:** Amazon India Business Performance Dashboard
**Audit date:** 2026-11-19
**Audit scope:** Read-only independent audit of `PoojaS-1616/data-analysis` (`main` @ `d4cb3cb`), folder `amazon-indian-business-dashboard-main`.

---

## 1. Critical Issues (Must Fix Before Submission)

### C-1: Undisclosed Synthetic Dataset with Implausible Product Pricing & Uniform Margins
- **Area:** Data Integrity & Business Analysis
- **Evidence:**
  - In `Raw_Data`, every product in `Electronics & Mobiles`—including `Laptop Backpack` (median ₹17,815, max ₹34,965), `Power Bank 20000mAh` (median ₹17,689, max ₹34,902), `Wireless Earbuds` (max ₹34,945), `Smartwatch` (max ₹34,993), and `5G Smartphone` (min ₹800, max ₹34,991)—is drawn from the exact same uniform ₹800–₹35,000 distribution. As a result, **`Laptop Backpack` is the #1 product by sales (₹2.65 Cr)**, beating `5G Smartphone` (₹2.43 Cr).
  - The same category-wide uniform price bands appear in `Home & Kitchen` (₹500–₹8,000; `Cotton Bedsheet Double` up to ₹7,999, `Water Purifier` down to ₹526), `Apparel & Fashion` (₹350–₹3,000), `Beauty & Personal Care` (₹200–₹1,500), and `Pantry & Groceries` (₹150–₹1,200; `Organic Turmeric Powder` up to ₹1,188).
  - Per-order profit margins on Delivered/Shipped orders are uniformly distributed `12.0%–35.0%` (mean `23.3%–23.7%`) identically across all 5 categories.
  - Neither `README.md` nor `Data_Cleaning_Process.md` discloses that the dataset is synthetic/simulated or notes this anomaly.
- **Impact:** Any hiring manager or senior analyst inspecting the Top 10 Products chart will immediately notice a ₹35,000 Laptop Backpack outselling 5G Smartphones and question whether the analyst performed basic domain sanity checks.
- **Recommended Action:** Add a clear **Data Provenance & Limitations** note to `README.md` and `Data_Cleaning_Process.md` stating that the dataset is a synthetic/simulated portfolio dataset, and explicitly flag the uniform category-level pricing and margin distributions as a known dataset artifact.

---

## 2. Major Issues (Fix Before Portfolio Submission)

### M-1: Six Headline README Metrics Are Not Traceable to Any Workbook Formula
- **Evidence:** `README.md` reports `23.67%` margin excluding Returned & Cancelled, `9.85%` combined R+C rate, `₹1.56 crore` associated R+C sales value, `2024` (₹5.70 Cr) vs `2025` (₹5.74 Cr) annual sales and `+0.73%` growth, plus category/payment/fulfilment/state `%` shares (`79%`, `50%`, `69%`, `49%`). While all reconcile mathematically against `Raw_Data`, none of them exists as a formula in the workbook.
- **Recommended Action:** Add an `Annual_Summary` table (including Jan–Aug like-for-like 2024/2025/2026) and `% Share` / `R+C Sales Value` / `Excl. R/C Margin` formulas in the summary sheets so 100% of README numbers are auditable in Excel.

### M-2: README Download URL Points to Wrong Repository Name
- **Evidence:** `README.md` line 98 links to `PoojaS-1616/data-analyst-portfolio` instead of `PoojaS-1616/data-analysis`. Currently relies on a GitHub redirect.
- **Recommended Action:** Update the link to `https://raw.githubusercontent.com/PoojaS-1616/data-analysis/main/amazon-indian-business-dashboard-main/Amazon_India_Business_Performance_Dashboard.xlsx` (or relative `./Amazon_India_Business_Performance_Dashboard.xlsx`).

### M-3: Dashboard Preview Image Is Truncated and Shows Excel UI Chrome
- **Evidence:** `Amazon_Indian_Dashboard_Preview.png` shows only Section 1 (omitting 7 of 9 charts and 6 of 12 KPIs) and displays row/column headers, sheet tabs, scrollbars, and the `"Accessibility: Investigate"` status bar.
- **Recommended Action:** Export a clean, full-height image of all 4 dashboard sections without Excel chrome and replace the preview PNG.

### M-4: Dashboard Visual & Layout Defects
- **Evidence:**
  1. Headers and KPI cards span `A:P` while charts extend to `T` (~25% overhang).
  2. Chart 8 (`K97:T114`) is misaligned by 1 row relative to Chart 7 (`A98:J115`).
  3. Charts 5 & 6 revert to Excel default colors and gray non-bold titles, breaking the Amazon orange/teal theme.
  4. Charts 4 (`Top 10 Products`) and 9 (`State`) plot #1 items at the bottom instead of the top.
  5. Chart 1 dual-axis scaling (5:1) plots the Profit line visually above the Sales line in most months.
- **Recommended Action:** Standardize all elements to a single column grid (`A:P` or `A:T`), align Chart 8 to row 98, unify Charts 5–6 styling, reverse category axes on Charts 4 & 9, and rescale Chart 1's secondary axis (or use column+line combo).

### M-5: Incomplete Analytical Depth (Missing Like-for-Like 2026 & Segment R+C Rates)
- **Evidence:** `README.md` emphasizes `+0.73%` slow growth (2024→2025) but omits the Jan–Aug like-for-like trend (**+7.51% YoY in Jan–Aug 2026**, ₹4.14 Cr vs ₹3.85 Cr) and the 2024→2025 volume (`+1.05%`) vs AOV (`−0.32%`) split. Return/cancellation rates by Payment, Fulfilment (Seller Flex 11.24% vs FBA 9.31%), and State are not computed in the workbook, and Chart 6 plots raw counts instead of the `%` rate already calculated in `Category_Returns_Cancellations!E2:E6`.
- **Recommended Action:** Add Jan–Aug YoY and volume/AOV decomposition to the workbook and README, compute segment R+C rates, and visualize `%` rates in Section 3.

### M-6: Workbook Opens on Wrong Tab & Contains Personal OneDrive Path
- **Evidence:** `xl/workbook.xml` has `activeTab="10"` (`Product_Summary`) instead of `Dashboard`, and embeds `x15ac:absPath url="https://d.docs.live.net/6BD3F40DABD6C24A/Documents/"`.
- **Recommended Action:** Run Excel's Document Inspector to strip personal/cloud metadata, click `Dashboard!A1`, and re-save.

---

## 3. Minor Issues (Recommended Polish)

| ID | Issue | Recommended Action |
|---|---|---|
| `m-1` | Inconsistent naming: folder `amazon-indian-business-dashboard-main` and `Amazon_Indian_Dashboard_Preview.png` use `Indian` / `-main` vs workbook `India`. | Standardize to `India` and remove `-main` suffix if updating links. |
| `m-2` | `Data_Cleaning_Process.md` not linked from `README.md`; pre-cleaning date conversion method not logged; no standalone CSV. | Link `Data_Cleaning_Process.md` in `README.md`; document verified post-conversion `ISNUMBER()` status. |
| `m-3` | `Top_Products` links positionally (`Product_Summary!A2:D11`) and `INDEX/MATCH` assumes unique product→category mapping. | Acceptable for current scope; optionally switch to `GETPIVOTDATA` or note the assumption. |
| `m-4` | Blank row `10002` in `Raw_Data` XML dimension (`A1:N10002`, outside table `A1:N10001`). | Delete row 10002 before saving. |
| `m-5` | `Order_Month` uses `=TEXT(B2,"yyyy-mm")` rather than structured reference `=TEXT([@[Order_Date]],"yyyy-mm")`. | Convert to structured reference for best practice. |
| `m-6` | `Dashboard!A2` subtitle is hardcoded text; helper lists are manual (disclosed in README). | Make `A2` a dynamic formula (`="Data as of "&TEXT(MAX(RawData[Order_Date]),"mmm yyyy")&" | "&TEXT(COUNTA(RawData[Order_ID]),"#,##0")&" orders..."`). |
| `m-7` | Chart 4 has redundant single-series `Sales` legend; bar charts lack data labels/axis titles; `Category_Analysis!D1` & `Top_Products!E1` say `Units_Sold` instead of `Ordered_Quantity`. | Remove Chart 4 legend, add clean `₹ Cr` / `₹ L` axis scaling or labels, rename `Units_Sold` headers. |
| `m-8` | UK `Fulfilment` (Dashboard/README) vs US `Fulfillment` (`Raw_Data` / sheet name). | Standardize spelling across documentation and labels. |
| `m-9` | `README.md` does not clarify that the 23.67% margin still includes in-progress `Shipped` orders (delivered-only = 23.59%) and rises mechanically because Returned/Cancelled profit = ₹0. | Add one clarifying sentence in `README.md`. |
