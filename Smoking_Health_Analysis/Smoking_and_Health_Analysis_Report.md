# Smoking & Health Analysis
## Technical Documentation and Analytical Report

**Project domain:** Healthcare analytics (descriptive, non-causal)
**BI platform:** Microsoft Power BI Desktop (PBIP / PBIR)
**Dataset file:** `Smoking_Health_Analysis.csv` (`10,000` rows × `15` source columns; SHA-256 `2623012E...`; **local-only, excluded from GitHub via `.gitignore`**)
**Portable data parameter:** `DataFolderPath` (Power Query M parameter; no hard-coded local paths)
**Supporting artifacts:** `validation_summary.json`, `DATA_PROVENANCE.md`, `scripts/validate_smoking_health.py`, `scripts/statistical_analysis.py`

> **Important:** This report documents descriptive analysis of the supplied dataset. It is not medical advice, a diagnostic tool, or evidence that smoking causes any particular condition. The dataset's provenance, synthetic/de-identified status, and redistribution rights have **not** been independently established; see `DATA_PROVENANCE.md`.

---

## 1. Executive summary

This project explores smoking status, recorded organ and health-condition categories, blood-pressure groupings, cholesterol, resting heart rate, and demographic distributions across 10,000 records. The redesigned Power BI report is organized into two full-width (`1280×720`) pages—**Executive Overview** (`12` visuals) and **Detailed Health Analysis** (`8` visuals)—with synchronized Gender, Region, and Smoking Status slicers.

### Headline figures (verified in Python and live Power BI DAX engine)

| Measure | Verified result |
|---|---:|
| Total records | 10,000 |
| Current smokers | 3,015 (30.15%) |
| Former smokers | 2,722 (27.22%) |
| Never smoked | 4,263 (42.63%) |
| Ever-smoked categories combined | 5,737 (57.37%) |
| Records with a recorded organ category | 7,227 (72.27%) |
| Records with a recorded health-condition category | 5,772 (57.72%) |
| Average cigarettes/day among current smokers | 17.11 *(overall mean: 5.16)* |
| Average smoking duration among current smokers | 17.67 years *(former smokers: 16.18 years)* |
| High BP category under primary project rule (`>=130` or `>=80`) | 6,049 (60.49%) |
| Flagged BP anomalies (`Diastolic_BP_mmHg >= Systolic_BP_mmHg`) | 49 (0.49%) |

### Interpretation in brief

