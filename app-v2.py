import streamlit as st
import pandas as pd
from datetime import datetime
import re  # For regular expression matching

# Constants for Admin Authentication
admin_username = st.secrets["general"]["ADMIN_USERNAME"]
admin_password = st.secrets["general"]["ADMIN_PASSWORD"]

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon="favicon.ico",
    layout="wide"
)

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_last_update_date():
    return {'date': None}

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def paginate_dataframe(df, page_size):
    page_num = st.session_state.get('page_num', 0)
    if 'next' in st.session_state:
        page_num += 1
    elif 'prev' in st.session_state:
        page_num -= 1
    page_num = max(page_num, 0)
    page_num = min(page_num, len(df) // page_size)
    st.session_state['page_num'] = page_num
    start_idx = page_num * page_size
    end_idx = (page_num + 1) * page_size
    return df.iloc[start_idx:end_idx]

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)  # Replace with your logo URL
    with col2:
        st.title("Your Stocklist")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    apply_filters = st.checkbox("Apply filters")

    if combined_data is not None and not combined_data.empty and apply_filters:
        # Renaming columns including making links clickable
        combined_data = combined_data.rename(columns={
            "Produktgruppekode": "Size/Format",
            "Varekategorikode": "Category",
            "Web URL": "Webshop",
            "Keyboard Language": "Keyboard",
            "Condition": "Condition"
        })
        combined_data['Webshop'] = combined_data['Webshop'].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>')

        # Excluding specific filters
        exclude_filters = ["Eksport Pris", "Lager", "Beskrivelse"]

        # Applying filters
        filters_widget_cols = st.columns(len(combined_data.columns) // 5 + 1)
        filters = {}
        for i, col in enumerate(combined_data.columns):
            if col not in ["Webshop"] + exclude_filters:  # Exclude the clickable links and specific filters from filters
                filters[col] = filters_widget_cols[i % len(filters_widget_cols)].multiselect(f"Filter by {col}", options=combined_data[col].unique())

        for col, selected_values in filters.items():
            if selected_values:
                combined_data = combined_data[combined_data[col].isin(selected_values)]
        
        # Paginating the filtered data
        page_size = 10  # Adjust the page size as needed
        paginated_data = paginate_dataframe(combined_data, page_size)

        # Displaying the paginated and filtered data
        st.write(paginated_data.to_html(escape=False), unsafe_allow_html=True)
        
        # Pagination buttons
        col1, col2, _ = st.columns([1,1,6])
        with col1:
            st.button("Previous", on_click=lambda: st.session_state.update({"prev": True}))
        with col2:
            st.button("Next", on_click=lambda: st.session_state.update({"next": True}))
    elif not apply_filters and combined_data is not None and not combined_data.empty:
        # Show the DataFrame without filters
        st.dataframe(combined_data)

# Your existing code for admin_page and main functions...

def admin_page():
    # Your existing code for admin_page
    pass

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a page:", ["Data Display", "Administration"])
    
    if page == "Data Display":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
