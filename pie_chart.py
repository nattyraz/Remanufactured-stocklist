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

def get_compatible_dock(reference, dock_df):
    """
    Get the compatible dock from the dock dataframe based on the reference.
    
    Parameters:
    - reference (str): The reference to search for.
    - dock_df (pd.DataFrame): The dock dataframe.
    
    Returns:
    - str: The compatible dock if found, None otherwise.
    """
    match = dock_df[dock_df['A'] == reference]
    if not match.empty:
        return match.iloc[0]['Compatible Dock']
    return None

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Refufurb stocklist")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
        col_item_cat, col_prod_group, col_keyboard, col_condition = st.columns(4)
        filters = {
            "Item Category Code": col_item_cat.multiselect("Item Category Code", list(combined_data["Item Category Code"].unique())),
            "Product Group Code": col_prod_group.multiselect("Product Group Code", list(combined_data["Product Group Code"].unique())),
            "Keyboard Language": col_keyboard.multiselect("Keyboard Language", list(combined_data["Keyboard Language"].unique())),
            "Condition": col_condition.multiselect("Condition", list(combined_data["Condition"].unique()))
        }
        
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
        columns_to_remove = ["Kunde land"]
        filtered_data = filtered_data.drop(columns=columns_to_remove, errors='ignore')
        
        columns_to_display = [col for col in filtered_data.columns if col not in currency_columns]
        columns_to_display.append(selected_currency)
        s = filtered_data[columns_to_display].style.format({selected_currency: lambda x : "{:.2f}".format(x)})
        st.dataframe(s)

def admin_page():
    st.title("Administration")

    username = st.text_input("Nom d'utilisateur", type="default")
    password = st.text_input("Mot de passe", type="password")
    
    if not check_credentials(username, password):
        st.warning("Identifiants incorrects. Veuillez réessayer.")
        return

    file1 = st.file_uploader("Importez le premier fichier:", type=["xlsx"])
    file2 = st.file_uploader("Importez le deuxième fichier:", type=["xlsx"])
    file3 = st.file_uploader("Importez le troisième fichier (optionnel):", type=["xlsx"])
    file4 = st.file_uploader("Importez le quatrième fichier (optionnel):", type=["xlsx"])
    
    files = [file for file in [file1, file2, file3, file4] if file]
    
    if files:
        dataframes = [pd.read_excel(file) for file in files]
        combined_data = pd.concat(dataframes)
        
        try:
            # Load the dock.csv file from the "data" directory
            dock_df = pd.read_csv("data/dock.csv")
            
            # Get compatible dock for each reference in combined_data
            
if 'Reference' in combined_data.columns:
    combined_data['Compatible Dock'] = combined_data['Reference'].apply(lambda x: get_compatible_dock(x, dock_df))
else:
    st.warning("'Reference' column not found in the imported files.")
    
        except FileNotFoundError:
            st.warning("dock.csv file not found in the 'data' directory. Compatible Dock information won't be added.")
        
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
