# Data Cleaning Process

**Project:** Supermart Grocery Sales Dashboard
**Dataset:** 9,994 order records (`Supermart Grocery Sales - Retail Analytics Dataset`, 2015–2018)

## 1. Data Provenance & Synthetic Characteristics

The dataset exhibits clear **synthetic (simulated) generation characteristics** verified across all 9,994 rows:
- **`Sales`:** Exact integers uniformly distributed between `500` and `2,500` (mean `1,496.60`, median `1,498.00`).
- **`Discount`:** 26 discrete values uniformly distributed between `0.10` (10%) and `0.35` (35%) in `0.01` increments.
- **`Profit` & `Profit Margin`:** On **9,994 / 9,994 rows**, `Profit / Sales` is an exact discrete integer percentage in `{5%, 6%, ..., 45%}` (mean `25.02%`, median `25.00%`, stdev `11.89%`), generated **independently of `Discount`** ($r = 0.000017$ with profit; $r = 0.008282$ with margin).
- **Geography:** All 9,994 rows list `State = Tamil Nadu`, yet all 24 cities appear across all 4 major regions (`West`, `East`, `Central`, `South`), confirming region labels are non-geographic synthetic tags inherited from the 9,994-row US Superstore template.

Original source values were preserved without artificial modification; these limitations are disclosed transparently across the workbook and documentation.

## 2. Order Date Validation & Remediation (Forensic Verification)

In the original raw CSV (`Supermart Grocery Sales - Retail Analytics Dataset.csv`), `Order Date` appeared in two string formats:
- **5,952 slash-format rows (59.56%):** First field `1–12`, second field `13–31` (`M/D/YYYY`).
- **4,042 dash-format rows (40.44%):** First field `1–12`, second field `1–12` (`MM-DD-YYYY`).

**Why dash-format dates were corrected to Month-First (`MM-DD-YYYY`):**
An earlier version of this workbook parsed the 4,042 dash-format rows day-first (`DD-MM-YYYY`). Independent forensic inspection proved that day-first parsing inverted month and day on **3,683 rows (36.85%)**:
- Under day-first parsing, Days 1–12 displayed an impossible spike matching Q4/September monthly seasonality (`Day 1 = 121`, `Day 2 = 131` vs `Day 9 = 589`, `Day 11 = 617`, `Day 12 = 668`; $\chi^2(\text{df}=11) = \mathbf{1,105.2}$, $p \ll 10^{-200}$).
- Under consistent month-first parsing (`MM-DD-YYYY` for both slash and dash rows, corroborated by the raw CSV and Kaggle dataset documentation), Days 1–12 become uniform (`285–379/day`, $\chi^2(\text{df}=11) = \mathbf{32.0}$), matching Days 13–28 (`269–398/day`), and every year (2015–2018) displays the exact same top-3 seasonal months (November, December, September).
- Annual totals (2015–2018) are 100% unaffected.

Full sensitivity tables are documented in [DATE_REMEDIATION_AND_SENSITIVITY_REPORT.md](./audit_reports/DATE_REMEDIATION_AND_SENSITIVITY_REPORT.md).

## 3. Integrity & Quality Checks (Verified on All 9,994 Rows)

| Check | Verified Result | Action |
|---|---|---|
| Total rows | 9,994 order records (`SupermartData` table `A1:N9995`) | All 9,994 retained |
| Missing values | 0 missing / blank cells across all 14 columns | None removed or imputed |
| Duplicate `Order ID` | 0 duplicates (`OD1`–`OD9994`) | All retained |
| Duplicate records | 0 duplicate full rows | None removed |
| Numeric validity | 0 negative or zero values in `Sales`, `Discount`, `Profit` | Values preserved as supplied |
| Text label consistency | 0 leading/trailing spaces across 7 Categories, 23 Sub-Categories, 24 Cities, 5 Regions, 1 State | No edits needed |
| Region `North` outlier | 1 order (`OD1`, Vellore, ₹1,254, 32% margin) | Retained and documented as immaterial |
| Product / SKU level | No SKU column in source dataset | Sub-Category used as product proxy |

## 4. Currency Assumption

The source dataset does not specify a currency symbol or unit. **INR (₹)** is assumed for illustrative display because all records list `State = Tamil Nadu`, with an explicit caveat that the underlying values are synthetic.

## 5. Reproducible Helper Columns (`SupermartData` Excel Table)

All 9,994 records are stored in an Excel Table named `SupermartData`, with live structured formulas that auto-populate for new rows:

| Column | Excel Formula | Purpose |
|---|---|---|
| `Year` | `=TEXT([@[Order Date]],"yyyy")` | 4-digit year text key compatible with wildcard `"*"` dropdown filters |
| `Month` | `=TEXT([@[Order Date]],"yyyy-mm")` | `YYYY-MM` monthly grouping key |
| `Profit Margin` | `=IF([@Sales]=0,0,[@Profit]/[@Sales])` | Row-level margin used strictly for `CORREL(Discount, Profit Margin)`; all summary tables use weighted `SUM(Profit) / SUM(Sales)` |
