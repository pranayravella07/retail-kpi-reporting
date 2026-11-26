"""Step 2b: load the labelled staging data into DuckDB and build the star schema with SQL."""
import duckdb
import pandas as pd

from config import BUDGET_GROWTH, SQL_DIR


def replace_table(con, name: str, df: pd.DataFrame) -> None:
    con.register("tmp_df", df)
    con.execute(f"DROP TABLE IF EXISTS {name}")
    con.execute(f"CREATE TABLE {name} AS SELECT * FROM tmp_df")
    con.unregister("tmp_df")


def build_dim_date(staging: pd.DataFrame) -> pd.DataFrame:
    dates = pd.to_datetime(staging["invoice_date"])
    days = pd.date_range(dates.min(), dates.max(), freq="D")
    return pd.DataFrame({
        "date": days.strftime("%Y-%m-%d"),
        "year": days.year,
        "quarter": days.quarter,
        "month": days.month,
        "month_name": days.strftime("%b"),
        "year_month": days.strftime("%Y-%m"),
        "weekday": days.strftime("%a"),
        "is_weekend": days.dayofweek >= 5,
    })


def run_sql_file(con, path) -> None:
    """Run every statement in a .sql file (statements are separated by ';')."""
    text = path.read_text(encoding="utf-8").replace("{budget_growth}", str(BUDGET_GROWTH))
    for statement in text.split(";"):
        if any(line.strip() and not line.strip().startswith("--") for line in statement.splitlines()):
            con.execute(statement)


def load_and_model(staging: pd.DataFrame, warehouse_path) -> None:
    con = duckdb.connect(str(warehouse_path))
    replace_table(con, "stg_sales", staging)
    replace_table(con, "dim_date", build_dim_date(staging))
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        print(f"  running {sql_file.name}")
        run_sql_file(con, sql_file)
    con.close()
