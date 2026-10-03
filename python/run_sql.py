"""
run_sql.py
----------
Loads data/cleaned/churn_clean.csv into a local SQLite database, builds the feature view,
runs every query in sql/02_churn_analysis.sql, and exports one CSV per query.

No database server needed: SQLite ships with Python.
Output:  outputs/churn.db  and  outputs/sql_results/<query_name>.csv
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def build_database(clean_csv, db_path):
    df = pd.read_csv(clean_csv, dtype={"zip_code": str})
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    df.to_sql("churn_clean", con, index=False)
    # Percentile cut-offs computed once so SQL, Excel and Tableau use the same thresholds
    params = pd.DataFrame([{
        "cltv_p25": df["cltv"].quantile(0.25),
        "cltv_p75": df["cltv"].quantile(0.75),
        "charge_p75": df["monthly_charges"].quantile(0.75),
    }])
    params.to_sql("params", con, index=False)
    con.executescript((ROOT / "sql" / "01_features_view.sql").read_text())
    con.commit()
    return con


def split_queries(sql_text):
    """Return [(name, statement)] using the '-- @query name' markers."""
    parts = re.split(r"^-- @query\s+(\w+)\s*$", sql_text, flags=re.M)
    return [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts), 2)]


def run(clean_csv=None, out_dir=None, db_path=None):
    clean_csv = Path(clean_csv) if clean_csv else ROOT / "data" / "cleaned" / "churn_clean.csv"
    out_dir = Path(out_dir) if out_dir else ROOT / "outputs"
    db_path = Path(db_path) if db_path else out_dir / "churn.db"
    res_dir = out_dir / "sql_results"
    res_dir.mkdir(parents=True, exist_ok=True)

    con = build_database(clean_csv, db_path)
    results = {}
    for name, stmt in split_queries((ROOT / "sql" / "02_churn_analysis.sql").read_text()):
        df = pd.read_sql_query(stmt, con)
        df.to_csv(res_dir / f"{name}.csv", index=False)
        results[name] = df
        print(f"  {name:<34} {len(df):>3} rows")
    # full feature table for Tableau cross-checks / Excel validation
    feats = pd.read_sql_query("SELECT * FROM churn_features", con)
    feats.to_csv(clean_csv.parent / "churn_features.csv", index=False)
    con.close()
    print(f"\nSQL results -> {res_dir}")
    return results


if __name__ == "__main__":
    run()
