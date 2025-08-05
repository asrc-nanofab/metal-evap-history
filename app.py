# app.py
import streamlit as st

from _01_view_data import view_data_page
from _02_add_entry import add_entry_page
from _03_user_data import user_data_page

# Page configuration
# st.set_page_config(page_title="Metal Evaporation History")  # , layout="wide")

# # Sidebar navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Choose a page", ["View Data", "Add Entry", "User Data"])

# # Route to appropriate page
# if page == "View Data":
#     view_data_page()
# elif page == "Add Entry":
#     add_entry_page()
# elif page == "User Data":
#     user_data_page()

# ------------------------------------------------------------------------------------------------

# app.py
import streamlit as st

from _01_view_data import view_data_page
from _02_add_entry import add_entry_page
from _03_user_data import user_data_page

# Page configuration
st.set_page_config(page_title="Metal Evaporation History")

# Page mapping - define once, use everywhere
PAGES = {
    "View Data": view_data_page,
    "Add Entry": add_entry_page,
    "User Data": user_data_page,
}

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", list(PAGES.keys()))

# Route to appropriate page
PAGES[page]()


# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import date, datetime
# import time
# # Remove or comment out the wide layout
# # st.set_page_config(layout="wide")


# def load_clean_data():
#     df = pd.read_csv("data/Ebeam_Deposition_Powers_CLEAN.csv")
#     # Ensure Date is datetime
#     df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#     # Normalize Material: strip spaces, lower, then title case
#     df["Material"] = df["Material"].astype(str).str.strip().str.lower().str.title()
#     # Remove rows with invalid or blank material names
#     df = df[df["Material"].notna() & (df["Material"].str.strip() != "")]
#     return df


# def append_row_to_csv(row_dict):
#     df = pd.read_csv("data/Ebeam_Deposition_Powers_CLEAN.csv")
#     columns = df.columns.tolist()
#     # Format date as MM/DD/YYYY
#     if isinstance(row_dict["Date"], (pd.Timestamp, date, datetime)):
#         row_dict["Date"] = pd.to_datetime(row_dict["Date"]).strftime("%m/%d/%Y")
#     else:
#         row_dict["Date"] = str(row_dict["Date"])
#     new_row = {col: row_dict.get(col, "") for col in columns}
#     new_row_df = pd.DataFrame([new_row])
#     df = pd.concat([df, new_row_df], ignore_index=True)
#     df.to_csv("data/Ebeam_Deposition_Powers_CLEAN.csv", index=False)
#     st.success("Entry added! Reload the View Data page to see the update.")


# def save_edited_data_to_csv(edited_df):
#     """Save the entire edited DataFrame back to CSV."""
#     try:
#         # Format dates consistently
#         if "Date" in edited_df.columns:
#             edited_df["Date"] = pd.to_datetime(
#                 edited_df["Date"], errors="coerce"
#             ).dt.strftime("%m/%d/%Y")

#         # Save to CSV
#         edited_df.to_csv("data/Ebeam_Deposition_Powers_CLEAN.csv", index=False)
#         return True
#     except Exception as e:
#         st.error(f"Error saving data: {e}")
#         return False


# # --- Multipage App ---
# page = st.sidebar.radio("Choose a page", ["View Data", "Add Entry", "Edit Data"])

# df = load_clean_data()

# if page == "View Data":
#     # Sidebar: material selector (only valid, normalized names)
#     materials = sorted(df["Material"].unique())
#     material = st.sidebar.selectbox("Select material", materials)

#     # Filter data using normalized material
#     filtered = df[df["Material"] == material].sort_values("Date")

#     # Date range selector (separate fields)
#     if not filtered.empty:
#         filtered["Date"] = pd.to_datetime(filtered["Date"], errors="coerce")
#         min_date = filtered["Date"].min().date()
#         max_date = filtered["Date"].max().date()
#         start_date = st.sidebar.date_input(
#             "Start date", value=min_date, min_value=min_date, max_value=max_date
#         )
#         end_date = st.sidebar.date_input(
#             "End date", value=max_date, min_value=min_date, max_value=max_date
#         )
#         # Filter by date range
#         mask = (filtered["Date"] >= pd.to_datetime(start_date)) & (
#             filtered["Date"] <= pd.to_datetime(end_date)
#         )
#         filtered = filtered[mask]

