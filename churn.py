import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# -------------------------------
# GLOBAL STYLE
# -------------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #061A2F, #020C1B);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1F33, #071B2F);
}
.card {
    background: #0E2238;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 0px 15px rgba(0,150,255,0.2);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("European_Bank.csv")

df = df.drop(['CustomerId', 'Surname', 'Year'], axis=1)

# Keep original for geography
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

age_filter = st.sidebar.multiselect(
    "Age Group", df['AgeGroup'].dropna().unique(),
    default=df['AgeGroup'].dropna().unique()
)

balance_filter = st.sidebar.multiselect(
    "Balance Group", df['BalanceGroup'].dropna().unique(),
    default=df['BalanceGroup'].dropna().unique()
)

credit_filter = st.sidebar.multiselect(
    "Credit Group", df['CreditGroup'].dropna().unique(),
    default=df['CreditGroup'].dropna().unique()
)

df_filtered = df[
    (df['AgeGroup'].isin(age_filter)) &
    (df['BalanceGroup'].isin(balance_filter)) &
    (df['CreditGroup'].isin(credit_filter))
]

# -------------------------------
# SIDEBAR DATASET OVERVIEW (FIXED)
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dataset Overview")

total_customers = len(df)
churned_customers = df['Exited'].sum()
churn_rate = df['Exited'].mean() * 100

st.sidebar.markdown(f"""
<div style="
    background-color:#081829;
    padding:15px;
    border-radius:10px;
    box-shadow:0px 0px 10px rgba(0,150,255,0.2);
">
    <p style="color:#A0B3C6;">Total Customers</p>
    <h2 style="color:white;">{total_customers}</h2>

    <p style="color:#A0B3C6;">Churned</p>
    <h2 style="color:white;">{churned_customers}</h2>

    <p style="color:#A0B3C6;">Churn %</p>
    <h2 style="color:#2ECC71;">{churn_rate:.2f}%</h2>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# TITLE
# -------------------------------
st.title("🏦 Customer Churn Dashboard")

# -------------------------------
# KPI CARDS
# -------------------------------
overall = df_filtered['Exited'].mean()*100
high_value = df_filtered[df_filtered['Balance'] > 100000]['Exited'].mean()*100
inactive = df_filtered[df_filtered['IsActiveMember'] == 0]['Exited'].mean()*100

c1, c2, c3 = st.columns(3)

c1.markdown(f"<div class='card'><h4>Overall Churn</h4><h2>{overall:.2f}%</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><h4>High Value Churn</h4><h2>{high_value:.2f}%</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><h4>Inactive Churn</h4><h2>{inactive:.2f}%</h2></div>", unsafe_allow_html=True)

# -------------------------------
# DONUT CHART
# -------------------------------
st.markdown("## 📊 Churn Distribution")

counts = df_filtered['Exited'].value_counts()

fig = go.Figure(data=[go.Pie(
    labels=["Stayed", "Churned"],
    values=counts.values,
    hole=0.6,
    marker_colors=["#2ECC71", "#FF4B4B"]
)])

fig.update_layout(
    annotations=[dict(text=f"{overall:.1f}%", x=0.5, y=0.5, showarrow=False, font_size=20)],
    paper_bgcolor="#061A2F",
    font_color="white"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 4 BAR CHARTS (FIXED GRID)
# -------------------------------
st.markdown("## 📊 Customer Segmentation Analysis")

row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# AGE
age = df_filtered.groupby('AgeGroup')['Exited'].mean()*100
fig1 = px.bar(x=age.index, y=age.values,
              color=age.index,
              title="Churn by Age",
              color_discrete_sequence=["#FF4B4B","#FFC300","#2ECC71","#1F3A93"])
fig1.update_layout(paper_bgcolor="#061A2F", font_color="white")

row1_col1.markdown('<div class="card">', unsafe_allow_html=True)
row1_col1.plotly_chart(fig1, use_container_width=True)
row1_col1.markdown('</div>', unsafe_allow_html=True)

# BALANCE
balance = df_filtered.groupby('BalanceGroup')['Exited'].mean()*100
fig2 = px.bar(x=balance.index, y=balance.values,
              color=balance.index,
              title="Churn by Balance",
              color_discrete_sequence=["#FF4B4B","#FFC300","#2ECC71"])
fig2.update_layout(paper_bgcolor="#061A2F", font_color="white")

row1_col2.markdown('<div class="card">', unsafe_allow_html=True)
row1_col2.plotly_chart(fig2, use_container_width=True)
row1_col2.markdown('</div>', unsafe_allow_html=True)

# CREDIT
credit = df_filtered.groupby('CreditGroup')['Exited'].mean()*100
fig3 = px.bar(x=credit.index, y=credit.values,
              color=credit.index,
              title="Churn by Credit Score",
              color_discrete_sequence=["#FF4B4B","#FFC300","#2ECC71"])
fig3.update_layout(paper_bgcolor="#061A2F", font_color="white")

row2_col1.markdown('<div class="card">', unsafe_allow_html=True)
row2_col1.plotly_chart(fig3, use_container_width=True)
row2_col1.markdown('</div>', unsafe_allow_html=True)

# TENURE
tenure = df_filtered.groupby('TenureGroup')['Exited'].mean()*100
fig4 = px.bar(x=tenure.index, y=tenure.values,
              color=tenure.index,
              title="Churn by Tenure",
              color_discrete_sequence=["#FF4B4B","#FFC300","#2ECC71"])
fig4.update_layout(paper_bgcolor="#061A2F", font_color="white")

row2_col2.markdown('<div class="card">', unsafe_allow_html=True)
row2_col2.plotly_chart(fig4, use_container_width=True)
row2_col2.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# GEOGRAPHY ANALYSIS
# -------------------------------
st.markdown("## 🌍 Geography Analysis")

geo = df_original.groupby('Geography')['Exited'].mean()*100

fig_geo = px.bar(x=geo.index, y=geo.values,
                 color=geo.index,
                 title="Churn by Country",
                 color_discrete_sequence=["#3498DB","#9B59B6","#E67E22"])

fig_geo.update_layout(paper_bgcolor="#061A2F", font_color="white")

st.plotly_chart(fig_geo, use_container_width=True)

# -------------------------------
# INSIGHTS
# -------------------------------
st.markdown("## 💡 Key Insights")

st.markdown("""
🔴 Mid-age customers have highest churn  
🟡 High-balance customers are risky  
🟢 Inactive users drive churn  
🔵 Geography impacts churn behavior  
""")

# -------------------------------
# DATASET PREVIEW
# -------------------------------
st.markdown("## 📄 Dataset Preview")

rows = st.slider("Select rows", 10, 1000, 50)
st.dataframe(df_filtered.head(rows))