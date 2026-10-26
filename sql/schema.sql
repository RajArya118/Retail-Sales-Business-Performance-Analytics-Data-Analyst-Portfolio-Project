-- ====================================================================
-- Retail Sales Analytics — Database Schema & DDL
-- Target DBMS: SQLite 3 (Compatible with PostgreSQL / MySQL / DuckDB)
-- ====================================================================

DROP VIEW IF EXISTS v_kpi_summary;
DROP VIEW IF EXISTS v_channel_performance;
DROP VIEW IF EXISTS v_category_performance;
DROP VIEW IF EXISTS v_monthly_sales;
DROP TABLE IF EXISTS retail_sales;

-- 1. Main Transactions Table
CREATE TABLE retail_sales (
    transaction_id       TEXT PRIMARY KEY,
    date                 TEXT NOT NULL,
    customer_id          TEXT NOT NULL,
    customer_gender      TEXT NOT NULL,
    customer_age         INTEGER NOT NULL CHECK(customer_age >= 18 AND customer_age <= 100),
    customer_region      TEXT NOT NULL,
    customer_type        TEXT NOT NULL,
    product_id           TEXT NOT NULL,
    product_category     TEXT NOT NULL,
    product_name         TEXT NOT NULL,
    quantity             INTEGER NOT NULL CHECK(quantity > 0),
    unit_price           REAL NOT NULL CHECK(unit_price > 0.0),
    discount_percent     REAL NOT NULL CHECK(discount_percent >= 0.0 AND discount_percent <= 1.0),
    discount_amount      REAL NOT NULL CHECK(discount_amount >= 0.0),
    tax_amount           REAL NOT NULL CHECK(tax_amount >= 0.0),
    total_amount         REAL NOT NULL CHECK(total_amount > 0.0),
    payment_method       TEXT NOT NULL,
    sales_channel        TEXT NOT NULL,
    store_location       TEXT NOT NULL,
    order_status         TEXT NOT NULL,
    year                 INTEGER,
    month                INTEGER,
    month_name           TEXT,
    year_month           TEXT,
    day                  INTEGER,
    day_name             TEXT,
    day_of_week          INTEGER,
    quarter              TEXT,
    is_weekend           INTEGER,
    gross_amount         REAL,
    net_amount           REAL,
    age_group            TEXT,
    discount_tier_label  TEXT,
    is_outlier           INTEGER
);

-- 2. Performance Indices
CREATE INDEX idx_sales_date ON retail_sales(date);
CREATE INDEX idx_sales_year_month ON retail_sales(year_month);
CREATE INDEX idx_sales_customer ON retail_sales(customer_id);
CREATE INDEX idx_sales_category ON retail_sales(product_category);
CREATE INDEX idx_sales_channel ON retail_sales(sales_channel);
CREATE INDEX idx_sales_status ON retail_sales(order_status);
CREATE INDEX idx_sales_region ON retail_sales(customer_region);

-- 3. Analytical Views
-- View A: Monthly Sales & Order Velocity
CREATE VIEW v_monthly_sales AS
SELECT 
    year_month,
    COUNT(transaction_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(gross_amount), 2) AS gross_revenue,
    ROUND(SUM(discount_amount), 2) AS total_discounts,
    ROUND(SUM(total_amount), 2) AS total_net_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;

-- View B: Product Category Summary
CREATE VIEW v_category_performance AS
SELECT 
    product_category,
    COUNT(transaction_id) AS order_count,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM retail_sales), 2) AS revenue_share_pct
FROM retail_sales
GROUP BY product_category
ORDER BY total_revenue DESC;

-- View C: Sales Channel Performance
CREATE VIEW v_channel_performance AS
SELECT 
    sales_channel,
    COUNT(transaction_id) AS order_count,
    ROUND(COUNT(transaction_id) * 100.0 / (SELECT COUNT(*) FROM retail_sales), 2) AS order_share_pct,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM retail_sales), 2) AS revenue_share_pct
FROM retail_sales
GROUP BY sales_channel
ORDER BY total_revenue DESC;

-- View D: Executive Top-Level KPI Summary
CREATE VIEW v_kpi_summary AS
SELECT 
    COUNT(transaction_id) AS total_transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product_id) AS active_products,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(total_amount), 2) AS total_gross_revenue,
    ROUND(SUM(CASE WHEN order_status = 'Completed' THEN total_amount ELSE 0 END), 2) AS realized_revenue,
    ROUND(SUM(CASE WHEN order_status = 'Returned' THEN total_amount ELSE 0 END), 2) AS return_refund_loss,
    ROUND(SUM(CASE WHEN order_status = 'Cancelled' THEN total_amount ELSE 0 END), 2) AS cancellation_loss,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(SUM(CASE WHEN order_status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fulfillment_rate_pct
FROM retail_sales;
