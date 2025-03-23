import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
from utils.gemini_service import render_mood_checkin
# Import Gemini chat
from utils.gemini_service import generate_affirmation, analyze_emotion, gemini_chat, generate_advice, generate_motivational_quote
from utils.transaction_utils import (
    load_transactions, 
    analyze_emotional_spending,
    get_transactions_by_emotion,
    get_top_trigger_for_emotion,
    calculate_potential_savings,
    predict_transaction_emotions
)
from utils.emotion_utils import (
    EMOTION_COLORS,
    EMOTION_EMOJIS,
    save_emotional_state,
    get_emotional_state_history,
    calculate_emotion_intensity
)
from utils.predictive_utils import generate_prediction

st.set_page_config(
    page_title="Mintality - Financial Wellness Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! I'm Wellnest, your financial wellness companion. How are you feeling about your finances today?"}
    ]
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
# Add control flags to prevent infinite loop
if "processing_input" not in st.session_state:
    st.session_state.processing_input = False
if "last_processed_message" not in st.session_state:
    st.session_state.last_processed_message = ""
# Add intensity asking flag
if "asking_intensity" not in st.session_state:
    st.session_state.asking_intensity = False
# Add emotion confirmation flags
if "asking_emotion_confirmation" not in st.session_state:
    st.session_state.asking_emotion_confirmation = False
if "showing_emotion_selector" not in st.session_state:
    st.session_state.showing_emotion_selector = False
if "current_transaction_for_confirmation" not in st.session_state:
    st.session_state.current_transaction_for_confirmation = None
