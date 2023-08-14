
import streamlit as st
import pandas as pd

# Path to the initial Excel file
FILE_PATH = "template price list.xlsx"

# Cache the initial loading of the Excel file to improve performance
@st.cache
def load_data():
    return pd.read_excel(FILE_PATH)

# Function to display the DataFrame in Streamlit
def display_data(df):
    st.write(df)

# Main application
def main():
    st.title("Gestionnaire de liste de prix")
    
    # Display the data
    df = load_data()
    display_data(df)
    
    # Allow user to upload a new file to update the data
    uploaded_file = st.file_uploader("Importez un nouveau fichier de stock pour mettre à jour:", type=["xlsx"])
    if uploaded_file is not None:
        df_new = pd.read_excel(uploaded_file)
        display_data(df_new)
        st.success("Les données ont été mises à jour avec succès!")

if __name__ == "__main__":
    main()
