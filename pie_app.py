import streamlit as st
import pandas as pd
import os
import glob
import re  # For regular expression matching
from datetime import datetime

# Set page configurations
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon=":bar_chart:",
    layout="wide"
)

def get_latest_stock_file(folder_path):
    # Construct the pattern to match files with the date format 'stocklist_YYYY-MM-DD.xlsx'
    file_pattern = os.path.join(folder_path, 'stocklist_*.xlsx')
    # Find all files matching the pattern
    matching_files = glob.glob(file_pattern)
    # Get the latest file based on the file naming convention
    latest_file = max(matching_files, key=os.path.getctime, default=None)
    return latest_file

def load_stock_data(file_path):
    # Load the data from the file
    if file_path and os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        return None

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def display_data_page(stock_data):
    st.title("Foxway stocklist")

    # Allow users to search the data
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    if search_query:
        stock_data = advanced_filter_data_by_search_query(stock_data, search_query)

    if stock_data is not None and not stock_data.empty:
        # Example rename columns
        rename_columns = {
            "Brand": "Brand",
            "Item Category Code": "Category",
            "Product Group Code": "Size/Format",
            "Condition": "Condition",
            "Keyboard Language": "Keyboard",
            # Add more column rename mapping if necessary
        }
        stock_data = stock_data.rename(columns=rename_columns)

        # Assuming 'Avail. Qty' is the column to show available quantity in your DataFrame
        # and you want to sort by this column in descending order
        stock_data = stock_data.sort_values(by='Avail. Qty', ascending=False)

        # Display the DataFrame
        st.dataframe(stock_data)

def main():
    # Assuming the 'data' folder is in the current working directory of your Streamlit application
    data_folder = 'data'  # Relative path to the data folder
    latest_stock_file = get_latest_stock_file(data_folder)

    # Load the stock data from the latest file available
    stock_data = load_stock_data(latest_stock_file)

    if stock_data is not None:
        # Display the stock data using the display_data_page function
        display_data_page(stock_data)
    else:
        st.error("No stock data file found for today.")

if __name__ == "__main__":
    main()
