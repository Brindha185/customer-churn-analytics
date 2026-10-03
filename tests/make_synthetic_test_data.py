"""
make_synthetic_test_data.py
---------------------------
!!! SYNTHETIC DATA - FOR PIPELINE SMOKE-TESTING ONLY !!!
Creates a small random file in the SAME LAYOUT as the IBM Telco file so you can check that
the scripts run on your machine. The values are random. Never report, screenshot or
draw any conclusion from results produced with it.

Used by:  python run_all.py --self-test
"""
import numpy as np
import pandas as pd

RAW_COLUMNS = [
    "CustomerID", "Count", "Country", "State", "City", "Zip Code", "Lat Long", "Latitude",
    "Longitude", "Gender", "Senior Citizen", "Partner", "Dependents", "Tenure Months",
    "Phone Service", "Multiple Lines", "Internet Service", "Online Security", "Online Backup",
    "Device Protection", "Tech Support", "Streaming TV", "Streaming Movies", "Contract",
    "Paperless Billing", "Payment Method", "Monthly Charges", "Total Charges", "Churn Label",
    "Churn Value", "Churn Score", "CLTV", "Churn Reason",
]


def make(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    cities = ["Los Angeles", "San Diego", "San Jose", "Fresno", "Sacramento", "Oakland", "Irvine"]
    internet = rng.choice(["DSL", "Fiber optic", "No"], n, p=[0.35, 0.45, 0.20])
    tenure = rng.integers(0, 73, n)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.25, 0.20])
    monthly = np.round(np.where(internet == "No", rng.uniform(18, 30, n), rng.uniform(40, 115, n)), 2)
    addon_no = np.where(internet == "No", "No internet service", "No")

    def addon():
        return np.where(internet == "No", addon_no, rng.choice(["Yes", "No"], n))

    churn = (rng.random(n) < np.where(contract == "Month-to-month", 0.35, 0.08)).astype(int)
    total = np.round(monthly * tenure * rng.uniform(0.95, 1.05, n), 2).astype(object)
    total[tenure == 0] = " "  # blank text, as in the real file
    df = pd.DataFrame({
        "CustomerID": [f"TEST-{i:05d}" for i in range(n)],
        "Count": 1, "Country": "United States", "State": "California",
        "City": rng.choice(cities, n), "Zip Code": rng.integers(90001, 96162, n),
        "Lat Long": "0,0", "Latitude": 34.0, "Longitude": -118.0,
        "Gender": rng.choice(["Male", "Female"], n),
        "Senior Citizen": rng.choice(["Yes", "No"], n, p=[0.16, 0.84]),
        "Partner": rng.choice(["Yes", "No"], n), "Dependents": rng.choice(["Yes", "No"], n, p=[0.3, 0.7]),
        "Tenure Months": tenure,
        "Phone Service": rng.choice(["Yes", "No"], n, p=[0.9, 0.1]),
        "Multiple Lines": rng.choice(["Yes", "No", "No phone service"], n),
        "Internet Service": internet,
        "Online Security": addon(), "Online Backup": addon(), "Device Protection": addon(),
        "Tech Support": addon(), "Streaming TV": addon(), "Streaming Movies": addon(),
        "Contract": contract, "Paperless Billing": rng.choice(["Yes", "No"], n),
        "Payment Method": rng.choice(["Electronic check", "Mailed check",
                                      "Bank transfer (automatic)", "Credit card (automatic)"], n),
        "Monthly Charges": monthly, "Total Charges": total,
        "Churn Label": np.where(churn == 1, "Yes", "No"), "Churn Value": churn,
        "Churn Score": rng.integers(5, 100, n), "CLTV": rng.integers(2000, 6500, n),
        "Churn Reason": np.where(churn == 1, rng.choice(
            ["Competitor offered more data", "Price too high", "Attitude of support person"], n), None),
    })
    return df[RAW_COLUMNS]


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "synthetic_test.xlsx"
    make().to_excel(out, index=False)
    print("Wrote", out)
