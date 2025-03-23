import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import random

# -----------------------
# ✅ Initialize session state
# -----------------------
if "checkins" not in st.session_state:
    st.session_state.checkins = []

if "expenses" not in st.session_state:
    st.session_state.expenses = [
        {"date": datetime.today() - timedelta(days=i),
         "amount": 15 + i * 3,
         "emotion": "stressed" if i % 2 == 0 else "happy",
         "category": "Food" if i % 2 == 0 else "Entertainment",
         "necessity": i % 10 + 1}
        for i in range(30)
    ]

# -----------------------
# 🌿 Page Config
# -----------------------
st.set_page_config(page_title="Mintality - Home", page_icon="🌿", layout="wide")
st.markdown("<h1 style='text-align: center; color: #3f704d;'>🌿 Welcome to Mintality</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Your personalized financial wellness companion</p>", unsafe_allow_html=True)

# -----------------------
# 🧘 Mood Check-in (Top Section)
# -----------------------
st.markdown("## 🧘 Daily Mood Check-In")
today = datetime.today().date()
already_checked_in = any(c["Date"] == today for c in st.session_state.checkins)

with st.container():
    if not already_checked_in:
        mood_today = st.slider("How's your mood today?", 1, 5, 3, format="😞|🙁|😐|🙂|😄")
        note = st.text_area("Anything you'd like to reflect on?", placeholder="Optional")
        if st.button("Submit Check-in", type="primary"):
            st.session_state.checkins.append({
                "Date": today,
                "Mood": mood_today,
                "Notes": note
            })
            st.success("✅ Check-in saved! Scroll down to see your trends 👇")
    else:
        today_checkin = [c for c in st.session_state.checkins if c["Date"] == today][0]
        st.info(f"✅ You've already checked in today. Mood: {today_checkin['Mood']}")

# -----------------------
# 💰 Hero Savings Section
# -----------------------
st.markdown("---")
weekly_budget = 200
total_spent = sum(e["amount"] for e in st.session_state.expenses[-7:])
savings = max(0, weekly_budget - total_spent)

st.markdown("### 💸 Your Weekly Financial Wellness Snapshot")
col1, col2 = st.columns([2, 3])
with col1:
    st.markdown(f"<h2 style='color: green;'>💵 ${savings:.2f}</h2>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #666;'>Estimated Money Saved This Week</h5>", unsafe_allow_html=True)
    st.success("🎯 Great job avoiding unnecessary spending!")
with col2:
    bar = go.Figure(go.Indicator(
        mode="gauge+number",
        value=savings,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Savings Progress"},
        gauge={'axis': {'range': [0, weekly_budget]},
               'bar': {'color': "green"},
               'steps': [{'range': [0, weekly_budget/2], 'color': "#f2f2f2"},
                         {'range': [weekly_budget/2, weekly_budget], 'color': "#d9f2d9"}]}
    ))
    st.plotly_chart(bar, use_container_width=True)

# -----------------------
# 📈 Mood Graph (Last 7 Days)
# -----------------------
mood_data = st.session_state.checkins[-7:]
if mood_data:
    st.markdown("---")
    st.markdown("### 📈 Mood Trend Over the Week")
    dates = [entry["Date"] for entry in mood_data]
    moods = [entry["Mood"] for entry in mood_data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=moods, mode='lines+markers',
                             line=dict(color='green', width=3), marker=dict(size=8)))
    fig.update_layout(yaxis=dict(range=[1, 5], title='Mood Level'),
                      xaxis_title='Date', height=300,
                      margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

# -----------------------
# 📆 Mood Graph (Last 30 Days)
# -----------------------
st.markdown("### 📅 Monthly Mood Tracker")
dates_30 = [datetime.today().date() - timedelta(days=i) for i in range(29, -1, -1)]
moods_30 = [random.randint(1, 5) for _ in range(30)]
df_mood = pd.DataFrame({"Date": dates_30, "Mood": moods_30})
fig_month = go.Figure()
fig_month.add_trace(go.Scatter(
    x=df_mood["Date"],
    y=df_mood["Mood"],
    mode='lines+markers',
    line=dict(color='mediumseagreen', width=3),
    marker=dict(size=6),
    name="Mood Level"
))
fig_month.update_layout(
    xaxis_title="Date",
    yaxis=dict(title="Mood (1 = Low, 5 = High)", range=[1, 5]),
    hovermode='x unified',
    height=300
)
st.plotly_chart(fig_month, use_container_width=True)

# -----------------------
# 📊 Spending Charts
# -----------------------
def create_emotion_spending_chart(expenses):
    df = pd.DataFrame(expenses)
    emotion_totals = df.groupby('emotion')['amount'].sum().reset_index().sort_values('amount', ascending=False)
    fig = px.bar(emotion_totals, x='emotion', y='amount', title='Spending by Emotional State',
                 labels={'emotion': 'Emotion', 'amount': 'Total Spent ($)'},
                 color='emotion', color_discrete_sequence=px.colors.qualitative.Set2)
    return fig

def create_category_chart(expenses):
    df = pd.DataFrame(expenses)
    category_totals = df.groupby('category')['amount'].sum().reset_index()
    fig = px.pie(category_totals, values='amount', names='category', title='Spending by Category',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_spending_trend_chart(expenses, days=30):
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date)
    daily_spending = df.groupby(df['date'].dt.date)['amount'].sum().reindex(date_range.date, fill_value=0)
    trend_df = pd.DataFrame({'date': daily_spending.index, 'amount': daily_spending.values})
    trend_df['moving_avg'] = trend_df['amount'].rolling(window=7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=trend_df['date'], y=trend_df['amount'], name='Daily Spending',
                         marker_color='rgba(100, 149, 237, 0.4)'))
    fig.add_trace(go.Scatter(x=trend_df['date'], y=trend_df['moving_avg'], name='7-Day Avg',
                             line=dict(color='blue', width=3)))
    fig.update_layout(title='Spending Trend (Last 30 Days)', xaxis_title='Date',
                      yaxis_title='Amount Spent ($)', hovermode='x unified')
    return fig

# -----------------------
# 📊 Financial Behavior Insights
# -----------------------
st.markdown("---")
st.markdown("### 📊 Financial Behavior Insights")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(create_emotion_spending_chart(st.session_state.expenses), use_container_width=True)
with col2:
    st.plotly_chart(create_category_chart(st.session_state.expenses), use_container_width=True)

st.plotly_chart(create_spending_trend_chart(st.session_state.expenses), use_container_width=True)

# -----------------------
# 🌈 Encouragement
# -----------------------
st.markdown("---")
st.success("🌈 Remember: Every small mindful step adds up — you're doing amazing!")
