# Final Submission Readiness Report

**Project:** Amazon India Business Performance Dashboard
**Repository:** `https://github.com/PoojaS-1616/data-analysis` (`main` @ `d4cb3cb83251922c2ca5d485344bbf3076568bc9`)
**Project Folder:** `amazon-indian-business-dashboard-main`
**Audit Date:** 2026-11-19
**Audit Mode:** Independent, evidence-based, read-only audit

---

## FINAL VERDICT

# **NOT READY FOR SUBMISSION**

- **Overall Score:** **74 / 100**
- **Verified Completion Percentage:** **80%** (6 PASS, 4 PARTIAL, 0 FAIL, 0 NOT VERIFIED across 10 core business requirements)
- **Critical Issues:** **1** (`C-1`)
- **Major Issues:** **6** (`M-1` through `M-6`)
- **Minor Issues:** **9** (`m-1` through `m-9`)

> **Why NOT READY FOR SUBMISSION:** Although the underlying Excel engineering, formula integrity, live PivotTable refresh, and numerical reconciliation (18/18 metrics) are **genuinely strong**, one unresolved Critical credibility issue (undisclosed synthetic dataset where a ₹35,000 `Laptop Backpack` outsells `5G Smartphone`) and six Major presentation/traceability/UX defects (a preview image cutting off 7 of 9 charts, workbook opening on a raw PivotTable tab, 6 README metrics absent from workbook formulas, legacy repo URL, visual alignment/palette breaks, and missing like-for-like 2026 growth) prevent immediate portfolio submission. All issues are straightforward to fix in a focused 2–3 hour remediation pass without rebuilding the workbook.

---

## 1. Evaluation Scorecard

| Evaluation Area | Weight | Score | Key Evidence |
|---|---:|---:|---|
| Requirement completeness | 20 | **15** | 6/10 PASS, 4/10 PARTIAL (annual trend, return/cancel depth, payment/fulfilment depth). |
| Data integrity and correctness | 15 | **11** | 10,000 clean rows, 0 nulls/duplicates, 100% exact sales math, 18/18 metrics reconcile. −4 pts for undisclosed synthetic pricing/margins (`C-1`). |
| Excel formulas and technical quality | 20 | **17** | Structured `RawData` table, 0 formula errors, live Excel 16.0 refresh & row-extension verified. −3 pts for 6 untraceable README metrics (`M-1`), wrong active tab (`M-6`), and positional PivotTable links. |
| Business analysis and insights | 15 | **10** | Disciplined definitions (no false loss/revenue claims, cautious recommendations). −5 pts for missing synthetic caveat (`C-1`), missing Jan–Aug 2026 YoY (+7.51%) & volume/AOV split (`M-5`), and missing segment R+C rates. |
| Dashboard design and usability | 10 | **6** | Clear 4-question hierarchy and readable KPI cards. −4 pts for `A:P` vs `A:T` overhang, Chart 5–6 theme break, inverted horizontal bars, Chart 7/8 stagger, dual-axis crossover (`M-4`), and truncated preview (`M-3`). |
| Documentation | 10 | **8** | Clear, honest `README.md` and `Data_Cleaning_Process.md`. −2 pts for legacy repo URL (`M-2`), missing synthetic disclosure (`C-1`), and unlinked cleaning doc (`m-2`). |
| GitHub and reproducibility | 10 | **7** | Clean 4-file folder, self-contained reproducible `.xlsx`. −3 pts for legacy download URL (`M-2`), OneDrive `absPath` metadata (`M-6`), inconsistent naming (`m-1`), and parent repo Windows long-path clone error. |
| **TOTAL** | **100** | **74** | |

---

## 2. Summary of Findings by Severity

