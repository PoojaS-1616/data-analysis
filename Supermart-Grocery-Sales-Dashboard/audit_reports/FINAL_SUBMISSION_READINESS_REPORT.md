# Final Submission Readiness Report — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Repository:** `https://github.com/PoojaS-1616/data-analysis` (Branch: `main`, commit `a8a2afa`)
**Project Folder:** `Supermart-Grocery-Sales-Dashboard`
**Audit Date:** 2026-11-19
**Audit Mode:** Independent, evidence-based, strictly read-only audit

---

## FINAL VERDICT

# **NOT READY FOR SUBMISSION**

- **Overall Score:** **68 / 100**
- **Verified Completion Percentage:** **75%** (5 PASS, 3 PARTIAL, 2 FAIL/BLOCKED on analytical reliability across 10 core audit requirements; 18/18 arithmetic reconciliations PASS against stored data)
- **Critical Issues:** **2** (`C-1`, `C-2`)
- **Major Issues:** **5** (`M-1` through `M-5`)
- **Minor Issues:** **5** (`m-1` through `m-5`)

> **Executive Summary:** Technically, the workbook's interactive Excel engineering is **well-built**: all 18 reported metrics reconcile 100% against the stored `Data` sheet, zero formula errors exist, weighted profit margins (`SUM(Profit)/SUM(Sales)`) are used consistently, and live testing in **Microsoft Excel 16.0** confirmed that all three dropdown filters (`Year`, `Region`, `Category`) work cleanly across single, combined, single-order, and empty-group selections. However, **two critical analytical defects** block portfolio submission: (1) forensic day-of-month analysis (`χ²(11) = 1,105.2`, $p \ll 10^{-200}$) proves that 4,042 dash-format dates were misparsed day-first instead of month-first, distorting monthly sales by up to **+82%** (Feb) and **−23%** (Dec) and flipping the #2/#3 seasonal months; and (2) the dataset is demonstrably synthetic (exact integer Sales `500–2500`, exact integer Profit % `5%–45%` generated independently of Discount), yet this is undisclosed and `README.md` extrapolates the synthetic `r = 0.000` artifact into a commercially unsafe discounting recommendation.

---

## 1. Evaluation Scorecard (Out of 100)

| Evaluation Area | Weight | Score | Key Evidence |
|---|---:|---:|---|
| Requirement completeness | 15 | **13** | All 4 business questions and 18 headline KPIs implemented; −2 pts for unquantified monthly date distortion and missing synthetic disclosure. |
| Data integrity and quality | 15 | **8** | 9,994 rows, 0 nulls, 0 duplicates, clean labels; −5 pts for misparsed dash dates (`C-1`), −2 pts for undisclosed synthetic structure & non-geographic region noise (`C-2`). |
| Excel formulas and technical quality | 20 | **16** | 0 formula errors, live Excel 16.0 interactive filter suite passed 7/7 tests, weighted margins used; −4 pts for hardcoded `Year`/`Month` columns, fixed non-table ranges (`M-1`), and opening on `Analysis` tab (`M-2`). |
| Business analysis and statistical correctness | 20 | **11** | Exact math on stored data and candid notes on North/Region-City; −5 pts for distorted monthly seasonality (`C-1`), −4 pts for undisclosed synthetic `r = 0.000` and unsafe README discount recommendation (`C-2`). |
| Dashboard design and usability | 10 | **6** | Cohesive teal palette, well-ordered Top-10 bars, single-axis trend; −4 pts for Chart 8 overlapping `KEY TAKEAWAYS`, redundant Chart 1 doughnut, Chart 3 overhang (`M-4`), and truncated Excel-chrome preview (`M-3`). |
| Documentation | 10 | **7** | Clear prose and candid caveats on North/SKU/Region; −3 pts for missing synthetic disclosure (`C-2`), README/workbook recommendation contradiction, weak INR justification (`M-5`), and missing raw date counts. |
| GitHub and reproducibility | 10 | **7** | Exact local-to-GitHub blob match on all 4 files; −3 pts for personal OneDrive folder path leak (`M-2`), truncated preview (`M-3`), missing direct `.xlsx` download link (`M-5`), and absent raw pre-cleaning CSV. |
| **TOTAL** | **100** | **68** | |

---

## 2. Summary of Findings by Severity

### Critical Issues (2)
- **C-1 — Dash-format dates misparsed day-first (statistically refuted by internal day-of-month distribution):** Days 1–12 show an impossible distribution (`Day 1 = 121`, `Day 2 = 131` vs `Day 9 = 589`, `Day 11 = 617`, `Day 12 = 668`; `χ²(11) = 1,105.2`), proving the 4,042 dash-format dates were month-first (`MM-DD-YYYY`). Swapping day/month on `day ≤ 12` shifts Feb by **−45.1%** (meaning as-is Feb is **+82% inflated**), Jan by **−35.9%** (+56% inflated), Dec by **+30.3%**, Nov by **+22.2%**, and Sep by **+21.0%**, changing the seasonal ranking from Nov > Sep > Dec to **Nov > Dec > Sep** and peak `2018-09` from ₹5.89L to **₹7.06L**.
- **C-2 — Undisclosed synthetic dataset & commercially unsafe discount recommendation:** `Sales` is uniform integer `[500, 2500]`, `Profit/Sales` is exact discrete integer `{5%..45%}` independent of `Discount` (`{10%..35%}`), and all 24 Tamil Nadu cities appear in all 4 regions. Not disclosing this—and recommending in `README.md` line 41 to *"test whether selective discounts can lift volume without costing profit"*—is analytically and commercially indefensible (and contradicts `Dashboard!K77` and `Insights!B17`).

