import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Import utilities
from utils.cohere_service import analyze_emotion
from utils.gemini_service import generate_advice, generate_affirmation
from utils.transaction_utils import (
    load_transactions, 
    analyze_emotional_spending,
    get_transactions_by_emotion,
    get_top_trigger_for_emotion,
    calculate_potential_savings
)
from utils.emotion_utils import (
    EMOTION_COLORS,
    EMOTION_EMOJIS,
    save_emotional_state,
    get_emotional_state_history,
    calculate_emotion_intensity
)

# Set page configuration
st.set_page_config(
    page_title="Wellnest - Financial Wellness Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi there! I'm Wellnest, your financial wellness companion. How are you feeling about your finances today?"}]
if "current_emotion" not in st.session_state:
    st.session_state.current_emotion = {"emotion": "neutral", "confidence": 0.5, "intensity": 0.2}
if "affirmation" not in st.session_state:
    st.session_state.affirmation = "My financial choices today create my tomorrow. I have the power to make decisions aligned with my goals."
if "transactions" not in st.session_state:
    st.session_state.transactions = load_transactions()
if "prediction" not in st.session_state:
    st.session_state.prediction = None
if "emotional_spending" not in st.session_state:
    st.session_state.emotional_spending = analyze_emotional_spending(st.session_state.transactions)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4527A0;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #5E35B1;
        margin-top: 0px;
        margin-bottom: 2rem;
    }
    .emotion-badge {
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 4px solid #9575CD;
    }
    .prediction-banner {
        padding: 1rem;
        background-color: #FFF8E1;
        border-left: 4px solid #FFB300;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .affirmation-card {
        padding: 1.5rem;
        background: linear-gradient(to right, #E8EAF6, #C5CAE9);
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #5E35B1;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">Wellnest</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Financial Wellness Companion</p>', unsafe_allow_html=True)

# Layout
left_col, right_col = st.columns([2, 1])

with left_col:
    # Emotion Display
    current_emotion = st.session_state.current_emotion
    emotion = current_emotion["emotion"]
    intensity = current_emotion["intensity"]
    
    emotion_color = EMOTION_COLORS.get(emotion, "#A5A5A5")
    emotion_emoji = EMOTION_EMOJIS.get(emotion, "😐")

    if intensity >= 0.8:
        intensity_label = "High"
    elif intensity >= 0.5:
        intensity_label = "Medium"
    else:
        intensity_label = "Low"
    
    st.markdown(
        f"""
        <div class="emotion-badge" style="background-color: {emotion_color}20; border-left: 4px solid {emotion_color};">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.8rem; margin-right: 0.5rem;">{emotion_emoji}</span>
                <div>
                    <div style="font-weight: bold; text-transform: capitalize;">{emotion}</div>
                    <div style="font-size: 0.8rem; color: #555;">
                        {intensity_label} intensity
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Prediction Display
    if st.session_state.prediction:
        prediction = st.session_state.prediction
        p_emotion = prediction["emotion"]
        p_category = prediction["category"]
        p_amount = prediction["estimated_amount"]
        p_time = prediction["time_of_day"]
        
        if p_emotion == 'stressed' and p_category == 'food':
            message = f"Based on your patterns, you might be tempted to order food delivery tonight."
            suggestion = 'Try a quick 15-minute homemade meal instead.'
        elif p_emotion == 'stressed' and p_category == 'shopping':
            message = f"You often shop online when feeling stressed, especially in the {p_time}."
            suggestion = 'Consider a 30-minute break from screens to reset.'
        elif p_emotion == 'anxious' and p_category == 'food':
            message = f"Anxiety often leads to food delivery orders (avg. ${p_amount})."
            suggestion = 'A 10-minute walk might help reduce anxiety.'
        else:
            message = f"When feeling {p_emotion}, you often spend on {p_category} (avg. ${p_amount})."
            suggestion = 'Being aware of this pattern can help make mindful choices.'
        
        st.markdown(
            f"""
            <div class="prediction-banner">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.3rem; margin-right: 0.5rem;">🔮</span>
                    <h3 style="margin: 0; font-weight: bold;">Spending Insight</h3>
                </div>
                <p style="margin: 0 0 0.5rem 0;">{message}</p>
                <div style="display: flex; align-items: center; color: #7B1FA2; font-weight: bold;">
                    <span style="margin-right: 0.4rem;">💡</span>
                    {suggestion}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Chat interface
    st.markdown("### Chat with Wellnest")
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f'<div class="chat-message user-message"><b>You:</b> {content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message" style="background-color: {emotion_color}20;"><b>Wellnest:</b> {content}</div>', unsafe_allow_html=True)
    
    user_input = st.text_input("Share how you're feeling about your finances...", key="user_input")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        emotion_result = analyze_emotion(user_input)
        emotion = emotion_result["emotion"]
        confidence = emotion_result["confidence"]
        
        intensity = calculate_emotion_intensity(emotion, confidence)
        emotional_state = save_emotional_state(emotion, confidence)
        
        st.session_state.current_emotion = {
            "emotion": emotion,
            "confidence": confidence,
            "intensity": intensity
        }
        
        from utils.predictive_utils import generate_prediction
        prediction = generate_prediction(st.session_state.transactions, emotion)
        if prediction:
            st.session_state.prediction = prediction
        
        financial_context = {
            "spending_trigger": prediction["category"] if prediction else None,
            "recent_emotional_spending": prediction["estimated_amount"] if prediction else 0,
            "monthly_savings_goal": 200,
            "primary_goal": "saving for vacation"
        }
        
        response = generate_advice(emotional_state, financial_context)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        if emotion != 'neutral':
            affirmation = generate_affirmation(emotion, financial_context["primary_goal"])
            st.session_state.affirmation = affirmation
        
        st.rerun()
    
    st.markdown(
        f"""
        <div class="affirmation-card">
            <h3 style="margin-top: 0; font-size: 1.1rem; color: #3949AB;">Today's Financial Affirmation</h3>
            <p style="font-style: italic; color: #283593; font-size: 1.2rem; margin-bottom: 0;">
                "{st.session_state.affirmation}"
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with right_col:
    st.markdown("### Emotional Spending Patterns")
    
    emotional_spending = st.session_state.emotional_spending
    
    if emotional_spending and emotional_spending["by_emotion"]:
        emotions = list(emotional_spending["by_emotion"].keys())
        amounts = list(emotional_spending["by_emotion"].values())
        total = sum(amounts)
        percentages = [amount / total * 100 for amount in amounts]
        colors = [EMOTION_COLORS.get(emotion, "#9C27B0") for emotion in emotions]
        
        df = pd.DataFrame({
            "Emotion": [emotion.capitalize() for emotion in emotions],
            "Percentage": percentages,
            "Amount": amounts
        })
        
        fig = px.pie(
            df, 
            values="Percentage", 
            names="Emotion", 
            color_discrete_sequence=colors,
            title="Spending by Emotion"
        )
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(height=300, margin=dict(t=30, b=0, l=0, r=0))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"**Total Emotional Spending:** ${emotional_spending['total']:.2f}")
        
        potential_savings = calculate_potential_savings(emotional_spending)
        st.info(f"💡 **Insight:** Reducing emotional spending by half could save you approximately **${potential_savings:.2f}** per month.")
        
        current_emotion = st.session_state.current_emotion["emotion"]
        if current_emotion != "neutral":
            trigger = get_top_trigger_for_emotion(st.session_state.transactions, current_emotion)
            if trigger["category"]:
                st.warning(
                    f"📊 When feeling **{current_emotion}**, you tend to spend most on **{trigger['category']}** "
                    f"(avg. ${trigger['amount']:.2f}), particularly during the **{trigger['time_of_day']}**."
                )
    else:
        st.info("No emotional spending data available yet.")
    
    st.markdown("### Recent Transactions")
    
    if st.session_state.transactions:
        df = pd.DataFrame(st.session_state.transactions)
        df = df[["date", "merchant", "amount", "category", "emotion_tag"]]
        df = df.sort_values("date", ascending=False).head(5)
        df.columns = ["Date", "Merchant", "Amount ($)", "Category", "Emotion"]
        
        def color_emotion(val):
            color = EMOTION_COLORS.get(val.lower(), "#A5A5A5")
            return f'background-color: {color}20'
        
        styled_df = df.style.map(color_emotion, subset=["Emotion"])
        styled_df = styled_df.format({"Amount ($)": "${:.2f}"})
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transaction data available.")

# Footer
st.markdown("---")
st.markdown("Wellnest - Your Financial Wellness Companion")


