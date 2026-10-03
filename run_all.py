"""
run_all.py  -  one command to run the whole pipeline.

  python run_all.py              # real run: needs data/raw/Telco_customer_churn.xlsx
  python run_all.py --self-test  # checks your setup with SYNTHETIC data (results are meaningless)

Steps: 1) clean data  2) load into SQLite + run SQL analysis  3) reconcile pandas vs SQL
       4) build the Excel workbook  5) build the 3 dashboard PNGs (screenshots/)
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "tests"))

import build_excel  # noqa: E402
import data_cleaning  # noqa: E402
import reconcile  # noqa: E402
import run_sql  # noqa: E402


def main():
    self_test = "--self-test" in sys.argv
    if self_test:
        import make_synthetic_test_data as synth
        work = Path(tempfile.mkdtemp(prefix="churn_selftest_"))
        raw_path = work / "synthetic_raw.xlsx"
        synth.make().to_excel(raw_path, index=False)
        cleaned_dir, out_dir = work / "cleaned", work / "outputs"
        excel_out = work / "customer_churn_analysis_SELFTEST.xlsx"
        print("\n*** SELF-TEST MODE: SYNTHETIC DATA. Do not use any result. ***\n")
    else:
        raw_path = ROOT / "data" / "raw" / "Telco_customer_churn.xlsx"
        cleaned_dir, out_dir = ROOT / "data" / "cleaned", ROOT / "outputs"
        excel_out = ROOT / "excel" / "customer_churn_analysis.xlsx"

    print("STEP 1/5  Cleaning data")
    data_cleaning.run(raw_path, cleaned_dir)
    clean_csv = cleaned_dir / "churn_clean.csv"

    print("\nSTEP 2/5  SQL analysis (SQLite)")
    run_sql.run(clean_csv, out_dir)

    print("\nSTEP 3/5  Reconciling SQL against an independent pandas calculation")
    ok = reconcile.run(clean_csv, out_dir / "sql_results")

    print("\nSTEP 4/5  Building Excel workbook")
    build_excel.build(raw_path, clean_csv, cleaned_dir / "cleaning_log.csv", excel_out)

    print("\nSTEP 5/5  Building the three dashboard images")
    shots_dir = (work / "screenshots") if self_test else ROOT / "screenshots"
    try:
        import build_dashboards
        build_dashboards.build(cleaned_dir / "churn_features.csv", shots_dir)
    except SystemExit as e:  # matplotlib missing, etc.
        print("  Skipped dashboards:", e)

    print("\n" + "=" * 60)
    print("DONE" + ("  (self-test: synthetic data)" if self_test else ""))
    print(f"  Cleaned data   : {cleaned_dir}")
    print(f"  SQL results    : {out_dir / 'sql_results'}")
    print(f"  Excel workbook : {excel_out}")
    print(f"  Dashboards     : {shots_dir}")
    if not self_test:
        print("  Tableau file   : data/cleaned/churn_clean_tableau.csv  (connect Tableau to this)")
    print("  Reconciliation :", "PASS" if ok else "FAIL - investigate before building dashboards")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
