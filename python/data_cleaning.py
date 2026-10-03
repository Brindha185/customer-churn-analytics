"""
data_cleaning.py
----------------
Loads the raw IBM Telco Customer Churn file (33-column version), checks it,
cleans it, and writes:

  data/cleaned/churn_clean.csv          -> snake_case headers (used by SQL + Excel)
  data/cleaned/churn_clean_tableau.csv  -> Title Case headers (used by Tableau)
  data/cleaned/cleaning_log.csv         -> what was checked / changed / how many rows

Usage:
  python python/data_cleaning.py                      # uses data/raw/Telco_customer_churn.xlsx
  python python/data_cleaning.py path/to/file.xlsx    # or a .csv

Cleaning is intentionally small: the project is about analysis, not code.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = ROOT / "data" / "raw" / "Telco_customer_churn.xlsx"

# Columns the rest of the project relies on (after header normalisation)
REQUIRED = [
    "customerid", "city", "zip_code", "latitude", "longitude", "gender",
    "senior_citizen", "partner", "dependents", "tenure_months", "phone_service",
    "multiple_lines", "internet_service", "online_security", "online_backup",
    "device_protection", "tech_support", "streaming_tv", "streaming_movies",
    "contract", "paperless_billing", "payment_method", "monthly_charges",
    "total_charges", "churn_label", "churn_value", "churn_score", "cltv",
    "churn_reason",
]
ADDON_COLS = ["online_security", "online_backup", "device_protection",
              "tech_support", "streaming_tv", "streaming_movies"]
DROP_COLS = ["count", "country", "state", "lat_long", "churn_label"]

FINAL_ORDER = [
    "customer_id", "city", "zip_code", "latitude", "longitude", "gender",
    "senior_citizen", "partner", "dependents", "tenure_months", "phone_service",
    "multiple_lines", "internet_service", "online_security", "online_backup",
    "device_protection", "tech_support", "streaming_tv", "streaming_movies",
    "contract", "paperless_billing", "payment_method", "monthly_charges",
    "total_charges", "churn_flag", "churn_score", "cltv", "churn_reason",
]


def load_raw(path=None):
    """Read the raw file exactly as provided (no changes)."""
    path = Path(path) if path else DEFAULT_RAW
    if not path.exists():
        sys.exit(
            f"\nRaw data file not found: {path}\n"
            "Download 'Telco_customer_churn.xlsx' from\n"
            "  https://www.kaggle.com/datasets/yeanzc/telco-customer-churn-ibm-dataset\n"
            "and place it in data/raw/ (see data/raw/README.md).\n"
        )
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path, dtype=str)  # read everything as text first, convert deliberately
    return pd.read_csv(path, dtype=str)


def _normalise_headers(df):
    out = df.copy()
    out.columns = (out.columns.str.strip().str.lower()
                   .str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_"))
    return out


def clean(raw):
    """Return (clean_df, log_df). `raw` is the untouched DataFrame from load_raw()."""
    log = []

    def note(check, found, action):
        log.append({"check": check, "rows_affected": found, "action": action})

    df = _normalise_headers(raw)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        sys.exit(
            "\nThe raw file does not look like the 33-column IBM Telco file.\n"
            f"Missing columns: {missing}\n"
            f"Columns found: {list(df.columns)}\n"
            "Use the file from the Kaggle link in data/raw/README.md.\n"
        )
    note("Rows / columns in raw file", len(df), f"{raw.shape[0]} rows x {raw.shape[1]} columns loaded")

    # strip whitespace in all text values
    for c in df.columns:
        df[c] = df[c].astype("string").str.strip()

    # 1. duplicates
    dup_ids = int(df["customerid"].duplicated().sum())
    note("Duplicate CustomerID", dup_ids, "Dropped (kept first)" if dup_ids else "None found")
    df = df.drop_duplicates(subset="customerid", keep="first")

    # 2. numeric conversions
    df["tenure_months"] = pd.to_numeric(df["tenure_months"], errors="coerce")
    df["monthly_charges"] = pd.to_numeric(df["monthly_charges"], errors="coerce")
    tc_raw = pd.to_numeric(df["total_charges"], errors="coerce")
    blank_tc = int(tc_raw.isna().sum())
    note("Total Charges blank/non-numeric (stored as text)", blank_tc,
         "Set to 0 (ASSUMPTION: customer not yet billed, normally tenure = 0)")
    df["total_charges"] = tc_raw.fillna(0)
    blank_tc_pos_tenure = int(((tc_raw.isna()) & (df["tenure_months"] > 0)).sum())
    note("...of which have tenure > 0 (unexpected)", blank_tc_pos_tenure, "Review manually if > 0")

    for c in ["churn_value", "churn_score", "cltv", "latitude", "longitude"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 3. Senior Citizen sometimes appears as 0/1
    df["senior_citizen"] = df["senior_citizen"].replace({"1": "Yes", "0": "No"})

    # 4. inconsistent categorical values in service columns
    n_std = 0
    for c in ADDON_COLS + ["multiple_lines"]:
        mask = df[c].str.startswith("No ", na=False)  # 'No internet service' / 'No phone service'
        n_std += int(mask.sum())
        df.loc[mask, c] = "No"
    note("'No internet/phone service' values merged into 'No'", n_std,
         "Standardised so Yes/No counts work (raw sheet keeps the original)")

    # 5. label consistency
    mismatch = int(((df["churn_label"] == "Yes") != (df["churn_value"] == 1)).sum())
    note("Churn Label vs Churn Value mismatch", mismatch,
         "Churn Value used as the flag; Churn Label dropped" + (" - INVESTIGATE" if mismatch else ""))

    # 6. missing values in fields we analyse
    key = ["tenure_months", "monthly_charges", "churn_value", "cltv", "contract", "payment_method"]
    na_key = int(df[key].isna().any(axis=1).sum())
    note("Rows with missing values in key analysis fields", na_key,
         "Dropped" if na_key else "None found")
    df = df.dropna(subset=key)

    # 7. impossible / suspicious values (flag only)
    neg = int(((df["tenure_months"] < 0) | (df["monthly_charges"] <= 0)).sum())
    note("Negative tenure or non-positive monthly charge", neg, "Dropped" if neg else "None found")
    df = df[(df["tenure_months"] >= 0) & (df["monthly_charges"] > 0)]
    susp = int(((df["tenure_months"] > 0) &
                (df["total_charges"] < df["monthly_charges"] * 0.5)).sum())
    note("Total Charges < 50% of Monthly Charges despite tenure > 0 (suspicious)", susp,
         "Flagged only, not removed (ASSUMPTION: 0.5 is a loose threshold)")

    # 8. outliers (IQR on monthly charges) - informational
    q1, q3 = df["monthly_charges"].quantile([0.25, 0.75])
    iqr = q3 - q1
    out = int(((df["monthly_charges"] < q1 - 1.5 * iqr) | (df["monthly_charges"] > q3 + 1.5 * iqr)).sum())
    note("Monthly Charges outside 1.5 x IQR", out, "Kept (billing amounts, not errors)")

    # 9. blank churn reason for active customers is structural, not missing
    df["churn_reason"] = df["churn_reason"].replace({"": pd.NA})
    active_with_reason = int(((df["churn_value"] == 0) & df["churn_reason"].notna()).sum())
    note("Active customers with a churn reason (unexpected)", active_with_reason,
         "Churn Reason is only expected for churned customers")

    # 10. types, names, column drops
    df["zip_code"] = df["zip_code"].astype("string")
    for c in ["tenure_months", "churn_value", "churn_score", "cltv"]:
        df[c] = df[c].astype(int)
    df = df.rename(columns={"customerid": "customer_id", "churn_value": "churn_flag"})
    dropped = [c for c in DROP_COLS if c in df.columns]
    df = df.drop(columns=dropped)
    note("Columns dropped", len(dropped), ", ".join(dropped) + " (constants / duplicates)")
    df = df[FINAL_ORDER].reset_index(drop=True)
    note("Rows / columns in cleaned file", len(df), f"{df.shape[0]} rows x {df.shape[1]} columns")
    return df, pd.DataFrame(log)


def tableau_headers(df):
    """Title Case headers so Tableau field names match the calculated fields in the guide."""
    pretty = {c: c.replace("_", " ").title() for c in df.columns}
    pretty.update({"customer_id": "CustomerID", "cltv": "CLTV", "zip_code": "Zip Code",
                   "churn_flag": "Churn Flag", "streaming_tv": "Streaming TV"})
    return df.rename(columns=pretty)


def run(raw_path=None, out_dir=None):
    out_dir = Path(out_dir) if out_dir else ROOT / "data" / "cleaned"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = load_raw(raw_path)
    df, log = clean(raw)
    df.to_csv(out_dir / "churn_clean.csv", index=False)
    tableau_headers(df).to_csv(out_dir / "churn_clean_tableau.csv", index=False)
    log.to_csv(out_dir / "cleaning_log.csv", index=False)
    print(log.to_string(index=False))
    print(f"\nWrote {len(df)} rows to {out_dir}")
    return raw, df, log


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
