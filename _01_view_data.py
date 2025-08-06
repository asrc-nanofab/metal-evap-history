# view_data.py
import streamlit as st
import pandas as pd
from src.data_service import get_view_data
from src.graphing import display_chart, CHART_TYPES
import logging

# Set up logging (only for errors)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def view_data_page():
    # Get data from database using separated service
    df = get_view_data()

    # Get unique materials from the DataFrame (only materials with data)
    if not df.empty:
        materials = sorted(df["Material"].unique().tolist())
    else:
        materials = []

    # Show basic info in sidebar
    st.sidebar.write(f"Total records: {len(df)}")
    st.sidebar.write(f"Available materials: {len(materials)}")

    if df.empty:
        st.error("No data found in database. Please check if data has been imported.")
        return

    # Sidebar: material selector (from database)
    if not materials:
        st.error("No materials found in database.")
        return

    material = st.sidebar.selectbox("Select material", materials)

    # Filter data using normalized material
    filtered = df[df["Material"] == material].sort_values("Date")

    st.sidebar.write(f"Records for {material}: {len(filtered)}")

    # Date range selector (separate fields)
    if not filtered.empty:
        # Ensure Date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(filtered["Date"]):
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
    else:
        st.warning(f"No data found for material: {material}")

    st.title(f"Deposition Data for {material}")

    # Chart type selector
    chart_type = st.selectbox(
        "Select Chart Type",
        options=list(CHART_TYPES.keys()),
        format_func=lambda x: CHART_TYPES[x],
        index=0,  # Default to box plot
    )

    # Only show chart and table if we have data
    if not filtered.empty:
        # Display the selected chart type
        display_chart(chart_type, filtered, material)

        # Show filtered data table for selected material
        st.subheader(f"Raw Data for {material}")
        table_df = filtered.reset_index(drop=True).copy()

        # Remove material column since it's redundant (already filtered by material)
        if "Material" in table_df.columns:
            table_df = table_df.drop("Material", axis=1)

        if "Date" in table_df.columns and not table_df.empty:
            # Ensure Date column is datetime before formatting
            if not pd.api.types.is_datetime64_any_dtype(table_df["Date"]):
                table_df["Date"] = pd.to_datetime(table_df["Date"], errors="coerce")
            table_df["Date"] = table_df["Date"].dt.strftime("%m/%d/%Y")
        st.dataframe(table_df, use_container_width=True, hide_index=True)
    else:
        st.info("No data available for the selected material and date range.")
