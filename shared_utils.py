# shared_utils.py
import pandas as pd
import streamlit as st
from datetime import date, datetime


def load_clean_data():
    df = pd.read_csv("data/Ebeam_Deposition_Powers_CLEAN.csv")
    # Ensure Date is datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    # Convert back to MM/DD/YYYY string format for display
    df["Date"] = df["Date"].dt.strftime("%m/%d/%Y")
    # Normalize Material: strip spaces, lower, then title case
    df["Material"] = df["Material"].astype(str).str.strip().str.lower().str.title()
    # Remove rows with invalid or blank material names
    df = df[df["Material"].notna() & (df["Material"].str.strip() != "")]
    # Drop Crystal Monitor column
    df = df.drop("Crystal_Monitor", axis=1, errors="ignore")
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
