import streamlit as st
import pandas as pd
from datetime import datetime
import re  # For regular expression matching

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon="favicon.ico",
    layout="wide"
)

# Use caching to store and retrieve the combined data
@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_last_update_date():
    return {'date': None}

def advanced_filter_data_by_search_query(df, query):
    # Transform the user's query to a more flexible regex pattern
    pattern = re.compile(re.escape(query).replace(r'\*', '.*').replace(r'\?', '.'), re.IGNORECASE)
    
    # Filter data using the regex pattern
    return df[df['Description'].str.contains(pattern) | df['No.'].astype(str).str.contains(pattern)]

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Remanufactured stocklist Lenovo Garantie Original")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    # Show last update date
    if last_update_date:
        st.write(f"Dernière mise à jour: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Search input
    search_query = st.text_input("Recherche par description ou No.:")
    
    # Filter data based on search query
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
        # Display filters for user selection in horizontal layout
        col_item_cat, col_prod_group, col_keyboard, col_condition = st.columns(4)
        filters = {
            "Item Category Code": col_item_cat.multiselect("Item Category Code", list(combined_data["Item Category Code"].unique())),
            "Product Group Code": col_prod_group.multiselect("Product Group Code", list(combined_data["Product Group Code"].unique())),
            "Keyboard Language": col_keyboard.multiselect("Keyboard Language", list(combined_data["Keyboard Language"].unique())),
            "Condition": col_condition.multiselect("Condition", list(combined_data["Condition"].unique()))
        }
        
        # Filter data based on user selections
        for column, selected_values in filters.items():
            if selected_values:
                combined_data = combined_data[combined_data[column].isin(selected_values)]
        
        # List of currency columns
        currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
        
        # Allow user to select a currency
        selected_currency = st.selectbox("Sélectionnez une devise:", currency_columns)
        
        # Filter rows with no price or zero price for the selected currency and "Avail. Qty" greater than 0
        filtered_data = combined_data[
            (combined_data[selected_currency].notna()) & 
            (combined_data[selected_currency] != 0) &
            (combined_data["Avail. Qty"] > 0)
        ]
        
        # Remove unwanted columns
        columns_to_remove = ["kunde land", "brand"]
        filtered_data = filtered_data.drop(columns=columns_to_remove, errors='ignore')
        
        # Display data with selected currency column, without the default index column
        columns_to_display = [col for col in filtered_data.columns if col not in currency_columns]
        columns_to_display.append(selected_currency)
        st.write(filtered_data[columns_to_display].reset_index(drop=True))

def admin_page():
    st.title("Administration")
    
    # Upload files
    file1 = st.file_uploader("Importez le premier fichier:", type=["xlsx"])
    file2 = st.file_uploader("Importez le deuxième fichier:", type=["xlsx"])
    
    # Combine files and update data
    if file1 and file2:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)
        
        # Combine the files
        combined_data = pd.concat([df1, df2])
        
        # Update last update date
        last_update_date = datetime.now()
        st.success("Les données ont été mises à jour avec succès!")
        
        # Preview the combined data
        st.write("Prévisualisation des données combinées :")
        st.write(combined_data)

        # Store the updated data and date using caching
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

