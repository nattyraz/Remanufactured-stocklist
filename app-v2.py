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
        st.title("Company Stocklist")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
        # Rename columns including 'Web URL' to 'Webshop'
        rename_columns = {
            "Keyboard Language": "Keyboard",
            "Condition": "Condition",
            "Product Group Code": "Size/Format",
            "Item Category Code": "Category",
            "Web URL": "Webshop"
        }
        combined_data = combined_data.rename(columns=rename_columns)

        col_keyboard, col_condition, col_size_format, col_category = st.columns(4)
        
        filters = {}
        if "Keyboard" in combined_data.columns:
            filters["Keyboard"] = col_keyboard.multiselect("Keyboard", combined_data["Keyboard"].unique())
        if "Condition" in combined_data.columns:
            filters["Condition"] = col_condition.multiselect("Condition", combined_data["Condition"].unique())
        if "Size/Format" in combined_data.columns:
            filters["Size/Format"] = col_size_format.multiselect("Size/Format", combined_data["Size/Format"].unique())
        if "Category" in combined_data.columns:
            filters["Category"] = col_category.multiselect("Category", combined_data["Category"].unique())

        for column, selected_values in filters.items():
            if selected_values:
                combined_data = combined_data[combined_data[column].isin(selected_values)]
        
        # Displaying the DataFrame with clickable 'Webshop' links
        combined_data['Webshop'] = combined_data['Webshop'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
        st.write(combined_data.to_html(escape=False, index=False), unsafe_allow_html=True)

def admin_page():
    st.sidebar.title("Administration")
    username = st.sidebar.text_input("Username", type="default")
    password = st.sidebar.text_input("Password", type="password")
    
    if not check_credentials(username, password):
        st.sidebar.warning("Incorrect credentials. Please try again.")
        return

    file1 = st.file_uploader("Upload file:", type=["xlsx"])
    
    if file1:
        combined_data = pd.read_excel(file1)
        last_update_date = datetime.now()
        st.success("Data has been updated successfully!")
        st.write("Preview of combined data:")
        st.write(combined_data)
        get_combined_data()['data'] = combined_data
        get_last_update_date()['date'] = last_update_date

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a page:", ["Data Display", "Administration"])
    
    if page == "Data Display":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
