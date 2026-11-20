# Data Provenance, Governance & Privacy Notice — Smoking & Health Analysis

**Dataset File:** `Smoking_Health_Analysis.csv`  
**Dimensions:** `10,000` rows × `15` columns (`1,030,910` bytes)  
**Verified SHA-256:** `2623012EFFA755D635A0F360E68DE96B589EB35D708AA017AEA28022264F3B37`  
**Audit Date:** 2026-11-20

---

## 1. Provenance, Licensing & Redistribution Status (Unverified)

- **Original Source / Author:** Project brief issued by **Sapphire IQ ("Brilliant Minds Intelligent Solutions")** for an educational Power BI case study. Upstream dataset creator and original data-collection protocol are **not independently verified**.
- **Synthetic vs. De-Identified vs. Real Data Status:** **Not independently verified.** Do **not** assume or claim that this dataset is synthetic, anonymized, or real clinical data without verified upstream documentation.
- **Redistribution Permission & Git Exclusion (Option B):** **Not independently verified.** No open data license is claimed. Accordingly, **`Smoking_Health_Analysis.csv` is excluded from Git tracking via `.gitignore` and removed from rewritten `main` history** (alongside the historical `.zip` archive and Sapphire IQ brief PDF). The CSV is retained **strictly locally** for authorized analysis and is **not redistributed** in this public repository.

---

## 2. Empirical Data-Quality & Structural Observations

Independent inspection of `Smoking_Health_Analysis.csv` recorded the following structural characteristics (reported strictly as empirical observations, **not** proof of synthetic generation):

1. **Identifier Structure:** `10,000` unique `Patient_ID` values following a sequential 7-character pattern (`PT00001` through `PT10000`), with `0` nulls and `0` exact duplicate rows.
2. **Date Range:** `Diagnosis_Date` contains `0` invalid dates and spans `2021-01-01` through `2026-09-30`.
3. **Blood-Pressure Anomalies (`49` records, `0.49%`):** `49` rows record `Diastolic_BP_mmHg >= Systolic_BP_mmHg` (physiologically impossible in standard arterial blood-pressure measurement). These records are **preserved untouched** in the source CSV and flagged transparently via a calculated column (`BP Anomaly Flag`) rather than silently deleted or altered.
4. **Former-Smoker Intensity Coding:** All `2,722` `Former Smoker` records have `Cigarettes_Per_Day = 0` despite recording `Years_Smoking` from `1` to `49` years (mean `16.18` years). Lifetime pack-years cannot be estimated for former smokers from the supplied fields.
5. **Independent Organ vs. Condition Labels:** `Diagnosed_Organ` (`7,227` non-default records) and `Health_Condition` (`5,772` non-default records) are non-nested classifications (`2,692` organ-only, `1,237` condition-only, `4,535` both, `1,536` neither).

---

## 3. Privacy & Responsible-Use Safeguards

- **No Record-Level Exposure:** Individual `Patient_ID` values and row-level patient records must **never** appear in documentation, screenshots, issues, or validation outputs. `Patient_ID` is hidden in the Power BI semantic model (`isHidden: true`).
- **Non-Clinical / Non-Causal Scope:** This project is strictly an educational, descriptive analytics case study. It is not a medical device, diagnostic system, clinical risk calculator, or proof of causal relationships.

---

## 4. Known Technical Limitation: Windows `MAX_PATH`

The existing nested folder structure (`Smoking_Health_Analysis/Smoking_Health_Analysis_Project_v2/Smoking and Health Analysis/.../visuals/...`) exceeds Windows' legacy 260-character `MAX_PATH` limit on default Git installations. Windows users cloning this repository should enable long paths in Git (`git clone -c core.longpaths=true ...`). The nested structure is intentionally preserved to avoid breaking existing references.
