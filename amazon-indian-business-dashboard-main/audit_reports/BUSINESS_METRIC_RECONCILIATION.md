# Business Metric Reconciliation

**Project:** Amazon India Business Performance Dashboard
**Audit date:** 2026-11-19
**Source audited:** `Raw_Data` sheet (Excel Table `RawData`, `A1:N10001`) in `Amazon_India_Business_Performance_Dashboard.xlsx`, git blob `5d83014364f72c89d5a83e9c3b39202343cc7b5e` on `main` @ `d4cb3cb`.

## Method

1. I recalculated each metric independently in Python (openpyxl, reading cached cell values) directly from the 10,000 source rows. I did not use the workbook's summary sheets for this step.
2. Separately, I opened a **temporary copy** of the workbook in Microsoft Excel 16.0 (COM automation). I ran **Data → Refresh All** and **CalculateFull** on it, then read the dashboard values. The values after recalculation were identical to the cached values. The original file's SHA-256 was unchanged afterwards.
3. I compared each result with the claim in `README.md`.

Tolerance: a README value is a match if it equals the independent value at the precision the README states.

## Reconciliation table

| # | Metric (README) | Independent value | Formula / denominator | In workbook? | Result |
|---|---|---|---|---|---|
| 1 | ≈ ₹15.58 crore recorded sales value | ₹15,57,89,893.89 (₹15.579 cr) | Σ `Total_Sales_INR`, all 10,000 rows, all statuses | Yes: `Dashboard!A8` `=SUM(RawData[Total_Sales_INR])` | ✅ MATCH |
| 2 | ≈ ₹3.32 crore recorded profit | ₹3,31,67,008.49 (₹3.317 cr) | Σ `Profit_INR`, all rows | Yes: `Dashboard!D8` | ✅ MATCH |
| 3 | 21.29% recorded profit margin | 21.2896% | Σ Profit ÷ Σ Sales (all statuses) | Yes: `Dashboard!N8` `=D8/A8` (shown as 21.3%) | ✅ MATCH |
| 4 | 23.67% margin excl. returned & cancelled | 23.6669% | Σ Profit ÷ Σ Sales where status ∈ {Delivered, Shipped}; denominator ₹14,01,41,151.25 (9,015 orders) | **No.** Calculated only in the README | ✅ MATCH (not traceable) |
| 5 | 10,000 total orders | 10,000 | COUNTA `Order_ID`; 10,000 distinct IDs | Yes: `Dashboard!G8` | ✅ MATCH |
| 6 | 485 returned orders | 485 | COUNTIFS status = "Returned" | Yes: `Order_Status!B4` → `Dashboard!G74` | ✅ MATCH |
| 7 | 500 cancelled orders | 500 | COUNTIFS status = "Cancelled" | Yes: `Order_Status!B5` → `Dashboard!J74` | ✅ MATCH |
| 8 | 4.85% return rate | 4.85% | 485 ÷ 10,000 (all recorded orders) | Yes: `Order_Status!C4` | ✅ MATCH |
| 9 | 5.00% cancellation rate | 5.00% | 500 ÷ 10,000 | Yes: `Order_Status!C5` | ✅ MATCH |
| 10 | 9.85% combined rate | 9.85% | 985 ÷ 10,000 | **No.** Not in any cell | ✅ MATCH (not traceable) |
| 11 | ≈ ₹1.56 crore associated sales value | ₹1,56,48,742.64 (Returned ₹79,60,583.45 + Cancelled ₹76,88,159.19) = 10.04% of recorded sales | Σ Sales where status ∈ {Returned, Cancelled} | **No** | ✅ MATCH (not traceable) |
| 12 | ≈ 79% sales from Electronics & Mobiles (from 30% of orders) | 79.32% of sales; 30.45% of orders | ₹12,35,69,507 ÷ ₹15,57,89,894; 3,045 ÷ 10,000 | Partly: the ₹ value is in `Category_Analysis!B2`; the share is not computed anywhere | ✅ MATCH |
| 13 | ≈ 50% sales from UPI | 50.40% (orders: 49.72%) | ₹7,85,15,436 ÷ total sales | Partly: `Payment_Analysis!B2`; share not computed | ✅ MATCH |
| 14 | ≈ 69% sales from FBA | 69.02% (orders: 70.54%) | ₹10,75,28,288 ÷ total sales | Partly: `Fulfillment_Analysis!B2`; share not computed | ✅ MATCH |
| 15 | ≈ 49% sales from MH + KA + DL | 48.997% | (₹2,95,54,237 + ₹2,44,15,704 + ₹2,23,61,687) ÷ total sales | Partly: `State_Analysis!B2:B4`; share not computed | ✅ MATCH |
| 16 | 2024→2025 annual sales growth ≈ 0.73% (₹5.70 cr → ₹5.74 cr) | +0.726% (₹5,70,12,820 → ₹5,74,26,873) | (S2025 − S2024) ÷ S2024, calendar years | **No.** No annual summary exists in the workbook | ✅ MATCH (not traceable) |
| 17 | Category returned+cancelled share 8.8%–10.6% | 8.81% (Pantry) – 10.61% (Beauty) | (R + C) ÷ category orders | Yes: `Category_Returns_Cancellations!E2:E6` | ✅ MATCH |
| 18 | KPI: Ordered quantity 24,926 / AOV ₹15,579 | 24,926 / ₹15,578.99 | Σ Quantity; Sales ÷ Orders (all statuses) | Yes: `Dashboard!J8`, `L8` | ✅ MATCH |

