import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

# Variables globales
LOGIN = "admin"
PASSWORD = "admin"  # Changez cette valeur par votre propre mot de passe
user_online_timestamp = datetime.now() - timedelta(days=1)
user_email = None

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_last_update_date():
    return {'date': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_user_count():
    return {'count': 0}

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def is_user_online():
    global user_online_timestamp
    return (datetime.now() - user_online_timestamp).seconds < 300

def display_data_page():
    global user_online_timestamp, user_email
    user_online_timestamp = datetime.now()
    get_user_count()['count'] += 1

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

    # ... [Reste du code pour afficher les données, sans modifications]

    email_input = st.text_input("Entrez votre e-mail pour recevoir des mises à jour:")
    if email_input:
        user_email = email_input
        st.success("E-mail enregistré avec succès!")

def admin_page():
    global user_email

    # Authentification pour l'accès à la page d'administration
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.title("Authentification")
        entered_login = st.text_input("Login:")
        entered_password = st.text_input("Password:", type="password")
        if st.button("Se connecter"):
            if entered_login == LOGIN and entered_password == PASSWORD:
                st.session_state.logged_in = True
                st.success("Connexion réussie!")
                st.experimental_rerun()
            else:
                st.error("Login ou mot de passe incorrect!")
                return

    st.title("Administration")
    
    # Affichage du nombre d'utilisateurs
    st.write(f"Nombre d'utilisateurs actuellement en ligne : {get_user_count()['count']}")

    # Importation des fichiers (accessible seulement par l'admin)
    file1 = st.file_uploader("Importez le premier fichier:", type=["xlsx"])
    # ... [Reste du code pour les autres importations et la gestion des données]

    if is_user_online():
        st.warning("Un utilisateur est actuellement en ligne!")
    if user_email:
        st.info(f"L'utilisateur avec l'e-mail {user_email} souhaite recevoir des mises à jour.")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choisissez une page:", ["Affichage des données", "Administration"])

    if page == "Affichage des données":
        display_data_page()
    elif page == "Administration":
        admin_page()

if __name__ == "__main__":
    main()
