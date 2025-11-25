import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# Database Setup
DB_FILE = 'blister.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            billing_date TEXT NOT NULL,
            next_schedule_date TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Helper Functions
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

def cycle_patient(patient_id, current_next_schedule):
    new_billing_date = current_next_schedule
    new_next_schedule = calculate_next_schedule(new_billing_date)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE patients SET billing_date = ?, next_schedule_date = ? WHERE id = ?',
              (new_billing_date, new_next_schedule, patient_id))
    conn.commit()
    conn.close()

# App Layout
st.set_page_config(page_title="Blister Pack Scheduler", page_icon="💊")

init_db()

st.title("💊 Blister Pack Scheduler")
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

elif option != "Select a patient...":
    # Logic for selecting existing patient could go here if we wanted to edit them
    # For now, we just use the list to filter or just show the main dashboard
    pass

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
                    cycle_patient(row['id'], row['next_schedule_date'])
                    st.success(f"Cycled {row['name']}!")
                    st.rerun()
    else:
        st.info("No immediate actions required.")
else:
    st.info("No patients found.")

# Dashboard Section
st.subheader("Patient Dashboard")

if not patients_df.empty:
    # Display as a nice table or cards
    # Using dataframe for simplicity, but could be custom HTML
    display_df = patients_df[['name', 'billing_date', 'next_schedule_date']].copy()
    display_df.columns = ['Patient Name', 'Billing Date', 'Next Schedule']
    st.dataframe(display_df, use_container_width=True)
else:
    st.write("No patients yet. Add one from the sidebar!")
