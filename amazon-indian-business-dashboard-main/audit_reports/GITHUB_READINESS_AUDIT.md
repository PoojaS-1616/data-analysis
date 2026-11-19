# GitHub Professional Readiness Audit

**Project:** Amazon India Business Performance Dashboard
**Repository:** `https://github.com/PoojaS-1616/data-analysis` (Branch: `main`, HEAD: `d4cb3cb83251922c2ca5d485344bbf3076568bc9`)
**Project Folder:** `amazon-indian-business-dashboard-main`
**Audit date:** 2026-11-19

---

## 1. Repository & Folder Inspection

A fresh clone of `origin/main` confirmed that `amazon-indian-business-dashboard-main` contains **exactly 4 files** and no subfolders:

| File | Size | Git Blob SHA-1 | Purpose |
|---|---:|---|---|
| `Amazon_India_Business_Performance_Dashboard.xlsx` | 1,421,449 B | `5d83014364...` | Self-contained Excel workbook (source data + calculations + dashboard) |
| `Amazon_Indian_Dashboard_Preview.png` | 133,851 B | `7488896120...` | Preview image embedded in README |
| `Data_Cleaning_Process.md` | 5,710 B | `6412c112e5...` | Data preparation and validation documentation |
| `README.md` | 8,131 B | `7c438bb8fe...` | Project overview, insights, recommendations, usage guide |

Root `README.md` of `PoojaS-1616/data-analysis` properly links to `./amazon-indian-business-dashboard-main/`.

---

## 2. Recruiter & Technical Evaluator Checklist

| Area | Status | Evidence & Findings |
|---|---|---|
| **Folder naming** | **Minor (`m-1`)** | `amazon-indian-business-dashboard-main` has a typo (`indian` instead of `india`) and a leftover GitHub ZIP-download suffix (`-main`), inconsistent with sibling folders (`BlinkIT-Grocery-Sales-Analysis`, `Supermart-Grocery-Sales-Dashboard`). |
| **File naming** | **Minor (`m-1`)** | `Amazon_Indian_Dashboard_Preview.png` uses `Indian` while the workbook uses `India` (`Amazon_India_Business_Performance_Dashboard.xlsx`). |
| **README presentation** | **Good** | Clean Markdown hierarchy, concise executive framing, readable tables, clear usage steps. |
| **Dashboard preview visibility** | **Poor (`M-3`)** | Renders inline via `./Amazon_Indian_Dashboard_Preview.png`, but shows only ~25% of the dashboard (Section 1) and exposes Excel UI chrome. A recruiter skimming GitHub never sees Sections 2, 3, or 4. |
| **Workbook accessibility & download link** | **Major (`M-2`)** | `README.md` line 98 points to `PoojaS-1616/data-analyst-portfolio` instead of `PoojaS-1616/data-analysis`. Currently succeeds via GitHub redirect (HTTP 200, identical blob), but is fragile and looks like a copy-paste oversight. |
| **Workbook first-impression UX** | **Major (`M-6`)** | Saved with `activeTab="10"` (`Product_Summary` PivotTable). A recruiter downloading and opening the file sees a raw PivotTable instead of the `Dashboard` sheet. |
| **Dataset availability & reproducibility** | **PASS (with caveats)** | All 10,000 source records are embedded inside `Raw_Data`, so any analyst can download the single `.xlsx` file and reproduce all 18 metrics and live Excel refreshes. No standalone CSV is provided (other folders in the same repo include `.csv` files), and 6 README metrics lack workbook formulas (`M-1`). |
| **Unnecessary files** | **PASS** | No temp files (`~$*.xlsx`), `.DS_Store`, or stray artifacts inside the project folder. |
| **Sensitive information exposure** | **Minor–Major (`M-6`)** | No credentials, API keys, or real customer PII. However, `xl/workbook.xml` embeds a personal OneDrive cloud path (`https://d.docs.live.net/6BD3F40DABD6C24A/Documents/`), and `docProps/core.xml` / `pivotCacheDefinition1.xml` store author name `Pooja Singh`. |
| **Repository-level clone health** | **Minor (repo-wide)** | A standard `git clone` of `PoojaS-1616/data-analysis` on Windows **fails checkout** due to Windows MAX_PATH limits in an unrelated sibling folder (`Smoking_Health_Analysis/.../0ad0aade9fb546ceb01e`), requiring `git -c core.longpaths=true` or sparse checkout. There is also no `.gitignore` or `LICENSE` file at the repo root. |

---

## 3. Can Another Analyst Reproduce the Project?

- **Workbook-level metrics & refresh:** **YES.** Verified by downloading/cloning the `.xlsx`, independently recalculating all 18 metrics from `Raw_Data` in Python, and testing `RefreshAll` + table-row addition in Microsoft Excel 16.0.
- **Pre-cleaning date conversion:** **NO (NOT VERIFIED).** Because only the cleaned workbook is published and the original conversion method was not logged, the raw-to-cleaned transformation cannot be independently reproduced.
- **Six README-only metrics:** **PARTIAL.** Reproducible from `Raw_Data`, but not wired into the workbook itself.

## Recommended Actions

1. Update `README.md` line 98 download URL to `PoojaS-1616/data-analysis`.
2. Replace `Amazon_Indian_Dashboard_Preview.png` with a clean full-dashboard preview (and optionally rename to `Amazon_India_Dashboard_Preview.png`).
3. Re-save the workbook on the `Dashboard` tab after stripping the OneDrive `absPath` via Excel's Document Inspector.
4. Optionally rename the folder to `Amazon-India-Business-Performance-Dashboard` (updating root `README.md` links accordingly) for consistent repo naming.
5. Add a root `.gitignore` and consider shortening the deeply nested path in `Smoking_Health_Analysis` so Windows users can clone the portfolio repository cleanly.
