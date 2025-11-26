"""
Blister Pack Scheduler - Main Application
Clean, professional design inspired by FinPlanner template
"""

import streamlit as st

# Import modules
from modules.database import init_db, init_default_data
from modules.ui_components import show_debug_info, check_app_access

# Import pages
from page_modules.login import show_login_page
from page_modules.blister_scheduler import show_blister_scheduler_page
from page_modules.user_admin import show_user_admin_page
from page_modules.patient_management import show_patient_management_page

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'full_name' not in st.session_state:
    st.session_state.full_name = None
if 'role' not in st.session_state:
    st.session_state.role = None

# App Configuration
st.set_page_config(
    page_title="Pharmalife Pharmacy", 
    page_icon="💊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Dark Theme
st.markdown("""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background-color: #111827;
        color: #F9FAFB;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1F2937;
        border-right: 1px solid #374151;
    }
    
    /* Sidebar toggle button - ensure it's above banner */
    button[kind="header"] {
        z-index: 9999999 !important;
    }
    
    [data-testid="collapsedControl"] {
        z-index: 9999999 !important;
        top: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #F3F4F6;
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* Navigation menu items */
    /* Navigation menu items */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
        gap: 0.5rem;
    }

    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
        background: transparent;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        color: #D1D5DB;
        font-size: 0.95rem;
        font-weight: 500;
        border: 1px solid transparent;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-right: 0;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        text-align: left;
    }
    
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
        background: #374151;
        color: #FFFFFF;
    }

    /* Hide the radio circle */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-of-type {
        display: none;
    }
    
    /* Selected item style */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
        background: #1F2937;
        color: #10B981;
        border: 1px solid #374151;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        font-weight: 600;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #F9FAFB;
        font-weight: 700;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        border: none;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #10B981;
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #059669;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #374151;
        color: #F3F4F6;
        border: 1px solid #4B5563;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #4B5563;
        border-color: #6B7280;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: #1F2937;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F9FAFB;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9CA3AF;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Cards/Expanders */
    .streamlit-expanderHeader {
        background: #1F2937;
        border: 1px solid #374151;
        border-radius: 6px;
        color: #F9FAFB;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: #374151;
        border-color: #4B5563;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #9CA3AF;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .stTabs [aria-selected="true"] {
        color: #F9FAFB;
        border-bottom-color: #10B981;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        background-color: #1F2937;
        border: 1px solid #4B5563;
        border-radius: 6px;
        color: #F9FAFB;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #10B981;
        box-shadow: 0 0 0 1px #10B981;
    }
    
    /* DataFrames */
    .stDataFrame {
        border: 1px solid #374151;
        border-radius: 6px;
    }
    
    /* Alert Boxes */
    .stAlert {
        background-color: #1F2937;
        color: #F9FAFB;
        border: 1px solid #374151;
    }
    
    /* Hide Welcome heading */
    .stHeadingWithActionElements {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
init_db()
init_default_data()

# Main Application Logic
if not st.session_state.logged_in:
    show_login_page()
else:
    # Add branding and user info to header
    st.markdown(f"""
        <style>
        /* Style the Streamlit header */
        header[data-testid="stHeader"] {{
            background-color: #1F2937;
            border-bottom: 1px solid #374151;
        }}
        
        /* Add custom content to header */
        header[data-testid="stHeader"]::before {{
            content: "PHARMALIFE";
            color: #10B981;
            font-weight: 700;
            font-size: 1.1rem;
            margin-right: auto;
            padding-left: 1rem;
        }}
        
        header[data-testid="stHeader"]::after {{
            content: "{st.session_state.full_name} ({st.session_state.role})";
            color: #D1D5DB;
            font-size: 0.9rem;
            padding-right: 1rem;
        }}
        </style>
    """, unsafe_allow_html=True)
    # Sidebar
    with st.sidebar:
        
        # Show debug info
        show_debug_info(
            st.session_state.user_id,
            st.session_state.username,
            st.session_state.role
        )
        
        # Check app access
        has_blister_access = check_app_access(
            st.session_state.user_id,
            st.session_state.role,
            'blister_scheduler'
        )
        
        # Navigation menu
        if st.session_state.role == 'admin':
            page = st.radio("", ["Blister Scheduler", "Patient Management", "User Management", "Logout"], label_visibility="collapsed")
        else:
            page = st.radio("", ["Blister Scheduler", "Patient Management", "Logout"], label_visibility="collapsed")
    
    # Handle navigation
    if page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.full_name = None
        st.session_state.role = None
        st.rerun()
    
    elif page == "Patient Management":
        show_patient_management_page()
    
    elif page == "User Management" and st.session_state.role == 'admin':
        show_user_admin_page()
    
    elif page == "Blister Scheduler":
        if not has_blister_access:
            st.error("You don't have access to the Blister Pack Scheduler.")
        else:
            show_blister_scheduler_page()
