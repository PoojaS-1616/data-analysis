-- ==============================================================================
-- BLINKIT QUICK-COMMERCE ANALYTICS WAREHOUSE: DIMENSIONAL STAR SCHEMA & DDL
-- ==============================================================================
-- Architecture: Star Schema (1 Central Fact Table, 2 Core Dimension Tables)
-- Granularity:  One record per unique (product_key, outlet_key) stocked listing
-- Currency:     Unspecified in source dataset; values stored in original units
-- Standard:     ANSI SQL / Compatible with SQLite, PostgreSQL, DuckDB
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- Drop existing views/tables for deterministic full rebuilds
DROP VIEW IF EXISTS vw_missing_sku_prioritization;
DROP VIEW IF EXISTS vw_category_pareto;
DROP VIEW IF EXISTS vw_format_controlled_tiers;
DROP VIEW IF EXISTS vw_outlet_assortment_gap;
DROP VIEW IF EXISTS vw_sku_pricing_variance;
DROP TABLE IF EXISTS fact_inventory_pricing;
DROP TABLE IF EXISTS dim_outlets;
DROP TABLE IF EXISTS dim_products;

-- ------------------------------------------------------------------------------
-- 1. DIMENSION: Products (dim_products)
-- ------------------------------------------------------------------------------
CREATE TABLE dim_products (
    product_key INTEGER PRIMARY KEY,
    item_identifier VARCHAR(16) NOT NULL UNIQUE,
    product_family VARCHAR(20) NOT NULL,            -- Food, Drinks, Non-Consumable
    item_type VARCHAR(50) NOT NULL,                 -- 16 distinct categories
    item_fat_content VARCHAR(20) NOT NULL,          -- Low Fat, Regular, Non-Edible
    item_weight NUMERIC(8, 3) NOT NULL,             -- Imputed cross-outlet mean weight
    is_edible BOOLEAN NOT NULL                      -- 1 for Food/Drinks, 0 for Non-Consumable
);

CREATE INDEX idx_products_item_id ON dim_products (item_identifier);
CREATE INDEX idx_products_category ON dim_products (item_type);
CREATE INDEX idx_products_family ON dim_products (product_family);

-- ------------------------------------------------------------------------------
-- 2. DIMENSION: Outlets (dim_outlets)
-- ------------------------------------------------------------------------------
CREATE TABLE dim_outlets (
    outlet_key INTEGER PRIMARY KEY,
    outlet_identifier VARCHAR(16) NOT NULL UNIQUE,  -- OUT010 to OUT049
    outlet_type VARCHAR(30) NOT NULL,               -- Grocery Store, Supermarket Type1/2/3
    outlet_location_tier VARCHAR(20) NOT NULL,      -- Tier 1, Tier 2, Tier 3
    outlet_size VARCHAR(20) NOT NULL,               -- Small, Medium, High, Unknown
    establishment_year INTEGER NOT NULL,
    outlet_age INTEGER NOT NULL                     -- Reference year (2026) - establishment_year
);

CREATE INDEX idx_outlets_outlet_id ON dim_outlets (outlet_identifier);
CREATE INDEX idx_outlets_type ON dim_outlets (outlet_type);
CREATE INDEX idx_outlets_tier ON dim_outlets (outlet_location_tier);

-- ------------------------------------------------------------------------------
-- 3. FACT: Inventory & Catalogue Listing Values (fact_inventory_pricing)
-- Grain: One row per unique (product_key, outlet_key) pair
-- ------------------------------------------------------------------------------
CREATE TABLE fact_inventory_pricing (
    fact_key INTEGER PRIMARY KEY,
    product_key INTEGER NOT NULL,
    outlet_key INTEGER NOT NULL,
    item_visibility NUMERIC(8, 6) NOT NULL,         -- Imputed display ratio
    sales_mrp NUMERIC(10, 2) NOT NULL,              -- Recorded Sales metric (31.29 to 266.89; currency unspecified; behaves like unit price)
    customer_rating NUMERIC(4, 2) NOT NULL,         -- Recorded rating (1.0 to 5.0)
    CONSTRAINT uq_fact_product_outlet UNIQUE (product_key, outlet_key),
    CONSTRAINT fk_fact_product FOREIGN KEY (product_key) REFERENCES dim_products (product_key),
    CONSTRAINT fk_fact_outlet FOREIGN KEY (outlet_key) REFERENCES dim_outlets (outlet_key)
);

