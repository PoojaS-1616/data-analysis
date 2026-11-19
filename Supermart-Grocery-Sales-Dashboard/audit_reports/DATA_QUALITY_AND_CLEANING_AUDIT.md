# Data Quality and Cleaning Audit — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Audit Date:** 2026-11-19
**Source Audited:** `Data` sheet (`A1:N9995`) in `Supermart_Grocery_Sales_Dashboard.xlsx` (git blob `e9dd348e4a7ee16a1805c43f402bf01c2d54490a`)

---

## 1. Independent Data Integrity Verification (9,994 Records)

| Check | Result | Verified Evidence |
|---|---|---|
| Total record count | **PASS** | Exactly **9,994** order rows (`A2:N9995`), 0 blank rows. Matches README. |
| Missing / blank values | **PASS** | **0** missing or blank cells across all 14 columns × 9,994 rows (139,916 cells). |
| Duplicate `Order ID` | **PASS** | **0** duplicates (`OD1`–`OD9994`, 9,994 unique IDs). |
| Duplicate records | **PASS** | **0** duplicate full rows; **0** duplicate rows excluding `Order ID`. |
| Data types | **PARTIAL (`M-1`)** | `Order Date`: 9,994 Excel datetimes; `Sales`: 9,994 ints; `Discount`: 9,994 floats; `Profit`: 9,994 numerics; `Profit Margin`: 9,994 formulas. **Defect:** `Year` (`L2:L9995`) and `Month` (`M2:M9995`) are **hardcoded text strings**, not formulas. |
| Negative / zero values | **PASS** | 0 negative or zero values in `Sales` (500–2,500), `Discount` (0.10–0.35), or `Profit` (25.25–1,120.95). |
| Category & sub-category labels | **PASS** | 7 categories, 23 sub-categories, 0 leading/trailing spaces, 100% consistent spelling. |
| City, Region & State labels | **ANOMALY (Documented)** | 24 cities, 5 regions (`West 3,203`, `East 2,848`, `Central 2,323`, `South 1,619`, `North 1`), 1 state (`Tamil Nadu 9,994`). **Every single one of the 24 cities appears in all 4 major regions** (and `Vellore` appears in all 5 including `North`). |
| Helper-column accuracy | **PASS (against stored dates)** | `Year` matches `Order Date.year` (as text) on 9,994/9,994 rows; `Month` matches `YYYY-MM` on 9,994/9,994 rows; `Profit Margin` (`=IF(I2=0,0,K2/I2)`) has 0 mismatches. |

---

## 2. Legitimate Anomalies vs Actual Data Errors

| Finding | Classification | Evidence & Assessment |
|---|---|---|
| Single `North` region order (`OD1`, Vellore, ₹1,254, 32% margin) | **Legitimate dataset quirk (properly retained)** | Correctly retained rather than deleted, and honestly documented in `Data_Cleaning_Process.md` and `Insights!B24`. |
| All 24 cities appear across all 4 regions | **Synthetic dataset artifact (documented)** | Correctly identified in `Data_Cleaning_Process.md` §4; proves `Region` is not geographically tied to `City` in Tamil Nadu. |
| `Sales` ∈ exact integer `[500, 2500]`; `Profit/Sales` ∈ exact integer `{5%..45%}`; `Discount` ∈ `{10%..35%}` independent of `Profit` | **Undisclosed synthetic dataset (`C-2`, Critical)** | `Sales` mean `1,496.60` / median `1,498.00`; `Profit/Sales` exact 2-decimal integer percent on **9,994/9,994 rows** (mean `25.02%`, median `25.00%`, stdev `11.89%`, matching $U(0.05, 0.45)$). Undisclosed in documentation. |
| 4,042 dash-format dates (`day ≤ 12`) parsed day-first (`dd-mm-yyyy`) | **Actual data-cleaning error (`C-1`, Critical)** | Day-of-month distribution (`χ²(11) = 1,105.2`) proves dash dates were `MM-DD-YYYY`. See [DATE_VALIDATION_AUDIT.md](./DATE_VALIDATION_AUDIT.md). |
| Hardcoded `Year` & `Month` helper columns (`Data!L2:M9995`) | **Technical defect (`M-1`, Major)** | Not formulas; will go stale if `Order Date` is edited. |

## Recommended Actions

1. Re-parse the 4,042 dash-format dates as `MM-DD-YYYY` (see `DATE_VALIDATION_AUDIT.md`) and convert `Year` and `Month` to live formulas (`=TEXT([@[Order Date]],"yyyy")` and `=TEXT([@[Order Date]],"yyyy-mm")`).
2. Add a **Synthetic Dataset & Distribution Characteristics** section to `Data_Cleaning_Process.md` documenting the uniform Sales, Discount, and Profit-Margin distributions.
3. Convert `Data!A1:N9995` to an Excel Table so formulas expand dynamically.
