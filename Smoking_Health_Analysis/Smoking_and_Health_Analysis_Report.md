# Smoking & Health Analysis
## Technical Documentation and Analytical Report

**Project domain:** Healthcare analytics  
**BI platform:** Microsoft Power BI  
**Project format:** Power BI Project (PBIP)  
**Dataset file:** `Smoking_Health_Analysis.csv`  
**Dataset dimensions:** 10,000 rows × 15 source columns  
**Supporting validation file:** `validation_summary.json`

> **Important:** This report documents descriptive analysis of the supplied dataset. It is not medical advice, a diagnostic tool, or evidence that smoking causes any particular condition. The dataset's provenance, synthetic/de-identified status, and redistribution rights have not been independently established.

---

## 1. Executive summary

This project explores smoking status, recorded organ and health-condition categories, selected health measurements, and demographic distributions across 10,000 records. The Power BI report is organized into two pages—**Executive Overview** and **Detailed Health Analysis**—with Gender, Region, and Smoking Status slicers.

### Headline figures

| Measure | Reported result |
|---|---:|
| Total records | 10,000 |
| Current smokers | 3,015 (30.15%) |
| Former smokers | 2,722 (27.22%) |
| Never smoked | 4,263 (42.63%) |
| Ever-smoked categories combined | 5,737 (57.37%) |
| Records with a recorded organ category | 7,227 (72.27%) |
| Records with a recorded health-condition category | 5,772 (57.72%) |
| Average cigarettes/day among current smokers | 17.11 |
| Average smoking duration among current smokers | 17.67 years |
| High BP category under the primary project rule | 6,049 (60.49%) |

### Interpretation in brief

- Current-smoker prevalence is close to 30% overall and varies only modestly across the reported age groups and regions.
- The 60+ age group contains the largest number of current smokers, but it is also the largest age group in the dataset. Counts should not be confused with within-group prevalence.
- The recorded-condition percentages are similar across smoking-status groups in the supplied summary. This is a description of this dataset, not evidence that smoking has no health effects.
- The BP categories are based on analyst-selected thresholds. They are analytical groupings, not clinical diagnoses.
- The pack-years calculation cannot estimate former smokers' historical exposure because their cigarettes/day field is recorded as zero.

## 2. Dataset and validation profile

The supplied CSV contains 15 source columns. The semantic model includes demographic fields, smoking fields, recorded organ and condition labels, diagnosis date, cholesterol, blood-pressure readings, BMI, and resting heart rate.

The current `validation_summary.json` reports:

| Validation item | Result |
|---|---:|
| Rows | 10,000 |
| Distinct Patient_ID values | 10,000 |
| Missing values | 0 |
| Model measures | 7 |
| Report pages | 2 |
| Slicer sync groups | Gender (2), Smoking Status (2), Region (2) |
| Opening report page | ExecutiveOverview |
| Theme registered | true |
| Rendered in Power BI Desktop | false |

These checks describe the supplied validation artifact. They do not independently establish source-data authenticity, representativeness, privacy status, or permission to publish.

## 3. Core KPIs and definitions

| KPI | Value | Calculation / interpretation |
|---|---:|---|
| Total Patients | 10,000 | Row count of the analysis table |
| Total Current Smokers | 3,015 | Count where `Smoking_Status = "Current Smoker"` |
| Patients with Recorded Organ | 7,227 | Count where `Diagnosed_Organ` is not `No Recorded Organ Condition` |
| Patients with Recorded Condition | 5,772 | Count where `Health_Condition` is not `No Diagnosed Condition` |
| Smoker Prevalence Rate | 30.15% | Current smokers divided by total records |

The recorded-organ and recorded-condition KPIs are independent classifications. The report records 2,692 records with an organ category but no diagnosed condition, and 1,237 records with a condition label but no recorded organ category. They should not be treated as nested groups.

### DAX definitions represented in the model

