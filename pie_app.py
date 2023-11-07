import streamlit as st
import pandas as pd
import os
import glob
import re
from datetime import datetime

# Set page configurations
st.set_page_config(page_title="Remanufactured Stocklist", page_icon=":bar_chart:", layout="wide")

def get_latest_stock_file(folder_path):
    file_pattern = os.path.join(folder_path, 'Foxway Item Stock Data Idea DCCAS_ROFO *.xlsx')
    matching_files = glob.glob(file_pattern)
    latest_file = max(matching_files, key=os.path.getctime, default=None)
    return latest_file

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

def display_data_page(df):
    st.title("Foxway stocklist")

    # Filtering Logic (Retained from previous version)
    # Description search box
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    if search_query:
        df = advanced_filter_data_by_search_query(df, search_query)

    # Checkboxes for 'Brand', 'Category', 'Size/Format', 'Keyboard', 'Condition'
    filter_columns = {
        "Brand": "Brand",
        "Category": "Item Category Code",
        "Size/Format": "Product Group Code",
        "Keyboard": "Keyboard Language",
        "Condition": "Condition",
    }
    filters = {col: [] for col in filter_columns.keys()}
    
    for name, col in filter_columns.items():
        if col in df.columns:
            filters[name] = st.multiselect(f"Filter by {name}:", options=df[col].unique(), default=df[col].unique())
    
    # Apply checklist filters
    for col, selected_options in filters.items():
        if selected_options:
            df = df[df[filter_columns[col]].isin(selected_options)]
    
    # Show quantities greater than 0 and sort by 'Avail. Qty'
    df = df[df["Avail. Qty"] > 0]
    df = df.sort_values("Avail. Qty", ascending=False)

    # Display the DataFrame
    st.dataframe(df)

def main():
    # The path to the data folder should be the absolute or relative path to the folder
    # where the Streamlit app has access to your stock data files
    data_folder = '/main/data'  # Update this path based on access from your Streamlit app
    latest_stock_file = get_latest_stock_file(data_folder)

    # Load the stock data from the latest file available
    stock_data = load_stock_data(latest_stock_file)

    if stock_data is not None:
        # Display the stock data using the display_data_page function
        display_data_page(stock_data)
    else:
        st.error("No stock data file found for today.")

# The advanced_filter_data_by_search_query and display_data_page functions should be here.

if __name__ == "__main__":
    main()
