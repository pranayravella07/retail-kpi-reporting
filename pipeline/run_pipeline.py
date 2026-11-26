"""Run the whole pipeline: extract -> clean -> load + model -> export -> report.

Usage:  python pipeline/run_pipeline.py
"""
import time

from clean import build_staging
from config import EXPORT_DIR, RAW_CSV, WAREHOUSE_PATH
from export import export_for_powerbi
from extract import main as extract
from load import load_and_model
from quality_report import print_report


def main() -> None:
    start = time.time()
    print("1/4 Extract")
    extract()
    print("2/4 Clean and label data quality issues")
    staging = build_staging(RAW_CSV)
    print(f"  {len(staging):,} raw rows labelled")
    print("3/4 Load into DuckDB and build star schema")
    load_and_model(staging, WAREHOUSE_PATH)
    print("4/4 Export CSV files for Power BI")
    export_for_powerbi(WAREHOUSE_PATH, EXPORT_DIR)
    print_report(WAREHOUSE_PATH)
    print(f"\nDone in {time.time() - start:.0f} seconds.")


if __name__ == "__main__":
    main()