```dax
Total Patients =
COUNTROWS('Smoking_Health_Analysis')

Total Current Smokers =
CALCULATE(
    COUNTROWS('Smoking_Health_Analysis'),
    'Smoking_Health_Analysis'[Smoking_Status] = "Current Smoker"
)

Patients with Recorded Organ =
CALCULATE(
    COUNTROWS('Smoking_Health_Analysis'),
    'Smoking_Health_Analysis'[Diagnosed_Organ] <> "No Recorded Organ Condition"
)

Patients with Recorded Condition =
CALCULATE(
    COUNTROWS('Smoking_Health_Analysis'),
    'Smoking_Health_Analysis'[Health_Condition] <> "No Diagnosed Condition"
)

Smoker Prevalence Rate =
DIVIDE([Total Current Smokers], [Total Patients], 0)

Average Cigarettes Per Day =
AVERAGE('Smoking_Health_Analysis'[Cigarettes_Per_Day])

Average Total Cholesterol =
AVERAGE('Smoking_Health_Analysis'[Total_Cholesterol_mg_dL])
```

## 4. Calculated columns and classification assumptions

### 4.1 Age groups

The model groups ages into four bands:

- 18–29
- 30–44
- 45–59
- 60+

An integer sort column is used to keep the bands in chronological order.

### 4.2 Blood-pressure category

The primary project rule is:

| Category | Project rule |
|---|---|
| High | Systolic BP ≥ 130 **or** diastolic BP ≥ 80 |
| Elevated | Systolic BP 120–129 **and** diastolic BP < 80 |
| Lower Range | All remaining records |

The validation summary reports:

| BP category | Records | Share |
|---|---:|---:|
| High | 6,049 | 60.49% |
| Elevated | 1,451 | 14.51% |
| Lower Range | 2,500 | 25.00% |

The original analysis also describes an alternative, looser threshold scenario (High at approximately 140/90 and Elevated at 120–139 or 80–89), with reported counts of 2,447 High, 5,053 Elevated, and 2,500 Lower Range. The alternative rule and its cholesterol comparison should be recalculated from the CSV before those sensitivity figures are treated as validated. BP categories in this project are analytical assumptions and should not be represented as medical diagnoses.

### 4.3 Estimated pack-years and exposure categories

The model calculates:

`Pack Years = (Cigarettes_Per_Day / 20) × Years_Smoking`

The exposure categories are Never Smoked, Former Smokers (0 Current PY), Light (<10), Moderate (10–19.9), and Heavy (20+).

**Important interpretation limitation:** The supplied data records zero cigarettes/day for former smokers. Consequently, the formula returns zero pack-years for them even though their reported average smoking duration is 16.18 years. The label “Former Smokers (0 Current PY)” is a data limitation placeholder—not evidence of zero lifetime exposure. Historical cigarettes/day or a separately supplied lifetime exposure measure would be needed to estimate their past pack-years.

## 5. Smoking patterns and demographic distribution

### 5.1 Smoking status

| Smoking status | Records | Share |
|---|---:|---:|
| Never Smoked | 4,263 | 42.63% |
| Current Smoker | 3,015 | 30.15% |
| Former Smoker | 2,722 | 27.22% |

The combined former- and current-smoker groups contain 5,737 records (57.37%).

### 5.2 Cigarettes per day

| Smoking status | Records | Average cigarettes/day | Standard deviation |
|---|---:|---:|---:|
| Current Smoker | 3,015 | 17.11 | 10.78 |
| Former Smoker | 2,722 | 0.00 | 0.00 |
| Never Smoked | 4,263 | 0.00 | 0.00 |
| All records | 10,000 | 5.16 | 9.83 |

The zero values for former and never smokers reflect the supplied field coding. They should not be interpreted as a measurement of former smokers' historical smoking intensity.

### 5.3 Current smokers by age group

| Age group | Records | Current smokers | Prevalence within age group |
|---|---:|---:|---:|
| 18–29 | 1,774 | 508 | 28.64% |
| 30–44 | 2,213 | 668 | 30.19% |
| 45–59 | 2,279 | 715 | 31.37% |
| 60+ | 3,734 | 1,124 | 30.10% |
| Total | 10,000 | 3,015 | 30.15% |

