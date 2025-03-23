from datetime import datetime
from utils.transaction_utils import get_transactions_by_emotion

def analyze_spending_patterns(transactions, emotion):
    """Analyze spending patterns for a specific emotion"""
    # Filter transactions by emotion
    emotion_transactions = get_transactions_by_emotion(transactions, emotion)
    
    if not emotion_transactions:
        return None
    
    # 1. Analyze spending by category
    category_spending = {}
    for transaction in emotion_transactions:
        category = transaction["category"]
        amount = float(transaction["amount"])
        
        if category not in category_spending:
            category_spending[category] = {
                "count": 0,
                "total": 0,
                "transactions": []
            }
        
        category_spending[category]["count"] += 1
        category_spending[category]["total"] += amount
        category_spending[category]["transactions"].append(transaction)
    
    # Calculate probabilities and averages
    total_transactions = len(emotion_transactions)
    category_patterns = {}
    
    for category, data in category_spending.items():
        category_patterns[category] = {
            "probability": data["count"] / total_transactions,
            "avg_amount": data["total"] / data["count"],
            "frequency": data["count"]
        }
    
    # 2. Analyze spending by time of day
    time_patterns = {}
    for transaction in emotion_transactions:
        time_of_day = transaction["time_of_day"]
        
        if time_of_day not in time_patterns:
            time_patterns[time_of_day] = 0
        
        time_patterns[time_of_day] += 1
    
    # Calculate time probabilities
    time_distribution = {}
    for time, count in time_patterns.items():
        time_distribution[time] = count / total_transactions
    
    # 3. Analyze spending by day of week
    day_patterns = {}
    for transaction in emotion_transactions:
        day_of_week = transaction["day_of_week"]
        
        if day_of_week not in day_patterns:
            day_patterns[day_of_week] = 0
        
        day_patterns[day_of_week] += 1
    
    # Calculate day probabilities
    day_distribution = {}
    for day, count in day_patterns.items():
        day_distribution[day] = count / total_transactions
    
    # 4. Find most common category-time combinations
    category_time_patterns = {}
    for transaction in emotion_transactions:
        key = f"{transaction['category']}-{transaction['time_of_day']}"
        
        if key not in category_time_patterns:
            category_time_patterns[key] = {
                "count": 0,
                "total": 0
            }
        
        category_time_patterns[key]["count"] += 1
        category_time_patterns[key]["total"] += float(transaction["amount"])
    
    # Find the most common pattern
    top_pattern = None
    top_count = 0
    
    for pattern, data in category_time_patterns.items():
        if data["count"] > top_count:
            top_count = data["count"]
            top_pattern = {
                "pattern": pattern,
                "count": data["count"],
                "probability": data["count"] / total_transactions,
                "avg_amount": data["total"] / data["count"]
            }
    
    return {
        "category_patterns": category_patterns,
        "time_distribution": time_distribution,
        "day_distribution": day_distribution,
        "top_pattern": top_pattern,
        "total_transactions": total_transactions
    }

def get_current_context():
    """Get current time context (time of day, day of week)"""
    now = datetime.now()
    hours = now.hour
    
    # Determine time of day
    if 5 <= hours < 12:
        time_of_day = "morning"
    elif 12 <= hours < 17:
        time_of_day = "afternoon"
    elif 17 <= hours < 21:
        time_of_day = "evening"
    else:
        time_of_day = "night"
    
    # Get day of week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week = days[now.weekday()]
    
    return {
        "time_of_day": time_of_day,
        "day_of_week": day_of_week
    }

def generate_prediction(transactions, emotion):
    """Generate predictions based on emotion and spending patterns"""
    # Get patterns for this emotion
    patterns = analyze_spending_patterns(transactions, emotion)
    
    if not patterns or not patterns.get("category_patterns"):
        return None
    
    # Get current context
    context = get_current_context()
    
    # Find highest probability category for current time
    highest_prob = 0
    likely_category = None
    likely_amount = 0
    
    for category, data in patterns["category_patterns"].items():
        # Adjust probability based on time of day match
        adjusted_prob = data["probability"]
        
        # If this time of day increases probability, adjust up
        if patterns["time_distribution"].get(context["time_of_day"], 0) > 0.3:
            adjusted_prob *= 1.5
        
        # If this day of week increases probability, adjust up
        if patterns["day_distribution"].get(context["day_of_week"], 0) > 0.3:
            adjusted_prob *= 1.3
        
        if adjusted_prob > highest_prob:
            highest_prob = adjusted_prob
            likely_category = category
            likely_amount = data["avg_amount"]
    
    # Only return prediction if probability is significant
    if highest_prob >= 0.3:
        return {
            "emotion": emotion,
            "category": likely_category,
            "probability": highest_prob,
            "estimated_amount": f"{likely_amount:.2f}",
            "time_of_day": context["time_of_day"],
            "day_of_week": context["day_of_week"]
        }
    
    return None