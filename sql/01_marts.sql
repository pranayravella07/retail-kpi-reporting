-- Star schema: one fact table (one row per valid sales line) and its dimensions.
-- Only rows without a data quality issue reach the fact table.

DROP TABLE IF EXISTS fct_sales;
CREATE TABLE fct_sales AS
SELECT
    sales_line_id,
    invoice,
    invoice_date,
    stock_code,
    customer_id,
    country,
    quantity,
    unit_price,
    revenue
FROM stg_sales
WHERE dq_issue IS NULL;

-- Products: a stock code can appear with slightly different descriptions,
-- so we keep the most frequent one.
DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product AS
WITH description_counts AS (
    SELECT stock_code, description, COUNT(*) AS n
    FROM stg_sales
    WHERE dq_issue IS NULL
    GROUP BY stock_code, description
),
ranked AS (
    SELECT stock_code, description,
           ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY n DESC, description) AS rn
    FROM description_counts
)
SELECT r.stock_code,
       r.description,
       ROUND(AVG(f.unit_price), 2) AS avg_unit_price,
       MIN(f.invoice_date)         AS first_sold,
       MAX(f.invoice_date)         AS last_sold
FROM ranked r
JOIN fct_sales f ON f.stock_code = r.stock_code
WHERE r.rn = 1
GROUP BY r.stock_code, r.description;

DROP TABLE IF EXISTS dim_country;
CREATE TABLE dim_country AS
SELECT country,
       CASE WHEN country = 'United Kingdom' THEN 'Domestic (UK)' ELSE 'International' END AS market
FROM fct_sales
GROUP BY country;

DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer AS
SELECT customer_id,
       MIN(invoice_date)         AS first_purchase,
       COUNT(DISTINCT invoice)   AS orders,
       ROUND(SUM(revenue), 2)    AS lifetime_revenue
FROM fct_sales
GROUP BY customer_id;
