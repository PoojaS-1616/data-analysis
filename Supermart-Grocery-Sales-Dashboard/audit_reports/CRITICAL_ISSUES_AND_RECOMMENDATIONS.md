# Critical Issues and Recommendations — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Repository:** `PoojaS-1616/data-analysis` (`main` @ `a8a2afa`), folder `Supermart-Grocery-Sales-Dashboard`
**Audit Date:** 2026-11-19

---

## 1. Critical Issues (Must Fix Before Submission)

### C-1: Dash-Format Dates Misparsed Day-First (Statistically Refuted by Internal Evidence)
- **Area:** Date Validation & Monthly Seasonality
- **Evidence:** All 4,042 rows with `day ≤ 12` (3,683 rows / 36.85% where `day ≠ month`) were parsed day-first (`dd-mm-yyyy`). Inspecting the stored day-of-month counts in `Data!F2:F9995` reveals an impossible distribution: `Day 1 = 121`, `Day 2 = 131` vs `Day 9 = 589`, `Day 11 = 617`, `Day 12 = 668` ($\chi^2(\text{df}=11) = 1,105.2$, $p \ll 10^{-200}$), proving the dash-format dates were **month-first (`MM-DD-YYYY`)**.
- **Quantified Impact:** Inflates January (+56.1%) and February (+82.0%), understates September (−17.3%), November (−18.2%), and December (−23.2%), reverses the #2/#3 seasonal ranking (true order: **Nov ₹21.94L > Dec ₹20.88L > Sep ₹20.64L**), and understates peak `2018-09` (₹5.89L vs ₹7.06L). Annual totals (2015–2018) are unaffected.
- **Recommended Action:** Re-parse dash-format dates as `MM-DD-YYYY`, verify uniform Day 1–28 counts, and refresh monthly charts and seasonal commentary.

### C-2: Undisclosed Synthetic Dataset & Commercially Unsafe Discount Recommendation
- **Area:** Data Integrity, Statistical Interpretation & Business Recommendations
- **Evidence:** `Sales` is exact uniform integer `[500, 2500]`, `Profit/Sales` is exact discrete integer `{5%..45%}` on 9,994/9,994 rows generated independently of `Discount` (`{10%..35%}`), and all 24 Tamil Nadu cities appear in all 4 regions (`West`, `East`, `Central`, `South`). Neither `README.md` nor `Data_Cleaning_Process.md` discloses that the dataset is synthetic. Worse, `README.md` line 41 recommends: *"Since discount level makes no visible difference to margin, test whether selective discounts can lift volume without costing profit"*—a commercially unsafe extrapolation of a synthetic artifact that also contradicts the workbook's own cautious wording (`Dashboard!K77`, `Insights!B17`).
- **Recommended Action:** Add a prominent synthetic-dataset disclosure to `README.md`, `Data_Cleaning_Process.md`, and `Dashboard`, and replace `README.md` line 41 with an explicit note that independent synthetic margins cannot establish real-world discount elasticity.

---

## 2. Major Issues (Fix Before Portfolio Submission)

### M-1: Hardcoded `Year` & `Month` Helper Columns and Static Non-Table Ranges
- **Evidence:** `Data!L2:L9995` (`Year`) and `Data!M2:M9995` (`Month`) are hardcoded text strings, not formulas, and `Data!A1:N9995` is a plain range rather than an Excel Table.
- **Recommended Action:** Convert `Data` to an Excel Table, replace `Year` and `Month` with `=TEXT([@[Order Date]],"yyyy")` and `=TEXT([@[Order Date]],"yyyy-mm")`, and update `Analysis` formulas to structured references.

### M-2: Workbook Opens on Wrong Tab (`Analysis`) & Leaks Personal OneDrive Path
- **Evidence:** `xl/workbook.xml` has `activeTab="1"` (`Analysis`), embeds `https://d.docs.live.net/6bd3f40dabd6c24a/Documents/DATA SCIENCE ^M AI/Github Project folders/Supermart-Grocery-Sales-Dashboard/`, and `docProps/core.xml` stores `cp:lastModifiedBy = Pooja Singh`.
- **Recommended Action:** Strip OneDrive `absPath` and personal metadata via Excel's Document Inspector (or clean XML), activate `Dashboard!A1`, and re-save.

### M-3: Truncated Preview Image with Excel UI Chrome
- **Evidence:** `Supermart_Grocery_Dashboard_Preview.png` shows only rows 1–30 (2 of 8 charts) and exposes column/row headers, worksheet tabs, scrollbar, and `"Accessibility: Investigate"`.
- **Recommended Action:** Export a clean full-dashboard PNG (`B1:S94`, all 8 charts + Key Takeaways, zero Excel chrome).

### M-4: Dashboard Visual Overlap & Chart Redundancy
- **Evidence:** Chart 8 (`Yearly Sales & Profit`) overlaps the left border of `KEY TAKEAWAYS` (`K77:S94`), clipping `"K"` and bullet dots; Chart 1 (7-slice doughnut of 14%–15% shares) duplicates Chart 4; Chart 3 overhangs slightly; Chart 7 lacks `%` data labels.
- **Recommended Action:** Trim Chart 8 width to end before column `K`, align Chart 3 flush with `S1`, add `%` data labels to Chart 7, and replace or remove redundant Chart 1.

### M-5: Weak Currency Justification & Missing Direct Download Link
- **Evidence:** Assuming INR solely from `State = Tamil Nadu` without acknowledging the synthetic US-Superstore derivative structure is weak; `README.md` lacks a direct clickable `.xlsx` download URL; pre-cleaning raw CSV is absent.
- **Recommended Action:** Qualify currency as "assumed INR (illustrative synthetic currency)" and add a direct raw GitHub `.xlsx` download link in `README.md`.

---

## 3. Minor Issues (Recommended Polish)

| ID | Issue | Recommended Action |
|---|---|---|
| `m-1` | `Dashboard!K77` Key Takeaways box is static text (properly labeled `(full dataset)`). | Optionally convert headline numbers to dynamic formulas referencing `Analysis`. |
| `m-2` | `Data!N2:N9995` row-level `Profit Margin` helper column used only for `CORREL`. | Document its sole purpose in `Data_Cleaning_Process.md` so reviewers know summary margins are weighted. |
| `m-3` | `Analysis!D160:D161` `CORREL` cells do not respond to filters (properly labeled `(full data)`). | Acceptable; keep label clear. |
| `m-4` | Single `North` order (`OD1`) plotted as an unreadable hairline sliver on Chart 2. | Add a subtle chart footnote or data labels so `North (1 order)` is transparent. |
| `m-5` | `Analysis!G94:G116` uses `>=MEDIAN` (flagging 8 items incl. median `Mutton`), while `README.md` says "above-median" and cites 3; `Data_Cleaning_Process.md` omits exact slash/dash row counts. | Align README wording (`≥ median`) and document exact date-format counts. |
