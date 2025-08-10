# user_data.py
import streamlit as st
from src.data_service import get_and_format_tool_data
from src.neon_db import MetalEvapDB
import logging

# Set up logging (only for errors)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def user_data_page():
    st.title("📊 User Data")
    # below the title, add a horizontal line
    st.info(
        "This page allows you to view and edit deposition data for a specific user."
    )

    # Get data from database using separated service
    df = get_and_format_tool_data()

    # Get unique users from the DataFrame (only users with data)
    if not df.empty:
        # Extract unique users from the data
        unique_users = sorted(df["User"].unique().tolist())
        user_options = ["All Users"] + unique_users
    else:
        unique_users = []
        user_options = ["All Users"]

    # User selection in sidebar
    st.sidebar.subheader("👤 Select User")

    if not unique_users:
        st.sidebar.warning("No users with data found.")
        return

    selected_user_name = st.sidebar.selectbox(
        "Choose a user:", options=user_options, index=0
    )

    # Filter data based on selected user
    if selected_user_name == "All Users":
        filtered_df = df
        st.sidebar.info("Showing data for all users")
    else:
        # Filter DataFrame by selected user name
        filtered_df = df[df["User"] == selected_user_name]
        st.sidebar.info(f"Showing data for {selected_user_name}")

    if filtered_df.empty:
        st.error("No data found for the selected user.")
        return

    # Display filtered data
    if selected_user_name == "All Users":
        st.subheader("👥 All Deposition Data")
    else:
        st.subheader(f"👤 Data for {selected_user_name}")

    # Summary statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Records", len(filtered_df))
    with col2:
        st.metric("Unique Materials", len(filtered_df["Material"].unique()))

    # Sort by date in descending order (most recent first)
    df_display = filtered_df.sort_values("Date", ascending=False).copy()

    # Select only the columns we want to display
    display_columns = [
        "Date",
        "Material",
        "Threshold_Power",
        "Power_Deposition",
        "Rate",
        "Thickness",
        "Measured_Thickness",
        "Crystal_Monitor",
        "Notes",
    ]
    df_display = df_display[display_columns]

    # Format date for display
    if "Date" in df_display.columns and not df_display.empty:
        df_display["Date"] = df_display["Date"].dt.strftime("%m/%d/%Y")

    # Add row numbers for easier reference
    # The index will start at 1, not 0 !!
    df_display.index = range(1, len(df_display) + 1)

    # Display the table with row selection
    st.dataframe(df_display, use_container_width=True)

    # Edit button to show/hide edit section
    st.markdown("---")

    # Initialize session state for edit mode
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    # Toggle edit mode with button
    if st.button("✏️ Edit Row", type="primary"):
        st.session_state.edit_mode = not st.session_state.edit_mode

    if st.session_state.edit_mode and len(df_display) > 0:
        st.subheader("✏️ Edit Row")
        st.info("Select a row number to view and edit its data.")

        # Row selector - number input for better performance with many rows
        max_row = len(df_display)
        selected_row = st.number_input(
            f"Enter row number to edit (1 to {max_row}):",
            min_value=1,
            max_value=max_row,
            value=1,
            step=1,
            help=f"Enter a number between 1 and {max_row} to select which row to edit",
        )

        if selected_row:
            # Convert to int to ensure we have an integer row number
            selected_row = int(selected_row)

            # Get the original data (before display formatting)
            # We need to use the same DataFrame that was used to create df_display
            # df_display was created from filtered_df with sorting and column selection
            sorted_filtered_df = filtered_df.sort_values("Date", ascending=False)
            original_row = sorted_filtered_df.iloc[selected_row - 1]
            st.write(f"**Tool Data Row ID:** {original_row['Tool_Data_ID']}")
            st.markdown("---")
            # Display selected row data
            st.subheader(f"📋 Row {selected_row} Data")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Current Values:**")

                # Display widgets that line up with input widgets
                st.text_input(
                    "Date:",
                    value=original_row["Date"].strftime("%m/%d/%Y"),
                    disabled=True,
                    key=f"current_date_{selected_row}",
                )
                st.text_input(
                    "User:",
                    value=original_row["User"],
                    disabled=True,
                    key=f"current_user_{selected_row}",
                )
                st.text_input(
                    "Material:",
                    value=original_row["Material"],
                    disabled=True,
                    key=f"current_material_{selected_row}",
                )
                st.text_input(
                    "Threshold Power:",
                    value=str(original_row["Threshold_Power"]),
                    disabled=True,
                    key=f"current_threshold_{selected_row}",
                )
                st.text_input(
                    "Power Deposition:",
                    value=str(original_row["Power_Deposition"]),
                    disabled=True,
                    key=f"current_power_{selected_row}",
                )
                st.text_input(
                    "Rate:",
                    value=str(original_row["Rate"]),
                    disabled=True,
                    key=f"current_rate_{selected_row}",
                )
                st.text_input(
                    "Thickness:",
                    value=str(original_row["Thickness"]),
                    disabled=True,
                    key=f"current_thickness_{selected_row}",
                )
                st.text_input(
                    "Measured Thickness:",
                    value=str(original_row["Measured_Thickness"])
                    if original_row["Measured_Thickness"] is not None
                    else "Not measured",
                    disabled=True,
                    key=f"current_measured_{selected_row}",
                )
                st.text_input(
                    "Crystal Monitor:",
                    value=str(original_row["Crystal_Monitor"]),
                    disabled=True,
                    key=f"current_crystal_{selected_row}",
                )
                st.text_area(
                    "Notes:",
                    value=str(original_row.get("Notes", ""))
                    if original_row.get("Notes")
                    else "No notes",
                    disabled=True,
                    height=80,
                    key=f"current_notes_{selected_row}",
                )

            with col2:
                st.write("**New Values:**")

                # Input widgets for editing
                new_date = st.date_input(
                    "Date:",
                    value=original_row["Date"].date(),
                    format="MM/DD/YYYY",
                    key=f"date_{selected_row}",
                )

                new_user = st.text_input(
                    "User:", value=original_row["User"], key=f"user_{selected_row}"
                )

                new_material = st.text_input(
                    "Material:",
                    value=original_row["Material"],
                    key=f"material_{selected_row}",
                )

                new_threshold_power = st.number_input(
                    "Threshold Power:",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(original_row["Threshold_Power"]),
                    step=0.1,
                    key=f"threshold_{selected_row}",
                )

                new_power_deposition = st.number_input(
                    "Power Deposition:",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(original_row["Power_Deposition"]),
                    step=0.1,
                    key=f"power_{selected_row}",
                )

                new_rate = st.number_input(
                    "Rate:",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(original_row["Rate"]),
                    step=0.1,
                    key=f"rate_{selected_row}",
                )

                new_thickness = st.number_input(
                    "Thickness:",
                    min_value=0.0,
                    max_value=10000.0,
                    value=float(original_row["Thickness"]),
                    step=0.1,
                    key=f"thickness_{selected_row}",
                )

                new_measured_thickness = st.number_input(
                    "Measured Thickness:",
                    min_value=0.0,
                    max_value=10000.0,
                    value=float(original_row["Measured_Thickness"])
                    if original_row["Measured_Thickness"] is not None
                    else None,
                    step=0.1,
                    help="Optional - leave empty if not measured",
                    key=f"measured_{selected_row}",
                )

                new_crystal_monitor = st.number_input(
                    "Crystal Monitor:",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(original_row["Crystal_Monitor"]),
                    step=0.1,
                    key=f"crystal_{selected_row}",
                )

                # Notes field (if we want to add it later)
                new_notes = st.text_area(
                    "Notes:",
                    value=str(original_row.get("Notes", ""))
                    if original_row.get("Notes")
                    else "",
                    height=80,
                    key=f"notes_{selected_row}",
                )

                # Save/Cancel buttons
                st.markdown("---")
                col_save, col_cancel = st.columns(2)

                with col_save:
                    if st.button("💾 Save Changes", key=f"save_{selected_row}"):
                        # Get the Tool Data ID for the update
                        tool_data_id = int(original_row["Tool_Data_ID"])

                        # Validation: Same pattern as add_entry_page
                        validation_errors = []

                        if not new_user.strip():
                            validation_errors.append("User name cannot be empty")
                        if not new_material.strip():
                            validation_errors.append("Material cannot be empty")
                        if new_threshold_power <= 0:
                            validation_errors.append(
                                "Threshold Power must be greater than 0"
                            )
                        if new_power_deposition <= 0:
                            validation_errors.append(
                                "Power Deposition must be greater than 0"
                            )
                        if new_rate <= 0:
                            validation_errors.append("Rate must be greater than 0")
                        if new_thickness <= 0:
                            validation_errors.append("Thickness must be greater than 0")
                        if new_crystal_monitor <= 0:
                            validation_errors.append(
                                "Crystal Monitor must be greater than 0"
                            )

                        # Display validation errors
                        if validation_errors:
                            st.error("**Please fix the following issues:**")
                            for error in validation_errors:
                                st.error(f"• {error}")
                        else:
                            # Update to database
                            try:
                                db = MetalEvapDB()

                                success = db.update_tool_data(
                                    tool_data_id=tool_data_id,
                                    user_name=new_user,
                                    material_name=new_material,
                                    date_recorded=new_date.strftime("%Y-%m-%d"),
                                    threshold_pct=new_threshold_power,
                                    deposition_pct=new_power_deposition,
                                    dep_rate=new_rate,
                                    thickness=new_thickness,
                                    measured_thickness=new_measured_thickness
                                    if new_measured_thickness is not None
                                    and new_measured_thickness > 0
                                    else None,
                                    crystal_pct=new_crystal_monitor,
                                    notes=new_notes.strip()
                                    if new_notes.strip()
                                    else None,
                                )

                                db.disconnect()

                                if success:
                                    st.success(
                                        f"✅ Successfully updated entry ID {tool_data_id}!"
                                    )
                                    st.rerun()
                                else:
                                    st.error("❌ No changes were made to the database.")

                            except Exception as e:
                                st.error(f"❌ Error updating entry: {str(e)}")
                                logger.error(f"Database update error: {e}")

                with col_cancel:
                    if st.button("❌ Cancel", key=f"cancel_{selected_row}"):
                        st.info("Edit cancelled. No changes were made.")
                        st.rerun()  # Refresh the page to hide edit section
    elif st.session_state.edit_mode and len(df_display) == 0:
        st.warning("No data available to edit.")
