import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# -------------------------------
# STYLING
# -------------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #061A2F, #020C1B);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1F33, #071B2F);
}

.kpi-card {
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 10px;
    color: white;
    font-weight: bold;
}

.total { background: #1F3A93; }
.churn { background: #E74C3C; }
.stayed { background: #2ECC71; }

h1, h2, h3, h4 { color: white; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("European_Bank.csv")
df = df.drop(['CustomerId', 'Surname', 'Year'], axis=1)

df_original = df.copy()

# Encoding
df = pd.get_dummies(df, columns=['Geography', 'Gender'], drop_first=True)

# -------------------------------
# SEGMENTATION
# -------------------------------
df['AgeGroup'] = pd.cut(df['Age'], [18,30,45,60,100],
                        labels=['Young','Adult','MidAge','Senior'])

df['BalanceGroup'] = pd.cut(df['Balance'], [-1,0,100000,200000],
                           labels=['Zero','Low','High'])

df['CreditGroup'] = pd.cut(df['CreditScore'], [300,600,750,900],
                          labels=['Low','Medium','High'])

df['TenureGroup'] = pd.cut(df['Tenure'], [-1,3,7,10],
                          labels=['New','Mid','Long'])

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.title("🔍 Filters")

age_filter = st.sidebar.multiselect("Age Group",
    df['AgeGroup'].dropna().unique(),
    default=df['AgeGroup'].dropna().unique())

balance_filter = st.sidebar.multiselect("Balance Group",
    df['BalanceGroup'].dropna().unique(),
    default=df['BalanceGroup'].dropna().unique())

credit_filter = st.sidebar.multiselect("Credit Group",
    df['CreditGroup'].dropna().unique(),
    default=df['CreditGroup'].dropna().unique())

df_filtered = df[
    (df['AgeGroup'].isin(age_filter)) &
    (df['BalanceGroup'].isin(balance_filter)) &
    (df['CreditGroup'].isin(credit_filter))
]

# -------------------------------
# SIDEBAR KPIs
# -------------------------------
st.sidebar.markdown("### 📊 Dataset Overview")

total_customers = len(df)
churned = int(df['Exited'].sum())
stayed = total_customers - churned

st.sidebar.markdown(f"""
<div class="kpi-card total">Total Customers<br>{total_customers}</div>
<div class="kpi-card churn">Churned Customers<br>{churned}</div>
<div class="kpi-card stayed">Stayed Customers<br>{stayed}</div>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.title("🏦 Customer Churn Dashboard")

# -------------------------------
# KPI TOP
# -------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Overall Churn", f"{df_filtered['Exited'].mean()*100:.2f}%")
col2.metric("High Value Churn",
            f"{df_filtered[df_filtered['Balance']>100000]['Exited'].mean()*100:.2f}%")
col3.metric("Inactive Churn",
            f"{df_filtered[df_filtered['IsActiveMember']==0]['Exited'].mean()*100:.2f}%")

# -------------------------------
# DONUT
# -------------------------------
st.subheader("📊 Churn Distribution")

counts = df_filtered['Exited'].value_counts()

fig = go.Figure(data=[go.Pie(
    labels=["Stayed", "Churned"],
    values=counts.values,
    hole=0.6,
    marker_colors=["#2ECC71","#E74C3C"]
)])

fig.update_layout(paper_bgcolor="#061A2F", font_color="white")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# BAR CHARTS
# -------------------------------
age = df_filtered.groupby('AgeGroup')['Exited'].mean()*100
bal = df_filtered.groupby('BalanceGroup')['Exited'].mean()*100
cred = df_filtered.groupby('CreditGroup')['Exited'].mean()*100
ten = df_filtered.groupby('TenureGroup')['Exited'].mean()*100

c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

# Age
fig1 = px.bar(x=age.index, y=age.values, color=age.index,
              title="📊 Churn by Age Group",
              color_discrete_sequence=["#FF4B4B","#FFC300","#2ECC71","#1F3A93"])
fig1.update_layout(paper_bgcolor="#061A2F", plot_bgcolor="#020C1B", font_color="white")
c1.plotly_chart(fig1, use_container_width=True)

# Balance
fig2 = px.bar(x=bal.index, y=bal.values, color=bal.index,
              title="💰 Churn by Balance Group",
              color_discrete_sequence=["#FF4B4B","#FFC300","#2ECC71"])
fig2.update_layout(paper_bgcolor="#061A2F", plot_bgcolor="#020C1B", font_color="white")
c2.plotly_chart(fig2, use_container_width=True)

# Credit
fig3 = px.bar(x=cred.index, y=cred.values, color=cred.index,
              title="📉 Churn by Credit Score",
              color_discrete_sequence=["#FF4B4B","#FFC300","#2ECC71"])
fig3.update_layout(paper_bgcolor="#061A2F", plot_bgcolor="#020C1B", font_color="white")
c3.plotly_chart(fig3, use_container_width=True)

# Tenure
fig4 = px.bar(x=ten.index, y=ten.values, color=ten.index,
              title="⏳ Churn by Tenure",
              color_discrete_sequence=["#FF4B4B","#FFC300","#2ECC71"])
fig4.update_layout(paper_bgcolor="#061A2F", plot_bgcolor="#020C1B", font_color="white")
c4.plotly_chart(fig4, use_container_width=True)
# -------------------------------
# GRAPH EXPLANATION NOTES
# -------------------------------
st.markdown("## 📘 Graph Explanation (For Clients)")

st.markdown("""
### 📊 Churn by Age Group
- Shows churn percentage across age categories  
- **MidAge customers have the highest churn → key risk segment**  
- Younger customers are more stable  

### 💰 Churn by Balance Group
- Shows churn based on account balance  
- **High balance customers churn more → high financial risk**  
- Zero balance customers have lowest churn  

### 📉 Churn by Credit Score
- Displays churn across credit score segments  
- Lower credit score customers show slightly higher churn  
- Indicates financial reliability impacts retention  

### ⏳ Churn by Tenure
- Shows churn based on how long customer stayed  
- New customers churn slightly more  
- Long-term customers are more stable  

""")

# -------------------------------
# GEOGRAPHY ANALYSIS
# -------------------------------
st.subheader("🌍 Geography Analysis")

geo_col1, geo_col2 = st.columns([2,1])

# Create Geography column back for visualization
df_geo = df_original.copy()

geo_churn = df_geo.groupby('Geography')['Exited'].mean() * 100

fig_geo = px.bar(
    x=geo_churn.index,
    y=geo_churn.values,
    color=geo_churn.index,
    color_discrete_map={
        "France": "#3498DB",
        "Germany": "#9B59B6",
        "Spain": "#E67E22"
    },
    title="Churn by Country"
)

fig_geo.update_layout(
    paper_bgcolor="#061A2F",
    plot_bgcolor="#020C1B",
    font_color="white"
)

geo_col1.plotly_chart(fig_geo, use_container_width=True)


# -------------------------------
# KEY INSIGHTS (Geography section)
# -------------------------------
geo_col2.markdown("""
### 💡 Key Insights

🔴 Mid-age customers have highest churn  
🟡 High-balance customers are risky  
🟢 Inactive users drive churn  
🔵 Geography impacts churn behavior  
""")

# -------------------------------
# DATA PREVIEW
# -------------------------------
st.subheader("📄 Dataset Preview")

rows = st.slider("Select rows", 10, 1000, 50)
st.dataframe(df_filtered.head(rows))

# -------------------------------
# MODEL
# -------------------------------
@st.cache_resource
def train_model(data):
    df_model = data.drop(['AgeGroup','BalanceGroup','CreditGroup','TenureGroup'], axis=1)
    X = df_model.drop('Exited', axis=1)
    y = df_model['Exited']

    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = RandomForestClassifier(class_weight='balanced')
    model.fit(X_train, y_train)
    return model, X.columns

model, feature_cols = train_model(df)

# -------------------------------
# PREDICTION
# -------------------------------
st.subheader("🤖 Predict Customer Churn")

st.markdown("""
- NumOfProducts → number of bank services  
- ActiveMember → 1=Yes, 0=No  
- HasCrCard → 1=Yes, 0=No  
""")

col1, col2 = st.columns(2)

with col1:
    age_val = st.slider("Age", 18, 80, 30)
    credit = st.slider("Credit Score", 300, 900, 600)
    balance_val = st.number_input("Balance", value=50000)
    salary = st.number_input("Estimated Salary", value=100000)

with col2:
    tenure = st.slider("Tenure", 0, 10, 3)
    products = st.selectbox("Products", [1,2,3,4])
    active = st.selectbox("Active Member", [1,0])
    card = st.selectbox("Has Credit Card", [1,0])

geo = st.selectbox("Geography", ["France","Spain","Germany"])
geo_spain = 1 if geo=="Spain" else 0
geo_germany = 1 if geo=="Germany" else 0

gender = st.selectbox("Gender", ["Male","Female"])
gender_male = 1 if gender=="Male" else 0

if st.button("Predict"):

    input_df = pd.DataFrame([[credit, age_val, tenure, balance_val,
                              products, card, active, salary,
                              geo_germany, geo_spain, gender_male]],
                            columns=feature_cols)

    prob = model.predict_proba(input_df)[0][1]

    st.markdown(f"## 🎯 Prediction Result: {prob*100:.2f}%")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob*100,
        gauge={
            'axis': {'range':[0,100]},
            'steps':[
                {'range':[0,30],'color':'#2ECC71'},
                {'range':[30,60],'color':'#F1C40F'},
                {'range':[60,100],'color':'#E74C3C'}
            ]
        }
    ))

    fig.update_layout(paper_bgcolor="#061A2F", font_color="white")
    st.plotly_chart(fig)

    if prob > 0.6:
        st.error("High Risk Customer")
    elif prob > 0.3:
        st.warning("Medium Risk Customer")
    else:
        st.success("Low Risk Customer" )