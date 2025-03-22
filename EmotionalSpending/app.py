import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import datetime
import csv
import io
import os
from utils import initialize_session_state, add_expense, delete_expense, get_date_range, filter_expenses, load_sample_data, load_sample_checkins
from visualization import create_emotion_spending_chart, create_category_chart, create_spending_trend_chart, create_emotion_category_heatmap, create_necessity_vs_emotion_chart
from analytics import get_spending_by_category, get_spending_by_emotion, get_top_spending_categories, calculate_spending_stats, identify_spending_patterns, calculate_budget_performance
from plaid_integration import generate_link_token, exchange_public_token, get_connected_banks, fetch_transactions, check_transaction_abnormalities, save_plaid_transaction_to_expenses
from ai_assistant import chat_with_gemini, analyze_spending_patterns, get_mindfulness_exercise, get_alternative_activity, get_quick_recipe, classify_transaction_impulsivity
from daily_checkin import initialize_checkin_state, add_daily_checkin, get_todays_checkin, is_checkin_due, predict_impulse_risk, get_user_spending_patterns, get_checkin_stats
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App title and page configuration
st.set_page_config(
    page_title="Emotion-Based Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()
initialize_checkin_state()

# Load sample data for demo if no data exists
if not st.session_state.expenses:
    load_sample_data()
    
if not hasattr(st.session_state, 'daily_checkins') or not st.session_state.daily_checkins:
    load_sample_checkins()

# Handle Plaid redirect
if 'plaid_link_token' not in st.session_state:
    st.session_state.plaid_link_token = None

if 'plaid_public_token' not in st.session_state:
    st.session_state.plaid_public_token = None

# Create sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Navigate to", [
    "Dashboard", 
    "Daily Check-In", 
    "Banking Connections", 
    "Add Expense", 
    "Transaction History", 
    "Budget & Goals",
    "AI Assistant"
])

# Check if daily check-in is due and show a notification
if is_checkin_due() and page != "Daily Check-In":
    st.sidebar.warning("⚠️ Your daily emotional check-in is due!")
    if st.sidebar.button("Do Check-in Now"):
        page = "Daily Check-In"

# Show connected bank accounts in sidebar
connected_banks = get_connected_banks()
if connected_banks:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Connected Banks")
    for bank in connected_banks:
        st.sidebar.markdown(f"✓ {bank['institution_name']}")

