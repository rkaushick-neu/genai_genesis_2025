import os
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import random
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Flag to track if we're using real Plaid or demo mode
USING_REAL_PLAID = False

# Try to import Plaid
try:
    import plaid
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode
    from plaid.model.link_token_create_request_update import LinkTokenCreateRequestUpdate
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
    PLAID_IMPORTED = True
except ImportError:
    PLAID_IMPORTED = False
    st.warning("Plaid library not properly installed or configured. Running in demo mode.")

def get_plaid_client():
    """Initialize and return a Plaid client"""
    global USING_REAL_PLAID
    
    # Check if Plaid is imported
    if not PLAID_IMPORTED:
        st.warning("Plaid integration is in demo mode. Connect a real bank account by adding Plaid API credentials.")
        return None
    
    client_id = os.getenv('PLAID_CLIENT_ID')
    secret = os.getenv('PLAID_SECRET')
    environment = os.getenv('PLAID_ENV', 'sandbox')
    
    # Check if credentials are available
    if not client_id or not secret:
        st.warning("Plaid API credentials not found. Running in demo mode.")
        return None
    
    try:
        # Configure Plaid client
        plaid_config = {
            'client_id': client_id,
            'secret': secret,
            'environment': environment
        }
        
        USING_REAL_PLAID = True
        return plaid.ApiClient(plaid.Configuration(**plaid_config))
    except Exception as e:
        st.error(f"Error initializing Plaid client: {str(e)}")
        return None

def generate_link_token(client_user_id, update_mode=False, access_token=None):
    """Generate a link token for Plaid Link initialization"""
    global USING_REAL_PLAID
    
    if not PLAID_IMPORTED or not USING_REAL_PLAID:
        # In demo mode, return a demo link token
        st.info("⚠️ Using demo mode for Plaid integration. To connect to real banks, please add Plaid API credentials.")
        # Return a fake link token for demo purposes
        return "demo-link-token-" + str(uuid.uuid4())
    
    try:
        client = get_plaid_client()
        if client is None:
            # Fallback to demo mode if client couldn't be initialized
            st.info("⚠️ Using demo mode for Plaid. To connect real banks, add valid Plaid API credentials.")
            return "demo-link-token-" + str(uuid.uuid4())
            
        link_token_api = plaid.PlaidApi(client)
        
        # Create user object
        user = LinkTokenCreateRequestUser(
            client_user_id=client_user_id
        )
        
        request_dict = {
            'user': user,
            'client_name': 'Emotion-Based Expense Tracker',
            'products': [Products('transactions')],
            'country_codes': [CountryCode('US')],
            'language': 'en'
        }
        
        # If update mode, add the access token
        if update_mode and access_token:
            request_dict['update'] = LinkTokenCreateRequestUpdate(access_token=access_token)
        
        # Create request
        request = LinkTokenCreateRequest(**request_dict)
        
        # Create link token
        response = link_token_api.link_token_create(request)
        
        return response['link_token']
    except Exception as e:
        st.error(f"Failed to generate link token: {str(e)}")
        return "demo-link-token-" + str(uuid.uuid4())

