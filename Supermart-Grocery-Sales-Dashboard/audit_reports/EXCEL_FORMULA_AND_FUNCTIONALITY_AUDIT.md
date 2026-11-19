# Excel Formula and Functionality Audit — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Audit Date:** 2026-11-19
**Workbook Audited:** `Supermart_Grocery_Sales_Dashboard.xlsx` (971,515 bytes, git blob `e9dd348e4a7ee16a1805c43f402bf01c2d54490a`)
**Verification Environments:**
- Static XML & Python (`openpyxl 3.1.5`, `zipfile`) inspection of untouched repository workbook.
- Dynamic recalculation & interactive dropdown filter testing on an **isolated temporary copy** in **Microsoft Excel 16.0** via COM automation (original file SHA-256 confirmed unchanged).

---

## 1. Workbook Architecture

- **5 visible worksheets:** `Dashboard` (`B1:S94`, 8 charts), `Analysis` (`A1:L161`), `Insights` (`B1:B26`), `Data` (`A1:N9995`), `Lists` (`A1:C9`).
- **Tables / PivotTables / VBA:** 0 Excel Tables, 0 PivotTables, 0 VBA macros, 0 external links.
- **Metadata & Open Behavior (`M-2`, Major):**
  - `xl/workbook.xml` sets `activeTab="1"` (`Analysis`) instead of `Dashboard`—verified in Excel 16.0 (`ActiveSheet on open: Analysis`).
  - `xl/workbook.xml` embeds a personal OneDrive path: `https://d.docs.live.net/6bd3f40dabd6c24a/Documents/DATA SCIENCE ^M AI/Github Project folders/Supermart-Grocery-Sales-Dashboard/`.
  - `docProps/core.xml` contains `<dc:creator>openpyxl</dc:creator>` and `<cp:lastModifiedBy>Pooja Singh</cp:lastModifiedBy>`.

---

## 2. Formula Audit Across All Sheets

Zero formula errors (`#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#N/A`, `#NUM!`) exist in any cell (verified statically and after `CalculateFull()` in Excel 16.0).

| Sheet / Range | Formula Pattern | Assessment |
|---|---|---|
| `Data!L2:M9995` (`Year`, `Month`) | **Hardcoded text strings** (no formulas!) | **FAIL (`M-1`, Major):** If an `Order Date` is edited, `Year` and `Month` will not update. |
| `Data!N2:N9995` (`Profit Margin`) | `=IF(I2=0,0,K2/I2)` (9,994/9,994 consistent) | **PASS:** Clean division-by-zero guard. |
| `Analysis!B3:B5` (Filter criteria) | `=IF(Dashboard!$D$3="All","*",Dashboard!$D$3)` (and `$H$3`, `$L$3`) | **PASS:** Clean wildcard pattern for `SUMIFS`/`COUNTIFS`/`AVERAGEIFS`. Note: works for `Year` because `Data!L2:L9995` is text (`"2018"`); if `Year` were numeric, `"*"` would fail to match numbers! |
| `Analysis!A9:F9` (6 KPIs) | `SUMIFS`, `COUNTIFS`, `IFERROR(AVERAGEIFS(...),0)`, weighted `IF(A9=0,0,B9/A9)` | **PASS (minor `M-1`):** Accurate weighted margin and zero-division guards; uses fixed `$A$2:$N$9995` non-table ranges. |
| `Analysis!A14:F20` (Categories) | `SUMIFS`/`COUNTIFS` (ignores Category filter intentionally) | **PASS:** Correctly preserves category comparison when Category filter is active. |
| `Analysis!A25:F29` (Regions) | `SUMIFS`/`COUNTIFS` (ignores Region filter intentionally) | **PASS:** Correctly preserves regional comparison. |
| `Analysis!A34:E37` (Years) | `SUMIFS` (ignores Year filter) + `=IF(B34=0,"",B35/B34-1)` YoY growth | **PASS:** Clean YoY growth with zero guard. |
| `Analysis!A42:C89` (48 Months) | `SUMIFS` (ignores Year filter; Region & Category apply) | **PASS (formula)** / **FAIL (underlying dates `C-1`)**. |
| `Analysis!A94:L116` (Sub-Categories) & `A121:L144` (Cities) | `SUMIFS`, `AVERAGEIFS`, `>=MEDIAN` flag, tie-broken `_xlfn.RANK.EQ(...) + COUNTIFS(...) - 1`, dynamic Top-10 `_xlfn.IFNA(INDEX/MATCH)` | **PASS:** Sophisticated, bug-free dynamic Top-10 ranking without PivotTables. |
| `Analysis!A154:H158` (Discount Bands) | Dual-bound `COUNTIFS`/`SUMIFS` (`>=lo`, `<hi`, top band `<0.36`), weighted `F/E` | **PASS:** Captures all 9,994 rows with zero overlap/gaps (sum of orders = 9,994). |
| `Analysis!D160:D161` (`CORREL`) | `=CORREL(Data!$J$2:$J$9995, Data!$K$2:$K$9995)` and `...$N$2:$N$9995` | **PASS (`m-3`):** Accurate on full dataset; properly labeled `(full data)`. |

