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

    # Initialize session state for navigation
    if "active_section" not in st.session_state:
        st.session_state.active_section = None

    # Show success/error messages if set
    if st.session_state.user_success:
        st.success(st.session_state.user_message)
        st.session_state.user_success = False
        st.session_state.user_message = ""

    if st.session_state.material_success:
        st.success(st.session_state.material_message)
        st.session_state.material_success = False
        st.session_state.material_message = ""

    # Navigation buttons
    st.markdown("---")
    st.subheader("Select an action:")

    # Create three columns for navigation buttons
    nav_col1, nav_col2, nav_col3 = st.columns(3)

    with nav_col1:
        if st.button(
            "👤 Add User",
            use_container_width=True,
            type="primary"
            if st.session_state.active_section == "add_user"
            else "secondary",
        ):
            st.session_state.active_section = "add_user"
            st.rerun()

    with nav_col2:
        if st.button(
            "🧪 Add Material",
            use_container_width=True,
            type="primary"
            if st.session_state.active_section == "add_material"
            else "secondary",
        ):
            st.session_state.active_section = "add_material"
            st.rerun()

    with nav_col3:
        if st.button(
            "💾 Database Backup",
            use_container_width=True,
            type="primary"
            if st.session_state.active_section == "database_backup"
            else "secondary",
        ):
            st.session_state.active_section = "database_backup"
            st.rerun()

    st.markdown("---")

    # ===== CONDITIONAL SECTIONS BASED ON NAVIGATION =====

    # ===== USER MANAGEMENT SECTION =====
    if st.session_state.active_section == "add_user":
        st.header("👤 Add New User")

        # User input fields
        first_name = st.text_input("First Name*", key="user_first_name")
        last_name = st.text_input("Last Name*", key="user_last_name")
        email = st.text_input("Email (Optional)", key="user_email")

        # Add user button
        if st.button(
            "Add User", key="add_user_button", type="primary", use_container_width=True
        ):
            # Strip whitespace from inputs
            first_name_clean = first_name.strip()
            last_name_clean = last_name.strip()
            email_clean = email.strip() if email else None

            # Validate inputs
            if not first_name_clean or not last_name_clean:
                st.error("First name and last name are required")
            else:
                try:
                    # Add user to database
                    user_id = db.add_user(
                        first_name=first_name_clean,
                        last_name=last_name_clean,
                        email=email_clean,
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
    elif st.session_state.active_section == "add_material":
        st.header("🧪 Add New Material")

        # Material input fields
        material_name = st.text_input("Material Name*", key="material_name")
        abbreviation = st.text_input("Abbreviation*", key="material_abbreviation")

        # Add material button
        if st.button(
            "Add Material",
            key="add_material_button",
            type="primary",
            use_container_width=True,
        ):
            # Strip whitespace from inputs
            material_name_clean = material_name.strip()
            abbreviation_clean = abbreviation.strip()

            # Validate inputs
            if not material_name_clean or not abbreviation_clean:
                st.error("Material name and abbreviation are required")
            else:
                try:
                    # Add material to database
                    success = db.add_material(  # noqa: F841
                        material_name=material_name_clean,
                        abbreviation=abbreviation_clean,
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
    elif st.session_state.active_section == "database_backup":
        st.header("💾 Database Backup")

        # Add explanation
        st.write("""
        Create and download a ZIP backup of the database tables. 
        This will generate a single ZIP file containing CSV exports of users, materials, and tool data.
        """)

        # Center the backup button
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Create backup data
            with st.spinner("Preparing backup..."):
                success, zip_data, result = create_database_backup_zip()

            if success and zip_data:
                # Calculate size in KB
                size_kb = len(zip_data) / 1024

                # Single button that downloads immediately
                st.download_button(
                    label="📥 Download Database Backup",
                    data=zip_data,
                    file_name=result,
                    mime="application/zip",
                    key="download_zip_backup",
                    use_container_width=True,
                    type="primary",
                )

                # Show backup info
                st.info(f"✅ Backup ready for download ({size_kb:.1f} KB)")
            else:
                st.error(f"❌ Backup failed: {result}")
                # Show a disabled button for feedback
                st.button(
                    "📥 Download Database Backup",
                    disabled=True,
                    use_container_width=True,
                    type="primary",
                )

    # If no section is selected, show a helpful message
    elif st.session_state.active_section is None:
        st.info("👆 Please select an action from the buttons above to get started.")

    # Close database connection
    db.disconnect()
