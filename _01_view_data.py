# view_data.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.app_utils import load_clean_data, MATERIAL_DICT


def view_data_page():
    df = load_clean_data()

    # Sidebar: material selector (only valid, normalized names)
    materials = sorted(MATERIAL_DICT.keys())
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
    st.dataframe(table_df, use_container_width=True, hide_index=True)
