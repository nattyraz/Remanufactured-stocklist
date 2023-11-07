import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Constants for Admin Authentication
admin_username = st.secrets["general"]["ADMIN_USERNAME"]
admin_password = st.secrets["general"]["ADMIN_PASSWORD"]

def check_credentials(username, password):
    return username == admin_username and password == admin_password

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
    st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    st.title("Foxway stocklist")

    combined_data = get_combined_data().get('data')

    search_query = st.text_input("Search by description or No. (use the * in your searches):")

    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
        combined_data.sort_values(by="Avail. Qty", ascending=False, inplace=True)
        
        filters = {}
        if "Brand" in combined_data.columns:
            filters["Brand"] = st.multiselect("Brand", list(combined_data["Brand"].unique()))
        if "Item Category Code" in combined_data.columns:
            filters["Category"] = st.multiselect("Category", list(combined_data["Item Category Code"].unique()))
        if "Product Group Code" in combined_data.columns:
            filters["Size/Format"] = st.multiselect("Size/Format", list(combined_data["Product Group Code"].unique()))
        if "Keyboard Language" in combined_data.columns:
            filters["Keyboard"] = st.multiselect("Keyboard", list(combined_data["Keyboard Language"].unique()))
        if "Condition" in combined_data.columns:
            filters["Condition"] = st.multiselect("Condition", list(combined_data["Condition"].unique()))
        if "Software Language" in combined_data.columns:
            filters["Software"] = st.multiselect("Software", list(combined_data["Software Language"].unique()))

        for key, value in filters.items():
            if value:
                combined_data = combined_data[combined_data[key].isin(value)]

        columns_to_display = [
            "Item Category Code", "Product Group Code", "Software Language",
            "Keyboard Language", "Graphics01", "Graphics02", "Condition",
            "Warranty", "Avail. Qty", "Promo Price EUR", "Promo Price DKK", 
            "Promo Price GBP"
        ]
        st.dataframe(combined_data[columns_to_display], height=600)

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
