"""Step 1: download the Online Retail II dataset and save it as one CSV file.

The source is an Excel file with two sheets (2009-2010 and 2010-2011).
Reading Excel is slow, so we do it only once and keep a CSV copy.
"""
import zipfile

import pandas as pd
import requests

from config import RAW_CSV, RAW_DIR, RAW_ZIP, SOURCE_URL


def download() -> None:
    if RAW_ZIP.exists():
        print(f"Already downloaded: {RAW_ZIP.name}")
        return
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("Downloading Online Retail II (~45 MB)...")
    with requests.get(SOURCE_URL, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(RAW_ZIP, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    print("Download finished.")


def excel_to_csv() -> None:
    if RAW_CSV.exists():
        print(f"Already converted: {RAW_CSV.name}")
        return
    with zipfile.ZipFile(RAW_ZIP) as z:
        xlsx_name = next(n for n in z.namelist() if n.lower().endswith(".xlsx"))
        z.extract(xlsx_name, RAW_DIR)
    print("Reading both Excel sheets (this takes 2-4 minutes)...")
    sheets = pd.read_excel(RAW_DIR / xlsx_name, sheet_name=None, dtype={"Invoice": str, "StockCode": str})
    df = pd.concat(sheets.values(), ignore_index=True)
    df.to_csv(RAW_CSV, index=False)
    print(f"Saved {len(df):,} rows to {RAW_CSV.name}")


def main() -> None:
    download()
    excel_to_csv()


if __name__ == "__main__":
    main()
