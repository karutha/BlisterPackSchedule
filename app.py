import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import os

# Database Setup
DB_FILE = 'blister.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Patients table
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            billing_date TEXT NOT NULL,
            next_schedule_date TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Schedule records table
    c.execute('''
        CREATE TABLE IF NOT EXISTS schedule_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            previous_billing_date TEXT NOT NULL,
            new_billing_date TEXT NOT NULL,
            new_next_schedule_date TEXT NOT NULL,
            cycled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    ''')
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Apps table
    c.execute('''
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            app_key TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User-Apps junction table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            app_id INTEGER NOT NULL,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (app_id) REFERENCES apps(id),
            UNIQUE(user_id, app_id)
        )
    ''')
    
    # Create default admin user if no users exist
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        admin_password = hash_password('admin123')
        c.execute('''
            INSERT INTO users (username, password_hash, full_name, role, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', admin_password, 'Administrator', 'admin', 1))
    
    # Create default app if no apps exist
    c.execute('SELECT COUNT(*) FROM apps')
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO apps (app_name, app_key, description)
            VALUES (?, ?, ?)
        ''', ('Blister Pack Scheduler', 'blister_scheduler', 'Manage patient medication cycles'))
    
    conn.commit()
    conn.close()

# Authentication Functions
def authenticate_user(username, password):
    """Authenticate a user"""
    conn = get_connection()
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute('''
        SELECT id, username, full_name, role, is_active 
        FROM users 
        WHERE username = ? AND password_hash = ? AND is_active = 1
    ''', (username, password_hash))
    user = c.fetchone()
    conn.close()
    return user

def get_user_apps(user_id):
    """Get apps assigned to a user"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT a.* FROM apps a
        JOIN user_apps ua ON a.id = ua.app_id
        WHERE ua.user_id = ?
    ''', conn, params=(user_id,))
    conn.close()
    return df

# User Management Functions
def get_all_users():
    """Get all users"""
    conn = get_connection()
    df = pd.read_sql_query('SELECT id, username, full_name, role, is_active FROM users ORDER BY created_at DESC', conn)
    conn.close()
    return df

def create_user(username, password, full_name, role):
    """Create a new user"""
    conn = get_connection()
    c = conn.cursor()
    password_hash = hash_password(password)
    try:
        c.execute('''
            INSERT INTO users (username, password_hash, full_name, role, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (username, password_hash, full_name, role))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, None

def update_user(user_id, full_name, role, is_active):
    """Update user details"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE users SET full_name = ?, role = ?, is_active = ?
        WHERE id = ?
    ''', (full_name, role, is_active, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Delete a user"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM user_apps WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_all_apps():
    """Get all apps"""
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM apps ORDER BY app_name', conn)
    conn.close()
    return df

def assign_app_to_user(user_id, app_id):
    """Assign an app to a user"""
    print(f"DEBUG assign_app_to_user called with user_id={user_id}, app_id={app_id}")
    print(f"DEBUG user_id type: {type(user_id)}, app_id type: {type(app_id)}")
    
    conn = get_connection()
    c = conn.cursor()
    try:
        # Check if assignment already exists
        c.execute('SELECT COUNT(*) FROM user_apps WHERE user_id = ? AND app_id = ?', (user_id, app_id))
        if c.fetchone()[0] > 0:
            conn.close()
            print(f"DEBUG Assignment already exists")
            return True  # Already assigned
        
        # Insert new assignment
        print(f"DEBUG Inserting user_id={user_id}, app_id={app_id}")
        c.execute('INSERT INTO user_apps (user_id, app_id) VALUES (?, ?)', (user_id, app_id))
        conn.commit()
        
        # Verify the insert worked
        c.execute('SELECT * FROM user_apps WHERE user_id = ? AND app_id = ?', (user_id, app_id))
        result = c.fetchone()
        print(f"DEBUG After insert, query result: {result}")
        
        success = result is not None
        
        conn.close()
        return success
    except Exception as e:
        print(f"Error assigning app: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return False

def remove_app_from_user(user_id, app_id):
    """Remove an app from a user"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM user_apps WHERE user_id = ? AND app_id = ?', (user_id, app_id))
    conn.commit()
    conn.close()

def get_user_assigned_apps(user_id):
    """Get app IDs assigned to a user"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT app_id FROM user_apps WHERE user_id = ?', (user_id,))
    app_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return app_ids

# Patient Management Functions
def calculate_next_schedule(billing_date_str):
    billing_date = datetime.strptime(billing_date_str, '%Y-%m-%d')
    next_schedule = billing_date + timedelta(days=28)
    return next_schedule.strftime('%Y-%m-%d')

def add_patient(name, billing_date):
    next_schedule = calculate_next_schedule(billing_date)
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO patients (name, billing_date, next_schedule_date) VALUES (?, ?, ?)',
              (name, billing_date, next_schedule))
    conn.commit()
    conn.close()

def get_patients():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients ORDER BY next_schedule_date ASC", conn)
    conn.close()
    return df

def cycle_patient(patient_id, patient_name, current_billing_date, current_next_schedule):
    new_billing_date = current_next_schedule
    new_next_schedule = calculate_next_schedule(new_billing_date)
    
    conn = get_connection()
    c = conn.cursor()
    
    # Save the cycle record to history
    c.execute('''
        INSERT INTO schedule_records 
        (patient_id, patient_name, previous_billing_date, new_billing_date, new_next_schedule_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (patient_id, patient_name, current_billing_date, new_billing_date, new_next_schedule))
    
    # Update the patient record
    c.execute('UPDATE patients SET billing_date = ?, next_schedule_date = ? WHERE id = ?',
              (new_billing_date, new_next_schedule, patient_id))
    
    conn.commit()
    conn.close()

