# Statistical and Business Analysis Audit — Supermart Grocery Sales Dashboard

**Project:** Supermart Grocery Sales Dashboard
**Audit Date:** 2026-11-19

---

## A. Discount Analysis Audit

| Discount Band | Orders | Sales (₹) | Profit (₹) | Weighted Margin | Mean Row Margin | AOV (₹) |
|---|---:|---:|---:|---:|---:|---:|
| 10–15% (`[0.10, 0.15)`) | 1,836 | 27,51,290 | 6,88,323 | 25.02% | 24.82% | 1,498.52 |
| 15–20% (`[0.15, 0.20)`) | 1,900 | 28,49,280 | 7,09,783 | 24.91% | 24.98% | 1,499.62 |
| 20–25% (`[0.20, 0.25)`) | 1,920 | 28,81,920 | 7,15,270 | 24.82% | 24.78% | 1,501.00 |
| 25–30% (`[0.25, 0.30)`) | 2,004 | 29,86,763 | 7,67,862 | 25.71% | 25.71% | 1,490.40 |
| 30–35% (`[0.30, 0.36)`) | 2,334 | 34,87,729 | 8,65,884 | 24.83% | 24.83% | 1,494.31 |

- **Correlations ($n = 9,994$):**
  - `Discount vs Profit`: $r = 0.000017$ ($t = 0.0017$, $p = 0.999$)
  - `Discount vs Profit Margin`: $r = 0.008282$ ($t = 0.8279$, $p = 0.408$)
  - `Discount vs Sales`: $r = -0.005512$ ($t = -0.551$, $p = 0.582$)
- **Note on group size:** Band `30–35%` contains 2,334 orders vs ~1,900 in other bands solely because it spans **6** discrete values (`0.30, 0.31, 0.32, 0.33, 0.34, 0.35`) while the first four bands each span **5** values. AOV is flat (~₹1,490–₹1,501) across all bands.
- **Critical Statistical & Commercial Finding (`C-2`):** Every row's `Profit` equals `Sales × k%` where `k` is an exact integer in `{5, 6, ..., 45}` drawn independently of `Discount`. Thus, the zero correlation is a **synthetic data-generation artifact**, not evidence that real-world grocery discounts do not erode profit. While `Dashboard!K77` and `Insights!B17` responsibly state *"This does not establish how changing discounts would affect sales or profit"*, **`README.md` line 41 contradicts this** by recommending: *"Since discount level makes no visible difference to margin, test whether selective discounts can lift volume without costing profit."* That conclusion is neither statistically nor commercially defensible.

---

## B. Regional Analysis Audit

- **Verified numbers:** `West` ₹47,98,743 (32.08%, 3,203 orders, 24.84% margin), `East` ₹42,48,368 (28.40%, 2,848 orders, 25.29%), `Central` ₹34,68,156 (23.19%, 2,323 orders, 24.70%), `South` ₹24,40,461 (16.32%, 1,619 orders, **25.55%**), `North` ₹1,254 (0.01%, 1 order `OD1`, 32.00%).
- **Geographic validity check:** All 24 Tamil Nadu cities appear in **all 4 major regions** (e.g., `Vellore` appears in Central, East, North, South, and West). Furthermore, the regional shares (`West 32%`, `East 28%`, `Central 23%`, `South 16%`) are inherited verbatim from the US Superstore dataset (`9,994` rows!).
- **Assessment:** The author deserves credit for spotting and documenting both the single `North` order and the city/region decoupling. However, `README.md` still frames `West` and `South` as business regions without clarifying that the region labels are non-geographic synthetic tags inherited from a template dataset.

---

## C. Category & Sub-Category Analysis Audit

- **Categories (7):** Narrowly clustered between **13.63%** (`Oil & Masala`) and **15.16%** (`Eggs, Meat & Fish`), with margins between **24.43%** and **25.39%**.
- **Sub-categories (23):** Median sales = `₹6,11,200` (`Mutton`); overall weighted margin = `25.0527%`.
- **High-sales / below-average-margin classification:** `Analysis!G94:G116` uses `AND(C94>=MEDIAN($C$94:$C$116), E94<SUM($D$94:$D$116)/SUM($C$94:$C$116))`, which flags **8 sub-categories**: `Spices` (23.82%), `Masalas` (24.23%), `Cakes` (24.56%), `Biscuits` (24.76%), `Mutton` (24.77%, equal to median), `Cookies` (24.82%), `Soft Drinks` (24.97%), and `Chocolates` (25.051%).
- **Assessment:** All cited margins (`Spices 23.8%`, `Masalas 24.2%`, `Cakes 24.6%`) are **numerically exact**. The author also sensibly notes that margins are tightly clustered (~24%–26%) so gaps are small. Minor wording discrepancy (`m-5`): `README.md` says "above-median" while the formula uses `>=MEDIAN` (including `Mutton`). Note also that because margins are synthetically uniform `U(5%, 45%)`, a 23.8% vs 25.1% gap on $n \approx 450$ is within ~2.1 standard errors of random sampling noise—another reason the synthetic nature must be disclosed before recommending pricing reviews.

---

## D. Seasonal Analysis Audit

- **Comparable periods:** All 4 years (2015–2018) contain all 12 months (48 complete monthly buckets).
- **Critical defect (`C-1`):** Because 4,042 dash-format dates were parsed day-first instead of month-first, monthly sales are distorted by **−23% to +82%**, and the true top-3 seasonal months are **November (₹21.94 L) > December (₹20.88 L) > September (₹20.64 L)**, not November > September > December.
- **Causal discipline:** To the author's credit, `README.md` does not fabricate causal explanations (e.g., Diwali) for the peaks, simply recommending inventory/promotion planning around peak months.

## Recommended Actions

1. Fix the dash-date parsing error (`C-1`) and re-run seasonal rankings.
2. Disclose the synthetic data-generation structure (`C-2`) and replace `README.md` line 41's discount recommendation with a clear note that independent synthetic margins cannot inform real-world discount elasticity.
3. Align `README.md` wording (`≥ median`) with `Analysis!G94:G116`.
