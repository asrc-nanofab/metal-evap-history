# staff_only.py
import streamlit as st
from src.neon_db import MetalEvapDB
from utils.backup_utils import create_database_backup_zip


def staff_only_page():
    # Title with red warning icon
    st.markdown(
        """
    <h1 style="text-align: center;">
        <span style="color:red;">⚠️</span> STAFF ADMIN ONLY <span style="color:red;">⚠️</span>
    </h1>
    """,
        unsafe_allow_html=True,
    )

    # Add warning message with custom styling for center alignment
    st.markdown(
        """
        <div style="text-align: center; padding: 10px; background-color: #fffacd; border-left: 6px solid #ffcc00; margin-bottom: 15px; color: #856404;">
            <strong>WARNING:</strong> This page is restricted to staff administrators only.<br>
            Changes made here directly affect the database.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize database connection
    try:
        db = MetalEvapDB()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return

    # Initialize session state for success/error messages
    if "user_success" not in st.session_state:
        st.session_state.user_success = False
        st.session_state.user_message = ""

    if "material_success" not in st.session_state:
        st.session_state.material_success = False
        st.session_state.material_message = ""

    # Show success/error messages if set
    if st.session_state.user_success:
        st.success(st.session_state.user_message)
        st.session_state.user_success = False
        st.session_state.user_message = ""

    if st.session_state.material_success:
        st.success(st.session_state.material_message)
        st.session_state.material_success = False
        st.session_state.material_message = ""

    # Create two columns for the two sections
    col1, col2 = st.columns(2)

    # ===== USER MANAGEMENT SECTION =====
    with col1:
        st.header("Add New User")

        # User input fields
        first_name = st.text_input("First Name*", key="user_first_name")
        last_name = st.text_input("Last Name*", key="user_last_name")
        email = st.text_input("Email (Optional)", key="user_email")

        # Add user button
        if st.button("Add User", key="add_user_button"):
            # Validate inputs
            if not first_name or not last_name:
                st.error("First name and last name are required")
            else:
                try:
                    # Add user to database
                    user_id = db.add_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email if email else None,
                    )

                    # Set success message
                    st.session_state.user_success = True
                    st.session_state.user_message = (
                        f"✅ User added successfully! (ID: {user_id})"
                    )

                    # Clear inputs by rerunning
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to add user: {e}")

    # ===== MATERIAL MANAGEMENT SECTION =====
    with col2:
        st.header("Add New Material")

        # Material input fields
        material_name = st.text_input("Material Name*", key="material_name")
        abbreviation = st.text_input("Abbreviation*", key="material_abbreviation")

        # Add material button
        if st.button("Add Material", key="add_material_button"):
            # Validate inputs
            if not material_name or not abbreviation:
                st.error("Material name and abbreviation are required")
            else:
                try:
                    # Check if we need to add a function to add materials
                    # For now, we'll add a placeholder
                    success = db.add_material(  # noqa: F841
                        material_name=material_name, abbreviation=abbreviation
                    )

                    # Set success message
                    st.session_state.material_success = True
                    st.session_state.material_message = (
                        f"✅ Material added successfully!"  # noqa: F541
                    )

                    # Clear inputs by rerunning
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to add material: {e}")

        # ===== DATABASE BACKUP SECTION =====
    st.markdown("---")
    st.header("Database Backup")

    # Add explanation
    st.write("""
    Create and download a ZIP backup of the database tables. 
    This will generate a single ZIP file containing CSV exports of users, materials, and tool data.
    """)

    # Center the backup button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Backup button
        if st.button(
            "📥 Download Database Backup", type="primary", use_container_width=True
        ):
            with st.spinner("Creating backup ZIP file..."):
                success, zip_data, result = create_database_backup_zip()

                if success and zip_data:
                    # Calculate size in KB
                    size_kb = len(zip_data) / 1024

                    # Show success message with download button
                    st.success(
                        f"✅ Backup ZIP created successfully! ({size_kb:.1f} KB)"
                    )

                    # Add download button
                    st.download_button(
                        label="📥 Download ZIP Backup",
                        data=zip_data,
                        file_name=result,
                        mime="application/zip",
                        key="download_zip_backup",
                        use_container_width=True,
                    )
                else:
                    st.error(f"❌ Backup failed: {result}")

    # Close database connection
    db.disconnect()