def get_schedule_history():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM schedule_records ORDER BY cycled_at DESC", conn)
    conn.close()
    return df

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

# App Layout
st.set_page_config(page_title="Blister Pack Scheduler", page_icon="💊", layout="wide")

# Initialize database
init_db()

# Login Screen
if not st.session_state.logged_in:
    # Center the title and description
    st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please login to access the Blister Pack Scheduler</p>", unsafe_allow_html=True)
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

else:
    # Main App (after login)
    st.title("💊 Blister Pack Scheduler")
    st.write(f"Welcome, **{st.session_state.full_name}** ({st.session_state.role})")
    
    # Sidebar
    st.sidebar.header("Navigation")
    
    # Check if user has access to Blister Scheduler app
    user_apps = get_user_apps(st.session_state.user_id)
    
    # Debug information (can be removed later)
    with st.sidebar.expander("🔍 Debug Info"):
        st.write(f"**User ID:** {st.session_state.user_id}")
        st.write(f"**Username:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.role}")
        st.write(f"**Apps DataFrame Empty:** {user_apps.empty}")
        if not user_apps.empty:
            st.write(f"**Assigned Apps:** {user_apps['app_key'].tolist()}")
        else:
            st.write("**Assigned Apps:** None")
        
        # Direct database query to verify
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM user_apps WHERE user_id = ?', (st.session_state.user_id,))
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
    
    has_blister_access = st.session_state.role == 'admin' or (
        not user_apps.empty and 'blister_scheduler' in user_apps['app_key'].values
    )
    
    if st.session_state.role == 'admin':
        page = st.sidebar.radio("Go to", ["Blister Scheduler", "User Management", "Logout"])
    else:
        page = st.sidebar.radio("Go to", ["Blister Scheduler", "Logout"])
    
    if page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.full_name = None
        st.session_state.role = None
        st.rerun()
    
    elif page == "User Management" and st.session_state.role == 'admin':
        st.header("👥 User Management")
        
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
                    st.info("ℹ️ No apps currently assigned to this user")
                
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
    
    elif page == "Blister Scheduler":
        if not has_blister_access:
            st.error("You don't have access to the Blister Pack Scheduler. Please contact an administrator.")
        else:
            # Original Blister Scheduler functionality
            st.header("Blister Pack Scheduler")
            st.write("Manage patient cycles with precision.")
            
            # Sidebar for Actions
            st.sidebar.header("Actions")
            
            # Fetch patients for dropdown
            patients_df = get_patients()
            existing_names = sorted(patients_df['name'].unique().tolist()) if not patients_df.empty else []
            
            # Patient Selection / Addition
            option = st.sidebar.selectbox(
                "Select Patient",
                ["Select a patient...", "+ Add New Patient"] + existing_names
            )
            
            if option == "+ Add New Patient":
                st.sidebar.subheader("Add New Patient")
                new_name = st.sidebar.text_input("Patient Name")
                billing_date = st.sidebar.date_input("Billing Date")
                
                if st.sidebar.button("Schedule Cycle"):
                    if new_name:
                        add_patient(new_name, billing_date.strftime('%Y-%m-%d'))
                        st.sidebar.success(f"Added {new_name}!")
                        st.rerun()
                    else:
                        st.sidebar.error("Please enter a name.")
            
            # Main Content
            
            # Alerts Section
            st.subheader("⚠️ Actions Required")
            today = datetime.now().strftime('%Y-%m-%d')
            
            if not patients_df.empty:
                due_patients = patients_df[patients_df['billing_date'] <= today]
                
                if not due_patients.empty:
                    for index, row in due_patients.iterrows():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.warning(f"**{row['name']}** is due for billing today ({row['billing_date']})")
                        with col2:
                            if st.button("Start Next Cycle", key=f"cycle_{row['id']}"):
                                cycle_patient(row['id'], row['name'], row['billing_date'], row['next_schedule_date'])
                                st.success(f"Cycled {row['name']}!")
                                st.rerun()
                else:
                    st.info("No immediate actions required.")
            else:
                st.info("No patients found.")
            
            # Dashboard Section
            st.subheader("Patient Dashboard")
            
            if not patients_df.empty:
                display_df = patients_df[['name', 'billing_date', 'next_schedule_date']].copy()
                display_df.columns = ['Patient Name', 'Billing Date', 'Next Schedule']
                st.dataframe(display_df, width='stretch')
            else:
                st.write("No patients yet. Add one from the sidebar!")
            
            # Schedule History Section
            st.subheader("📋 Schedule History")
            
            history_df = get_schedule_history()
            
            if not history_df.empty:
                display_history = history_df[[
                    'patient_name', 
                    'previous_billing_date', 
                    'new_billing_date', 
                    'new_next_schedule_date', 
                    'cycled_at'
                ]].copy()
                display_history.columns = [
                    'Patient Name', 
                    'Previous Billing', 
                    'New Billing', 
                    'Next Schedule', 
                    'Cycled At'
                ]
                st.dataframe(display_history, width='stretch')
            else:
                st.info("No schedule history yet. Cycle a patient to see records here.")
