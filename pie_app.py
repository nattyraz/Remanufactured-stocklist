import streamlit as st
import pandas as pd
from datetime import datetime
import re  # For regular expression matching

# Constants for Admin Authentication
admin_username = st.secrets["general"]["ADMIN_USERNAME"]
admin_password = st.secrets["general"]["ADMIN_PASSWORD"]

def check_credentials(username, password):
    return username == admin_username and password == admin_password

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

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Foxway stocklist")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
        # Sorted by stock quantity in descending order and filtered for available quantities
        combined_data.sort_values(by="Avail. Qty", ascending=False, inplace=True)

        # Filtering interface wide across the page under search query, using the same columns layout as your original code
        col_brand, col_category, col_size_format, col_keyboard, col_condition = st.columns(5)
        
        if "Brand" in combined_data.columns:
            brand_filter = col_brand.multiselect("Brand", options=sorted(combined_data["Brand"].unique()))
            if brand_filter:
                combined_data = combined_data[combined_data["Brand"].isin(brand_filter)]
        if "Item Category Code" in combined_data.columns:
            category_filter = col_category.multiselect("Category", options=sorted(combined_data["Item Category Code"].unique()))
            if category_filter:
                combined_data = combined_data[combined_data["Item Category Code"].isin(category_filter)]
        if "Product Group Code" in combined_data.columns:
            size_format_filter = col_size_format.multiselect("Size/Format", options=sorted(combined_data["Product Group Code"].unique()))
            if size_format_filter:
                combined_data = combined_data[combined_data["Product Group Code"].isin(size_format_filter)]
        if "Keyboard Language" in combined_data.columns:
            keyboard_filter = col_keyboard.multiselect("Keyboard", options=sorted(combined_data["Keyboard Language"].unique()))
            if keyboard_filter:
                combined_data = combined_data[combined_data["Keyboard Language"].isin(keyboard_filter)]
        if "Condition" in combined_data.columns:
            condition_filter = col_condition.multiselect("Condition", options=sorted(combined_data["Condition"].unique()))
            if condition_filter:
                combined_data = combined_data[combined_data["Condition"].isin(condition_filter)]

        # Remove unwanted columns before displaying dataframe
        columns_to_remove = ["Kunde land", "Brand"]
        combined_data = combined_data.drop(columns=columns_to_remove, errors='ignore')

        # Display DataFrame, keeping the currency columns and formatting them properly
        currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
        combined_data = combined_data[combined_data["Avail. Qty"] > 0]  # Filter out zero quantities
        
        # Show DataFrame with specified columns and format currency values
        st.dataframe(combined_data.style.format({col: "€{:,.2f}" for col in currency_columns}),
                     height=800, width=1200)

def admin_page():
    st.sidebar.title("Administration")
    username = st.sidebar.text_input("Username", type="default")
    password = st.sidebar.text_input("Password", type="password")

    if check_credentials(username, password):
        st.success("Authentication successful.")

        # Logic for file upload and processing
        file = st.file_uploader("Upload a file:", type="xlsx")
        if file is not None:
            df = pd.read_excel(file)
            combined_data = get_combined_data().get('data')
            if combined_data is not None:
                combined_data = pd.concat([combined_data, df])
            else:
                combined_data = df
            
            get_combined_data()['data'] = combined_data
            get_last_update_date()['date'] = datetime.now()
            st.write("Preview of combined data:")
            st.dataframe(combined_data)
    else:
        st.sidebar.error("Invalid credentials.")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a page:", ["Data View", "Admin"])

    if page == "Data View":
        display_data_page()
    elif page == "Admin":
        admin_page()

if __name__ == "__main__":
    main()
