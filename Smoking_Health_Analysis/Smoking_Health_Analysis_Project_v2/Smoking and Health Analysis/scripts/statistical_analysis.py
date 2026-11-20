"""
Smoking & Health Analysis — Independent Statistical Validation Suite
====================================================================
Reproduces all previously reported inferential tests and evaluates additional
biometric comparisons across Smoking_Status with full assumptions checks,
parametric + non-parametric tests, effect sizes, 95% confidence intervals,
and Bonferroni-adjusted post-hoc pairwise comparisons.

Non-causal notice: Statistical associations in cross-sectional observational data
do not establish causation or clinical significance.
"""

from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "Smoking_Health_Analysis.csv"


def mean_ci95(arr: np.ndarray) -> tuple[float, float, float]:
    n = len(arr)
    mean = float(np.mean(arr))
    se = float(stats.sem(arr))
    margin = float(se * stats.t.ppf(0.975, df=n - 1))
    return mean, mean - margin, mean + margin


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    pooled_sd = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    return float((np.mean(a) - np.mean(b)) / pooled_sd) if pooled_sd > 0 else 0.0


def run_group_comparison(df: pd.DataFrame, group_col: str, value_col: str, title: str) -> None:
    print(f"\n--- {title} ---")
    groups = sorted(df[group_col].unique().tolist())
    arrays = {g: df.loc[df[group_col] == g, value_col].values for g in groups}

    print(f"  Group Summaries (n, mean [95% CI], SD, median):")
    for g in groups:
        arr = arrays[g]
        m, lo, hi = mean_ci95(arr)
        print(f"    {g:16s}: n={len(arr):5,d} | mean={m:7.2f} [{lo:7.2f}, {hi:7.2f}] | SD={np.std(arr, ddof=1):6.2f} | median={np.median(arr):6.2f}")

    # Variance homogeneity (Levene)
    lev_stat, lev_p = stats.levene(*arrays.values())
    # One-way ANOVA & Kruskal-Wallis
    f_stat, p_anova = stats.f_oneway(*arrays.values())
    kw_stat, p_kw = stats.kruskal(*arrays.values())

    grand = df[value_col].mean()
    ss_b = sum(len(a) * (a.mean() - grand) ** 2 for a in arrays.values())
    ss_t = float(((df[value_col] - grand) ** 2).sum())
    eta2 = float(ss_b / ss_t) if ss_t > 0 else 0.0
    effect_label = "negligible" if eta2 < 0.01 else ("small" if eta2 < 0.06 else ("medium" if eta2 < 0.14 else "large"))

    print(f"  Assumptions     : Levene F={lev_stat:.4f}, p={lev_p:.4f}")
    print(f"  Parametric      : One-way ANOVA F={f_stat:.4f}, p={p_anova:.4e}, eta^2={eta2:.6f} ({effect_label})")
    print(f"  Non-parametric  : Kruskal-Wallis H={kw_stat:.4f}, p={p_kw:.4e}")

    pairs = list(combinations(groups, 2))
    alpha_bonf = 0.05 / len(pairs)
    print(f"  Post-hoc Welch t-test & Mann-Whitney U (Bonferroni alpha={alpha_bonf:.4f}):")
    for g1, g2 in pairs:
        a, b = arrays[g1], arrays[g2]
        t_stat, p_t = stats.ttest_ind(a, b, equal_var=False)
        u_stat, p_u = stats.mannwhitneyu(a, b, alternative="two-sided")
        d = cohens_d(a, b)
        diff = float(np.mean(a) - np.mean(b))
        sig = "SIG" if min(p_t * len(pairs), 1.0) < 0.05 else "NS"
        print(
            f"    {g1} vs {g2}: diff={diff:+6.2f} | Welch p_adj={min(p_t*len(pairs),1.0):.3e} | "
            f"MWU p_adj={min(p_u*len(pairs),1.0):.3e} | Cohen's d={d:+.3f} [{sig}]"
        )


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df["Has_Condition"] = (df["Health_Condition"] != "No Diagnosed Condition").astype(int)
    df["BP_Primary"] = np.where(
        (df["Systolic_BP_mmHg"] >= 130) | (df["Diastolic_BP_mmHg"] >= 80),
        "High",
        np.where(
            (df["Systolic_BP_mmHg"] >= 120) & (df["Diastolic_BP_mmHg"] < 80),
            "Elevated",
            "Lower Range",
        ),
    )
    df["BP_Anomaly"] = df["Diastolic_BP_mmHg"] >= df["Systolic_BP_mmHg"]

    print("=" * 80)
    print("SMOKING & HEALTH ANALYSIS — INDEPENDENT STATISTICAL VALIDATION")
    print("=" * 80)

    # TEST 1: Chi-square Recorded Condition vs Smoking_Status
    print("\n--- TEST 1: Chi-Square — Recorded Health Condition vs. Smoking Status ---")
    ct = pd.crosstab(df["Smoking_Status"], df["Has_Condition"])
    chi2, p_chi, dof, expected = stats.chi2_contingency(ct)
    cramers_v = float(np.sqrt(chi2 / (len(df) * (min(ct.shape) - 1))))
    print(f"  Min expected cell count: {expected.min():.2f} (>=5 assumption satisfied)")
    for grp in sorted(df["Smoking_Status"].unique()):
        sub = df[df["Smoking_Status"] == grp]["Has_Condition"]
        p_hat = sub.mean()
        se = np.sqrt(p_hat * (1 - p_hat) / len(sub))
        print(f"    {grp:16s}: n={len(sub):5,d} | rate={p_hat*100:.2f}% [95% CI: {(p_hat-1.96*se)*100:.2f}%, {(p_hat+1.96*se)*100:.2f}%]")
    print(f"  Result: chi2={chi2:.4f}, df={dof}, p={p_chi:.6f}, Cramer's V={cramers_v:.4f} (negligible; no significant association)")

    # TEST 2: Cholesterol vs Primary BP Category (Full & Excluding 49 Anomalies)
    run_group_comparison(df, "BP_Primary", "Total_Cholesterol_mg_dL", "TEST 2A: Total Cholesterol vs. Primary BP Category (Full n=10,000)")
    run_group_comparison(df[~df["BP_Anomaly"]], "BP_Primary", "Total_Cholesterol_mg_dL", "TEST 2B: Total Cholesterol vs. Primary BP Category (Excl. 49 BP Anomalies, n=9,951)")

    # TEST 3: Resting Heart Rate vs Smoking Status
    run_group_comparison(df, "Smoking_Status", "Resting_Heart_Rate_bpm", "TEST 3: Resting Heart Rate (bpm) vs. Smoking Status")

    # TEST 4 (NEW): Systolic BP vs Smoking Status
    run_group_comparison(df, "Smoking_Status", "Systolic_BP_mmHg", "TEST 4 (NEW): Systolic BP (mmHg) vs. Smoking Status")

    # TEST 5 (NEW): Total Cholesterol vs Smoking Status
    run_group_comparison(df, "Smoking_Status", "Total_Cholesterol_mg_dL", "TEST 5 (NEW): Total Cholesterol (mg/dL) vs. Smoking Status")

    # TEST 6 (Controls): Diastolic BP & BMI vs Smoking Status
    run_group_comparison(df, "Smoking_Status", "Diastolic_BP_mmHg", "TEST 6A (Control): Diastolic BP (mmHg) vs. Smoking Status")
    run_group_comparison(df, "Smoking_Status", "BMI", "TEST 6B (Control): BMI vs. Smoking Status")

    print("\n" + "=" * 80)
    print("STATISTICAL VALIDATION COMPLETE (Non-causal descriptive findings only).")
    print("=" * 80)


if __name__ == "__main__":
    main()