def exchange_public_token(public_token):
    """Exchange public token for access token"""
    global USING_REAL_PLAID
    
    # Check if we're using demo mode
    if not PLAID_IMPORTED or not USING_REAL_PLAID or public_token.startswith("demo-link-token"):
        # In demo mode, create demo access token and item ID
        if 'plaid_access_tokens' not in st.session_state:
            st.session_state.plaid_access_tokens = {}
            
        demo_item_id = "demo-item-" + str(uuid.uuid4())
        demo_access_token = "demo-access-token-" + str(uuid.uuid4())
        
        # Store in session state
        st.session_state.plaid_access_tokens[demo_item_id] = demo_access_token
        
        # Add demo bank to show in UI
        if 'demo_banks' not in st.session_state:
            st.session_state.demo_banks = []
            
        st.session_state.demo_banks.append({
            "item_id": demo_item_id,
            "access_token": demo_access_token,
            "institution_name": "Demo Bank " + str(len(st.session_state.demo_banks) + 1)
        })
        
        st.success("Successfully connected to Demo Bank (running in demo mode)")
        return demo_access_token, demo_item_id
    
    try:
        client = get_plaid_client()
        if client is None:
            # Fallback to demo mode
            return exchange_public_token("demo-link-token")
            
        api = plaid.PlaidApi(client)
        
        request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        
        response = api.item_public_token_exchange(request)
        access_token = response['access_token']
        item_id = response['item_id']
        
        # Store access token in session state
        if 'plaid_access_tokens' not in st.session_state:
            st.session_state.plaid_access_tokens = {}
        
        st.session_state.plaid_access_tokens[item_id] = access_token
        
        return access_token, item_id
    except Exception as e:
        st.error(f"Failed to exchange public token: {str(e)}")
        # Fallback to demo mode on error
        return exchange_public_token("demo-link-token")

def get_institution_name(institution_id):
    """Get bank name by institution ID"""
    try:
        client = get_plaid_client()
        api = plaid.PlaidApi(client)
        
        request = InstitutionsGetByIdRequest(
            institution_id=institution_id,
            country_codes=[CountryCode('US')]
        )
        
        response = api.institutions_get_by_id(request)
        return response['institution']['name']
    except plaid.ApiException as e:
        st.error(f"Failed to get institution name: {e}")
        return "Unknown Institution"

def get_connected_banks():
    """Get a list of all connected bank accounts"""
    global USING_REAL_PLAID
    
    # Return demo banks if we're in demo mode
    if not PLAID_IMPORTED or not USING_REAL_PLAID:
        if 'demo_banks' in st.session_state and st.session_state.demo_banks:
            return st.session_state.demo_banks
    
    # Check for regular banks
    if 'plaid_access_tokens' not in st.session_state:
        return []
    
    banks = []
    
    # Add demo banks first
    if 'demo_banks' in st.session_state:
        banks.extend(st.session_state.demo_banks)
    
    # For actual Plaid tokens, try to get real bank info
    for item_id, access_token in st.session_state.plaid_access_tokens.items():
        # Skip demo tokens
        if access_token.startswith("demo-access-token"):
            continue
            
        try:
            client = get_plaid_client()
            if client is None:
                # If not connected to Plaid, just show a generic name
                banks.append({
                    'item_id': item_id,
                    'access_token': access_token,
                    'institution_name': 'Connected Bank'
                })
                continue
                
            api = plaid.PlaidApi(client)
            
            # Get item information
            item_response = api.item_get({'access_token': access_token})
            institution_id = item_response['item']['institution_id']
            institution_name = get_institution_name(institution_id)
            
            banks.append({
                'item_id': item_id,
                'access_token': access_token,
                'institution_name': institution_name
            })
        except Exception as e:
            st.error(f"Failed to retrieve bank information: {str(e)}")
            # Still add the bank with a generic name
            banks.append({
                'item_id': item_id,
                'access_token': access_token,
                'institution_name': 'Connected Bank'
            })
    
    return banks

