# add_entry.py
import streamlit as st
from datetime import date
from utils.app_utils import append_row_to_csv, MATERIAL_DICT


def add_entry_page():
    # Hide the "press enter to submit" tooltip

    st.title("Add New Deposition Entry")

    # Initialize session state
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0

    with st.form(f"add_entry_form_{st.session_state.reset_counter}"):
        today = date.today()
        entry_date = today.strftime("%m/%d/%Y")
        st.write(f"Date: {entry_date}")
        # Use normalized material names for dropdown
        materials = sorted(MATERIAL_DICT.keys())
        material = st.selectbox("Material*", materials)
        threshold_power = st.number_input(
            "Threshold Power (%)*",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            placeholder="This can be done after this entry...",
            help="Enter threshold power percentage",
        )
        deposition_power = st.number_input(
            "Deposition Power (%)*",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            placeholder="This can be done after this entry...",
            help="Enter deposition power percentage",
        )
        rate = st.number_input(
            "Rate (A/s)*",
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            placeholder="This can be done after this entry...",
            help="Enter deposition rate in Angstroms per second",
        )
        thickness = st.number_input(
            "Thickness (nm)*",
            min_value=0.0,
            max_value=10000.0,
            step=0.01,
            help="Enter thickness in nanometers",
        )
        measured = st.number_input(
            "Measured Thickness (nm)",
            min_value=0.0,
            max_value=10000.0,
            step=0.01,
            help="Enter measured thickness in nanometers",
        )
        crystal_monitor = st.number_input(
            "Crystal Monitor*",
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            placeholder="This can be done after this entry...",
            help="Enter crystal monitor reading",
        )
        notes = st.text_area(
            "Notes",
            height=100,
            placeholder="Enter detailed comments here...",
        )

        submitted = st.form_submit_button(
            "Add Entry", disabled=st.session_state.form_submitted
        )

        if submitted and not st.session_state.form_submitted:
            # Validation: Check for meaningful values
            validation_errors = []

            # Core required fields (must be > 0)
            if threshold_power <= 0:
                validation_errors.append("Threshold Power must be greater than 0")
            if deposition_power <= 0:
                validation_errors.append("Deposition Power must be greater than 0")
            if rate <= 0:
                validation_errors.append("Rate must be greater than 0")
            if thickness <= 0:
                validation_errors.append("Thickness must be greater than 0")
            if crystal_monitor <= 0:
                validation_errors.append("Crystal Monitor must be greater than 0")

            # Display validation errors
            if validation_errors:
                st.error("**Please fix the following issues:**")
                for error in validation_errors:
                    st.error(f"• {error}")
            else:
                # Mark as submitted and save data
                st.session_state.form_submitted = True

                row_dict = {
                    "Date": entry_date,
                    "Material": material,
                    "Threshold_Power": threshold_power,
                    "Power_Deposition": deposition_power,
                    "Rate": rate,
                    "Thickness_nm": thickness,
                    "Measured_Thickness_nm": measured,
                    "Crystal_Monitor": crystal_monitor,
                    "Notes": notes,
                }
                append_row_to_csv(row_dict)

    # Reset button
    if st.session_state.form_submitted:
        if st.button("🔄 Add Another Entry"):
            st.session_state.form_submitted = False
            st.session_state.reset_counter += 1  # Forces new form with default values
            st.rerun()
