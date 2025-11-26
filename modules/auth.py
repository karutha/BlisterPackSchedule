"""
Authentication module for Blister Pack Scheduler
Handles password hashing and user authentication
"""

import hashlib
import pandas as pd
from modules.database import get_connection

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """
    Authenticate a user
    Returns tuple: (id, username, full_name, role, is_active) or None
    """
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
