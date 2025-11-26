"""
Database module for Blister Pack Scheduler
Handles database connection, initialization, and schema management
"""

import sqlite3
import os

# Database Setup
DB_FILE = 'blister.db'

def get_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_connection()
    c = conn.cursor()
    
    # Patients table
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            delivery TEXT,
            insurance TEXT,
            cost REAL,
            blister_schedule TEXT,
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
    
    conn.commit()
    conn.close()

def init_default_data():
    """Initialize default admin user and app"""
    conn = get_connection()
    c = conn.cursor()
    
    # Import hash_password from auth module
    from modules.auth import hash_password
    
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
