-- 00_cleaning_reference_postgres.sql
-- REFERENCE ONLY (not executed by run_all.py). Shows the same cleaning in SQL, PostgreSQL syntax,
-- for readers who load the raw file into a database instead of using python/data_cleaning.py.
-- Assumes you imported the raw sheet into churn_raw with every column as TEXT and snake_case names.

CREATE TABLE churn_clean AS
SELECT
  customerid                                           AS customer_id,
  city,
  CAST(zip_code AS VARCHAR(10))                        AS zip_code,
  CAST(latitude AS DECIMAL(9,6))                       AS latitude,
  CAST(longitude AS DECIMAL(9,6))                      AS longitude,
  gender, senior_citizen, partner, dependents,
  CAST(tenure_months AS INT)                           AS tenure_months,
  phone_service,
  CASE WHEN multiple_lines     LIKE 'No %' THEN 'No' ELSE multiple_lines     END AS multiple_lines,
  internet_service,
  CASE WHEN online_security    LIKE 'No %' THEN 'No' ELSE online_security    END AS online_security,
  CASE WHEN online_backup      LIKE 'No %' THEN 'No' ELSE online_backup      END AS online_backup,
  CASE WHEN device_protection  LIKE 'No %' THEN 'No' ELSE device_protection  END AS device_protection,
  CASE WHEN tech_support       LIKE 'No %' THEN 'No' ELSE tech_support       END AS tech_support,
  CASE WHEN streaming_tv       LIKE 'No %' THEN 'No' ELSE streaming_tv       END AS streaming_tv,
  CASE WHEN streaming_movies   LIKE 'No %' THEN 'No' ELSE streaming_movies   END AS streaming_movies,
  contract, paperless_billing, payment_method,
  CAST(monthly_charges AS DECIMAL(8,2))                AS monthly_charges,
  CASE WHEN TRIM(total_charges) = '' THEN 0 ELSE CAST(total_charges AS DECIMAL(10,2)) END AS total_charges,
  CAST(churn_value AS INT)                             AS churn_flag,
  CAST(churn_score AS INT)                             AS churn_score,
  CAST(cltv AS INT)                                    AS cltv,
  NULLIF(TRIM(churn_reason), '')                       AS churn_reason
FROM (SELECT DISTINCT ON (customerid) * FROM churn_raw ORDER BY customerid) d;

-- Quality checks
SELECT COUNT(*) AS rows_total, COUNT(DISTINCT customer_id) AS unique_ids FROM churn_clean;
SELECT COUNT(*) FROM churn_clean WHERE tenure_months = 0;
SELECT COUNT(*) FROM churn_clean WHERE tenure_months > 0 AND total_charges < monthly_charges * 0.5;
SELECT contract, COUNT(*) FROM churn_clean GROUP BY contract;
SELECT MIN(monthly_charges), MAX(monthly_charges), MIN(tenure_months), MAX(tenure_months) FROM churn_clean;
