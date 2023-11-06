
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

# Attempt to close the sidebar by default using JavaScript
hide_streamlit_style = '''
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stSidebar {visibility: hidden;}
            </style>
            <script>
            document.addEventListener("DOMContentLoaded", function(event) { 
                document.querySelector('.css-1d391kg').click();
            });
            </script>
            '''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
        st.image("logo_foxway.png", width=100)
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
        # Sort the dataframe by 'Avail. Qty' in descending order
        combined_data = combined_data.sort_values(by="Avail. Qty", ascending=False)

        # Rename columns
        rename_columns = {
            "Brand": "Brand",
            "Item Category Code": "Category",
            "Product Group Code": "Size/Format",
            "Condition": "Condition",
            "Keyboard Language": "Keyboard"
        }
        combined_data = combined_data.rename(columns=rename_columns)

        col_brand, col_category, col_size_format, col_keyboard, col_condition = st.columns(5)

        # Display filters for the columns if they exist
        # ... (rest of filter setup remains unchanged)

        # Display all currency columns and apply formatting
        currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
        currency_format = {currency: "${:,.2f}".format for currency in currency_columns}
        s = combined_data.style.format(currency_format)
        
        # Increase the default number of displayed rows by adjusting the height
        st.dataframe(s, height=500)  # Adjust the height if necessary to display more rows

# ... (rest of the code remains unchanged)

def admin_page():
    # ... (unchanged code for the admin page)

# ... (rest of the main function and '__main__' block remains unchanged)
