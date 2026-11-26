-- Monthly actual revenue and an ASSUMED budget.
-- The dataset has no real budget, so the plan for each 2011 month is the same month
-- in 2010 plus {budget_growth} growth. This lets us show budget vs. actual honestly labelled.

DROP TABLE IF EXISTS monthly_budget;
CREATE TABLE monthly_budget AS
WITH monthly AS (
    SELECT SUBSTR(invoice_date, 1, 7)               AS year_month,
           CAST(SUBSTR(invoice_date, 1, 4) AS INTEGER) AS year,
           SUBSTR(invoice_date, 6, 2)               AS month,
           ROUND(SUM(revenue), 2)                   AS actual_revenue
    FROM fct_sales
    GROUP BY SUBSTR(invoice_date, 1, 7), SUBSTR(invoice_date, 1, 4), SUBSTR(invoice_date, 6, 2)
)
SELECT cur.year_month,
       cur.actual_revenue,
       ROUND(prev.actual_revenue * (1 + {budget_growth}), 2) AS budget_revenue
FROM monthly cur
LEFT JOIN monthly prev
       ON prev.month = cur.month AND prev.year = cur.year - 1
WHERE cur.year = 2011;
