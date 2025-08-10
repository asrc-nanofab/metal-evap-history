# add_entry.py
import streamlit as st
from datetime import date
from src.neon_db import MetalEvapDB


def add_entry_page():
    st.title("Add New Deposition Entry")

    # Initialize session state for form reset
    if "form_counter" not in st.session_state:
        st.session_state.form_counter = 0

    # Initialize session state for success message
    if "show_success" not in st.session_state:
        st.session_state.show_success = False
    if "success_message" not in st.session_state:
        st.session_state.success_message = ""

    # Success message will be shown after the Add Entry button

    # Initialize database connection
    try:
        db = MetalEvapDB()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return

    # Get data for dropdowns
    try:
        users = db.get_user_names_for_dropdown()
        materials = [row["material_name"] for row in db.get_all_materials()]
    except Exception as e:
        st.error(f"Failed to load dropdown data: {e}")
        return

    # Check if we have users and materials
    if not users:
        st.error("No users found in database. Please add users first.")
        return

    if not materials:
        st.error("No materials found in database. Please populate materials first.")
        return

    # Auto-assign current date
    today = date.today()
    entry_date = today.strftime("%m/%d/%Y")
    st.write(f"**Date:** {entry_date}")

    # User selection - add "None" as first option
    user_options = ["None"] + users
    selected_user = st.selectbox(
        "User*",
        options=user_options,
        help="Select the user making this entry",
        key=f"user_select_{st.session_state.form_counter}",
    )

    # Material selection - add "None" as first option
    material_options = ["None"] + sorted(materials)
    material = st.selectbox(
        "Material*",
        options=material_options,
        help="Select the material being deposited",
        key=f"material_select_{st.session_state.form_counter}",
    )

    # Input widgets (not in a form) - add unique keys for session state
    threshold_power = st.number_input(
        "Threshold Power (%)*",
        min_value=0.0,
        max_value=100.0,
        value=None,
        step=0.1,
        placeholder="Enter threshold power % (0-100)",
        help="Enter threshold power % (0-100)",
        key=f"threshold_power_input_{st.session_state.form_counter}",
    )

    deposition_power = st.number_input(
        "Deposition Power (%)*",
        min_value=0.0,
        max_value=100.0,
        value=None,
        step=0.1,
        placeholder="Enter deposition power % (0-100)",
        help="Enter deposition power % (0-100)",
        key=f"deposition_power_input_{st.session_state.form_counter}",
    )

    rate = st.number_input(
        "Rate (A/s)*",
        min_value=0.0,
        max_value=100.0,
        value=None,
        step=0.01,
        placeholder="Enter deposition rate in Angstroms per second",
        help="Enter deposition rate in Angstroms per second (A/s)",
        key=f"rate_input_{st.session_state.form_counter}",
    )

    thickness = st.number_input(
        "Thickness (nm)*",
        min_value=0.0,
        max_value=10000.0,
        value=None,
        step=0.01,
        placeholder="Enter thickness displayed in nm",
        help="Enter thickness displayed in nm",
        key=f"thickness_input_{st.session_state.form_counter}",
    )

    measured = st.number_input(
        "Measured Thickness (nm) (OPTIONAL)",
        min_value=0.0,
        max_value=10000.0,
        value=None,
        step=0.01,
        placeholder="This value is optional and can be updated later",
        help="Enter measured thickness in nanometers (optional)",
        key=f"measured_input_{st.session_state.form_counter}",
    )

    crystal_monitor = st.number_input(
        "Crystal Monitor*",
        min_value=0.0,
        max_value=100.0,
        value=None,
        step=0.01,
        placeholder="Enter crystal monitor reading",
        help="Enter crystal monitor reading",
        key=f"crystal_monitor_input_{st.session_state.form_counter}",
    )

    notes = st.text_area(
        "Notes",
        height=100,
        placeholder="Enter detailed comments here...",
        key=f"notes_input_{st.session_state.form_counter}",
    )

    # Submit button
    if st.button("Add Entry", type="primary"):
        # Validation: Check for meaningful values
        validation_errors = []

        # Check for "None" selections
        if selected_user == "None":
            validation_errors.append("Please select a user")
        if material == "None":
            validation_errors.append("Please select a material")

        # Core required fields (must be > 0)
        if threshold_power is None or threshold_power <= 0:
            validation_errors.append("Threshold Power must be greater than 0")
        if deposition_power is None or deposition_power <= 0:
            validation_errors.append("Deposition Power must be greater than 0")
        if rate is None or rate <= 0:
            validation_errors.append("Rate must be greater than 0")
        if thickness is None or thickness <= 0:
            validation_errors.append("Thickness must be greater than 0")
        if crystal_monitor is None or crystal_monitor <= 0:
            validation_errors.append("Crystal Monitor must be greater than 0")

        # Display validation errors
        if validation_errors:
            st.error("**Please fix the following issues:**")
            for error in validation_errors:
                st.error(f"• {error}")
        else:
            # Add to database
            try:
                entry_id = db.add_entry_from_widgets(
                    user_name=selected_user,
                    material_name=material,
                    thickness=thickness,
                    threshold_pct=threshold_power,
                    deposition_pct=deposition_power,
                    dep_rate=rate,
                    crystal_pct=crystal_monitor,
                    measured_thickness=measured
                    if measured is not None and measured > 0
                    else None,
                    notes=notes if notes.strip() else None,
                )

                # Set success message in session state
                st.session_state.success_message = (
                    f"✅ Entry added successfully! (ID: {entry_id})"
                )
                st.session_state.show_success = True

                # Increment counter to force new widget instances
                st.session_state.form_counter += 1

                # Rerun to apply the reset
                st.rerun()

            except Exception as e:
                st.error(f"Failed to add entry: {e}")

    # Show success message if set (appears after the button)
    if st.session_state.show_success:
        st.success(st.session_state.success_message)
        # Clear the success message after showing it
        st.session_state.show_success = False
        st.session_state.success_message = ""

    # Close database connection
    db.disconnect()
