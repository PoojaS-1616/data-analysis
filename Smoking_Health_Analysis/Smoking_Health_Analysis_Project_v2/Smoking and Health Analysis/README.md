# Smoking & Health Analysis | Power BI Portfolio Project

An exploratory healthcare-analytics project built with **Microsoft Power BI (PBIP)** and validated with **Python (`pandas`, `scipy`)**. It examines smoking-status patterns, recorded health-condition categories, blood-pressure groupings, cholesterol levels, resting heart rate, and demographic distributions across a dataset of 10,000 records.

> **Responsible-use notice:** This is an educational analytics project, not a clinical tool. It must not be used for diagnosis, treatment decisions, individual risk assessment, or causal conclusions. Dataset provenance, synthetic/de-identified status, and redistribution permission have **not** been independently established; see [DATA_PROVENANCE.md](DATA_PROVENANCE.md).

## Project at a glance

| Item | Description |
|---|---|
| Domain | Healthcare / public-health analytics (descriptive, non-causal) |
| BI platform | Microsoft Power BI Desktop (PBIP format) |
| Dataset size | 10,000 rows × 15 source columns (`0` nulls, `0` duplicates, `49` flagged BP anomalies) |
| Data source configuration | Portable Power Query parameter (`DataFolderPath`) — no hard-coded local paths |
| Semantic model | `Smoking_Health_Analysis` fact/analysis table + `_Measures` (`17` DAX measures with `KEEPFILTERS`, `8` calculated columns) |
| Report pages | Executive Overview (`12` visuals); Detailed Health Analysis (`8` visuals) — `1280×720` `FitToPage` |
| Interactive filters | Synchronized Gender, Region, and Smoking Status slicers across both pages |
| Reproducible validation | `scripts/validate_smoking_health.py` and `scripts/statistical_analysis.py` |

## Business questions

This report explores the following descriptive questions:

1. How are records distributed across current, former, and never-smoker categories?
2. How does current-smoking prevalence vary across age groups, gender, and region?
3. What smoking intensity is recorded for current smokers (distinct from 0-coded former smokers)?
4. How are recorded organ categories and health-condition labels distributed?
5. How do cholesterol averages compare across the project's assumed blood-pressure categories (and under an alternative sensitivity rule)?
6. What patterns appear when recorded health-condition rates and biometrics (resting heart rate, systolic BP, cholesterol) are compared across smoking-status and exposure groups?

These are strictly descriptive questions. The dataset and analysis do **not** establish that smoking caused any recorded condition or measurement.

## Verified key figures

All figures below are independently reproduced in Python (`scripts/validate_smoking_health.py`) and verified live in Power BI Desktop's embedded Analysis Services DAX engine:

| Metric | Verified value |
|---|---:|
| Total records | 10,000 |
| Distinct `Patient_ID` values | 10,000 *(hidden in model; never exposed in outputs)* |
| Current smokers | 3,015 (30.15%) |
| Former smokers | 2,722 (27.22%) |
| Never smoked | 4,263 (42.63%) |
| Ever-smoked categories combined | 5,737 (57.37%) |
| Records with a recorded organ category | 7,227 (72.27%) |
| Records with a recorded health-condition category | 5,772 (57.72%) |
| Average cigarettes/day among current smokers | 17.11 *(overall mean: 5.16)* |
| High BP under primary project rule (`>=130` or `>=80`) | 6,049 (60.49%) |
| Flagged BP anomalies (`Diastolic >= Systolic`) | 49 (0.49%) *(preserved untouched; flagged via `BP Anomaly Flag`)* |

## Dashboard structure (redesigned two-page `1280×720` layout)

### 1. Executive Overview (`12` visuals)

- **Header banner** & **3 synchronized dropdown slicers** (`Gender`, `Region`, `Smoking Status`).
- **5 KPI cards:** Total Patients, Current Smokers, **Smoker Prevalence Rate**, Recorded Organ Category, and Recorded Health Condition (all protected with `KEEPFILTERS` + `COALESCE` so slicer selections never overwrite KPIs).
- **3 equal-height charts:**
  - Smoking Status Distribution (`donutChart`).
  - Average Cigarettes / Day by Smoking Status (`barChart`, noting former smokers are 0-coded).
  - Average Total Cholesterol (mg/dL) by Project BP Rule (`columnChart`).