### Critical Issues (1)
- **C-1 — Undisclosed synthetic dataset with implausible pricing & uniform margins:** Every product within a category shares an identical uniform price band (e.g., `Laptop Backpack` and `Power Bank 20000mAh` sell for ₹800–₹34,993, making `Laptop Backpack` #1 at ₹2.65 Cr ahead of `5G Smartphone`), and all 5 categories share an identical 12%–35% per-order margin band. Neither `README.md` nor `Data_Cleaning_Process.md` discloses this.

### Major Issues (6)
- **M-1 — Six README metrics not traceable to workbook formulas:** 23.67% margin excl. R/C, 9.85% combined R+C rate, ₹1.56 Cr R+C sales value, 2024 vs 2025 sales (+0.73%), and dimension `%` shares exist only in README prose.
- **M-2 — Wrong repository in README download URL:** `README.md` line 98 points to `PoojaS-1616/data-analyst-portfolio` instead of `PoojaS-1616/data-analysis` (works only via GitHub redirect).
- **M-3 — Truncated preview image with Excel UI chrome:** `Amazon_Indian_Dashboard_Preview.png` shows only Section 1 (omitting 7 of 9 charts) and exposes row/column headers, sheet tabs, and status bar.
- **M-4 — Dashboard layout & visual defects:** `A:P` banners vs `A:T` charts overhang; Chart 8 misaligned by 1 row vs Chart 7; Charts 5 & 6 break the orange/teal color palette and bold title font; Charts 4 & 9 plot #1 items at the bottom; Chart 1 dual-axis plots Profit visually above Sales.
- **M-5 — Missing like-for-like 2026 growth & segment R+C rate analysis:** Jan–Aug 2026 sales grew **+7.51% YoY** (omitted), 2024→2025 volume (+1.05%) vs AOV (−0.32%) split is omitted, segment R+C rates are absent, and Chart 6 plots counts instead of `%` rate.
- **M-6 — Wrong active tab & personal OneDrive metadata:** Workbook opens on `Product_Summary` (`activeTab="10"`) instead of `Dashboard`, and `xl/workbook.xml` contains a personal OneDrive `absPath` URL.

### Minor Issues (9)
- `m-1` Inconsistent `Indian`/`-main` folder & preview naming; `m-2` `Data_Cleaning_Process.md` not linked in `README.md` & incomplete cleaning log; `m-3` Positional PivotTable links in `Top_Products`; `m-4` Blank trailing row 10002 on `Raw_Data`; `m-5` Cell-relative `TEXT(B2,"yyyy-mm")` instead of structured reference; `m-6` Static `Dashboard!A2` subtitle & manual helper lists; `m-7` Redundant Chart 4 legend, missing axis titles/labels, `Units_Sold` header mismatch; `m-8` `Fulfilment` vs `Fulfillment` spelling; `m-9` Missing mechanical-margin / Shipped-inclusion clarification on 23.67%.

---

## 3. Missing Deliverables & Unverified Items

- **Missing deliverables:** Full-dashboard clean preview image (`M-3`); workbook formulas backing 6 README headline metrics (`M-1`); synthetic-data provenance disclosure (`C-1`); optional standalone CSV (not mandatory since `Raw_Data` is embedded, and confidential source data should never be published).
- **Unverified items:** Pre-cleaning raw state of `Order_Date` (text format and initial `=ISNUMBER(B2)` = `FALSE` results) is **NOT VERIFIED** because the pre-cleaning source file and conversion log were not retained. Everything else—including all 18 metrics, all formulas, all 9 charts, and live Microsoft Excel 16.0 refresh & table extension—was **directly verified**.

---

## 4. Required Corrections Checklist (Priority Order)

1. Disclose synthetic/simulated dataset provenance and uniform category pricing/margin distributions in `README.md` and `Data_Cleaning_Process.md` (`C-1`).
2. Fix `README.md` line 98 download URL to `PoojaS-1616/data-analysis` (`M-2`).
3. Add workbook formulas for the 6 untraceable README metrics, Jan–Aug YoY growth, and segment R+C rates (`M-1`, `M-5`).
4. Fix dashboard alignment (`A:P` vs `A:T`, Chart 8 row 98), Charts 5–6 styling, Charts 4 & 9 bar order, and Chart 1 secondary axis (`M-4`).
5. Strip OneDrive `absPath` via Document Inspector, select `Dashboard!A1`, and re-save (`M-6`).
6. Export a clean full-dashboard PNG without Excel UI chrome to replace `Amazon_Indian_Dashboard_Preview.png` (`M-3`).

---

## 5. Final Professional Assessment

This project demonstrates **above-average analytical discipline and solid Excel fundamentals**: zero formula errors, clean structured table architecture, verified dynamic refresh, 100% numerical accuracy across all 18 reported metrics, and unusually careful business definitions that avoid common junior-analyst traps (conflating gross sales with delivered revenue, treating returns as confirmed loss, or comparing partial-year 2026 to full-year 2025). Addressing the synthetic-data disclosure, visual polish, preview screenshot, active tab, and metric traceability will elevate this project from **74/100 (Not Ready)** to **90+/100 (Strong Portfolio-Ready Submission)**.

---

## Companion Audit Reports

- [REQUIREMENT_TRACEABILITY_MATRIX.md](./REQUIREMENT_TRACEABILITY_MATRIX.md)
- [EXCEL_TECHNICAL_AUDIT.md](./EXCEL_TECHNICAL_AUDIT.md)
- [BUSINESS_METRIC_RECONCILIATION.md](./BUSINESS_METRIC_RECONCILIATION.md)
- [DASHBOARD_DESIGN_AUDIT.md](./DASHBOARD_DESIGN_AUDIT.md)
- [DOCUMENTATION_AUDIT.md](./DOCUMENTATION_AUDIT.md)
- [GITHUB_READINESS_AUDIT.md](./GITHUB_READINESS_AUDIT.md)
- [CRITICAL_ISSUES_AND_RECOMMENDATIONS.md](./CRITICAL_ISSUES_AND_RECOMMENDATIONS.md)