---

## 3. Live Interactive Dropdown Filter Testing (Microsoft Excel 16.0)

Data validations verified natively in Excel 16.0:
- `Dashboard!D3` (Year): `Type=3 (xlValidateList)`, `Formula1 = =Lists!$A$2:$A$6`
- `Dashboard!H3` (Region): `Type=3 (xlValidateList)`, `Formula1 = =Lists!$B$2:$B$7`
- `Dashboard!L3` (Category): `Type=3 (xlValidateList)`, `Formula1 = =Lists!$C$2:$C$9`

*(Note: `openpyxl` emits a warning and drops these because Excel stores cross-sheet list validations in `x14:dataValidations` extensions; live Excel 16.0 testing confirmed all three work natively.)*

| Test Case | Filter (`Year \| Region \| Category`) | Sales (₹) | Profit (₹) | Margin | Orders | Top Sub-Category | Top City | Errors | Result |
|---|---|---:|---:|---:|---:|---|---|---:|---|
| 1. Baseline | `All \| All \| All` | 1,49,56,982 | 37,47,121 | 25.1% | 9,994 | Health Drinks | Kanyakumari | 0 | **PASS** |
| 2. Single Year | `2018 \| All \| All` | 49,77,512 | 12,44,183 | 25.0% | 3,312 | Health Drinks | Kanyakumari | 0 | **PASS** |
| 3. Single Region | `All \| South \| All` | 24,40,461 | 6,23,563 | 25.6% | 1,619 | Health Drinks | Kanyakumari | 0 | **PASS** |
| 4. Single Category | `All \| All \| Snacks` | 22,37,546 | 5,68,179 | 25.4% | 1,514 | Cookies | Kanyakumari | 0 | **PASS** |
| 5. Combined 3-Way | `2018 \| West \| Snacks` | 2,49,934 | 61,944 | 24.8% | 162 | Cookies | Tirunelveli | 0 | **PASS** |
| 6. Single-Order Edge | `All \| North \| All` | 1,254 | 401 | 32.0% | 1 | Masalas | Vellore | 0 | **PASS** |
| 7. Empty Group | `2018 \| North \| Snacks` | 0 | 0 | 0.0% | 0 | *(blank)* | *(blank)* | 0 | **PASS** |
| 8. Reset | `All \| All \| All` | 1,49,56,982 | 37,47,121 | 25.1% | 9,994 | Health Drinks | Kanyakumari | 0 | **PASS** |

**Interactive Testing Verdict:** **PASS (8/8).** Every KPI, dynamic Top-10 ranking, and chart source range responds cleanly with zero `#DIV/0!` or `#N/A` errors even on empty selections.

## Recommended Actions

1. Convert `Data!A1:N9995` to an Excel Table (`SupermartData`) and replace hardcoded `Year` and `Month` strings with `=TEXT([@[Order Date]],"yyyy")` and `=TEXT([@[Order Date]],"yyyy-mm")` (`M-1`).
2. Save the workbook with `Dashboard` active (`A1`) and strip OneDrive `absPath` and personal author metadata (`M-2`).
