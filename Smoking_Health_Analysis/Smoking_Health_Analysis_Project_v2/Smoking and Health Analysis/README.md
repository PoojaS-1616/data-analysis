# Smoking & Health Analysis | Power BI Portfolio Project

An exploratory healthcare-analytics project built with **Microsoft Power BI**. It examines smoking-status patterns, recorded health-condition categories, blood-pressure groupings, cholesterol levels, and demographic distributions across a dataset of 10,000 records.

> **Responsible-use notice:** This is an educational analytics project, not a clinical tool. It must not be used for diagnosis, treatment decisions, individual risk assessment, or causal conclusions. Dataset provenance and redistribution permission have not yet been independently established; do not assume the data is synthetic or anonymized.

## Project at a glance

| Item | Description |
|---|---|
| Domain | Healthcare / public-health analytics |
| BI platform | Microsoft Power BI |
| Project format | Power BI Project (PBIP) |
| Dataset size | 10,000 rows × 15 source columns |
| Semantic model | One primary analysis table plus measures and calculated columns |
| Report pages | Executive Overview; Detailed Health Analysis |
| Interactive filters | Gender, Region, Smoking Status |
| Supporting files | Analytical report and validation summary |

## Business questions

This report explores the following questions:

1. How are records distributed across current, former, and never-smoker categories?
2. How does current-smoking prevalence vary across age groups, gender, and region?
3. What smoking intensity is recorded for current smokers?
4. How are recorded organ categories and health-condition labels distributed?
5. How do cholesterol averages compare across the project's assumed blood-pressure categories?
6. What patterns appear when recorded health-condition categories are compared with estimated smoking exposure?

These are descriptive questions. The dataset and analysis do not establish that smoking caused any recorded condition or measurement.

## Key figures in the current validation summary

| Metric | Reported value |
|---|---:|
| Total records | 10,000 |
| Distinct Patient_ID values | 10,000 |
| Current smokers | 3,015 (30.15%) |
| Former smokers | 2,722 (27.22%) |
| Never smoked | 4,263 (42.63%) |
| Ever-smoked categories combined | 5,737 (57.37%) |
| Records with a recorded organ category | 7,227 (72.27%) |
| Records with a recorded health-condition category | 5,772 (57.72%) |
| Average cigarettes/day among current smokers | 17.11 |
| Records classified as High BP under the primary project rule | 6,049 (60.49%) |

The figures above are reproduced from the project's current validation summary and report. They should be rechecked against the source file after any data or model change.

## Dashboard structure

### 1. Executive Overview

- Four KPI cards: total records, current smokers, records with a recorded organ category, and records with a recorded health-condition category.
- Smoking-status distribution.
- Average cigarettes per day by smoking status.
- Average total cholesterol by the project's BP risk category.

### 2. Detailed Health Analysis

- Current smokers across age groups.
- Organ-by-condition cross-tabulation.
- Health-condition distribution across estimated smoking-exposure categories.

Gender, Region, and Smoking Status slicers are configured to synchronize across the two report pages. The report metadata identifies **Executive Overview** as the opening page.

## Repository contents

| Path | Purpose |
|---|---|
| `Smoking_and_Health_Analysis.pbip` | Power BI project entry point |
| `Smoking_and_Health_Analysis.Dataset/` | Semantic-model definition, including `model.bim` |
| `Smoking_and_Health_Analysis.Report/` | Report pages, visuals, theme, and report metadata |
| `Smoking_Health_Analysis.csv` | Source dataset currently included in this repository |
| `Smoking_and_Health_Analysis_Report.md` | Detailed methodology, findings, and limitations |
| `validation_summary.json` | Stored validation metrics and report metadata |

## Open the Power BI project

1. Install or open a compatible version of **Power BI Desktop** that supports PBIP projects.
2. Download or clone this repository.
3. Open `Smoking_and_Health_Analysis.pbip` from this project folder.
4. Review the Power Query source expression before refreshing. The current model definition contains a machine-specific Windows file path; it will not work unchanged on another computer.
5. In Power BI Desktop, use **Transform data → Data source settings** (or edit the Power Query source) to point to the CSV in your local project folder.
6. Select **Close & Apply**, then refresh the model.
7. Save the project and inspect both report pages.

### First-refresh checks

With all slicers cleared, compare the report against the validation summary:

- Total records: **10,000**
- Current smokers: **3,015**
- Records with recorded organ category: **7,227**
- Records with recorded health-condition category: **5,772**
- Average cigarettes/day for current smokers: approximately **17.11**
- Primary BP category counts: High **6,049**, Elevated **1,451**, Lower Range **2,500**

Also test that each slicer selection is reflected on both report pages. These are expected-value checks, not proof that the report has rendered correctly. The stored validation summary states that rendering in Power BI Desktop has **not** yet been verified.

## Metric definitions and interpretation notes

- **Current-smoker prevalence:** current-smoker records divided by all records in the current filter context.
- **Recorded organ:** `Diagnosed_Organ` is not equal to `No Recorded Organ Condition`.
- **Recorded condition:** `Health_Condition` is not equal to `No Diagnosed Condition`.
- **Pack-years formula in the current model:** `(Cigarettes_Per_Day / 20) × Years_Smoking`.
- **BP categories:** analyst-defined thresholds; see the analytical report. They are not presented as a clinical diagnosis.

The two recorded-condition KPIs are separate classifications and should not be interpreted as nested populations.

## Data quality, provenance, and privacy

The validation summary reports 10,000 rows, 10,000 distinct Patient_ID values, and zero missing values. These checks alone do not establish that the data is real, synthetic, anonymized, representative, or approved for redistribution.

Before distributing this repository further:

- Confirm the dataset's original source and license or written redistribution permission.
- Confirm whether the records are synthetic, de-identified, or real personal/health data.
- If permission or privacy status is uncertain, do not publish or redistribute the CSV. Remove it from future releases only after reviewing the appropriate repository-history implications.
- Do not add real patient details, identifiers, or sensitive records to screenshots, issues, or documentation.

## Limitations

- The analysis is cross-sectional and descriptive; it cannot establish causality or change over time.
- The BP thresholds are analyst assumptions and materially affect category counts.
- Former smokers have zero cigarettes/day in the supplied data. Their historical daily intensity is not recorded, so the current pack-years calculation assigns them zero even though the report records an average smoking duration of about 16.18 years. Their calculated exposure must not be interpreted as zero lifetime exposure.
- The report contains inferential statistics (including chi-square and ANOVA p-values), but the underlying test scripts and full test specifications are not included in the inspected project documentation. Those p-values are therefore reported claims, not independently reproduced results in this repository.
- The validation summary records `rendered_in_power_bi_desktop: false`; visual rendering and interaction remain to be confirmed in Power BI Desktop.
- Diagnosis_Date is present in the source schema but is not used in the current report visuals.

## Tools and techniques

- Microsoft Power BI Desktop
- Power BI Project (PBIP)
- DAX measures and calculated columns
- Power Query (M)
- Markdown documentation
- JSON-based validation summary

## Documentation

See [the detailed analytical report](Smoking_and_Health_Analysis_Report.md) for KPI definitions, reported findings, calculation assumptions, dashboard specifications, and limitations.

---

**Project status:** Documented PBIP project; Power BI Desktop rendering and portable refresh are not yet independently verified.

**Disclaimer:** For educational and exploratory analytics only. Not medical advice, not a diagnostic system, and not evidence of causal relationships.
