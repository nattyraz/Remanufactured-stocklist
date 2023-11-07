import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Constants for Admin Authentication
admin_username = st.secrets["general"]["ADMIN_USERNAME"]
admin_password = st.secrets["general"]["ADMIN_PASSWORD"]

def check_credentials(username, password):
    return username == admin_username and password == admin_password

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon=":bar_chart:",
    layout="wide"
)

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Foxway stocklist")
    
    combined_data = get_combined_data()['data']
    
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)
    
    if combined_data is not None and not combined_data.empty:
        combined_data = combined_data[combined_data["Avail. Qty"] > 0].sort_values(by="Avail. Qty", ascending=False)

        # Add filters back into the code
        filters = {}
        
        if "Brand" in combined_data.columns:
            filters["Brand"] = st.sidebar.multiselect("Brand", list(combined_data["Brand"].unique()))
        if "Category" in combined_data.columns:
            filters["Category"] = st.sidebar.multiselect("Category", list(combined_data["Category"].unique()))
        if "Size/Format" in combined_data.columns:
            filters["Size/Format"] = st.sidebar.multiselect("Size/Format", list(combined_data["Size/Format"].unique()))
        if "Keyboard" in combined_data.columns:
            filters["Keyboard"] = st.sidebar.multiselect("Keyboard", list(combined_data["Keyboard"].unique()))
        if "Condition" in combined_data.columns:
            filters["Condition"] = st.sidebar.multiselect("Condition", list(combined_data["Condition"].unique()))
        
        # Apply filters to the dataframe
        for column, selected_values in filters.items():
            if selected_values:
                combined_data = combined_data[combined_data[column].isin(selected_values)]

        # Displaying all currency columns
        currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
        
        # Define columns to display. Ensure these column names match your dataframe's column names
        columns_to_display = [col for col in combined_data.columns if col not in currency_columns] + currency_columns
        
        # Increase the max rows to display in the dataframe
        st.dataframe(combined_data[columns_to_display], height=600)  # You can adjust the height as needed

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choisissez une page:", ["Affichage des données", "Administration"])

    if page == "Affichage des données":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()


