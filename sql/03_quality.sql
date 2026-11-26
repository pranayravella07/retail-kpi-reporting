-- Data quality summary: how many rows each rule rejected.

DROP TABLE IF EXISTS dq_summary;
CREATE TABLE dq_summary AS
SELECT COALESCE(dq_issue, 'valid') AS dq_issue,
       COUNT(*)                     AS rows_count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM stg_sales), 2) AS pct_of_raw
FROM stg_sales
GROUP BY COALESCE(dq_issue, 'valid');
