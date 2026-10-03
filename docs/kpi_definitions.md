# KPI Definitions

Single snapshot: "churn rate" = churned customers / all customers in the file. It is not a month-over-month rate.

| KPI | Formula | Business meaning | Why management cares |
|---|---|---|---|
| Total Customers | COUNT(customer_id) | Customers observed in the period | Scale; denominator of every rate |
| Active Customers | COUNT(churn_flag = 0) | Customers still paying | Current base to protect |
| Churned Customers | COUNT(churn_flag = 1) | Customers lost | Size of the problem |
| Overall Churn Rate | Churned / Total | Share of customers lost | Headline health metric; benchmark for every segment |
| Retention Rate | 1 - Churn Rate | Share kept | Positive framing for executives |
| Monthly Recurring Revenue (MRR) | SUM(monthly_charges) where active | Recurring revenue now | The revenue base to protect |
| Revenue Lost from Churn | SUM(monthly_charges) where churned (monthly); x12 for annualised (ASSUMPTION) | Recurring revenue that left | Turns churn into a budget argument |
| Average Monthly Charges | AVG(monthly_charges), shown active vs churned | Typical bill | Do high-bill customers leave more? |
| Average Customer Tenure | AVG(tenure_months), shown active vs churned | Typical relationship length | A short churned-customer tenure points to early-life risk |
| High-Risk Customers | COUNT(high_risk_flag = 1) | Active customers matching the risk profile | Size of the retention campaign |
| Revenue at Risk | SUM(monthly_charges) where high_risk_flag = 1 | Monthly revenue exposed to the next wave | Prioritisation and campaign budget |
| Risk Profile Precision | Churn rate among ALL customers matching the profile | How accurate the rule is | If close to the overall rate, the rule is useless |
| Risk Profile Capture | Churners matching the profile / all churners | How much churn the rule covers | Coverage of the retention programme |