def generate_demo_transactions(bank_name, start_date=None, end_date=None):
    """Generate demo transactions for testing"""
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.now().date()
        
    # Convert dates to datetime for easier manipulation
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.min.time())
    
    # Define demo merchants by category
    merchants_by_category = {
        'FOOD_AND_DRINK': ['Starbucks', 'Chipotle', 'Whole Foods', 'Local Restaurant', 'Grubhub', 'DoorDash'],
        'GENERAL_MERCHANDISE': ['Amazon', 'Target', 'Walmart', 'Best Buy', 'Apple Store', 'IKEA'],
        'ENTERTAINMENT': ['Netflix', 'Spotify', 'Steam', 'Movie Theater', 'Concert Tickets', 'Bowling Alley'],
        'TRANSPORTATION': ['Uber', 'Lyft', 'Gas Station', 'Public Transit', 'Airline Tickets', 'Car Repair'],
        'RENT_AND_UTILITIES': ['Rent Payment', 'Electric Bill', 'Water Bill', 'Internet Service', 'Phone Bill'],
        'PERSONAL_CARE': ['Haircut', 'Gym Membership', 'Pharmacy', 'Spa', 'Cosmetics'],
        'TRAVEL': ['Hotel Stay', 'Airbnb', 'Car Rental', 'Travel Agency', 'Cruise Line']
    }
    
    # Generate random transactions
    transactions = []
    
    # Number of days in the date range
    date_range = (end_date - start_date).days + 1
    num_transactions = min(date_range * 3, 50)  # Up to 3 transactions per day, max 50
    
    for _ in range(num_transactions):
        # Random date within range
        tx_date = start_date + timedelta(days=random.randint(0, date_range - 1))
        
        # Random category and merchant
        category = random.choice(list(merchants_by_category.keys()))
        merchant = random.choice(merchants_by_category[category])
        
        # Random amount (weighted by category)
        if category in ['RENT_AND_UTILITIES', 'TRAVEL']:
            amount = round(random.uniform(100, 1000), 2)
        elif category in ['GENERAL_MERCHANDISE', 'TRANSPORTATION']:
            amount = round(random.uniform(20, 200), 2)
        else:
            amount = round(random.uniform(5, 50), 2)
        
        # Create transaction
        transaction = {
            'transaction_id': str(uuid.uuid4()),
            'date': tx_date,
            'merchant': merchant,
            'name': merchant,
            'amount': amount,
            'category': category,
            'bank': bank_name
        }
        
        transactions.append(transaction)
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Sort by date (newest first)
    df = df.sort_values('date', ascending=False)
    
    return df

def fetch_transactions(access_token, start_date=None, end_date=None):
    """Fetch transactions from Plaid"""
    global USING_REAL_PLAID
    
    # Set default date range to last 30 days if not specified
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.now().date()
    
    # Check if we're using demo mode or if this is a demo token
    if not PLAID_IMPORTED or not USING_REAL_PLAID or access_token.startswith("demo-access-token"):
        # Find bank name from session state
        bank_name = "Demo Bank"
        if 'demo_banks' in st.session_state:
            for bank in st.session_state.demo_banks:
                if bank.get('access_token') == access_token:
                    bank_name = bank.get('institution_name', "Demo Bank")
                    break
                    
        # Generate demo transactions
        st.info(f"⚠️ Using demo data for {bank_name}. For real banking data, please add valid Plaid API credentials.")
        return generate_demo_transactions(bank_name, start_date, end_date)
    
    try:
        client = get_plaid_client()
        if client is None:
            # Fallback to demo mode
            return generate_demo_transactions("Demo Bank", start_date, end_date)
            
        api = plaid.PlaidApi(client)
        
        # Convert to ISO format string
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        
        # Create request
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date_str,
            end_date=end_date_str,
            options=TransactionsGetRequestOptions(
                include_personal_finance_category=True
            )
        )
        
        # Make request
        response = api.transactions_get(request)
        transactions = response['transactions']
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Process transactions
        if not df.empty:
            # Format data
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = df['amount'].apply(lambda x: float(x))
            
            # Get merchant name or description
            df['merchant'] = df.apply(
                lambda row: row.get('merchant_name', row.get('name', 'Unknown')), 
                axis=1
            )
            
            # Set transaction category
            df['category'] = df.apply(
                lambda row: row['personal_finance_category']['primary'] 
                if 'personal_finance_category' in row and row['personal_finance_category'] 
                else (row.get('category', ['Uncategorized'])[0] if row.get('category') else 'Uncategorized'), 
                axis=1
            )
            
            # Only include expenses (positive amounts in Plaid represent expenses)
            df = df[df['amount'] > 0]
            
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch transactions: {str(e)}")
        # Fallback to demo mode on error
        return generate_demo_transactions("Demo Bank", start_date, end_date)

