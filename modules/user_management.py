"""
User Management module for Blister Pack Scheduler
Handles user CRUD operations and app assignments
"""

import sqlite3
import pandas as pd
from modules.database import get_connection
from modules.auth import hash_password

# User CRUD Operations
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

# App Management
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
