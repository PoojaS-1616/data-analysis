# Dashboard Design Audit — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Audit Date:** 2026-11-19
**Evidence Inspected:**
1. Repository preview image `Supermart_Grocery_Dashboard_Preview.png`.
2. Full visual renders of the entire `Dashboard` sheet (`B1:S94`) exported in 3 full-width slices from an isolated copy in Microsoft Excel 16.0.
3. Chart XML (`xl/charts/chart1.xml`–`chart8.xml`) and drawing anchors (`xl/drawings/drawing1.xml`).

---

## 1. Visual & Usability Evaluation

| Criterion | Rating | Evidence & Findings |
|---|---|---|
| **Colour palette & typography** | **Strong** | Cohesive executive teal (`#0D9488` / `#0F766E`) + dark forest (`#113832`) palette applied consistently across the banner, KPI strip, and all 8 charts. Crisp sans-serif hierarchy. |
| **KPI design & filter placement** | **Strong** | Yellow dropdown filter bar (`D3`, `H3`, `L3`) with clear instructional cue (`◄ yellow cells are dropdown filters`) sits cleanly above the 6-card KPI banner (`B5:S7`). Indian lakh/crore comma formatting (`1,49,56,982`) is readable and consistent. |
| **Horizontal bar ordering** | **Strong** | Both `Top 10 Sub-Categories` (Chart 5) and `Top 10 Cities` (Chart 6) correctly place #1 (`Health Drinks`, `Kanyakumari`) at the top. |
| **Trend chart scaling (Chart 3)** | **Strong** | `Monthly Sales & Profit Trend (2015–2018)` uses a single Y-axis so Sales and Profit are visually proportional with zero dual-axis distortion. |
| **Layout alignment & overlap** | **Poor (`M-4`)** | **1. Text clipping overlap:** Chart 8 (`Yearly Sales & Profit`, anchored `col=1..10, colOff=41760`) physically overlaps the left edge of the `KEY TAKEAWAYS` panel (`K77:S94`), clipping the `"K"` in `"KEY TAKEAWAYS"` and the leading bullet dots (`•`) on all 4 bullets.<br>**2. Right-edge overhang:** Chart 3 (`Monthly Trend`) extends to `col=19, colOff=263880`, protruding slightly beyond the `B1:S1` banner and the other charts (`colOff=41760`). |
| **Chart selection & redundancy** | **Fair (`M-4`, `m-4`)** | **1. Redundant doughnut (Chart 1):** `Sales Share by Category` displays 7 nearly identical slices (`15%, 15%, 14%, 14%, 14%, 14%, 14%`)—both hard to compare on a doughnut and redundant with `Sales vs Profit by Category` (Chart 4) directly below it.<br>**2. Missing data labels (Chart 7):** `Profit Margin by Discount Band` plots 5 visually flat bars (`24.8%–25.7%`) with no data labels, making exact values unreadable.<br>**3. Unreadable sliver (Chart 2):** `North` (1 order, ₹1,254 vs ₹48L `West`) appears as a barely visible hairline sliver. |
| **Repository preview image** | **Poor (`M-3`)** | `Supermart_Grocery_Dashboard_Preview.png` shows only rows 1–30 (2 of 8 charts), cutting off Chart 3 mid-title and omitting Charts 4–8 and the Key Takeaways box entirely. It also includes Excel UI chrome (column/row headers, worksheet tabs, scrollbar, `"Accessibility: Investigate"`). |

---

## 2. Portfolio Readiness Judgment

The underlying visual design (color palette, KPI strip, filter bar, single-axis trend, top-down horizontal bars) is **above average** for an Excel portfolio dashboard. However, the **Chart 8 clipping of `KEY TAKEAWAYS`**, the **redundant Chart 1 doughnut**, and the **truncated Excel-window preview PNG** must be fixed before portfolio submission.

## Recommended Actions

1. Narrow Chart 8 to end cleanly inside column `J` (leaving a clean white gutter before `K77:S94`) and add left padding/indent to `K77` (`M-4`).
2. Align Chart 3's right edge flush with `S1` (`M-4`).
3. Replace redundant Chart 1 (or convert to a Category Margin / Order Volume view) and add `%` data labels to Chart 7 (`M-4`).
4. Export a clean, full-page PNG of `B1:S94` (all 8 charts + Key Takeaways, zero Excel UI chrome) to replace `Supermart_Grocery_Dashboard_Preview.png` (`M-3`).
