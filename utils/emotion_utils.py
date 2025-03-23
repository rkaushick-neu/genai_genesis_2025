import json
import streamlit as st
from datetime import datetime

# Emotion color mappings for visualization
EMOTION_COLORS = {
    "stressed": "#EF5350",    # Red
    "anxious": "#FF9800",     # Orange
    "retail_therapy": "#7E57C2", # Purple
    "happy": "#4CAF50",       # Green
    "motivated": "#2196F3",   # Blue
    "neutral": "#9E9E9E"      # Gray
}

# Emotion emoji mappings
EMOTION_EMOJIS = {
    "stressed": "😟",
    "anxious": "😰",
    "retail_therapy": "🛍️",
    "happy": "😊",
    "motivated": "💪",
    "neutral": "😐"
}

# Calculate intensity of emotional state (0-1 scale)
def calculate_emotion_intensity(emotion, confidence):
    """Calculate the intensity of an emotional state"""
    # Base intensity on emotion type and confidence
    base_intensity = {
        "stressed": 0.8,
        "anxious": 0.7,
        "retail_therapy": 0.6,
        "happy": 0.5,
        "motivated": 0.4,
        "neutral": 0.2
    }.get(emotion, 0.5)
    
    # Adjust by confidence
    return min(base_intensity * confidence * 1.5, 1.0)

# Check if emotion is above risk threshold
def is_high_risk_emotion(emotion, intensity):
    """Check if an emotion is above risk threshold for spending"""
    risk_thresholds = {
        "stressed": 0.6,
        "anxious": 0.65,
        "retail_therapy": 0.55,
        "happy": 0.8,     # Even positive emotions can lead to spending
        "motivated": 0.75,
        "neutral": 0.9
    }
    
    return intensity >= risk_thresholds.get(emotion, 0.7)

# Save emotional state to session state history
def save_emotional_state(emotion, confidence):
    """Save emotional state to history in session state"""
    # Create emotional state object
    emotional_state = {
        "emotion": emotion,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat(),
        "intensity": calculate_emotion_intensity(emotion, confidence)
    }
    
    # Initialize history if it doesn't exist
    if "emotional_states" not in st.session_state:
        st.session_state.emotional_states = []
    
    # Add new state and trim history (keep last 10)
    st.session_state.emotional_states.append(emotional_state)
    if len(st.session_state.emotional_states) > 10:
        st.session_state.emotional_states = st.session_state.emotional_states[-10:]
    
    return emotional_state

# Get emotional state history
def get_emotional_state_history():
    """Get the history of emotional states"""
    if "emotional_states" not in st.session_state:
        st.session_state.emotional_states = []
    
    return st.session_state.emotional_states