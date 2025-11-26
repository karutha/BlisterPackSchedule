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
            color: #FFFFFF;
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
            page = st.radio("Navigation Menu", ["Blister Scheduler", "Patient Management", "User Management", "Logout"], label_visibility="collapsed")
        else:
            page = st.radio("Navigation Menu", ["Blister Scheduler", "Patient Management", "Logout"], label_visibility="collapsed")
    
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