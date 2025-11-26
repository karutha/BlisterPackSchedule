"""
Patient Management page - Full CRUD operations for patients with modern design
"""

import streamlit as st
import pandas as pd
from modules.patient_management import get_patients, add_patient, update_patient, delete_patient

def show_patient_management_page():
    """Display the patient management page with modern Airtable-inspired styling"""
    
    # Fetch patients
    patients_df = get_patients()
    # Statistics with modern design
    st.markdown("## Patient Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total Patients", len(patients_df) if not patients_df.empty else 0)
    with col2:
        active_count = len(patients_df[patients_df['next_schedule_date'].notna()]) if not patients_df.empty else 0
        st.metric("📅 Active Schedules", active_count)
    with col3:
        avg_cost = patients_df['cost'].mean() if not patients_df.empty and 'cost' in patients_df.columns else 0
        st.metric("💰 Avg Cost", f"${avg_cost:.2f}")
    
    # Tabs
    tab1, tab2 = st.tabs(["📋 All Patients", "➕ Add New Patient"])
    
    with tab1:
        st.markdown("### Manage Patients")
        
        if not patients_df.empty:
            # Search functionality
            search = st.text_input("🔍 Search patients", placeholder="Type patient name...", label_visibility="collapsed")
            
            if search:
                filtered_df = patients_df[patients_df['name'].str.contains(search, case=False, na=False)]
            else:
                filtered_df = patients_df
            
            st.caption(f"Showing {len(filtered_df)} of {len(patients_df)} patients")
            # Display patients in modern expanders
            for index, patient in filtered_df.iterrows():
                with st.expander(f"👤 **{patient['name']}** - Next: {patient['next_schedule_date']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📦 Delivery**")
                        st.write(patient.get('delivery', 'N/A'))
                        st.markdown("**🏥 Insurance**")
                        st.write(patient.get('insurance', 'N/A'))
                        st.markdown("**💰 Cost**")
                        st.write(f"${patient.get('cost', 0.0):.2f}" if patient.get('cost') else "N/A")
                    
                    with col2:
                        st.markdown("**📋 Blister Schedule**")
                        st.write(patient.get('blister_schedule', 'N/A'))
                        st.markdown("**📅 Billing Date**")
                        st.write(patient['billing_date'])
                        st.markdown("**🔄 Next Schedule**")
                        st.write(patient['next_schedule_date'])
                    
                    st.markdown("**Edit Patient**")
                    
                    with st.form(key=f"edit_form_{patient['id']}"):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            edit_name = st.text_input("Patient Name", value=patient['name'], key=f"name_{patient['id']}")
                            edit_delivery = st.selectbox("Delivery", 
                                                        ["", "Home Delivery", "Pickup", "Mail", "Other"],
                                                        index=["", "Home Delivery", "Pickup", "Mail", "Other"].index(patient.get('delivery', '')) if patient.get('delivery') in ["", "Home Delivery", "Pickup", "Mail", "Other"] else 0,
                                                        key=f"delivery_{patient['id']}")
                            edit_insurance = st.text_input("Insurance", value=patient.get('insurance', ''), key=f"insurance_{patient['id']}")
                        
                        with col_b:
                            edit_cost = st.number_input("Cost ($)", value=float(patient.get('cost', 0.0)) if patient.get('cost') else 0.0, 
                                                       min_value=0.0, step=0.01, key=f"cost_{patient['id']}")
                            edit_blister_schedule = st.selectbox("Blister Schedule",
                                                                ["", "Weekly", "Bi-weekly", "Monthly", "Custom"],
                                                                index=["", "Weekly", "Bi-weekly", "Monthly", "Custom"].index(patient.get('blister_schedule', '')) if patient.get('blister_schedule') in ["", "Weekly", "Bi-weekly", "Monthly", "Custom"] else 0,
                                                                key=f"schedule_{patient['id']}")
                            edit_billing_date = st.date_input("Billing Date", 
                                                              value=pd.to_datetime(patient['billing_date']).date() if patient['billing_date'] else None,
                                                              key=f"billing_{patient['id']}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Update Patient", type="primary", use_container_width=True):
                                update_patient(
                                    patient['id'],
                                    edit_name,
                                    edit_delivery if edit_delivery else None,
                                    edit_insurance if edit_insurance else None,
                                    edit_cost if edit_cost > 0 else None,
                                    edit_blister_schedule if edit_blister_schedule else None,
                                    edit_billing_date.strftime('%Y-%m-%d')
                                )
                                st.success(f"✅ Updated {edit_name}!")
                                st.rerun()
                        
                        with col_btn2:
                            if st.form_submit_button("🗑️ Delete Patient", type="secondary", use_container_width=True):
                                delete_patient(patient['id'])
                                st.success(f"✅ Deleted {patient['name']}!")
                                st.rerun()
        else:
            st.info("📝 No patients found. Add your first patient using the 'Add New Patient' tab!")
    
    with tab2:
        st.markdown("### Add New Patient")
        
        with st.form("add_patient_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Basic Information**")
                new_name = st.text_input("Patient Name *", placeholder="e.g., John Doe")
                new_delivery = st.selectbox("Delivery Method", ["", "Home Delivery", "Pickup", "Mail", "Other"])
                new_insurance = st.text_input("Insurance Provider", placeholder="e.g., Blue Cross, Medicare")
            
            with col2:
                st.markdown("**Schedule & Billing**")
                new_cost = st.number_input("Medication Cost ($)", min_value=0.0, step=0.01, value=0.0)
                new_blister_schedule = st.selectbox("Blister Schedule", ["", "Weekly", "Bi-weekly", "Monthly", "Custom"])
                new_billing_date = st.date_input("Billing Date *")
            
            st.divider()
            
            col_submit1, col_submit2 = st.columns(2)
            
            with col_submit1:
                if st.form_submit_button("➕ Add Patient", type="primary", use_container_width=True):
                    if new_name and new_billing_date:
                        add_patient(
                            new_name,
                            new_billing_date.strftime('%Y-%m-%d'),
                            new_delivery if new_delivery else None,
                            new_insurance if new_insurance else None,
                            new_cost if new_cost > 0 else None,
                            new_blister_schedule if new_blister_schedule else None
                        )
                        st.success(f"✅ Successfully added {new_name}!")
                        st.rerun()
                    else:
                        st.error("❌ Please enter at least Patient Name and Billing Date")
            
            with col_submit2:
                st.form_submit_button("🔄 Clear Form", type="secondary", use_container_width=True)
    