- Current-smoker prevalence is `30.15%` overall and varies only modestly across age groups and regions.
- The `60+` age group contains the largest count of current smokers (`1,124`) because it is the largest age band (`3,734`); its within-group prevalence (`30.10%`) matches the overall rate.
- Recorded-condition percentages are similar across smoking-status groups (`57.45%` / `56.94%` / `58.41%`; $\chi^2 = 1.596, p = 0.4502$). This describes this dataset only and is **not** evidence that smoking has no health effects.
- Current smokers show small but statistically significant upward shifts in resting heart rate (`+2.96 bpm`), systolic BP (`+4.03 mmHg`), and total cholesterol (`+8.10 mg/dL`) compared with never smokers ($\eta^2 = 0.013\text{–}0.015$, Cohen's $d = 0.25\text{–}0.27$), while former and never smokers are statistically indistinguishable ($p_{\text{adj}} = 1.00$).
- BP categories are analyst-defined groupings, not clinical diagnoses, and the pack-years formula cannot estimate former smokers' historical exposure because their `Cigarettes_Per_Day` is coded as `0`.

## 2. Dataset, data-quality audit, and validation profile

Independent inspection (`scripts/validate_smoking_health.py`) verified `10,000` rows, `15` columns, `0` missing values, `0` exact duplicate rows, `10,000` distinct `Patient_ID` values (`PT00001`–`PT10000`, hidden in the model), and `0` invalid `Diagnosis_Date` values (`2021-01-01` to `2026-09-30`).

### Blood-pressure anomaly investigation (`49` records, `0.49%`)

Independent auditing uncovered **`49` physiologically impossible records** where `Diastolic_BP_mmHg >= Systolic_BP_mmHg` (`Diastolic - Systolic` range `0.0–20.0 mmHg`, median `3.0`, mean `3.96 mmHg`; `Never Smoked: 25`, `Former Smoker: 18`, `Current Smoker: 6`). All `49` records fall into Primary BP = `High` because `Diastolic >= 85 >= 80`. These records are **preserved untouched** in the source CSV and flagged transparently via `BP Anomaly Flag` and `[BP Anomaly Records]`.

| Primary BP category | Full (`n = 10,000`) | Excl. 49 anomalies (`n = 9,951`) | Count diff | Mean chol (full) | Mean chol (excl.) | Mean diff |
|---|---:|---:|---:|---:|---:|---:|
| High | 6,049 | 6,000 | -49 | 197.81 mg/dL | 197.87 mg/dL | -0.062 mg/dL |
| Elevated | 1,451 | 1,451 | 0 | 195.73 mg/dL | 195.73 mg/dL | 0.000 mg/dL |
| Lower Range | 2,500 | 2,500 | 0 | 195.35 mg/dL | 195.35 mg/dL | 0.000 mg/dL |

### Current `validation_summary.json` status

| Validation item | Result |
|---|---:|
| Rows / Distinct `Patient_ID` / Missing values | `10,000` / `10,000` / `0` |
| Flagged BP anomalies (`Diastolic >= Systolic`) | `49` (`0.49%`) |
| Semantic model tables / measures | `2` / `17` (`DataFolderPath` parameter configured) |
| Report pages / visuals | `2` / `20` (`Executive Overview: 12`, `Detailed Health Analysis: 8`) |
| Slicer sync groups | Gender (`2`), Smoking Status (`2`), Region (`2`) |
| Statistical tests reproduced in Python | `true` |
| Live Power BI model load, refresh & `KEEPFILTERS` DAX tests | `true` (`Power BI Desktop 2.159.1231.0`) |
| Interactive GUI rendering & screenshots (`rendered_in_power_bi_desktop`) | **`false`** *(blocked by non-interactive Windows session; pending interactive review)* |

## 3. Core KPIs, DAX measures, and slicer-context verification

The semantic model defines `17` formatted DAX measures in `_Measures`, including all `7` original measures upgraded with **`KEEPFILTERS`** and **`COALESCE`** to prevent slicer overwrites and `(Blank)` cards:

```dax
Total Patients =
COALESCE(COUNTROWS('Smoking_Health_Analysis'), 0)

Total Current Smokers =
COALESCE(
    CALCULATE(
        COUNTROWS('Smoking_Health_Analysis'),
        KEEPFILTERS('Smoking_Health_Analysis'[Smoking_Status] = "Current Smoker")
    ),
    0
)

Patients with Recorded Organ =
COALESCE(
    CALCULATE(
        COUNTROWS('Smoking_Health_Analysis'),
        KEEPFILTERS('Smoking_Health_Analysis'[Diagnosed_Organ] <> "No Recorded Organ Condition")
    ),
    0
)

Patients with Recorded Condition =
COALESCE(
    CALCULATE(
        COUNTROWS('Smoking_Health_Analysis'),
        KEEPFILTERS('Smoking_Health_Analysis'[Health_Condition] <> "No Diagnosed Condition")
    ),
    0
)

Smoker Prevalence Rate =
DIVIDE([Total Current Smokers], [Total Patients], 0)
```

Additional focused measures added in Phase 5: `Total Former Smokers`, `Total Never Smokers`, `Avg Cigarettes Per Day (Current Smokers)`, `Recorded Organ Rate`, `Recorded Condition Rate`, `High BP Patients`, `High BP Rate`, `Average Resting Heart Rate`, `Average Systolic BP`, and `BP Anomaly Records`.

### Live Power BI DAX slicer-context verification (`localhost:49246`, post-refresh)

| Active `Smoking_Status` slicer | Total Patients | Current Smokers | Smoker Prevalence | Recorded Organ | Recorded Condition |
|---|---:|---:|---:|---:|---:|
| **No Selection** | 10,000 | 3,015 | 30.15% | 7,227 | 5,772 |
| **Current Smoker** | 3,015 | 3,015 | 100.00% | 2,165 | 1,732 |
| **Former Smoker** | 2,722 | **0** | **0.00%** | 1,959 | 1,550 |
| **Never Smoked** | 4,263 | **0** | **0.00%** | 3,103 | 2,490 |

Filtering `Diagnosed_Organ = "No Recorded Organ Condition"` (`n = 2,773`) returned `Patients with Recorded Organ = 0`, and filtering `Health_Condition = "No Diagnosed Condition"` (`n = 4,228`) returned `Patients with Recorded Condition = 0`, confirming `KEEPFILTERS` behavior live.

The recorded-organ (`7,227`) and recorded-condition (`5,772`) KPIs remain independent, non-nested classifications (`2,692` organ-only, `1,237` condition-only, `4,535` both, `1,536` neither).

## 4. Calculated columns, BP sensitivity reconciliation, and pack-years caveat

- **Age groups:** `18–29`, `30–44`, `45–59`, `60+` sorted via hidden `Age Group Sort` (`summarizeBy: none`).
- **BP Anomaly Flag (non-destructive):** `IF([Diastolic_BP_mmHg] >= [Systolic_BP_mmHg], "Diastolic >= Systolic", "Valid (Systolic > Diastolic)")`.
- **Blood-pressure classification & sensitivity reconciliation (discrepancy resolved):**

| Scenario | Project threshold rule | High (n / mean chol) | Elevated (n / mean chol) | Lower Range (n / mean chol) |
|---|---|---:|---:|---:|
| **Primary (Model)** | High: `Sys >= 130` or `Dia >= 80`; Elevated: `Sys 120–129` & `Dia < 80` | `6,049` (`197.81 mg/dL`) | `1,451` (`195.73 mg/dL`) | `2,500` (`195.35 mg/dL`) |
| **Alternative (Sensitivity)** | High: `Sys >= 140` or `Dia >= 90`; Elevated: `Sys >= 120` or `Dia >= 80` | `2,447` (`197.87 mg/dL`) | `5,053` (`197.18 mg/dL`) | `2,500` (`195.35 mg/dL`) |

This resolves the previously noted `195.73` vs. `197.18 mg/dL` discrepancy: both values are exact under their respective threshold rules. Both rules are analyst assumptions, not clinical diagnoses.

- **Pack-years & exposure categories:** `Pack Years = (Cigarettes_Per_Day / 20) × Years_Smoking`. Because all `2,722` Former Smokers have `Cigarettes_Per_Day = 0` despite averaging `16.18` smoking years (`1–49`), their `0.00` value is a data-coding placeholder (`Former Smokers (0 Current PY)`), **not** zero lifetime exposure.

## 5. Smoking patterns and demographic distribution

- **Smoking status:** Never Smoked `4,263` (`42.63%`), Current Smoker `3,015` (`30.15%`), Former Smoker `2,722` (`27.22%`).
- **Cigarettes per day:** Current Smokers mean `17.11` (`SD = 10.78`), Former Smokers `0.00`, Never Smoked `0.00`, Overall `5.16` (`SD = 9.83`).
- **Current smokers by age group:** `18–29`: `508 / 1,774` (`28.64%`); `30–44`: `668 / 2,213` (`30.19%`); `45–59`: `715 / 2,279` (`31.37%`); `60+`: `1,124 / 3,734` (`30.10%`).
- **Gender & region:** Female `1,445 / 4,769` (`30.30%`), Male `1,524 / 5,042` (`30.23%`), Other `46 / 189` (`24.34%`, small group size); Regions range from `29.07%` (South) to `32.19%` (Central).

## 6. Recorded organ and health-condition distribution

Lungs (`2,792`, `27.92%`), No Recorded Organ Condition (`2,773`, `27.73%`), Heart (`2,197`, `21.97%`), Liver (`1,231`, `12.31%`), and Kidneys (`1,007`, `10.07%`). Lungs and Heart represent `4,989` records (`49.89%` overall; `69.03%` of recorded-organ records).

## 7. Independent statistical validation (`scripts/statistical_analysis.py`)

All previously cited inferential tests were independently reproduced and supplemented with non-parametric checks (Kruskal-Wallis / Mann-Whitney U), Levene variance tests, Bonferroni-adjusted post-hoc comparisons ($\alpha_{\text{adj}} = 0.0167$), effect sizes, and 95% confidence intervals:

| Test | Variables | Parametric | Non-parametric | Effect size | Non-causal interpretation |
|---|---|---|---|---|---|
| **Test 1** | `Has_Condition` vs. `Smoking_Status` | $\chi^2 = 1.596, df = 2, p = 0.4502$ | — | Cramér's $V = 0.0126$ (**negligible**) | Reproduces `p = 0.45`; no significant association in this dataset. |
| **Test 2A/2B** | `Total_Cholesterol` vs. `BP_Primary` | $F = 6.076, p = 0.0023$ | $H = 10.855, p = 0.0044$ | $\eta^2 = 0.0012$ (**negligible**) | Reproduces `p = 0.002`; negligible `2.46 mg/dL` spread (unchanged excl. 49 anomalies). |
| **Test 3** | `Resting_Heart_Rate` vs. `Smoking_Status` | $F = 73.78, p = 1.56 \times 10^{-32}$ | $H = 133.71, p = 9.21 \times 10^{-30}$ | $\eta^2 = 0.0145$ (**small**; $d = +0.270$) | Reproduces `~3 bpm, p < 0.001`: Current (`76.97`) > Former (`74.16`) & Never (`74.02`); Former vs. Never NS ($p_{\text{adj}} = 1.00$). |
| **Test 4 (NEW)** | `Systolic_BP` vs. `Smoking_Status` | $F = 71.89, p = 1.00 \times 10^{-31}$ | $H = 131.74, p = 2.47 \times 10^{-29}$ | $\eta^2 = 0.0142$ (**small**; $d = +0.261$) | Current (`126.02`) > Former (`121.94`) & Never (`122.00 mmHg`, `+4.03`); Former vs. Never NS ($p_{\text{adj}} = 1.00$). |
| **Test 5 (NEW)** | `Total_Cholesterol` vs. `Smoking_Status` | $F = 64.06, p = 2.26 \times 10^{-28}$ | $H = 125.13, p = 6.72 \times 10^{-28}$ | $\eta^2 = 0.0127$ (**small**; $d = +0.248$) | Current (`202.50`) > Former (`194.60`) & Never (`194.40 mg/dL`, `+8.10`); Former vs. Never NS ($p_{\text{adj}} = 1.00$). |
| **Test 6A/6B** | `Diastolic_BP` & `BMI` vs. `Smoking_Status` | $p = 0.090$ / $p = 0.475$ | $p = 0.065$ / $p = 0.464$ | $\eta^2 < 0.0005$ (**negligible**) | No statistically significant differences across smoking status. |

## 8. Redesigned Power BI report specification & validation status

- **Theme & canvas:** Clinical Navy & Teal Enterprise Theme (`healthcare_theme.json`), `useEnhancedTooltips: true`, explicit `1280×720` `FitToPage` layout on both pages, `0/20` broken visual references.
- **Executive Overview (`12` visuals):** Header banner, 3 full-width synced slicers (`Gender`, `Region`, `Smoking Status`), 5 KPI cards (adding `Smoker Prevalence Rate`), and 3 equal-height bottom charts (`donutChart`, `barChart`, `columnChart`).
- **Detailed Health Analysis (`8` visuals):** Identical slicer bar, `Current Smokers by Age Group`, expanded full-width `Organ-Wise Health Condition Matrix`, `Recorded Condition Rate (%) by Exposure` (replacing the unreadable 16-series stacked chart), and `Avg Resting Heart Rate (bpm) by Smoking Status`.
- **Semantic model hygiene:** Hidden `Patient_ID` and sort columns (`Age Group Sort`, `BP Risk Sort`, `Exposure Sort`), `summarizeBy: "none"` on all continuous clinical/sort columns, unused Auto Date/Time tables removed, and `DataFolderPath` M parameter added (zero hard-coded personal paths).
- **Power BI validation status:** Model load, full refresh via `DataFolderPath`, and live DAX slicer tests **PASSED** in Power BI Desktop (`2.159.1231.0`). Interactive GUI rendering inspection and screenshot capture remain **pending** (`rendered_in_power_bi_desktop: false`) due to non-interactive Windows session constraints.

## 9. Limitations and responsible use

- Cross-sectional descriptive data cannot establish causality, temporal sequence, or individual medical prognosis.
- Statistical significance at `n = 10,000` reflects sample power and must be interpreted alongside small/negligible effect sizes.
- BP thresholds are analyst assumptions; `49` records (`0.49%`) have `Diastolic >= Systolic` and are flagged without alteration.
- Former smokers' historical daily cigarette intensity is unrecorded (`0` coded), so their pack-years cannot be interpreted as zero lifetime exposure.
- Dataset provenance, synthetic/de-identified status, and redistribution rights remain **unverified** (`DATA_PROVENANCE.md`).
- Nested PBIP paths exceed Windows' legacy 260-character `MAX_PATH` limit on default Git clones (`git clone -c core.longpaths=true` required on Windows).

---

**Use restriction:** Educational and exploratory analytics only. Not for diagnosis, treatment, individual medical decisions, or causal claims.
