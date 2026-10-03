# START HERE

## What this is
A complete, runnable analytics project: cleaning -> SQL -> Excel workbook -> Tableau-ready data and build guide -> docs.
It contains **no results yet**, because the real dataset must be downloaded by you (see below).

## Run it in 5 steps (Windows / Mac / Linux, about 10 minutes)
1. Install Python 3.9 or newer (https://www.python.org/downloads/). Check: `python --version` (or `python3 --version`).
2. Open a terminal in this folder and install the two libraries:
   `pip install -r requirements.txt`
3. **Smoke test** (synthetic data, results are meaningless, it only proves your setup works):
   `python run_all.py --self-test`
   You should see `Reconciliation: PASS`.
4. Download the real dataset (free Kaggle account) and save it as `data/raw/Telco_customer_churn.xlsx`
   (instructions + link: `data/raw/README.md`).
5. Run the real thing:
   `python run_all.py`
   (On Mac/Linux use `python3` if `python` is not found.)

## What you get after step 5
| Output | Location |
|---|---|
| Cleaned data (SQL/Excel) | `data/cleaned/churn_clean.csv` |
| **Tableau input file** | `data/cleaned/churn_clean_tableau.csv` |
| Cleaning log | `data/cleaned/cleaning_log.csv` |
| Derived-fields table (cross-check) | `data/cleaned/churn_features.csv` |
| SQLite database | `outputs/churn.db` |
| 22 SQL query results (CSV) | `outputs/sql_results/` |
| Excel workbook with dashboard | `excel/customer_churn_analysis.xlsx` |
| **3 ready-made dashboard images** | `screenshots/dashboard_1_executive.png`, `dashboard_2_segmentation.png`, `dashboard_3_risk.png` |

## Then
1. Open the Excel workbook (formulas calculate when it opens). Read the **Read Me** sheet.
2. Optional check: `python tests/verify_excel_vs_sql.py excel/customer_churn_analysis.xlsx outputs/sql_results`
   (open the workbook in Excel and save it once first so values are stored).
3. (Optional) Rebuild the dashboards in Tableau with `tableau/TABLEAU_BUILD_GUIDE.md` and `tableau/calculated_fields.md`.
4. Fill in `docs/insights_template.md` and `docs/recommendations_template.md` from YOUR results, then complete the README.
5. Tick through `docs/project_checklist.md`.

## Where can I run this?
Anywhere with Python: your laptop, or Google Colab / GitHub Codespaces (upload the folder, then `!pip install -r requirements.txt`
and `!python run_all.py`). Tableau is a separate desktop app (Tableau Public is free).

## Troubleshooting
- "Raw data file not found": the dataset is not in `data/raw/` with the exact file name.
- "does not look like the 33-column IBM Telco file": you downloaded the older 21-column version. Use the Kaggle link in `data/raw/README.md`.
- Excel shows blank numbers: press F9, or check Formulas > Calculation Options > Automatic.
- `python` not found: try `python3`, or reinstall Python and tick "Add to PATH".