#     st.title(f"Deposition Data for {material}")

#     fig, ax1 = plt.subplots(figsize=(8, 4))

#     # Plot Deposition Power and Threshold Power on Y-axis, Date on X-axis
#     ax1.plot(
#         filtered["Date"],
#         filtered["Power_Deposition"],
#         label="Deposition Power",
#         marker="o",
#     )
#     ax1.plot(
#         filtered["Date"],
#         filtered["Threshold_Power"],
#         label="Threshold Power",
#         marker="o",
#     )

#     ax1.set_xlabel("Date")
#     ax1.set_ylabel("Power")
#     ax1.legend(loc="upper left")

#     st.pyplot(fig)

#     # Show filtered data table for selected material
#     st.subheader(f"Raw Data for {material}")
#     table_df = filtered.reset_index(drop=True).copy()
#     if "Date" in table_df.columns:
#         table_df["Date"] = table_df["Date"].dt.strftime("%m/%d/%Y")
#     st.dataframe(table_df, use_container_width=True)

# elif page == "Add Entry":
#     st.title("Add New Deposition Entry")
#     with st.form("add_entry_form"):
#         today = date.today()
#         entry_date = today.strftime("%m/%d/%Y")
#         st.write(f"Date: {entry_date}")
#         # Use normalized material names for dropdown
#         materials = sorted(df["Material"].unique())
#         material = st.selectbox("Material", materials)
#         threshold_power = st.number_input(
#             "Threshold Power (%)", min_value=0.0, max_value=100.0, step=0.01
#         )
#         deposition_power = st.number_input(
#             "Deposition Power (%)", min_value=0.0, max_value=100.0, step=0.01
#         )
#         rate = st.number_input("Rate (A/s)", min_value=0.0, max_value=100.0, step=0.01)
#         thickness = st.number_input(
#             "Thickness (per xTal Monitor)", min_value=0.0, max_value=10000.0, step=0.01
#         )
#         crystal_monitor = st.number_input(
#             "Crystal Monitor", min_value=0.0, max_value=100.0, step=0.01
#         )
#         submitted = st.form_submit_button("Add Entry")
#         if submitted:
#             row_dict = {
#                 "Date": entry_date,
#                 "Material": material,
#                 "Threshold_Power": threshold_power,
#                 "Power_Deposition": deposition_power,
#                 "Rate": rate,
#                 "Thickness_nm": thickness,
#                 "Crystal_Monitor": crystal_monitor,
#             }

#             append_row_to_csv(row_dict)

# elif page == "Edit Data":
#     st.title("Edit Deposition Data")

#     st.info(
#         "💡 **Instructions**: View all data below, then select a specific row to edit."
#     )

#     # Download backup before making any changes
#     st.subheader("📥 Backup Data")
#     csv_backup = df.to_csv(index=False)
#     st.download_button(
#         label="📄 Download Current Data as Backup",
#         data=csv_backup,
#         file_name=f"deposition_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
#         mime="text/csv",
#         help="Download your data before making any edits",
#     )

#     st.markdown("---")

#     # Display full dataframe (read-only)
#     st.subheader("📊 All Deposition Data")
#     st.info("This table is read-only. Select a row below to edit it.")

#     # Add row numbers for easier selection
#     df_display = df.copy()
#     df_display.index = df_display.index + 1  # Start row numbers from 1
#     st.dataframe(df_display, use_container_width=True, height=400)

#     st.markdown("---")

#     # Row selection
#     st.subheader("✏️ Select Row to Edit")

#     if len(df) == 0:
#         st.warning("No data available to edit.")
#     else:
#         # Simple number input for row selection
#         selected_row_num = st.number_input(
#             "Enter row number to edit:",
#             min_value=1,
#             max_value=len(df),
#             value=1,
#             step=1,
#             help=f"Choose a row number between 1 and {len(df)}",
#         )

