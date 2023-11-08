import streamlit as st
import pandas as pd
import os
import glob
import re
from datetime import datetime

# Set page configurations to use the wide layout
st.set_page_config(page_title="foxway Stocklist", page_icon="favicon.ico", layout="wide")

def paginated_df_display(dataframe, rows_per_page=30):
    num_pages = len(dataframe) // rows_per_page + (1 if len(dataframe) % rows_per_page > 0 else 0)
    page_num = st.selectbox('Select page number:', range(num_pages))
    start_idx = page_num * rows_per_page
    end_idx = (page_num + 1) * rows_per_page
    st.dataframe(dataframe.iloc[start_idx:end_idx], use_container_width=True)

def get_latest_stock_file(folder_path):
    file_pattern = os.path.join(folder_path, 'Foxway Item Stock Data Idea DCCAS_ROFO *.xlsx')
    matching_files = glob.glob(file_pattern)
    latest_file = None
    latest_time = None
    for f in matching_files:
        try:
            date_str = f.split(' ')[-1].split('.xlsx')[0]
            date_time_obj = datetime.strptime(date_str, "%Y-%m-%dT%H_%M_%S")
            if latest_file is None or date_time_obj > latest_time:
                latest_file = f
                latest_time = date_time_obj
        except ValueError:
            continue
    return latest_file

def load_stock_data(file_path):
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

def display_data_page(df, latest_file_date):
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.image("logo_foxway.png", width=100)  # Replace with your local path to the logo if necessary
    with col2:
        st.title("Foxway stocklist")
    with col3:
        st.write(latest_file_date.strftime("%B %d, %Y"))

    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    if search_query:
        df = advanced_filter_data_by_search_query(df, search_query)

    df = df[(df['Avail. Qty'] > 0) & 
            (df['Promo Price EUR'] > 0) & 
            (df['Promo Price DKK'] > 0) & 
            (df['Promo Price GBP'] > 0)]
    df = df.sort_values("Avail. Qty", ascending=False)

    if df is not None and not df.empty:
        rename_columns = {
            "Brand": "Brand",
            "Item Category Code": "Category",
            "Product Group Code": "Size/Format",
            "Condition": "Condition",
            "Keyboard Language": "Keyboard",
            "Software Language": "OS",
        }
        df = df.rename(columns=rename_columns)

        columns_to_remove = ["Kunde land"]
        df = df.drop(columns=columns_to_remove, errors='ignore')

        if "Kunde land" in df.columns:
           st.error("The column 'Kunde land' is still present.")
        else:
           st.success("The column 'Kunde land' has been successfully removed.")
        
        paginated_df_display(df, rows_per_page=25)

def main():
    if 'filter_state' not in st.session_state:
        st.session_state['filter_state'] = {}

    data_folder = 'data/'  # Update this path based on access from your Streamlit app
    latest_stock_file = get_latest_stock_file(data_folder)

    if latest_stock_file:
        try:
            latest_file_date = datetime.strptime(latest_stock_file.split('/')[-1].split(' ')[-1].split('.xlsx')[0], "%Y-%m-%dT%H_%M_%S")
        except Exception as e:
            latest_file_date = datetime.now()
            st.error(f"Error extracting date from file name: {e}")

        stock_data = load_stock_data(latest_stock_file)

        if stock_data is not None:
            display_data_page(stock_data, latest_file_date)
        else:
            st.error("No stock data file found.")
    else:
        st.error("Could not find the latest stock file.")

# Run the main function
if __name__ == "__main__":
    main()

