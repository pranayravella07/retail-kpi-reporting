"""Central settings for the pipeline. Change paths or rules here, not in the scripts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXPORT_DIR = DATA_DIR / "powerbi"          # CSV files that Power BI reads
WAREHOUSE_PATH = DATA_DIR / "retail.duckdb"
SQL_DIR = ROOT / "sql"

# Source: UCI Machine Learning Repository, "Online Retail II" (CC BY 4.0)
SOURCE_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
RAW_ZIP = RAW_DIR / "online_retail_ii.zip"
RAW_CSV = RAW_DIR / "online_retail_ii.csv"   # both Excel sheets combined, created once by extract.py

# The dataset has no budget. To show budget vs. actual we use an ASSUMED plan:
# budget for each month of 2011 = actual revenue of the same month in 2010 x (1 + growth).
BUDGET_GROWTH = 0.05
