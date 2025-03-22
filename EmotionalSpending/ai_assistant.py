import os
import google.generativeai as genai
import streamlit as st
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Gemini API
def setup_gemini():
    """Initialize the Gemini API client"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        st.error("Google API key not found. Please add your GOOGLE_API_KEY to environment variables.")
        return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        return False

def get_gemini_model():
    """Get the Gemini model for chat interactions"""
    if setup_gemini():
        try:
            # Use Gemini Pro model for chat
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"Error accessing Gemini model: {e}")
    return None

def chat_with_gemini(user_message, chat_history=None):
    """Chat with Gemini AI about spending habits and emotional wellness"""
    model = get_gemini_model()
    
    if not model:
        return "I'm unable to connect to the AI assistant at the moment. Please check your API key."
    
    if chat_history is None:
        chat_history = []
    
    # System prompt to guide the AI
    system_prompt = """
    You are a supportive financial wellness coach helping people understand the emotional aspects of their spending.
    Your goal is to help the user develop healthier spending habits by:
    1. Identifying emotional triggers for spending
    2. Suggesting alternatives to impulse purchases
    3. Providing brief mindfulness exercises when stress is detected
    4. Recommending simple, budget-friendly activities or recipes
    5. Being empathetic but focused on practical advice
    
    Keep responses concise and supportive. Don't be judgmental about spending habits.
    When suggesting alternatives to shopping, focus on free or low-cost options.
    """
    
    try:
        # Set up chat session
        chat = model.start_chat(history=chat_history)
        
        # Add system prompt if this is the first message
        if not chat_history:
            chat.send_message(system_prompt)
        
        # Send user message and get response
        response = chat.send_message(user_message)
        
        # Return the response text
        return response.text
    except Exception as e:
        st.error(f"Error communicating with Gemini: {e}")
        return "I'm having trouble processing your request. Please try again later."

def analyze_spending_patterns(expenses):
    """Use Gemini to analyze spending patterns and provide insights"""
    model = get_gemini_model()
    
    if not model or not expenses:
        return "Not enough data to analyze spending patterns."
    
    # Prepare expense data for analysis
    df = pd.DataFrame(expenses)
    
    # Generate summary statistics
    emotion_spending = df.groupby('emotion')['amount'].sum().to_dict()
    top_emotion = max(emotion_spending.items(), key=lambda x: x[1]) if emotion_spending else (None, 0)
    
    category_spending = df.groupby('category')['amount'].sum().to_dict()
    unnecessary_spending = df[df['necessity'] <= 5]['amount'].sum() if 'necessity' in df.columns else 0
    
    # Create prompt for Gemini
    prompt = f"""
    Based on the user's spending data, provide a brief analysis (100 words max) and actionable advice:
    
    Top emotional trigger: {top_emotion[0]} (${top_emotion[1]:.2f})
    Category breakdown: {category_spending}
    Money spent on non-necessities: ${unnecessary_spending:.2f}
    
    Provide 2-3 practical tips to reduce emotional spending, especially when feeling {top_emotion[0]}.
    Be empathetic, non-judgmental, and focus on small, achievable changes.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating spending analysis: {e}")
        return "Unable to analyze spending patterns at this time."

def get_mindfulness_exercise():
    """Get a quick mindfulness exercise to prevent impulse purchases"""
    model = get_gemini_model()
    
    if not model:
        return "Take a deep breath and pause before making your purchase."
    
    prompt = """
    Provide a very brief (50 words max) mindfulness exercise that someone can do when 
    they feel the urge to make an impulse purchase. The exercise should be simple, 
    quick, and help ground the person in the present moment.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating mindfulness exercise: {e}")
        return "Take a deep breath and pause before making your purchase."

def get_alternative_activity(emotion, category):
    """Get an alternative activity based on the user's current emotion and spending category"""
    model = get_gemini_model()
    
    if not model:
        return "Consider going for a walk or calling a friend instead of shopping."
    
    prompt = f"""
    A person is feeling {emotion} and considering spending money on {category}.
    Suggest a free or very low-cost alternative activity (under 50 words) that could 
    satisfy the emotional need without spending money. Be specific and practical.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating alternative activity: {e}")
        return "Consider going for a walk or calling a friend instead of shopping."

def get_quick_recipe():
    """Get a quick, budget-friendly recipe recommendation"""
    model = get_gemini_model()
    
    if not model:
        return "Try a simple pasta dish with ingredients you already have at home."
    
    prompt = """
    Provide a very simple, budget-friendly recipe (100 words max) that uses common pantry items.
    The recipe should be quick to make, require minimal ingredients, and be satisfying.
    Format as a brief ingredients list followed by 2-3 simple steps.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating recipe: {e}")
        return "Try a simple pasta dish with ingredients you already have at home."

def classify_transaction_impulsivity(transaction, user_spending_patterns):
    """Use Gemini to classify if a transaction appears impulsive based on patterns"""
    model = get_gemini_model()
    
    if not model:
        return {
            "is_impulsive": None,
            "confidence": 0,
            "reasoning": "AI assistant unavailable"
        }
    
    # Create context from user's spending patterns
    emotions_pattern = user_spending_patterns.get('emotions', {})
    category_pattern = user_spending_patterns.get('categories', {})
    merchants_pattern = user_spending_patterns.get('merchants', {})
    
    prompt = f"""
    Analyze this transaction and determine if it's likely an impulsive purchase:
    
    Transaction details:
    - Merchant: {transaction.get('merchant', 'Unknown')}
    - Amount: ${transaction.get('amount', 0):.2f}
    - Category: {transaction.get('category', 'Uncategorized')}
    - Time: {transaction.get('date', datetime.now()).strftime('%Y-%m-%d')}
    
    User's spending patterns:
    - Common emotional spending triggers: {list(emotions_pattern.keys())[:3] if emotions_pattern else 'No data'}
    - Typical categories: {list(category_pattern.keys())[:3] if category_pattern else 'No data'}
    - Frequently visited merchants: {list(merchants_pattern.keys())[:3] if merchants_pattern else 'No data'}
    
    Respond in JSON format with these fields only:
    {
        "is_impulsive": true/false,
        "confidence": (number between 0-100),
        "reasoning": "brief explanation"
    }
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the response - in a real app, you would properly parse JSON here
        # This is a simplified approach
        response_text = response.text
        result = {
            "is_impulsive": "true" in response_text.lower(),
            "confidence": 70,  # Default value
            "reasoning": response_text.split("reasoning")[1].split('"')[1] if "reasoning" in response_text else "Based on spending patterns"
        }
        return result
    except Exception as e:
        st.error(f"Error classifying transaction: {e}")
        return {
            "is_impulsive": None,
            "confidence": 0,
            "reasoning": "Could not classify transaction"
        }