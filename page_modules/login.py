"""
Login page for Blister Pack Scheduler
"""

import streamlit as st
from modules.auth import authenticate_user

def show_login_page():
    """Display the login page"""
    # Center the title and description
    st.markdown("<h1 style='text-align: center; color: #10B981;'>💊 Pharmalife Pharmacy</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #F9FAFB;'>🔐 Login</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9CA3AF;'>Please login to access the Blister Pack Scheduler</p>", unsafe_allow_html=True)
    st.write("")  # Add some spacing
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.full_name = user[2]
                    st.session_state.role = user[3]
                    st.success(f"Welcome, {user[2]}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.info("**Default credentials:** Username: `admin` | Password: `admin123`")
