import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import date, datetime

# Remove or comment out the wide layout
# st.set_page_config(layout="wide")


# --- Data Cleaning Script ---
def clean_and_save_csv():
    df = pd.read_csv("data/Ebeam Deposition Powers - Metal Evap User Run Data.csv")
    # Standardize column names
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(r"[\s:()%]", "_", regex=True)
    df.columns = df.columns.str.replace(r"_+", "_", regex=True)
    df.columns = df.columns.str.strip("_")

    # Replace all forms of N/A with np.nan
    df = df.replace({r"(?i)^(n/a|na|\?|crystal failed|)$": np.nan}, regex=True)

    # Identify numeric columns (except Material and Date)
    non_numeric_cols = ["Material", "Date"]
    numeric_cols = [col for col in df.columns if col not in non_numeric_cols]

    # Remove units and symbols, handle ranges and multi-values
    def clean_numeric(val):
        if pd.isna(val):
            return np.nan
        val = str(val).strip()
        # Remove units (%, nm, ma, etc.)
        val = re.sub(r"[^0-9.\-]", "", val)
        # Handle ranges (e.g., 10-12)
        if "-" in val:
            parts = [float(x) for x in val.split("-") if x]
            if parts:
                return np.mean(parts)
            else:
                return np.nan
        try:
            return float(val)
        except ValueError:
            return np.nan

    for col in numeric_cols:
        df[col] = df[col].apply(clean_numeric)

    # Drop rows with any non-numeric or missing values in numeric columns
    df_clean = df.dropna(subset=numeric_cols, how="any")

    # Save cleaned CSV
    df_clean.to_csv("data/Ebeam_Deposition_Powers_CLEAN.csv", index=False)


# Run cleaning script (uncomment to run as a script)
# clean_and_save_csv()


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


# --- Multipage App ---
page = st.sidebar.radio("Choose a page", ["View Data", "Add Entry"])

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
        threshold_power = st.number_input("Threshold Power", min_value=0.0, step=0.01)
        deposition_power = st.number_input("Deposition Power", min_value=0.0, step=0.01)
        rate = st.number_input("Rate", min_value=0.0, step=0.01)
        thickness = st.number_input("Thickness (nm)", min_value=0.0, step=0.01)
        crystal_monitor = st.number_input("Crystal Monitor", min_value=0.0, step=0.01)
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
