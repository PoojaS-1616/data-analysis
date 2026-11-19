# Documentation Audit

**Project:** Amazon India Business Performance Dashboard
**Audit date:** 2026-11-19
**Files audited:** `README.md` (108 lines, 8,131 bytes) and `Data_Cleaning_Process.md` (154 lines, 5,710 bytes).

---

## 1. README.md Audit Checklist

| Section / Element | Status | Evidence & Findings |
|---|---|---|
| Project overview & business objectives | **PASS** | Lines 1–26 clearly state scope (10,000 orders, Jan 2024–Aug 2026) and organize objectives into 4 business questions matching the 4 dashboard sections. |
| Dashboard preview & image link | **PARTIAL (`M-3`)** | Line 7 (`./Amazon_Indian_Dashboard_Preview.png`) resolves cleanly on GitHub, but the image is truncated to Section 1 and includes raw Excel UI chrome. |
| KPI definitions & analytical caveats | **PASS** | Line 27 and lines 90–91 clearly distinguish recorded sales from delivered revenue, note Shipped orders are in progress, and state returned/cancelled sales value is not confirmed financial loss. |
| Business insights accuracy | **PASS (with `M-1`, `C-1`)** | All 18 reported metrics reconcile 100% with `Raw_Data`. However, 6 headline figures are not traceable to any workbook cell (`M-1`), and the synthetic/simulated nature of the dataset is never disclosed (`C-1`). |
| Recommendations quality | **PASS** | Lines 47–55 offer 4 grounded, non-speculative recommendations that avoid causal overclaiming. Minor gap: Recommendation 4 asks for analyses (Jan–Aug 2026 YoY and 2024→2025 volume/AOV split) that could be answered directly from the current data (`M-5`). |
| Technical implementation & sheet guide | **PASS** | Lines 57–72 accurately list all 11 worksheets, `RawData` table, `Order_Month` column, and Excel features used (all verified present). |
| Workbook update instructions & limitations | **PASS** | Lines 73–83 and 96–103 give accurate step-by-step instructions (`Automatic` calc, `Data → Refresh All`, `Ctrl+Alt+F9`) and honestly disclose manual helper lists and static subtitle. |
| Dataset description | **PARTIAL (`C-1`)** | Lines 84–91 list all 14 columns accurately, but omit data source/provenance and do not state that the dataset is synthetic. |
| **Workbook download URL** | **FAIL (`M-2`)** | Line 98 links to `https://raw.githubusercontent.com/PoojaS-1616/data-analyst-portfolio/main/amazon-indian-business-dashboard-main/Amazon_India_Business_Performance_Dashboard.xlsx` — pointing to **`data-analyst-portfolio`** instead of the actual repository **`data-analysis`**. Currently works only via a GitHub rename redirect (HTTP 200, same blob hash), which is fragile and misleading. |
| Cross-reference to `Data_Cleaning_Process.md` | **MISSING (`m-2`)** | `README.md` never links to `Data_Cleaning_Process.md`, reducing its discoverability for reviewers. |

---

## 2. Data_Cleaning_Process.md Audit Checklist

| Section / Element | Status | Evidence & Findings |
|---|---|---|
| Overview & column listing | **PASS** | Accurately states 10,000 records, 0 removed, 13 original columns + `Order_Month` helper. |
| Validation checks | **PASS** | Missing values (0), duplicate rows (0), duplicate Order IDs (0), numeric bounds, discount bounds (`0.00`–`0.25`, 0 missing, 0 negative), and text consistency all verified true against `Raw_Data`. |
| Date conversion documentation | **PARTIAL (`m-2`)** | Transparently notes `Order_Date` was text and converted to Excel dates, and provides a reproducible Text-to-Columns procedure. However, lines 92, 103, and 147–154 explicitly admit the original conversion method and post-conversion `=ISNUMBER()` results were not recorded. |
| `Order_Month` derivation | **PASS** | Accurately documents `=TEXT(B2,"yyyy-mm")` (verified across all 10,000 rows). |
| Returned & cancelled order handling | **PASS** | Correctly explains retaining Returned/Cancelled records and not treating their sales value as confirmed loss. |
| Synthetic data & price-plausibility check | **FAIL (`C-1`)** | No outlier or domain-plausibility check is documented; the uniform ₹800–₹35,000 pricing across `Laptop Backpack` and `5G Smartphone` went unflagged. |
| Terminology consistency | **Minor (`m-8`)** | Uses UK `fulfilment` in prose while the dataset/workbook uses US `Fulfillment` (`Raw_Data!L1`, `Fulfillment_Analysis`). |

---

## 3. Claims Lacking Supporting Evidence

1. **Unverified pre-cleaning state:** `Data_Cleaning_Process.md` claims `Order_Date` was originally stored as text and `=ISNUMBER(B2)` returned `FALSE`, while also noting the pre-cleaning raw file and post-conversion results were not retained. The current workbook's dates are verified valid Excel dates, but the pre-cleaning state is **NOT VERIFIED**.
2. **Untraceable README metrics (`M-1`):** Six metrics in `README.md` (23.67% margin excl. R/C, 9.85% combined rate, ₹1.56 Cr R/C value, ₹5.70 Cr vs ₹5.74 Cr / +0.73% annual growth, and dimension `%` shares) are numerically accurate against `Raw_Data` but have no supporting formula in the workbook.

## Recommended Actions

1. **Fix `README.md` line 98** to point to `PoojaS-1616/data-analysis` (or a relative link `./Amazon_India_Business_Performance_Dashboard.xlsx`).
2. **Add a Data Provenance / Synthetic Data note** in both `README.md` and `Data_Cleaning_Process.md` explicitly stating the dataset is simulated/synthetic for portfolio demonstration and noting the uniform category price/margin ranges.
3. **Add a link** from `README.md` to `[Data_Cleaning_Process.md](./Data_Cleaning_Process.md)`.
4. **Update `Data_Cleaning_Process.md`** to close the open "Documentation Limitations" note (or confirm post-conversion `=ISNUMBER()` = 10,000/10,000 `TRUE` on the current workbook).
