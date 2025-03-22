import streamlit as st
import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def initialize_checkin_state():
    """Initialize session state variables for daily check-ins"""
    if 'daily_checkins' not in st.session_state:
        st.session_state.daily_checkins = []
    
    if 'last_checkin_date' not in st.session_state:
        st.session_state.last_checkin_date = None
    
    if 'checkin_model' not in st.session_state:
        st.session_state.checkin_model = None
    
    if 'encoders' not in st.session_state:
        st.session_state.encoders = {
            'mood': LabelEncoder(),
            'energy': LabelEncoder(),
            'stress': LabelEncoder()
        }

def add_daily_checkin(mood, energy_level, stress_level, financial_goals, notes):
    """Add a new daily check-in"""
    today = datetime.date.today()
    
    # Create check-in object
    checkin = {
        'date': today.strftime('%Y-%m-%d'),
        'mood': mood,
        'energy': energy_level,
        'stress': stress_level,
        'financial_goals': financial_goals,
        'notes': notes
    }
    
    # Update last check-in date
    st.session_state.last_checkin_date = today
    
    # Add to check-ins list
    st.session_state.daily_checkins.append(checkin)
    
    # Sort check-ins by date (newest first)
    st.session_state.daily_checkins = sorted(
        st.session_state.daily_checkins, 
        key=lambda x: x['date'], 
        reverse=True
    )
    
    # Update model
    update_impulse_prediction_model()
    
    return checkin

def get_todays_checkin():
    """Get today's check-in if it exists"""
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    for checkin in st.session_state.daily_checkins:
        if checkin['date'] == today:
            return checkin
    
    return None

def is_checkin_due():
    """Check if a daily check-in is due"""
    today = datetime.date.today()
    
    if st.session_state.last_checkin_date is None:
        return True
    
    # Check if the last check-in was before today
    last_checkin = datetime.datetime.strptime(
        st.session_state.last_checkin_date.strftime('%Y-%m-%d'), '%Y-%m-%d'
    ).date()
    
    return last_checkin < today

def update_impulse_prediction_model():
    """Update the machine learning model for predicting impulse purchases"""
    # Need both check-ins and expenses
    if (len(st.session_state.daily_checkins) < 5 or 
        len(st.session_state.expenses) < 5):
        return
    
    try:
        # Create DataFrame for check-ins
        checkin_df = pd.DataFrame(st.session_state.daily_checkins)
        checkin_df['date'] = pd.to_datetime(checkin_df['date'])
        
        # Create DataFrame for expenses
        expense_df = pd.DataFrame(st.session_state.expenses)
        expense_df['date'] = pd.to_datetime(expense_df['date'])
        
        # Label each expense as impulsive or not based on necessity rating
        # This is a simple approach - in reality, you might have user feedback
        expense_df['impulsive'] = expense_df['necessity'].apply(lambda x: 1 if x < 5 else 0)
        
        # Group expenses by date and calculate:
        # - Total spent
        # - Number of transactions
        # - Average necessity
        # - Count of impulsive purchases
        daily_spending = expense_df.groupby(expense_df['date'].dt.date).agg({
            'amount': 'sum',
            'transaction_id': 'count',
            'necessity': 'mean',
            'impulsive': 'sum'
        }).reset_index()
        
        daily_spending.columns = ['date', 'total_spent', 'transaction_count', 'avg_necessity', 'impulsive_count']
        daily_spending['date'] = pd.to_datetime(daily_spending['date'])
        
        # Merge check-ins with spending data
        combined_data = pd.merge(
            checkin_df,
            daily_spending,
            on='date',
            how='left'
        )
        
        # Fill missing values
        combined_data = combined_data.fillna({
            'total_spent': 0,
            'transaction_count': 0,
            'avg_necessity': 5,
            'impulsive_count': 0
        })
        
        # Encode categorical features
        for col, encoder in st.session_state.encoders.items():
            if col in combined_data.columns:
                combined_data[f'{col}_encoded'] = encoder.fit_transform(combined_data[col])
        
        # Prepare features and target
        features = ['mood_encoded', 'energy_encoded', 'stress_encoded']
        target = 'impulsive_count'
        
        # Create and train the model
        X = combined_data[features].values
        y = combined_data[target].values
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Save model to session state
        st.session_state.checkin_model = {
            'model': model,
            'feature_names': features
        }
    except Exception as e:
        st.error(f"Error updating prediction model: {e}")