### 2. Detailed Health Analysis (`8` visuals)

- **Identical header & synchronized slicer bar** for seamless page switching.
- **Top row:** Current Smokers by Age Group (`columnChart`) + full-width Organ-Wise Health Condition Cross-Tabulation Matrix (`pivotTable`).
- **Bottom row:**
  - Recorded Condition Rate (%) by Smoking Exposure (`barChart` replacing the previously crowded 16-series stacked bar chart; explicitly notes `Former = 0 Current PY`).
  - Average Resting Heart Rate (bpm) by Smoking Status (`columnChart`, highlighting the strongest reproduced biometric difference).

## Repository contents

| Path | Purpose |
|---|---|
| `Smoking_and_Health_Analysis.pbip` | Power BI Project entry point |
| `Smoking_and_Health_Analysis.Dataset/` | Semantic model (`model.bim` with `DataFolderPath`, `17` DAX measures, `BP Anomaly Flag`) |
| `Smoking_and_Health_Analysis.Report/` | Redesigned 2-page PBIR report (`20` visuals) and Clinical Navy & Teal theme |
| `Smoking_Health_Analysis.csv` | Local-only source dataset (**excluded via `.gitignore`**; not redistributed in GitHub) |
| `Smoking_and_Health_Analysis_Report.md` | Full analytical & technical report (kept identical to root-level copy) |
| `DATA_PROVENANCE.md` | Data-governance, provenance, privacy, and Windows `MAX_PATH` notice |
| `validation_summary.json` | Verified validation metrics, BP sensitivity figures, and Power BI validation flags |
| `scripts/validate_smoking_health.py` | Independent Python data-quality, 49-BP-anomaly, KPI, and DAX slicer validation |
| `scripts/statistical_analysis.py` | Reproducible Chi-square, ANOVA, Kruskal-Wallis, Bonferroni post-hoc, and effect-size tests |

## Open and refresh the Power BI project (portable `DataFolderPath` setup)

> **Windows cloning note (`MAX_PATH`):** Because the existing nested PBIP path exceeds Windows' legacy 260-character limit on default Git installations, clone with long paths enabled:
> ```powershell
> git clone -c core.longpaths=true https://github.com/PoojaS-1616/data-analysis.git
> ```

1. **Obtain the authorized dataset locally:** `Smoking_Health_Analysis.csv` is **not redistributed** in this repository because its provenance and redistribution rights remain unverified ([DATA_PROVENANCE.md](DATA_PROVENANCE.md)). Place your authorized local copy of `Smoking_Health_Analysis.csv` inside `Smoking_Health_Analysis_Project_v2/Smoking and Health Analysis/` before refreshing the PBIP or running the Python validation scripts.
2. Install or open **Power BI Desktop** (tested with version `2.159.1231.0`).
3. Open `Smoking_and_Health_Analysis.pbip` from this project folder.
4. Configure the portable **`DataFolderPath`** Power Query parameter before refreshing:
   - Go to **Home → Transform data → Edit parameters**.
   - Set **`DataFolderPath`** to the full local path of the folder containing `Smoking_Health_Analysis.csv` (for example, `C:\path\to\Smoking_Health_Analysis\Smoking_Health_Analysis_Project_v2\Smoking and Health Analysis`). Trailing slashes and backslashes are normalized automatically.
   - Click **OK**, then **Apply changes / Refresh**.
5. Verify the expected no-selection KPIs (`Total Patients: 10,000`, `Current Smokers: 3,015`, `Smoker Prevalence Rate: 30.15%`, `Recorded Organ: 7,227`, `Recorded Condition: 5,772`).
6. Test slicer filtering (`Former Smoker` and `Never Smoked` must show `Current Smokers = 0` and `Smoker Prevalence Rate = 0.00%`).

## Independent Python validation & statistical testing

