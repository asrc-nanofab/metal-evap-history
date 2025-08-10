# app.py
import streamlit as st

from _01_view_data import view_data_page
from _02_add_entry import add_entry_page
from _03_user_data import user_data_page
from _04_staff_only import staff_only_page

# Page configuration
st.set_page_config(page_title="Metal Evaporation History")

# Page mapping - define once, use everywhere
PAGES = {
    "View Data": view_data_page,
    "Add Entry": add_entry_page,
    "User Data": user_data_page,
    "⚠️ STAFF ONLY ⚠️": staff_only_page,
}

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", list(PAGES.keys()))

# Route to appropriate page
PAGES[page]()
