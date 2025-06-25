import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re


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


df = load_clean_data()

# Sidebar: material selector (only valid, normalized names)
materials = sorted(df["Material"].unique())
material = st.sidebar.selectbox("Select material", materials)

# Filter data using normalized material
filtered = df[df["Material"] == material].sort_values("Date")

st.title(f"Deposition Data for {material}")

fig, ax1 = plt.subplots(figsize=(8, 4))

# Plot Deposition Power and Threshold Power on Y-axis, Date on X-axis
ax1.plot(
    filtered["Date"], filtered["Power_Deposition"], label="Deposition Power", marker="o"
)
ax1.plot(
    filtered["Date"], filtered["Threshold_Power"], label="Threshold Power", marker="o"
)

ax1.set_xlabel("Date")
ax1.set_ylabel("Power")
ax1.legend(loc="upper left")

st.pyplot(fig)

# Show filtered data table for selected material
st.subheader(f"Raw Data for {material}")
st.dataframe(filtered.reset_index(drop=True))