#         # Convert to 0-based index
#         selected_row_idx = selected_row_num - 1

#         # Get the selected row data
#         selected_row = df.iloc[selected_row_idx].copy()

#         # Show which row is selected
#         date_str = (
#             pd.to_datetime(selected_row["Date"]).strftime("%m/%d/%Y")
#             if pd.notna(selected_row["Date"])
#             else "No Date"
#         )
#         material = (
#             selected_row["Material"]
#             if pd.notna(selected_row["Material"])
#             else "No Material"
#         )

#         st.info(f"📍 **Selected**: Row {selected_row_num} - {date_str} - {material}")

#         st.markdown("---")
#         st.subheader(f"🔧 Editing Row {selected_row_num}")

#         # Create two columns: Original vs New values
#         col1, col2 = st.columns(2)

#         with col1:
#             st.markdown("**📋 Original Values**")
#             # Display original values (read-only)
#             orig_date = (
#                 pd.to_datetime(selected_row["Date"]).strftime("%m/%d/%Y")
#                 if pd.notna(selected_row["Date"])
#                 else ""
#             )
#             st.text_input("Date", value=orig_date, disabled=True, key="orig_date")
#             st.text_input(
#                 "Material",
#                 value=selected_row["Material"],
#                 disabled=True,
#                 key="orig_material",
#             )
#             st.number_input(
#                 "Threshold Power (%)",
#                 value=float(selected_row["Threshold_Power"]),
#                 disabled=True,
#                 key="orig_threshold",
#             )
#             st.number_input(
#                 "Deposition Power (%)",
#                 value=float(selected_row["Power_Deposition"]),
#                 disabled=True,
#                 key="orig_deposition",
#             )
#             st.number_input(
#                 "Rate (A/s)",
#                 value=float(selected_row["Rate"]),
#                 disabled=True,
#                 key="orig_rate",
#             )
#             st.number_input(
#                 "Thickness (per xTal Monitor)",
#                 value=float(selected_row["Thickness_nm"]),
#                 disabled=True,
#                 key="orig_thickness",
#             )
#             st.number_input(
#                 "Crystal Monitor",
#                 value=float(selected_row["Crystal_Monitor"]),
#                 disabled=True,
#                 key="orig_crystal",
#             )

#         with col2:
#             st.markdown("**✏️ New Values**")
#             # Editable fields with original values as defaults

#             # Date field
#             try:
#                 orig_date_obj = pd.to_datetime(selected_row["Date"]).date()
#             except:  # noqa: E722
#                 orig_date_obj = date.today()

#             new_date = st.date_input(
#                 "Date",
#                 value=orig_date_obj,
#                 key="new_date",
#                 help="Select the new date",
#             )

#             # Material dropdown with current materials + ability to type new ones
#             current_materials = sorted(df["Material"].unique().tolist())
#             current_material_idx = (
#                 current_materials.index(selected_row["Material"])
#                 if selected_row["Material"] in current_materials
#                 else 0
#             )

#             new_material = st.selectbox(
#                 "Material",
#                 options=current_materials,
#                 index=current_material_idx,
#                 key="new_material",
#             )

#             # Numeric fields with validation
#             new_threshold = st.number_input(
#                 "Threshold Power (%)",
#                 min_value=0.0,
#                 max_value=100.0,
#                 value=float(selected_row["Threshold_Power"]),
#                 step=0.01,
#                 key="new_threshold",
#             )

#             new_deposition = st.number_input(
#                 "Deposition Power (%)",
#                 min_value=0.0,
#                 max_value=100.0,
#                 value=float(selected_row["Power_Deposition"]),
#                 step=0.01,
#                 key="new_deposition",
#             )

#             new_rate = st.number_input(
#                 "Rate (A/s)",
#                 min_value=0.0,
#                 max_value=100.0,
#                 value=float(selected_row["Rate"]),
#                 step=0.01,
#                 key="new_rate",
#             )

