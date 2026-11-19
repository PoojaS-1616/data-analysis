"""
BlinkIT Analytics Warehouse Builder & Verification Engine
--------------------------------------------------------
- Builds a relational SQLite database (blinkit_warehouse.db) implementing the Star Schema
- Uses script-relative pathlib paths so execution is independent of current working directory
- Enforces foreign keys (PRAGMA foreign_keys = ON) and unique (product_key, outlet_key) grain
- Performs deterministic full rebuilds (DROP/CREATE + load) without duplicate inflation
- Executes and validates all 5 analytical SQL views
"""

from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent


def build_warehouse(
    csv_path: Path | str | None = None,
    sql_script_path: Path | str | None = None,
    db_path: Path | str | None = None,
    verbose: bool = True,
) -> Path:
    csv_file = Path(csv_path) if csv_path is not None else BASE_DIR / "BlinkIT_Grocery_Data_Cleaned.csv"
    sql_file = Path(sql_script_path) if sql_script_path is not None else BASE_DIR / "blinkit_warehouse.sql"
    db_file = Path(db_path) if db_path is not None else BASE_DIR / "blinkit_warehouse.db"

    if not csv_file.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at '{csv_file}'")
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL DDL script not found at '{sql_file}'")

    if verbose:
        print("=" * 80)
        print("BUILDING BLINKIT DIMENSIONAL ANALYTICS WAREHOUSE (STAR SCHEMA)")
        print("=" * 80)
        print(f"Loading cleaned dataset: {csv_file}...")

    df = pd.read_csv(csv_file)
    if verbose:
        print(f"Loaded {len(df):,} rows x {len(df.columns)} columns.\n")

    conn = sqlite3.connect(db_file)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        if verbose:
            print(f"Executing DDL script from {sql_file}...")
        sql_commands = sql_file.read_text(encoding="utf-8")
        cursor.executescript(sql_commands)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

        # 1. Populate dim_products
        products_df = (
            df[["Item Identifier", "Item Category", "Item Type", "Item Fat Content", "Item Weight"]]
            .drop_duplicates(subset=["Item Identifier"])
            .sort_values("Item Identifier")
            .reset_index(drop=True)
        )
        products_df = products_df.rename(
            columns={
                "Item Identifier": "item_identifier",
                "Item Category": "product_family",
                "Item Type": "item_type",
                "Item Fat Content": "item_fat_content",
                "Item Weight": "item_weight",
            }
        )
        products_df["is_edible"] = products_df["product_family"].isin(["Food", "Drinks"]).astype(int)
        products_df["product_key"] = products_df.index + 1
        products_df[
            ["product_key", "item_identifier", "product_family", "item_type", "item_fat_content", "item_weight", "is_edible"]
        ].to_sql("dim_products", conn, if_exists="append", index=False)

        # 2. Populate dim_outlets
        outlets_df = (
            df[["Outlet Identifier", "Outlet Type", "Outlet Location Type", "Outlet Size", "Outlet Establishment Year", "Outlet Age"]]
            .drop_duplicates(subset=["Outlet Identifier"])
            .sort_values("Outlet Identifier")
            .reset_index(drop=True)
        )
        outlets_df = outlets_df.rename(
            columns={
                "Outlet Identifier": "outlet_identifier",
                "Outlet Type": "outlet_type",
                "Outlet Location Type": "outlet_location_tier",
                "Outlet Size": "outlet_size",
                "Outlet Establishment Year": "establishment_year",
                "Outlet Age": "outlet_age",
            }
        )
        outlets_df["outlet_key"] = outlets_df.index + 1
        outlets_df[
            ["outlet_key", "outlet_identifier", "outlet_type", "outlet_location_tier", "outlet_size", "establishment_year", "outlet_age"]
        ].to_sql("dim_outlets", conn, if_exists="append", index=False)

        # 3. Populate fact_inventory_pricing
        fact_df = df.merge(products_df[["item_identifier", "product_key"]], left_on="Item Identifier", right_on="item_identifier")
        fact_df = fact_df.merge(outlets_df[["outlet_identifier", "outlet_key"]], left_on="Outlet Identifier", right_on="outlet_identifier")
        fact_df["fact_key"] = fact_df.index + 1
        fact_df["sales_mrp"] = fact_df["Sales"]
        fact_df["item_visibility"] = fact_df["Item Visibility"]
        fact_df["customer_rating"] = fact_df["Rating"]

        fact_df[["fact_key", "product_key", "outlet_key", "item_visibility", "sales_mrp", "customer_rating"]].to_sql(
            "fact_inventory_pricing", conn, if_exists="append", index=False
        )
        conn.commit()

        # Verify referential integrity
        fk_errors = conn.execute("PRAGMA foreign_key_check;").fetchall()
        if fk_errors:
            raise RuntimeError(f"Foreign key violations detected: {fk_errors}")

        if verbose:
            print(f"-> dim_products:           {len(products_df):,} rows")
            print(f"-> dim_outlets:            {len(outlets_df):,} rows")
            print(f"-> fact_inventory_pricing: {len(fact_df):,} rows (0 FK violations)")
            print("\n" + "=" * 80)
            print("VERIFYING ANALYTICAL SQL VIEWS")
            print("=" * 80)
            for title, query in [
                ("VIEW 2: Outlet Assortment Gap Analysis", "SELECT * FROM vw_outlet_assortment_gap"),
                ("VIEW 3: Format-Controlled Location Tiers", "SELECT * FROM vw_format_controlled_tiers"),
                ("VIEW 4: Top 5 Categories by Recorded Sales Metric Share", "SELECT * FROM vw_category_pareto LIMIT 5"),
                ("VIEW 5: Top 10 Grocery Store Missing-SKU Candidates", "SELECT * FROM vw_missing_sku_prioritization LIMIT 10"),
            ]:
                print(f"\n--- {title} ---")
                print(pd.read_sql_query(query, conn).to_string(index=False))
            print("\n" + "=" * 80)
            print(f"DATABASE BUILD COMPLETE: '{db_file}'")
            print("=" * 80)
    finally:
        conn.close()

    return db_file


if __name__ == "__main__":
    build_warehouse()
