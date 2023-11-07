import streamlit as st
import pandas as pd
import os
import glob
import re  # For regular expression matching

# Set page configurations
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon=":bar_chart:",
    layout="wide"
)

def get_latest_stock_file(folder_path):
    # Construct the pattern to match files with the desired format
    file_pattern = os.path.join(folder_path, 'Foxway Item Stock Data Idea DCCAS_ROFO *.xlsx')
    # Find all files matching the pattern
    matching_files = glob.glob(file_pattern)
    # Get the latest file based on the file naming convention
    latest_file = None
    latest_time = None
    date_fmt = '%Y-%m-%dT%H_%M_%S'
    for filename in matching_files:
        # Extract the date and time from the filename
        timestamp_str = filename.split('DCCAS_ROFO ')[-1].rstrip('.xlsx')
        timestamp = datetime.strptime(timestamp_str, date_fmt)
        if not latest_time or timestamp > latest_time:
            latest_time = timestamp
            latest_file = filename
    return latest_file

def load_stock_data(file_path):
    # Load the data from the file
    if file_path and os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        return None

# Include the definitions for advanced_filter_data_by_search_query and display_data_page.
# ...

def main():
    # If you're using Streamlit sharing or Streamlit for Teams, you might need to adjust the path to where your files are stored.
    data_folder = '/main/data'  # Absolute path to the data folder
    latest_stock_file = get_latest_stock_file(data_folder)

    # Load the stock data from the latest file available
    stock_data = load_stock_data(latest_stock_file)

    if stock_data is not None:
        # Display the stock data using the display_data_page function
        display_data_page(stock_data)
    else:
        st.error("No stock data file found for today.")

# The display_data_page function should now accept a DataFrame as an argument.
# ...

if __name__ == "__main__":
    main()
