# Excel Technical Audit

**Project:** Amazon India Business Performance Dashboard
**Audit date:** 2026-11-19
**Workbook audited:** `Amazon_India_Business_Performance_Dashboard.xlsx` (1,421,449 bytes, git blob `5d83014364f72c89d5a83e9c3b39202343cc7b5e`)
**Verification environments:**
- Static XML & Python (`openpyxl 3.1.5`, `zipfile`) inspection of the untouched repository file.
- Dynamic recalculation & PivotTable refresh testing on an **isolated temporary copy** in **Microsoft Excel 16.0** via COM automation (original file SHA-256 verified unchanged afterwards).

---

## 1. Workbook Structure Overview

The workbook contains **11 visible worksheets**, **1 Excel Table** (`RawData`), **1 PivotTable** (`PivotTable1`), **9 native charts** (all on `Dashboard`), **0 VBA macros**, **0 defined names**, and **0 external data links**.

| # | Worksheet | Used Range | Purpose |
|---|---|---|---|
| 1 | `Dashboard` | `A1:P138` (charts to col `T`) | Executive dashboard: 12 KPI cards, 9 charts across 4 sections |
| 2 | `Raw_Data` | `A1:N10002` | Source table `RawData` (`A1:N10001`, 10,000 rows + header) + 1 blank trailing row |
| 3 | `Monthly_KPIs` | `A1:G33` | 32 monthly rows (`2024-01` to `2026-08`) |
| 4 | `Category_Analysis` | `A1:D6` | 5 categories: Sales, Profit, Units_Sold |
| 5 | `Top_Products` | `A1:E11` | Bridge sheet linking `Product_Summary` to Dashboard Chart 4 |
| 6 | `Order_Status` | `A1:C5` | 4 statuses: Order counts & share of total orders |
| 7 | `Category_Returns_Cancellations` | `A1:E6` | 5 categories: Returned, Cancelled, Total Orders, Combined % |
| 8 | `Payment_Analysis` | `A1:C6` | 5 payment methods: Sales, Profit |
| 9 | `Fulfillment_Analysis` | `A1:C4` | 3 fulfilment channels: Sales, Profit |
| 10 | `State_Analysis` | `A1:D11` | 10 states: Sales, Profit, Orders |
| 11 | `Product_Summary` | `A1:D11` | PivotTable (`PivotTable1`) ranking Top 10 products by Sales |

**Finding M-6 (Major):** `xl/workbook.xml` records `activeTab="10"` (`Product_Summary`) and `firstSheet="8"`. Opening the file lands the user on the raw PivotTable instead of `Dashboard`. Additionally, `xl/workbook.xml` contains a personal OneDrive path (`https://d.docs.live.net/6BD3F40DABD6C24A/Documents/`).

---

## 2. Data Integrity Audit (`Raw_Data`)

| Check | Result | Evidence / Details |
|---|---|---|
| Total record count | **PASS** | Exactly 10,000 order rows (`A2:N10001`), matching `RawData` table ref `A1:N10001`. Row 10002 is blank (outside table, minor XML bloat `m-4`). |
| Missing / blank values | **PASS** | 0 missing or blank cells across all 14 columns × 10,000 rows (140,000 cells). |
| Duplicate records | **PASS** | 0 duplicate full rows; 0 duplicate rows excluding `Order_ID`. |
| Duplicate `Order_ID` | **PASS** | 10,000 unique IDs (`IN-AMD-100000` through `IN-AMD-109999`). |
| Data types | **PASS** | `Order_Date`: 10,000/10,000 true Excel date serials (midnight timestamps); `Quantity`: 10,000 ints; currency/discount cols: 100% numeric; text cols: 100% strings. |
| Date validity & range | **PASS** | `2024-01-01` to `2026-08-30` (note: PivotCache metadata shows `maxDate="2026-08-31T00:00:00"` while actual max record in both table and cache records is `2026-08-30`). |
| `Order_Month` alignment | **PASS** | 0 mismatches between `Order_Month` cached values and `Order_Date.strftime("%Y-%m")` across all 10,000 rows. |
| Label consistency | **PASS** | 0 leading/trailing spaces across Category (5), Payment_Method (5), Fulfillment (3), Order_Status (4), Ship_State (10), Product (25). Each product maps uniquely to 1 category. |
| Arithmetic & bounds | **PASS** | `Quantity` ∈ [1, 4]; `Unit_Price_INR` ∈ [150.27, 34,992.80]; `Discount_Pct` ∈ {0, 0.05, 0.10, 0.15, 0.20, 0.25}; `Total_Sales_INR` = `Quantity × Unit_Price_INR × (1 - Discount_Pct)` within ₹0.005 rounding on all 10,000 rows; 0 negative values; 0 rows with `Profit_INR > Total_Sales_INR`; all 985 Returned/Cancelled rows have `Profit_INR = 0`; all 9,015 Delivered/Shipped rows have positive profit. |
| Domain plausibility | **CRITICAL (`C-1`)** | Every product within a category shares an identical uniform price distribution (e.g., `Laptop Backpack`, `Power Bank 20000mAh`, and `5G Smartphone` all span ₹800–₹34,993 with median ~₹17.8k), and every category has identical per-order margins (12.0%–35.0%, mean 23.3%–23.7%). Undisclosed synthetic data. |