# Main content
if page == "Dashboard":
    st.title("Spending & Emotions Dashboard")
    
    # Daily check-in prompt if needed
    if is_checkin_due():
        st.warning("⚠️ You haven't completed your daily emotional check-in yet. This helps us identify patterns that might lead to impulse spending.")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Complete Check-in"):
                page = "Daily Check-In"
                st.rerun()
    else:
        # Show check-in stats
        checkin_stats = get_checkin_stats()
        st.success(f"✓ Daily check-in complete. Your current mood: {checkin_stats['avg_mood']}, Energy: {checkin_stats['avg_energy']}, Streak: {checkin_stats['checkin_streak']} days")
    
    # Summary metrics
    if len(st.session_state.expenses) > 0:
        stats = calculate_spending_stats(st.session_state.expenses)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Spent", f"${stats['total_spent']:.2f}")
        col2.metric("Avg. Transaction", f"${stats['avg_transaction']:.2f}")
        col3.metric("Highest Emotion Spending", stats['top_emotion'])
        col4.metric("Highest Category", stats['top_category'])
        
        # Add impulse spending stat
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Unnecessary Spending", f"${stats['unnecessary_spending']:.2f}")
        col2.metric("Last 30 Days", f"${stats['last_30_days']:.2f}")
        
        # AI-generated insights
        st.subheader("AI Insights")
        with st.expander("View AI Analysis of Your Spending Patterns", expanded=True):
            ai_analysis = analyze_spending_patterns(st.session_state.expenses)
            st.write(ai_analysis)
        
        # Spending visualizations
        st.subheader("Spending by Emotional State")
        st.plotly_chart(create_emotion_spending_chart(st.session_state.expenses), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Spending by Category")
            st.plotly_chart(create_category_chart(st.session_state.expenses), use_container_width=True)
        
        with col2:
            st.subheader("Spending Trend")
            st.plotly_chart(create_spending_trend_chart(st.session_state.expenses), use_container_width=True)
        
        # Additional visualizations
        st.subheader("Spending Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_emotion_category_heatmap(st.session_state.expenses), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_necessity_vs_emotion_chart(st.session_state.expenses), use_container_width=True)
        
        # Insights
        st.subheader("Spending Insights")
        emotion_spending = get_spending_by_emotion(st.session_state.expenses)
        highest_emotion = max(emotion_spending.items(), key=lambda x: x[1]) if emotion_spending else ("No data", 0)
        
        st.info(f"💡 You tend to spend the most when feeling '{highest_emotion[0]}'. "
                f"Being aware of this pattern can help you avoid impulsive purchases.")
        
        # Recent transactions
        st.subheader("Recent Transactions")
        if st.session_state.expenses:
            recent_df = pd.DataFrame(st.session_state.expenses[-5:])
            if not recent_df.empty:
                recent_df['date'] = pd.to_datetime(recent_df['date']).dt.strftime('%Y-%m-%d')
                recent_df['amount'] = recent_df['amount'].apply(lambda x: f"${x:.2f}")
                st.table(recent_df[['date', 'category', 'amount', 'emotion', 'justification']])
    else:
        st.info("No expenses recorded yet. Add some expenses to see your dashboard!")
        
        # Quickstart options
        st.subheader("Get Started")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Connect a Bank Account"):
                page = "Banking Connections"
                st.rerun()
        
        with col2:
            if st.button("Add an Expense Manually"):
                page = "Add Expense"
                st.rerun()
        
        with col3:
            if st.button("Complete Daily Check-in"):
                page = "Daily Check-In"
                st.rerun()

elif page == "Daily Check-In":
    st.title("Daily Emotional Check-in")
    
    today_checkin = get_todays_checkin()
    
    if today_checkin:
        st.success("✓ You've already completed your check-in for today!")
        
        # Display today's check-in
        st.subheader("Today's Check-in")
        col1, col2, col3 = st.columns(3)
        col1.metric("Mood", today_checkin['mood'])
        col2.metric("Energy Level", today_checkin['energy'])
        col3.metric("Stress Level", today_checkin['stress'])
        
        st.subheader("Your Financial Goal for Today")
        st.write(today_checkin['financial_goals'])
        
        st.subheader("Notes")
        st.write(today_checkin['notes'] if today_checkin['notes'] else "No notes")
        
        # Option to update today's check-in
        if st.button("Update Today's Check-in"):
            st.session_state.update_checkin = True
            st.rerun()
    else:
        st.write("Taking a moment each day to reflect on how you're feeling helps identify patterns that might lead to impulse spending.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mood = st.selectbox("How are you feeling today?", [
                "Very Happy", "Happy", "Neutral", "Sad", "Very Sad"
            ])
            
            energy_level = st.selectbox("What's your energy level?", [
                "Very High", "High", "Moderate", "Low", "Very Low"
            ])
            
            stress_level = st.selectbox("How stressed do you feel?", [
                "Very Low", "Low", "Moderate", "High", "Very High"
            ])
        
        with col2:
            st.write("**Predicted Impulse Spending Risk:**")
            risk_level = predict_impulse_risk(mood, energy_level, stress_level)
            
            if risk_level == "High":
                st.error("⚠️ HIGH RISK: Based on your current state, you might be more susceptible to impulse purchases today.")
                st.write(get_mindfulness_exercise())
            elif risk_level == "Medium":
                st.warning("⚠️ MEDIUM RISK: Be mindful of your spending today.")
            else:
                st.success("✓ LOW RISK: You're in a good state to make thoughtful purchasing decisions.")
            
            financial_goals = st.text_area("Financial goal or intention for today:", 
                placeholder="Example: I will avoid online shopping today or I will bring lunch from home")
            
            notes = st.text_area("Any other notes about your day:", 
                placeholder="Example: Had a stressful meeting, feeling tempted to shop online")
        
        if st.button("Save Daily Check-in"):
            add_daily_checkin(mood, energy_level, stress_level, financial_goals, notes)
            st.success("Check-in recorded successfully!")
            st.balloons()
            st.rerun()
        
        # Show check-in history
        if st.session_state.daily_checkins:
            st.subheader("Check-in History")
            checkin_df = pd.DataFrame(st.session_state.daily_checkins)
            
            if not checkin_df.empty:
                checkin_df['date'] = pd.to_datetime(checkin_df['date'])
                checkin_df = checkin_df.sort_values('date', ascending=False)
                checkin_df['date'] = checkin_df['date'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    checkin_df[['date', 'mood', 'energy', 'stress', 'financial_goals']],
                    use_container_width=True,
                    hide_index=True
                )

elif page == "Banking Connections":
    st.title("Connect Your Bank Accounts")
    
    # Instructions
    st.write("""
    Connect your bank accounts to automatically import transactions and identify potential impulse purchases.
    Your data is securely handled and never shared with third parties.
    """)
    
    # Display connected banks
    if connected_banks:
        st.subheader("Connected Accounts")
        for i, bank in enumerate(connected_banks):
            st.success(f"✓ Connected to: {bank['institution_name']}")
            
            # Fetch recent transactions
            if st.button(f"View Recent Transactions from {bank['institution_name']}", key=f"view_txn_{i}"):
                with st.spinner("Fetching recent transactions..."):
                    transactions = fetch_transactions(bank['access_token'])
                    
                    if not transactions.empty:
                        st.write(f"Found {len(transactions)} recent transactions.")
                        
                        # Format for display
                        display_df = transactions.copy()
                        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                        display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
                        
                        st.dataframe(
                            display_df[['date', 'merchant', 'amount', 'category']],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Check for abnormalities
                        abnormalities = check_transaction_abnormalities(transactions)
                        if not abnormalities.empty:
                            st.subheader("Potential Impulse Purchases")
                            st.warning("We've identified transactions that might be impulse purchases based on your spending patterns:")
                            
                            for _, abnormality in abnormalities.iterrows():
                                with st.expander(f"${abnormality['amount']:.2f} at {abnormality['merchant']} on {abnormality['date'].strftime('%Y-%m-%d')}"):
                                    st.write(f"**Why flagged:** {abnormality['abnormality_type']}")
                                    st.write(f"**Details:** {abnormality['description']}")
                                    
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        emotion = st.selectbox("How were you feeling?", [
                                            "Happy", "Excited", "Stressed", "Sad", "Bored", 
                                            "Anxious", "Neutral", "Frustrated", "Tired", "Other"
                                        ], key=f"emotion_{abnormality['transaction_id']}")
                                    
                                    with col2:
                                        justification = st.text_input("Purchase justification", 
                                            key=f"justification_{abnormality['transaction_id']}")
                                    
                                    with col3:
                                        necessity = st.slider("How necessary was this?", 1, 10, 5, 
                                            key=f"necessity_{abnormality['transaction_id']}")
                                    
                                    if st.button("Save to Expense Tracker", key=f"save_{abnormality['transaction_id']}"):
                                        # Find the original transaction in the dataframe
                                        original_txn = transactions[
                                            transactions['transaction_id'] == abnormality['transaction_id']
                                        ].iloc[0] if 'transaction_id' in transactions.columns else None
                                        
                                        if original_txn is not None:
                                            save_plaid_transaction_to_expenses(
                                                original_txn, emotion, justification, necessity
                                            )
                                            st.success("Transaction saved to expense tracker!")
                                            
                                            # Get a mindful suggestion based on the emotion
                                            st.info(f"💡 Next time you feel {emotion}, try this instead:\n\n{get_alternative_activity(emotion, abnormality['category'])}")
                    else:
                        st.info("No transactions found for the selected time period.")
            
            # Import all transactions for emotional tagging
            if st.button(f"Import All Transactions from {bank['institution_name']}", key=f"import_{i}"):
                with st.spinner("Importing transactions..."):
                    transactions = fetch_transactions(bank['access_token'])
                    
                    if not transactions.empty:
                        st.session_state.plaid_import_transactions = transactions
                        st.session_state.current_import_index = 0
                        st.rerun()
                    else:
                        st.info("No transactions found to import.")
    
    # Handle transaction import workflow
    if hasattr(st.session_state, 'plaid_import_transactions') and hasattr(st.session_state, 'current_import_index'):
        transactions = st.session_state.plaid_import_transactions
        
        if st.session_state.current_import_index < len(transactions):
            st.subheader("Tag Transactions with Emotional Data")
            
            # Get current transaction
            current_txn = transactions.iloc[st.session_state.current_import_index]
            
            # Display transaction details
            st.write(f"Transaction {st.session_state.current_import_index + 1} of {len(transactions)}")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Merchant", current_txn['merchant'])
            col2.metric("Amount", f"${current_txn['amount']:.2f}")
            col3.metric("Date", current_txn['date'].strftime('%Y-%m-%d'))
            
            # Get user input
            col1, col2 = st.columns(2)
            
            with col1:
                emotion = st.selectbox("How were you feeling during this purchase?", [
                    "Happy", "Excited", "Stressed", "Sad", "Bored", 
                    "Anxious", "Neutral", "Frustrated", "Tired", "Other"
                ])
            
            with col2:
                necessity = st.slider("How necessary was this purchase?", 1, 10, 5, 
                    help="1 = Completely unnecessary, 10 = Absolutely essential")
            
            justification = st.text_area("Purchase justification (optional)", 
                placeholder="Why did you make this purchase? Was it planned or impulsive?")
            
            # AI assistance
            user_patterns = get_user_spending_patterns()
            impulsivity_prediction = classify_transaction_impulsivity(current_txn, user_patterns)
            
            if impulsivity_prediction.get('is_impulsive'):
                st.warning(f"⚠️ Our AI suggests this might have been an impulse purchase: {impulsivity_prediction.get('reasoning', '')}")
            
            # Next/Skip buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Save and Next"):
                    save_plaid_transaction_to_expenses(current_txn, emotion, justification, necessity)
                    st.session_state.current_import_index += 1
                    st.rerun()
            
            with col2:
                if st.button("Skip"):
                    st.session_state.current_import_index += 1
                    st.rerun()
            
            with col3:
                if st.button("Stop Import"):
                    del st.session_state.plaid_import_transactions
                    del st.session_state.current_import_index
                    st.rerun()
        else:
            # Finished importing
            st.success("All transactions have been processed!")
            del st.session_state.plaid_import_transactions
            del st.session_state.current_import_index
    
    # Connect a new bank
    st.subheader("Connect a New Account")
    
    # Generate Plaid Link token if not already generated
    if not st.session_state.plaid_link_token:
        if st.button("Connect a Bank Account"):
            with st.spinner("Preparing secure connection..."):
                # Generate a unique user ID (in a real app, this would be persistent)
                user_id = f"user_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                link_token = generate_link_token(user_id)
                
                if link_token:
                    st.session_state.plaid_link_token = link_token
                    st.rerun()
    else:
        # Display Plaid Link button using the token
        st.markdown(
            f"""
            <html>
            <head>
              <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
            </head>
            <body>
              <button onclick="loadPlaidLink()">Continue to Connect Bank</button>
              <script>
                function loadPlaidLink() {{
                  const handler = Plaid.create({{
                    token: '{st.session_state.plaid_link_token}',
                    onSuccess: (public_token, metadata) => {{
                      console.log('Success!', public_token, metadata);
                      // In a real app, you would send the public_token to your server for exchange
                      // For this demo, store in session state
                      localStorage.setItem('plaid_public_token', public_token);
                      localStorage.setItem('plaid_metadata', JSON.stringify(metadata));
                      alert('Account connected! The public token is stored in localStorage for demonstration. Check the console for details.');
                    }},
                    onExit: (err, metadata) => {{
                      console.log('Exited', err, metadata);
                    }},
                  }});
                  handler.open();
                }}
              </script>
            </body>
            </html>
            """,
            unsafe_allow_html=True
        )
        
        # In a real app, you would handle the public token exchange server-side
        # For this demo, provide a field to manually enter the public token
        public_token = st.text_input("Public token (from browser console)", 
            help="In a real app, this would be handled automatically through a server endpoint")
        
        if st.button("Complete Connection") and public_token:
            with st.spinner("Completing bank connection..."):
                access_token, item_id = exchange_public_token(public_token)
                
                if access_token and item_id:
                    st.success("Bank account connected successfully!")
                    st.session_state.plaid_link_token = None  # Reset for next connection
                    st.rerun()
                else:
                    st.error("Failed to complete bank connection. Please try again.")
        
        # Option to cancel and reset
        if st.button("Cancel"):
            st.session_state.plaid_link_token = None
            st.rerun()

elif page == "Add Expense":
    st.title("Record New Expense")
    
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("Date", datetime.date.today())
        amount = st.number_input("Amount ($)", min_value=0.01, format="%.2f")
        category = st.selectbox("Category", [
            "Food & Dining", "Shopping", "Entertainment", "Transportation", 
            "Utilities", "Housing", "Healthcare", "Personal Care", 
            "Education", "Travel", "Gifts & Donations", "Other"
        ])
        merchant = st.text_input("Merchant/Store (optional)")
    
    with col2:
        emotion = st.selectbox("How were you feeling?", [
            "Happy", "Excited", "Stressed", "Sad", "Bored", 
            "Anxious", "Neutral", "Frustrated", "Tired", "Other"
        ])
        justification = st.text_area("Purchase Justification", 
            placeholder="Why did you make this purchase? Was it planned or impulsive?")
        necessity = st.slider("How necessary was this purchase?", 1, 10, 5, 
            help="1 = Completely unnecessary, 10 = Absolutely essential")
    
    if necessity <= 3:
        st.warning("This purchase seems non-essential. Would you like some mindfulness tips?")
        with st.expander("Show mindfulness exercise"):
            st.write(get_mindfulness_exercise())
    
    if st.button("Save Expense"):
        # Create expense object with optional merchant field
        expense = {
            'date': date.strftime('%Y-%m-%d'),
            'amount': float(amount),
            'category': category,
            'emotion': emotion,
            'justification': justification,
            'necessity': necessity,
            'source': 'manual'
        }
        
        # Add merchant if provided
        if merchant:
            expense['merchant'] = merchant
        
        # Add to expenses list
        st.session_state.expenses.append(expense)
        
        # Sort expenses by date (newest first)
        st.session_state.expenses = sorted(
            st.session_state.expenses, 
            key=lambda x: x['date'], 
            reverse=True
        )
        
        st.success("Expense recorded successfully!")
        st.balloons()
        
        # If purchase was impulsive (necessity <= 4), offer alternatives
        if necessity <= 4:
            st.subheader("Next time you feel this way...")
            st.info(get_alternative_activity(emotion, category))

elif page == "Transaction History":
    st.title("Transaction History")
    
    # Filters
    st.subheader("Filter Transactions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_category = st.multiselect("Category", 
            ["All"] + list(set(expense.get('category', 'Uncategorized') for expense in st.session_state.expenses)),
            default="All")
    
    with col2:
        filter_emotion = st.multiselect("Emotion", 
            ["All"] + list(set(expense.get('emotion', 'Unknown') for expense in st.session_state.expenses)),
            default="All")
    
    with col3:
        if st.session_state.expenses:
            start_date, end_date = get_date_range()
            date_range = st.date_input(
                "Date Range",
                [start_date, end_date]
            )
        else:
            date_range = st.date_input("Date Range", [datetime.date.today(), datetime.date.today()])
    
    # Source filter
    source_options = ["All"]
    if any(expense.get('source') == 'plaid' for expense in st.session_state.expenses):
        source_options.append("Bank Import")
    if any(expense.get('source') == 'manual' for expense in st.session_state.expenses):
        source_options.append("Manual Entry")
    
    filter_source = st.selectbox("Source", source_options, index=0)
    
    # Apply filters
    filtered_expenses = filter_expenses(
        category=None if "All" in filter_category else filter_category,
        emotion=None if "All" in filter_emotion else filter_emotion,
        start_date=date_range[0] if len(date_range) >= 1 else None,
        end_date=date_range[1] if len(date_range) >= 2 else None
    )
    
    # Filter by source
    if filter_source != "All":
        source_value = 'plaid' if filter_source == "Bank Import" else 'manual'
        filtered_expenses = [
            expense for expense in filtered_expenses
            if expense.get('source', 'manual') == source_value
        ]
    
    # Display transactions
    if filtered_expenses:
        df = pd.DataFrame(filtered_expenses)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False)
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        df['amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
        
        # Add source label if present
        if 'source' in df.columns:
            df['source'] = df['source'].apply(lambda x: "Bank Import" if x == 'plaid' else "Manual Entry")
        
        # Determine columns to display
        display_columns = ['date', 'category', 'amount', 'emotion', 'necessity']
        if 'merchant' in df.columns:
            display_columns.insert(2, 'merchant')
        if 'source' in df.columns:
            display_columns.append('source')
        if 'justification' in df.columns:
            display_columns.append('justification')
        
        st.dataframe(
            df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Option to delete transactions
        if st.button("Delete Selected Transaction"):
            delete_index = st.number_input("Enter the row index to delete (0 is the most recent)", 
                                          min_value=0, 
                                          max_value=len(filtered_expenses)-1 if filtered_expenses else 0)
            delete_expense(delete_index)
            st.success("Transaction deleted!")
            st.rerun()
        
        # Export data
        if st.button("Export Data to CSV"):
            csv_data = io.StringIO()
            writer = csv.DictWriter(csv_data, fieldnames=df.columns)
            writer.writeheader()
            writer.writerows(filtered_expenses)
            
            st.download_button(
                label="Download CSV",
                data=csv_data.getvalue(),
                file_name="expense_emotion_data.csv",
                mime="text/csv"
            )
    else:
        st.info("No transactions found with the selected filters.")

elif page == "Budget & Goals":
    st.title("Budget & Goals")
    
    # Monthly budget setting
    st.subheader("Set Monthly Budget")
    
    if 'monthly_budget' not in st.session_state:
        st.session_state.monthly_budget = 1000.0
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_budget = st.number_input("Monthly Budget ($)", 
                                    min_value=0.0, 
                                    value=st.session_state.monthly_budget, 
                                    format="%.2f")
        
        if st.button("Update Budget"):
            st.session_state.monthly_budget = new_budget
            st.success(f"Monthly budget updated to ${new_budget:.2f}")
    
    # Current month's spending and budget performance
    with col2:
        budget_performance = calculate_budget_performance(
            st.session_state.expenses, 
            st.session_state.monthly_budget,
            st.session_state.category_budgets if 'category_budgets' in st.session_state else None
        )
        
        current_month_total = budget_performance['current_spending']
        budget_remaining = budget_performance['remaining']
        
        st.metric("Current Month's Spending", f"${current_month_total:.2f}")
        st.metric("Budget Remaining", f"${budget_remaining:.2f}", 
                 delta=-current_month_total if budget_remaining >= 0 else budget_remaining)
    
    # Budget progress bar
    progress = min(budget_performance['percent_used'] / 100, 1.0)
    st.progress(progress)
    
    if progress >= 0.8:
        st.warning(f"⚠️ You've used {budget_performance['percent_used']:.1f}% of your monthly budget!")
    
    # Daily spending allowance
    if budget_performance['days_remaining'] > 0:
        st.info(f"💡 Daily spending allowance for the rest of this month: ${budget_performance['daily_remaining']:.2f}/day for {budget_performance['days_remaining']} days")
    
    # AI-assisted budget recommendations
    st.subheader("AI Budget Recommendations")
    if st.button("Get Personalized Budget Advice"):
        patterns = identify_spending_patterns(st.session_state.expenses)
        user_patterns = get_user_spending_patterns()
        
        if patterns and user_patterns:
            # Pass this data to the AI for analysis
            with st.spinner("Analyzing your spending patterns..."):
                advice = analyze_spending_patterns(st.session_state.expenses)
                st.write(advice)
        else:
            st.info("We need more transaction data to provide personalized recommendations.")
    
    # Emotion spending goals
    st.subheader("Emotional Spending Goals")
    st.write("Set goals to reduce spending in specific emotional states")
    
    emotion_data = get_spending_by_emotion(st.session_state.expenses)
    
    if not emotion_data:
        st.info("Add some expenses to set emotion-based spending goals.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            target_emotion = st.selectbox("Select Emotion to Target", list(emotion_data.keys()))
            current_emotion_spending = emotion_data.get(target_emotion, 0)
            st.metric(f"Current {target_emotion} Spending", f"${current_emotion_spending:.2f}")
        
        with col2:
            target_reduction = st.slider("Reduction Target (%)", 5, 50, 20)
            target_amount = current_emotion_spending * (1 - target_reduction/100)
            st.metric(f"Target {target_emotion} Spending", f"${target_amount:.2f}", 
                     delta=-current_emotion_spending * target_reduction/100)
        
        st.info(f"💡 Tip: When feeling {target_emotion}, try implementing a 24-hour waiting period before making non-essential purchases.")
        
        # AI suggestions for avoiding emotional spending
        if st.button(f"Get tips for managing {target_emotion} spending"):
            with st.spinner("Generating personalized advice..."):
                alternative = get_alternative_activity(target_emotion, 
                    list(get_spending_by_category(st.session_state.expenses).keys())[0] if get_spending_by_category(st.session_state.expenses) else "Shopping")
                st.write(alternative)
    
    # Category spending goals
    st.subheader("Category Spending Goals")
    category_data = get_spending_by_category(st.session_state.expenses)
    
    if not category_data:
        st.info("Add some expenses to set category-based spending goals.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            target_category = st.selectbox("Select Category to Target", list(category_data.keys()))
            current_category_spending = category_data.get(target_category, 0)
            st.metric(f"Current {target_category} Spending", f"${current_category_spending:.2f}")
        
        with col2:
            category_target = st.number_input(f"Monthly Budget for {target_category} ($)", 
                                            min_value=0.0, 
                                            value=current_category_spending,
                                            format="%.2f")
            
            if st.button("Set Category Budget"):
                if 'category_budgets' not in st.session_state:
                    st.session_state.category_budgets = {}
                st.session_state.category_budgets[target_category] = category_target
                st.success(f"Budget for {target_category} set to ${category_target:.2f}")
        
        # Check category budget performance
        if 'category_budgets' in st.session_state and target_category in st.session_state.category_budgets:
            category_budget = st.session_state.category_budgets[target_category]
            category_used = (current_category_spending / category_budget) * 100 if category_budget > 0 else 100
            
            st.progress(min(category_used / 100, 1.0))
            
            if category_used > 90:
                st.warning(f"⚠️ You've used {category_used:.1f}% of your {target_category} budget!")
            elif category_used < 50:
                st.success(f"✓ You're doing well with your {target_category} budget! ({category_used:.1f}% used)")

elif page == "AI Assistant":
    st.title("AI Wellness Coach")
    
    # Initialize chat history if it doesn't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Coach:** {message['content']}")
    
    # Chat input
    user_message = st.text_input("Ask your financial wellness coach anything...", 
        placeholder="Example: I'm feeling stressed and want to shop online. What should I do?")
    
    # Quick prompt buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("I need a budget-friendly recipe"):
            user_message = "Can you suggest a quick, budget-friendly recipe for dinner tonight?"
    
    with col2:
        if st.button("Help me avoid impulse shopping"):
            user_message = "I'm feeling the urge to buy something online right now. Help me resist."
    
    with col3:
        if st.button("Stress reduction techniques"):
            user_message = "I'm feeling stressed about money. What are some free ways to reduce stress?"
    
    # Process chat
    if user_message:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = chat_with_gemini(user_message, st.session_state.chat_history)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
        
        # Rerun to show new messages
        st.rerun()
    
    # Additional resources
    with st.expander("Quick Wellness Resources"):
        tab1, tab2, tab3 = st.tabs(["Mindfulness Exercise", "Budget Recipe", "Spending Alternative"])
        
        with tab1:
            st.subheader("1-Minute Mindfulness Exercise")
            st.write(get_mindfulness_exercise())
        
        with tab2:
            st.subheader("Quick Budget-Friendly Recipe")
            st.write(get_quick_recipe())
        
        with tab3:
            st.subheader("Alternative to Shopping")
            st.write(get_alternative_activity("Stressed", "Shopping"))

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This app helps you track spending in relation to your emotional state "
    "to identify patterns and prevent impulsive purchases. "
    "Connect your bank accounts for real-time transaction monitoring."
)
