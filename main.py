import pandas as pd
import streamlit as st

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("credit_risk_sample.csv")
    df = df[df['loan_status'].isin(['Fully Paid', 'Charged Off'])].dropna(subset=['emp_length'])
    df['default'] = df['loan_status'].apply(lambda x: 1 if x == 'Charged Off' else 0)

    def parse_emp_length(val):
        if val == '10+ years':
            return 10
        if val == '< 1 year':
            return 0.5
        try:
            return float(val.strip().split()[0])
        except:
            return None

    df['emp_length_clean'] = df['emp_length'].apply(parse_emp_length)

    # Add risk segments
    q1_income = df['annual_inc'].quantile(0.25)
    df['is_low_income'] = df['annual_inc'] < q1_income

    grade_defaults = df.groupby('grade')['default'].mean()
    median_default = grade_defaults.median()
    high_risk_grades = grade_defaults[grade_defaults > median_default].index.tolist()
    df['is_high_risk_grade'] = df['grade'].isin(high_risk_grades)

    return df, q1_income, high_risk_grades, grade_defaults

# Load processed data
df, q1_income, high_risk_grades, grade_defaults = load_data()

# Title
st.title("🔍 Credit Risk Default Predictor")
st.markdown("Estimate the default probability based on income and credit grade.")

# Input form
st.subheader("📥 Enter Applicant Details")
income_input = st.number_input("Annual Income (₹)", min_value=10000, max_value=500000, step=1000)
grade_input = st.selectbox("Credit Grade", sorted(df['grade'].unique()))

# Display segment info
is_low_income = income_input < q1_income
is_high_risk_grade = grade_input in high_risk_grades

# Default probability
if is_low_income and is_high_risk_grade:
    prob = df[(df['is_low_income']) & (df['is_high_risk_grade'])]['default'].mean()
    risk_level = "🔴 High Risk"
elif is_low_income:
    prob = df[df['is_low_income']]['default'].mean()
    risk_level = "🟠 Medium Risk (Low Income)"
elif is_high_risk_grade:
    prob = df[df['is_high_risk_grade']]['default'].mean()
    risk_level = "🟠 Medium Risk (Weak Grade)"
else:
    prob = df[(~df['is_low_income']) & (~df['is_high_risk_grade'])]['default'].mean()
    risk_level = "🟢 Low Risk"

st.markdown(f"### 🔮 Estimated Probability of Default: `{prob:.2%}`")
st.markdown(f"### 📉 Risk Segment: **{risk_level}**")

# Show reference stats
st.subheader("📊 Reference: Default Rates by Grade")
st.dataframe(grade_defaults.round(4).rename("P(Default)"))

