import streamlit as st
from firebase_setup import db
import google.generativeai as genai
import datetime
import random
import plotly.graph_objs as go


genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-pro")

# Fake mood and savings data for past 7 days (replace with Firestore data later)
dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(6, -1, -1)]
moods = [random.randint(1, 5) for _ in dates]  # 1=Low, 5=High
savings = 200 - sum([random.randint(5, 30) for _ in range(7)])  # Random spending

# Page config
st.set_page_config(page_title="Mintality - Home", page_icon="🌿")
st.title("🌿 Welcome to Mintality")

# Quick Check-in
st.header("🧘 How are you feeling today?")
mood_today = st.slider("Mood (1 = Low, 5 = Great)", 1, 5, 3)
journal = st.text_area("Write a quick note about your feelings (optional)")
if st.button("Submit Check-in"):
    st.success("✅ Check-in saved! Come back tomorrow for your next one.")

# Mood Graph
st.markdown("---")
st.subheader("📊 Your Mood This Week")
fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=moods, mode='lines+markers', line=dict(color='green'), name='Mood'))
fig.update_layout(yaxis=dict(range=[1, 5], title='Mood Level'), xaxis_title='Date', height=300)
st.plotly_chart(fig, use_container_width=True)

# Savings Overview
st.markdown("---")
st.subheader("💰 Your Estimated Savings")
st.metric("Money Saved This Week", f"${savings}", "+")

# Encouragement or Insight
st.markdown("---")
st.info("🌈 Remember: Every small mindful decision adds up. You're doing great!")

# Future: Show average mood, daily streaks, Gemini affirmations, budget tips, etc.
