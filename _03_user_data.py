# edit_data.py
import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
from utils.app_utils import load_clean_data, save_edited_data_to_csv


def user_data_page():
    st.title("Edit Deposition Data")
    st.info(
        "💡 **Instructions**: View all data below, then select a specific row to edit."
    )

    df = load_clean_data()

    # Backup section
    st.subheader("📥 Backup Data")
    csv_backup = df.to_csv(index=False)
    st.download_button(
        "📄 Download Current Data as Backup",
        data=csv_backup,
        file_name=f"deposition_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        help="Download your data before making any edits",
    )

    st.markdown("---")

    # Display data
    st.subheader("📊 All Deposition Data")
    st.info("This table is read-only. Select a row below to edit it.")
    df_display = df.copy()
    df_display.index = df_display.index + 1
    st.dataframe(df_display, use_container_width=True, height=400)

    st.markdown("---")

    # Row selection
    st.subheader("✏️ Select Row to Edit")

    if len(df) == 0:
        st.warning("No data available to edit.")
        return

    selected_row_num = st.number_input(
        "Enter row number to edit:",
        min_value=1,
        max_value=len(df),
        value=1,
        step=1,
        help=f"Choose a row number between 1 and {len(df)}",
    )

    selected_row_idx = selected_row_num - 1
    selected_row = df.iloc[selected_row_idx].copy()

    # Show selection
    date_str = (
        pd.to_datetime(selected_row["Date"]).strftime("%m/%d/%Y")
        if pd.notna(selected_row["Date"])
        else "No Date"
    )
    material = (
        selected_row["Material"]
        if pd.notna(selected_row["Material"])
        else "No Material"
    )
    st.info(f"📍 **Selected**: Row {selected_row_num} - {date_str} - {material}")

    st.markdown("---")
    st.subheader(f"🔧 Editing Row {selected_row_num}")

    # Field configurations
    field_configs = {
        "Date": {"type": "date", "icon": "📅"},
        "Material": {"type": "selectbox", "icon": "🧪"},
        "Threshold_Power": {
            "type": "number",
            "label": "Threshold Power (%)",
            "min": 0.0,
            "max": 100.0,
            "icon": "⚡",
        },
        "Power_Deposition": {
            "type": "number",
            "label": "Deposition Power (%)",
            "min": 0.0,
            "max": 100.0,
            "icon": "⚡",
        },
        "Rate": {
            "type": "number",
            "label": "Rate (A/s)",
            "min": 0.0,
            "max": 100.0,
            "icon": "📈",
        },
        "Thickness_nm": {
            "type": "number",
            "label": "Thickness (per xTal Monitor)",
            "min": 0.0,
            "max": 10000.0,
            "icon": "📏",
        },
        # "Measured": {
        #     "type": "number",
        #     "label": "Measured",
        #     "min": 0.0,
        #     "max": 10000.0,
        #     "icon": "📐",
        # },
        # "Crystal_Monitor": {
        #     "type": "number",
        #     "label": "Crystal Monitor",
        #     "min": 0.0,
        #     "max": 100.0,
        #     "icon": "💎",
        # },
    }

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📋 Original Values**")
        # Show original values (read-only)
        orig_date = (
            pd.to_datetime(selected_row["Date"]).strftime("%m/%d/%Y")
            if pd.notna(selected_row["Date"])
            else ""
        )
        st.text_input("Date", value=orig_date, disabled=True)
        st.text_input("Material", value=selected_row["Material"], disabled=True)

        for field, config in field_configs.items():
            if config["type"] == "number":
                st.number_input(
                    config["label"], value=float(selected_row[field]), disabled=True
                )

    # Get new values
    new_values = {}
    with col2:
        st.markdown("**✏️ New Values**")

        # Date field
        try:
            orig_date_obj = pd.to_datetime(selected_row["Date"]).date()
        except:  # noqa: E722
            orig_date_obj = date.today()
        new_values["Date"] = st.date_input("Date", value=orig_date_obj, key="new_date")

        # Material field
        current_materials = sorted(df["Material"].unique().tolist())
        current_material_idx = (
            current_materials.index(selected_row["Material"])
            if selected_row["Material"] in current_materials
            else 0
        )
        new_values["Material"] = st.selectbox(
            "Material",
            options=current_materials,
            index=current_material_idx,
            key="new_material",
        )

        # Number fields
        for field, config in field_configs.items():
            if config["type"] == "number":
                new_values[field] = st.number_input(
                    config["label"],
                    min_value=config["min"],
                    max_value=config["max"],
                    value=float(selected_row[field]),
                    step=0.01,
                    key=f"new_{field.lower()}",
                )

    # Detect changes
    changes = {}
    changes["Date"] = new_values["Date"] != orig_date_obj
    changes["Material"] = new_values["Material"] != selected_row["Material"]
    for field in field_configs:
        if field_configs[field]["type"] == "number":
            changes[field] = new_values[field] != float(selected_row[field])

    changes_detected = any(changes.values())

    # Show changes
    if changes_detected:
        st.markdown("---")
        st.warning("🔄 **Changes Detected:**")

        with st.expander("View Specific Changes", expanded=True):
            if changes["Date"]:
                st.write(
                    f"📅 Date: {orig_date} → {new_values['Date'].strftime('%m/%d/%Y')}"
                )
            if changes["Material"]:
                st.write(
                    f"🧪 Material: {selected_row['Material']} → {new_values['Material']}"
                )

            for field, config in field_configs.items():
                if config["type"] == "number" and changes[field]:
                    old_val = selected_row[field]
                    new_val = new_values[field]
                    unit = (
                        "%"
                        if "Power" in config["label"]
                        else ("A/s" if "Rate" in config["label"] else "")
                    )
                    st.write(
                        f"{config['icon']} {config['label']}: {old_val}{unit} → {new_val}{unit}"
                    )

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Save Changes", type="primary", disabled=not changes_detected):
            # Prepare row data
            new_row_data = {
                "Date": new_values["Date"].strftime("%m/%d/%Y"),
                "Material": new_values["Material"],
                **{
                    field: new_values[field]
                    for field in field_configs
                    if field_configs[field]["type"] == "number"
                },
            }

            # Update and save
            df_updated = df.copy()
            for col, value in new_row_data.items():
                df_updated.at[selected_row_idx, col] = value

            if save_edited_data_to_csv(df_updated):
                st.success(f"✅ Row {selected_row_idx + 1} updated successfully!")
                st.info("🔄 Refresh the page to see all updates.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to save changes!")

    with col2:
        st.info("💡 **To discard changes:** Navigate away or select a different row")

    with col3:
        st.metric("Editing Row", f"{selected_row_num} of {len(df)}")
