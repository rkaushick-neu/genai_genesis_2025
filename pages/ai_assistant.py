
import streamlit as st

st.set_page_config(page_title="Mintality - AI Assistant", page_icon="🤖")
st.title("🤖 Mintality AI Assistant")

st.markdown("Chat with your financial wellness assistant! Ask for savings tips, get affirmations, or talk through spending urges.")

# Placeholder for actual Gemini integration
user_input = st.text_input("You:", placeholder="e.g. I'm feeling anxious about my budget this month.")
if st.button("Send"):
    st.write("🧠 Gemini says:")
    st.success("You're not alone. Let’s look at small ways you can ease your budget stress this week.")
