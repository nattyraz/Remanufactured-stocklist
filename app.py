import streamlit as st
import pandas as pd
from datetime import datetime

# Use caching to store and retrieve the combined data
@st.cache(allow_output_mutation=True)
def get_combined_data():
    return None

@st.cache(allow_output_mutation=True)
def get_last_update_date():
    return None

def display_data_page():
    combined_data = get_combined_data()
    last_update_date = get_last_update_date()
    
    st.title("Affichage des données")
    
    # Show last update date
    if last_update_date:
        st.write(f"Dernière mise à jour: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display data
    if combined_data is not None:
        # List of currency columns
        currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
        
        # Allow user to select a currency
        selected_currency = st.selectbox("Sélectionnez une devise:", currency_columns)
        
        # Display data with selected currency column
        columns_to_display = [col for col in combined_data.columns if col not in currency_columns]
        columns_to_display.append(selected_currency)
        st.write(combined_data[columns_to_display])

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
        get_combined_data.cache_clear()
        get_combined_data.cache_on_next_run = False
        get_last_update_date.cache_clear()
        get_last_update_date.cache_on_next_run = False
        
        get_combined_data(combined_data)
        get_last_update_date(last_update_date)

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choisissez une page:", ["Affichage des données", "Administration"])
    
    if page == "Affichage des données":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
