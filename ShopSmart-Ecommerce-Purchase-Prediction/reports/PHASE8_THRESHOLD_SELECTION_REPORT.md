# PHASE 8.1 — LEAKAGE-SAFE THRESHOLD SELECTION REPORT
## ShopSmart — E-Commerce Customer Purchase Prediction

**Evaluation Date:** 2026-11-21  
**Source Experiment Runner:** `src/phase8_experiments.py`  
**Machine-Readable Evidence:** `outputs/phase8/phase8_summary.json`

---

## 1. Methodology Correction & Leakage-Safe Split Design

In earlier exploratory diagnostics, decision thresholds were tabulated directly on the held-out test set. Selecting an operating threshold using test data introduces optimistic selection bias. Phase 8.1 replaces that procedure with a strict three-way stratified split (`random_state = 42`):

| Split Partition | Rows | Share | Purpose |
|---|---:|---:|---|
| **Inner Training (`X_tr`)** | `6,400` | `64%` | Fit all preprocessing (`SimpleImputer`, `IQRCapper`, `StandardScaler`, `OneHotEncoder`) and model weights |
| **Validation (`X_val`)** | `1,600` | `16%` | Select and lock decision thresholds (cross-checked via 5-fold OOF on `8,000` training rows) |
| **Untouched Final Test (`X_test`)** | `2,000` | `20%` | Evaluated **once** after all thresholds are locked (identical partition to historical Phases 1–7) |

- **5-Fold OOF Stability Cross-Check (`n = 8,000`):** Best F1 threshold = **`0.40`** (`OOF F1 = 0.8010`), matching the validation-set selection (`t = 0.40`, `Val F1 = 0.8008`).

---

## 2. Threshold Comparison — Validation Selection vs. Untouched Final Test

All five operating thresholds were selected and locked using **validation data only**, then evaluated once on the untouched final test set (`n = 2,000`, model refit on full `8,000` training rows):

| Strategy | Locked Threshold | Selection Criterion (Validation Only) | Val Prec / Rec / F1 | Untouched Test Acc | Untouched Test Prec | Untouched Test Rec | Untouched Test F1 | Test Targeted (%) | Test CM (`TN / FP / FN / TP`) |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|
| **Default** | `0.50` | Standard cutoff (`t = 0.50`) | `0.7240 / 0.8650 / 0.7882` | `0.7045` | `0.7279` | `0.8688` | `0.7921` | `77.35%` | `283 / 421 / 170 / 1,126` |
| **Val F1-Optimal** | `0.40` | Maximize validation F1 | `0.6922 / 0.9499 / 0.8008` | `0.6965` | `0.6930` | `0.9545` | **`0.8030`** | `89.25%` | `156 / 548 / 59 / 1,237` |
| **High-Recall (`>=0.90`)** | `0.47` | Val Recall `>= 0.90`, max Precision | `0.7119 / 0.9007 / 0.7952` | **`0.7090`** | `0.7198` | `0.9020` | `0.8007` | `81.20%` | `249 / 455 / 127 / 1,169` |
| **High-Precision (`>=0.80`)** | `0.67` | Val Precision `>= 0.80`, max Recall | `0.8039 / 0.6326 / 0.7080` | `0.6575` | **`0.8083`** | `0.6181` | `0.7005` | `49.55%` | `514 / 190 / 495 / 801` |
| **Cost-Sensitive** | `0.30` | Max Val Utility (`TP*₹180 - FP*₹65`) | `0.6634 / 0.9884 / 0.7940` | `0.6745` | `0.6681` | `0.9892` | `0.7975` | `95.95%` | `67 / 637 / 14 / 1,282` |

---

## 3. Business Implications & Why Highest F1 Is Not Automatically Best

1. **Why F1-Optimal (`t = 0.40`) Can Over-Target:** Maximizing F1 targets **`89.25%`** of active carts (`1,785 / 2,000`) and produces `548` false positives. Under tight marketing budgets or costly coupon offers, blanket targeting erodes ROI.
2. **High-Precision Regime (`t = 0.67`):** Cuts false positives by **`54.9%`** vs. default `0.50` (`421 -> 190`) and lifts precision to **`80.83%`** while focusing spend on the top **`49.55%`** of sessions — well suited for expensive incentives or margin-sensitive campaigns.
3. **Balanced Operating Point (`t = 0.47` or `t = 0.50`):** Achieves highest held-out accuracy (`0.7090` at `t = 0.47`) with strong recall (`90.20%`) and moderate outreach volume (`81.20%`).
4. **Unit-Economics Sensitivity (`t = 0.30`):** When missed buyers are much costlier than outreach (`₹180` vs. `₹65`), the utility-optimal threshold shifts downward (`0.30`), emphasizing that **thresholds must be tied to real campaign economics** (explored interactively in Page 8: Business Impact Simulator).

---

## 4. Limitations

- Offline cost-sensitive utility assumes fixed per-customer gains/costs and does not model heterogeneous causal uplift across probability bands.
- Production threshold changes should be validated via randomized controlled A/B experiments before permanent rollout.
