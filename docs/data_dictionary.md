# Data Dictionary

Source: IBM Telco Customer Churn (extended, 33-column version), IBM Cognos Analytics sample data
(Kaggle: https://www.kaggle.com/datasets/yeanzc/telco-customer-churn-ibm-dataset). Fictional data: a telco
offering home phone + internet in California, Q3.

## Columns kept in `churn_clean.csv` (28)

| Column (cleaned) | Tableau header | Meaning | Notes |
|---|---|---|---|
| customer_id | CustomerID | Unique customer key | |
| city, zip_code, latitude, longitude | City, Zip Code, Latitude, Longitude | Primary residence | California only; city is the "region" substitute |
| gender | Gender | Male / Female | |
| senior_citizen | Senior Citizen | Yes / No | Only age-related field; no exact age available |
| partner, dependents | Partner, Dependents | Household context | |
| tenure_months | Tenure Months | Months as a customer | 0-72 expected |
| phone_service, multiple_lines | Phone Service, Multiple Lines | Phone products | "No phone service" merged into "No" |
| internet_service | Internet Service | DSL / Fiber optic / No | Main product-type field |
| online_security, online_backup, device_protection, tech_support, streaming_tv, streaming_movies | (Title Case) | Add-on services, Yes / No | "No internet service" merged into "No" |
| contract | Contract | Month-to-month / One year / Two year | |
| paperless_billing | Paperless Billing | Yes / No | |
| payment_method | Payment Method | 4 methods | |
| monthly_charges | Monthly Charges | Current monthly bill | |
| total_charges | Total Charges | Lifetime billing | Blank for brand-new customers in the raw file; set to 0 (assumption) |
| churn_flag | Churn Flag | **Target.** 1 = churned, 0 = active | From raw `Churn Value` |
| churn_score | Churn Score | IBM-modelled churn score | Modelled, not observed. Do NOT use to "discover" drivers (circular). |
| cltv | CLTV | IBM-modelled customer lifetime value | Modelled, not observed. Used for value segments only. |
| churn_reason | Churn Reason | Stated reason for leaving | Churned customers only; self-reported |

## Dropped columns
`Count` (constant 1), `Country`, `State` (constants), `Lat Long` (duplicates Latitude/Longitude),
`Churn Label` (duplicates Churn Value; checked for mismatches first).

## Derived fields (SQL view `churn_features`, Excel red-header columns, Tableau calculated fields)

| Field | Rule | Business reason |
|---|---|---|
| tenure_group | 0-6, 7-12, 13-24, 25-48, 49-72 months | Early-life churn behaves differently from long-tenure churn |
| charge_group | Under 35 / 35 to 69.99 / 70 to 89.99 / 90 and above | Tests price sensitivity |
| high_spender | Monthly Charges >= 75th percentile | Prioritise revenue |
| household_type | Senior / Non-senior with dependents / with partner / single | Age substitute for targeting |
| value_segment | CLTV <= P25 Low, >= P75 High, else Mid | Forward-looking value |
| contract_category | Month-to-month vs Long-term | Commitment lever |
| services_count | Number of add-ons = Yes (0-6) | Depth of relationship; "plan" proxy |
| revenue_lost_monthly | Monthly Charges if churned else 0 | Churn in money |
| risk_profile_match | Month-to-month AND tenure <= 12 AND has internet AND no Tech Support | Rule-based risk profile (assumption v1) |
| high_risk_flag | risk_profile_match AND still active | Retention call list |
