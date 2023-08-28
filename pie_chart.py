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

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_last_update_date():
    return {'date': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_user_ips():
    return []

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_online_users():
    return set()

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def display_data_page():
    user_ip = st.session_state.get("user_ip", "unknown")
    online_users = get_online_users()
    online_users.add(user_ip)

    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Remanufactured stocklist Lenovo Garantie Original")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
        # ... [rest of the code as is]

ddef admin_page():
    st.title("Administration")

    # Admin authentication
    password = st.sidebar.text_input("Enter admin password:", type='password')
    if password != "secret_password":  # Replace "secret_password" with your own password
        st.error("Access denied. Invalid password!")
        return
    
    # Display online users
    online_users = get_online_users()
    st.write(f"Users currently online: {len(online_users)}")

    # ... [rest of the code as is]

def main():
    # Check and record user IP
    user_ip = st.request.headers.get("client-ip", "unknown")
    st.session_state.user_ip = user_ip
    user_ips = get_user_ips()
    if user_ip not in user_ips:
        user_ips.append(user_ip)

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choisissez une page:", ["Affichage des données", "Administration"])
    
    if page == "Affichage des données":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
