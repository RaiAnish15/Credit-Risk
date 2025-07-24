
# 📊 Credit Risk Segment Dashboard

This Streamlit dashboard estimates the probability of loan default based on a person's **income** and **credit grade** using real historical loan data.

---

## 🔍 Overview

- Accepts user input: `Annual Income` and `Credit Grade (A–G)`
- Uses pre-segmented historical data to classify:
  - **Income Segment**: very low, low, medium, high
  - **Grade Risk Level**: risky, medium, safe
- Displays:
  - Risk Segment tag (e.g., 🔴 Very High Risk)
  - Estimated Probability of Default (empirical)
- Helpful for:
  - Pre-loan screening
  - Risk profiling
  - Educational and financial analytics

---

## 📁 Folder Structure

```
credit-risk-segment-dashboard/
│
├── credit_risk_sample.csv       # Cleaned CSV (Filtered from LendingClub)
├── dashboard_app.py             # Streamlit app code
├── requirements.txt             # Python dependencies
└── README.md                    # Project info
```

---

## 🧼 Data Source & Processing

### 📦 Source:
The dataset is a **filtered sample** of LendingClub loan data (publicly available via Kaggle or open data portals).

- Original Dataset: [LendingClub Loan Data](https://www.kaggle.com/datasets/wendykan/lending-club-loan-data)
- Filtered to include:
  - Only `loan_status` as `Fully Paid` or `Charged Off`
  - Removed missing `emp_length`
  - Created `default` = 1 (Charged Off), 0 (Fully Paid)
  - Parsed `emp_length` into numerical form
  - Segmented income into 4 quantile-based bins
  - Classified grades by historical default rate


## 🤝 License

This project is for educational purposes. Attribution to [LendingClub](https://www.lendingclub.com/info/statistics.action) for the data.

---
