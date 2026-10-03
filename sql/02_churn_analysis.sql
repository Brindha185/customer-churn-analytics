-- 02_churn_analysis.sql  (SQLite dialect)
-- Each query starts with a "-- @query <name>" marker; python/run_sql.py runs them and
-- exports one CSV per query to outputs/sql_results/.
-- Segment queries ALWAYS show customer counts next to rates. Small segments mislead.

-- @query q00_kpi_summary
-- One-row KPI table. Used to reconcile SQL vs Excel vs Tableau.
SELECT
  COUNT(*)                                                         AS total_customers,
  SUM(1 - churn_flag)                                              AS active_customers,
  SUM(churn_flag)                                                  AS churned_customers,
  ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2)                     AS churn_rate_pct,
  ROUND(100.0 * (1 - 1.0 * SUM(churn_flag) / COUNT(*)), 2)         AS retention_rate_pct,
  ROUND(SUM(CASE WHEN churn_flag = 0 THEN monthly_charges END), 2) AS mrr_active,
  ROUND(SUM(revenue_lost_monthly), 2)                              AS monthly_revenue_lost,
  ROUND(AVG(monthly_charges), 2)                                   AS avg_monthly_charges,
  ROUND(AVG(tenure_months), 2)                                     AS avg_tenure_months,
  SUM(high_risk_flag)                                              AS high_risk_customers,
  ROUND(SUM(CASE WHEN high_risk_flag = 1 THEN monthly_charges END), 2) AS monthly_revenue_at_risk
FROM churn_features;

-- @query q01_overall_churn
-- The headline number; every segment is compared against it.
SELECT COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * SUM(churn_flag) / COUNT(*), 2) AS churn_pct
FROM churn_features;

-- @query q02_churn_by_gender
-- A near-zero gap is a legitimate finding: report it as "not a driver".
SELECT gender, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY gender ORDER BY churn_pct DESC;

-- @query q03_churn_by_household
-- Age substitute: the dataset has no age, only Senior Citizen + household fields.
SELECT household_type, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY household_type ORDER BY churn_pct DESC;

-- @query q04_churn_by_city
-- Region substitute (California only). Minimum 30 customers so tiny cities don't top the list by chance.
SELECT city, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY city HAVING COUNT(*) >= 30
ORDER BY churn_pct DESC LIMIT 15;

-- @query q05_churn_by_contract
SELECT contract, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY contract ORDER BY churn_pct DESC;

-- @query q06_churn_by_plan_proxy
-- "Plan" substitute: internet type x number of add-on services.
SELECT internet_service, services_count, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY internet_service, services_count
ORDER BY internet_service, services_count;

-- @query q07_churn_by_payment_method
-- Payment method may just reflect contract type. See q19 before blaming the payment method.
SELECT payment_method, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY payment_method ORDER BY churn_pct DESC;

-- @query q08_churn_by_tenure_group
-- Finds the danger window in a customer's life.
SELECT tenure_group, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY tenure_group ORDER BY MIN(tenure_months);

-- @query q09_churn_by_monthly_charges
-- Price sensitivity. q20 repeats this inside each contract type to separate price from contract.
SELECT charge_group, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct,
       ROUND(AVG(monthly_charges), 2) AS avg_bill
FROM churn_features GROUP BY charge_group ORDER BY MIN(monthly_charges);

-- @query q10_revenue_lost
-- Monthly billing that left. Annualised column assumes lost customers would have stayed 12 months (ASSUMPTION).
SELECT ROUND(SUM(revenue_lost_monthly), 2)                 AS monthly_revenue_lost,
       ROUND(SUM(revenue_lost_monthly) * 12, 2)            AS annualised_assumption,
       ROUND(100.0 * SUM(revenue_lost_monthly) / SUM(monthly_charges), 2) AS pct_of_total_billing
FROM churn_features;

-- @query q11_top_risk_segments
-- Rate AND volume: a high-rate segment with a tiny share of churn is a different priority from a big one.
SELECT contract_category, tenure_group, internet_service,
       COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct,
       ROUND(100.0 * SUM(churn_flag) / (SELECT SUM(churn_flag) FROM churn_features), 2) AS share_of_all_churn
