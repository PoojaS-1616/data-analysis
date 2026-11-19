# Remediation Changelog — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Repository:** `PoojaS-1616/data-analysis` (`main` @ `a8a2afa`)
**Folder:** `Supermart-Grocery-Sales-Dashboard`
**Remediation Date:** 2026-11-19
**Pre-Remediation Backup Location:** `C:\Users\pooja\.gemini\antigravity\scratch\backups\supermart-dashboard-backup-20261119_201300`

All 9,994 non-date source records (`Order ID`, `Customer Name`, `Category`, `Sub Category`, `City`, `Region`, `State`, `Sales`, `Discount`, `Profit`) were verified **9,994 / 9,994 identical** to the original raw CSV. All 9,994 `Order Date` values were verified **9,994 / 9,994 identical** to the raw CSV parsed consistently as `MM-DD-YYYY` / `M/D/YYYY`.

---

## Summary of Changes by Audit Issue ID

| Issue ID | Severity | Status | Concrete Changes Made |
|---|---|---|---|
| **C-1** | Critical | **RESOLVED** | Located original raw CSV (`Supermart Grocery Sales - Retail Analytics Dataset.csv`) and confirmed 5,952 slash rows (`day 13–31`) and 4,042 dash rows (`day 1–12`). Corrected the 3,683 inverted dash-format dates (`day ≠ month`) to `MM-DD-YYYY`, reducing Day 1–12 chi-square from `1,105.2` to `32.0`. Rebuilt monthly trends (peak `2018-09` = `₹7,05,680`, lowest `2015-02` = `₹66,030`; Nov/Dec/Sep top 3 in all 4 years), raised Chart 3 Y-axis to `8,00,000`, and updated `Dashboard!K77`, `Insights`, `README.md`, `Data_Cleaning_Process.md`, and `DATE_REMEDIATION_AND_SENSITIVITY_REPORT.md`. |
| **C-2** | Critical | **RESOLVED** | Added explicit synthetic-dataset disclosure banner and provenance notes in `README.md`, `Data_Cleaning_Process.md`, `Dashboard!B2`, `Dashboard!K77`, and `Insights!B17,B24,B25`. Removed the commercially unsafe discount recommendation from `README.md` line 41 and replaced it with a clear statistical caveat explaining that independent synthetic margins cannot establish real-world discount elasticity. |
| **M-1** | Major | **RESOLVED** | Converted `Data!A1:N9995` to Excel Table `SupermartData`; replaced hardcoded `Year` and `Month` text strings with live structured formulas `=TEXT([@[Order Date]],"yyyy")` and `=TEXT([@[Order Date]],"yyyy-mm")`; updated `Profit Margin` to `=IF([@Sales]=0,0,[@Profit]/[@Sales])`; converted 304 `Analysis` formula cells to structured `SupermartData[...]` references. Verified live row expansion in Microsoft Excel 16.0. |
| **M-2** | Major | **RESOLVED** | Set `Dashboard` as active opening worksheet (`A1`, scroll `1,1`); stripped personal OneDrive `x15ac:absPath` URL from `xl/workbook.xml`; cleared `dc:creator` and `cp:lastModifiedBy` in `docProps/core.xml`. Verified clean open in Excel 16.0. |
| **M-3** | Major | **RESOLVED** | Replaced truncated Excel-window screenshot with a clean, full-dashboard high-resolution preview PNG (`1810 × 2361 px`, 688 KB, zero Excel UI chrome, all 6 KPIs, all 8 charts, and `KEY TAKEAWAYS` fully visible). |
| **M-4** | Major | **RESOLVED** | Narrowed Chart 8 (`Yearly Sales & Profit`) strictly before column `K` and added clean indent/border to `KEY TAKEAWAYS` (`K77:S94`) to eliminate text clipping; aligned Chart 3 (`Monthly Trend`) flush with `B1:S1`; replaced redundant Chart 1 (`Sales Share` doughnut) with a distinct **`Profit Margin by Category`** column chart with `%` data labels; added `%` data labels to Chart 7 (`Profit Margin by Discount Band`). |
| **M-5** | Major | **RESOLVED** | Qualified INR (₹) as an illustrative assumed currency for a synthetic dataset in `README.md`, `Data_Cleaning_Process.md`, `Dashboard!B2/K77`, and `Insights!B25`; added a direct clickable raw GitHub `.xlsx` download URL in `README.md`. |
| **m-1** | Minor | **DOCUMENTED (Retained Intentionally)** | `Dashboard!K77` Key Takeaways box remains a curated executive summary clearly labeled `(full synthetic dataset, assumed INR)` so full-dataset benchmarks remain visible while users explore filtered slices. |
| **m-2** | Minor | **RESOLVED** | Documented in `Data_Cleaning_Process.md` §5 that row-level `Profit Margin` is used strictly for `CORREL(Discount, Profit Margin)`, while all summary tables use weighted `SUM(Profit)/SUM(Sales)`. |
| **m-3** | Minor | **DOCUMENTED (Retained Intentionally)** | `Analysis!D160:D161` `CORREL` formulas intentionally remain full-dataset correlations (clearly labeled `(full data)`) because Excel `CORREL` does not support conditional `SUMIFS`-style criteria without dynamic array helpers. |
| **m-4** | Minor | **DOCUMENTED (Retained Intentionally)** | `North` (1 order, `OD1`) remains visible in Chart 2 and `Analysis!A29:F29` for 100% data completeness and is explicitly noted in `README.md` and `Insights!B24`. |
| **m-5** | Minor | **RESOLVED** | Aligned `README.md` wording (`≥ median sales`, 8 flagged sub-categories) with `Analysis!G94:G116`, and documented exact raw CSV slash (5,952) and dash (4,042) row counts in `Data_Cleaning_Process.md`. |
