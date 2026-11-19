# Documentation and GitHub Readiness Audit — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Repository:** `https://github.com/PoojaS-1616/data-analysis` (Branch: `main`, commit `a8a2afa`)
**Project Folder:** `Supermart-Grocery-Sales-Dashboard`
**Audit Date:** 2026-11-19

---

## 1. GitHub-to-Local Sync Verification

All 4 files in `Supermart-Grocery-Sales-Dashboard/` match `origin/main` byte-for-byte:

| File | Size (B) | Git Blob SHA-1 | Status |
|---|---:|---|---|
| `Supermart_Grocery_Sales_Dashboard.xlsx` | 971,515 | `e9dd348e4a7ee16a1805c43f402bf01c2d54490a` | Exact match |
| `Supermart_Grocery_Dashboard_Preview.png` | 122,131 | `800a677af4146c1798970814a3b060fd407d8465` | Exact match |
| `README.md` | 4,434 | `2d1793fef4ebecf6b7823341c8f64f84ba3839d8` | Exact match |
| `Data_Cleaning_Process.md` | 2,086 | `d50bcc489f17a60ec2b3d3f62f1813955bb09982` | Exact match |

No stray temporary files (`~$*.xlsx`), logs, or credentials exist in the folder.

---

## 2. README.md & Data_Cleaning_Process.md Audit

| Area | Status | Evidence & Findings |
|---|---|---|
| Project overview & 4 business questions | **PASS** | `README.md` lines 1–26 clearly define scope and business questions. |
| Quantitative agreement with workbook | **PASS (stored data)** | All 18 reported figures reconcile with `Analysis` & `Data` (subject to `C-1` date-parsing impact on monthly metrics). |
| Synthetic dataset disclosure | **FAIL (`C-2`)** | Neither `README.md` nor `Data_Cleaning_Process.md` discloses that the dataset is synthetic (uniform integer `Sales`, independent uniform integer `Profit %`, non-geographic `Region` tags inherited from US Superstore). |
| Discount recommendation consistency | **FAIL (`C-2`)** | `README.md` line 41 recommends testing selective discounts without costing profit, contradicting `Dashboard!K77` and `Insights!B17` (*"does not establish how changing discounts would affect sales or profit"*). |
| Currency assumption (`₹`) | **PARTIAL (`M-5`)** | `Data_Cleaning_Process.md` §7 assumes `₹` solely because `State = Tamil Nadu`. While transparent, this is insufficient evidence: the dataset is a synthetic Indianized derivative of US Superstore with integer sales `500–2,500` and no currency metadata. It should be labeled "assumed INR (illustrative synthetic currency)". |
| Geographic & product-level limitations | **PASS** | Candidly documents Tamil Nadu-only state, single `North` order (`OD1`), city/region decoupling, and sub-category proxy for missing SKU column. |
| Date-cleaning documentation | **PARTIAL (`C-1`, `m-5`)** | Transparently states the slash/dash rule and notes monthly risk, **but** omits exact row counts of slash vs dash dates, omits the raw pre-cleaning CSV (**NOT VERIFIED**), and fails to test the day-of-month distribution (`χ² = 1,105.2`). |
| Tools & interactive usage instructions | **PASS** | Accurately lists `SUMIFS`, `COUNTIFS`, `AVERAGEIFS`, `CORREL`, dropdown filters, and usage steps. |
| Preview image & relative links | **PARTIAL (`M-3`)** | `Supermart_Grocery_Dashboard_Preview.png` and `Data_Cleaning_Process.md` links resolve properly, but the preview image cuts off 6 of 8 charts and includes Excel UI chrome. |
| Direct workbook download link | **MISSING (`M-5`)** | `README.md` line 78 says *"Download the `.xlsx` file from this folder"* without providing a clickable raw GitHub download URL. |

---

## 3. Recruiter & Reproducibility Assessment

- **Folder & file naming:** **Clean** (`Supermart-Grocery-Sales-Dashboard` — professional, consistent naming, no `-main` suffix).
- **Workbook first-impression UX (`M-2`):** **Poor** — opens on `Analysis` (`activeTab="1"`) instead of `Dashboard`.
- **Metadata privacy (`M-2`):** **Major leak** — `xl/workbook.xml` exposes a personal OneDrive folder path (`https://d.docs.live.net/6bd3f40dabd6c24a/Documents/DATA SCIENCE ^M AI/Github Project folders/Supermart-Grocery-Sales-Dashboard/`) and author name `Pooja Singh`.
- **Reproducibility:** Another analyst can download the `.xlsx`, use the dropdown filters, and reproduce all 18 stored-data metrics cleanly. However, pre-cleaning date parsing cannot be re-executed because the raw CSV is not archived, and `Year`/`Month` are hardcoded strings rather than formulas (`M-1`).

## Recommended Actions

1. Add a **Synthetic Dataset & Provenance** disclosure to `README.md` and `Data_Cleaning_Process.md`, and remove the unsafe discount recommendation (`C-2`).
2. Add a direct raw GitHub download link for `Supermart_Grocery_Sales_Dashboard.xlsx` in `README.md` (`M-5`).
3. Replace `Supermart_Grocery_Dashboard_Preview.png` with a clean full-dashboard export (`M-3`).
4. Strip the OneDrive `absPath` and personal metadata, and re-save on `Dashboard` (`M-2`).
