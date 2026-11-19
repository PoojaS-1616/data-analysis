"""
BlinkIT Grocery Catalogue Architecture & Assortment Explorer
============================================================
Interactive Streamlit Dashboard backed by SQLite Star Schema (blinkit_warehouse.db)

Key Design Principles:
- Script-relative paths (works from any working directory)
- Read-only SQLite connection (mode=ro) + strict single-statement SELECT/WITH SQL guard
- Currency-honest reporting (currency is unspecified in source; displayed in original dataset units)
- Clear separation between verified catalogue metrics and hypothetical user-controlled scenarios
"""

from pathlib import Path
import re
import sqlite3
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="BlinkIT Catalogue Pricing & Assortment Explorer",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; font-weight: 600; }
    .insight-box {
        background-color: #17263c;
        color: #e2ecf7 !important;
        border: 1px solid #2e476e;
        border-left: 5px solid #2986cc;
        padding: 14px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }
    .insight-box b { color: #6bb9f0 !important; }
    .warning-box {
        background-color: #332810;
        color: #fceecb !important;
        border: 1px solid #66501a;
        border-left: 5px solid #ffcc00;
        padding: 14px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }
    .warning-box b { color: #ffd740 !important; }
</style>
""",
    unsafe_allow_html=True,
)


def validate_readonly_sql(query: str) -> tuple[bool, str]:
    """Validate that a user query is a single read-only SELECT or WITH statement."""
    if not query or not query.strip():
        return False, "Query cannot be empty."
    # Strip SQL block comments and single-line comments
    cleaned = re.sub(r"/\*.*?\*/", " ", query, flags=re.S)
    cleaned = re.sub(r"--[^\n]*", " ", cleaned)
    cleaned = cleaned.strip()
    # Allow at most one optional trailing semicolon
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()
    if ";" in cleaned:
        return False, "Multiple SQL statements are not permitted."
    if not re.match(r"^(SELECT|WITH)\b", cleaned, flags=re.I):
        return False, "Only read-only SELECT or WITH queries are permitted."
    forbidden = r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|PRAGMA|VACUUM|REINDEX|BEGIN|COMMIT|ROLLBACK)\b"
    if re.search(forbidden, cleaned, flags=re.I):
        return False, "Modification, DDL, and PRAGMA statements are blocked."
    return True, cleaned


@st.cache_data
def load_data() -> pd.DataFrame:
    csv_path = BASE_DIR / "BlinkIT_Grocery_Data_Cleaned.csv"
    if not csv_path.exists():
        st.error(f"Cleaned dataset not found at '{csv_path}'. Run `python run_analysis.py` first.")
        st.stop()
    df = pd.read_csv(csv_path)
    required = {"Item Identifier", "Item Type", "Outlet Identifier", "Outlet Type", "Outlet Location Type", "Sales", "Rating"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Dataset is missing required columns: {sorted(missing)}")
        st.stop()
    if df.empty:
        st.error("Loaded dataset is empty.")
        st.stop()
    return df


@st.cache_resource
def get_readonly_db_connection() -> sqlite3.Connection:
    db_path = BASE_DIR / "blinkit_warehouse.db"
    if not db_path.exists():
        if str(BASE_DIR) not in sys.path:
            sys.path.insert(0, str(BASE_DIR))
        import build_warehouse
        build_warehouse.build_warehouse(verbose=False)
    # Open strictly read-only via SQLite URI
    db_uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(db_uri, uri=True, check_same_thread=False)


def format_compact(amount: float) -> str:
    if abs(amount) >= 1_000_000:
        return f"{amount / 1_000_000:.2f}M"
    if abs(amount) >= 1_000:
        return f"{amount / 1_000:.1f}k"
    return f"{amount:,.2f}"


df = load_data()
conn = get_readonly_db_connection()

# --- Dynamic Network Metrics (zero hardcoded numbers) ---
total_catalogue_value = float(df["Sales"].sum())
mean_sales_value = float(df["Sales"].mean())
total_skus = int(df["Item Identifier"].nunique())
total_categories = int(df["Item Type"].nunique())
total_stores = int(df["Outlet Identifier"].nunique())

outlet_counts = df.groupby(["Outlet Identifier", "Outlet Type"])["Item Identifier"].count()
sup_mask = outlet_counts.index.get_level_values("Outlet Type") != "Grocery Store"
groc_mask = ~sup_mask
sup_count = int(sup_mask.sum())
groc_count = int(groc_mask.sum())
sup_avg_skus = float(outlet_counts[sup_mask].mean()) if sup_count else 0.0
groc_avg_skus = float(outlet_counts[groc_mask].mean()) if groc_count else 0.0
avg_sku_gap = max(sup_avg_skus - groc_avg_skus, 0.0)
sup_mean_sales = float(df.loc[df["Outlet Type"] != "Grocery Store", "Sales"].mean()) if sup_count else mean_sales_value
network_catalogue_gap = avg_sku_gap * groc_count * sup_mean_sales
network_gap_pct = (network_catalogue_gap / total_catalogue_value * 100.0) if total_catalogue_value > 0 else 0.0
within_sku_sd = float(df.groupby("Item Identifier")["Sales"].std().mean())

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🛒 BlinkIT Catalogue Explorer")
    st.caption("Product-Outlet Assortment & Pricing Architecture")
    st.markdown("---")
    st.subheader("Data Units & Scope")
    st.caption(
        "• **Records:** Product-outlet catalogue listings (no transaction quantities or timestamps).\n"
        "• **Units:** Currency is unspecified in the source; values are shown in original dataset units.\n"
        "• **Source:** Rebranded public retail catalogue dataset (BigMart Sales lineage)."
    )
    st.markdown("---")
    st.info(
        "All KPIs and SQL views are computed dynamically from the cleaned dataset and read-only SQLite Star Schema."
    )

# --- Header ---
st.title("🛒 BlinkIT Catalogue Pricing & Assortment Explorer")
st.markdown(
    f"**Scope:** Diagnostic analysis of {len(df):,} product-outlet records across {total_skus:,} SKUs and {total_stores} outlets. "
    f"Closing the average Grocery Store assortment gap ({avg_sku_gap:.1f} SKUs/store vs Supermarket benchmark) represents a "
    f"hypothetical catalogue-value addition of **+{format_compact(network_catalogue_gap)} units** (+{network_gap_pct:.2f}% of current catalogue sum; not a revenue forecast)."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Sum of Recorded Sales Metric", format_compact(total_catalogue_value), f"+{network_gap_pct:.2f}% hypothetical gap")
col2.metric("Mean Recorded Sales Value", f"{mean_sales_value:,.2f}", f"Avg within-SKU SD: {within_sku_sd:.2f}")
col3.metric("Network SKU Depth", f"{total_skus:,} SKUs", f"{total_categories} Item Categories")
col4.metric("Outlets Analyzed", f"{total_stores} Outlets", f"{sup_count} Supermarkets · {groc_count} Grocery Stores")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Assortment Gap Scenario",
    "🔬 Sales Variance Decomposition",
    "⚖️ Store-Format Audit (Simpson's Paradox)",
    "🎯 Missing-SKU Explorer",
    "🗄️ Read-Only SQL Explorer",
])

# ==============================================================================
# TAB 1: HYPOTHETICAL CATALOGUE ASSORTMENT SCENARIO
# ==============================================================================
with tab1:
    st.header("🏪 Grocery Store Assortment Breadth & Hypothetical Scenario")
    st.markdown(
        f"Grocery stores (`OUT010`, `OUT019`) list an average of **{groc_avg_skus:.1f} SKUs** compared to "
        f"**{sup_avg_skus:.1f} SKUs** in Supermarkets. Because the dataset contains **product-outlet listings without unit quantities, "
        f"timestamps, or COGS**, the calculator below models **catalogue breadth expansion** plus an optional, explicitly hypothetical scenario."
    )

    sim_col1, sim_col2 = st.columns([1, 2])
    grocery_outlets = sorted(df.loc[df["Outlet Type"] == "Grocery Store", "Outlet Identifier"].unique().tolist())

    with sim_col1:
        st.subheader("⚙️ Scenario Inputs (User Assumptions)")
        if not grocery_outlets:
            st.warning("No Grocery Store outlets found in the dataset.")
            st.stop()
        store_labels = {
            oid: f"{oid} ({df.loc[df['Outlet Identifier']==oid, 'Outlet Location Type'].iloc[0]} · Size {df.loc[df['Outlet Identifier']==oid, 'Outlet Size'].iloc[0]})"
            for oid in grocery_outlets
        }
        target_store_id = st.selectbox("Select Target Grocery Store", grocery_outlets, format_func=lambda x: store_labels[x])
        store_data = df[df["Outlet Identifier"] == target_store_id]
        current_skus = int(len(store_data))
        max_missing = max(int(round(sup_avg_skus)) - current_skus, 0)

        skus_to_add = st.slider(
            "Hypothetical Missing SKUs Added",
            min_value=0,
            max_value=max(max_missing, 1),
            value=max_missing,
            help=f"Reaching the Supermarket benchmark ({sup_avg_skus:.1f} SKUs) adds {max_missing} SKUs.",
        )
        st.caption("Optional illustrative unit-velocity assumption (not observed in dataset):")
        assumed_units_per_sku = st.slider("Assumed Annual Units Sold per Added SKU (Hypothetical)", 1, 24, 6, step=1)
        assumed_margin_pct = st.slider("Assumed Gross Margin % (Hypothetical)", 5.0, 35.0, 20.0, step=1.0) / 100.0

    with sim_col2:
        st.subheader("📈 Observed Catalogue vs. Hypothetical Scenario")
        current_val = float(store_data["Sales"].sum())
        incremental_catalogue_val = skus_to_add * sup_mean_sales
        projected_catalogue_val = current_val + incremental_catalogue_val
        expansion_pct = (incremental_catalogue_val / current_val * 100.0) if current_val > 0 else 0.0

        # Explicitly labelled illustrative scenario
        illustrative_gross_sales = incremental_catalogue_val * assumed_units_per_sku
        illustrative_gross_margin = illustrative_gross_sales * assumed_margin_pct

        m1, m2, m3 = st.columns(3)
        m1.metric("Catalogue Value Added (1× Listing)", format_compact(incremental_catalogue_val), f"+{expansion_pct:.1f}% vs current store")
        m2.metric("Hypothetical Gross Sales", format_compact(illustrative_gross_sales), f"Assumed {assumed_units_per_sku} units/SKU/yr")
        m3.metric("Hypothetical Gross Margin", format_compact(illustrative_gross_margin), f"At assumed {assumed_margin_pct*100:.0f}% margin")

        chart_df = pd.DataFrame({
            "Stage": ["Current Catalogue Value (Observed)", "Catalogue Value Added (1× Listing)", "Projected Catalogue Value (Scenario)"],
            "Value": [current_val, incremental_catalogue_val, projected_catalogue_val],
        })
        fig = px.bar(
            chart_df,
            x="Stage",
            y="Value",
            text_auto=".3s",
            color="Stage",
            color_discrete_sequence=["#6c757d", "#28a745", "#007bff"],
            title=f"Catalogue Value Comparison for {target_store_id} (Dataset Units)",
            labels={"Value": "Recorded Sales Metric (Dataset Units)"},
        )
        fig.update_layout(showlegend=False, height=320, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, width="stretch")

    st.markdown(
        f"""
    <div class="warning-box">
        <b>⚠️ Methodology & Limitations (Illustrative Scenario Only):</b><br>
        • <b>Observed baseline:</b> <b>{target_store_id}</b> currently lists <b>{current_skus:,} SKUs</b> (summed Recorded Sales value = <b>{current_val:,.2f}</b>).<br>
        • <b>Catalogue addition formula:</b> <code>{skus_to_add} SKUs × {sup_mean_sales:.2f} (Supermarket mean Recorded Sales value) = {incremental_catalogue_val:,.2f}</code>.<br>
        • <b>Why this is NOT a financial forecast:</b> The source dataset contains no transaction quantities, customer demand, COGS, or holding-cost data.
        The hypothetical gross sales (<b>{illustrative_gross_sales:,.2f}</b>) and gross margin (<b>{illustrative_gross_margin:,.2f}</b>) figures above depend entirely on your slider assumptions
        and do not represent guaranteed revenue, working capital, or operating profit.
    </div>
    """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# TAB 2: SALES VARIANCE DECOMPOSITION
# ==============================================================================
with tab2:
    st.header("🔬 Variance Decomposition: What Does the Recorded Sales Field Represent?")

    grand_mean = df["Sales"].mean()
    ss_total = ((df["Sales"] - grand_mean) ** 2).sum()
    r2_sku = ((df.groupby("Item Identifier")["Sales"].transform("mean") - grand_mean) ** 2).sum() / ss_total if ss_total else 0.0
    r2_cat = ((df.groupby("Item Type")["Sales"].transform("mean") - grand_mean) ** 2).sum() / ss_total if ss_total else 0.0
    r2_outlet = ((df.groupby("Outlet Identifier")["Sales"].transform("mean") - grand_mean) ** 2).sum() / ss_total if ss_total else 0.0

    st.markdown(
        f"`Sales` behaves like a SKU-level unit price rather than store-level demand volume: "
        f"**{r2_sku * 100:.2f}% of its variance is explained by `Item Identifier` alone** ($R^2 = {r2_sku:.4f}$). "
        f"Currency is not specified in the source dataset, so values are displayed in original dataset units."
    )

    v_col1, v_col2 = st.columns(2)
    with v_col1:
        decomp_df = pd.DataFrame({
            "Factor": ["Item Identifier (SKU)", "Category (Item Type)", "Outlet Identifier (Store)"],
            "Variance Explained (%)": [r2_sku * 100, r2_cat * 100, r2_outlet * 100],
        })
        fig_decomp = px.bar(
            decomp_df,
            x="Factor",
            y="Variance Explained (%)",
            text=decomp_df["Variance Explained (%)"].apply(lambda x: f"{x:.2f}%"),
            color="Factor",
            color_discrete_sequence=["#0066cc", "#6c757d", "#dc3545"],
            title="Proportion of Recorded Sales Variance Explained (R²)",
        )
        fig_decomp.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_decomp, width="stretch")

    with v_col2:
        sample_skus = df["Item Identifier"].value_counts().head(10).index.tolist()
        selected_sku = st.selectbox("Inspect SKU Recorded Sales Value across Outlets", sample_skus)
        sku_records = df[df["Item Identifier"] == selected_sku][["Outlet Identifier", "Outlet Type", "Sales"]].copy()
        fig_sku = px.scatter(
            sku_records,
            x="Outlet Identifier",
            y="Sales",
            color="Outlet Type",
            size=[14] * len(sku_records),
            title=f"Recorded Sales Value by Outlet for SKU: {selected_sku}",
            labels={"Sales": "Recorded Sales Value (Dataset Units)"},
        )
        fig_sku.update_layout(height=350)
        st.plotly_chart(fig_sku, width="stretch")

    st.markdown(
        f"""
    <div class="insight-box">
        <b>Key Takeaway:</b> The average within-SKU standard deviation is only <b>{within_sku_sd:.2f}</b> vs <b>{df['Sales'].std():.2f}</b> overall.
        Store-level sums of `Sales` therefore track <b>catalogue breadth (number of SKUs listed)</b> rather than realized unit volume.
    </div>
    """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# TAB 3: STORE-FORMAT COMPOSITION AUDIT (SIMPSON'S PARADOX)
# ==============================================================================
with tab3:
    st.header("⚖️ Store-Format Composition Audit (Simpson's Paradox)")
    st.markdown(
        "A naive tier-level average suggests Tier 2 outlets have higher per-store catalogue values than Tier 1 and Tier 3. "
        "Controlling for store format shows this is an artifact of **outlet composition**."
    )

    simpson_mode = st.radio("Analytical View", ["Naive Aggregated View (Confounded)", "Format-Controlled View (Supermarkets Only)"], horizontal=True)

    if simpson_mode == "Naive Aggregated View (Confounded)":
        naive_df = df.groupby("Outlet Location Type").agg(Catalogue_Sum=("Sales", "sum"), Stores=("Outlet Identifier", "nunique")).reset_index()
        naive_df["Catalogue_Value_Per_Store"] = naive_df["Catalogue_Sum"] / naive_df["Stores"]
        fig_naive = px.bar(
            naive_df,
            x="Outlet Location Type",
            y="Catalogue_Value_Per_Store",
            text=naive_df["Catalogue_Value_Per_Store"].apply(lambda x: f"{x:,.0f}"),
            color="Outlet Location Type",
            color_discrete_sequence=["#dc3545", "#28a745", "#ffc107"],
            title="Naive Average Catalogue Value per Store by Tier (Confounded)",
            labels={"Catalogue_Value_Per_Store": "Catalogue Value per Store (Dataset Units)"},
        )
        fig_naive.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_naive, width="stretch")
        st.warning("⚠️ Confounded view: Tier 2 appears higher only because it contains zero Grocery Stores.")
    else:
        ctrl_df = (
            df[df["Outlet Type"] != "Grocery Store"]
            .groupby("Outlet Location Type")
            .agg(Catalogue_Sum=("Sales", "sum"), Stores=("Outlet Identifier", "nunique"))
            .reset_index()
        )
        ctrl_df["Catalogue_Value_Per_Supermarket"] = ctrl_df["Catalogue_Sum"] / ctrl_df["Stores"]
        fig_ctrl = px.bar(
            ctrl_df,
            x="Outlet Location Type",
            y="Catalogue_Value_Per_Supermarket",
            text=ctrl_df["Catalogue_Value_Per_Supermarket"].apply(lambda x: f"{x:,.0f}"),
            color="Outlet Location Type",
            color_discrete_sequence=["#007bff", "#007bff", "#007bff"],
            title="Supermarkets-Only Catalogue Value per Store (Format-Controlled)",
            labels={"Catalogue_Value_Per_Supermarket": "Catalogue Value per Supermarket (Dataset Units)"},
        )
        fig_ctrl.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_ctrl, width="stretch")
        vals = ctrl_df["Catalogue_Value_Per_Supermarket"]
        spread_pct = ((vals.max() - vals.min()) / vals.mean() * 100.0) if vals.mean() > 0 else 0.0
        st.success(
            f"✅ Format-controlled view: average Supermarket catalogue value ranges from {vals.min():,.0f} to {vals.max():,.0f} "
            f"across tiers (spread = {spread_pct:.2f}% of mean). Descriptive comparison only; not a significance test."
        )

# ==============================================================================
# TAB 4: MISSING-SKU EXPLORER
# ==============================================================================
with tab4:
    st.header("🎯 Grocery Store Missing-SKU Candidate Explorer")
    st.markdown(
        "SKUs stocked in 1 to 8 Supermarkets that are absent from both Grocery Stores (`OUT010`, `OUT019`). "
        "Priority score (`supermarket_presence × mean_sales_value`) is an illustrative catalogue-screening heuristic, not a demand ranking."
    )

    missing_df = pd.read_sql_query("SELECT * FROM vw_missing_sku_prioritization", conn)
    rec_col1, rec_col2 = st.columns([1, 2])
    with rec_col1:
        all_families = sorted(missing_df["product_family"].unique().tolist())
        all_cats = sorted(missing_df["item_type"].unique().tolist())
        default_cats = [c for c in ["Fruits and Vegetables", "Snack Foods", "Frozen Foods"] if c in all_cats] or all_cats[:3]
        sel_family = st.multiselect("Filter Product Family", all_families, default=all_families)
        sel_cat = st.multiselect("Filter Category", all_cats, default=default_cats)
        min_pres = st.slider("Minimum Supermarket Presence (Stores)", 1, 8, 7)

    filtered_missing = missing_df[
        (missing_df["product_family"].isin(sel_family))
        & (missing_df["item_type"].isin(sel_cat))
        & (missing_df["supermarket_presence"] >= min_pres)
    ]

    with rec_col2:
        if filtered_missing.empty:
            st.info("No candidate SKUs match the current filter selection. Broaden your filters to inspect candidates.")
        else:
            fig_scatter = px.scatter(
                filtered_missing,
                x="mean_sales_value",
                y="expansion_priority_score",
                color="item_type",
                size="supermarket_presence",
                hover_data=["item_identifier", "avg_rating"],
                title="Heuristic Priority Score vs. Mean Recorded Sales Value",
                labels={"mean_sales_value": "Mean Recorded Sales Value (Dataset Units)", "expansion_priority_score": "Heuristic Priority Score"},
            )
            fig_scatter.update_layout(height=380)
            st.plotly_chart(fig_scatter, width="stretch")

    st.subheader(f"Candidate SKU Queue ({len(filtered_missing)} SKUs)")
    st.dataframe(
        filtered_missing.style.format({"mean_sales_value": "{:,.2f}", "expansion_priority_score": "{:,.2f}", "avg_rating": "{:.2f}"}),
        width="stretch",
    )
    st.download_button(
        label="📥 Export Candidate SKUs to CSV",
        data=filtered_missing.to_csv(index=False).encode("utf-8"),
        file_name="blinkit_missing_sku_candidates.csv",
        mime="text/csv",
    )

# ==============================================================================
# TAB 5: READ-ONLY SQL STAR SCHEMA EXPLORER
# ==============================================================================
with tab5:
    st.header("🗄️ Read-Only SQL Star Schema Explorer")
    st.markdown(
        "Connected strictly in **read-only mode** (`mode=ro`) to `blinkit_warehouse.db`. "
        "Inspect pre-built analytical views or run validated single-statement `SELECT`/`WITH` queries."
    )

    ALLOWED_VIEWS = [
        "vw_outlet_assortment_gap",
        "vw_format_controlled_tiers",
        "vw_category_pareto",
        "vw_missing_sku_prioritization",
        "vw_sku_pricing_variance",
    ]
    view_choice = st.selectbox("Select Analytical Warehouse View", ALLOWED_VIEWS)
    limit_rows = st.slider("Row Limit", 5, 50, 15)
    # View name validated against fixed allowlist; limit passed as SQL parameter
    view_data = pd.read_sql_query(f"SELECT * FROM {view_choice} LIMIT ?", conn, params=(int(limit_rows),))
    st.dataframe(view_data, width="stretch")

    st.subheader("Read-Only Custom SQL Query")
    custom_sql = st.text_area(
        "Enter a single SELECT or WITH query against `fact_inventory_pricing`, `dim_products`, `dim_outlets`:",
        value="SELECT p.item_type, COUNT(f.fact_key) AS listings, ROUND(AVG(f.sales_mrp), 2) AS mean_sales_value FROM fact_inventory_pricing f JOIN dim_products p ON f.product_key = p.product_key GROUP BY p.item_type ORDER BY mean_sales_value DESC LIMIT 5;",
    )
    if st.button("Execute Read-Only Query"):
        ok, result = validate_readonly_sql(custom_sql)
        if not ok:
            st.error(f"Query rejected: {result}")
        else:
            try:
                sql_res = pd.read_sql_query(result, conn)
                st.dataframe(sql_res, width="stretch")
                st.success(f"Query returned {len(sql_res)} rows.")
            except Exception as exc:
                st.error(f"SQL Error: {exc}")

st.markdown("---")
st.caption("BlinkIT Grocery Catalogue Analysis · Portfolio Project · Currency unspecified (original dataset units)")
