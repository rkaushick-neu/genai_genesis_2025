import streamlit as st
from datetime import datetime

# --- Page Setup ---
st.set_page_config(page_title="My Profile | Mintality", page_icon="👤")

# --- Custom CSS ---
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #4527A0; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #5E35B1; margin-top: 0px; margin-bottom: 2rem; }
    .profile-box { background-color: #F5F5F5; padding: 2rem; border-radius: 1rem; margin-top: 1rem; }
    .highlight { color: #3949AB; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("""<h1 class="main-header">👤 My Profile</h1>
<p class="sub-header">Manage your identity, preferences and financial goals</p>
""", unsafe_allow_html=True)

# --- Personal Info ---
with st.container():
    st.subheader("👩‍💼 Personal Info")
    name = st.text_input("Full Name", value=st.session_state.get("user_name", "Mintality User"))
    email = st.text_input("Email", value=st.session_state.get("user_email", "you@example.com"))
    st.session_state.user_name = name
    st.session_state.user_email = email

# --- Preferences ---
with st.container():
    st.markdown("---")
    st.subheader("🔐 Preferences")
    theme = st.selectbox("Choose Theme", ["Light", "Dark"], index=0)
    notifications = st.toggle("Enable Notifications", value=True)
    budget_cycle = st.selectbox("Preferred Budget Cycle", ["Weekly", "Bi-Weekly", "Monthly"], index=2)
    monthly_budget = st.slider("Monthly Budget ($)", 100, 2000, 500, step=50)

    st.session_state.preferences = {
        "theme": theme,
        "notifications": notifications,
        "budget_cycle": budget_cycle,
        "monthly_budget": monthly_budget
    }

# --- Financial Goals ---
with st.container():
    st.markdown("---")
    st.subheader("🎯 Financial Goals")
    goal = st.text_area("Your Goal", value=st.session_state.get("financial_goal", "Save $200 each month for an emergency fund."))
    st.session_state.financial_goal = goal

# --- Check-in History ---
with st.container():
    st.markdown("---")
    st.subheader("📆 Mood Check-in History")
    checkins = st.session_state.get("checkins", [])
    if checkins:
        st.write("Here's a summary of your recent mood check-ins:")
        st.table(checkins[::-1])  # reverse for latest first
    else:
        st.info("You haven't done any mood check-ins yet. Head to the dashboard to log your first one!")

# --- Confirmation ---
st.success("✅ Profile auto-saved in session state.")
