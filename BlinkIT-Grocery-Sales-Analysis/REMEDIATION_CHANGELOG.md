# Remediation & Improvement Changelog — BlinkIT Grocery Sales Analysis

**Project:** BlinkIT Grocery Sales Analysis
**Repository:** `PoojaS-1616/data-analysis` (`main`)
**Last Updated:** 2026-11-19
**Verified Environment:** Windows 11 · Python `3.14.8` (`.venv`) · Streamlit `1.67.0` · Pandas `3.1.1` · Plotly `7.1.0`
**Publication Status:** Phase 1 remediation and cleaned Git history (restricted datasets removed from `main` history) are published on GitHub (`9fb1da88`); Phase 2 reproducibility and documentation refinements are verified and documented below.

---

## Phase 1: Technical Audit Remediation (Issues BK-C1 through BK-m5)

| Issue ID | Severity | Status | Concrete Changes Made |
|---|---|---|---|
| **BK-C1** | Critical | **RESOLVED** | Redesigned `app.py` Tab 1 Simulator into an explicitly hypothetical catalogue-assortment scenario clearly separating observed catalogue breadth (`OUT010`/`OUT019` vs. Supermarket benchmark) from user-defined velocity/margin sliders, with an explicit methodology & limitations warning box and zero claims of guaranteed working-capital ROI or profit uplift. |
| **BK-C2** | Critical | **RESOLVED** | Removed `$` USD symbols and misleading `revenue` labels across `blinkit_warehouse.sql` (renamed Views 3–4 columns to `total_catalogue_value`, `catalogue_value_per_store`, `category_sales_metric`, `sales_metric_share_pct`, `cumulative_sales_metric_pct`), `run_analysis.py` (all titles/axes/prints), `app.py` (Tab 3 labels), `BlinkIT_Grocery_Sales_Analysis_v2.ipynb`, and `README.md`. All values are consistently reported in original dataset units (currency unspecified). |
| **BK-M1** | Major | **RESOLVED** | Refactored `build_warehouse.py` and `run_analysis.py` to resolve all file paths via `BASE_DIR = Path(__file__).resolve().parent`, verified across multiple working directories. |
| **BK-M2** | Major | **RESOLVED** | Removed blank `dashboard_preview.png`; captured an uncropped live screenshot (`dashboard_live_screenshot.png`) of the remediated Streamlit app and embedded it in `README.md`. |
| **BK-M3** | Major | **RESOLVED** | Rewrote `README.md` to remove inaccurate badges and leftover notes, correct dataset filename casing, update project tree & visual counts (`12` unique PNGs), and document SQL view schemas and reproducible setup steps. |
| **BK-M4** | Major | **RESOLVED** | Consolidated on `BlinkIT_Grocery_Sales_Analysis_v2.ipynb` as the single canonical notebook (33 code cells, verified clean execution with 0 error outputs) and pruned duplicate PNGs in `visuals/`, leaving 12 unique high-resolution figures. |
| **BK-M5** | Major | **RESOLVED** | Added `UNIQUE(product_key, outlet_key)` and `PRAGMA foreign_keys = ON` to `blinkit_warehouse.sql` and `build_warehouse.py`. Updated `app.py` to open SQLite strictly read-only (`uri=True`, `mode=ro`), parameterized `LIMIT ?`, and implemented `validate_readonly_sql()` (comment-stripping, single-statement `SELECT`/`WITH` allowlist; verified blocking 7/7 malicious test queries). |
| **BK-M6** | Major | **RESOLVED** | Documented Analytics Vidhya BigMart Sales provenance and proprietary non-redistribution restrictions in `README.md`. Excluded both restricted datasets in `.gitignore`, removed them from Git tracking and rewritten Git history (`git-filter-repo`, 0 reachable dataset blobs in `main`), and published the cleaned `main` branch to GitHub (`9fb1da88`) while preserving both local files intact for authorized local execution. Note: repository history cleanup cannot remove pre-existing copies in external forks, external clones, or temporary remote caches. |
| **BK-M7** | Major | **RESOLVED** | Replaced all hardcoded KPIs in `app.py` with dynamic calculations from `df`, unified uplift baseline across `app.py` and `run_analysis.py` (Supermarket mean `141.09` → `+109,630.35`, `+9.12%`), and added empty-dataset / missing-column / zero-denominator guards. |
| **BK-m1** | Minor | **RESOLVED** | Added zero-division guards across KPI and variance calculations in `app.py`. |
| **BK-m2** | Minor | **RESOLVED** | Replaced all deprecated `use_container_width=True` calls in `app.py` with `width="stretch"` (verified on Streamlit `1.67.0`; `0` deprecation warnings). |
| **BK-m3** | Minor | **RESOLVED** | Replaced external sidebar logo URL in `app.py` with an offline-safe markdown header. |
| **BK-m4** | Minor | **RESOLVED** | Parameterized `REFERENCE_YEAR = 2026` explicitly in `run_analysis.py` and documented reference year in `blinkit_warehouse.sql`. |
| **BK-m5** | Minor | **RESOLVED** | Corrected View 5 header comment in `blinkit_warehouse.sql` (`1 to 8 Supermarkets`, `658` SKUs) and embedded the live dashboard screenshot in `README.md`. |

---

## Phase 2: Final Reproducibility & GitHub Readiness Polish (2026-11-19)

- **`.gitignore` Hardening:** Added explicit exclusions for `.venv/`, `.env`, `.env.*`, `*.sqlite`, `*.sqlite3`, `*.log`, and `.ipynb_checkpoints/` while preserving all restricted-dataset and database protections.
- **`requirements.txt` Floor Alignment:** Updated `streamlit>=1.30.0` to `streamlit>=1.50.0` so installations support `width="stretch"` used in `app.py` (tested on Python `3.14.8` with Streamlit `1.67.0`).
- **`README.md` Portfolio & Windows Upgrade:** Added structured Business Objectives, Technical Architecture, 5-Tab Dashboard Features, Windows PowerShell non-activation setup commands (`.venv\Scripts\python.exe`), `Ctrl+C` stop guidance, and Troubleshooting (including safe guidance for Windows Application Control).
- **`app.py` Guard & Usability Polish:** Added `"Outlet Size"` to `load_data()` required-column validation, improved missing-CSV and database auto-build error messages while preserving underlying error details, added KPI `help` tooltips and a sidebar tab guide, and disabled Tab 4 CSV export when 0 SKUs match active filters.
