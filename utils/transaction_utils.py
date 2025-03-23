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

def analyze_emotional_spending(transactions):
    """Analyze spending patterns related to emotions"""
    if not transactions:
        return {"total": 0, "by_emotion": {}}
    
    # Group transactions by emotion
    emotional_spending = {"total": 0, "by_emotion": {}}
    
    for transaction in transactions:
        # Skip neutral emotions
        if transaction['emotion_tag'] == 'neutral':
            continue
        
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
    return [t for t in transactions if t['emotion_tag'] == emotion]

def get_emotional_spending_by_category(transactions, emotion):
    """Get spending by category for a specific emotion"""
    emotion_transactions = get_transactions_by_emotion(transactions, emotion)
    
    # Group by category
    category_spending = {}
    for transaction in emotion_transactions:
        category = transaction['category']
        amount = float(transaction['amount'])
        
        if category not in category_spending:
            category_spending[category] = 0
        
        category_spending[category] += amount
    
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
    if not transactions:
        return {}
    
    # Convert dates to datetime objects
    for t in transactions:
        t['date_obj'] = datetime.strptime(t['date'], '%Y-%m-%d')
    
    # Calculate cutoff date
    latest_date = max(t['date_obj'] for t in transactions)
    cutoff_date = latest_date - pd.Timedelta(days=days)
    
    # Filter transactions within time range
    recent_transactions = [t for t in transactions if t['date_obj'] >= cutoff_date]
    
    # Group by emotion and calculate totals
    trends = {}
    for transaction in recent_transactions:
        emotion = transaction['emotion_tag']
        
        if emotion not in trends:
            trends[emotion] = 0
        
        trends[emotion] += transaction['amount']
    
    return trends

def get_spending_by_day_of_week(transactions, emotion=None):
    """Get spending patterns by day of week, optionally filtered by emotion"""
    if not transactions:
        return {}
    
    # Filter by emotion if specified
    if emotion:
        transactions = get_transactions_by_emotion(transactions, emotion)
    
    # Group by day of week
    day_spending = {
        "Monday": 0, "Tuesday": 0, "Wednesday": 0, 
        "Thursday": 0, "Friday": 0, "Saturday": 0, "Sunday": 0
    }
    
    for transaction in transactions:
        day = transaction['day_of_week']
        day_spending[day] += transaction['amount']
    
    return day_spending

def get_spending_by_time_of_day(transactions, emotion=None):
    """Get spending patterns by time of day, optionally filtered by emotion"""
    if not transactions:
        return {}
    
    # Filter by emotion if specified
    if emotion:
        transactions = get_transactions_by_emotion(transactions, emotion)
    
    # Group by time of day
    time_spending = {
        "morning": 0, "afternoon": 0, "evening": 0, "night": 0
    }
    
    for transaction in transactions:
        time = transaction['time_of_day']
        time_spending[time] += transaction['amount']
    
    return time_spending

def get_top_merchants_by_emotion(transactions, emotion, limit=3):
    """Get top merchants for a specific emotion"""
    emotion_transactions = get_transactions_by_emotion(transactions, emotion)
    
    # Group by merchant
    merchant_spending = {}
    for transaction in emotion_transactions:
        merchant = transaction['merchant']
        amount = transaction['amount']
        
        if merchant not in merchant_spending:
            merchant_spending[merchant] = 0
        
        merchant_spending[merchant] += amount
    
    # Sort by amount
    sorted_merchants = sorted(
        merchant_spending.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    # Return top N
    return sorted_merchants[:limit]

def tag_transaction_with_emotion(transaction_data, emotion):
    """Add emotion tag to a transaction (for future data)"""
    transaction_data['emotion_tag'] = emotion
    return transaction_data

def calculate_average_transaction_by_emotion(transactions):
    """Calculate average transaction amount by emotion"""
    if not transactions:
        return {}
    
    # Group by emotion
    emotion_counts = {}
    emotion_totals = {}
    
    for transaction in transactions:
        emotion = transaction['emotion_tag']
        amount = transaction['amount']
        
        if emotion not in emotion_counts:
            emotion_counts[emotion] = 0
            emotion_totals[emotion] = 0
        
        emotion_counts[emotion] += 1
        emotion_totals[emotion] += amount
    
    # Calculate averages
    averages = {}
    for emotion in emotion_totals:
        if emotion_counts[emotion] > 0:
            averages[emotion] = emotion_totals[emotion] / emotion_counts[emotion]
    
    return averages

# Add to utils/transaction_utils.py

def predict_transaction_emotions(transactions, classified_transactions):
    """
    Predict emotions for unclassified transactions based on patterns in classified ones
    """
    # Get all classified transaction patterns
    category_emotion_patterns = {}
    merchant_emotion_patterns = {}
    time_emotion_patterns = {}
    
    for t in classified_transactions:
        category = t['category']
        merchant = t['merchant']
        time = t['time_of_day']
        emotion = t['emotion_tag']
        
        # Update category-emotion patterns
        if category not in category_emotion_patterns:
            category_emotion_patterns[category] = {}
        if emotion not in category_emotion_patterns[category]:
            category_emotion_patterns[category][emotion] = 0
        category_emotion_patterns[category][emotion] += 1
        
        # Update merchant-emotion patterns
        if merchant not in merchant_emotion_patterns:
            merchant_emotion_patterns[merchant] = {}
        if emotion not in merchant_emotion_patterns[merchant]:
            merchant_emotion_patterns[merchant][emotion] = 0
        merchant_emotion_patterns[merchant][emotion] += 1
        
        # Update time-emotion patterns
        if time not in time_emotion_patterns:
            time_emotion_patterns[time] = {}
        if emotion not in time_emotion_patterns[time]:
            time_emotion_patterns[time][emotion] = 0
        time_emotion_patterns[time][emotion] += 1
    
    # Function to get most common emotion
    def get_most_common_emotion(patterns):
        if not patterns:
            return "neutral", 0.5
        
        most_common = max(patterns.items(), key=lambda x: x[1])
        total = sum(patterns.values())
        confidence = most_common[1] / total
        return most_common[0], confidence
    
    # Predict emotions for unclassified transactions
    predictions = []
    for t in transactions:
        if t.get('emotion_tag') == 'neutral' or not t.get('emotion_tag'):
            category = t['category']
            merchant = t['merchant']
            time = t['time_of_day']
            
            # Get predictions from different factors
            category_emotion, category_conf = get_most_common_emotion(
                category_emotion_patterns.get(category, {})
            )
            merchant_emotion, merchant_conf = get_most_common_emotion(
                merchant_emotion_patterns.get(merchant, {})
            )
            time_emotion, time_conf = get_most_common_emotion(
                time_emotion_patterns.get(time, {})
            )
            
            # Weight the different factors
            emotions = [
                (category_emotion, category_conf * 0.5),
                (merchant_emotion, merchant_conf * 0.3),
                (time_emotion, time_conf * 0.2)
            ]
            
            # Group by emotion and sum weights
            combined_weights = {}
            for emotion, weight in emotions:
                if emotion not in combined_weights:
                    combined_weights[emotion] = 0
                combined_weights[emotion] += weight
            
            # Select the emotion with highest combined weight
            final_emotion, confidence = get_most_common_emotion(combined_weights)
            
            predictions.append({
                'transaction': t,
                'predicted_emotion': final_emotion,
                'confidence': confidence
            })
    
    return predictions