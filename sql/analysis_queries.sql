-- ====================================================================
-- Retail Sales Analytics — Core Business Analysis Queries
-- Suite of 12 production-grade SQL queries for executive reporting
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Executive KPI Overview
-- Business Question: What are our macro-level financial and operational metrics?
-- --------------------------------------------------------------------
SELECT 
    COUNT(transaction_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_unique_customers,
    COUNT(DISTINCT product_id) AS total_active_skus,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(gross_amount), 2) AS total_gross_merchandise_value,
    ROUND(SUM(discount_amount), 2) AS total_discounts_granted,
    ROUND(SUM(tax_amount), 2) AS total_sales_tax_collected,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM retail_sales;


-- --------------------------------------------------------------------
-- QUERY 2: Fulfillment & Revenue Leakage Analysis
-- Business Question: How much revenue is realized vs. lost to returns and cancellations?
-- --------------------------------------------------------------------
SELECT 
    order_status,
    COUNT(transaction_id) AS order_count,
    ROUND(COUNT(transaction_id) * 100.0 / (SELECT COUNT(*) FROM retail_sales), 2) AS order_percentage,
    ROUND(SUM(total_amount), 2) AS monetary_value,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM retail_sales), 2) AS revenue_percentage
FROM retail_sales
GROUP BY order_status
ORDER BY monetary_value DESC;


-- --------------------------------------------------------------------
-- QUERY 3: Monthly Trend & Month-over-Month (MoM) Growth
-- Business Question: What is our monthly revenue trajectory and MoM growth rate?
-- Uses Window Function LAG() for chronological growth tracking.
-- --------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT 
        year_month,
        COUNT(transaction_id) AS total_orders,
        SUM(quantity) AS units_sold,
        ROUND(SUM(total_amount), 2) AS monthly_revenue,
        ROUND(AVG(total_amount), 2) AS aov
    FROM retail_sales
    GROUP BY year_month
)
SELECT 
    year_month,
    total_orders,
    units_sold,
    monthly_revenue,
    aov,
    LAG(monthly_revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY year_month)) * 100.0 / 
        LAG(monthly_revenue, 1) OVER (ORDER BY year_month), 
        2
    ) AS mom_growth_pct
FROM monthly_metrics
ORDER BY year_month;


-- --------------------------------------------------------------------
-- QUERY 4: Product Category Performance & Share
-- Business Question: Which merchandise departments generate the highest volume and margin?
-- --------------------------------------------------------------------
SELECT 
    product_category,
    COUNT(transaction_id) AS order_count,
    SUM(quantity) AS units_sold,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM retail_sales), 2) AS revenue_share_pct
FROM retail_sales
GROUP BY product_category
ORDER BY total_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 5: Top 10 Best-Selling Products by Revenue
-- Business Question: What are our flagship merchandise items?
-- --------------------------------------------------------------------
SELECT 
    product_id,
    product_name,
    product_category,
    COUNT(transaction_id) AS times_purchased,
    SUM(quantity) AS total_quantity_sold,
    ROUND(AVG(unit_price), 2) AS unit_price,
    ROUND(SUM(total_amount), 2) AS total_generated_revenue
FROM retail_sales
GROUP BY product_id, product_name, product_category
ORDER BY total_generated_revenue DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 6: Multi-Channel Sales Performance
-- Business Question: How do Online, In-Store, and Mobile App compare in revenue and basket size?
-- --------------------------------------------------------------------
SELECT 
    sales_channel,
    COUNT(transaction_id) AS total_orders,
    ROUND(COUNT(transaction_id) * 100.0 / (SELECT COUNT(*) FROM retail_sales), 2) AS volume_share_pct,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM retail_sales), 2) AS revenue_share_pct,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(AVG(quantity), 2) AS avg_units_per_order
FROM retail_sales
GROUP BY sales_channel
ORDER BY total_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 7: Regional and Store Location Performance
-- Business Question: Which geographic territories and store branches are outperforming?
-- --------------------------------------------------------------------
SELECT 
    customer_region,
    store_location,
    COUNT(transaction_id) AS order_count,
    SUM(quantity) AS units_sold,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM retail_sales
GROUP BY customer_region, store_location
ORDER BY customer_region, total_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 8: Customer Loyalty Tier Analysis
-- Business Question: How does customer loyalty tier impact basket size and promotional discount?
-- --------------------------------------------------------------------
SELECT 
    customer_type,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(transaction_id) AS total_orders,
    ROUND(COUNT(transaction_id) * 1.0 / COUNT(DISTINCT customer_id), 2) AS avg_orders_per_customer,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value,
    ROUND(AVG(discount_percent) * 100.0, 2) AS avg_discount_rate_pct
FROM retail_sales
GROUP BY customer_type
ORDER BY total_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 9: Demographic Age Cohort Spending Dynamics
-- Business Question: Which generation represents our core revenue driver?
-- --------------------------------------------------------------------
SELECT 
    age_group,
    COUNT(transaction_id) AS order_count,
    ROUND(COUNT(transaction_id) * 100.0 / (SELECT COUNT(*) FROM retail_sales), 2) AS order_share_pct,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM retail_sales), 2) AS revenue_share_pct,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM retail_sales
GROUP BY age_group
ORDER BY total_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 10: Payment Tender Breakdown & Digital Adoption
-- Business Question: What payment methods do shoppers prefer?
-- --------------------------------------------------------------------
SELECT 
    payment_method,
    COUNT(transaction_id) AS transaction_count,
    ROUND(COUNT(transaction_id) * 100.0 / (SELECT COUNT(*) FROM retail_sales), 2) AS transaction_share_pct,
    ROUND(SUM(total_amount), 2) AS total_volume_settled,
    ROUND(AVG(total_amount), 2) AS average_ticket_size
FROM retail_sales
GROUP BY payment_method
ORDER BY transaction_count DESC;


-- --------------------------------------------------------------------
-- QUERY 11: Top 10 High-Value Repeat Customers (CLV Ranking)
-- Business Question: Who are our top individual shoppers by lifetime spend?
-- --------------------------------------------------------------------
SELECT 
    customer_id,
    customer_gender,
    customer_age,
    customer_region,
    customer_type,
    COUNT(transaction_id) AS total_orders_placed,
    SUM(quantity) AS total_items_bought,
    ROUND(SUM(total_amount), 2) AS lifetime_expenditure,
    ROUND(AVG(total_amount), 2) AS avg_spend_per_visit
FROM retail_sales
GROUP BY customer_id, customer_gender, customer_age, customer_region, customer_type
ORDER BY lifetime_expenditure DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 12: Day of Week & Weekend vs. Weekday Dynamics
-- Business Question: Is shopping activity significantly higher on weekends?
-- --------------------------------------------------------------------
SELECT 
    CASE WHEN is_weekend = 1 THEN 'Weekend (Sat-Sun)' ELSE 'Weekday (Mon-Fri)' END AS day_classification,
    COUNT(transaction_id) AS order_count,
    ROUND(COUNT(transaction_id) * 100.0 / (SELECT COUNT(*) FROM retail_sales), 2) AS volume_share_pct,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM retail_sales), 2) AS revenue_share_pct,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM retail_sales
GROUP BY is_weekend
ORDER BY total_revenue DESC;
