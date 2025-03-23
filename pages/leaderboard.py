import streamlit as st
import pandas as pd
import plotly.express as px
import random

st.set_page_config(page_title="🏆 Leaderboard | Mintality", page_icon="🏆")

st.markdown("""
    <style>
    .main-header { font-size: 2.8rem; color: #311B92; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px #ccc; }
    .sub-header { font-size: 1.2rem; color: #5E35B1; margin-top: 0; margin-bottom: 2rem; font-weight: 500; }
    .highlight-box {
        background-color: #FFF3E0;
        border-left: 6px solid #FB8C00;
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .leaderboard-table thead tr th {
        background-color: #E1BEE7 !important;
        font-weight: bold;
        color: #4A148C;
    }
    .leaderboard-table tbody tr:hover {
        background-color: #F3E5F5;
    }
    .alex-row td {
        background-color: #FFF8E1 !important;
        font-weight: bold;
    }
    .motivational-tip {
        font-style: italic;
        color: #6A1B9A;
        margin-top: 2rem;
    }
    .top-card {
        background-color: #F3E5F5;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 1px 1px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    .top-card h3 {
        color: #4A148C;
        margin-bottom: 0.3rem;
    }
    .top-card p {
        margin: 0.2rem 0;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 class="main-header">🏍 Monthly Leaderboard</h1>
<p class="sub-header">Celebrate the top savers and stay motivated on your financial journey!</p>
""", unsafe_allow_html=True)

# Confetti effect
st.balloons()

# Congratulatory message for Alex
st.markdown("""
<div class="highlight-box">
    🎉 <strong>Congratulations Alex!</strong> You're among the <strong>Top 5 savers this month</strong>! Your commitment to mindful spending is inspiring. Keep it up!
</div>
""", unsafe_allow_html=True)

# Dummy leaderboard data
names = ["Sarah", "James", "Riya", "Carlos", "Alex", "John", "Emily", "Zara", "Leo", "Mia"]
savings = sorted([random.randint(600, 850) for _ in range(10)], reverse=True)
moods = [round(random.uniform(3.5, 5.0), 1) for _ in range(10)]

# Create DataFrame
data = pd.DataFrame({
    "Rank": list(range(1, 11)),
    "Name": names,
    "Savings This Month ($)": savings,
    "Mood Score": moods
})

# Top 3 cards
st.subheader("🥇 Top 3 Savers")
top_cols = st.columns(3)
for i in range(3):
    with top_cols[i]:
        st.markdown(f"""
        <div class="top-card">
            <h3>#{data.iloc[i]['Rank']} - {data.iloc[i]['Name']}</h3>
            <p>💰 <strong>${data.iloc[i]['Savings This Month ($)']}</strong></p>
            <p>😊 Mood Score: <strong>{data.iloc[i]['Mood Score']}</strong></p>
        </div>
        """, unsafe_allow_html=True)

# Bar Chart
st.subheader("📈 Mood & Savings Overview")
fig = px.bar(
    data,
    x="Name",
    y="Savings This Month ($)",
    color="Mood Score",
    color_continuous_scale="Purples",
    title="Savings and Mood Score by User",
    labels={"Mood Score": "Mood", "Savings This Month ($)": "Savings ($)"}
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Highlight Alex's row
def highlight_alex(row):
    return ['background-color: #FFF8E1; font-weight: bold;' if row.Name == "Alex" else '' for _ in row]

# Full table
st.subheader("📊 Full Leaderboard")
st.dataframe(
    data.style.apply(highlight_alex, axis=1),
    use_container_width=True,
    hide_index=True,
    height=450,
    column_config={"Mood Score": st.column_config.NumberColumn(format="{:.1f}")}
)

# Motivational tip
tips = [
    "Every dollar you save is a vote for the future you want.",
    "Small habits lead to big results — keep logging your moods and spending.",
    "You’re not just saving money, you’re rewriting your story.",
    "Financial freedom begins with a single mindful choice."
]
st.markdown(f"<div class='motivational-tip'>💡 {random.choice(tips)}</div>", unsafe_allow_html=True)
