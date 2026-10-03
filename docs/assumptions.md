# Assumptions & Limitations

Keep this file honest and complete. It is one of the strongest parts of the project in an interview.

## Data limitations (dataset-driven)
1. **No calendar dates.** There is no signup or cancellation date, so there is no monthly/quarterly churn trend.
   The "trend" visual is a *lifecycle view* (churn by months since signup). Do not call it a time trend.
2. **No age.** Only Senior Citizen (Yes/No) plus Partner/Dependents. Household type is the substitute.
3. **No subscription plan.** Plan proxy = Internet Service type x number of add-on services x Contract.
4. **No support calls / satisfaction** in this version. Tech Support (Yes/No) is the support proxy.
5. **Region = California cities only.** City analysis needs a minimum size; thresholds below.
6. **Single snapshot.** Churn rate here is churned / all customers in the file.
7. **Churn Score and CLTV are IBM-modelled.** CLTV is used only for value segments. Churn Score is not used to find drivers
   (it already encodes a model, so using it would be circular).
8. **The data is fictional.** Say "public IBM sample dataset", not "real company data".
9. **Observational data.** Findings are associations. Recommendations are hypotheses to A/B test, not proof.

## Analyst assumptions (all adjustable)
| Assumption | Where it lives | Why |
|---|---|---|
| Blank Total Charges set to 0 | data_cleaning.py | Blank rows should be brand-new customers (tenure 0); the script reports any exceptions |
| Tenure bands 0-6 / 7-12 / 13-24 / 25-48 / 49-72 | SQL view, Excel formula, Tableau calc | Sensible lifecycle stages; re-cut after viewing the distribution |
| Charge bands <35 / 35-69.99 / 70-89.99 / 90+ | same | Rough price tiers; re-cut after viewing the distribution |
| Value segment = CLTV quartiles; high spender = top quarter of monthly charges | params table / Calculations!B22:B24 | Data-driven cut-offs |
| Risk profile v1 = Month-to-month AND tenure <= 12 AND has internet AND no Tech Support | SQL view, Excel, Tableau | Starting hypothesis; **back-test it (Q16)** and revise from your own findings |
| Annualised revenue = monthly x 12 | SQL q10/q17, Excel, Tableau | Assumes lost customers would have stayed 12 months |
| City minimum 30 customers; segment minimum 50 | SQL q04/q11, Excel, Tableau | Avoids small-sample noise |
| Suspicious billing flag: Total Charges < 50% of Monthly Charges (tenure > 0) | data_cleaning.py | Loose sanity check, flag only |

## SQL dialect notes
The project runs on SQLite (bundled with Python, no install). For PostgreSQL / MySQL:
- `MAX(a, b)` (scalar) -> `GREATEST(a, b)`
- Integer division in q14: `(x - 1) / 6` -> `FLOOR((x - 1) / 6.0)` in Postgres
- `CREATE VIEW ... CROSS JOIN params` works unchanged; load `params` as a one-row table
- Cleaning reference in Postgres syntax: `sql/00_cleaning_reference_postgres.sql`
