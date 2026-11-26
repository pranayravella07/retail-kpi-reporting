"""Print a short data quality report from the warehouse."""
import duckdb

from clean import RULES

DESCRIPTIONS = dict(RULES)


def print_report(warehouse_path) -> None:
    con = duckdb.connect(str(warehouse_path), read_only=True)
    total = con.execute("SELECT COUNT(*) FROM stg_sales").fetchone()[0]
    rows = con.execute("SELECT dq_issue, rows_count, pct_of_raw FROM dq_summary ORDER BY rows_count DESC").fetchall()
    revenue = con.execute("SELECT ROUND(SUM(revenue), 2) FROM fct_sales").fetchone()[0]
    con.close()

    print("\n=== Data quality report ===")
    print(f"Raw rows: {total:,}")
    for issue, n, pct in rows:
        label = "passed all rules" if issue == "valid" else DESCRIPTIONS.get(issue, "")
        print(f"  {issue:<22} {n:>10,}  ({pct:>5}%)  {label}")
    print(f"Revenue in fct_sales: {revenue:,.2f} GBP")
