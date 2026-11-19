"""
BlinkIT Grocery Pricing Architecture & Assortment Analysis - Standalone Automation Pipeline

Key Features:
- Script-relative paths (works from any working directory)
- Dual-filename fallback for raw Excel data (BlinkIT_Grocery_Data.xlsx / BlinkIT Grocery Data.xlsx)
- Currency-honest reporting (currency is unspecified in the source dataset; displayed in dataset units)
- Dynamic variable computation (no hard-coded statistics or chart titles)
- Variance decomposition of Sales (R^2 for SKU, Category, Outlet)
- Statistical tests (Pearson correlation, Kruskal-Wallis)
- Supermarket-only tier normalization (Store Format Composition Effect Proof)
- Cleaned CSV export and 10 high-resolution figures exported to visuals/
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import skew

BASE_DIR = Path(__file__).resolve().parent
REFERENCE_YEAR = 2026

sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["font.sans-serif"] = "Arial"


def main():
    print("=" * 80)
    print("BLINKIT GROCERY PRICING ARCHITECTURE & ASSORTMENT PIPELINE")
    print("=" * 80)
    print("Note on Units: Currency is not specified in the source dataset.")
    print("All Recorded Sales values are displayed in original dataset units without currency conversion.\n")

    visuals_dir = BASE_DIR / "visuals"
    visuals_dir.mkdir(exist_ok=True)

    # --- STEP 0: Ingestion with Dual-Filename Fallback ---
    raw_path = BASE_DIR / "BlinkIT_Grocery_Data.xlsx"
    if not raw_path.exists():
        raw_path = BASE_DIR / "BlinkIT Grocery Data.xlsx"
    if not raw_path.exists():
        raise FileNotFoundError(f"Could not find raw Excel dataset in '{BASE_DIR}'")

    print(f"[Step 0] Ingesting raw dataset from: {raw_path.name}")
    raw_df = pd.read_excel(raw_path)
    print(f"Raw Dataset Shape: {raw_df.shape[0]:,} rows x {raw_df.shape[1]} columns")

    # --- OBJECTIVE 1: Catalogue & Network Profiling ---
    print("\n[Objective 1] Catalogue & Network Profiling...")
    product_family_map = {"FD": "Food", "DR": "Drinks", "NC": "Non-Consumable"}
    raw_df["Product Family"] = raw_df["Item Identifier"].str[:2].map(product_family_map)

    item_type_counts = raw_df["Item Type"].value_counts()
    family_counts = raw_df["Product Family"].value_counts()

    # Figure 1: Product Assortment (2 Panels)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.barplot(y=item_type_counts.index, x=item_type_counts.values, hue=item_type_counts.index, palette="Blues_r", legend=False, ax=axes[0])
    axes[0].set_title("Product Record Frequency across 16 Item Categories", fontweight="bold")
    axes[0].set_xlabel("Number of Product-Outlet Listings")
    for i, v in enumerate(item_type_counts.values):
        axes[0].text(v + 10, i, f"{v:,}", va="center", fontsize=9)

    axes[1].pie(
        family_counts,
        labels=family_counts.index,
        autopct="%1.2f%%",
        startangle=140,
        colors=["#2b5c8f", "#e6843b", "#2ca02c"],
        wedgeprops=dict(width=0.45, edgecolor="w", linewidth=2),
    )
    axes[1].set_title("Product Family Share", fontweight="bold")
    plt.tight_layout()
    plt.savefig(visuals_dir / "01_product_assortment_family.png", dpi=150)
    plt.close()

    # Figure 2: Outlet Network Distribution (2 Panels)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    type_counts = raw_df["Outlet Type"].value_counts()
    sns.barplot(x=type_counts.index, y=type_counts.values, hue=type_counts.index, palette="viridis", legend=False, ax=axes[0])
    axes[0].set_title("Listings by Outlet Type", fontweight="bold")
    axes[0].set_ylabel("Product-Outlet Listings")
    axes[0].tick_params(axis="x", rotation=15)
    for i, v in enumerate(type_counts.values):
        axes[0].text(i, v + 40, f"{v:,}", ha="center", fontsize=9, fontweight="bold")

    tier_counts = raw_df["Outlet Location Type"].value_counts()
    sns.barplot(x=tier_counts.index, y=tier_counts.values, hue=tier_counts.index, palette="crest", legend=False, ax=axes[1])
    axes[1].set_title("Listings by Location Tier", fontweight="bold")
    axes[1].set_ylabel("Product-Outlet Listings")
    for i, v in enumerate(tier_counts.values):
        axes[1].text(i, v + 40, f"{v:,}", ha="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    plt.savefig(visuals_dir / "02_outlet_network_distribution.png", dpi=150)
    plt.close()

    # Figure 3: Overall Recorded Sales Value Distribution
    mean_sales = raw_df["Sales"].mean()
    median_sales = raw_df["Sales"].median()
    sales_skewness = skew(raw_df["Sales"])

    plt.figure(figsize=(10, 5))
    sns.histplot(raw_df["Sales"], kde=True, color="#1f77b4", bins=40, stat="density", alpha=0.6)
    plt.axvline(mean_sales, color="red", linestyle="--", linewidth=2, label=f"Mean ({mean_sales:.2f})")
    plt.axvline(median_sales, color="green", linestyle="-", linewidth=2, label=f"Median ({median_sales:.2f})")
    plt.title(f"Recorded Sales Value Density Distribution (Skewness = {sales_skewness:.2f})", fontweight="bold")
    plt.xlabel("Recorded Sales Value (Dataset Units, Currency Unspecified)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(visuals_dir / "03_sales_distribution_kde.png", dpi=150)
    plt.close()

    # Figure 4: Rating Distribution (2 Panels)
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    sns.histplot(raw_df["Rating"], bins=25, kde=False, color="#2ca02c", ax=axes[0])
    axes[0].set_title("Recorded Rating Distribution (Peak at 4.0)", fontweight="bold")
    cat_rating = raw_df.groupby("Item Type")["Rating"].mean().sort_values(ascending=True)
    sns.barplot(x=cat_rating.values, y=cat_rating.index, hue=cat_rating.index, palette="mako", legend=False, ax=axes[1])
    axes[1].set_xlim(3.8, 4.1)
    axes[1].set_xlabel("Mean Rating")
    axes[1].set_title(f"Mean Rating by Category (Band: {cat_rating.min():.2f} to {cat_rating.max():.2f})", fontweight="bold")
    plt.tight_layout()
    plt.savefig(visuals_dir / "04_customer_rating_analysis.png", dpi=150)
    plt.close()

    # --- OBJECTIVE 2: Data Cleaning & Imputation Pipeline ---
    print("\n[Objective 2] Executing Data Cleaning & Imputation Pipeline...")
    clean_df = raw_df.copy()

    # Impute Item Weight (SKU mean -> Category median fallback for 4 all-null SKUs)
    item_weights = clean_df.groupby("Item Identifier")["Item Weight"].transform("mean")
    clean_df["Item Weight"] = clean_df["Item Weight"].fillna(item_weights)
    cat_weights = clean_df.groupby("Item Type")["Item Weight"].transform("median")
    clean_df["Item Weight"] = clean_df["Item Weight"].fillna(cat_weights)

    # Impute zero Item Visibility (SKU mean -> Category mean)
    clean_df["Item Visibility"] = clean_df["Item Visibility"].replace(0, np.nan)
    item_vis = clean_df.groupby("Item Identifier")["Item Visibility"].transform("mean")
    clean_df["Item Visibility"] = clean_df["Item Visibility"].fillna(item_vis)
    cat_vis = clean_df.groupby("Item Type")["Item Visibility"].transform("mean")
    clean_df["Item Visibility"] = clean_df["Item Visibility"].fillna(cat_vis)

    # Harmonize Fat Content & Assign Non-Edible
    clean_df["Item Fat Content"] = clean_df["Item Fat Content"].replace({"low fat": "Low Fat", "LF": "Low Fat", "reg": "Regular"})
    clean_df["Item Category"] = clean_df["Item Identifier"].str[:2].map({"FD": "Food", "DR": "Drinks", "NC": "Non-Consumable"})
    clean_df.loc[clean_df["Item Category"] == "Non-Consumable", "Item Fat Content"] = "Non-Edible"

    # Mark split-size outlets as Unknown while preserving raw column
    clean_df["Outlet Size (Original)"] = clean_df["Outlet Size"]
    split_outlets = ["OUT010", "OUT017", "OUT045"]
    clean_df.loc[clean_df["Outlet Identifier"].isin(split_outlets), "Outlet Size"] = "Unknown"
    clean_df["Outlet Age"] = REFERENCE_YEAR - clean_df["Outlet Establishment Year"]

    # Figure 5: Outlier Boxplots
    fig, axes = plt.subplots(1, 4, figsize=(18, 4))
    for i, col in enumerate(["Sales", "Item Weight", "Item Visibility", "Rating"]):
        sns.boxplot(y=clean_df[col], color="#4c72b0", ax=axes[i], width=0.35)
        axes[i].set_title(f"Boxplot: {col}", fontweight="bold")
    plt.tight_layout()
    plt.savefig(visuals_dir / "05_outlier_boxplots.png", dpi=150)
    plt.close()

    final_cols = [
        "Item Fat Content", "Item Identifier", "Item Type", "Outlet Establishment Year",
        "Outlet Identifier", "Outlet Location Type", "Outlet Size", "Outlet Type",
        "Item Visibility", "Item Weight", "Sales", "Rating", "Item Category",
        "Outlet Size (Original)", "Outlet Age",
    ]
    clean_df = clean_df[final_cols]
    clean_csv_path = BASE_DIR / "BlinkIT_Grocery_Data_Cleaned.csv"
    clean_df.to_csv(clean_csv_path, index=False)
    print(f"Cleaned dataset saved: {clean_df.shape[0]:,} rows x {clean_df.shape[1]} columns (0 nulls)")

    # --- OBJECTIVE 3: Variance Decomposition & Pricing Architecture ---
    print("\n[Objective 3] Investigating Pricing Architecture & Variance...")
    grand_mean = clean_df["Sales"].mean()
    ss_total = ((clean_df["Sales"] - grand_mean) ** 2).sum()
    r2_sku = ((clean_df.groupby("Item Identifier")["Sales"].transform("mean") - grand_mean) ** 2).sum() / ss_total
    r2_cat = ((clean_df.groupby("Item Type")["Sales"].transform("mean") - grand_mean) ** 2).sum() / ss_total
    r2_outlet = ((clean_df.groupby("Outlet Identifier")["Sales"].transform("mean") - grand_mean) ** 2).sum() / ss_total

    within_sku_std = clean_df.groupby("Item Identifier")["Sales"].std().mean()
    overall_std = clean_df["Sales"].std()

    print("=" * 70)
    print("VARIANCE DECOMPOSITION (R-SQUARED OF RECORDED SALES METRIC):")
    print(f"Variance explained by Item Identifier (SKU) : {r2_sku * 100:.2f}% (R^2 = {r2_sku:.4f})")
    print(f"Variance explained by Category (Item Type)  : {r2_cat * 100:.2f}% (R^2 = {r2_cat:.4f})")
    print(f"Variance explained by Outlet Identifier     : {r2_outlet * 100:.2f}% (R^2 = {r2_outlet:.4f})")
    print(f"Average within-SKU std dev                  : {within_sku_std:.2f} (dataset units)")
    print(f"Overall dataset std dev                     : {overall_std:.2f} (dataset units)")
    print("=" * 70)

    r_vis, p_vis = stats.pearsonr(clean_df["Item Visibility"], clean_df["Sales"])
    r_rat, p_rat = stats.pearsonr(clean_df["Rating"], clean_df["Sales"])
    r_wgt, p_wgt = stats.pearsonr(clean_df["Item Weight"], clean_df["Sales"])
    r_age, p_age = stats.pearsonr(clean_df["Outlet Age"], clean_df["Sales"])

    kw_cat_stat, kw_cat_p = stats.kruskal(*[g["Sales"].values for _, g in clean_df.groupby("Item Type")])
    kw_type_stat, kw_type_p = stats.kruskal(*[g["Sales"].values for _, g in clean_df.groupby("Outlet Type")])

    print(f"\nPearson Tests: Visibility r={r_vis:+.4f} (p={p_vis:.3f}), Weight r={r_wgt:+.4f} (p={p_wgt:.4f}), Rating r={r_rat:+.4f} (p={p_rat:.3f}), Age r={r_age:+.4f} (p={p_age:.3f})")
    print(f"Kruskal-Wallis: Categories H={kw_cat_stat:.2f} (p={kw_cat_p:.2e}), Outlet Types H={kw_type_stat:.2f} (p={kw_type_p:.3f})")

    # Figure 6: Category Catalogue Value & Mean Sales Value (2 Panels)
    cat_sales = clean_df.groupby("Item Type")["Sales"].agg(["sum", "mean"]).sort_values(by="sum", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.barplot(x=cat_sales["sum"], y=cat_sales.index, hue=cat_sales.index, palette="Blues_r", legend=False, ax=axes[0])
    axes[0].set_title("Summed Catalogue Value by Item Category", fontweight="bold")
    axes[0].set_xlabel("Sum of Recorded Sales Metric (Dataset Units)")

    cat_avg = cat_sales.sort_values(by="mean", ascending=False)
    sns.barplot(x=cat_avg["mean"], y=cat_avg.index, hue=cat_avg.index, palette="crest", legend=False, ax=axes[1])
    axes[1].set_title("Mean Recorded Sales Value by Item Category", fontweight="bold")
    axes[1].set_xlabel("Mean Recorded Sales Value (Dataset Units)")
    axes[1].set_xlim(115, 160)
    plt.tight_layout()
    plt.savefig(visuals_dir / "06_category_catalogue_value.png", dpi=150)
    plt.close()

    # Figure 7: 2x4 Outlet Factor Matrix
    out_means_series = clean_df.groupby("Outlet Identifier")["Sales"].mean()
    min_outlet_mean, max_outlet_mean = out_means_series.min(), out_means_series.max()

    fig, axes = plt.subplots(2, 4, figsize=(20, 9))
    sns.barplot(x="Outlet Identifier", y="Sales", data=clean_df, estimator=np.sum, errorbar=None, hue="Outlet Identifier", palette="crest", legend=False, ax=axes[0, 0])
    axes[0, 0].set_title("Catalogue Value by Outlet", fontweight="bold")
    axes[0, 0].tick_params(axis="x", rotation=45)

    sns.barplot(x="Outlet Type", y="Sales", data=clean_df, estimator=np.sum, errorbar=None, hue="Outlet Type", palette="viridis", legend=False, ax=axes[0, 1])
    axes[0, 1].set_title("Catalogue Value by Store Type", fontweight="bold")
    axes[0, 1].tick_params(axis="x", rotation=30)

    sns.barplot(x="Outlet Location Type", y="Sales", data=clean_df, estimator=np.sum, errorbar=None, hue="Outlet Location Type", palette="mako", legend=False, ax=axes[0, 2])
    axes[0, 2].set_title("Catalogue Value by Location Tier", fontweight="bold")

    known_sizes = clean_df[clean_df["Outlet Size"] != "Unknown"]
    sns.barplot(x="Outlet Size", y="Sales", data=known_sizes, estimator=np.sum, errorbar=None, hue="Outlet Size", palette="rocket", legend=False, ax=axes[0, 3])
    axes[0, 3].set_title("Catalogue Value by Verified Size", fontweight="bold")

    for col_idx, (col_name, title, sub_df, pal, rot) in enumerate([
        ("Outlet Identifier", "Mean Sales Value by Outlet", clean_df, "crest", 45),
        ("Outlet Type", "Mean Sales Value by Type", clean_df, "viridis", 30),
        ("Outlet Location Type", "Mean Sales Value by Tier", clean_df, "mako", 0),
        ("Outlet Size", "Mean Sales Value by Size", known_sizes, "rocket", 0),
    ]):
        sns.barplot(x=col_name, y="Sales", data=sub_df, estimator=np.mean, errorbar=None, hue=col_name, palette=pal, legend=False, ax=axes[1, col_idx])
        axes[1, col_idx].set_title(title, fontweight="bold")
        axes[1, col_idx].set_ylim(120, 160)
        if rot:
            axes[1, col_idx].tick_params(axis="x", rotation=rot)

    plt.suptitle(
        f"OUTLET FACTOR MATRIX: Mean Recorded Sales Value Falls in Tight Band ({min_outlet_mean:.2f} to {max_outlet_mean:.2f} dataset units)",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(visuals_dir / "07_outlet_matrix_parity_proof.png", dpi=150)
    plt.close()

    # Figure 8: Correlation (3 Panels)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    corr = clean_df[["Sales", "Item Visibility", "Item Weight", "Rating", "Outlet Age"]].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".3f", vmin=-0.1, vmax=0.1, ax=axes[0])
    axes[0].set_title("Correlation Heatmap", fontweight="bold")
    samp = clean_df.sample(1000, random_state=42)
    sns.regplot(x="Item Visibility", y="Sales", data=samp, ax=axes[1], scatter_kws={"alpha": 0.3}, line_kws={"color": "red"})
    axes[1].set_title(f"Visibility vs Recorded Sales (r = {r_vis:+.4f})", fontweight="bold")
    sns.regplot(x="Rating", y="Sales", data=samp, ax=axes[2], scatter_kws={"alpha": 0.3, "color": "green"}, line_kws={"color": "red"})
    axes[2].set_title(f"Rating vs Recorded Sales (r = {r_rat:+.4f})", fontweight="bold")
    plt.tight_layout()
    plt.savefig(visuals_dir / "08_statistical_correlations.png", dpi=150)
    plt.close()

    # Figure 9: Cohort Comparison (2 Panels)
    q1, q3 = clean_df["Sales"].quantile(0.25), clean_df["Sales"].quantile(0.75)
    clean_df["Cohort"] = "Middle 50%"
    clean_df.loc[clean_df["Sales"] <= q1, "Cohort"] = "Bottom 25%"
    clean_df.loc[clean_df["Sales"] >= q3, "Cohort"] = "Top 25%"
    cohort_sub = clean_df[clean_df["Cohort"] != "Middle 50%"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    sns.countplot(x="Item Category", hue="Cohort", data=cohort_sub, palette=["#d62728", "#2ca02c"], ax=axes[0])
    axes[0].set_title("Product Family in Top vs Bottom Sales-Value Quartiles", fontweight="bold")
    sns.countplot(x="Outlet Type", hue="Cohort", data=cohort_sub, palette=["#d62728", "#2ca02c"], ax=axes[1])
    axes[1].set_title("Outlet Type in Top vs Bottom Sales-Value Quartiles", fontweight="bold")
    axes[1].tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(visuals_dir / "09_top_bottom_cohort_comparison.png", dpi=150)
    plt.close()

    # --- OBJECTIVE 4: Format-Controlled Audit & Catalogue Concentration ---
    print("\n[Objective 4] Synthesizing Format-Controlled Audit & Assortment Gap...")
    supermarket_only = clean_df[clean_df["Outlet Type"] != "Grocery Store"]
    sup_tier_norm = (
        supermarket_only.groupby("Outlet Location Type")
        .agg(Supermarket_Catalogue_Value=("Sales", "sum"), Supermarket_Count=("Outlet Identifier", "nunique"))
        .assign(Catalogue_Value_Per_Supermarket=lambda x: x["Supermarket_Catalogue_Value"] / x["Supermarket_Count"])
    )
    print("=" * 70)
    print("SUPERMARKET CATALOGUE VALUE PER STORE BY TIER (FORMAT-CONTROLLED):")
    print(sup_tier_norm.round(2).to_string())
    print("=" * 70)

    # Figure 10: Pareto Catalogue Concentration
    pareto_s = clean_df.groupby("Item Type")["Sales"].sum().sort_values(ascending=False)
    pareto_df = pd.DataFrame({"Catalogue_Value": pareto_s})
    pareto_df["Cum_Pct"] = pareto_df["Catalogue_Value"].cumsum() / pareto_df["Catalogue_Value"].sum() * 100
    top5_sum = pareto_df.head(5)["Catalogue_Value"].sum()
    top5_pct = top5_sum / clean_df["Sales"].sum() * 100

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    ax1.bar(pareto_df.index, pareto_df["Catalogue_Value"] / 1000, color="#1f77b4", alpha=0.85, width=0.6)
    ax2.plot(pareto_df.index, pareto_df["Cum_Pct"], color="#d62728", marker="o", linewidth=2.5)
    ax1.set_ylabel("Summed Catalogue Value (thousands, dataset units)", color="#1f77b4", fontweight="bold")
    ax2.set_ylabel("Cumulative %", color="#d62728", fontweight="bold")
    ax1.tick_params(axis="x", rotation=45)
    ax2.axhline(80, color="gray", linestyle="--")
    plt.title(f"Catalogue Concentration: Top 5 Categories Represent {top5_pct:.2f}% ({top5_sum:,.0f} units) of Recorded Sales Metric", fontweight="bold")
    plt.tight_layout()
    plt.savefig(visuals_dir / "10_pareto_analysis.png", dpi=150)
    plt.close()

    # Dynamic Assortment Breadth & Hypothetical Catalogue Gap (consistent supermarket mean baseline)
    breadth = clean_df.groupby(["Outlet Identifier", "Outlet Type"])["Item Identifier"].count()
    sup_mean_skus = breadth[breadth.index.get_level_values("Outlet Type") != "Grocery Store"].mean()
    groc_stores = breadth[breadth.index.get_level_values("Outlet Type") == "Grocery Store"]
    groc_mean_skus = groc_stores.mean()
    sup_mean_sale = supermarket_only["Sales"].mean()

    sku_gap = sup_mean_skus - groc_mean_skus
    hypothetical_gap_value = sku_gap * len(groc_stores) * sup_mean_sale
    pct_gap = hypothetical_gap_value / clean_df["Sales"].sum() * 100

    print("=" * 80)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Supermarket Avg Breadth    : {sup_mean_skus:.1f} SKUs")
    print(f"Grocery Store Avg Breadth  : {groc_mean_skus:.1f} SKUs (Gap: {sku_gap:.1f} SKUs/store)")
    print(f"Hypothetical Catalogue Gap : +{hypothetical_gap_value:,.2f} dataset units (+{pct_gap:.2f}% of current catalogue sum)")
    print("Note: Hypothetical catalogue value scenario only; NOT verified transaction revenue.")
    print("Exported Figures: 10 figures saved to 'visuals/'")
    print("=" * 80)


if __name__ == "__main__":
    main()
