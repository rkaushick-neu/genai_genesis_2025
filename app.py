import streamlit as st

# App config
st.set_page_config(
    page_title="Mintality",
    page_icon="🌿",
    layout="centered"
)

st.title("🌿 Welcome to Mintality")

st.markdown("""
Mintality is your all-in-one personal financial wellness assistant — powered by generative AI and mindfulness.  
Use the sidebar to explore:
- ✅ Your mood & savings dashboard
- 🤖 Chat with an AI assistant
- 👤 View and update your profile
""")

st.markdown("---")

st.info("Use the sidebar to navigate between pages.")
