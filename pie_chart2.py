
import streamlit as st
import pandas as pd
from datetime import datetime
import re  # For regular expression matching
import matplotlib.pyplot as plt

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
    query = query.replace(" ", ".*")  # Replace spaces with .*
    query = query.replace("*", ".*")  # Replace * with .*
    pattern = re.compile(query, re.IGNORECASE)

    # Filter data using the regex pattern
    return df[df['Description'].str.contains(pattern) | df['No.'].astype(str).str.contains(pattern)]

def display_pie_chart(data, column_name):
    data_to_plot = data[column_name].value_counts()
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie(data_to_plot, labels=data_to_plot.index, startangle=90, autopct='%1.1f%%')
    ax.axis('equal')
    st.pyplot(fig)

def display_data_page():
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    # Show last update date
    if last_update_date:
        st.write(f"Dernière mise à jour: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Search input
    search_query = st.text_input("Recherche par description ou No. (utilisez le * dans vos recherches):")
    
    # Filter data based on search query
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    # Display filters for user selection in horizontal layout
    col_item_cat, col_prod_group, col_keyboard, col_condition = st.columns(4)
    filters = {
        "Item Category Code": col_item_cat.multiselect("Produits catégories", list(combined_data["Item Category Code"].unique())),
        "Product Group Code": col_prod_group.multiselect("Format", list(combined_data["Product Group Code"].unique())),
        "Keyboard Language": col_keyboard.multiselect("Keyboard Language", list(combined_data["Keyboard Language"].unique())),
        "Condition": col_condition.multiselect("Condition", list(combined_data["Condition"].unique()))
    }
    
    # Filter data based on user selections
    for column, selected_values in filters.items():
        if selected_values:
            combined_data = combined_data[combined_data[column].isin(selected_values)]

    # Display the pie chart next to the data frame
    col_data, col_chart = st.columns([6, 1])
    with col_data:
        st.write(combined_data.reset_index(drop=True))
    with col_chart:
        display_pie_chart(combined_data, "Condition")

def admin_page():
    st.title("Administration")
    
    # Upload files
    uploaded_files = st.file_uploader("Importez les fichiers:", type=["xlsx"], accept_multiple_files=True)
    
    # Combine files and update data
    if uploaded_files:
        dataframes = [pd.read_excel(file) for file in uploaded_files]
        combined_data = pd.concat(dataframes, ignore_index=True)
        
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