def save_plaid_transaction_to_expenses(transaction, emotion, justification, necessity):
    """Save a Plaid transaction to the app's expense tracking system"""
    if 'expenses' not in st.session_state:
        st.session_state.expenses = []
    
    # Map Plaid categories to app categories
    category_mapping = {
        'FOOD_AND_DRINK': 'Food & Dining',
        'GENERAL_MERCHANDISE': 'Shopping',
        'ENTERTAINMENT': 'Entertainment',
        'TRANSPORTATION': 'Transportation',
        'RENT_AND_UTILITIES': 'Utilities',
        'HOME_IMPROVEMENT': 'Housing',
        'MEDICAL': 'Healthcare',
        'PERSONAL_CARE': 'Personal Care',
        'EDUCATION': 'Education',
        'TRAVEL': 'Travel',
        'GENERAL_SERVICES': 'Other',
        'CHARITABLE_GIVING': 'Gifts & Donations'
    }
    
    # Create expense object
    expense = {
        'date': transaction['date'].strftime('%Y-%m-%d'),
        'amount': float(transaction['amount']),
        'category': category_mapping.get(transaction['category'], 'Other'),
        'merchant': transaction.get('merchant', 'Unknown'),
        'emotion': emotion,
        'justification': justification,
        'necessity': necessity,
        'transaction_id': transaction.get('transaction_id', ''),
        'source': 'plaid'
    }
    
    # Add to expenses list
    st.session_state.expenses.append(expense)
    
    # Sort expenses by date (newest first)
    st.session_state.expenses = sorted(
        st.session_state.expenses, 
        key=lambda x: x['date'], 
        reverse=True
    )
    
    return expense

def check_transaction_abnormalities(transactions_df):
    """
    Check for abnormalities in transactions:
    - Unusually large transactions
    - Transactions at odd times
    - Spending in unusual categories
    - Multiple transactions at the same merchant
    """
    if transactions_df.empty:
        return pd.DataFrame()
    
    abnormalities = []
    
    # Calculate average and standard deviation of amounts
    avg_amount = transactions_df['amount'].mean()
    std_amount = transactions_df['amount'].std()
    
    if std_amount > 0:  # Avoid division by zero
        # Flag unusually large transactions (> 2 standard deviations from mean)
        large_transactions = transactions_df[
            transactions_df['amount'] > (avg_amount + 2 * std_amount)
        ]
        
        for _, transaction in large_transactions.iterrows():
            abnormalities.append({
                'transaction_id': transaction.get('transaction_id', ''),
                'date': transaction['date'],
                'merchant': transaction.get('merchant', 'Unknown'),
                'amount': transaction['amount'],
                'category': transaction.get('category', 'Uncategorized'),
                'abnormality_type': 'Unusually large amount',
                'description': f"This amount (${transaction['amount']:.2f}) is significantly higher than your usual spending"
            })
    
    # Flag multiple transactions at the same merchant on the same day
    merchant_counts = transactions_df.groupby(['date', 'merchant']).size().reset_index(name='count')
    multiple_transactions = merchant_counts[merchant_counts['count'] > 1]
    
    for _, group in multiple_transactions.iterrows():
        same_merchant_txns = transactions_df[
            (transactions_df['date'] == group['date']) & 
            (transactions_df['merchant'] == group['merchant'])
        ]
        
        if len(same_merchant_txns) > 1:
            total_spent = same_merchant_txns['amount'].sum()
            abnormalities.append({
                'transaction_id': same_merchant_txns.iloc[0].get('transaction_id', ''),
                'date': group['date'],
                'merchant': group['merchant'],
                'amount': total_spent,
                'category': same_merchant_txns.iloc[0].get('category', 'Uncategorized'),
                'abnormality_type': 'Multiple purchases',
                'description': f"You made {group['count']} purchases at {group['merchant']} on {group['date'].strftime('%Y-%m-%d')}"
            })
    
    # Return abnormalities as DataFrame
    return pd.DataFrame(abnormalities) if abnormalities else pd.DataFrame()