Run the reproducible validation and statistical test scripts directly (Python 3.14 tested with `pandas`, `numpy`, `scipy`):

```powershell
py -3.14 scripts/validate_smoking_health.py
py -3.14 scripts/statistical_analysis.py
```

### Summary of reproduced & newly validated statistical results (non-causal)

| Test | Variables | p-value | Effect size | Practical interpretation |
|---|---|---:|---|---|
| Chi-square | `Has_Condition` vs. `Smoking_Status` | `0.4502` | Cramér's `V = 0.0126` (negligible) | No statistically significant association in this dataset (`57.45% / 56.94% / 58.41%`). |
| ANOVA / Kruskal-Wallis | `Total_Cholesterol` vs. `BP_Primary` | `0.0023` / `0.0044` | `eta² = 0.0012` (negligible) | Statistically significant due to `n = 10,000`, but negligible practical spread (`2.46 mg/dL`). |
| ANOVA / Kruskal-Wallis | `Resting_Heart_Rate` vs. `Smoking_Status` | `1.56e-32` / `9.21e-30` | `eta² = 0.0145` (small; `d = +0.270`) | Current (`76.97`) > Former (`74.16`) & Never (`74.02 bpm`); Former vs. Never NS (`p_adj = 1.00`). |
| ANOVA / Kruskal-Wallis | `Systolic_BP` vs. `Smoking_Status` | `1.00e-31` / `2.47e-29` | `eta² = 0.0142` (small; `d = +0.261`) | Current (`126.02`) > Former (`121.94`) & Never (`122.00 mmHg`); Former vs. Never NS (`p_adj = 1.00`). |
| ANOVA / Kruskal-Wallis | `Total_Cholesterol` vs. `Smoking_Status` | `2.26e-28` / `6.72e-28` | `eta² = 0.0127` (small; `d = +0.248`) | Current (`202.50`) > Former (`194.60`) & Never (`194.40 mg/dL`); Former vs. Never NS (`p_adj = 1.00`). |

*Statistical significance at `n = 10,000` must not be conflated with large practical effect size or clinical causality.*

## Data quality, provenance, and limitations

- **Unverified provenance & rights:** Dataset origin, synthetic/de-identified status, and redistribution rights remain **unverified**; see [DATA_PROVENANCE.md](DATA_PROVENANCE.md).
- **49 blood-pressure anomalies (`0.49%`):** `49` records have `Diastolic_BP_mmHg >= Systolic_BP_mmHg`. They are preserved untouched in the CSV and surfaced via `BP Anomaly Flag` and `[BP Anomaly Records]`. Excluding them changes Primary High BP mean cholesterol by only `-0.062 mg/dL`.
- **Former-smoker pack-years caveat:** Former smokers have `Cigarettes_Per_Day = 0` despite averaging `16.18` years of smoking; their calculated `0` pack-years must **not** be interpreted as zero lifetime exposure.
- **BP thresholds:** Primary (`130/80`) and Alternative (`140/90`) BP categories are analyst-defined groupings, not clinical diagnoses.
- **Power BI validation status:** Model loading, live refresh via `DataFolderPath`, and live DAX slicer evaluation **PASSED** inside Power BI Desktop's embedded Analysis Services engine (`2.159.1231.0`). Interactive GUI rendering inspection and screenshot capture remain **pending** (`rendered_in_power_bi_desktop: false`) because automated runs occurred in a non-interactive Windows session.

## Tools and documentation

- **Tools:** Microsoft Power BI Desktop (PBIP / PBIR / DAX / Power Query M), Python (`pandas`, `numpy`, `scipy`), Markdown, JSON.
- **Detailed documentation:** [Smoking_and_Health_Analysis_Report.md](Smoking_and_Health_Analysis_Report.md) · [DATA_PROVENANCE.md](DATA_PROVENANCE.md).

---

**Project status:** Semantic model, portable `DataFolderPath` refresh, live DAX slicer behavior, and Python statistical validation verified; interactive GUI rendering inspection and screenshots pending.

**Disclaimer:** For educational and exploratory analytics only. Not medical advice, not a diagnostic system, and not evidence of causal relationships.