The 60+ group has the largest number of current smokers because it is the largest age group. Its within-group prevalence (30.10%) is close to the overall prevalence (30.15%).

### 5.4 Gender and region

| Gender | Records | Current smokers | Prevalence |
|---|---:|---:|---:|
| Female | 4,769 | 1,445 | 30.30% |
| Male | 5,042 | 1,524 | 30.23% |
| Other | 189 | 46 | 24.34% |

| Region | Records | Current smokers | Prevalence |
|---|---:|---:|---:|
| Central | 1,609 | 518 | 32.19% |
| East | 1,746 | 531 | 30.41% |
| North | 2,400 | 721 | 30.04% |
| South | 1,971 | 573 | 29.07% |
| West | 2,274 | 672 | 29.55% |

The Other gender category contains 189 records, substantially fewer than Female and Male. Its percentage should therefore be interpreted with that smaller group size in mind.

## 6. Recorded organ and health-condition distribution

The report groups records across the following organ labels:

| Organ category | Records | Share of all records |
|---|---:|---:|
| Lungs | 2,792 | 27.92% |
| Heart | 2,197 | 21.97% |
| Liver | 1,231 | 12.31% |
| Kidneys | 1,007 | 10.07% |
| No Recorded Organ Condition | 2,773 | 27.73% |

Lungs and Heart together account for 4,989 records (49.89% of all records and approximately 69.0% of records with a recorded organ category).

The report also cross-tabulates the organ labels against health-condition labels. These are recorded categories in the supplied file; their clinical validity and data-generation process have not been established by the documentation reviewed.

## 7. Cholesterol by BP category

The primary project summary reports:

| BP category | Records | Average total cholesterol (mg/dL) |
|---|---:|---:|
| Lower Range | 2,500 | 195.35 |
| Elevated | 1,451 | 195.73 |
| High | 6,049 | 197.81 |
| All records | 10,000 | 196.89 |

The reported difference between the High and Lower Range averages is approximately 2.46 mg/dL. This is a small descriptive difference and should not be presented as a clinically meaningful effect.

**Validation note:** The previous narrative contains a different Elevated-category cholesterol value (197.18 mg/dL) in its alternative-threshold sensitivity discussion. The validation summary gives 195.73 mg/dL for the primary Elevated category. These values refer to different or insufficiently specified calculations and must not be mixed. Recompute each scenario directly from the CSV and clearly label the threshold rule before publishing a sensitivity comparison.

## 8. Health-condition patterns by smoking status and estimated exposure

The report records the following proportions with a diagnosed condition:

| Smoking status | Records | With recorded condition |
|---|---:|---:|
| Current Smoker | 3,015 | 57.45% |
| Former Smoker | 2,722 | 56.94% |
| Never Smoked | 4,263 | 58.41% |

The supplied analysis reports similar percentages across these categories. This does **not** establish that smoking has no health effect. Possible explanations cannot be determined from these descriptive tables alone; the data-generation process, measurement definitions, confounding variables, selection effects, and completeness of condition recording would need to be examined.

The source report also lists condition rates across estimated exposure groups:

| Exposure category | Records | With recorded condition |
|---|---:|---:|
| Never Smoked | 4,263 | 58.41% |
| Former Smokers (0 Current PY) | 2,722 | 56.94% |
| Light (<10 Pack-Years) | 1,562 | 58.96% |
| Moderate (10–19.9 Pack-Years) | 706 | 57.79% |
| Heavy (20+ Pack-Years) | 747 | 53.95% |

Because former smokers' historical intensity is unavailable and current exposure categories are calculated from the supplied fields, this table should not be described as a validated lifetime dose-response analysis.

### Inferential-statistics status

