# Project Checklist

## Setup
- [ ] Python 3.9+ installed; `pip install -r requirements.txt`
- [ ] `python run_all.py --self-test` finishes with Reconciliation: PASS (synthetic data, checks your setup only)
- [ ] Real dataset downloaded to `data/raw/Telco_customer_churn.xlsx`
- [ ] GitHub repo created, this folder pushed

## Data cleaning
- [ ] `python run_all.py` runs; read `data/cleaned/cleaning_log.csv`
- [ ] Any "unexpected" counts in the log investigated and explained in docs/assumptions.md
- [ ] Cleaning also done by hand in Excel once (steps in the Excel sheet comments + README) so you can explain it
- [ ] SQL cleaning reference reviewed (`sql/00_cleaning_reference_postgres.sql`)

## Feature engineering and KPIs
- [ ] Each derived field explained in docs/data_dictionary.md (reason, not just rule)
- [ ] KPI definitions in docs/kpi_definitions.md understood (formula, meaning, why management cares)
- [ ] Risk profile back-tested (q16); revised if lift is weak, and the SAME rule updated in SQL, Excel and Tableau

## Analysis
- [ ] SQL results reviewed (`outputs/sql_results/`), at least q00-q21 read
- [ ] Controlled comparisons read: q19 (payment x contract), q20 (price x contract)
- [ ] Excel workbook opened; formulas inspected; real PivotTables + slicers added (Read Me sheet, 10 minutes)
- [ ] `python tests/verify_excel_vs_sql.py excel/customer_churn_analysis.xlsx outputs/sql_results` = PASS (after opening and saving the workbook in Excel once)

## Dashboards (ready-made PNGs) and optional Tableau
- [ ] `screenshots/` contains the 3 generated dashboard PNGs; open each and sanity-check against `outputs/sql_results/`
- [ ] Connected to churn_clean_tableau.csv; all calculated fields created
- [ ] KPIs reconciled with q00_kpi_summary.csv
- [ ] Dashboard 1, 2, 3 built per tableau/TABLEAU_BUILD_GUIDE.md
- [ ] Reference lines, tooltips, filters, navigation buttons added
- [ ] Screenshots exported to screenshots/; .twbx saved to tableau/

## Insights, recommendations, documentation
- [ ] 8-12 insights written (docs/insights_template.md) with real numbers only; failed hypotheses reported honestly
- [ ] Each recommendation tied to a confirmed finding (docs/recommendations_template.md)
- [ ] README placeholders ([FILL]) all replaced; screenshots linked
- [ ] Assumptions & limitations section complete

## Interview readiness
- [ ] Can explain every assumption and why you chose it
- [ ] Can explain why Churn Score was not used to find drivers
- [ ] Can explain why the "trend" is a lifecycle view, not a calendar trend
- [ ] Can explain how the numbers tie out across SQL, Excel and Tableau (reconcile.py)
- [ ] Can explain what you would do differently with dated data (cohorts, survival analysis)
- [ ] Repo pinned on GitHub profile and linked from resume

## Skills demonstrated
Excel | SQL | Tableau | Data cleaning | EDA | KPI development | Customer segmentation | Business analysis | Data visualisation | Business recommendations
