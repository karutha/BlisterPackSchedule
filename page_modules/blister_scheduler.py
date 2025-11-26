"""
Blister Scheduler page - Clean FinPlanner-inspired design
"""
import streamlit as st
from datetime import datetime
from modules.patient_management import get_patients, cycle_patient, get_schedule_history

def show_blister_scheduler_page():
    """Display the blister scheduler page"""
    
    # Fetch data
    patients_df = get_patients()
    today = datetime.now().strftime('%Y-%m-%d')
    history_df = get_schedule_history()
    
    # Statistics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_patients = len(patients_df) if not patients_df.empty else 0
        st.metric("Total Patients", total_patients)
    
    with col2:
        due_count = len(patients_df[patients_df['billing_date'] <= today]) if not patients_df.empty else 0
        st.metric("Due Today", due_count)
    
    with col3:
        upcoming_count = len(patients_df[patients_df['next_schedule_date'] > today]) if not patients_df.empty else 0
        st.metric("Upcoming", upcoming_count)
    
    with col4:
        history_count = len(history_df) if not history_df.empty else 0
        st.metric("Total Cycles", history_count)
    
    st.markdown("")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Actions Required", "📅 Schedule Calendar", "🔄 Manual Cycle", "📊 Recent History"])
    
    with tab1:
        st.markdown("### Actions Required")
        
        if not patients_df.empty:
            due_patients = patients_df[patients_df['billing_date'] <= today]
            
            if not due_patients.empty:
                for index, row in due_patients.iterrows():
                    with st.container():
                        st.markdown(f"""<div style="background: #1F2937; padding: 1rem; border-radius: 6px; border: 1px solid #374151; margin-bottom: 0.5rem;">
                                <div style="color: #F9FAFB; font-weight: 600; margin-bottom: 0.3rem;">{row['name']}</div>
                                <div style="color: #9CA3AF; font-size: 0.85rem;">Billing: {row['billing_date']} | Next: {row['next_schedule_date']}</div>
                            </div>""", unsafe_allow_html=True)
                        if st.button("Start Cycle", key=f"cycle_{row['id']}", type="primary"):
                            cycle_patient(row['id'], row['name'], row['billing_date'], row['next_schedule_date'])
                            st.success(f"✅ Cycled {row['name']}!")
                            st.rerun()
            else:
                st.success("✅ All clear! No actions required.")
        else:
            st.info("No patients found.")
        
        st.markdown("")
        st.markdown("### Active Patients")
        
        if not patients_df.empty:
            st.dataframe(
                patients_df[['name', 'billing_date', 'next_schedule_date']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No patients yet.")
    
    with tab2:
        st.markdown("### 📅 Schedule Calendar")
        
        # Calendar controls
        if 'cal_year' not in st.session_state:
            st.session_state.cal_year = datetime.now().year
        if 'cal_month' not in st.session_state:
            st.session_state.cal_month = datetime.now().month
            
        col_cal1, col_cal2, col_cal3 = st.columns([1, 5, 1])
        with col_cal1:
            if st.button("◀ Prev", key="prev_month"):
                if st.session_state.cal_month == 1:
                    st.session_state.cal_month = 12
                    st.session_state.cal_year -= 1
                else:
                    st.session_state.cal_month -= 1
                st.rerun()
                
        with col_cal2:
            month_name = datetime(st.session_state.cal_year, st.session_state.cal_month, 1).strftime("%B %Y")
            st.markdown(f"<h3 style='text-align: center; margin: 0;'>{month_name}</h3>", unsafe_allow_html=True)
            
        with col_cal3:
            if st.button("Next ▶", key="next_month"):
                if st.session_state.cal_month == 12:
                    st.session_state.cal_month = 1
                    st.session_state.cal_year += 1
                else:
                    st.session_state.cal_month += 1
                st.rerun()
        
        st.markdown("")
        
        # Calendar Grid
        import calendar
        cal = calendar.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)
        
        # Days header
        cols = st.columns(7)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for idx, day in enumerate(days):
            cols[idx].markdown(f"<div style='text-align: center; font-weight: bold; color: #9CA3AF;'>{day}</div>", unsafe_allow_html=True)
        
        # Calendar days
        for week in cal:
            cols = st.columns(7)
            for idx, day in enumerate(week):
                with cols[idx]:
                    if day != 0:
                        # Check for patients due on this day
                        date_str = f"{st.session_state.cal_year}-{st.session_state.cal_month:02d}-{day:02d}"
                        due_on_day = patients_df[patients_df['next_schedule_date'] == date_str]
                        
                        # Style for today
                        is_today = date_str == datetime.now().strftime('%Y-%m-%d')
                        bg_color = "#374151" if is_today else "#1F2937"
                        border_color = "#10B981" if is_today else "#374151"
                        
                        # Create day cell
                        html_content = f"""<div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 6px; padding: 8px; min-height: 80px; margin-bottom: 8px;">
                        <div style="text-align: right; color: #9CA3AF; font-size: 0.8rem; margin-bottom: 4px;">{day}</div>"""
                        
                        if not due_on_day.empty:
                            for _, p in due_on_day.iterrows():
                                html_content += f"""<div style="background-color: #10B981; color: white; font-size: 0.7rem; padding: 2px 4px; border-radius: 4px; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{p['name']}">{p['name']}</div>"""
                        
                        html_content += "</div>"
                        st.markdown(html_content, unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='min-height: 80px;'></div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🔄 Manual Cycle Start")
        st.markdown("Select a patient to manually start a new cycle with a custom billing date.")
        
        if not patients_df.empty:
            col_man1, col_man2, col_man3 = st.columns([2, 2, 1])
            
            with col_man1:
                selected_patient_name = st.selectbox(
                    "Select Patient", 
                    options=patients_df['name'].tolist(),
                    key="manual_patient_select"
                )
            
            with col_man2:
                manual_date = st.date_input(
                    "New Billing Date",
                    value=datetime.now(),
                    key="manual_billing_date"
                )
                
            with col_man3:
                st.write("") # Spacing
                st.write("") # Spacing
                if st.button("Start Cycle", type="primary", key="manual_start_btn", use_container_width=True):
                    # Get patient details
                    patient_row = patients_df[patients_df['name'] == selected_patient_name].iloc[0]
                    cycle_patient(
                        patient_row['id'], 
                        patient_row['name'], 
                        patient_row['billing_date'], 
                        patient_row['next_schedule_date'],
                        manual_billing_date=manual_date.strftime('%Y-%m-%d')
                    )
                    st.success(f"✅ Manually cycled {selected_patient_name}!")
                    st.rerun()
        else:
            st.info("No patients available.")
    
    with tab4:
        st.markdown("### 📊 Recent Schedule History")
        
        if not history_df.empty:
            recent = history_df.head(10)
            st.dataframe(
                recent[['patient_name', 'previous_billing_date', 'new_billing_date', 'cycled_at']],
                use_container_width=True,
                hide_index=True
            )
            if len(history_df) > 10:
                st.caption(f"Showing 10 of {len(history_df)} total cycles")
        else:
            st.info("No history yet.")
