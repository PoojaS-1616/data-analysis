# Data Cleaning Process

**Project:** Amazon India Business Performance Dashboard
**Dataset:** 10,000 synthetic e-commerce order records (`2024-01-01` to `2026-08-30`)

## Overview & Data Provenance

This project uses a **synthetic (simulated) dataset** designed to demonstrate end-to-end Excel data validation, modeling, PivotTable ranking, and executive dashboard design. It does **not** represent confidential internal Amazon India sales data.

Before building the dashboard, the dataset was validated for missing values, duplicate records, data types, numeric bounds, arithmetic consistency, and label standardization. The primary technical issue found during preparation was that `Order_Date` values were stored as text strings and were converted into true Excel date serials. **Zero records were removed, and zero source values were altered to manufacture insights.**

## Original Columns

`Order_ID`, `Order_Date`, `Category`, `Product`, `Quantity`, `Unit_Price_INR`, `Discount_Pct`, `Total_Sales_INR`, `Profit_INR`, `Payment_Method`, `Fulfillment`, `Order_Status`, `Ship_State`

One calculated helper column (`Order_Month`) was added inside the `RawData` Excel Table during preparation.

## Validation Checks (Verified Across All 10,000 Records)

| Check | Verified Result | Action |
|---|---|---|
| Total record count | 10,000 order rows (`RawData` table `A1:N10001`; trailing blank row `10002` removed during remediation) | All 10,000 records retained |
| Missing / blank values | 0 missing values across all 14 columns (140,000 cells) | No rows dropped or imputed |
| Duplicate records | 0 duplicate full rows; 0 duplicate rows excluding `Order_ID` | No duplicates removed |
| Duplicate `Order_ID` | 0 duplicates (`IN-AMD-100000` through `IN-AMD-109999`) | All records retained |
| `Order_Date` data type | 10,000 / 10,000 verified true Excel date serials (`2024-01-01` to `2026-08-30`) | Text dates converted prior to modeling |
| `Order_Month` alignment | 0 mismatches against `YYYY-MM` of `Order_Date` across 10,000 rows | Structured formula `=TEXT([@[Order_Date]],"yyyy-mm")` applied |
| Numeric fields & bounds | 0 blanks, 0 text entries, 0 negative values across `Quantity` (1–4), `Unit_Price_INR` (₹150.27–₹34,992.80), `Discount_Pct` (0%–25%), `Total_Sales_INR` (₹118.82–₹1,39,647.92), `Profit_INR` (₹0–₹45,596.30) | Values retained as supplied |
| Sales arithmetic check | `Total_Sales_INR = Quantity × Unit_Price_INR × (1 - Discount_Pct)` verified within ₹0.005 rounding on all 10,000 rows | Confirmed consistent |
| Profit vs Status check | 985 / 985 Returned & Cancelled rows have `Profit_INR = 0`; 9,015 / 9,015 Delivered & Shipped rows have positive profit; 0 rows with `Profit_INR > Total_Sales_INR` | Confirmed consistent |
| Text label consistency | 0 leading/trailing spaces; exact canonical labels across Category (5), Product (25, 1:1 with Category), Payment_Method (5), Fulfillment (3), Order_Status (4), Ship_State (10) | No label corrections required |

### Discount Validation

`Discount_Pct` stores discounts as decimal fractions (`0.00`, `0.05`, `0.10`, `0.15`, `0.20`, `0.25`):

| Check | Verified Result |
|---|---|
| Minimum discount | `0.00` (0%) |
| Maximum discount | `0.25` (25%) |
| Missing discount values | 0 |
| Negative discount values | 0 |

### Canonical Text Labels Verified

- **Category (5):** `Electronics & Mobiles`, `Home & Kitchen`, `Apparel & Fashion`, `Beauty & Personal Care`, `Pantry & Groceries`
- **Order_Status (4):** `Delivered`, `Shipped`, `Returned`, `Cancelled`
- **Fulfillment (3):** `Amazon (FBA)`, `Seller Flex`, `Merchant (FBM)`
- **Payment_Method (5):** `UPI`, `Credit/Debit Card`, `Cash on Delivery (COD)`, `Net Banking`, `Amazon Pay Later`
- **Ship_State (10):** `Maharashtra`, `Karnataka`, `Delhi`, `Tamil Nadu`, `Uttar Pradesh`, `Telangana`, `West Bengal`, `Gujarat`, `Rajasthan`, `Kerala`

## Synthetic Dataset Characteristics & Domain-Plausibility Notes

Domain-plausibility checks on the prepared dataset identified clear synthetic-generation patterns that must be understood when interpreting results:

1. **Uniform category-wide unit pricing:** All five products within each category share an identical uniform price range:
   - `Electronics & Mobiles`: ₹800–₹34,993 (all 5 items—including `Laptop Backpack` and `Power Bank 20000mAh`—have medians of ~₹17,300–₹18,100)
   - `Home & Kitchen`: ₹500–₹8,000
   - `Apparel & Fashion`: ₹352–₹3,000
   - `Beauty & Personal Care`: ₹202–₹1,500
   - `Pantry & Groceries`: ₹150–₹1,200
2. **Uniform per-order profit margins:** Across all 5 categories, Delivered and Shipped orders follow the same 12.0%–35.0% per-order margin distribution (mean 23.3%–23.7%).

**Handling decision:** Original source values were intentionally preserved without artificial price/margin adjustments, and these synthetic characteristics are disclosed transparently in both `README.md` and the `Dashboard` subtitle.

## Date Correction & `Order_Month` Helper Column

During initial preparation, `Order_Date` values were stored as text strings (`=ISNUMBER(B2)` returned `FALSE`). They were converted into Excel date serials and formatted consistently.

To reproduce date conversion on a raw text-date column:
1. Confirm source date order (DMY vs MDY).
2. Select `Order_Date` → **Data → Text to Columns** → **Delimited** → **Next** → select **Date** with the matching order → **Finish**.
3. Apply a consistent display format and verify `=ISNUMBER()` returns `TRUE` across all rows (verified **10,000 / 10,000 `TRUE`** on the published workbook).

The `Order_Month` helper column in `RawData` derives the `YYYY-MM` grouping key using a structured table reference:

```excel
=TEXT([@[Order_Date]],"yyyy-mm")
```

## Returned and Cancelled Orders

Returned (485) and Cancelled (500) orders are valid operational outcomes, not data-cleaning errors, and were retained in full to support return/cancellation rate analysis and segment comparisons. Because these 985 rows retain a recorded sales value (₹1.56 crore combined) while carrying `Profit_INR = 0`, their sales value is documented as **associated recorded sales value**, not confirmed financial loss.

## Audit-Trail Limitation

The pre-cleaning raw file (containing the original text-formatted `Order_Date` values before Text-to-Columns conversion) was not archived in the repository, so the pre-conversion state cannot be independently re-executed from the repo alone. However, the post-cleaning state of all 10,000 records inside `Raw_Data` has been independently verified against every validation check above.