The previous report cites a chi-square p-value of 0.45 for condition rates by smoking status, an ANOVA p-value of 0.002 for cholesterol by BP category, and a heart-rate difference of approximately 3 bpm (with a reported p-value below 0.001). The inspected project documentation does not include the test scripts, full test specifications, assumptions, or reproducible outputs needed to independently verify these inferential claims. They are therefore retained as previously reported claims, not certified statistical results. Recalculate them with documented methods before using them in a formal portfolio case study or business recommendation.

## 9. Power BI report specification

| Page | Visual | Purpose |
|---|---|---|
| Executive Overview | Four KPI cards | Overall record and smoking/condition counts |
| Executive Overview | Smoking Status Distribution | Compare current, former, and never-smoker categories |
| Executive Overview | Average Cigarettes / Day by Status | Show the supplied current-use field by status |
| Executive Overview | Average Cholesterol by BP Risk | Compare cholesterol averages across project BP categories |
| Detailed Health Analysis | Current Smokers Across Age Groups | Compare counts by age band |
| Detailed Health Analysis | Organ-Wise Health Condition Matrix | Cross-tabulate recorded condition and organ labels |
| Detailed Health Analysis | Health Condition Distribution by Smoking Exposure | Compare recorded condition categories across exposure bands |

The model metadata describes Gender, Region, and Smoking Status slicer sync groups across the two pages. It also identifies Executive Overview as the opening page and confirms that a theme is registered.

**Rendering status:** The stored validation summary explicitly states `rendered_in_power_bi_desktop: false`. The PBIP definitions and metadata have been inspected, but the final rendered appearance, interactions, and refresh behavior have not been independently verified in Power BI Desktop.

## 10. Technical and reproducibility notes

- The semantic model contains one primary analysis table and a measures table.
- The model metadata includes seven measures and calculated columns for age grouping, BP classification, pack-years, and exposure categories.
- The Power Query definition currently references a machine-specific path: `C:/Users/pooja/Downloads/Smoking and Health Analysis/Smoking_Health_Analysis.csv`.
- That path must be replaced with a portable or locally configured source before another user can refresh the project reliably.
- The project includes a validation summary, but the statistical test scripts and a complete reproducible analysis pipeline were not part of the documentation inspected for this report.

## 11. Recommendations and next steps

1. **Confirm data provenance and publication rights.** Establish whether the dataset is synthetic, de-identified, or real data and whether it may legally and ethically be redistributed. Do not assume that unique IDs or zero missing values mean the dataset is anonymized.
2. **Make the data source portable.** Replace the hard-coded local path with a documented parameter or a project-relative source configuration, then test refresh on a second location.
3. **Recalculate the BP sensitivity analysis.** Use one clearly defined threshold rule per scenario and regenerate both category counts and cholesterol summaries from the CSV.
4. **Improve smoking-exposure measurement.** Obtain historical cigarettes/day for former smokers or exclude them from pack-year comparisons with an explicit explanation.
5. **Reproduce inferential tests.** Add scripts or notebooks documenting the statistical tests, variables, assumptions, sample sizes, effect sizes, confidence intervals, and p-values.
6. **Validate the rendered report.** Open the PBIP in Power BI Desktop, refresh it, inspect both pages, test slicer synchronization, and capture approved screenshots.
7. **Keep the documentation and dashboard aligned.** Re-run the validation checks whenever the CSV, DAX, Power Query, or report visuals change.

## 12. Limitations and responsible use

- Cross-sectional descriptive data cannot establish causality, temporal sequence, or individual prognosis.
- BP group thresholds are analyst-defined assumptions and change the resulting category distribution.
- Former smokers' historical daily cigarette consumption is not available in the supplied fields; the current pack-years calculation therefore understates their historical exposure.
- The Other gender group is comparatively small.
- Diagnosis_Date is present in the source schema but is not used in the report visuals described here.
- The provenance, representativeness, clinical validity, and redistribution rights of the dataset have not been established by the inspected documentation.
- Statistical significance claims require reproducible test code and should not be interpreted as evidence of clinical importance.

---

**Use restriction:** Educational and exploratory analytics only. Not for diagnosis, treatment, individual medical decisions, or causal claims.
