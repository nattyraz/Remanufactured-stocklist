
import streamlit as st
import pandas as pd
from datetime import datetime
import re  # For regular expression matching

# Constants for Admin Authentication
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "foxway2023"

def check_credentials(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon="favicon.ico",
    layout="wide"
)

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_last_update_date():
    return {'date': None}

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def get_compatible_docks(model, dock_df):
    compatible_docks = []
    row = dock_df[dock_df['Model'] == model]
    if not row.empty:
        for col in dock_df.columns:
            if pd.notna(row[col].values[0]) and col != 'Model':
                compatible_docks.append(col)
    return compatible_docks

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Remanufactured stocklist Lenovo Garantie Original")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)
    
    # Display compatible docks based on model
    model_input = st.text_input("Enter a model to check compatible docks:")
    if model_input:
        try:
            # Load the dock.csv file from the "data" directory
            dock_df = pd.read_csv("/mnt/data/dock.csv", delimiter=";")
            docks = get_compatible_docks(model_input, dock_df)
            if docks:
                st.write("Compatible docks for model", model_input, "are:")
                for dock in docks:
                    st.write(dock)
            else:
                st.write("No compatible docks found for model", model_input)
        except FileNotFoundError:
            st.warning("dock.csv file not found. Please make sure it is available.")
    
    # Rest of the display_data_page function remains unchanged

# Rest of the code remains unchanged (admin_page, main, etc.)