### Major Issues (5)
- **M-1 — Hardcoded `Year` & `Month` helper columns (`Data!L2:M9995`) and static non-table ranges:** Editing `Order Date` or appending rows does not update `Year`, `Month`, or any `Analysis` formula (`$A$2:$N$9995`).
- **M-2 — Opens on wrong tab (`Analysis`) & leaks personal OneDrive path:** `xl/workbook.xml` has `activeTab="1"` (`Analysis`) and embeds `https://d.docs.live.net/6bd3f40dabd6c24a/Documents/DATA SCIENCE ^M AI/Github Project folders/Supermart-Grocery-Sales-Dashboard/` plus `cp:lastModifiedBy = Pooja Singh`.
- **M-3 — Truncated preview PNG with Excel UI chrome:** `Supermart_Grocery_Dashboard_Preview.png` shows only 2 of 8 charts and includes Excel column/row headers, tabs, scrollbar, and `"Accessibility: Investigate"`.
- **M-4 — Dashboard visual overlap & chart redundancy:** Chart 8 (`Yearly Sales & Profit`) clips the left edge of `KEY TAKEAWAYS` (`K77:S94`); Chart 1 (7-slice doughnut of 14%–15% slices) duplicates Chart 4; Chart 3 overhangs slightly; Chart 7 lacks data labels.
- **M-5 — Weak currency justification & missing direct workbook link:** Assuming INR solely from `State = Tamil Nadu` without noting synthetic/illustrative currency is weak; `README.md` has no direct `.xlsx` download link; pre-cleaning CSV is absent.

### Minor Issues (5)
- `m-1` Static `KEY TAKEAWAYS` box on `Dashboard!K77` (labeled full dataset); `m-2` Row-level `Profit Margin` helper column used only for `CORREL`; `m-3` `CORREL` cells unfiltered (labeled full data); `m-4` Single `North` order plotted as unreadable sliver on Chart 2; `m-5` `>=MEDIAN` flags 8 sub-categories (including median item `Mutton`) while README says "above-median" and cites 3.

---

## 3. Missing Deliverables & Unverified Findings

- **Missing deliverables:** Clean full-dashboard preview PNG; direct workbook download URL in `README.md`; synthetic-data provenance disclosure; formula-driven `Year`/`Month` columns and Excel Table conversion.
- **Unverified findings:** Exact count of original slash-format vs dash-format date strings before cleaning is **NOT VERIFIED** because the pre-cleaning raw CSV was not committed to GitHub (inferred count of `day ≤ 12` rows in the converted workbook is 4,042, with 3,683 where `day ≠ month`).

---

## 4. Prioritized Remediation Roadmap

1. **Re-parse dash-format dates as `MM-DD-YYYY`** (or clearly re-verify against the raw CSV) and rebuild monthly trends/seasonality (`C-1`).
2. **Disclose the synthetic dataset** in `README.md`, `Data_Cleaning_Process.md`, and `Dashboard`, and remove the unsafe discount recommendation from `README.md` line 41 (`C-2`).
3. **Convert `Data` to an Excel Table**, replace hardcoded `Year`/`Month` strings with `=TEXT([@[Order Date]],"yyyy")` and `=TEXT([@[Order Date]],"yyyy-mm")`, and use structured references (`M-1`).
4. **Fix Dashboard layout:** eliminate Chart 8's overlap on `K77`, replace or remove redundant Chart 1, add data labels to Chart 7, and export a clean full-dashboard PNG (`M-3`, `M-4`).
5. **Save on `Dashboard` tab (`A1`), strip OneDrive `absPath` & author metadata**, add a direct `.xlsx` download link in `README.md`, and qualify the INR assumption (`M-2`, `M-5`).

---

## 5. Final Professional Assessment

This project has **strong Excel interactivity and clean weighted-margin formulas**—the dynamic `SUMIFS`/`COUNTIFS`/`RANK.EQ`/`INDEX-MATCH` architecture with 3 working dropdowns is genuinely impressive. However, because a **36.85% date-parsing inversion (`C-1`)** corrupts the monthly seasonality narrative and an **undisclosed synthetic dataset (`C-2`)** underpins a commercially flawed discounting recommendation, the project is **NOT READY FOR SUBMISSION** until those two critical issues and the five major presentation/metadata defects are resolved.

---

## Companion Audit Reports (`audit_reports/`)

- [REQUIREMENT_TRACEABILITY_MATRIX.md](./REQUIREMENT_TRACEABILITY_MATRIX.md)
- [DATA_QUALITY_AND_CLEANING_AUDIT.md](./DATA_QUALITY_AND_CLEANING_AUDIT.md)
- [DATE_VALIDATION_AUDIT.md](./DATE_VALIDATION_AUDIT.md)
- [BUSINESS_METRIC_RECONCILIATION.md](./BUSINESS_METRIC_RECONCILIATION.md)
- [STATISTICAL_AND_BUSINESS_ANALYSIS_AUDIT.md](./STATISTICAL_AND_BUSINESS_ANALYSIS_AUDIT.md)
- [EXCEL_FORMULA_AND_FUNCTIONALITY_AUDIT.md](./EXCEL_FORMULA_AND_FUNCTIONALITY_AUDIT.md)
- [DASHBOARD_DESIGN_AUDIT.md](./DASHBOARD_DESIGN_AUDIT.md)
- [DOCUMENTATION_AND_GITHUB_AUDIT.md](./DOCUMENTATION_AND_GITHUB_AUDIT.md)
- [CRITICAL_ISSUES_AND_RECOMMENDATIONS.md](./CRITICAL_ISSUES_AND_RECOMMENDATIONS.md)
