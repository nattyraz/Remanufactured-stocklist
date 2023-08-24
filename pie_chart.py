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
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:  # Check if the sub-query is not empty
            sub_query = sub_query.replace("*", ".*")  # Convert * to .* for regex
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

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
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Search input
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    

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
        selected_currency = st.selectbox("Select a currency:", currency_columns)
        
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
        s = filtered_data[columns_to_display].style.format({selected_currency: lambda x : "{:.2f}".format(x)})
        
# Assuming combined_data is your dataframe

# 1. Add a multiselect box for users to select references from "No." column
selected_references = st.multiselect('Select references from "No." column:', combined_data['No.'].unique())

# 2. Add a button to initiate download
if st.button('Download selected references'):
    # 3. Generate a file with selected references and provide a link for download
    with open('selected_references.txt', 'w') as f:
        for ref in selected_references:
            f.write(f"{ref}\n")
    st.download_button(label="Download", data=f, file_name='selected_references.txt', mime='text/plain')
st.dataframe(s)

def admin_page():
    st.title("Administration")
    
    # Upload files
    file1 = st.file_uploader("Importez le premier fichier:", type=["xlsx"])
    file2 = st.file_uploader("Importez le deuxième fichier:", type=["xlsx"])
    file3 = st.file_uploader("Importez le troisième fichier (optionnel):", type=["xlsx"])
    file4 = st.file_uploader("Importez le quatrième fichier (optionnel):", type=["xlsx"])
    
    files = [file for file in [file1, file2, file3, file4] if file]  # List of uploaded files
    
    if files:
        dataframes = [pd.read_excel(file) for file in files]  # Convert files to DataFrames
        
        # Combine the files
        combined_data = pd.concat(dataframes)
        
        # Update last update date
        last_update_date = datetime.now()
        st.success("The data has been updated successfully!")
        
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

if __name__ == "__main__":
    main()
