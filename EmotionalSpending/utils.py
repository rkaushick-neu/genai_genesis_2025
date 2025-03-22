import streamlit as st
import datetime
import pandas as pd
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    
    if 'monthly_budget' not in st.session_state:
        st.session_state.monthly_budget = 1000.0
    
    if 'category_budgets' not in st.session_state:
        st.session_state.category_budgets = {}
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

def add_expense(date, amount, category, emotion, justification, necessity):
    """Add a new expense to the session state"""
    expense = {
        'date': date.strftime('%Y-%m-%d'),
        'amount': float(amount),
        'category': category,
        'emotion': emotion,
        'justification': justification,
        'necessity': necessity,
        'source': 'manual'
    }
    
    st.session_state.expenses.append(expense)
    # Sort expenses by date (newest first)
    st.session_state.expenses = sorted(
        st.session_state.expenses, 
        key=lambda x: x['date'], 
        reverse=True
    )

def delete_expense(index):
    """Delete an expense from the session state by index"""
    if 0 <= index < len(st.session_state.expenses):
        del st.session_state.expenses[index]
        return True
    return False

def get_date_range():
    """Get the date range of all expenses"""
    if not st.session_state.expenses:
        return datetime.date.today(), datetime.date.today()
    
    dates = [datetime.datetime.strptime(expense['date'], '%Y-%m-%d').date() 
             for expense in st.session_state.expenses]
    return min(dates), max(dates)

def filter_expenses(category=None, emotion=None, start_date=None, end_date=None):
    """Filter expenses based on category, emotion, and date range"""
    filtered = st.session_state.expenses
    
    # Handle multiple categories
    if category and isinstance(category, list) and not any(c == "All" for c in category):
        filtered = [expense for expense in filtered if expense['category'] in category]
    elif category and not isinstance(category, list) and category != "All":
        filtered = [expense for expense in filtered if expense['category'] == category]
    
    # Handle multiple emotions
    if emotion and isinstance(emotion, list) and not any(e == "All" for e in emotion):
        filtered = [expense for expense in filtered if expense['emotion'] in emotion]
    elif emotion and not isinstance(emotion, list) and emotion != "All":
        filtered = [expense for expense in filtered if expense['emotion'] == emotion]
    
    if start_date:
        filtered = [
            expense for expense in filtered
            if datetime.datetime.strptime(expense['date'], '%Y-%m-%d').date() >= start_date
        ]
    
    if end_date:
        filtered = [
            expense for expense in filtered
            if datetime.datetime.strptime(expense['date'], '%Y-%m-%d').date() <= end_date
        ]
    
    return filtered

def load_sample_data():
    """Load sample data for demo purposes"""
    # Only load sample data if expenses is empty
    if not st.session_state.expenses:
        today = datetime.date.today()
        
        # Define sample emotions and categories
        emotions = ["Happy", "Sad", "Stressed", "Bored", "Excited", "Anxious", "Neutral"]
        categories = ["Food & Dining", "Shopping", "Entertainment", "Transportation", "Utilities"]
        merchants = ["Starbucks", "Amazon", "Walmart", "Netflix", "Uber", "Local Restaurant", "Target", "Gas Station"]
        
        # Generate sample expenses for the past 30 days
        for i in range(30):
            date = today - datetime.timedelta(days=i)
            # Add 1-3 expenses per day
            for _ in range(random.randint(1, 3)):
                # Create expense
                emotion = random.choice(emotions)
                category = random.choice(categories)
                merchant = random.choice(merchants)
                
                # Make necessity more likely to be low for certain emotions
                necessity_high_emotions = ["Happy", "Excited"]
                necessity_low_emotions = ["Stressed", "Sad", "Bored"]
                
                if emotion in necessity_high_emotions:
                    necessity = random.randint(5, 10)
                elif emotion in necessity_low_emotions:
                    necessity = random.randint(1, 5)
                else:
                    necessity = random.randint(1, 10)
                
                # Create justifications based on emotions
                justifications = {
                    "Happy": ["Celebrating a win", "Treating myself", "In a good mood"],
                    "Excited": ["New product launch", "Special occasion", "Couldn't resist"],
                    "Stressed": ["Needed a break", "Retail therapy", "Comfort purchase"],
                    "Sad": ["Cheering myself up", "Feeling down", "Needed a boost"],
                    "Bored": ["Nothing else to do", "Browsing turned to buying", "Impulse buy"],
                    "Anxious": ["Distraction purchase", "Worried about missing out", "Stress relief"],
                    "Neutral": ["Regular purchase", "Needed it", "Routine shopping"]
                }
                
                justification = random.choice(justifications.get(emotion, ["Sample purchase"]))
                
                # Create the expense with merchant info
                expense = {
                    'date': date.strftime('%Y-%m-%d'),
                    'amount': round(random.uniform(5, 200), 2),
                    'category': category,
                    'emotion': emotion,
                    'merchant': merchant,
                    'justification': justification,
                    'necessity': necessity,
                    'source': 'manual'
                }
                
                st.session_state.expenses.append(expense)
        
        # Sort expenses by date (newest first)
        st.session_state.expenses = sorted(
            st.session_state.expenses, 
            key=lambda x: x['date'], 
            reverse=True
        )

def load_sample_checkins():
    """Load sample data for daily check-ins"""
    if not hasattr(st.session_state, 'daily_checkins') or not st.session_state.daily_checkins:
        today = datetime.date.today()
        
        # Define sample moods and energy levels
        moods = ["Very Happy", "Happy", "Neutral", "Sad", "Very Sad"]
        energy_levels = ["Very High", "High", "Moderate", "Low", "Very Low"]
        stress_levels = ["Very Low", "Low", "Moderate", "High", "Very High"]
        
        # Sample financial goals
        goals = [
            "Avoid online shopping today",
            "Bring lunch from home",
            "No impulse purchases",
            "Stick to my grocery list",
            "Put $10 into savings",
            "No eating out today",
            "Review my budget"
        ]
        
        # Generate sample check-ins for past 14 days
        for i in range(14):
            date = today - datetime.timedelta(days=i)
            
            # Skip some days randomly to create gaps in the streak
            if i > 5 and random.random() < 0.3:
                continue
                
            # Create check-in
            checkin = {
                'date': date.strftime('%Y-%m-%d'),
                'mood': random.choice(moods),
                'energy': random.choice(energy_levels),
                'stress': random.choice(stress_levels),
                'financial_goals': random.choice(goals),
                'notes': "Sample check-in data" if random.random() < 0.5 else ""
            }
            
            st.session_state.daily_checkins.append(checkin)
        
        # Sort check-ins by date (newest first)
        st.session_state.daily_checkins = sorted(
            st.session_state.daily_checkins, 
            key=lambda x: x['date'], 
            reverse=True
        )
        
        # Set last check-in date
        if st.session_state.daily_checkins and st.session_state.daily_checkins[0]['date'] == today.strftime('%Y-%m-%d'):
            st.session_state.last_checkin_date = today

def get_secret(key, default=None):
    """Safely get a secret from environment variables"""
    value = os.getenv(key)
    return value if value else default
