"""
Patient Management module for Blister Pack Scheduler
Handles patient CRUD operations, scheduling, and cycle management
"""

import pandas as pd
from datetime import datetime, timedelta
from modules.database import get_connection

# Helper Functions
def calculate_next_schedule(billing_date_str, schedule_type="Monthly"):
    """Calculate next schedule date based on schedule type"""
    billing_date = datetime.strptime(billing_date_str, '%Y-%m-%d')
    
    if schedule_type == "Weekly":
        days = 7
    elif schedule_type == "Bi-weekly":
        days = 14
    elif schedule_type == "Monthly":
        days = 28
    else:
        days = 28  # Default to 28 days
        
    next_schedule = billing_date + timedelta(days=days)
    return next_schedule.strftime('%Y-%m-%d')

# Patient CRUD Operations
def add_patient(name, billing_date, delivery=None, insurance=None, cost=None, blister_schedule="Monthly"):
    """Add a new patient"""
    next_schedule = calculate_next_schedule(billing_date, blister_schedule)
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO patients 
                 (name, delivery, insurance, cost, blister_schedule, billing_date, next_schedule_date) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (name, delivery, insurance, cost, blister_schedule, billing_date, next_schedule))
    conn.commit()
    conn.close()

def update_patient(patient_id, name, delivery, insurance, cost, blister_schedule, billing_date):
    """Update an existing patient"""
    # Recalculate next schedule based on new billing date and schedule type
    next_schedule = calculate_next_schedule(billing_date, blister_schedule)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute('''UPDATE patients 
                 SET name = ?, delivery = ?, insurance = ?, cost = ?, blister_schedule = ?, 
                     billing_date = ?, next_schedule_date = ?
                 WHERE id = ?''',
              (name, delivery, insurance, cost, blister_schedule, billing_date, next_schedule, patient_id))
    conn.commit()
    conn.close()

def delete_patient(patient_id):
    """Delete a patient"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM schedule_records WHERE patient_id = ?', (patient_id,))
    c.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()

def get_patients():
    """Get all patients"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients ORDER BY next_schedule_date ASC", conn)
    conn.close()
    return df

# Schedule Management
def cycle_patient(patient_id, patient_name, current_billing_date, current_next_schedule, manual_billing_date=None):
    """Cycle a patient to the next billing period"""
    # Get patient's schedule type
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT blister_schedule FROM patients WHERE id = ?', (patient_id,))
    result = c.fetchone()
    schedule_type = result[0] if result else "Monthly"
    
    if manual_billing_date:
        new_billing_date = manual_billing_date
    else:
        new_billing_date = current_next_schedule
        
    new_next_schedule = calculate_next_schedule(new_billing_date, schedule_type)
    
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
    """Get all schedule history records"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM schedule_records ORDER BY cycled_at DESC", conn)
    conn.close()
    return df
