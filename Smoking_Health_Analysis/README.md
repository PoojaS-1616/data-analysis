# Smoking & Health Analysis | Power BI & Python Portfolio Project

![Platform](https://img.shields.io/badge/Power%20BI-PBIP%20%7C%20DAX-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.14%20Validated-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Domain](https://img.shields.io/badge/Domain-Healthcare%20Analytics-0D9488?style=for-the-badge)

An exploratory, descriptive healthcare-analytics case study built with **Microsoft Power BI (PBIP / PBIR)** and independently validated with **Python (`pandas`, `numpy`, `scipy`)**. It examines smoking-status distributions, recorded organ and health-condition categories, blood-pressure threshold sensitivity, cholesterol, resting heart rate, and demographic patterns across **10,000 records**.

> **Responsible-Use & Dataset Notice:** This project is strictly for educational and exploratory analytics. It is **not** medical advice, a diagnostic system, or evidence of causal relationships. The source dataset (`Smoking_Health_Analysis.csv`) is **not included in this GitHub repository** because its upstream provenance, synthetic/de-identified status, and redistribution permissions remain **unverified** (see [DATA_PROVENANCE.md](Smoking_Health_Analysis_Project_v2/Smoking%20and%20Health%20Analysis/DATA_PROVENANCE.md)).

---

## Quick Navigation

| Resource | Description |
|---|---|
| [Analytical & Technical Report](Smoking_and_Health_Analysis_Report.md) | Canonical full report: methodology, DAX definitions, 49-BP-anomaly audit, BP sensitivity reconciliation, and statistical tests |
| [Power BI Project Setup README](Smoking_Health_Analysis_Project_v2/Smoking%20and%20Health%20Analysis/README.md) | Detailed PBIP/PBIR structure, `DataFolderPath` parameter steps, and first-refresh verification |
| [Power BI Project Entry Point (`.pbip`)](Smoking_Health_Analysis_Project_v2/Smoking%20and%20Health%20Analysis/Smoking_and_Health_Analysis.pbip) | Open in Power BI Desktop (nested PBIP/PBIR folder preserved) |
| [Data Provenance & Governance](Smoking_Health_Analysis_Project_v2/Smoking%20and%20Health%20Analysis/DATA_PROVENANCE.md) | Provenance facts, unverified rights status, privacy safeguards, and Windows `MAX_PATH` note |
| [Data Quality & DAX Validation Script](Smoking_Health_Analysis_Project_v2/Smoking%20and%20Health%20Analysis/scripts/validate_smoking_health.py) | Reproduces KPIs, 49 BP anomalies, BP sensitivity rules, and `KEEPFILTERS` slicer scenarios |
| [Statistical Analysis Script](Smoking_Health_Analysis_Project_v2/Smoking%20and%20Health%20Analysis/scripts/statistical_analysis.py) | Reproduces Chi-square, ANOVA, Kruskal-Wallis, Bonferroni post-hoc tests, effect sizes, and 95% CIs |
| [Validation Summary (`JSON`)](Smoking_Health_Analysis_Project_v2/Smoking%20and%20Health%20Analysis/validation_summary.json) | Machine-readable verified counts, sensitivity figures, and honest Power BI validation flags |

---

## Verified Headline KPIs

All metrics below were independently verified in Python (`scripts/validate_smoking_health.py`) and evaluated live inside Power BI Desktop's embedded Analysis Services DAX engine (`2.159.1231.0`):

| Metric | Verified Value |
|---|---:|
| Total records | `10,000` (`0` nulls, `0` exact duplicates) |
| Current smokers | `3,015` (`30.15%`) |
| Former smokers | `2,722` (`27.22%`) |
| Never smoked | `4,263` (`42.63%`) |
| Records with a recorded organ category | `7,227` (`72.27%`) |
| Records with a recorded health-condition category | `5,772` (`57.72%`) |
| Average cigarettes/day (current smokers) | `17.11` *(overall mean: `5.16`)* |
| High BP under primary project rule (`>=130` or `>=80`) | `6,049` (`60.49%`) |
| Flagged BP anomalies (`Diastolic >= Systolic`) | `49` (`0.49%`) *(preserved untouched; flagged via `BP Anomaly Flag`)* |

---

## Key Analytical Highlights (Descriptive, Non-Causal)

- **DAX Slicer Integrity (`KEEPFILTERS` + `COALESCE`):** Upgraded `17` measures in `model.bim` so selecting `Former Smoker` or `Never Smoked` accurately returns `0` Current Smokers (`0.00%` prevalence) instead of overwriting the active slicer.
- **Blood-Pressure Sensitivity Reconciled:** Primary rule (`130/80`) Elevated mean cholesterol = `195.73 mg/dL` (`n = 1,451`); Alternative rule (`140/90`) Elevated mean cholesterol = `197.18 mg/dL` (`n = 5,053`). Both are analyst-defined thresholds, not clinical diagnoses.
- **49 Flagged BP Anomalies (`Diastolic >= Systolic`):** Identified and preserved without altering source data; excluding them changes Primary High BP mean cholesterol by only `-0.062 mg/dL`.
- **Statistical Significance vs. Practical Effect Size:** Recorded condition rates do not differ significantly across smoking status ($\chi^2 = 1.596, p = 0.4502$, Cramér's $V = 0.0126$). Current smokers show small upward shifts in resting heart rate (`+2.96 bpm`, $\eta^2 = 0.0145$), systolic BP (`+4.03 mmHg`, $\eta^2 = 0.0142$), and total cholesterol (`+8.10 mg/dL`, $\eta^2 = 0.0127$) compared with never smokers, while former and never smokers are statistically indistinguishable ($p_{\text{adj}} = 1.00$).

---

## Two-Page Power BI Dashboard & Validation Status

- **Executive Overview (`12` visuals, `1280×720` `FitToPage`):** Synchronized `Gender`, `Region`, and `Smoking Status` slicers, 5 KPI cards (including `Smoker Prevalence Rate`), Smoking Status donut chart, Avg Cigarettes/Day bar chart, and Avg Cholesterol by Project BP Rule column chart.
- **Detailed Health Analysis (`8` visuals, `1280×720` `FitToPage`):** Identical synchronized slicer bar, Current Smokers by Age Group, expanded Organ-Wise Health Condition Matrix, Recorded Condition Rate (%) by Exposure (replacing the crowded 16-series stacked chart), and Avg Resting Heart Rate (bpm) by Smoking Status.
- **Honest Validation Status (`validation_summary.json`):**
  - **PASSED:** Power BI Desktop PBIP model loading, live `DataFolderPath` refresh (`10,000` rows), live `KEEPFILTERS` DAX slicer verification across all scenarios, `31/31` JSON/BIM validity, `20/20` visual cross-references (`0` broken), and Python validation/statistical scripts.
  - **PENDING (`rendered_in_power_bi_desktop: false`):** Interactive Power BI Desktop GUI visual inspection and live dashboard screenshots have **not** yet been completed (automated testing ran in a non-interactive Windows session; no screenshots have been fabricated).

---

## Quick-Start Setup (Authorized Local Dataset Required)

1. **Clone with Windows long paths enabled** (required due to the preserved nested PBIP path):
   ```powershell
   git clone -c core.longpaths=true https://github.com/PoojaS-1616/data-analysis.git
   ```
2. **Place your authorized local dataset:** Copy `Smoking_Health_Analysis.csv` (excluded from GitHub via `.gitignore`) into `Smoking_Health_Analysis/Smoking_Health_Analysis_Project_v2/Smoking and Health Analysis/`.
3. **Open in Power BI Desktop:** Open `Smoking_and_Health_Analysis.pbip`, go to **Home → Transform data → Edit parameters**, set **`DataFolderPath`** to your local project folder path, then click **Apply changes / Refresh**.
4. **Run independent Python validation (optional):**
   ```powershell
   py -3.14 "Smoking_Health_Analysis_Project_v2/Smoking and Health Analysis/scripts/validate_smoking_health.py"
   py -3.14 "Smoking_Health_Analysis_Project_v2/Smoking and Health Analysis/scripts/statistical_analysis.py"
   ```

---

## Data Governance & Limitations

- **Provenance & Redistribution:** The project brief was issued by **Sapphire IQ ("Brilliant Minds Intelligent Solutions")**; upstream dataset origin, synthetic/de-identified status, and redistribution rights remain **unverified** ([DATA_PROVENANCE.md](Smoking_Health_Analysis_Project_v2/Smoking%20and%20Health%20Analysis/DATA_PROVENANCE.md)). `Smoking_Health_Analysis.csv` is retained strictly locally and excluded from GitHub.
- **Former-Smoker Pack-Years Caveat:** Former smokers are coded with `0` current cigarettes/day despite averaging `16.18` years of smoking; calculated `0` pack-years must not be interpreted as zero lifetime exposure.
- **Non-Causal Scope:** Cross-sectional descriptive findings do not establish clinical diagnoses or causation.