def predict_impulse_risk(mood, energy_level, stress_level):
    """Predict the risk of impulse spending based on current mood and energy levels"""
    if st.session_state.checkin_model is None:
        # Return medium risk if no model is available
        return "Medium"
    
    try:
        # Encode inputs
        mood_encoded = st.session_state.encoders['mood'].transform([mood])[0]
        energy_encoded = st.session_state.encoders['energy'].transform([energy_level])[0]
        stress_encoded = st.session_state.encoders['stress'].transform([stress_level])[0]
        
        # Create feature vector
        features = np.array([[mood_encoded, energy_encoded, stress_encoded]])
        
        # Make prediction
        model = st.session_state.checkin_model['model']
        prediction = model.predict(features)[0]
        
        # Interpret prediction
        if prediction == 0:
            return "Low"
        elif prediction == 1:
            return "Medium"
        else:
            return "High"
    except Exception as e:
        st.error(f"Error making prediction: {e}")
        return "Medium"

def get_user_spending_patterns():
    """Analyze user spending patterns for prediction"""
    if not st.session_state.expenses:
        return {}
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.expenses)
    
    # Analyze emotions
    emotion_counts = df['emotion'].value_counts().to_dict() if 'emotion' in df.columns else {}
    
    # Analyze categories
    category_counts = df['category'].value_counts().to_dict() if 'category' in df.columns else {}
    
    # Analyze merchants
    merchant_counts = df['merchant'].value_counts().to_dict() if 'merchant' in df.columns else {}
    
    # Analyze necessity ratings
    avg_necessity = df['necessity'].mean() if 'necessity' in df.columns else 5
    
    return {
        'emotions': emotion_counts,
        'categories': category_counts,
        'merchants': merchant_counts,
        'avg_necessity': avg_necessity
    }

def get_checkin_stats():
    """Get statistics from check-ins"""
    if not st.session_state.daily_checkins:
        return {
            'avg_mood': 'No data',
            'avg_energy': 'No data',
            'avg_stress': 'No data',
            'checkin_streak': 0
        }
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.daily_checkins)
    
    # Map text values to numeric
    mood_map = {'Very Happy': 5, 'Happy': 4, 'Neutral': 3, 'Sad': 2, 'Very Sad': 1}
    energy_map = {'Very High': 5, 'High': 4, 'Moderate': 3, 'Low': 2, 'Very Low': 1}
    stress_map = {'Very Low': 5, 'Low': 4, 'Moderate': 3, 'High': 2, 'Very High': 1}
    
    # Calculate average values
    avg_mood = df['mood'].map(mood_map).mean() if 'mood' in df.columns else None
    avg_energy = df['energy'].map(energy_map).mean() if 'energy' in df.columns else None
    avg_stress = df['stress'].map(stress_map).mean() if 'stress' in df.columns else None
    
    # Calculate check-in streak
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    streak = 1
    today = datetime.date.today()
    
    for i in range(len(df) - 1):
        date1 = df.iloc[i]['date'].date()
        date2 = df.iloc[i + 1]['date'].date()
        
        if (date1 - date2).days == 1:
            streak += 1
        else:
            break
    
    # Format mood and energy levels as text
    mood_text = "No data"
    if avg_mood is not None:
        if avg_mood > 4:
            mood_text = "Very Happy"
        elif avg_mood > 3:
            mood_text = "Happy"
        elif avg_mood > 2:
            mood_text = "Neutral"
        elif avg_mood > 1:
            mood_text = "Sad"
        else:
            mood_text = "Very Sad"
    
    energy_text = "No data"
    if avg_energy is not None:
        if avg_energy > 4:
            energy_text = "Very High"
        elif avg_energy > 3:
            energy_text = "High"
        elif avg_energy > 2:
            energy_text = "Moderate"
        elif avg_energy > 1:
            energy_text = "Low"
        else:
            energy_text = "Very Low"
    
    stress_text = "No data"
    if avg_stress is not None:
        if avg_stress > 4:
            stress_text = "Very Low"
        elif avg_stress > 3:
            stress_text = "Low"
        elif avg_stress > 2:
            stress_text = "Moderate"
        elif avg_stress > 1:
            stress_text = "High"
        else:
            stress_text = "Very High"
    
    return {
        'avg_mood': mood_text,
        'avg_energy': energy_text,
        'avg_stress': stress_text,
        'checkin_streak': streak
    }