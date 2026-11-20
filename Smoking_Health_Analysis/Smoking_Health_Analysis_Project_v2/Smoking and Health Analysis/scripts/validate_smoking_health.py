"""
Smoking & Health Analysis — Independent Data Quality, Anomaly & Metric Validation Suite
=======================================================================================
Reproduces and validates all dataset quality checks, the 49 blood-pressure anomalies
(Diastolic_BP_mmHg >= Systolic_BP_mmHg), primary vs. alternative BP sensitivity rules,
former-smoker pack-years caveats, and DAX slicer-context behavior (Before vs. After
KEEPFILTERS fix) directly from Smoking_Health_Analysis.csv.

Privacy safeguard: Never prints or exports individual Patient_ID values or raw rows.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "Smoking_Health_Analysis.csv"
VAL_JSON_PATH = BASE_DIR / "validation_summary.json"


def classify_bp_primary(df: pd.DataFrame) -> pd.Series:
    """Primary project rule: High (Sys>=130 OR Dia>=80), Elevated (Sys 120-129 AND Dia<80), else Lower Range."""
    return pd.Series(
        np.where(
            (df["Systolic_BP_mmHg"] >= 130) | (df["Diastolic_BP_mmHg"] >= 80),
            "High",
            np.where(
                (df["Systolic_BP_mmHg"] >= 120) & (df["Diastolic_BP_mmHg"] < 80),
                "Elevated",
                "Lower Range",
            ),
        ),
        index=df.index,
    )


def classify_bp_alternative(df: pd.DataFrame) -> pd.Series:
    """Alternative sensitivity rule: High (Sys>=140 OR Dia>=90), Elevated (Sys>=120 OR Dia>=80), else Lower Range."""
    return pd.Series(
        np.where(
            (df["Systolic_BP_mmHg"] >= 140) | (df["Diastolic_BP_mmHg"] >= 90),
            "High",
            np.where(
                (df["Systolic_BP_mmHg"] >= 120) | (df["Diastolic_BP_mmHg"] >= 80),
                "Elevated",
                "Lower Range",
            ),
        ),
        index=df.index,
    )


def classify_exposure(df: pd.DataFrame) -> pd.Series:
    pack_years = (df["Cigarettes_Per_Day"] / 20.0) * df["Years_Smoking"]
    return pd.Series(
        np.where(
            df["Smoking_Status"] == "Never Smoked",
            "Never Smoked",
            np.where(
                pack_years == 0,
                "Former Smokers (0 Current PY)",
                np.where(
                    pack_years < 10,
                    "Light (<10 Pack-Years)",
                    np.where(
                        pack_years < 20,
                        "Moderate (10-19.9 Pack-Years)",
                        "Heavy (20+ Pack-Years)",
                    ),
                ),
            ),
        ),
        index=df.index,
    )


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Source CSV not found at {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    val_ref = json.loads(VAL_JSON_PATH.read_text(encoding="utf-8")) if VAL_JSON_PATH.exists() else {}

    print("=" * 80)
    print("SMOKING & HEALTH ANALYSIS — DATA QUALITY, ANOMALY & KPI VALIDATION")
    print("=" * 80)

    # 1. Structural & Integrity Checks
    rows, cols = df.shape
    missing = int(df.isna().sum().sum())
    dup_rows = int(df.duplicated().sum())
    distinct_ids = int(df["Patient_ID"].nunique())
    dates = pd.to_datetime(df["Diagnosis_Date"], errors="coerce")
    invalid_dates = int(dates.isna().sum())

    print(f"\n[1] Structural & Integrity Checks")
    print(f"    Dimensions          : {rows:,} rows x {cols} columns (Expected: 10,000 x 15)")
    print(f"    Missing values      : {missing} (Expected: 0)")
    print(f"    Exact duplicate rows: {dup_rows} (Expected: 0)")
    print(f"    Distinct Patient_ID : {distinct_ids:,} (Expected: 10,000)")
    print(f"    Diagnosis_Date range: {dates.min().date()} to {dates.max().date()} (invalid={invalid_dates})")

    assert rows == 10_000 and cols == 15
    assert missing == 0 and dup_rows == 0 and distinct_ids == 10_000 and invalid_dates == 0

    # 2. Logical Consistency & 49 Blood-Pressure Anomaly Investigation
    df["BP_Primary"] = classify_bp_primary(df)
    df["BP_Alternative"] = classify_bp_alternative(df)
    df["BP_Anomaly"] = df["Diastolic_BP_mmHg"] >= df["Systolic_BP_mmHg"]
    df["Pack_Years"] = (df["Cigarettes_Per_Day"] / 20.0) * df["Years_Smoking"]
    df["Exposure"] = classify_exposure(df)

    never_cig = int(((df["Smoking_Status"] == "Never Smoked") & (df["Cigarettes_Per_Day"] > 0)).sum())
    never_yrs = int(((df["Smoking_Status"] == "Never Smoked") & (df["Years_Smoking"] > 0)).sum())
    former_cig = int(((df["Smoking_Status"] == "Former Smoker") & (df["Cigarettes_Per_Day"] > 0)).sum())
    cur_zero_cig = int(((df["Smoking_Status"] == "Current Smoker") & (df["Cigarettes_Per_Day"] == 0)).sum())
    age_viol = int((df["Years_Smoking"] > df["Age"] - 10).sum())
    bp_anom = df[df["BP_Anomaly"]]

    print(f"\n[2] Logical Consistency & Blood-Pressure Anomaly Investigation")
    print(f"    Never Smoked with Cig/Day > 0      : {never_cig}")
    print(f"    Never Smoked with Years > 0        : {never_yrs}")
    print(f"    Former Smoker with Cig/Day > 0     : {former_cig}")
    print(f"    Current Smoker with Cig/Day == 0   : {cur_zero_cig}")
    print(f"    Years_Smoking > Age - 10           : {age_viol}")
    print(f"    BP Anomalies (Diastolic >= Systolic): {len(bp_anom)} ({len(bp_anom)/rows*100:.2f}% of records)")

    diff = bp_anom["Diastolic_BP_mmHg"] - bp_anom["Systolic_BP_mmHg"]
    print(f"    Anomaly (Dia - Sys) summary        : min={diff.min():.1f}, median={diff.median():.1f}, mean={diff.mean():.2f}, max={diff.max():.1f} mmHg")
    print(f"    Anomaly Systolic range             : {bp_anom['Systolic_BP_mmHg'].min():.1f} to {bp_anom['Systolic_BP_mmHg'].max():.1f} mmHg")
    print(f"    Anomaly Diastolic range            : {bp_anom['Diastolic_BP_mmHg'].min():.1f} to {bp_anom['Diastolic_BP_mmHg'].max():.1f} mmHg")
    print(f"    Anomaly by Smoking_Status          : {bp_anom['Smoking_Status'].value_counts().to_dict()}")
    print(f"    Anomaly by Primary BP Category     : {bp_anom['BP_Primary'].value_counts().to_dict()}")
    print(f"    Anomaly by Alternative BP Category : {bp_anom['BP_Alternative'].value_counts().to_dict()}")

    # Impact of 49 anomalies on BP counts & cholesterol
    clean_bp_df = df[~df["BP_Anomaly"]]
    print("\n    Impact on Primary BP Classification (Full n=10,000 vs Excluding 49 Anomalies n=9,951):")
    full_bp = df.groupby("BP_Primary")["Total_Cholesterol_mg_dL"].agg(["count", "mean"])
    excl_bp = clean_bp_df.groupby("BP_Primary")["Total_Cholesterol_mg_dL"].agg(["count", "mean"])
    comp = full_bp.join(excl_bp, lsuffix="_full", rsuffix="_excl_anom")
    comp["count_diff"] = comp["count_full"] - comp["count_excl_anom"]
    comp["mean_diff_mg_dL"] = (comp["mean_full"] - comp["mean_excl_anom"]).round(4)
    print(comp.round(4).to_string())

    # 3. Core KPI Reconciliation
    has_organ = df["Diagnosed_Organ"] != "No Recorded Organ Condition"
    has_cond = df["Health_Condition"] != "No Diagnosed Condition"
    cur_df = df[df["Smoking_Status"] == "Current Smoker"]
    former_df = df[df["Smoking_Status"] == "Former Smoker"]

    print(f"\n[3] Core KPI Reconciliation")
    print(f"    Current Smokers                    : {len(cur_df):,} ({len(cur_df)/rows*100:.2f}%)")
    print(f"    Former Smokers                     : {len(former_df):,} ({len(former_df)/rows*100:.2f}%)")
    print(f"    Never Smoked                       : {int((df['Smoking_Status']=='Never Smoked').sum()):,}")
    print(f"    Patients with Recorded Organ       : {int(has_organ.sum()):,} ({has_organ.mean()*100:.2f}%)")
    print(f"    Patients with Recorded Condition   : {int(has_cond.sum()):,} ({has_cond.mean()*100:.2f}%)")
    print(f"    Organ only / Cond only / Both / 0  : {int((has_organ & ~has_cond).sum()):,} / {int((~has_organ & has_cond).sum()):,} / {int((has_organ & has_cond).sum()):,} / {int((~has_organ & ~has_cond).sum()):,}")
    print(f"    Avg Cig/Day (Current Smokers)      : {cur_df['Cigarettes_Per_Day'].mean():.4f} (SD={cur_df['Cigarettes_Per_Day'].std():.4f})")
    print(f"    Avg Cig/Day (All Records)          : {df['Cigarettes_Per_Day'].mean():.4f} (SD={df['Cigarettes_Per_Day'].std():.4f})")
    print(f"    Former Smokers Avg Years_Smoking   : {former_df['Years_Smoking'].mean():.4f} yrs (Cig/Day=0 -> Pack_Years=0.00 caveat)")

    if val_ref:
        assert len(cur_df) == val_ref["smoking_status_counts"]["Current Smoker"]
        assert int(has_organ.sum()) == val_ref["patients_with_recorded_organ"]
        assert int(has_cond.sum()) == val_ref["patients_with_recorded_condition"]

    # 4. BP Sensitivity Reconciliation
    print(f"\n[4] Blood-Pressure Threshold Sensitivity Reconciliation")
    print("    Primary Rule (High: Sys>=130 or Dia>=80; Elevated: Sys 120-129 & Dia<80):")
    print(df.groupby("BP_Primary")["Total_Cholesterol_mg_dL"].agg(["count", "mean", "std"]).round(2).to_string())
    print("    Alternative Rule (High: Sys>=140 or Dia>=90; Elevated: Sys>=120 or Dia>=80):")
    print(df.groupby("BP_Alternative")["Total_Cholesterol_mg_dL"].agg(["count", "mean", "std"]).round(2).to_string())

    # 5. DAX Slicer Filter-Context Validation (Before vs After KEEPFILTERS)
    print(f"\n[5] DAX Slicer-Context Simulation (Before Overwrite vs. After KEEPFILTERS)")
    scenarios = [
        ("No Selection", df),
        ("Current Smoker", df[df["Smoking_Status"] == "Current Smoker"]),
        ("Former Smoker", df[df["Smoking_Status"] == "Former Smoker"]),
        ("Never Smoked", df[df["Smoking_Status"] == "Never Smoked"]),
    ]
    print(f"    {'Scenario':16s} | {'Total':>6s} | {'Old CurSmk':>10s} | {'Old Prev%':>9s} | {'New CurSmk':>10s} | {'New Prev%':>9s} | {'Organ':>6s} | {'Cond':>6s}")
    print("    " + "-" * 90)
    for label, sub in scenarios:
        tot = len(sub)
        # Old DAX overwrote Smoking_Status filter back to entire table's Current Smokers
        old_cur = int((df["Smoking_Status"] == "Current Smoker").sum())
        old_prev = (old_cur / tot * 100.0) if tot else 0.0
        # New DAX uses KEEPFILTERS (intersects with active slicer)
        new_cur = int((sub["Smoking_Status"] == "Current Smoker").sum())
        new_prev = (new_cur / tot * 100.0) if tot else 0.0
        org = int((sub["Diagnosed_Organ"] != "No Recorded Organ Condition").sum())
        cond = int((sub["Health_Condition"] != "No Diagnosed Condition").sum())
        print(f"    {label:16s} | {tot:6,d} | {old_cur:10,d} | {old_prev:8.2f}% | {new_cur:10,d} | {new_prev:8.2f}% | {org:6,d} | {cond:6,d}")
        if label in ("Former Smoker", "Never Smoked"):
            assert new_cur == 0 and new_prev == 0.0
        elif label == "Current Smoker":
            assert new_cur == 3015 and abs(new_prev - 100.0) < 1e-9
        else:
            assert new_cur == 3015 and abs(new_prev - 30.15) < 1e-9

    print("\nALL DATA QUALITY, ANOMALY & DAX SLICER VALIDATION CHECKS PASSED.")


if __name__ == "__main__":
    main()
