"""
reconcile.py
------------
Independent check: recompute the headline KPIs with pandas and compare them with the SQL results.
If these match, you can say "numbers tie out across SQL, Excel and Tableau" in an interview.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def run(clean_csv=None, results_dir=None):
    clean_csv = Path(clean_csv) if clean_csv else ROOT / "data" / "cleaned" / "churn_clean.csv"
    results_dir = Path(results_dir) if results_dir else ROOT / "outputs" / "sql_results"
    df = pd.read_csv(clean_csv)
    sql = pd.read_csv(results_dir / "q00_kpi_summary.csv").iloc[0]

    expected = {
        "total_customers": len(df),
        "active_customers": int((df.churn_flag == 0).sum()),
        "churned_customers": int(df.churn_flag.sum()),
        "churn_rate_pct": round(100 * df.churn_flag.mean(), 2),
        "mrr_active": round(df.loc[df.churn_flag == 0, "monthly_charges"].sum(), 2),
        "monthly_revenue_lost": round(df.loc[df.churn_flag == 1, "monthly_charges"].sum(), 2),
        "avg_monthly_charges": round(df.monthly_charges.mean(), 2),
        "avg_tenure_months": round(df.tenure_months.mean(), 2),
    }
    ok = True
    print(f"{'KPI':<24}{'pandas':>14}{'SQL':>14}  status")
    for k, v in expected.items():
        match = abs(float(sql[k]) - float(v)) < 0.01
        ok &= match
        print(f"{k:<24}{v:>14}{sql[k]:>14}  {'OK' if match else 'MISMATCH'}")
    print("\nReconciliation:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    run()
