import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Constants for Admin Authentication
admin_username = st.secrets["general"]["ADMIN_USERNAME"]
admin_password = st.secrets["general"]["ADMIN_PASSWORD"]

def check_credentials(username, password):
    return username == admin_username and password == admin_password

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
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Stocklist Dashboard")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")

    if combined_data is None or combined_data.empty:
        st.warning("Aucune donnée chargée. Veuillez télécharger des données via la page d'administration.")
        return

    search_query = st.text_input("Search by description or No. (use the * in your searches):")
    
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    # Display filters for specific columns
    if combined_data is not None and not combined_data.empty:
        filters = {}
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filters['Varekategorikode'] = st.multiselect('Varekategorikode:', options=pd.unique(combined_data['Varekategorikode']), default=pd.unique(combined_data['Varekategorikode']))
        with col2:
            filters['Produktgruppekode'] = st.multiselect('Produktgruppekode:', options=pd.unique(combined_data['Produktgruppekode']), default=pd.unique(combined_data['Produktgruppekode']))
        with col3:
            filters['Keyboard Sprog'] = st.multiselect('Keyboard Sprog:', options=pd.unique(combined_data['Keyboard Sprog']), default=pd.unique(combined_data['Keyboard Sprog']))
        with col4:
            filters['Condition'] = st.multiselect('Condition:', options=pd.unique(combined_data['Condition']), default=pd.unique(combined_data['Condition']))
        
        for column, selected_options in filters.items():
            if selected_options:
                combined_data = combined_data[combined_data[column].isin(selected_options)]
        
    paginated_data = paginate_dataframe(combined_data, 10)
    st.write(paginated_data.to_html(escape=False), unsafe_allow_html=True)

def process_admin_file_upload():
    uploaded_file = st.file_uploader("Téléchargez le fichier de stock:", type=["xlsx"])
    if uploaded_file is not None:
        try:
            dataframe = pd.read_excel(uploaded_file)
            get_combined_data()['data'] = dataframe
            get_last_update_date()['date'] = datetime.now()
            st.success("Le fichier de stock a été téléchargé et traité avec succès.")
            st.write("Aperçu des données chargées :")
            st.dataframe(dataframe)
        except Exception as e:
            st.error(f"Une erreur s'est produite lors du traitement du fichier : {e}")

def admin_page():
    st.sidebar.title("Administration")
    username = st.sidebar.text_input("Nom d'utilisateur", key="username")
    password = st.sidebar.text_input("Mot de passe", type="password", key="password")
    
    if st.sidebar.button("Connexion"):
        if check_credentials(username, password):
            st.session_state['admin_logged_in'] = True
            process_admin_file_upload()
        else:
            st.sidebar.error("Identifiants incorrects. Veuillez réessayer.")
            st.session_state['admin_logged_in'] = False

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a page:", ["Data Display", "Administration"])
    
    if page == "Data Display":
        display_data_page()
    elif page == "Administration":
        admin_page()

if __name__ == "__main__":
    main()