**Summary:** 18 of 18 reported metrics reconcile. **No numerical discrepancies were found.** However, 6 headline figures (rows 4, 10, 11, 16, and the shares in rows 12–15) appear only in the README and **cannot be traced to any workbook cell**. See finding M-1.

## Interpretation notes and definitional checks

| Check | Finding | Severity |
|---|---|---|
| Is recorded sales value presented as delivered revenue? | No. The KPI is labelled "Recorded Sales Value", and the README states that it includes all statuses and is not delivered sales. ✅ | — |
| Are returned/cancelled values presented as losses? | No. README line 37 and Data_Cleaning_Process.md both say this is "not confirmed financial loss". ✅ | — |
| Are shipped orders classified as delivered? | No. Delivered (8,147) and Shipped (868) are reported separately. ✅ | — |
| Denominator of the 23.67% margin | It includes **Shipped** orders, which are still in progress and may later be returned or cancelled. **Delivered-only margin = 23.59%** (₹2,96,97,473 ÷ ₹12,58,94,210). The label "excluding returned and cancelled" is accurate but incomplete. | Minor (m-9) |
| Why 23.67% > 21.29% | This is **mechanical**: every Returned/Cancelled row has `Profit_INR = 0` (985/985 rows), so excluding them only shrinks the denominator. It is not evidence of better underlying profitability. The README does not explain this. | Minor (m-9) |
| Partial-year 2026 | The README correctly excludes Jan–Aug 2026 from the full-year comparison. ✅ It does **not** report the like-for-like period, which changes the narrative (see below). | Major (M-5) |
| Profit definition | Profit is taken as supplied. No cost data exists, so profit cannot be validated. Per-order margin on Delivered/Shipped rows is uniformly 12.0%–35.0% in every category (mean 23.3–23.7%). | Info. See C-1 |

### Like-for-like period analysis (missing from the project)

| Period | Orders | Recorded sales | Profit |
|---|---:|---:|---:|
| Jan–Aug 2024 | 2,495 | ₹3,88,62,189 | ₹82,70,749 |
| Jan–Aug 2025 | 2,482 | ₹3,84,59,822 | ₹80,59,153 |
| Jan–Aug 2026 | 2,551 | ₹4,13,50,201 | ₹88,33,476 |

- Jan–Aug 2026 vs Jan–Aug 2025: **sales +7.51%**, orders +2.78%, profit +9.61%.
- Jan–Aug 2025 vs Jan–Aug 2024: sales −1.04%.
- Full-year 2024→2025 growth of +0.73% breaks down as orders **+1.05%** and AOV **−0.32%**. Recommendation 4 asks for this decomposition, but the project does not perform it.

The README's "slow growth" narrative is arithmetically correct for full calendar years. It omits the most recent like-for-like signal, which is materially positive.

### Segment rates not reported (relevant to requirements 6–8)

| Segment | Orders | Returned % | Cancelled % | R+C % | Margin |
|---|---:|---:|---:|---:|---:|
| Amazon (FBA) | 7,054 | 4.76% | 4.55% | 9.31% | 21.28% |
| Seller Flex | 1,966 | 4.93% | 6.31% | 11.24% | 21.84% |
| Merchant (FBM) | 980 | 5.31% | 5.61% | 10.92% | 20.33% |
| UPI | 4,972 | 4.87% | 5.01% | 9.88% | 21.21% |
| Credit/Debit Card | 2,074 | 5.45% | 5.59% | 11.04% | 21.00% |
| COD | 1,458 | 3.64% | 5.42% | 9.05% | 21.68% |
| Net Banking | 1,024 | 6.05% | 3.42% | 9.47% | 21.35% |
| Amazon Pay Later | 472 | 3.18% | 4.45% | 7.63% | 21.96% |

The largest deviations from the 9.85% overall rate are Seller Flex (+1.39 pp, ≈ +2.1 standard errors) and Amazon Pay Later (−2.22 pp, ≈ −1.6 SE). They are borderline, and Recommendation 3 correctly treats such gaps as hypotheses. None of these rates is computed in the workbook.

## Verdict for this phase

- **Numerical accuracy: PASS.** Every stated figure is correct.
- **Traceability: PARTIAL.** Several headline figures exist only in prose.
- **Interpretation: PASS with minor caveats.** The definitions are careful. Two improvements are needed: the Shipped-inclusion caveat and the like-for-like period.
