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
    page_icon=":bar_chart:",
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
        # Tri par stock du plus grand au plus petit et filtre pour n'afficher que les lignes avec des quantités disponibles
        combined_data = combined_data[combined_data["Avail. Qty"] > 0].sort_values(by="Avail. Qty", ascending=False)
        
        # Configurer les filtres
        filters = {}
        columns_for_filters = ['Brand', 'Category', 'Size/Format', 'Keyboard', 'Condition']
        for col in columns_for_filters:
            filters[col] = st.multiselect(f"Filter by {col}", options=list(combined_data[col].unique()))
        
        # Appliquer les filtres au DataFrame
        for key, value in filters.items():
            if value:
                combined_data = combined_data[combined_data[key].isin(value)]

        # Supprimer les colonnes indésirables
        columns_to_remove = ["Kunde land", "Brand"]  # Ajoutez d'autres noms de colonnes à supprimer si nécessaire
        combined_data = combined_data.drop(columns=columns_to_remove, errors='ignore')

        # Affichage des trois monnaies et suppression du filtre de devise
        currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
        columns_to_display = [col for col in combined_data.columns if col not in currency_columns] + currency_columns
        st.dataframe(combined_data[columns_to_display], height=700)  # Vous pouvez ajuster la hauteur selon vos besoins

# ... (reste du code pour admin_page et main inchangé)

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
            combined_data = get_combined_data()['data']
            if combined_data is not None:
                combined_data = pd.concat([combined_data, df])
            else:
                combined_data = df
            st.write(combined_data)
            get_combined_data()['data'] = combined_data
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
