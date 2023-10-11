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

# Function to categorize the 'Condition' column and create a 'Sub-Condition' for further filtering
def filter_condition(df):
    df['Sub-Condition'] = df['Condition']
    
    conditions = {
        'neuf': ['01 New'],
        'refurb': ['08 Ref.', '02 Bulk', '04 Demo', 'Demo', 'Grade B', 'Grade A', 'Grade C', 'Defekt'],
        'remanufactured': ['SILVER', 'BRONZE', 'GOLD'],
        'premium': ['Premium']
    }
    
    for category, condition_values in conditions.items():
        df.loc[df['Condition'].isin(condition_values), 'Condition'] = category
    
    return df

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_last_update_date():
    return {'date': None}

def display_data_page():
    col1, col2 = st.columns([1, 6])
    
    with col1:
        st.image("logo_url", width=100)
        
    with col2:
        st.title("New, Demo & Remanufactured stocklist Lenovo Garantie Original")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    # Assume advanced_filter_data_by_search_query is a function you've defined to filter data
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
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

        # Added this for the new filter
        col_sub_condition = st.columns(1)
        filters["Sub-Condition"] = col_sub_condition[0].multiselect("Sub-Condition", list(combined_data['Sub-Condition'].unique()))
        
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
        
        columns_to_remove = ["Kunde land", "Brand"]
        filtered_data = filtered_data.drop(columns=columns_to_remove, errors='ignore')
        
        columns_to_display = [col for col in filtered_data.columns if col not in currency_columns]
        columns_to_display.append(selected_currency)
        
        s = filtered_data[columns_to_display].style.format({selected_currency: lambda x : "{:.2f}".format(x)})
        st.dataframe(s)

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
        
        st.success("Les données ont été mises à jour avec succès!")
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
