# Smoking and Health Analysis — Power BI project

Power BI project (PBIP) for the Sapphire IQ *Smoking and Health Analysis Dashboard* brief
(`Sapphire IQ Smoking and Health Analysis.pdf`).

## Contents

| Item | Purpose |
| :--- | :--- |
| `Smoking_and_Health_Analysis.pbip` | Open this in Power BI Desktop |
| `Smoking_and_Health_Analysis.Dataset/` | Semantic model (`model.bim`): table, 7 measures, calculated columns |
| `Smoking_and_Health_Analysis.Report/` | Two-page report (Executive Overview, Detailed Health Analysis) |
| `Smoking_Health_Analysis.csv` | Source data (10,000 rows) |
| `Smoking_and_Health_Analysis_Report.md` | Written analytical report |
| `validation_summary.json` | Figures recomputed from the CSV |

## Open and refresh

The Power Query source is set to:

`C:/Users/pooja/Downloads/Smoking and Health Analysis/Smoking_Health_Analysis.csv`

1. Extract the zip so the folder is exactly `C:\Users\pooja\Downloads\Smoking and Health Analysis\` (choose *Downloads* as the destination; do not leave an extra wrapper folder).
2. Open `Smoking_and_Health_Analysis.pbip` in Power BI Desktop.
3. **Home → Refresh.** If the source is not found: **Transform data → Data source settings → Change Source**, point to the CSV, then **Close & Apply**.
4. Save the project in Power BI Desktop.

## Checks to do after the first refresh (with all slicers cleared)

- KPI cards show **10,000**, **3,015**, **7,227**, **5,772**.
- Avg Cigarettes / Day by Status shows **17.11** for Current Smoker and 0 for the other two.
- Selecting a value in a slicer on one page applies on the other page (sync groups: Gender, Region, Smoking Status).
- The report opens on *Executive Overview* and uses the Neutral Healthcare Theme (Home → Themes).
- Matrix and 100% stacked chart are readable.

## What changed in this version

- Slicers on both pages are now in sync groups (previously each page filtered independently).
- Custom theme is registered in `report.json` and the base-theme file it references is present.
- Report opens on page 1.
- Written report rewritten: corrected cholesterol range, standard deviations, Lungs + Heart share and the over-stated interpretation; aligned to the dashboard as built; added a BP-threshold sensitivity check and limitations.
- Removed backup files, duplicate theme files and machine-specific `localSettings.json`.

## Not verified here

The project could not be opened in Power BI Desktop when it was prepared, so visuals have not been rendered. The checks above confirm it on your machine.

*Educational/exploratory analysis only. It does not establish diagnoses or prove causation.*
