# Dashboard Design Audit

**Project:** Amazon India Business Performance Dashboard
**Audit date:** 2026-11-19
**Evidence inspected:**
1. `Amazon_Indian_Dashboard_Preview.png` (repository preview image).
2. Full visual renders of the entire `Dashboard` sheet (`A1:T138`, exported in 3 full-width sections from a temporary copy in Microsoft Excel 16.0).
3. Chart XML (`xl/charts/chart1.xml`–`chart9.xml`) and drawing anchors (`xl/drawings/drawing1.xml`).

---

## 1. Executive Visual Assessment

The dashboard has a **strong structural foundation**: a dark navy header banner, numbered business-question sections ("Q: How is the business performing overall?"), clean KPI cards with Indian rupee formatting (`₹15,57,89,894`), gridlines hidden (`showGridLines="0"`), and an intentional Amazon-inspired color palette (orange `#FF9900` for Sales, teal `#067D62` for Profit).

However, **multiple execution defects** across layout alignment, chart styling consistency, axis orientation, and the repository preview image prevent it from looking like a polished, executive-ready portfolio piece today.

---

## 2. Detailed Evaluation by Design Criterion

| Criterion | Rating | Evidence & Findings |
|---|---|---|
| **Visual hierarchy & storytelling** | **Strong** | 4 numbered sections, each framed by a plain-English business question (`Dashboard!A4:A5`, `A29:A30`, `A70:A71`, `A95:A96`). Logical flow from overall KPIs → Category/Product → Order Outcomes → Payment/Fulfilment/Geography. |
| **KPI readability** | **Good** | 12 KPI cards (rows 7–9 and 73–75) use large bold numbers, clear labels, Indian lakh/crore comma formatting, and semantic color accents (teal for Profit/Delivered, rust-orange for Returned/Cancelled). |
| **Alignment & grid consistency** | **Poor (`M-4`)** | **1. Right-edge overhang:** All section banners (`A1:P1`, `A4:P4`, `A29:P29`, `A70:P70`, `A95:P95`) and KPI strips (`A7:P9`, `A73:P75`) stop at column **P**, whereas full-width charts (Charts 1, 4, 9) and right-hand charts (Charts 3, 8) extend to column **T** (`col=19`), protruding ~25% past the right edge of every banner.<br>**2. Vertical stagger:** Chart 7 (`Payment Method`) starts at row 98 (`A98:J115`), while paired Chart 8 (`Fulfilment Method`) starts at row 97 (`K97:T114`)—a visible 1-row misalignment.<br>**3. Section 3 chart shift:** Chart 5 (`A77:I94`) has a left offset (`colOff=152400`) and Chart 6 ends at col `S` (`J77:S94`), differing from the `A:J` / `K:T` grid used in Sections 2 and 4. |
| **Colour & typography consistency** | **Fair (`M-4`)** | Charts 1, 2, 4, 7, 8, and 9 use bold black titles with Amazon orange (`#FF9900`) and teal (`#067D62`). **Charts 5 and 6** (`Order Status Distribution` and `Returned and Cancelled Orders by Category`) revert to Excel's default gray non-bold titles and default Office pastel colors (soft orange, light blue, purple, brown), looking visually pasted-in from a different workbook. |
| **Chart selection & axis readability** | **Fair (`M-4`, `m-7`)** | **1. Inverted horizontal bars:** Chart 4 (`Top 10 Products`) and Chart 9 (`State`) leave the vertical category axis in default order (`minMax`), placing the #1 product (`Laptop Backpack`) and #1 state (`Maharashtra`) at the **bottom** instead of the top.<br>**2. Dual-axis crossover (Chart 1):** Left axis (`Sales`: ₹0–₹70L) and right axis (`Profit`: ₹0–₹14L) use a 5:1 scale. Because margins are ~21.3% (>20%), the green Profit line sits **above** the orange Sales line in nearly every month, creating an immediate visual illusion that profit exceeds sales.<br>**3. Pie chart usage (Charts 3 & 5):** Acceptable for 4–5 categories with `%` labels, though a horizontal bar chart would make the 4.9% vs 5.0% Returned/Cancelled comparison clearer.<br>**4. Missing rate chart (Chart 6):** Plots raw Returned+Cancelled counts rather than the `%` rate already calculated in `Category_Returns_Cancellations!E2:E6`, visually overstating Electronics' relative return rate. |
| **Chart labels & clutter** | **Fair (`m-7`)** | Chart 4 (`Top 10 Products`) displays a redundant single-series legend (`Sales`). Bar/column charts (Charts 2, 4, 6, 7, 8, 9) have no data labels and no axis titles; long unscaled currency axis ticks (`₹14,00,00,000`) consume plot space where `₹ Cr` scaling would be cleaner. |
| **Repository preview image** | **Poor (`M-3`)** | `Amazon_Indian_Dashboard_Preview.png` captures only Section 1 plus the clipped title of Section 2—omitting 7 of the 9 charts and 6 of the 12 KPIs. It also exposes raw Excel UI chrome (column letters `A–Y`, row numbers, sheet tabs, scrollbars, and status bar `"Accessibility: Investigate"`). |
| **Executive-level usability** | **Moderate** | No interactive slicers (e.g., Year, Category, State) are included—acceptable for a formula-driven static dashboard, but limits executive self-service exploration. |

---

## 3. Portfolio Readiness Judgment

- **In its current state:** The dashboard shows clear analytical intent and clean KPI framing, but the **25% right-edge chart overhang**, **inverted Top-10/State bars**, **broken color/font theme on Charts 5–6**, **dual-axis Profit-above-Sales visual**, and **truncated Excel-window screenshot** noticeably detract from senior-analyst polish.
- **Effort to fix:** All visual defects are layout/formatting adjustments that can be resolved in ~60–90 minutes without altering the underlying data model.

## Recommended Actions

1. **Standardize grid width:** Either extend all headers/KPIs to `A:T` or resize all charts to fit `A:P` so every section aligns flush left and right.
2. **Fix chart alignment:** Align Chart 8 to row 98 (`K98:T115`) to match Chart 7, and align Charts 5–6 to the same column grid as Charts 2–3.
3. **Unify styling on Charts 5 & 6:** Apply the same bold black title font and cohesive brand palette used on the other 7 charts.
4. **Reverse category axes on Charts 4 & 9:** Enable *Categories in reverse order* (and set horizontal axis crosses at maximum category) so `Laptop Backpack` and `Maharashtra` appear at the top. Remove the redundant `Sales` legend on Chart 4.
5. **Fix Chart 1 dual-axis visual:** Adjust the secondary (Profit) axis maximum to `₹20,00,000` or `₹25,00,000` (or use a combo column-for-Sales + line-for-Profit chart) so Profit plots cleanly below Sales.
6. **Replace `Amazon_Indian_Dashboard_Preview.png`:** Export a clean, full-dashboard image (all 4 sections, zero Excel UI chrome) for `README.md`.
