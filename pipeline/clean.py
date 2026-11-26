"""Step 2a: label every raw row with the first data quality rule it breaks.

Nothing is deleted here. Rows with dq_issue = NULL are valid sales;
all other rows are counted in the quality report, so nothing disappears silently.
"""
import numpy as np
import pandas as pd

# Rules in the order they are checked. The first rule a row breaks is its label.
RULES = [
    ("duplicate_row", "Exact duplicate of an earlier row (incl. overlap between the two Excel sheets)"),
    ("cancelled_original_sale", "Sale that was later cancelled by a matching 'C' invoice (same customer, product, quantity, price)"),
    ("cancelled_invoice", "Invoice number starts with 'C': a cancellation, not a sale"),
    ("non_product_code", "Postage, fees, manual adjustments or test codes, not a product"),
    ("non_positive_quantity", "Quantity is zero or negative"),
    ("non_positive_price", "Unit price is zero or negative"),
    ("missing_description", "Product has no description"),
]


def load_raw(path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"Invoice": str, "StockCode": str, "Customer ID": "string"})
    df = df.rename(columns={
        "Invoice": "invoice", "StockCode": "stock_code", "Description": "description",
        "Quantity": "quantity", "InvoiceDate": "invoice_ts", "Price": "unit_price",
        "Customer ID": "customer_id", "Country": "country",
    })
    df["invoice_ts"] = pd.to_datetime(df["invoice_ts"])
    df["customer_id"] = df["customer_id"].str.replace(r"\.0$", "", regex=True)  # 12345.0 -> 12345
    df["description"] = df["description"].astype("string").str.strip()
    return df


def find_cancelled_originals(df: pd.DataFrame, is_duplicate: pd.Series) -> pd.Series:
    """Flag sales that a later cancellation fully reverses.

    A cancellation (invoice starting with 'C', negative quantity) is matched to sales with the same
    customer, product, quantity and price. If a key has N cancellations, the N most recent matching
    sales before the last cancellation are flagged, so each cancellation removes exactly one sale.
    """
    keys = ["customer_id", "stock_code", "abs_qty", "unit_price"]
    is_cancel = df["invoice"].str.startswith("C", na=False)
    base = df.assign(abs_qty=df["quantity"].abs())
    usable = base["customer_id"].notna() & ~is_duplicate   # guests can't be matched reliably

    cancels = base[usable & is_cancel & (base["quantity"] < 0)]
    sales = base[usable & ~is_cancel & (base["quantity"] > 0)].reset_index(names="row_id")

    per_key = cancels.groupby(keys).agg(n_cancel=("invoice_ts", "size"), last_cancel_ts=("invoice_ts", "max"))
    candidates = sales.merge(per_key, left_on=keys, right_index=True)
    candidates = candidates[candidates["invoice_ts"] <= candidates["last_cancel_ts"]]
    candidates = candidates.sort_values("invoice_ts", ascending=False)
    candidates["rank"] = candidates.groupby(keys).cumcount() + 1

    flagged_rows = candidates.loc[candidates["rank"] <= candidates["n_cancel"], "row_id"]
    return df.index.isin(flagged_rows)


def label_quality(df: pd.DataFrame) -> pd.DataFrame:
    is_duplicate = df.duplicated(keep="first")
    checks = {
        "duplicate_row": is_duplicate,
        "cancelled_original_sale": find_cancelled_originals(df, is_duplicate),
        "cancelled_invoice": df["invoice"].str.startswith("C", na=False),
        # real product codes start with 5 digits, e.g. 85123A
        "non_product_code": ~df["stock_code"].str.match(r"^\d{5}", na=False),
        "non_positive_quantity": df["quantity"] <= 0,
        "non_positive_price": df["unit_price"] <= 0,
        "missing_description": df["description"].isna() | (df["description"] == ""),
    }
    df = df.copy()
    df["dq_issue"] = np.select([checks[name] for name, _ in RULES], [name for name, _ in RULES], default=None)
    return df


def add_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Columns that make the SQL simple and portable."""
    df = df.copy()
    df["sales_line_id"] = np.arange(1, len(df) + 1)
    df["invoice_date"] = df["invoice_ts"].dt.strftime("%Y-%m-%d")
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    df["customer_id"] = df["customer_id"].fillna("Guest")   # guest orders are still revenue
    df["invoice_ts"] = df["invoice_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def build_staging(raw_path) -> pd.DataFrame:
    return add_columns(label_quality(load_raw(raw_path)))
