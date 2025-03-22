import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_spending_by_category(expenses):
    """Calculate total spending by category"""
    if not expenses:
        return {}
    
    category_totals = {}
    for expense in expenses:
        category = expense['category']
        amount = expense['amount']
        
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    return category_totals

def get_spending_by_emotion(expenses):
    """Calculate total spending by emotion"""
    if not expenses:
        return {}
    
    emotion_totals = {}
    for expense in expenses:
        emotion = expense['emotion']
        amount = expense['amount']
        
        if emotion in emotion_totals:
            emotion_totals[emotion] += amount
        else:
            emotion_totals[emotion] = amount
    
    return emotion_totals

def get_top_spending_categories(expenses, top_n=3):
    """Return the top N spending categories"""
    category_totals = get_spending_by_category(expenses)
    
    # Sort categories by amount
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Return top N or all if fewer than N
    return sorted_categories[:min(top_n, len(sorted_categories))]

def get_top_spending_emotions(expenses, top_n=3):
    """Return the top N emotional states by spending"""
    emotion_totals = get_spending_by_emotion(expenses)
    
    # Sort emotions by amount
    sorted_emotions = sorted(emotion_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Return top N or all if fewer than N
    return sorted_emotions[:min(top_n, len(sorted_emotions))]

def calculate_spending_stats(expenses):
    """Calculate various spending statistics"""
    if not expenses:
        return {
            'total_spent': 0,
            'avg_transaction': 0,
            'top_emotion': 'N/A',
            'top_category': 'N/A',
            'last_30_days': 0,
            'unnecessary_spending': 0
        }
    
    # Calculate total spent
    total_spent = sum(expense['amount'] for expense in expenses)
    
    # Calculate average transaction
    avg_transaction = total_spent / len(expenses)
    
    # Get top emotion and category
    top_emotions = get_top_spending_emotions(expenses, 1)
    top_categories = get_top_spending_categories(expenses, 1)
    
    top_emotion = top_emotions[0][0] if top_emotions else 'N/A'
    top_category = top_categories[0][0] if top_categories else 'N/A'
    
    # Calculate spending in last 30 days
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    last_30_days_spent = sum(
        expense['amount'] for expense in expenses
        if datetime.strptime(expense['date'], '%Y-%m-%d') >= thirty_days_ago
    )
    
    # Calculate "unnecessary" spending (necessity <= 5)
    unnecessary_spending = sum(
        expense['amount'] for expense in expenses
        if expense['necessity'] <= 5
    )
    
    return {
        'total_spent': total_spent,
        'avg_transaction': avg_transaction,
        'top_emotion': top_emotion,
        'top_category': top_category,
        'last_30_days': last_30_days_spent,
        'unnecessary_spending': unnecessary_spending
    }

def identify_spending_patterns(expenses):
    """Identify patterns in spending behavior"""
    if not expenses:
        return []
    
    patterns = []
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    
    # Pattern 1: Emotional spending correlations
    emotion_spending = get_spending_by_emotion(expenses)
    if emotion_spending:
        max_emotion = max(emotion_spending.items(), key=lambda x: x[1])
        patterns.append({
            'type': 'emotion_correlation',
            'description': f"You spend the most when feeling '{max_emotion[0]}'",
            'data': {
                'emotion': max_emotion[0],
                'amount': max_emotion[1]
            }
        })
    
    # Pattern 2: Day of week spending patterns
    if 'date' in df.columns:
        df['day_of_week'] = df['date'].dt.day_name()
        day_spending = df.groupby('day_of_week')['amount'].sum()
        
        if not day_spending.empty:
            max_day = day_spending.idxmax()
            patterns.append({
                'type': 'day_of_week',
                'description': f"You tend to spend the most on {max_day}s",
                'data': {
                    'day': max_day,
                    'amount': day_spending[max_day]
                }
            })
    
    # Pattern 3: Low necessity but high spending emotions
    if 'necessity' in df.columns and 'emotion' in df.columns:
        low_necessity = df[df['necessity'] <= 4]
        
        if not low_necessity.empty:
            low_necessity_emotions = low_necessity.groupby('emotion')['amount'].sum()
            if not low_necessity_emotions.empty:
                top_unnecessary_emotion = low_necessity_emotions.idxmax()
                patterns.append({
                    'type': 'unnecessary_spending',
                    'description': f"When feeling '{top_unnecessary_emotion}', you make more unnecessary purchases",
                    'data': {
                        'emotion': top_unnecessary_emotion,
                        'amount': low_necessity_emotions[top_unnecessary_emotion]
                    }
                })
    
    return patterns

def calculate_budget_performance(expenses, monthly_budget, category_budgets=None):
    """Calculate performance against budget"""
    if not expenses or monthly_budget <= 0:
        return {
            'total_budget': monthly_budget,
            'current_spending': 0,
            'remaining': monthly_budget,
            'percent_used': 0,
            'days_remaining': 30,
            'daily_remaining': monthly_budget / 30 if monthly_budget > 0 else 0,
            'category_performance': {}
        }
    
    # Get current month's expenses
    now = datetime.now()
    current_month_start = datetime(now.year, now.month, 1)
    next_month_start = current_month_start + timedelta(days=32)
    next_month_start = datetime(next_month_start.year, next_month_start.month, 1)
    
    current_month_expenses = [
        expense for expense in expenses
        if current_month_start <= datetime.strptime(expense['date'], '%Y-%m-%d') < next_month_start
    ]
    
    # Calculate current spending
    current_spending = sum(expense['amount'] for expense in current_month_expenses)
    
    # Calculate remaining budget
    remaining = monthly_budget - current_spending
    
    # Calculate percent used
    percent_used = (current_spending / monthly_budget) * 100 if monthly_budget > 0 else 100
    
    # Calculate days remaining in month
    days_in_month = (next_month_start - current_month_start).days
    days_elapsed = (now - current_month_start).days
    days_remaining = max(0, days_in_month - days_elapsed)
    
    # Calculate daily remaining budget
    daily_remaining = remaining / days_remaining if days_remaining > 0 else 0
    
    # Calculate category performance if category budgets provided
    category_performance = {}
    if category_budgets:
        category_spending = get_spending_by_category(current_month_expenses)
        
        for category, budget in category_budgets.items():
            spent = category_spending.get(category, 0)
            category_performance[category] = {
                'budget': budget,
                'spent': spent,
                'remaining': budget - spent,
                'percent_used': (spent / budget) * 100 if budget > 0 else 100
            }
    
    return {
        'total_budget': monthly_budget,
        'current_spending': current_spending,
        'remaining': remaining,
        'percent_used': percent_used,
        'days_remaining': days_remaining,
        'daily_remaining': daily_remaining,
        'category_performance': category_performance
    }
