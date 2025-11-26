"""
UI Components module for Blister Pack Scheduler
Reusable UI components and helpers
"""

import streamlit as st
from modules.database import get_connection
from modules.auth import get_user_apps

def show_debug_info(user_id, username, role):
    """Display debug information in sidebar"""
    user_apps = get_user_apps(user_id)
    
    with st.sidebar.expander("🔍 Debug Info"):
        st.write(f"**User ID:** {user_id}")
        st.write(f"**Username:** {username}")
        st.write(f"**Role:** {role}")
        st.write(f"**Apps DataFrame Empty:** {user_apps.empty}")
        if not user_apps.empty:
            st.write(f"**Assigned Apps:** {user_apps['app_key'].tolist()}")
        else:
            st.write("**Assigned Apps:** None")
        
        # Direct database query to verify
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM user_apps WHERE user_id = ?', (user_id,))
        raw_assignments = c.fetchall()
        conn.close()
        st.write(f"**Raw DB user_apps records:** {raw_assignments}")
        
        # Check all apps in database
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, app_key FROM apps')
        all_apps = c.fetchall()
        conn.close()
        st.write(f"**All apps in DB:** {all_apps}")

def check_app_access(user_id, role, app_key='blister_scheduler'):
    """Check if user has access to a specific app"""
    user_apps = get_user_apps(user_id)
    has_access = role == 'admin' or (
        not user_apps.empty and app_key in user_apps['app_key'].values
    )
    return has_access
