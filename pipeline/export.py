"""Step 2c: export the star schema as CSV files for Power BI."""
import duckdb

TABLES = ["fct_sales", "dim_date", "dim_product", "dim_customer", "dim_country", "monthly_budget", "dq_summary"]


def export_for_powerbi(warehouse_path, export_dir) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(warehouse_path), read_only=True)
    for table in TABLES:
        df = con.execute(f"SELECT * FROM {table}").df()
        df.to_csv(export_dir / f"{table}.csv", index=False)
        print(f"  {table}.csv  ({len(df):,} rows)")
    con.close()
