-- Q1 Revenue, orders and average order value per year (2009 and 2011 are partial years)
SELECT SUBSTR(invoice_date, 1, 4)                         AS year,
       ROUND(SUM(revenue), 0)                             AS revenue_gbp,
       COUNT(DISTINCT invoice)                            AS orders,
       ROUND(SUM(revenue) / COUNT(DISTINCT invoice), 2)   AS avg_order_value
FROM fct_sales
GROUP BY SUBSTR(invoice_date, 1, 4)
ORDER BY year;

-- Q2 Year-over-year growth by month (2011 vs. 2010)
WITH monthly AS (
    SELECT SUBSTR(invoice_date, 1, 4) AS year, SUBSTR(invoice_date, 6, 2) AS month, SUM(revenue) AS revenue
    FROM fct_sales
    GROUP BY SUBSTR(invoice_date, 1, 4), SUBSTR(invoice_date, 6, 2)
)
SELECT cur.month,
       ROUND(prev.revenue, 0)                                   AS revenue_2010,
       ROUND(cur.revenue, 0)                                    AS revenue_2011,
       ROUND(100.0 * (cur.revenue - prev.revenue) / prev.revenue, 1) AS yoy_pct
FROM monthly cur
JOIN monthly prev ON prev.month = cur.month AND prev.year = '2010'
WHERE cur.year = '2011'
ORDER BY cur.month;

-- Q3 Top 10 products by revenue
SELECT p.description,
       ROUND(SUM(f.revenue), 0)  AS revenue_gbp,
       SUM(f.quantity)           AS units_sold
FROM fct_sales f
JOIN dim_product p ON p.stock_code = f.stock_code
GROUP BY p.description
ORDER BY revenue_gbp DESC
LIMIT 10;

-- Q4 Revenue share by market, and top 5 international countries
SELECT c.market AS segment,
       ROUND(SUM(f.revenue), 0) AS revenue_gbp,
       ROUND(100.0 * SUM(f.revenue) / (SELECT SUM(revenue) FROM fct_sales), 1) AS share_pct
FROM fct_sales f JOIN dim_country c ON c.country = f.country
GROUP BY c.market
UNION ALL
SELECT * FROM (
    SELECT '  ' || f.country, ROUND(SUM(f.revenue), 0),
           ROUND(100.0 * SUM(f.revenue) / (SELECT SUM(revenue) FROM fct_sales), 1)
    FROM fct_sales f JOIN dim_country c ON c.country = f.country
    WHERE c.market = 'International'
    GROUP BY f.country
    ORDER BY 2 DESC
    LIMIT 5
);

-- Q5 Budget vs. actual 2011 (budget is an ASSUMPTION: same month 2010 + 5%)
SELECT year_month,
       ROUND(actual_revenue, 0)                                      AS actual_gbp,
       ROUND(budget_revenue, 0)                                      AS budget_gbp,
       ROUND(actual_revenue - budget_revenue, 0)                     AS variance_gbp,
       ROUND(100.0 * (actual_revenue - budget_revenue) / budget_revenue, 1) AS variance_pct
FROM monthly_budget
ORDER BY year_month;

-- Q6 Registered vs. guest customers, and how much revenue comes from repeat customers
SELECT CASE WHEN c.customer_id = 'Guest' THEN 'Guest orders'
            WHEN c.orders > 1 THEN 'Repeat customers'
            ELSE 'One-time customers' END   AS customer_type,
       COUNT(*)                              AS customers,
       ROUND(SUM(c.lifetime_revenue), 0)     AS revenue_gbp,
       ROUND(100.0 * SUM(c.lifetime_revenue) / (SELECT SUM(revenue) FROM fct_sales), 1) AS share_pct
FROM dim_customer c
GROUP BY 1
ORDER BY revenue_gbp DESC;

-- Q7 Price comparison: average unit price at home vs. abroad for the 10 best-selling products
WITH top_products AS (
    SELECT stock_code FROM fct_sales GROUP BY stock_code ORDER BY SUM(quantity) DESC LIMIT 10
)
SELECT p.description,
       ROUND(AVG(CASE WHEN c.market = 'Domestic (UK)' THEN f.unit_price END), 2) AS avg_price_uk,
       ROUND(AVG(CASE WHEN c.market = 'International' THEN f.unit_price END), 2) AS avg_price_international
FROM fct_sales f
JOIN top_products t ON t.stock_code = f.stock_code
JOIN dim_product p  ON p.stock_code = f.stock_code
JOIN dim_country c  ON c.country = f.country
GROUP BY p.description
ORDER BY p.description;
