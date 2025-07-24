import pandas as pd
import streamlit as st

# === Data Load and Processing ===
@st.cache_data
def load_data():
    df = pd.read_csv("credit_risk_sample.csv")
    df = df[df['loan_status'].isin(['Fully Paid', 'Charged Off'])].dropna(subset=['emp_length'])
    df['default'] = df['loan_status'].apply(lambda x: 1 if x == 'Charged Off' else 0)

    def parse_emp_length(val):
        if val == '10+ years': return 10
        if val == '< 1 year': return 0.5
        try:
            return float(val.strip().split()[0])
        except:
            return None
    df['emp_length_clean'] = df['emp_length'].apply(parse_emp_length)

    # Income Segmentation
    q1, q2, q3 = df['annual_inc'].quantile([0.25, 0.5, 0.75])
    def income_segment(inc):
        if inc < q1: return 'very_low'
        elif inc < q2: return 'low'
        elif inc < q3: return 'medium'
        else: return 'high'
    df['income_segment'] = df['annual_inc'].apply(income_segment)

    # Grade Risk Mapping
    grade_defaults = df.groupby('grade')['default'].mean()
    sorted_grades = sorted(grade_defaults.items(), key=lambda x: x[1])
    safe_grades = [g for g, _ in sorted_grades[:2]]
    risky_grades = [g for g, _ in sorted_grades[-3:]]
    def grade_risk(g):
        if g in safe_grades: return 'safe'
        elif g in risky_grades: return 'risky'
        else: return 'medium'
    df['grade_risk'] = df['grade'].apply(grade_risk)

    # Segment label
    def risk_label(inc_seg, grade_risk):
        mapping = {
            ('very_low', 'risky'): '🔴 Very High Risk',
            ('very_low', 'medium'): '🔴 High Risk',
            ('very_low', 'safe'): '🟠 Elevated Risk',
            ('low', 'risky'): '🔴 High Risk',
            ('low', 'medium'): '🟠 Medium-High Risk',
            ('low', 'safe'): '🟡 Moderate Risk',
            ('medium', 'risky'): '🟠 Medium Risk',
            ('medium', 'medium'): '🟡 Low-Medium Risk',
            ('medium', 'safe'): '🟢 Low Risk',
            ('high', 'risky'): '🟡 Borderline Risk',
            ('high', 'medium'): '🟢 Low Risk',
            ('high', 'safe'): '🟢 Very Low Risk'
        }
        return mapping.get((inc_seg, grade_risk), "Unknown")
    df['risk_segment'] = df.apply(lambda row: risk_label(row['income_segment'], row['grade_risk']), axis=1)

    return df, grade_defaults, q1, q2, q3, safe_grades, risky_grades

# === Load Data ===
df, grade_defaults, q1, q2, q3, safe_grades, risky_grades = load_data()

# === Streamlit UI ===
st.title("📊 Credit Risk Segment Estimator")
st.markdown("Estimate the default risk based on income and credit grade using realistic segmentation.")

# Income input
income_input = st.slider("💰 Annual Income (₹)", 
                         int(df['annual_inc'].min()), 
                         int(df['annual_inc'].max()), 
                         step=1000)

# Grade input
grade_input = st.select_slider("📈 Credit Grade", options=sorted(df['grade'].unique()))

# Segment functions
def get_income_segment(inc):
    if inc < q1: return 'very_low'
    elif inc < q2: return 'low'
    elif inc < q3: return 'medium'
    else: return 'high'

def get_grade_risk(g):
    if g in safe_grades: return 'safe'
    elif g in risky_grades: return 'risky'
    else: return 'medium'

def get_risk_label(inc_seg, grade_risk):
    mapping = {
        ('very_low', 'risky'): '🔴 Very High Risk',
        ('very_low', 'medium'): '🔴 High Risk',
        ('very_low', 'safe'): '🟠 Elevated Risk',
        ('low', 'risky'): '🔴 High Risk',
        ('low', 'medium'): '🟠 Medium-High Risk',
        ('low', 'safe'): '🟡 Moderate Risk',
        ('medium', 'risky'): '🟠 Medium Risk',
        ('medium', 'medium'): '🟡 Low-Medium Risk',
        ('medium', 'safe'): '🟢 Low Risk',
        ('high', 'risky'): '🟡 Borderline Risk',
        ('high', 'medium'): '🟢 Low Risk',
        ('high', 'safe'): '🟢 Very Low Risk'
    }
    return mapping.get((inc_seg, grade_risk), "Unknown")

# Segment identification
inc_seg = get_income_segment(income_input)
grade_risk_level = get_grade_risk(grade_input)
segment_label = get_risk_label(inc_seg, grade_risk_level)

# Calculate probability
subset = df[(df['income_segment'] == inc_seg) & (df['grade_risk'] == grade_risk_level)]
prob = subset['default'].mean() if not subset.empty else None

# Output
st.markdown(f"### 🧮 Income Segment: `{inc_seg.upper()}`")
st.markdown(f"### 🛡️ Grade Risk Level: `{grade_risk_level.upper()}`")
st.markdown(f"### 🚨 Risk Segment: **{segment_label}**")

if prob is not None:
    st.markdown(f"### 🔮 Estimated Probability of Default: `{prob:.2%}`")
else:
    st.warning("⚠️ Not enough data to estimate this combination. Try adjusting the inputs.")

# Reference table
st.subheader("📊 Default Rate by Credit Grade")
st.dataframe(grade_defaults.round(4).rename("P(Default)"))