---

## 3. Formula Audit

Every formula across all 11 worksheets was extracted and verified. **Zero formula errors** (`#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#N/A`, `#NUM!`) exist in any cell (verified both statically and after `CalculateFull` in Excel 16.0).

| Sheet / Range | Formula Pattern | Assessment |
|---|---|---|
| `Raw_Data!C2:C10001` | `=TEXT(B2,"yyyy-mm")` (10,000/10,000 consistent) | **PASS (minor `m-5`)**: Valid table calculated column; propagates on row insertion (verified in Excel 16.0). Using `=TEXT([@[Order_Date]],"yyyy-mm")` would be cleaner structured-reference syntax. |
| `Dashboard!A8,D8,G8,J8,L8,N8` | `=SUM(RawData[Total_Sales_INR])`, `=SUM(RawData[Profit_INR])`, `=COUNTA(RawData[Order_ID])`, `=SUM(RawData[Quantity])`, `=A8/G8`, `=D8/A8` | **PASS**: Dynamic structured references; zero hardcoded KPI values. |
| `Dashboard!A74:N74` | Direct links to `Order_Status!B2:B5` and `C4:C5` | **PASS**: Properly linked. |
| `Monthly_KPIs!B2:G33` | `SUMIFS`/`COUNTIFS` on `RawData[Order_Month]`, `=IFERROR(B2/D2,0)`, `=IFERROR(C2/B2,0)` | **PASS**: Consistent across all 32 months; `IFERROR` guards division by zero. |
| `Category_Analysis!B2:D6` | `SUMIFS` on `RawData[Category]` | **PASS**: Complete and consistent. |
| `Order_Status!B2:C5` | `=COUNTIFS(RawData[Order_Status],$A2)`, `=B2/COUNTA(RawData[Order_ID])` | **PASS**: Denominator correctly uses total recorded orders (10,000). |
| `Category_Returns_Cancellations!B2:E6` | Dual-criteria `COUNTIFS` + `=IF(D2=0,"",(B2+C2)/D2)` | **PASS**: Accurate category-level combined rate. |
| `Payment_Analysis!B2:C6`, `Fulfillment_Analysis!B2:C4`, `State_Analysis!B2:D11` | `SUMIFS` and `COUNTIFS` on structured table columns | **PASS**: Consistent, zero broken ranges. |
| `Top_Products!A2:E11` | Positional links `=IF(Product_Summary!A2="","",Product_Summary!A2)` + `=IF(A2="","",INDEX(RawData[Category],MATCH(A2,RawData[Product],0)))` | **PASS (minor `m-3`)**: Works cleanly with current 25 unique products; positional references rely on PivotTable staying at `A1:D11` without grand totals (`rowGrandTotals="0" colGrandTotals="0"`). |

**Note on README formula claims:** `README.md` line 94 lists `Excel Tables, structured references, SUMIFS, COUNTIFS, TEXT, INDEX/MATCH, PivotTables and charts`. Every single listed feature is genuinely present and used. (`AVERAGEIFS` is not claimed and not used.)

**Formula gaps:**
- **M-1 (Major):** Six metrics highlighted in `README.md` (23.67% margin excl. R/C, 9.85% combined R+C rate, ₹1.56 Cr R+C sales value, 2024 vs 2025 annual sales & +0.73% growth, and dimension % shares) have no formulas anywhere in the workbook.
- **m-6 (Minor):** Dimension label lists (`Monthly_KPIs!A2:A33`, `Category_Analysis!A2:A6`, etc.) and `Dashboard!A2` subtitle are manually typed (honestly documented in `README.md` lines 79–82).

---

## 4. PivotTable & Live Refresh Verification (Microsoft Excel 16.0)

`PivotTable1` on `Product_Summary!A1:D11` was inspected in XML and tested live on an isolated copy in Microsoft Excel 16.0:

- **Source:** Excel Table `RawData` (`cacheSource type="worksheet"`, `worksheetSource name="RawData"`, `recordCount="10000"`).
- **Configuration:** Row field = `Product` (sorted descending by `Sum of Total_Sales_INR`, `top10 val="10"` filter); Data fields = `Sum of Total_Sales_INR`, `Sum of Profit_INR`, `Sum of Quantity`; `refreshOnLoad="1"` enabled; Grand totals disabled.
- **Test 1 — Baseline RefreshAll + CalculateFull:**
  - `xl.Calculation` = `xlCalculationAutomatic`.
  - After `$wb.RefreshAll()` and `$xl.CalculateFull()`, all 12 Dashboard KPIs and all 10 `Top_Products` values matched cached values identically. Error cells across all 10 non-raw sheets = **0**.
- **Test 2 — Dynamic Table Extension Test (Synthetic Row Append):**
  - Appended 1 synthetic row to `RawData` (`2026-08-15`, `Electronics & Mobiles`, `Laptop Backpack`, ₹10,00,000 sales, ₹2,00,000 profit).
  - `Order_Month` auto-filled `=TEXT(B10002,"yyyy-mm")` → `"2026-08"`.
  - `Dashboard!G8` automatically updated `10000` → `10001`; `Dashboard!A8` updated `₹15,57,89,893.89` → `₹15,67,89,893.89`; `Monthly_KPIs!B33` (`2026-08`) updated `+₹10,00,000`.
  - Pre-refresh `Top_Products!C2` remained `₹2,65,29,187.41`; post-`RefreshAll()` it updated to `₹2,75,29,187.41`.
- **Verdict:** **PASS.** Dynamic table expansion and PivotTable refresh work exactly as documented in `README.md`.

---

## 5. Chart Technical Audit (9 Charts on `Dashboard`)

All 9 charts are native Excel charts (`pivotSource: False`) referencing the summary sheets:

| Chart | Title | Type | Data Range | Technical Check |
|---|---|---|---|---|
| Chart 1 | Monthly Recorded Sales Value and Profit | Dual-axis Line | `Monthly_KPIs!A2:C33` | Ranges valid; dual-axis scaling (5:1) plots Profit above Sales (`M-4`). |
| Chart 2 | Recorded Sales Value and Profit by Category | Clustered Column | `Category_Analysis!A2:C6` | Ranges valid; no data labels or axis titles (`m-7`). |
| Chart 3 | Ordered Quantity by Category | Pie | `Category_Analysis!A2:A6, D2:D6` | Ranges valid; `%` data labels enabled. |
| Chart 4 | Top 10 Products by Recorded Sales Value | Horizontal Bar | `Top_Products!A2:A11, C2:C11` | Ranges valid; category axis not reversed (#1 at bottom, `M-4`); redundant single-series legend (`m-7`). |
| Chart 5 | Order Status Distribution | Pie | `Order_Status!A2:B5` | Ranges valid; `%` data labels enabled; inconsistent theme colors (`M-4`). |
| Chart 6 | Returned and Cancelled Orders by Category | Stacked Column | `Category_Returns_Cancellations!A2:C6` | Ranges valid; plots counts instead of `%` rate (`E2:E6` unused); inconsistent colors (`M-4`). |
| Chart 7 | Recorded Sales Value and Profit by Payment Method | Clustered Column | `Payment_Analysis!A2:C6` | Ranges valid. |
| Chart 8 | Recorded Sales Value and Profit by Fulfilment Method | Clustered Column | `Fulfillment_Analysis!A2:C4` | Ranges valid; anchored at row 97 vs Chart 7 at row 98 (`M-4`). |
| Chart 9 | Recorded Sales Value and Profit by State | Horizontal Bar | `State_Analysis!A2:C11` | Ranges valid; category axis not reversed (`Maharashtra` at bottom, `M-4`). |

---

## Recommended Actions

1. Open the workbook, select `Dashboard!A1`, and re-save so `activeTab="0"` (`Dashboard`).
2. Run **File → Info → Check for Issues → Inspect Document** to strip the OneDrive `absPath` URL (`M-6`).
3. Add formulas for the 6 untraceable README metrics (`M-1`) and convert `Order_Month` to `=TEXT([@[Order_Date]],"yyyy-mm")` (`m-5`).
4. Rename `Units_Sold` headers on `Category_Analysis!D1` and `Top_Products!E1` to `Ordered_Quantity` (`m-7`) and remove blank row 10002 on `Raw_Data` (`m-4`).
