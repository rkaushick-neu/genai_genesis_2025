import os
import pandas as pd
from datetime import datetime

def load_transactions():
    """Load transactions from CSV file"""
    try:
        # Path to transactions file
        file_path = os.path.join('data', 'transactions.csv')
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Transaction file not found at {file_path}")
            return []
        
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Convert dataframe to list of dictionaries
        transactions = df.to_dict('records')
        
        # Convert amount to float
        for t in transactions:
            t['amount'] = float(t['amount'])
        
        return transactions
    
    except Exception as e:
        print(f"Error loading transactions: {e}")
        return []

def load_masked_transactions():
    """Load masked transactions from CSV file"""
    try:
        # Path to masked transactions file
        file_path = os.path.join('data', 'transactions_masked.csv')
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Masked transaction file not found at {file_path}")
            return pd.DataFrame()  # Return empty DataFrame instead of empty list
        
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Add emotion_tag column if it doesn't exist
        if 'emotion_tag' not in df.columns:
            df['emotion_tag'] = None
        
        # Convert amount to float if it's not already
        if 'amount' in df.columns:
            df['amount'] = df['amount'].astype(float)
        
        return df
    
    except Exception as e:
        print(f"Error loading masked transactions: {e}")
        return pd.DataFrame()  # Return empty DataFrame instead of empty list

def analyze_emotional_spending(transactions):
    """Analyze spending patterns related to emotions"""
    if not isinstance(transactions, pd.DataFrame) or transactions.empty:
        return {"total": 0, "by_emotion": {}}
    
    # Group transactions by emotion
    emotional_spending = {"total": 0, "by_emotion": {}}
    
    # Skip neutral emotions
    non_neutral_transactions = transactions[transactions['emotion_tag'] != 'neutral']
    
    for _, transaction in non_neutral_transactions.iterrows():
        emotion = transaction['emotion_tag']
        amount = float(transaction['amount'])
        
        # Add to emotion-specific total
        if emotion not in emotional_spending['by_emotion']:
            emotional_spending['by_emotion'][emotion] = 0
        
        emotional_spending['by_emotion'][emotion] += amount
        emotional_spending['total'] += amount
    
    return emotional_spending

def get_transactions_by_emotion(transactions, emotion):
    """Filter transactions by emotion"""
    if not isinstance(transactions, pd.DataFrame):
        return []
    return transactions[transactions['emotion_tag'] == emotion].to_dict('records')

def get_emotional_spending_by_category(transactions, emotion):
    """Get spending by category for a specific emotion"""
    if not isinstance(transactions, pd.DataFrame):
        return {}
    
    emotion_transactions = transactions[transactions['emotion_tag'] == emotion]
    
    # Group by category and sum amounts
    category_spending = emotion_transactions.groupby('category')['amount'].sum().to_dict()
    
    return category_spending

def get_top_trigger_for_emotion(transactions, emotion):
    """Get the top spending trigger for an emotion"""
    category_spending = get_emotional_spending_by_category(transactions, emotion)
    
    if not category_spending:
        return {"category": None, "amount": 0, "time_of_day": None}
    
    # Find category with highest spending
    top_category = max(category_spending, key=category_spending.get)
    highest_amount = category_spending[top_category]
    
    # Find common time of day
    emotion_transactions = get_transactions_by_emotion(transactions, emotion)
    time_patterns = {}
    
    for transaction in emotion_transactions:
        if transaction['category'] == top_category:
            time_of_day = transaction['time_of_day']
            
            if time_of_day not in time_patterns:
                time_patterns[time_of_day] = 0
            
            time_patterns[time_of_day] += 1
    
    # Find most common time of day
    top_time = max(time_patterns, key=time_patterns.get) if time_patterns else None
    
    return {
        "category": top_category,
        "amount": highest_amount,
        "time_of_day": top_time
    }

def calculate_potential_savings(emotional_spending):
    """Calculate potential savings from reducing emotional spending"""
    # Assume we could reduce emotional spending by 50%
    return emotional_spending["total"] * 0.5

def get_spending_trends_by_emotion(transactions, days=30):
    """Get spending trends by emotion over the last N days"""
    if not isinstance(transactions, pd.DataFrame) or transactions.empty:
        return {}
    
    # Convert dates to datetime objects
    transactions['date_obj'] = pd.to_datetime(transactions['date'])
    
    # Calculate cutoff date
    latest_date = transactions['date_obj'].max()
    cutoff_date = latest_date - pd.Timedelta(days=days)
    
    # Filter transactions within time range
    recent_transactions = transactions[transactions['date_obj'] >= cutoff_date]
    
    # Group by emotion and calculate totals
    trends = recent_transactions.groupby('emotion_tag')['amount'].sum().to_dict()
    
    return trends

def get_spending_by_day_of_week(transactions, emotion=None):
    """Get spending patterns by day of week, optionally filtered by emotion"""
    if not isinstance(transactions, pd.DataFrame) or transactions.empty:
        return {}
    
    # Filter by emotion if specified
    if emotion:
        transactions = transactions[transactions['emotion_tag'] == emotion]
    
    # Group by day of week
    day_spending = transactions.groupby('day_of_week')['amount'].sum().to_dict()
    
    # Ensure all days are present
    all_days = {
        "Monday": 0, "Tuesday": 0, "Wednesday": 0, 
        "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0
    }
    all_days.update(day_spending)
    
    return all_days

def get_spending_by_time_of_day(transactions, emotion=None):
    """Get spending patterns by time of day, optionally filtered by emotion"""
    if not isinstance(transactions, pd.DataFrame) or transactions.empty:
        return {}
    
    # Filter by emotion if specified
    if emotion:
        transactions = transactions[transactions['emotion_tag'] == emotion]
    
    # Group by time of day
    time_spending = transactions.groupby('time_of_day')['amount'].sum().to_dict()
    
    # Ensure all times are present
    all_times = {
        "morning": 0, "afternoon": 0, "evening": 0, "night": 0
    }
    all_times.update(time_spending)
    
    return all_times

def get_top_merchants_by_emotion(transactions, emotion, limit=3):
    """Get top merchants for a specific emotion"""
    if not isinstance(transactions, pd.DataFrame) or transactions.empty:
        return []
    
    # Filter by emotion and group by merchant
    merchant_spending = transactions[transactions['emotion_tag'] == emotion].groupby('merchant')['amount'].sum()
    
    # Sort by amount and get top N
    top_merchants = merchant_spending.sort_values(ascending=False).head(limit)
    
    return list(zip(top_merchants.index, top_merchants.values))

def tag_transaction_with_emotion(transaction_data, emotion):
    """Add emotion tag to a transaction (for future data)"""
    transaction_data['emotion_tag'] = emotion
    return transaction_data

def calculate_average_transaction_by_emotion(transactions):
    """Calculate average transaction amount by emotion"""
    if not isinstance(transactions, pd.DataFrame) or transactions.empty:
        return {}
    
    # Group by emotion and calculate mean
    averages = transactions.groupby('emotion_tag')['amount'].mean().to_dict()
    
    return averages