if "selected_emotion" not in st.session_state:
    st.session_state.selected_emotion = None

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #4527A0; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #5E35B1; margin-top: 0px; margin-bottom: 2rem; }
    .emotion-badge { padding: 0.5rem 1rem; border-radius: 1rem; margin-bottom: 1rem; }
    .chat-message { padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; }
    .user-message { background-color: #E3F2FD; border-left: 4px solid #2196F3; }
    .assistant-message { background-color: #F5F5F5; border-left: 4px solid #9575CD; }
    .prediction-banner { padding: 1rem; background-color: #FFF8E1; border-left: 4px solid #FFB300; border-radius: 0.5rem; margin-bottom: 1rem; }
    .affirmation-card { padding: 1.5rem; background: linear-gradient(to right, #E8EAF6, #C5CAE9); border-radius: 0.5rem; margin-bottom: 1rem; }
    .stButton>button { background-color: #5E35B1; color: white; border: none; border-radius: 4px; padding: 0.5rem 1rem; }
    .emotion-confirm-card { background-color: #f1f8e9; padding: 16px; border-radius: 8px; margin-bottom: 20px; }
    .intensity-card { background-color: #e3f2fd; padding: 16px; border-radius: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">Mintality</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your Financial Wellness Companion</p>', unsafe_allow_html=True)

# Check for transactions that need emotion confirmation
if (st.session_state.transactions and 
    not st.session_state.asking_emotion_confirmation and 
    not st.session_state.asking_intensity and
    not st.session_state.showing_emotion_selector):
    # Find transactions without emotion tags or with 'neutral' tag
    unclassified = [t for t in st.session_state.transactions 
                    if t.get('emotion_tag') == 'neutral' or not t.get('emotion_tag')]
    
    if unclassified and len(unclassified) > 0:
        classified = [t for t in st.session_state.transactions if t.get('emotion_tag') != 'neutral']
        
        if len(classified) > 0:
            # Get predictions
            try:
                predictions = predict_transaction_emotions(unclassified, classified)
                
                # Find first low confidence prediction
                for pred in predictions:
                    if pred['confidence'] < 0.6:  # Confidence threshold
                        st.session_state.asking_emotion_confirmation = True
                        st.session_state.current_transaction_for_confirmation = {
                            'transaction': pred['transaction'],
                            'predicted_emotion': pred['predicted_emotion'],
                            'confidence': pred['confidence']
                        }
                        break
            except Exception as e:
                st.error(f"Error predicting emotions: {e}")

left_col, right_col = st.columns([2, 1])

with left_col:
    current_emotion = st.session_state.current_emotion
    emotion = current_emotion["emotion"]
    intensity = current_emotion["intensity"]
    emotion_color = EMOTION_COLORS.get(emotion, "#A5A5A5")
    emotion_emoji = EMOTION_EMOJIS.get(emotion, "😐")
    intensity_label = "High" if intensity >= 0.8 else "Medium" if intensity >= 0.5 else "Low"

    st.markdown(f"""
        <div class="emotion-badge" style="background-color: {emotion_color}20; border-left: 4px solid {emotion_color};">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.8rem; margin-right: 0.5rem;">{emotion_emoji}</span>
                <div>
                    <div style="font-weight: bold; text-transform: capitalize;">{emotion}</div>
                    <div style="font-size: 0.8rem; color: #555;">{intensity_label} intensity</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display emotion confirmation interface if needed
    if st.session_state.asking_emotion_confirmation:
        transaction = st.session_state.current_transaction_for_confirmation['transaction']
        pred_emotion = st.session_state.current_transaction_for_confirmation['predicted_emotion']
        
        st.markdown(f"""
        <div class="emotion-confirm-card">
            <h3 style="margin-top: 0;">Help Us Understand Your Emotions</h3>
            <p>For this transaction at <b>{transaction['merchant']}</b> for <b>${transaction['amount']:.2f}</b> on {transaction['date']}, 
               I think you might have been feeling <b>{pred_emotion}</b>. Is that correct?</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, that's right", key="yes_button"):
                # Update transaction with confirmed emotion
                for t in st.session_state.transactions:
                    if (t['merchant'] == transaction['merchant'] and 
                        t['amount'] == transaction['amount'] and 
                        t['date'] == transaction['date']):
                        t['emotion_tag'] = pred_emotion
                
                # Reset confirmation state
                st.session_state.asking_emotion_confirmation = False
                st.session_state.current_transaction_for_confirmation = None
                
                # Update emotional spending analysis
                st.session_state.emotional_spending = analyze_emotional_spending(st.session_state.transactions)
                st.experimental_rerun()
        
        with col2:
            if st.button("No, that's not right", key="no_button"):
                # Set flag to show emotion selector on next run
                st.session_state.showing_emotion_selector = True
                st.session_state.asking_emotion_confirmation = False
                st.experimental_rerun()
    
    # Display emotion selector if needed
    elif st.session_state.showing_emotion_selector:
        transaction = st.session_state.current_transaction_for_confirmation['transaction']
        
        st.markdown(f"""
        <div class="emotion-confirm-card">
            <h3 style="margin-top: 0;">Select Emotion</h3>
            <p>For this transaction at <b>{transaction['merchant']}</b> for <b>${transaction['amount']:.2f}</b> on {transaction['date']}, 
               how were you feeling?</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show emotion selector
        emotions = ["stressed", "anxious", "retail_therapy", "happy", "motivated", "neutral"]
        selected_emotion = st.selectbox("Choose an emotion:", emotions, key="emotion_selector")
        
        if st.button("Confirm Emotion", key="confirm_emotion_button"):
            # Update transaction with user-selected emotion
            for t in st.session_state.transactions:
                if (t['merchant'] == transaction['merchant'] and 
                    t['amount'] == transaction['amount'] and 
                    t['date'] == transaction['date']):
                    t['emotion_tag'] = selected_emotion
            
            # Reset confirmation states
            st.session_state.showing_emotion_selector = False
            st.session_state.current_transaction_for_confirmation = None
            
            # Update emotional spending analysis
            st.session_state.emotional_spending = analyze_emotional_spending(st.session_state.transactions)
            st.experimental_rerun()
    
    # Display intensity selection interface if needed
    elif st.session_state.asking_intensity:
        emotion = st.session_state.current_emotion["emotion"]
        
        st.markdown(f"""
        <div class="intensity-card">
            <h3 style="margin-top: 0;">How intensely are you feeling {emotion}?</h3>
        </div>
        """, unsafe_allow_html=True)
        
        intensity_level = st.slider("Intensity level", 0.1, 1.0, 0.5, 0.1)
        
        if st.button("Confirm", key="confirm_intensity_button"):
            # Update emotional state with user-provided intensity
            emotional_state = {
                "emotion": emotion,
                "confidence": st.session_state.current_emotion["confidence"],
                "intensity": intensity_level
            }
            
            st.session_state.current_emotion = emotional_state
            save_emotional_state(emotion, emotional_state["confidence"], intensity_level)
            
            # Generate response based on intensity
            financial_context = {
                "spending_trigger": None,
                "recent_emotional_spending": 0,
                "monthly_savings_goal": 200,
                "primary_goal": "saving for vacation"
            }
            
            try:
                if intensity_level < 0.4:
                    # Low intensity
                    response = generate_motivational_quote(emotion)
                else:
                    # High intensity
                    response = generate_advice(emotional_state, financial_context)
                    
                    # Also generate prediction
                    prediction = generate_prediction(st.session_state.transactions, emotion)
                    if prediction:
                        st.session_state.prediction = prediction
            except Exception as e:
                st.error(f"Error generating response: {e}")
                response = "I understand how you're feeling. Let's take a moment to think about your finances mindfully."
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Update affirmation
            try:
                affirmation = generate_affirmation(emotion, financial_context["primary_goal"])
                st.session_state.affirmation = affirmation
            except Exception as e:
                st.error(f"Error generating affirmation: {e}")
            
            # Reset asking state
            st.session_state.asking_intensity = False
            st.experimental_rerun()
    else:
        # Display prediction if available
        if st.session_state.prediction:
            prediction = st.session_state.prediction
            p_emotion = prediction["emotion"]
            p_category = prediction["category"]
            p_amount = prediction["estimated_amount"]
            p_time = prediction["time_of_day"]
            
            # Customize message based on emotion and category
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

        st.markdown("### Chat with Wellnest")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                role = message["role"]
                content = message["content"]
                css_class = "user-message" if role == "user" else "assistant-message"
                speaker = "You" if role == "user" else "Wellnest"

                # Add dynamic background only for assistant
                style = f"background-color: {emotion_color}20;" if role == "assistant" else ""

                st.markdown(
                    f'<div class="chat-message {css_class}" style="{style}"><b>{speaker}:</b> {content}</div>',
                    unsafe_allow_html=True
                )

            user_input = st.text_input("Share how you're feeling about your finances...", key="user_input")
            
            # Only process input if it's new and we're not already processing
            if (user_input and 
                not st.session_state.processing_input and 
                user_input != st.session_state.last_processed_message and 
                not st.session_state.asking_intensity and 
                not st.session_state.asking_emotion_confirmation and
                not st.session_state.showing_emotion_selector):
                # Set processing flag to prevent reprocessing
                st.session_state.processing_input = True
                st.session_state.last_processed_message = user_input
                
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": user_input})

                try:
                    # Analyze emotion
                    emotion_result = analyze_emotion(user_input)
                    emotion = emotion_result["emotion"]
                    confidence = emotion_result["confidence"]

                    # Calculate intensity
                    intensity = calculate_emotion_intensity(emotion, confidence)
                    
                    # If emotion is strong but confidence is low, ask for intensity
                    if emotion != "neutral" and confidence < 0.7:
                        st.session_state.current_emotion = {
                            "emotion": emotion,
                            "confidence": confidence,
                            "intensity": intensity
                        }
                        st.session_state.asking_intensity = True
                        st.session_state.processing_input = False
                        st.experimental_rerun()
                    
                    # Otherwise continue normal flow
                    emotional_state = save_emotional_state(emotion, confidence)

                    # Update current emotion
                    st.session_state.current_emotion = {
                        "emotion": emotion,
                        "confidence": confidence,
                        "intensity": intensity
                    }

                    # Generate prediction if available
                    try:
                        prediction = generate_prediction(st.session_state.transactions, emotion)
                        if prediction:
                            st.session_state.prediction = prediction
                    except Exception as e:
                        st.error(f"Error generating prediction: {e}")
                        prediction = None

                    # Set up financial context
                    financial_context = {
                        "spending_trigger": prediction["category"] if prediction else None,
                        "recent_emotional_spending": prediction["estimated_amount"] if prediction else 0,
                        "monthly_savings_goal": 200,
                        "primary_goal": "saving for vacation"
                    }

                    # Generate response
                    response = gemini_chat(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    # Generate new affirmation for non-neutral emotions
                    if emotion != 'neutral':
                        try:
                            affirmation = generate_affirmation(emotion, financial_context["primary_goal"])
                            st.session_state.affirmation = affirmation
                        except Exception as e:
                            st.error(f"Error generating affirmation: {e}")
                
                except Exception as e:
                    st.error(f"Error processing input: {e}")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "I'm having trouble processing that right now. Can you try again or phrase that differently?"
                    })
                
                # Reset processing flag
                st.session_state.processing_input = False
                st.experimental_rerun()

        # Affirmation card
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
            color = EMOTION_COLORS.get(str(val).lower(), "#A5A5A5")
            return f'background-color: {color}20'
        
        styled_df = df.style.map(color_emotion, subset=["Emotion"])
        styled_df = styled_df.format({"Amount ($)": "${:.2f}"})
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transaction data available.")

# Footer
st.markdown("---")
st.markdown("Mintality - Your Financial Wellness Companion")
