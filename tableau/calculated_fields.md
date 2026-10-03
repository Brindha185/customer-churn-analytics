# Tableau Calculated Fields (copy-paste)

Connect Tableau to `data/cleaned/churn_clean_tableau.csv`. Its headers are Title Case so these field names match exactly:
CustomerID, City, Zip Code, Latitude, Longitude, Gender, Senior Citizen, Partner, Dependents, Tenure Months,
Phone Service, Multiple Lines, Internet Service, Online Security, Online Backup, Device Protection, Tech Support,
Streaming TV, Streaming Movies, Contract, Paperless Billing, Payment Method, Monthly Charges, Total Charges,
Churn Flag, Churn Score, CLTV, Churn Reason.

Create via Analysis > Create Calculated Field. Keep names EXACTLY as below (the guide refers to them).
Labels (e.g. "0-6 mo") match SQL and Excel so all three tools tie out.

## Core KPIs
```
Total Customers          COUNTD([CustomerID])
Churned Customers        SUM([Churn Flag])
Active Customers         COUNTD([CustomerID]) - SUM([Churn Flag])
Churn Rate               SUM([Churn Flag]) / COUNTD([CustomerID])
Retention Rate           1 - [Churn Rate]
MRR (Active)             SUM(IF [Churn Flag] = 0 THEN [Monthly Charges] END)
Revenue Lost (Monthly)   SUM(IF [Churn Flag] = 1 THEN [Monthly Charges] END)
Revenue Lost (Annualised, assumption)   [Revenue Lost (Monthly)] * 12
Avg Monthly Charges      AVG([Monthly Charges])
Avg Tenure (Months)      AVG([Tenure Months])
```
Format: Churn Rate / Retention Rate as Percentage (1 decimal); revenue fields as Currency (0 decimals).
Use: KPI cards on Dashboard 1.

## Benchmarks and shares
```
Overall Churn Rate       { FIXED : SUM([Churn Flag]) / COUNTD([CustomerID]) }
Churn Rate vs Overall    [Churn Rate] - [Overall Churn Rate]
Share of All Churn       SUM([Churn Flag]) / TOTAL(SUM([Churn Flag]))
```
Use: Overall Churn Rate as a reference line on every segment chart; Churn Rate vs Overall as bar colour (diverging);
Share of All Churn in tooltips and the segment table.

## Segments
```
Tenure Group
IF [Tenure Months] <= 6 THEN '0-6 mo'
ELSEIF [Tenure Months] <= 12 THEN '7-12 mo'
ELSEIF [Tenure Months] <= 24 THEN '13-24 mo'
ELSEIF [Tenure Months] <= 48 THEN '25-48 mo'
ELSE '49-72 mo' END

Charge Group
IF [Monthly Charges] < 35 THEN 'Under 35'
ELSEIF [Monthly Charges] < 70 THEN '35 to 69.99'
ELSEIF [Monthly Charges] < 90 THEN '70 to 89.99'
ELSE '90 and above' END

Household Type
IF [Senior Citizen] = 'Yes' THEN 'Senior'
ELSEIF [Dependents] = 'Yes' THEN 'Non-senior with dependents'
ELSEIF [Partner] = 'Yes' THEN 'Non-senior with partner'
ELSE 'Non-senior single' END

Contract Category
IF [Contract] = 'Month-to-month' THEN 'Month-to-month' ELSE 'Long-term' END

Services Count
(IF [Online Security] = 'Yes' THEN 1 ELSE 0 END)
+ (IF [Online Backup] = 'Yes' THEN 1 ELSE 0 END)
+ (IF [Device Protection] = 'Yes' THEN 1 ELSE 0 END)
+ (IF [Tech Support] = 'Yes' THEN 1 ELSE 0 END)
+ (IF [Streaming TV] = 'Yes' THEN 1 ELSE 0 END)
+ (IF [Streaming Movies] = 'Yes' THEN 1 ELSE 0 END)

Value Segment    (CLTV quartiles)
IF [CLTV] <= { FIXED : PERCENTILE([CLTV], 0.25) } THEN 'Low'
ELSEIF [CLTV] >= { FIXED : PERCENTILE([CLTV], 0.75) } THEN 'High'
ELSE 'Mid' END

Lifecycle Bucket Start   (6-month buckets)
INT((MAX([Tenure Months], 1) - 1) / 6) * 6 + 1
```
Note: Tableau's `MAX(a, b)` with two arguments is a row-level function, so the Lifecycle formula above works as written.
Use "Lifecycle Bucket Start" as a dimension (convert to Discrete) on the lifecycle chart.

## Risk (rule v1 - an ASSUMPTION; back-test it, then revise)
```
Risk Profile Match
IF [Contract] = 'Month-to-month' AND [Tenure Months] <= 12
   AND [Internet Service] <> 'No' AND [Tech Support] = 'No'
THEN 1 ELSE 0 END

High Risk Flag
IF [Churn Flag] = 0 AND [Risk Profile Match] = 1 THEN 1 ELSE 0 END

Customer Risk Segment
IF [Churn Flag] = 1 THEN 'Churned'
ELSEIF [High Risk Flag] = 1 THEN 'High risk'
ELSEIF [Contract] = 'Month-to-month' THEN 'Watch'
ELSE 'Stable' END

High-Risk Customers      SUM([High Risk Flag])
Revenue at Risk (Monthly)   SUM(IF [High Risk Flag] = 1 THEN [Monthly Charges] END)
Risk Profile Precision   SUM(IF [Risk Profile Match] = 1 THEN [Churn Flag] END) / SUM([Risk Profile Match])
Risk Profile Capture     SUM(IF [Risk Profile Match] = 1 THEN [Churn Flag] END) / SUM([Churn Flag])
```
Use: Dashboard 3. Precision and Capture go in a small "How good is the rule?" text card.
Back-test first: Precision should be clearly above Overall Churn Rate (lift > 1). If it isn't, change the rule
in SQL, Excel AND Tableau together.

## Reconciliation (do this before building charts)
Put Total Customers, Churned Customers, Churn Rate, MRR (Active), Revenue Lost (Monthly), High-Risk Customers
in one text table and compare with `outputs/sql_results/q00_kpi_summary.csv`. They must match.
