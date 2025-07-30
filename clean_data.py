import pandas as pd
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
