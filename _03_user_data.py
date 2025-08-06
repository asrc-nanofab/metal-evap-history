# user_data.py
import streamlit as st
from src.data_service import get_and_format_tool_data
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

    # Show basic info in sidebar
    st.sidebar.write(f"Total records: {len(filtered_df)}")

    if not filtered_df.empty:
        st.sidebar.write(
            f"Date range: {filtered_df['Date'].min().strftime('%m/%d/%Y')} to {filtered_df['Date'].max().strftime('%m/%d/%Y')}"
        )
        st.sidebar.write(
            f"Materials: {', '.join(sorted(filtered_df['Material'].unique()))}"
        )

    if filtered_df.empty:
        st.error("No data found for the selected user.")
        return

    # Display filtered data
    if selected_user_name == "All Users":
        st.subheader("📊 All Deposition Data")
    else:
        st.subheader(f"📊 Data for {selected_user_name}")

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
        "Crystal_Monitor",
    ]
    df_display = df_display[display_columns]

    # Format date for display
    if "Date" in df_display.columns and not df_display.empty:
        df_display["Date"] = df_display["Date"].dt.strftime("%m/%d/%Y")

    # Add row numbers for easier reference
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

        # Row selector
        selected_row = st.selectbox(
            "Choose a row to edit:",
            options=df_display.index.tolist(),
            format_func=lambda x: f"Row {x}",
        )

        if selected_row:
            # Get the original data (before display formatting)
            # We need to use the same DataFrame that was used to create df_display
            # df_display was created from filtered_df with sorting and column selection
            sorted_filtered_df = filtered_df.sort_values("Date", ascending=False)
            original_row = sorted_filtered_df.iloc[selected_row - 1]

            # Display selected row data
            st.subheader(f"📋 Row {selected_row} Data")

            col1, col2 = st.columns(2)

            # Show Tool Data ID separately
            st.write(f"**Tool Data ID:** {original_row['Tool_Data_ID']}")
            st.markdown("---")

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
                    "Crystal Monitor:",
                    value=str(original_row["Crystal_Monitor"]),
                    disabled=True,
                    key=f"current_crystal_{selected_row}",
                )

            with col2:
                st.write("**New Values:**")

                # Input widgets for editing
                new_date = st.date_input(
                    "Date:",
                    value=original_row["Date"].date(),
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
                    value=float(original_row["Threshold_Power"]),
                    step=0.1,
                    key=f"threshold_{selected_row}",
                )

                new_power_deposition = st.number_input(
                    "Power Deposition:",
                    value=float(original_row["Power_Deposition"]),
                    step=0.1,
                    key=f"power_{selected_row}",
                )

                new_rate = st.number_input(
                    "Rate:",
                    value=float(original_row["Rate"]),
                    step=0.1,
                    key=f"rate_{selected_row}",
                )

                new_thickness = st.number_input(
                    "Thickness:",
                    value=float(original_row["Thickness"]),
                    step=0.1,
                    key=f"thickness_{selected_row}",
                )

                new_crystal_monitor = st.number_input(
                    "Crystal Monitor:",
                    value=float(original_row["Crystal_Monitor"]),
                    step=0.1,
                    key=f"crystal_{selected_row}",
                )

                # Save/Cancel buttons
                st.markdown("---")
                col_save, col_cancel = st.columns(2)

                with col_save:
                    if st.button("💾 Save Changes", key=f"save_{selected_row}"):
                        st.success(
                            "Save functionality will be implemented in the next step!"
                        )

                with col_cancel:
                    if st.button("❌ Cancel", key=f"cancel_{selected_row}"):
                        st.info("Edit cancelled. No changes were made.")
                        st.rerun()  # Refresh the page to hide edit section
    elif st.session_state.edit_mode and len(df_display) == 0:
        st.warning("No data available to edit.")