CREATE INDEX idx_fact_product_key ON fact_inventory_pricing (product_key);
CREATE INDEX idx_fact_outlet_key ON fact_inventory_pricing (outlet_key);

-- ==============================================================================
-- 4. ANALYTICAL SQL VIEWS & CORE BUSINESS QUERIES
-- ==============================================================================

-- VIEW 1: SKU-Level Recorded Sales Value Dispersion
-- Demonstrates that SKU explains 99.97% of variance with narrow cross-store spread
CREATE VIEW vw_sku_pricing_variance AS
SELECT 
    p.item_identifier,
    p.item_type,
    p.product_family,
    COUNT(f.outlet_key) AS outlets_stocked_count,
    ROUND(AVG(f.sales_mrp), 2) AS mean_sales_value,
    ROUND(MIN(f.sales_mrp), 2) AS min_sales_value,
    ROUND(MAX(f.sales_mrp), 2) AS max_sales_value,
    ROUND(MAX(f.sales_mrp) - MIN(f.sales_mrp), 2) AS value_spread
FROM fact_inventory_pricing f
JOIN dim_products p ON f.product_key = p.product_key
GROUP BY p.item_identifier, p.item_type, p.product_family;

-- VIEW 2: Outlet Assortment Breadth & Catalogue Value Gap Model
-- Quantifies the assortment breadth gap (541.5 SKUs vs 930.0 SKUs in Supermarkets)
CREATE VIEW vw_outlet_assortment_gap AS
WITH outlet_stats AS (
    SELECT 
        o.outlet_identifier,
        o.outlet_type,
        o.outlet_location_tier,
        o.outlet_size,
        COUNT(f.product_key) AS skus_stocked,
        SUM(f.sales_mrp) AS total_catalogue_value,
        AVG(f.sales_mrp) AS mean_sales_value
    FROM fact_inventory_pricing f
    JOIN dim_outlets o ON f.outlet_key = o.outlet_key
    GROUP BY o.outlet_identifier, o.outlet_type, o.outlet_location_tier, o.outlet_size
),
benchmarks AS (
    SELECT 
        ROUND(AVG(CASE WHEN outlet_type != 'Grocery Store' THEN skus_stocked END), 1) AS benchmark_supermarket_skus,
        ROUND(AVG(CASE WHEN outlet_type != 'Grocery Store' THEN total_catalogue_value END), 2) AS benchmark_supermarket_value
    FROM outlet_stats
)
SELECT 
    os.outlet_identifier,
    os.outlet_type,
    os.outlet_location_tier,
    os.outlet_size,
    os.skus_stocked,
    ROUND(os.total_catalogue_value, 2) AS total_catalogue_value,
    ROUND(os.mean_sales_value, 2) AS mean_sales_value,
    ROUND(b.benchmark_supermarket_skus - os.skus_stocked, 1) AS sku_assortment_gap,
    ROUND(b.benchmark_supermarket_value - os.total_catalogue_value, 2) AS catalogue_value_gap
FROM outlet_stats os
CROSS JOIN benchmarks b
ORDER BY os.total_catalogue_value DESC;

