import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
import time
# Remove or comment out the wide layout
# st.set_page_config(layout="wide")


def load_clean_data():
    df = pd.read_csv("data/Ebeam_Deposition_Powers_CLEAN.csv")
    # Ensure Date is datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    # Normalize Material: strip spaces, lower, then title case
    df["Material"] = df["Material"].astype(str).str.strip().str.lower().str.title()
    # Remove rows with invalid or blank material names
    df = df[df["Material"].notna() & (df["Material"].str.strip() != "")]
    return df


def append_row_to_csv(row_dict):
    df = pd.read_csv("data/Ebeam_Deposition_Powers_CLEAN.csv")
    columns = df.columns.tolist()
    # Format date as MM/DD/YYYY
    if isinstance(row_dict["Date"], (pd.Timestamp, date, datetime)):
        row_dict["Date"] = pd.to_datetime(row_dict["Date"]).strftime("%m/%d/%Y")
    else:
        row_dict["Date"] = str(row_dict["Date"])
    new_row = {col: row_dict.get(col, "") for col in columns}
    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df], ignore_index=True)
    df.to_csv("data/Ebeam_Deposition_Powers_CLEAN.csv", index=False)
    st.success("Entry added! Reload the View Data page to see the update.")


def save_edited_data_to_csv(edited_df):
    """Save the entire edited DataFrame back to CSV."""
    try:
        # Format dates consistently
        if "Date" in edited_df.columns:
            edited_df["Date"] = pd.to_datetime(
                edited_df["Date"], errors="coerce"
            ).dt.strftime("%m/%d/%Y")

        # Save to CSV
        edited_df.to_csv("data/Ebeam_Deposition_Powers_CLEAN.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False


# --- Multipage App ---
page = st.sidebar.radio("Choose a page", ["View Data", "Add Entry", "Edit Data"])

df = load_clean_data()

if page == "View Data":
    # Sidebar: material selector (only valid, normalized names)
    materials = sorted(df["Material"].unique())
    material = st.sidebar.selectbox("Select material", materials)

    # Filter data using normalized material
    filtered = df[df["Material"] == material].sort_values("Date")

    # Date range selector (separate fields)
    if not filtered.empty:
        filtered["Date"] = pd.to_datetime(filtered["Date"], errors="coerce")
        min_date = filtered["Date"].min().date()
        max_date = filtered["Date"].max().date()
        start_date = st.sidebar.date_input(
            "Start date", value=min_date, min_value=min_date, max_value=max_date
        )
        end_date = st.sidebar.date_input(
            "End date", value=max_date, min_value=min_date, max_value=max_date
        )
        # Filter by date range
        mask = (filtered["Date"] >= pd.to_datetime(start_date)) & (
            filtered["Date"] <= pd.to_datetime(end_date)
        )
        filtered = filtered[mask]

    st.title(f"Deposition Data for {material}")

    fig, ax1 = plt.subplots(figsize=(8, 4))

    # Plot Deposition Power and Threshold Power on Y-axis, Date on X-axis
    ax1.plot(
        filtered["Date"],
        filtered["Power_Deposition"],
        label="Deposition Power",
        marker="o",
    )
    ax1.plot(
        filtered["Date"],
        filtered["Threshold_Power"],
        label="Threshold Power",
        marker="o",
    )

    ax1.set_xlabel("Date")
    ax1.set_ylabel("Power")
    ax1.legend(loc="upper left")

    st.pyplot(fig)

    # Show filtered data table for selected material
    st.subheader(f"Raw Data for {material}")
    table_df = filtered.reset_index(drop=True).copy()
    if "Date" in table_df.columns:
        table_df["Date"] = table_df["Date"].dt.strftime("%m/%d/%Y")
    st.dataframe(table_df, use_container_width=True)

elif page == "Add Entry":
    st.title("Add New Deposition Entry")
    with st.form("add_entry_form"):
        today = date.today()
        entry_date = today.strftime("%m/%d/%Y")
        st.write(f"Date: {entry_date}")
        # Use normalized material names for dropdown
        materials = sorted(df["Material"].unique())
        material = st.selectbox("Material", materials)
        threshold_power = st.number_input(
            "Threshold Power (%)", min_value=0.0, max_value=100.0, step=0.01
        )
        deposition_power = st.number_input(
            "Deposition Power (%)", min_value=0.0, max_value=100.0, step=0.01
        )
        rate = st.number_input("Rate (A/s)", min_value=0.0, max_value=100.0, step=0.01)
        thickness = st.number_input(
            "Thickness (per xTal Monitor)", min_value=0.0, max_value=10000.0, step=0.01
        )
        crystal_monitor = st.number_input(
            "Crystal Monitor", min_value=0.0, max_value=100.0, step=0.01
        )
        submitted = st.form_submit_button("Add Entry")
        if submitted:
            row_dict = {
                "Date": entry_date,
                "Material": material,
                "Threshold_Power": threshold_power,
                "Power_Deposition": deposition_power,
                "Rate": rate,
                "Thickness_nm": thickness,
                "Crystal_Monitor": crystal_monitor,
            }

            append_row_to_csv(row_dict)

elif page == "Edit Data":
    st.title("Edit Deposition Data")

    st.info(
        "💡 **Instructions**: Click on any cell to edit it. Add or delete rows using the controls."
    )
    st.warning(
        "⚠️ **Important**: Changes will overwrite your CSV file. Consider making a backup first."
    )

    # Create a copy for editing to avoid modifying the original
    df_to_edit = df.copy()

    # Configure editable columns
    edited_df = st.data_editor(
        df_to_edit,
        use_container_width=True,
        num_rows="dynamic",  # Allow adding/deleting rows
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                help="Entry date",
                format="MM/DD/YYYY",
            ),
            "Material": st.column_config.SelectboxColumn(
                "Material",
                help="Select material type",
                options=sorted(df["Material"].unique()),
                required=True,
            ),
            "Threshold_Power": st.column_config.NumberColumn(
                "Threshold Power (%)",
                help="Threshold power percentage",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f",
            ),
            "Power_Deposition": st.column_config.NumberColumn(
                "Deposition Power (%)",
                help="Power used for deposition",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f",
            ),
            "Rate": st.column_config.NumberColumn(
                "Rate (A/s)",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f",
            ),
            "Thickness_nm": st.column_config.NumberColumn(
                "Thickness (per xTal Monitor)",
                min_value=0.0,
                max_value=10000.0,
                step=0.01,
                format="%.2f",
            ),
            "Crystal_Monitor": st.column_config.NumberColumn(
                "Crystal Monitor",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f",
            ),
        },
        key="data_editor",
    )

    # Show changes detection
    changes_made = not edited_df.equals(df_to_edit)

    if changes_made:
        st.warning("🔄 You have unsaved changes!")

        # Show what changed (simple version)
        with st.expander("View Changes", expanded=False):
            # Row count changes
            if len(edited_df) != len(df_to_edit):
                st.write(f"📊 Row count: {len(df_to_edit)} → {len(edited_df)}")

            # Content changes
            if len(edited_df) == len(df_to_edit):
                # Same number of rows, so check for content changes
                try:
                    # Find which rows are different
                    comparison = edited_df.compare(
                        df_to_edit, names=("updated", "original")
                    )
                    if not comparison.empty:
                        st.write("✏️ **Modified cells detected:**")
                        st.dataframe(comparison, use_container_width=True)
                except Exception:
                    st.write("✏️ Cell modifications detected")

            # Summary
            st.write(
                "💡 Click 'Save Changes' to apply these modifications to your CSV file"
            )

    # Save controls
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Save Changes", type="primary", disabled=not changes_made):
            # Optional: Validate with Pydantic here if you want
            if save_edited_data_to_csv(edited_df):
                st.success("✅ Changes saved successfully!")
                st.info("🔄 Refresh the page to see updates on other pages.")
                time.sleep(1)  # Brief pause so user sees the success message
                st.rerun()
            else:
                st.error("❌ Failed to save changes!")

    with col2:
        if st.button("🔄 Discard Changes", disabled=not changes_made):
            st.rerun()

    with col3:
        # Export current view to CSV
        csv_data = edited_df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=f"deposition_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    # Display some stats
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entries", len(edited_df))
    with col2:
        st.metric("Materials", edited_df["Material"].nunique())
    with col3:
        if changes_made:
            st.metric("Unsaved Changes", "Yes", delta="⚠️")
        else:
            st.metric("Unsaved Changes", "No", delta="✅")
