# Raw data - download it yourself

The real dataset is NOT included in this project (no network access when this was built, and the license
should be checked before redistributing).

1. Open https://www.kaggle.com/datasets/yeanzc/telco-customer-churn-ibm-dataset
2. Download `Telco_customer_churn.xlsx` (7,043 rows, 33 columns; IBM Cognos Analytics sample data).
   Original IBM write-up: https://community.ibm.com/community/user/businessanalytics/blogs/steven-macko/2019/07/11/telco-customer-churn-1113
3. Save it in this folder as exactly: `data/raw/Telco_customer_churn.xlsx`
4. Run `python run_all.py` from the project root.

A Kaggle account is free. The file is fictional sample data (a telco in California, Q3).
If the file name differs, either rename it or run `python python/data_cleaning.py path/to/file.xlsx`
for the cleaning step only.
