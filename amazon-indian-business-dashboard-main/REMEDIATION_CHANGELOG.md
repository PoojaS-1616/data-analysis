# Remediation Changelog

**Project:** Amazon India Business Performance Dashboard
**Repository:** `PoojaS-1616/data-analysis` (`main` @ `d4cb3cb`)
**Folder:** `amazon-indian-business-dashboard-main`
**Remediation Date:** 2026-11-19
**Pre-Remediation Backup Location:** `C:\Users\pooja\.gemini\antigravity\scratch\backups\amazon-dashboard-backup-20261119_192106`

All 10,000 original source records in `Raw_Data` were preserved byte-for-byte (`10,001 / 10,001` header + data rows verified identical against the untouched backup).

---

## Summary of Changes by Audit Issue ID

| Issue ID | Severity | Status | Concrete Changes Made |
|---|---|---|---|
| **C-1** | Critical | **RESOLVED** | Added explicit synthetic-dataset disclosure banner and dedicated **Dataset & Methodology** section in `README.md`, domain-plausibility section in `Data_Cleaning_Process.md` (documenting uniform category price bands and 12%–35% margin bands), and `"Synthetic portfolio dataset"` label in the dynamic `Dashboard!A2` subtitle. Zero source records altered. |
| **M-1** | Major | **RESOLVED** | Implemented 100% formula-driven structured-reference calculations for all previously untraceable README metrics: `Order_Status!D2:F9` (Excl. R/C margin `23.67%`, Delivered-only margin `23.59%`, Combined R+C `9.85%` & `₹1,56,48,743` associated sales value), `Annual_Analysis` (2024 vs 2025 full-year growth `+0.73%`, YoY category shares), and `Sales_Share_Pct` columns on `Category_Analysis`, `Payment_Analysis`, `Fulfillment_Analysis`, and `State_Analysis` (plus Top-3 states rollup `49.00%`). |
| **M-2** | Major | **RESOLVED** | Updated `README.md` workbook download URL from `PoojaS-1616/data-analyst-portfolio` to `https://raw.githubusercontent.com/PoojaS-1616/data-analysis/main/amazon-indian-business-dashboard-main/Amazon_India_Business_Performance_Dashboard.xlsx`. Verified all relative links (`./Amazon_Indian_Dashboard_Preview.png`, `./Data_Cleaning_Process.md`). |
| **M-3** | Major | **RESOLVED** | Replaced truncated Excel-window screenshot with a clean, full-dashboard, high-resolution preview (`1508 × 3470 px`, zero Excel UI chrome, all 4 sections and all 9 charts clearly legible) in `Amazon_Indian_Dashboard_Preview.png`. |
| **M-4** | Major | **RESOLVED** | Extended all Dashboard banners and KPI strips flush across `A:T` to match full-width charts; aligned all 9 charts to exact left/right grid coordinates (`Left=0`, `Width=fullW` or equal-width pairs with `10pt` gap); aligned Chart 8 to row 98 matching Chart 7; unified Charts 5 & 6 title typography and Amazon palette (Teal `#067D62`, Blue `#146EB4`, Orange `#FF9900`, Rust `#C7511F`); reversed horizontal bar axes on Charts 4 & 9 so #1 items (`Laptop Backpack`, `Maharashtra`) appear at the top; rescaled Chart 1 secondary axis (`₹25,00,000` max) so Profit plots cleanly below Sales; added dynamic executive footnote at `Dashboard!A138:T138`. |
| **M-5** | Major | **RESOLVED** | Added new `Annual_Analysis` sheet with full-year 2024→2025 decomposition (Sales `+0.73%`, Orders `+1.05%`, AOV `−0.32%`), like-for-like Jan–Aug 2024/2025/2026 comparisons (Jan–Aug 2026 YoY Sales `+7.52%`, Orders `+2.78%`, Profit `+9.61%`), and YoY category sales shares. Added Returned %, Cancelled %, and Combined R+C % formulas to `Payment_Analysis`, `Fulfillment_Analysis`, and `State_Analysis`, and updated `README.md` and `Dashboard!A138` with these validated findings. |
| **M-6** | Major | **RESOLVED** | Set `Dashboard` as the active worksheet on open (`ActiveSheet = Dashboard`, `A1` selected, scroll at `1,1`); stripped personal OneDrive `x15ac:absPath` block from `xl/workbook.xml`; cleared personal author strings from `docProps/core.xml` and `refreshedBy` from `xl/pivotCache/pivotCacheDefinition1.xml`. Verified clean open and `RefreshAll` in Microsoft Excel 16.0. |
| **m-1** | Minor | **DOCUMENTED (Retained Intentionally)** | Kept folder name `amazon-indian-business-dashboard-main` and preview filename `Amazon_Indian_Dashboard_Preview.png` to avoid breaking root `README.md` links, git history, and external portfolio URLs. |
| **m-2** | Minor | **RESOLVED** | Linked `Data_Cleaning_Process.md` directly from `README.md` (two locations) and documented verified post-cleaning `10,000 / 10,000` `ISNUMBER` date status and pre-cleaning archive limitation transparently. |
| **m-3** | Minor | **DOCUMENTED (Retained Intentionally)** | `Top_Products!A2:E11` positional links to `Product_Summary` (`PivotTable1` with grand totals disabled) and `INDEX/MATCH` were verified working under live `RefreshAll` and `RawData` row expansion in Excel 16.0; retained for clarity and compatibility across Excel versions. |
| **m-4** | Minor | **RESOLVED** | Deleted blank trailing row `10002` from `Raw_Data`. |
| **m-5** | Minor | **RESOLVED** | Converted `RawData[Order_Month]` calculated column from `=TEXT(B2,"yyyy-mm")` to structured reference `=TEXT([@[Order_Date]],"yyyy-mm")`; verified automatic fill on new row insertion in Excel 16.0. |
| **m-6** | Minor | **RESOLVED (Subtitle) / DOCUMENTED (Helper Lists)** | Replaced static `Dashboard!A2` subtitle with a dynamic formula referencing `MAX/MIN(RawData[Order_Date])` and `COUNTA(RawData[Order_ID])`. Manual helper label lists remain transparently documented in `README.md` under Updating the Dashboard. |
| **m-7** | Minor | **RESOLVED** | Removed redundant single-series `Sales` legend from Chart 4; renamed `Units_Sold` headers on `Category_Analysis!D1` and `Top_Products!E1` to `Ordered_Quantity`. |
| **m-8** | Minor | **RESOLVED** | Standardized spelling to `Fulfillment` across `Dashboard` (Section 4 banner, subtitle, Chart 8 title), `README.md`, and `Data_Cleaning_Process.md` to match the dataset column and sheet name. |
| **m-9** | Minor | **RESOLVED** | Clarified in `README.md` and `Dashboard!A138` that the 23.67% margin excludes Returned/Cancelled orders but still includes in-progress Shipped orders (Delivered-only = 23.59%), and rises mechanically because Returned/Cancelled rows have zero profit. |
