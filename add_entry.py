# add_entry.py
import streamlit as st
from datetime import date
from shared_utils import load_clean_data, append_row_to_csv


def add_entry_page():
    st.title("Add New Deposition Entry")

    df = load_clean_data()

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