FROM churn_features
GROUP BY contract_category, tenure_group, internet_service
HAVING COUNT(*) >= 50
ORDER BY churn_pct DESC LIMIT 10;

-- @query q12_high_spender_high_risk_callist
-- ACTIVE customers matching the risk profile who are in the top quarter of monthly charges.
SELECT customer_id, city, contract, tenure_months, internet_service, tech_support,
       services_count, monthly_charges, cltv
FROM churn_features
WHERE high_risk_flag = 1 AND high_spender = 1
ORDER BY monthly_charges DESC LIMIT 50;

-- @query q13_retention_by_segment
SELECT contract_category, tenure_group, COUNT(*) AS customers,
       ROUND(100.0 * (1 - AVG(churn_flag)), 2) AS retention_pct
FROM churn_features GROUP BY contract_category, tenure_group
ORDER BY contract_category, MIN(tenure_months);

-- @query q14_lifecycle_churn
-- NO DATE COLUMN in this dataset, so this is churn by months-since-signup (a lifecycle view),
-- NOT a calendar trend. Do not label it "monthly trend".
SELECT ((MAX(tenure_months, 1) - 1) / 6) * 6 + 1   AS months_from,
       ((MAX(tenure_months, 1) - 1) / 6) * 6 + 6   AS months_to,
       COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY months_from ORDER BY months_from;

-- @query q15_churn_reasons
-- Customer-stated reasons (churned customers only). Self-reported: treat as signals.
SELECT churn_reason, COUNT(*) AS churners,
       ROUND(100.0 * COUNT(*) / (SELECT SUM(churn_flag) FROM churn_features), 2) AS pct_of_churners,
       ROUND(SUM(monthly_charges), 2) AS monthly_revenue_lost
FROM churn_features WHERE churn_flag = 1
GROUP BY churn_reason ORDER BY churners DESC LIMIT 10;

-- @query q16_risk_rule_backtest
-- Validates the risk profile on ALL customers: precision (churn rate among matches),
-- capture (share of all churners matched) and lift vs the overall rate.
SELECT risk_profile_match, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct,
       ROUND(100.0 * SUM(churn_flag) / (SELECT SUM(churn_flag) FROM churn_features), 2) AS share_of_all_churners,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM churn_features), 2) AS share_of_customers,
       ROUND(AVG(churn_flag) / (SELECT AVG(churn_flag) FROM churn_features), 2) AS lift_vs_overall
FROM churn_features GROUP BY risk_profile_match;

-- @query q17_revenue_at_risk
SELECT COUNT(*) AS high_risk_customers,
       ROUND(SUM(monthly_charges), 2) AS monthly_revenue_at_risk,
       ROUND(SUM(monthly_charges) * 12, 2) AS annualised_assumption
FROM churn_features WHERE high_risk_flag = 1;

-- @query q18_value_segment_churn
-- Are we losing valuable customers or low-value ones? (CLTV is IBM-modelled.)
SELECT value_segment, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct,
       ROUND(SUM(revenue_lost_monthly), 2) AS monthly_revenue_lost
FROM churn_features GROUP BY value_segment ORDER BY churn_pct DESC;

-- @query q19_payment_by_contract
-- Does payment method still matter once contract type is held fixed?
SELECT contract_category, payment_method, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY contract_category, payment_method
ORDER BY contract_category, churn_pct DESC;

-- @query q20_price_by_contract
-- Does price still matter once contract type is held fixed?
SELECT contract_category, charge_group, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features GROUP BY contract_category, charge_group
ORDER BY contract_category, MIN(monthly_charges);

-- @query q21_support_proxy
-- Tech Support as the support proxy (dataset has no support-call or satisfaction fields).
SELECT internet_service, tech_support, COUNT(*) AS customers, SUM(churn_flag) AS churned,
       ROUND(100.0 * AVG(churn_flag), 2) AS churn_pct
FROM churn_features WHERE internet_service <> 'No'
GROUP BY internet_service, tech_support ORDER BY internet_service, tech_support;
