import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_emotion_spending_chart(expenses):
    """Create a bar chart showing spending by emotional state"""
    if not expenses:
        # Return empty figure if no expenses
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Emotion",
            yaxis_title="Amount ($)"
        )
        return fig
    
    # Group by emotion and sum amounts
    df = pd.DataFrame(expenses)
    emotion_totals = df.groupby('emotion')['amount'].sum().reset_index()
    emotion_totals = emotion_totals.sort_values('amount', ascending=False)
    
    # Create bar chart
    fig = px.bar(
        emotion_totals, 
        x='emotion', 
        y='amount',
        title='Spending by Emotional State',
        labels={'emotion': 'Emotional State', 'amount': 'Total Spent ($)'},
        color='emotion',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_layout(
        xaxis_title="Emotional State",
        yaxis_title="Amount Spent ($)",
        xaxis={'categoryorder':'total descending'}
    )
    
    return fig

def create_category_chart(expenses):
    """Create a pie chart showing spending by category"""
    if not expenses:
        # Return empty figure if no expenses
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Group by category and sum amounts
    df = pd.DataFrame(expenses)
    category_totals = df.groupby('category')['amount'].sum().reset_index()
    
    # Create pie chart
    fig = px.pie(
        category_totals,
        values='amount',
        names='category',
        title='Spending by Category',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    
    return fig

def create_spending_trend_chart(expenses, days=30):
    """Create a line chart showing spending trend over time"""
    if not expenses:
        # Return empty figure if no expenses
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Date",
            yaxis_title="Amount ($)"
        )
        return fig
    
    # Convert to DataFrame
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date and ensure all dates in range have values
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Create date range and group expenses by date
    date_range = pd.date_range(start=start_date, end=end_date)
    daily_spending = df.groupby(df['date'].dt.date)['amount'].sum().reindex(date_range.date, fill_value=0)
    
    # Create DataFrame for plotting
    trend_df = pd.DataFrame({
        'date': daily_spending.index,
        'amount': daily_spending.values
    })
    
    # Calculate 7-day moving average
    trend_df['moving_avg'] = trend_df['amount'].rolling(window=7, min_periods=1).mean()
    
    # Create line chart
    fig = go.Figure()
    
    # Add daily spending as bars
    fig.add_trace(go.Bar(
        x=trend_df['date'],
        y=trend_df['amount'],
        name='Daily Spending',
        marker_color='rgba(156, 165, 196, 0.4)'
    ))
    
    # Add moving average as line
    fig.add_trace(go.Scatter(
        x=trend_df['date'],
        y=trend_df['moving_avg'],
        name='7-Day Average',
        line=dict(color='rgba(49, 77, 207, 0.8)', width=3)
    ))
    
    fig.update_layout(
        title='Spending Trend (Last 30 Days)',
        xaxis_title='Date',
        yaxis_title='Amount Spent ($)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

def create_emotion_category_heatmap(expenses):
    """Create a heatmap showing spending by emotion and category"""
    if not expenses:
        # Return empty figure if no expenses
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Convert to DataFrame
    df = pd.DataFrame(expenses)
    
    # Create pivot table for heatmap
    pivot = df.pivot_table(
        index='emotion', 
        columns='category', 
        values='amount', 
        aggfunc='sum',
        fill_value=0
    )
    
    # Create heatmap
    fig = px.imshow(
        pivot,
        text_auto='.2f',
        aspect='auto',
        color_continuous_scale='Blues',
        title='Spending Heatmap by Emotion and Category'
    )
    
    fig.update_layout(
        xaxis_title='Category',
        yaxis_title='Emotion',
        coloraxis_colorbar_title='Amount ($)'
    )
    
    return fig

def create_necessity_vs_emotion_chart(expenses):
    """Create a scatter plot showing necessity rating vs. amount by emotion"""
    if not expenses:
        # Return empty figure if no expenses
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig
    
    # Convert to DataFrame
    df = pd.DataFrame(expenses)
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='necessity',
        y='amount',
        color='emotion',
        size='amount',
        hover_data=['category', 'date'],
        title='Spending Necessity vs. Amount by Emotion',
        labels={
            'necessity': 'Necessity Rating (1-10)',
            'amount': 'Amount Spent ($)',
            'emotion': 'Emotional State'
        }
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=1, dtick=1, range=[0.5, 10.5]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig
