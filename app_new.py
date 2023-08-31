import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Constants for Admin Authentication
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "foxway2023"

def check_credentials(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

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

def decode_description(description):
    abbreviations = {
        "FHD": "Full HD",
        "B": "Bluetooth",
        "C": "Camera",
        "WI": "Wifi",
        "NOOS": "No Operating System",
        "N": "NFT",
        "MB": "Multy Burner",
        "w10P": "Windows 10 Pro",
        "W11P": "Windows 11 pro",
        "W10": "Windows 10 Home",
        "W11": "Windows 11 Home",
        "GC": "Graphic Card",
        "4": "4G inclus",
        "4U": "4G upgrable"
        # Ajoutez d'autres abréviations si nécessaire
    }
    
   # Ignorer la première partie de la description
    description_end = description.split("/", 1)[-1]
    
    details = []
    for abbr, full in abbreviations.items():
        if abbr in description_end:
            details.append(full)
    return ", ".join(details)


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

    if combined_data is not None and not combined_data.empty:
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
        
        filters = {}
        if "Brand" in combined_data.columns:
            filters["Brand"] = col_brand.multiselect("Brand", list(combined_data["Brand"].unique()))
        if "Category" in combined_data.columns:
            filters["Category"] = col_category.multiselect("Category", list(combined_data["Category"].unique()))
        if "Size/Format" in combined_data.columns:
            filters["Size/Format"] = col_size_format.multiselect("Size/Format", list(combined_data["Size/Format"].unique()))
        if "Keyboard" in combined_data.columns:
            filters["Keyboard"] = col_keyboard.multiselect("Keyboard", list(combined_data["Keyboard"].unique()))
        if "Condition" in combined_data.columns:
            filters["Condition"] = col_condition.multiselect("Condition", list(combined_data["Condition"].unique()))
        
        for column, selected_values in filters.items():
            if selected_values:
                combined_data = combined_data[combined_data[column].isin(selected_values)]
        
        currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
        selected_currency = st.selectbox("Select a currency:", currency_columns)
        
        filtered_data = combined_data[
            (combined_data[selected_currency].notna()) & 
            (combined_data[selected_currency] != 0) &
            (combined_data["Avail. Qty"] > 0)
        ]
        
        # Remove unwanted columns
        columns_to_remove = ["Kunde land", "Brand"]
        filtered_data = filtered_data.drop(columns=columns_to_remove, errors='ignore')
        
        columns_to_display = [col for col in filtered_data.columns if col not in currency_columns]
        columns_to_display.append(selected_currency)
        s = filtered_data[columns_to_display].style.format({selected_currency: lambda x : "{:.2f}".format(x)})
        st.dataframe(s)

        ref_selected = st.selectbox("Sélectionnez une référence pour plus de détails:", combined_data['No.'].unique())
        if ref_selected:
            description = combined_data[combined_data['No.'] == ref_selected]['Description'].iloc[0]
            decoded_description = decode_description(description)
            st.write(f"Description détaillée pour la référence {ref_selected}: {decoded_description}")

def admin_page():
    st.sidebar.title("Administration")
    username = st.sidebar.text_input("Nom d'utilisateur", type="default")
    password = st.sidebar.text_input("Mot de passe", type="password")
    
    if not check_credentials(username, password):
        st.sidebar.warning("Identifiants incorrects. Veuillez réessayer.")
        return

    file1 = st.file_uploader("Importez le premier fichier:", type=["xlsx"])
    file2 = st.file_uploader("Importez le deuxième fichier:", type=["xlsx"])
    file3 = st.file_uploader("Importez le troisième fichier (optionnel):", type=["xlsx"])
    file4 = st.file_uploader("Importez le quatrième fichier (optionnel):", type=["xlsx"])
    
    files = [file for file in [file1, file2, file3, file4] if file]
    
    if files:
        dataframes = [pd.read_excel(file) for file in files]
        combined_data = pd.concat(dataframes)
        last_update_date = datetime.now()
        st.success("The data has been updated successfully!")
        st.write("Prévisualisation des données combinées :")
        st.write(combined_data)
        get_combined_data()['data'] = combined_data
        get_last_update_date()['date'] = last_update_date

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choisissez une page:", ["Affichage des données", "Administration"])
    
    if page == "Affichage des données":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()