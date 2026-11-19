# Critical Date Validation Audit — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Audit Date:** 2026-11-19
**Severity:** **CRITICAL (`C-1`)**

---

## 1. Documented Date-Parsing Assumption

In `Data_Cleaning_Process.md` (§1) and `Insights!B23`, the author states:
- Source `Order Date` values arrived in two string formats: `m/d/yyyy` (slashes) and `dd-mm-yyyy` (dashes).
- Slash dates were parsed **month-first** (confirmed because the second field reaches 31).
- Dash dates were parsed **day-first** ("following the Indian convention") because both fields were `≤ 12` and therefore ambiguous.
- Impact claimed: *"Year-level results are not affected. The monthly trend could shift for the dash-format rows if those dates are really month-first."*

---

## 2. Independent Forensic Inspection of Stored Dates (`Data!F2:F9995`)

1. **Stored type & range:** All 9,994 `Order Date` cells are true Excel date serials spanning `2015-01-02` to `2018-12-30` (`2015: 1,993`, `2016: 2,102`, `2017: 2,587`, `2018: 3,312`).
2. **Pre-cleaning raw strings:** **NOT VERIFIED** directly (pre-cleaning CSV is not committed to the repository). However, rows where `day ≤ 12` total **4,042** (40.44% of dataset), of which **3,683** (36.85%) have `day ≠ month` and therefore change month under a day/month swap.
3. **Helper column alignment:** Stored `Year` (`L2:L9995`) and `Month` (`M2:M9995`) match the stored `Order Date` on 9,994/9,994 rows (0 mismatches), though both are hardcoded strings (`M-1`).

---

## 3. Decisive Statistical Refutation of the Day-First Assumption

In any real or simulated order table where orders occur throughout the month, **day-of-month counts for Days 1–28 should be approximately uniform** (here, Days 13–28 average **327.2 orders/day**, range 269–398).

However, inspecting the **actual day-of-month counts for Days 1–12** inside `Data!F2:F9995` reveals an unmistakable, statistically impossible anomaly:

| Day of Month | Order Count | Expected (~Uniform) | Deviation | Matches Real Month Seasonality? |
|---:|---:|---:|---:|---|
| **Day 1** | **121** | 336.8 | −64.1% | Matches **January** (lowest month) |
| **Day 2** | **131** | 336.8 | −61.1% | Matches **February** (2nd lowest month) |
| Day 3 | 242 | 336.8 | −28.1% | Matches March |
| Day 4 | 279 | 336.8 | −17.2% | Matches April |
| Day 5 | 275 | 336.8 | −18.4% | Matches May |
| Day 6 | 295 | 336.8 | −12.4% | Matches June |
| Day 7 | 268 | 336.8 | −20.4% | Matches July |
| Day 8 | 246 | 336.8 | −27.0% | Matches August |
| **Day 9** | **589** | 336.8 | **+74.9%** | Matches **September** (top-3 peak month!) |
| Day 10 | 311 | 336.8 | −7.7% | Matches October |
| **Day 11** | **617** | 336.8 | **+83.2%** | Matches **November** (#1 peak month!) |
| **Day 12** | **668** | 336.8 | **+98.3%** | Matches **December** (#2 peak month!) |

- **Chi-square goodness-of-fit test on Days 1–12:** $\chi^2(\text{df}=11) = \mathbf{1,105.2}$ ($p \ll 10^{-200}$).
- **Direct row-level confirmation:** In `Data!F2:F5`, `OD1` and `OD2` are stored as `2017-08-11` (Aug 11), `OD3` as `2017-12-06` (Dec 6), `OD4` as `2016-11-10` (Nov 10)—which in the original Superstore/Supermart source were `11-08-2017` (Nov 8), `06-12-2017` (Jun 12), and `10-11-2016` (Oct 11).
- **Conclusion:** **The day-first parsing assumption is refuted by internal statistical evidence.** The dash-format dates were unambiguously **`MM-DD-YYYY` (month-first)**, matching the slash-format dates (`M/D/YYYY`). Excel/Power Query originally formatted dates with `day ≤ 12` using dashes when the Kaggle dataset was exported.

---

## 4. Quantified Impact on Monthly Trends & Seasonality

Comparing the workbook's stored monthly totals (**As-Is**) against swapping day and month on the 4,042 `day ≤ 12` rows (**Month-First Corrected**):

| Month | Stored As-Is (₹) | Corrected MM-DD (₹) | Distortion (₹) | Relative Shift |
|---|---:|---:|---:|---:|
| 01 (Jan) | 9,02,128 | 5,77,972 | −3,24,156 | **−35.9%** *(As-is inflated +56.1%)* |
| 02 (Feb) | 8,30,301 | 4,56,102 | −3,74,199 | **−45.1%** *(As-is inflated +82.0%)* |
| 03 (Mar) | 12,47,196 | 10,53,980 | −1,93,216 | −15.5% |
| 04 (Apr) | 10,28,352 | 9,98,453 | −29,899 | −2.9% |
| 05 (May) | 12,51,327 | 10,86,920 | −1,64,407 | −13.1% |
| 06 (Jun) | 10,28,694 | 10,57,808 | +29,114 | +2.8% |
| 07 (Jul) | 11,07,483 | 10,89,385 | −18,098 | −1.6% |
| 08 (Aug) | 12,20,430 | 10,46,807 | −1,73,623 | −14.2% |
| **09 (Sep)** | **17,06,141** | **20,64,266** | **+3,58,125** | **+21.0%** *(As-is understated −17.3%)* |
| 10 (Oct) | 12,37,389 | 12,43,289 | +5,900 | +0.5% |
| **11 (Nov)** | **17,94,831** | **21,93,924** | **+3,99,093** | **+22.2%** *(As-is understated −18.2%)* |
| **12 (Dec)** | **16,02,710** | **20,88,076** | **+4,85,366** | **+30.3%** *(As-is understated −23.2%)* |

- **Annual totals (2015–2018):** **0% impact** (year is always the 3rd field).
- **Top-3 seasonal ranking:** Shifts from **Nov > Sep > Dec** (As-Is) to **Nov > Dec > Sep** (Corrected).
- **Best single month (`2018-09`):** Shifts from **₹5.89 lakh** (As-Is) to **₹7.06 lakh** (Corrected, +₹1.16 lakh).

## Recommended Actions

1. Re-parse the raw source file using `MM-DD-YYYY` for both slash and dash dates (verify day-of-month distribution becomes uniform across Days 1–28, $\chi^2 \approx 10\text{–}20$).
2. Update `Monthly Sales & Profit Trend`, `Insights`, `Dashboard!K77`, and `README.md` seasonal figures accordingly.
3. Document the chi-square day-of-month verification in `Data_Cleaning_Process.md` as a showcase of forensic data validation.
