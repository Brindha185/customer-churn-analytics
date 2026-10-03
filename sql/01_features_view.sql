-- 01_features_view.sql  (SQLite dialect; Postgres/MySQL notes in docs/assumptions.md)
-- Builds the analysis view with every derived field, once.
-- Requires tables: churn_clean (from data/cleaned/churn_clean.csv) and params (percentile cut-offs).
-- Change bands or the risk rule HERE and every query below updates.

DROP VIEW IF EXISTS churn_features;
CREATE VIEW churn_features AS
SELECT
  c.*,
  CASE WHEN tenure_months <= 6  THEN '0-6 mo'
       WHEN tenure_months <= 12 THEN '7-12 mo'
       WHEN tenure_months <= 24 THEN '13-24 mo'
       WHEN tenure_months <= 48 THEN '25-48 mo'
       ELSE '49-72 mo' END                                   AS tenure_group,
  CASE WHEN monthly_charges < 35 THEN 'Under 35'
       WHEN monthly_charges < 70 THEN '35 to 69.99'
       WHEN monthly_charges < 90 THEN '70 to 89.99'
       ELSE '90 and above' END                                     AS charge_group,
  CASE WHEN monthly_charges >= p.charge_p75 THEN 1 ELSE 0 END AS high_spender,
  CASE WHEN senior_citizen = 'Yes' THEN 'Senior'
       WHEN dependents = 'Yes'     THEN 'Non-senior with dependents'
       WHEN partner = 'Yes'        THEN 'Non-senior with partner'
       ELSE 'Non-senior single' END                       AS household_type,
  CASE WHEN cltv <= p.cltv_p25 THEN 'Low'
       WHEN cltv >= p.cltv_p75 THEN 'High'
       ELSE 'Mid' END                                     AS value_segment,
  CASE WHEN contract = 'Month-to-month' THEN 'Month-to-month' ELSE 'Long-term' END AS contract_category,
  (CASE WHEN online_security   = 'Yes' THEN 1 ELSE 0 END +
   CASE WHEN online_backup     = 'Yes' THEN 1 ELSE 0 END +
   CASE WHEN device_protection = 'Yes' THEN 1 ELSE 0 END +
   CASE WHEN tech_support      = 'Yes' THEN 1 ELSE 0 END +
   CASE WHEN streaming_tv      = 'Yes' THEN 1 ELSE 0 END +
   CASE WHEN streaming_movies  = 'Yes' THEN 1 ELSE 0 END) AS services_count,
  CASE WHEN churn_flag = 1 THEN monthly_charges ELSE 0 END AS revenue_lost_monthly,
  -- RISK PROFILE (assumption v1, validate with Q16): month-to-month, first year, has internet, no Tech Support
  CASE WHEN contract = 'Month-to-month' AND tenure_months <= 12
             AND internet_service <> 'No' AND tech_support = 'No'
       THEN 1 ELSE 0 END                                  AS risk_profile_match,
  CASE WHEN churn_flag = 0 AND contract = 'Month-to-month' AND tenure_months <= 12
             AND internet_service <> 'No' AND tech_support = 'No'
       THEN 1 ELSE 0 END                                  AS high_risk_flag
FROM churn_clean c
CROSS JOIN params p;
