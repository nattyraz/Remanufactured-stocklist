import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re

# Variables globales
LOGIN = "admin"
PASSWORD = "admin"  # Changez cette valeur à votre propre mot de passe.
user_online_timestamp = datetime.now() - timedelta(days=1)
user_email = None

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

def is_user_online():
    global user_online_timestamp
    return (datetime.now() - user_online_timestamp).seconds < 300

def display_data_page():
    global user_online_timestamp, user_email
    user_online_timestamp = datetime.now()

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
        col_item_cat, col_prod_group, col_keyboard, col_condition = st.columns(4)
        filters = {
            "Item Category Code": col_item_cat.multiselect("Item Category Code", list(combined_data["Item Category Code"].unique())),
            "Product Group Code": col_prod_group.multiselect("Product Group Code", list(combined_data["Product Group Code"].unique())),
            "Keyboard Language": col_keyboard.multiselect("Keyboard Language", list(combined_data["Keyboard Language"].unique())),
            "Condition": col_condition.multiselect("Condition", list(combined_data["Condition"].unique()))
        }

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

        columns_to_remove = ["Kunde land"]
        filtered_data = filtered_data.drop(columns=columns_to_remove, errors='ignore')
        columns_to_display = [col for col in filtered_data.columns if col not in currency_columns]
        columns_to_display.append(selected_currency)
        s = filtered_data[columns_to_display].style.format({selected_currency: lambda x: "{:.2f}".format(x)})
        st.dataframe(s)

    email_input = st.text_input("Entrez votre e-mail pour recevoir des mises à jour:")
    if email_input:
        user_email = email_input
        st.success("E-mail enregistré avec succès!")

def admin_page():
    global user_email

    st.title("Administration")
    file1 = st.file_uploader("Importez le premier fichier:", type=["xlsx"])
    file2 = st.file_uploader("Importez le deuxième fichier:", type=["xlsx"])
    file3 = st.file_uploader("Importez le troisième fichier (optionnel):", type=["xlsx"])
    file4 = st.file_uploader("Importez le quatrième fichier (optionnel):", type=["xlsx"])

    files = [file for file in [file1, file2, file3, file4] if file]
    if files:
        dataframes = [pd.read_excel(file) for file in files]
        combined_data = pd.concat(dataframes)
        last_update_date = datetime.now()
        st.success("Les données ont été mises à jour avec succès!")
        st.write("Prévisualisation des données combinées :")
        st.write(combined_data)
        get_combined_data()['data'] = combined_data
        get_last_update_date()['date'] = last_update_date

    if is_user_online():
        st.warning("Un utilisateur est actuellement en ligne!")
    if user_email:
        st.info(f"L'utilisateur avec l'e-mail {user_email} souhaite recevoir des mises à jour.")

def main():
    st.sidebar.title("Navigation")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        page = st.sidebar.radio("Choisissez une page:", ["Affichage des données", "Administration"])
    else:
        page = "Authentification"

    if page == "Affichage des données":
        display_data_page()
    elif page == "Administration":
        admin_page()
    else:
        st.title("Authentification")
        entered_login = st.text_input("Login:")
        entered_password = st.text_input("Password:", type="password")
        if st.button("Se connecter"):
            if entered_login == LOGIN and entered_password == PASSWORD:
                st.session_state.logged_in = True
                st.success("Connexion réussie!")
            else:
                st.error("Login ou mot de passe incorrect!")

if __name__ == "__main__":
    main()