#             new_thickness = st.number_input(
#                 "Thickness (per xTal Monitor)",
#                 min_value=0.0,
#                 max_value=10000.0,
#                 value=float(selected_row["Thickness_nm"]),
#                 step=0.01,
#                 key="new_thickness",
#             )

#             new_crystal = st.number_input(
#                 "Crystal Monitor",
#                 min_value=0.0,
#                 max_value=100.0,
#                 value=float(selected_row["Crystal_Monitor"]),
#                 step=0.01,
#                 key="new_crystal",
#             )

#         # Check if any changes were made
#         changes_detected = (
#             new_date != orig_date_obj
#             or new_material != selected_row["Material"]
#             or new_threshold != float(selected_row["Threshold_Power"])
#             or new_deposition != float(selected_row["Power_Deposition"])
#             or new_rate != float(selected_row["Rate"])
#             or new_thickness != float(selected_row["Thickness_nm"])
#             or new_crystal != float(selected_row["Crystal_Monitor"])
#         )

#         # Show changes summary
#         if changes_detected:
#             st.markdown("---")
#             st.warning("🔄 **Changes Detected:**")

#             with st.expander("View Specific Changes", expanded=True):
#                 if new_date != orig_date_obj:
#                     st.write(f"📅 Date: {orig_date} → {new_date.strftime('%m/%d/%Y')}")
#                 if new_material != selected_row["Material"]:
#                     st.write(
#                         f"🧪 Material: {selected_row['Material']} → {new_material}"
#                     )
#                 if new_threshold != float(selected_row["Threshold_Power"]):
#                     st.write(
#                         f"⚡ Threshold Power: {selected_row['Threshold_Power']}% → {new_threshold}%"
#                     )
#                 if new_deposition != float(selected_row["Power_Deposition"]):
#                     st.write(
#                         f"⚡ Deposition Power: {selected_row['Power_Deposition']}% → {new_deposition}%"
#                     )
#                 if new_rate != float(selected_row["Rate"]):
#                     st.write(f"📈 Rate: {selected_row['Rate']} A/s → {new_rate} A/s")
#                 if new_thickness != float(selected_row["Thickness_nm"]):
#                     st.write(
#                         f"📏 Thickness: {selected_row['Thickness_nm']} → {new_thickness}"
#                     )
#                 if new_crystal != float(selected_row["Crystal_Monitor"]):
#                     st.write(
#                         f"💎 Crystal Monitor: {selected_row['Crystal_Monitor']} → {new_crystal}"
#                     )

#         # Action buttons
#         st.markdown("---")
#         col1, col2, col3 = st.columns(3)

#         with col1:
#             if st.button(
#                 "💾 Save Changes", type="primary", disabled=not changes_detected
#             ):
#                 # Create new row data - direct save, no validation
#                 new_row_data = {
#                     "Date": new_date.strftime("%m/%d/%Y"),
#                     "Material": new_material,
#                     "Threshold_Power": new_threshold,
#                     "Power_Deposition": new_deposition,
#                     "Rate": new_rate,
#                     "Thickness_nm": new_thickness,
#                     "Crystal_Monitor": new_crystal,
#                 }

#                 # Update the dataframe
#                 df_updated = df.copy()
#                 for col, value in new_row_data.items():
#                     df_updated.at[selected_row_idx, col] = value

#                 # Save to CSV directly
#                 if save_edited_data_to_csv(df_updated):
#                     st.success(f"✅ Row {selected_row_idx + 1} updated successfully!")
#                     st.info("🔄 Refresh the page to see all updates.")
#                     time.sleep(1)
#                     st.rerun()
#                 else:
#                     st.error("❌ Failed to save changes!")

#         with col2:
#             st.info(
#                 "💡 **To discard changes:** Navigate away or select a different row"
#             )

#         with col3:
#             # Show row info
#             st.metric("Editing Row", f"{selected_row_idx + 1} of {len(df)}")
