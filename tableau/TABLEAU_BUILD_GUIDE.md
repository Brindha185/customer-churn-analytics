# Tableau Build Guide - 3 dashboards

Prerequisite: run `python run_all.py` successfully. Connect to **data/cleaned/churn_clean_tableau.csv**.
Create every field in `calculated_fields.md` first. Tableau Public (free) or Desktop both work.
(If you use Tableau Public, check whether your version saves a local .twbx; anything you publish is public,
which is fine for a public sample dataset.)

## 0. Setup checklist
1. Connect > Text file > churn_clean_tableau.csv.
2. In the data pane make sure: Churn Flag, Tenure Months, Monthly Charges, Total Charges, Churn Score, CLTV, Latitude, Longitude
   are numeric; everything else is a string. Zip Code -> string (dimension).
3. Create all calculated fields. Reconcile KPIs against q00_kpi_summary.csv.
4. Set default number formats on the calculated fields (percent / currency).
5. **Drivers sheet only (Dashboard 3):** add the CSV a *second time* as a separate data source named "Drivers (pivoted)" and
   pivot there (details in section 3). Never use the pivoted source for other sheets: pivoting multiplies rows.

## 1. Design system (apply to all three)
- Fixed dashboard size **1200 x 800 px**. Background white; sheet backgrounds none.
- Colours: neutral grey for base bars (#A6A6A6 or #BFBFBF); **one accent red (#C0392B) = churn / risk**; blue (#2E75B6) = retained / neutral categories.
- Diverging colour for "Churn Rate vs Overall": blue (below average) - white - red (above average), centred on 0.
- Fonts: one family (Tableau default or Arial); titles 14 pt bold, labels 9-10 pt, KPI numbers 24 pt bold.
- Remove gridlines, axis rulers, zero lines, borders, and any legend that direct labels can replace.
- Sort bars descending (categories with natural order - tenure, charge band - keep natural order).
- Always show customer counts beside rates (label or tooltip) so small segments are not misread.
- Every segment chart gets a dashed reference line: **Overall Churn Rate**.
- Tooltips: segment name, Customers, Churned, Churn Rate, Revenue Lost (Monthly), Share of All Churn - nothing else.
- Navigation: three Navigation buttons (Overview / Segmentation / Risk) at the same top-right position on every dashboard.
- Filters (max 4, apply to all worksheets on that dashboard): Contract, Internet Service, Senior Citizen, (Tenure Group on page 2).

## 2. Dashboard 1 - Executive Overview

Layout (1200 x 800): title row (60 px) -> KPI strip (100 px) -> 2 rows of charts (about 290 px each) -> footer note.

| Sheet name | Chart | Columns / Rows | Marks / filters | Insight |
|---|---|---|---|---|
| D1 KPI Total Customers | Text | Total Customers | 24 pt number, small label | Scale |
| D1 KPI Churn Rate | Text | Churn Rate | red | Headline metric |
| D1 KPI Retention Rate | Text | Retention Rate | blue | Positive framing |
| D1 KPI Revenue Lost | Text | Revenue Lost (Monthly) | red; add Annualised in tooltip | Churn in money |
| D1 KPI Active | Text | Active Customers | | Base to protect |
| D1 Churn by Contract | Horizontal bar | Rows: Contract. Columns: Churn Rate | Reference line = Overall Churn Rate; label = Churn Rate and Total Customers | Does commitment matter? |
| D1 Lifecycle | Line or column | Columns: Lifecycle Bucket Start (discrete). Rows: Churn Rate | Title "Churn by months since signup (lifecycle view)". **No calendar dates exist - never call this a trend.** | Where in the customer lifecycle churn concentrates |
| D1 Churn by City | Horizontal bar | Rows: City. Columns: Churn Rate | Filter: Total Customers >= 30 (filter on COUNTD CustomerID, set "Top 15 by Churn Rate") | Is geography a real signal or noise? Optional: symbol map using Latitude/Longitude |

## 3. Dashboard 2 - Customer Segmentation

| Sheet name | Chart | Fields | Notes | Insight |
|---|---|---|---|---|
| D2 Household | Bar | Rows: Household Type. Columns: Churn Rate | Ref line = Overall | Age-proxy differences |
| D2 Tenure | Column | Columns: Tenure Group (natural order). Rows: Churn Rate | Add Total Customers as label | The danger window |
| D2 Plan Proxy | Heatmap (highlight table) | Rows: Internet Service. Columns: Services Count. Colour: Churn Rate. Label: Total Customers | | Does churn fall with more add-ons? |
| D2 Payment Method | Bar | Rows: Payment Method. Columns: Churn Rate. Colour: Contract Category (optional) | Compare with and without Contract Category before drawing conclusions | Payment method effect beyond contract |
| D2 Customer Value | Bar | Rows: Value Segment (Low, Mid, High). Columns: Churn Rate; second sheet/label: Revenue Lost (Monthly) | | Losing valuable or low-value customers? |
| D2 Segment Matrix | Highlight table | Rows: Contract Category. Columns: Tenure Group. Colour: Churn Rate. Label: Total Customers | Colour scale white -> red | Hotspots where two factors combine |

## 4. Dashboard 3 - Retention & Risk

| Sheet name | Chart | Fields | Notes | Insight |
|---|---|---|---|---|
| D3 Top Risk Segments | Bar (top 10) | Rows: Contract Category + Tenure Group + Internet Service (combined field or hierarchy). Columns: Churn Rate. Size/label: Churned Customers | Filter: Total Customers >= 50 | Priority segments by rate AND volume |
| D3 Revenue at Risk | Bar | Rows: Customer Risk Segment. Columns: Revenue at Risk (Monthly) or MRR | | How much money the campaign protects |
| D3 Risk Distribution | Stacked bar (100%) | Rows: Contract Category. Columns: Number of Records. Colour: Customer Risk Segment | | Size of each risk tier |
| D3 Rule Quality | Text card | Risk Profile Precision, Risk Profile Capture, Overall Churn Rate | | "How good is the rule?" - be honest if lift is small |
| D3 Churn Reasons | Horizontal bar (top 10) | Rows: Churn Reason (filter Churn Flag = 1). Columns: Churned Customers | | Customer-stated causes (self-reported) |
| D3 Churn Drivers | Horizontal bar | see below | | Which attribute values deviate most from average |
| D3 Actions | Text box | 3-4 recommendations, written AFTER you have findings (docs/recommendations_template.md) | | Decision-ready close |

### Churn drivers sheet (no machine learning)
1. Add `churn_clean_tableau.csv` again as a **second data source** ("Drivers (pivoted)").
2. In the Data Source tab, select these columns (Ctrl-click): Contract, Internet Service, Payment Method, Paperless Billing,
   Tech Support, Online Security, Online Backup, Device Protection, Streaming TV, Streaming Movies, Senior Citizen, Partner, Dependents.
   Right-click > **Pivot**.
3. You now have **Pivot Field Names** (e.g. Contract) and **Pivot Field Values** (e.g. Month-to-month).
4. Recreate in this source: `Churn Rate` (SUM([Churn Flag]) / COUNTD([CustomerID]) - correct when grouped by
   Pivot Field Names + Pivot Field Values, because each customer appears once per field), `Total Customers`, and
   `Overall Churn Rate` as **{ FIXED : AVG([Churn Flag]) }** (AVG is correct here because every customer is duplicated
   the same number of times; the usual SUM/COUNTD version would be wrong in this pivoted source). Then
   `Churn Rate vs Overall` = [Churn Rate] - [Overall Churn Rate].
5. Build: Rows = Pivot Field Names + Pivot Field Values. Columns = Churn Rate vs Overall. Filter: Total Customers >= 100.
   Sort descending, diverging colour. Title: "Attribute values with the biggest gap vs average churn".
6. Read this as "associated with", never "caused by": attribute values overlap (month-to-month customers are often also
   on fiber, and so on).

## 5. Assembling each dashboard
1. New Dashboard > Size: Fixed 1200 x 800.
2. Drag a Vertical layout container; add a title text box (project name + one-line subtitle, e.g.
   "Customer Churn & Retention - Executive Overview").
3. Add the KPI sheets in a Horizontal container (equal widths), then the charts in two horizontal rows.
4. Show filters: right-click a chart > Filters > select Contract, Internet Service, Senior Citizen; apply to "All Using This Data Source".
5. Add Navigation buttons (Objects > Navigation) pointing to the other dashboards.
6. Add a small footer text: "Source: IBM Telco Customer Churn sample dataset (fictional). Single snapshot; no calendar dates."
7. Hide sheet titles you don't need; keep chart titles as questions or takeaways.
8. Test: filter Contract = Month-to-month and check numbers against SQL (q05 / q11).

## 6. Export for the README
File > Export Image for each dashboard -> `screenshots/dashboard_1_executive.png`, `dashboard_2_segmentation.png`,
`dashboard_3_risk.png`. Save the workbook as `tableau/customer_churn_dashboard.twbx`.
