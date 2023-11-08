import streamlit as st
import pandas as pd
import os
import glob
import re
from datetime import datetime

# Define a function for paginated display of the dataframe
def paginated_df_display(dataframe, rows_per_page=30):
    # Calcul du nombre total de pages
    num_pages = len(dataframe) // rows_per_page + (1 if len(dataframe) % rows_per_page > 0 else 0)
    
    # Ajout d'une boîte de sélection pour choisir le numéro de page
    page_num = st.selectbox('Select page number:', range(num_pages))
    
    # Calcul des indices de début et de fin de la page actuelle
    start_idx = page_num * rows_per_page
    end_idx = (page_num + 1) * rows_per_page
    
    # Affichage du sous-ensemble du DataFrame correspondant à la page actuelle
    st.dataframe(dataframe.iloc[start_idx:end_idx])

def display_data_page(df, latest_file_date):
    # ... votre code existant pour configurer l'interface utilisateur ...

    # Juste avant d'afficher le DataFrame avec st.dataframe(df),
    # remplacez cette ligne par un appel à la fonction paginated_df_display :
    if df is not None and not df.empty:
        # ... votre code existant pour le filtrage ...

        # Affichage paginé du DataFrame
        paginated_df_display(df, rows_per_page=25)  # Ici, on passe le DataFrame et le nombre de lignes par page.

# Set page configurations
st.set_page_config(page_title="foxway Stocklist", page_icon="favicon.ico", layout="wide")

def get_latest_stock_file(folder_path):
    file_pattern = os.path.join(folder_path, 'Foxway Item Stock Data Idea DCCAS_ROFO *.xlsx')
    matching_files = glob.glob(file_pattern)
    latest_file = None
    latest_time = None

    # Match files based on the pattern 'Foxway Item Stock Data Idea DCCAS_ROFO YYYY-MM-DDTHH_MM_SS.xlsx'
    for f in matching_files:
        try:
            # Extract the datetime string and convert it to a datetime object
            date_str = f.split(' ')[-1].split('.xlsx')[0]
            date_time_obj = datetime.strptime(date_str, "%Y-%m-%dT%H_%M_%S")
            if latest_file is None or date_time_obj > latest_time:
                latest_file = f
                latest_time = date_time_obj
        except ValueError as e:
            # Skip files that don't match the expected pattern
            continue

    return latest_file

def load_stock_data(file_path):
    if file_path and os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        return None

# Include the definitions for advanced_filter_data_by_search_query and display_data_page.
def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def display_data_page(df, latest_file_date):
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Foxway stocklist")
    with col3:
        st.write(latest_file_date.strftime("%B %d, %Y"))  # Format the date as you like

    def display_data_page(df, latest_file_date):
        # ... your existing code ...

        # When you're ready to display the DataFrame:
        if df is not None and not df.empty:
            # ... your existing filtering code ...

            # Display the DataFrame, setting a height that can accommodate at least 25 rows
            # Note: The actual number of rows displayed can vary based on row height and available screen size
            st.dataframe(df, height=1000)  # Adjust the height as needed to show at least 25 rows


    # Search functionality
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    if search_query:
        df = advanced_filter_data_by_search_query(df, search_query)

    # Filter out rows where 'Avail. Qty' is zero or any of the 'Promo Price' columns are zero
    df = df[(df['Avail. Qty'] > 0) & 
            (df['Promo Price EUR'] > 0) & 
            (df['Promo Price DKK'] > 0) & 
            (df['Promo Price GBP'] > 0)]
    df = df.sort_values("Avail. Qty", ascending=False)

    # If there is data to display
    if df is not None and not df.empty:
        # Rename columns for user-friendliness if needed
        rename_columns = {
            "Brand": "Brand",
            "Item Category Code": "Category",
            "Product Group Code": "Size/Format",
            "Condition": "Condition",
            "Keyboard Language": "Keyboard",
            "Software Language": "OS",
            
        }
        df = df.rename(columns=rename_columns)
        # If there is data to display
    if df is not None and not df.empty:
        # Remove unwanted columns
        columns_to_remove = ["Kunde land"]  # Specify the columns you want to remove
        df = df.drop(columns=columns_to_remove, errors='ignore')  # Use errors='ignore' to avoid errors if the column does not exist

        # Create filter columns
        col_brand, col_category, col_size_format, col_keyboard, col_condition = st.columns(5)

        # Retrieve filter states from session state
        filters = st.session_state['filter_state']

        # Function to get safe defaults (only those present in current options)
        def get_safe_defaults(column_name, options):
            if column_name in filters:
                return [default for default in filters[column_name] if default in options]
            return []

        # Create multiselect filters for each column with safe defaults
        with col_brand:
            brand_options = list(df["Brand"].unique())
            filters["Brand"] = st.multiselect("Brand", options=brand_options, default=get_safe_defaults("Brand", brand_options))
        with col_category:
            category_options = list(df["Category"].unique())
            filters["Category"] = st.multiselect("Category", options=category_options, default=get_safe_defaults("Category", category_options))
        with col_size_format:
            size_format_options = list(df["Size/Format"].unique())
            filters["Size/Format"] = st.multiselect("Size/Format", options=size_format_options, default=get_safe_defaults("Size/Format", size_format_options))
        with col_keyboard:
            keyboard_options = list(df["Keyboard"].unique())
            filters["Keyboard"] = st.multiselect("Keyboard", options=keyboard_options, default=get_safe_defaults("Keyboard", keyboard_options))
        with col_condition:
            condition_options = list(df["Condition"].unique())
            filters["Condition"] = st.multiselect("Condition", options=condition_options, default=get_safe_defaults("Condition", condition_options))

        # Update the session state
        st.session_state['filter_state'] = filters

        # Apply the filters to the dataframe
        for column, selected_values in filters.items():
            if selected_values:
                df = df[df[column].isin(selected_values)]

        if "Kunde land" in df.columns:
           st.error("The column 'Kunde land' is still present.")
        else:
           st.success("The column 'Kunde land' has been successfully removed.")

        
        # Display the filtered dataframe
        st.dataframe(df)


def main():
    # Initialize session state for filters if it doesn't exist
    if 'filter_state' not in st.session_state:
        st.session_state['filter_state'] = {}

    data_folder = 'data/'  # Update this path based on access from your Streamlit app
    latest_stock_file = get_latest_stock_file(data_folder)

    if latest_stock_file:
        try:
            # Assuming the file name format is '... YYYY-MM-DDTHH_MM_SS.xlsx'
            latest_file_date = datetime.strptime(latest_stock_file.split('/')[-1].split(' ')[-1].split('.xlsx')[0], "%Y-%m-%dT%H_%M_%S")
        except Exception as e:
            latest_file_date = datetime.now()  # Default to current time if date extraction fails
            st.error(f"Error extracting date from file name: {e}")

        stock_data = load_stock_data(latest_stock_file)

        if stock_data is not None:
            # Pass the extracted date to the display function
            display_data_page(stock_data, latest_file_date)
        else:
            st.error("No stock data file found.")
    else:
        st.error("Could not find the latest stock file.")

if __name__ == "__main__":
    main()