-- VIEW 3: Store-Format Composition Audit (Simpson's Paradox / Tier 2 Check)
-- Shows that Tier 2 higher per-store totals reflect having zero Grocery Stores
CREATE VIEW vw_format_controlled_tiers AS
SELECT 
    o.outlet_location_tier,
    o.outlet_type,
    COUNT(DISTINCT o.outlet_identifier) AS store_count,
    COUNT(f.product_key) AS total_listings,
    ROUND(SUM(f.sales_mrp), 2) AS total_catalogue_value,
    ROUND(AVG(f.sales_mrp), 2) AS mean_sales_value,
    ROUND(SUM(f.sales_mrp) / COUNT(DISTINCT o.outlet_identifier), 2) AS catalogue_value_per_store
FROM fact_inventory_pricing f
JOIN dim_outlets o ON f.outlet_key = o.outlet_key
GROUP BY o.outlet_location_tier, o.outlet_type
ORDER BY o.outlet_location_tier, o.outlet_type;

-- VIEW 4: Category Catalogue Concentration & Running Totals (Pareto)
-- Evaluates cumulative concentration of the recorded Sales metric across categories
CREATE VIEW vw_category_pareto AS
WITH category_metrics AS (
    SELECT 
        p.item_type AS category_name,
        CASE
            WHEN COUNT(DISTINCT p.product_family) = 1 THEN MIN(p.product_family)
            ELSE 'Mixed'
        END AS product_family,
        COUNT(f.fact_key) AS listing_count,
        SUM(f.sales_mrp) AS category_sales_metric,
        AVG(f.sales_mrp) AS mean_sales_value
    FROM fact_inventory_pricing f
    JOIN dim_products p ON f.product_key = p.product_key
    GROUP BY p.item_type
),
ranked_categories AS (
    SELECT 
        category_name,
        product_family,
        listing_count,
        ROUND(category_sales_metric, 2) AS category_sales_metric,
        ROUND(mean_sales_value, 2) AS mean_sales_value,
        ROUND(category_sales_metric * 100.0 / SUM(category_sales_metric) OVER (), 2) AS sales_metric_share_pct,
        ROUND(listing_count * 100.0 / SUM(listing_count) OVER (), 2) AS listing_share_pct,
        SUM(category_sales_metric) OVER (ORDER BY category_sales_metric DESC) AS cumulative_sales_metric,
        SUM(category_sales_metric) OVER () AS total_network_sales_metric
    FROM category_metrics
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY category_sales_metric DESC) AS pareto_rank,
    category_name,
    product_family,
    listing_count,
    listing_share_pct,
    category_sales_metric,
    sales_metric_share_pct,
    ROUND(cumulative_sales_metric * 100.0 / total_network_sales_metric, 2) AS cumulative_sales_metric_pct
FROM ranked_categories
ORDER BY category_sales_metric DESC;

-- VIEW 5: Grocery Store Missing-SKU Candidate List
-- Lists all SKUs stocked in 1 to 8 Supermarkets but omitted from Grocery Stores (OUT010 & OUT019)
-- Ranked by supermarket_presence (stores carrying the SKU) and mean_sales_value (illustrative heuristic)
CREATE VIEW vw_missing_sku_prioritization AS
WITH grocery_skus AS (
    SELECT DISTINCT p.item_identifier
    FROM fact_inventory_pricing f
    JOIN dim_products p ON f.product_key = p.product_key
    JOIN dim_outlets o ON f.outlet_key = o.outlet_key
    WHERE o.outlet_type = 'Grocery Store'
),
supermarket_stocking AS (
    SELECT 
        p.item_identifier,
        p.item_type,
        p.product_family,
        p.item_fat_content,
        COUNT(DISTINCT o.outlet_identifier) AS supermarket_presence,
        ROUND(AVG(f.sales_mrp), 2) AS mean_sales_value,
        ROUND(AVG(f.customer_rating), 2) AS avg_rating
    FROM fact_inventory_pricing f
    JOIN dim_products p ON f.product_key = p.product_key
    JOIN dim_outlets o ON f.outlet_key = o.outlet_key
    WHERE o.outlet_type != 'Grocery Store'
      AND p.item_identifier NOT IN (SELECT item_identifier FROM grocery_skus)
    GROUP BY p.item_identifier, p.item_type, p.product_family, p.item_fat_content
)
SELECT 
    item_identifier,
    item_type,
    product_family,
    item_fat_content,
    supermarket_presence,
    mean_sales_value,
    avg_rating,
    ROUND(supermarket_presence * mean_sales_value, 2) AS expansion_priority_score
FROM supermarket_stocking
ORDER BY supermarket_presence DESC, mean_sales_value DESC;
