import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon="favicon.ico",
    layout="wide"
)

# Load the tab-separated data directly (replace this with your document content)
data = """
No.	Description	Item Category Code	Product Group Code	Software Language	Keyboard Language	Graphics01	Graphics02	Condition	Warranty	Avail. Qty	Promo Price EUR	Promo Price DKK	Promo Price GBP	Brand
10US0005FR-CTO2-S	AIO V530-22ICB i3-8100T/4GB/1TB/FHD/MB/B/C/NOOS	PC	ALL-IN-ONE		FR	Intel(R) UHD Graphics 630		SILVER	1YR CCR	1	241	1794	200	LENOVO DESKTOP
11CD004NUK-S	M90a i5-10500/8GB/256M2/FHD/MB/B/C(IR)/W10P	PC	ALL-IN-ONE	GB	GB	Intel UHD Graphics 630 Shared Video Memory (UMA)		SILVER	1YR CCR	1	616	4590	511	THINKCENTRE
# ... (rest of your data here, truncated for brevity)
"""

@st.cache_data
def get_combined_data():
    # Convert the tab-separated string to a DataFrame
    from io import StringIO
    df = pd.read_csv(StringIO(data), sep='\t')
    return {'data': df}

@st.cache_data
def get_last_update_date():
    return {'date': datetime.now()}  # Simulate an update date

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Foxway Stocklist")

    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']

    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")

    search_query = st.text_input("Search by description or No. (use * in your searches):")

    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
        # Rename columns
        rename_columns = {
            "Brand": "Brand",
            "Item Category Code": "Category",
            "Product Group Code": "Size/Format",
            "Condition": "Condition",
            "Keyboard Language": "Keyboard"
        }
        combined_data = combined_data.rename(columns=rename_columns)

        col_brand, col_category, col_size_format, col_keyboard, col_condition = st.columns(5)

        filters = {}
        if "Brand" in combined_data.columns:
            filters["Brand"] = col_brand.multiselect("Brand", list(combined_data["Brand"].unique()))
        if "Category" in combined_data.columns:
            filters["Category"] = col_category.multiselect("Category", list(combined_data["Category"].unique()))
        if "Size/Format" in combined_data.columns:
            filters["Size/Format"] = col_size_format.multiselect("Size/Format", list(combined_data["Size/Format"].unique()))
        if "Keyboard" in combined_data.columns:
            filters["Keyboard"] = col_keyboard.multiselect("Keyboard", list(combined_data["Keyboard"].unique()))
        if "Condition" in combined_data.columns:
            filters["Condition"] = col_condition.multiselect("Condition", list(combined_data["Condition"].unique()))

        for column, selected_values in filters.items():
            if selected_values:
                combined_data = combined_data[combined_data[column].isin(selected_values)]

        currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
        selected_currency = st.selectbox("Select a currency:", currency_columns)

        filtered_data = combined_data[
            (combined_data[selected_currency].notna()) &
            (combined_data[selected_currency] != 0) &
            (combined_data["Avail. Qty"] > 0)
        ]

        # Remove unwanted columns
        columns_to_remove = ["Kunde land", "Brand"]
        filtered_data = filtered_data.drop(columns=columns_to_remove, errors='ignore')

        columns_to_display = [col for col in filtered_data.columns if col not in currency_columns]
        columns_to_display.append(selected_currency)
        s = filtered_data[columns_to_display].style.format({selected_currency: "{:.2f}"})
        st.dataframe(s)

def main():
    display_data_page()  # Directly show the data page for now

if __name__ == "__main__":
    main()
