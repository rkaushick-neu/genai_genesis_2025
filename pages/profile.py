
import streamlit as st

st.set_page_config(page_title="Mintality - Profile", page_icon="👤")
st.title("👤 Your Profile")

st.markdown("Manage your account settings, preferences, and financial goals.")

st.subheader("📛 User Info")
st.text_input("Name", value="Mintality User")
st.text_input("Email", value="you@example.com")
st.selectbox("Preferred Budget Cycle", ["Weekly", "Bi-Weekly", "Monthly"])
st.slider("Monthly Budget ($)", 100, 2000, 500, step=50)

st.subheader("🎯 Financial Goals")
st.text_area("Your Goal", "Save $200 each month for an emergency fund.")

st.button("💾 Save Changes")
