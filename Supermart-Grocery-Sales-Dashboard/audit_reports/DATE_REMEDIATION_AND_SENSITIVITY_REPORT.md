# Date Remediation and Sensitivity Report — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Date:** 2026-11-19
**Audit Issue Addressed:** Critical Issue `C-1` (Dash-Format Date Interpretation)

---

## 1. Evidence Recovered (Phase 2 Investigation)

1. **Original raw CSV recovered locally:** `C:\Users\pooja\OneDrive\Documents\DATA SCIENCE + AI\PROJECTS\Supermart Grocery Sales - Retail Analytics Dataset.csv` (`9,994` rows).
   - **Parity check vs original audited workbook:** `9,994 / 9,994` non-date fields match identically, and `9,994 / 9,994` dates in the pre-remediation workbook match parsing slash rows as `M/D/YYYY` and dash rows as `DD-MM-YYYY`.
2. **Exact format partition in raw CSV:**
   - **Slash-format rows (`/`):** `5,952` rows (**59.56%**), first part ∈ `[1, 12]`, second part ∈ `[13, 31]`, year ∈ `[2015, 2018]`.
   - **Dash-format rows (`-`):** `4,042` rows (**40.44%**), first part ∈ `[1, 12]`, second part ∈ `[1, 12]`, year ∈ `[2015, 2018]`.
   - **Key structural proof:** Every single row with `day ≥ 13` uses slashes, and every single row with `day ≤ 12` uses dashes. This is the classic Excel regional-export signature of a `MM/DD/YYYY` CSV re-saved on a `DD-MM-YYYY` locale, where Excel preserves `MM-DD` order in the string (e.g., `OD1 = 11-08-2017`, `OD3 = 06-12-2017`).
3. **Independent Kaggle dataset documentation:** Confirms `OD1: 11-08-2017 = November 8, 2017` (`MM-DD-YYYY`) and `OD3: 6/12/2017 = June 12, 2017`.
4. **Statistical proof (Day-of-Month Chi-Square Test):**
   - **Pre-remediation (Dash = DD-MM):** Days 1–12 counts = `[121, 131, 242, 279, 275, 295, 268, 246, 589, 311, 617, 668]` → $\chi^2(\text{df}=11) = \mathbf{1,105.2}$ ($p \ll 10^{-200}$).
   - **Post-remediation (All = MM-DD):** Days 1–12 counts = `[337, 379, 365, 308, 366, 285, 298, 356, 344, 300, 359, 345]` → $\chi^2(\text{df}=11) = \mathbf{32.0}$ (uniform, matching Days 13–28 range of `269–398`).

**Conclusion:** Multi-source evidence conclusively confirms that all 4,042 dash-format rows (3,683 rows / 36.85% where `day ≠ month`) were **`MM-DD-YYYY`**.

---

## 2. Sensitivity Comparison: Pre-Remediation (Mixed) vs Corrected (MM-DD)

### Annual Totals (2015–2018)
- **0% change** across all 4 years (`2015: ₹29,75,599`, `2016: ₹31,31,959`, `2017: ₹38,71,912`, `2018: ₹49,77,512`; YoY `+5.3%`, `+23.6%`, `+28.6%`).

### Monthly Totals (All Years Combined)

| Month | Pre-Remediation (Dash = DD-MM) | Corrected (All = MM-DD) | Difference (₹) | Shift (%) |
|---|---:|---:|---:|---:|
| 01 (Jan) | ₹9,02,128 | ₹5,77,972 | −₹3,24,156 | −35.9% |
| 02 (Feb) | ₹8,30,301 | ₹4,56,102 | −₹3,74,199 | −45.1% |
| 03 (Mar) | ₹12,47,196 | ₹10,53,980 | −₹1,93,216 | −15.5% |
| 04 (Apr) | ₹10,28,352 | ₹9,98,453 | −₹29,899 | −2.9% |
| 05 (May) | ₹12,51,327 | ₹10,86,920 | −₹1,64,407 | −13.1% |
| 06 (Jun) | ₹10,28,694 | ₹10,57,808 | +₹29,114 | +2.8% |
| 07 (Jul) | ₹11,07,483 | ₹10,89,385 | −₹18,098 | −1.6% |
| 08 (Aug) | ₹12,20,430 | ₹10,46,807 | −₹1,73,623 | −14.2% |
| **09 (Sep)** | ₹17,06,141 | **₹20,64,266** | **+₹3,58,125** | **+21.0%** |
| 10 (Oct) | ₹12,37,389 | ₹12,43,289 | +₹5,900 | +0.5% |
| **11 (Nov)** | ₹17,94,831 | **₹21,93,924** | **+₹3,99,093** | **+22.2%** |
| **12 (Dec)** | ₹16,02,710 | **₹20,88,076** | **+₹4,85,366** | **+30.3%** |

### Seasonal Conclusions Impact

| Metric | Pre-Remediation (Mixed) | Corrected (MM-DD) |
|---|---|---|
| Combined Top-3 Months | Nov > Sep > Dec | **Nov (₹21.9L) > Dec (₹20.9L) > Sep (₹20.6L)** |
| Consistency Across All 4 Years | Sep missed Top 3 in 2017 | **Nov, Dec, Sep are Top 3 in ALL 4 years (4/4)** |
| Best Single Month | `2018-09` = ₹5,89,384 (₹5.9L) | **`2018-09` = ₹7,05,680 (₹7.1L)** |
| Lowest Single Month | `2015-02` = ₹1,20,444 (₹1.2L) | **`2015-02` = ₹66,030 (₹0.7L)** |

## 3. Verification Status

- Corrected all 3,683 inverted dates in `Supermart_Grocery_Sales_Dashboard.xlsx` (`SupermartData[Order Date]`).
- Verified **9,994 / 9,994** exact date match against the raw CSV parsed as `MM-DD-YYYY` / `M/D/YYYY`.
- Verified live `Year` and `Month` formula recalculation in Microsoft Excel 16.0 (`Analysis!B86 = 7,05,680`, `Analysis!B43 = 66,030`).
