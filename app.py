import streamlit as st
import pandas as pd
import plotly.express as px
import random
import os
from dotenv import load_dotenv
from utils.gemini_service import analyze_emotion, gemini_chat

# Load .env variables
load_dotenv()

st.set_page_config(page_title="🍿 Mintality - Home", page_icon="🍿")

# --- Header ---
st.markdown("""
    <h1 style='text-align: center; color: #3f704d;'>🍿 Welcome to Mintality</h1>
    <p style='text-align: center;'>Your personalized financial wellness companion</p>
""", unsafe_allow_html=True)

# --- Session State ---
if "emotion_slider" not in st.session_state:
    st.session_state.emotion_slider = 3
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hey there! How can I support you today emotionally or financially?"}
    ]
if "emotion_detected" not in st.session_state:
    st.session_state.emotion_detected = None
if "slider_processed" not in st.session_state:
    st.session_state.slider_processed = False
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

# --- Mood Slider & Emotion Trigger ---
st.markdown("## 🧘 Daily Mood Check-In")
emoji_map = {1: "😞", 2: "🙁", 3: "😐", 4: "🙂", 5: "😄"}

new_slider = st.slider("Rate your current mood", 1, 5, st.session_state.emotion_slider, key="mood_slider")
st.session_state.emotion_slider = new_slider

if new_slider != 3 and not st.session_state.slider_processed:
    user_emotion = analyze_emotion(emoji_map[new_slider])
    st.session_state.emotion_detected = user_emotion['emotion']
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": f"Thanks for sharing. It seems like you're feeling **{user_emotion['emotion']}**. Want to talk about it?"
    })
    st.session_state.slider_processed = True

# Reset the processed flag if user returns to neutral (3)
if new_slider == 3:
    st.session_state.slider_processed = False

# --- Chat Panel ---
st.markdown("---")
st.markdown("### 💬 Talk to Gemini")
chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_messages:
        role = msg["role"]
        bubble_color = "#e3f2fd" if role == "user" else "#f3e5f5"
        speaker = "You" if role == "user" else "Gemini"
        st.markdown(f"""
            <div style='background-color: {bubble_color}; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <strong>{speaker}:</strong> {msg['content']}
            </div>
        """, unsafe_allow_html=True)

    user_input = st.text_input("Type your message", key="user_chat_input")
    if user_input and user_input.strip() != "" and user_input != st.session_state.last_user_input:
        st.session_state.last_user_input = user_input
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        response = gemini_chat(user_input)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()

# --- Motivational Message ---
st.markdown("---")
st.success("🌈 Remember: Every small mindful step adds up — you're doing amazing!")
