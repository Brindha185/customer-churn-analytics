# Business Insights - hypotheses to test, then write up

No numbers are pre-filled. Run `python run_all.py`, open `outputs/sql_results/`, and fill in ONLY what the data shows.
If a hypothesis fails, report that - "gender is not a driver" or "payment method disappears once contract is controlled" are good findings.

Always: report the customer count next to each rate, and check whether one factor is just a stand-in for another.

## Hypotheses

| # | Hypothesis | Test with (outputs/sql_results/...) | Supported if... | Result (fill in) |
|---|---|---|---|---|
| 1 | Month-to-month customers churn more than 1- or 2-year customers | q05_churn_by_contract | Large gap on adequate counts | |
| 2 | Churn is highest early in the customer lifecycle | q08_churn_by_tenure_group, q14_lifecycle_churn | Early groups sit well above overall churn | |
| 3 | Higher monthly charges go with higher churn | q09, then q20_price_by_contract | Rate rises across bands AND survives within a contract type | |
| 4 | One internet service type (e.g. fiber) churns more than another | q06_churn_by_plan_proxy | Gap persists within the same contract/tenure | |
| 5 | Customers with Tech Support / more add-ons churn less | q21_support_proxy, q06 | Rate falls as add-ons rise | |
| 6 | A payment method is associated with higher churn | q07, then q19_payment_by_contract | Gap persists after controlling for contract | |
| 7 | Seniors / households without partner or dependents churn more | q03_churn_by_household | Clear gap on adequate counts | |
| 8 | Gender is not a meaningful driver | q02_churn_by_gender | Small gap | |
| 9 | Churn is concentrated in a few segments that hold a large share of all churn | q11_top_risk_segments | Top segments account for a big share_of_all_churn | |
| 10 | Stated reasons are dominated by price / competitor / support issues | q15_churn_reasons | These top the list | |
| 11 | The high-risk profile identifies churners better than chance | q16_risk_rule_backtest | lift_vs_overall clearly above 1 and share_of_all_churners meaningful | |
| 12 | Churned customers skew toward high- or low-value segments | q18_value_segment_churn | Revenue lost share differs from customer share | |

## Write-up template (one per confirmed insight; aim for 8-12 total)

**Finding:** [one sentence, e.g. "Customers on X churn more than customers on Y."]
**Evidence:** [rates for X vs Y with customer counts, share of all churn, source query]
**Business implication:** [what it means for revenue, acquisition cost, or product]
**Recommended action:** [specific, testable action, owner, success metric]
**Caveat:** [confounding, small sample, modelled fields, observational data]
