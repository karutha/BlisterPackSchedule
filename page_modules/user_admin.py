"""
User Administration page - User management and app assignments
"""

import streamlit as st
from modules.user_management import (
    get_all_users, create_user, update_user, delete_user,
    get_all_apps, assign_app_to_user, remove_app_from_user, get_user_assigned_apps
)

def show_user_admin_page():
    """Display the user administration page"""
    
    tab1, tab2 = st.tabs(["Users", "App Assignments"])
    
    with tab1:
        st.subheader("Manage Users")
        
        # Add new user
        with st.expander("➕ Add New User"):
            with st.form("add_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_full_name = st.text_input("Full Name")
                new_role = st.selectbox("Role", ["user", "admin"])
                
                if st.form_submit_button("Create User"):
                    if new_username and new_password and new_full_name:
                        success, user_id = create_user(new_username, new_password, new_full_name, new_role)
                        if success:
                            st.success(f"User '{new_username}' created successfully!")
                            st.rerun()
                        else:
                            st.error("Username already exists!")
                    else:
                        st.error("Please fill in all fields")
        
        # List users
        st.subheader("Existing Users")
        users_df = get_all_users()
        
        if not users_df.empty:
            for index, user in users_df.iterrows():
                with st.expander(f"👤 {user['full_name']} (@{user['username']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Role:** {user['role']}")
                        st.write(f"**Status:** {'Active' if user['is_active'] else 'Inactive'}")
                    
                    with col2:
                        edit_full_name = st.text_input("Full Name", value=user['full_name'], key=f"fn_{user['id']}")
                        edit_role = st.selectbox("Role", ["user", "admin"], 
                                                index=0 if user['role'] == 'user' else 1, 
                                                key=f"role_{user['id']}")
                        edit_active = st.checkbox("Active", value=bool(user['is_active']), key=f"active_{user['id']}")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Update", key=f"update_{user['id']}"):
                                update_user(user['id'], edit_full_name, edit_role, 1 if edit_active else 0)
                                st.success("User updated!")
                                st.rerun()
                        
                        with col_b:
                            if user['username'] != 'admin':  # Prevent deleting admin
                                if st.button("Delete", key=f"delete_{user['id']}", type="secondary"):
                                    delete_user(user['id'])
                                    st.success("User deleted!")
                                    st.rerun()
        else:
            st.info("No users found")
    
    with tab2:
        st.subheader("App Assignments")
        
        users_df = get_all_users()
        apps_df = get_all_apps()
        
        if not users_df.empty and not apps_df.empty:
            selected_user = st.selectbox("Select User", 
                                        users_df['username'].tolist(),
                                        format_func=lambda x: f"{users_df[users_df['username']==x]['full_name'].values[0]} (@{x})")
            
            user_id = int(users_df[users_df['username'] == selected_user]['id'].values[0])
            assigned_apps = get_user_assigned_apps(user_id)
            
            # Debug: Show the user_id being used
            st.write(f"🔍 **Debug:** Assigning to user_id = {user_id}")
            
            # Show currently assigned apps
            if assigned_apps:
                assigned_app_names = apps_df[apps_df['id'].isin(assigned_apps)]['app_name'].tolist()
                st.success(f"✅ Currently assigned: {', '.join(assigned_app_names)}")
            else:
                st.info(f"ℹ️ No apps currently assigned to this user")
            
            st.write("**Available Apps:**")
            
            for index, app in apps_df.iterrows():
                is_assigned = app['id'] in assigned_apps
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    status_icon = "✅" if is_assigned else "⬜"
                    st.write(f"{status_icon} **{app['app_name']}** - {app['description']}")
                
                with col2:
                    if is_assigned:
                        if st.button("Remove", key=f"remove_app_{app['id']}"):
                            remove_app_from_user(user_id, app['id'])
                            st.success(f"Removed {app['app_name']}")
                            st.rerun()
                    else:
                        if st.button("Assign", key=f"assign_app_{app['id']}"):
                            success = assign_app_to_user(user_id, app['id'])
                            if success:
                                st.success(f"✅ Successfully assigned {app['app_name']}")
                            else:
                                st.error(f"❌ Failed to assign {app['app_name']}")
                            st.rerun()
        else:
            st.info("No users or apps available")
