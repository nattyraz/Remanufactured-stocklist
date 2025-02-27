import streamlit as st
import pandas as pd
from datetime import datetime
import re  # For regular expression matching
from openai import OpenAI
import requests
import json

# Constants for Admin Authentication
admin_username = st.secrets["general"]["ADMIN_USERNAME"]
admin_password = st.secrets["general"]["ADMIN_PASSWORD"]

# Configuration d'OpenRouter
client = OpenAI(
    api_key=st.secrets["openrouter"]["API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

def check_credentials(username, password):
    return username == admin_username and password == admin_password

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon="favicon.ico",
    layout="wide"
)

# Initialize session state for data and last update
if 'combined_data' not in st.session_state:
    st.session_state.combined_data = None
if 'last_update_date' not in st.session_state:
    st.session_state.last_update_date = None

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ ]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

# Fonction pour chercher avec SerpApi
def search_serpapi(query):
    params = {
        "q": f"site:psref.lenovo.com {query}",
        "api_key": st.secrets["serpapi"]["API_KEY"],
        "num": 5  # Limite à 5 résultats
    }
    url = "https://serpapi.com/search"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Erreur {response.status_code}"}

# Fonction pour interagir avec le LLM OpenRouter
def get_llm_response(prompt):
    response = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000  # Augmenté pour des réponses plus détaillées
    )
    return response.choices[0].message.content

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Foxway stocklist")

    combined_data = st.session_state.combined_data
    last_update_date = st.session_state.last_update_date

    if last_update_date:
        st.write(f"Last update: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")

    search_query = st.text_input("Search by description or No. (use the * in your searches):")

    if search_query and combined_data is not None:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    if combined_data is not None and not combined_data.empty:
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

        columns_to_remove = ["Kunde land", "Brand"]
        filtered_data = filtered_data.drop(columns=columns_to_remove, errors='ignore')

        columns_to_display = [col for col in filtered_data.columns if col not in currency_columns]
        columns_to_display.append(selected_currency)
        s = filtered_data[columns_to_display].style.format({selected_currency: lambda x: "{:.2f}".format(x)})
        st.dataframe(s)

    # Section Recherche Lenovo PSREF
    st.subheader("Recherche intelligente Lenovo PSREF")
    psref_query = st.text_input("Entre une référence Lenovo (ex: ThinkPad X1 Carbon) ou une question :")
    if psref_query:
        # Recherche avec SerpApi
        search_results = search_serpapi(psref_query)
        if "error" not in search_results:
            organic_results = search_results.get("organic_results", [])
            results_text = "\n".join([f"{result['title']}: {result.get('snippet', 'Pas de description')} (Lien: {result['link']})" for result in organic_results])
            st.write("Résultats bruts PSREF :", results_text)
        else:
            st.write("Erreur lors de la recherche :", search_results["error"])
            results_text = "Aucune donnée récupérée."

        # Analyse par le LLM avec formatage en JSON
        llm_prompt = f"""
        Voici les résultats d'une recherche sur Lenovo PSREF pour '{psref_query}':
        {results_text}

        Analyse ces données et retourne un tableau structuré **au format JSON uniquement** (sans texte supplémentaire autour) avec les colonnes suivantes pour chaque produit trouvé :
        - "Modèle" : Nom du produit
        - "Mémoire" : Quantité et type de mémoire (ex: "16 Go DDR4")
        - "Mémoire Modifiable" : "Oui" ou "Non" (si la mémoire peut être mise à jour)
        - "Disque" : Taille et type de stockage (ex: "512 Go SSD")
        - "Disque Modifiable" : "Oui" ou "Non" (si le disque peut être remplacé)
        - "Options Modifiables" : Liste des autres options modifiables (ex: "Batterie, Wi-Fi")
        - "Lien PSREF" : URL vers la page PSREF

        Si une information est manquante, mets "Non spécifié" ou une estimation raisonnable basée sur les données.
        """
        llm_response = get_llm_response(llm_prompt).strip()  # Nettoie les espaces ou retours à la ligne
        
        # Convertir la réponse JSON en DataFrame
        try:
            results_json = json.loads(llm_response)
            if isinstance(results_json, list) and results_json:
                df_results = pd.DataFrame(results_json)
                st.subheader("Résultats formatés")
                # Afficher le DataFrame sans unsafe_allow_html
                st.dataframe(df_results)
                # Ajouter des boutons de lien séparés
                st.write("Liens PSREF (cliquez pour ouvrir) :")
                for index, row in df_results.iterrows():
                    st.link_button(f"Lien pour {row['Modèle']}", row["Lien PSREF"])
            else:
                st.write("Le LLM n'a pas retourné de données structurées. Voici la réponse brute :", llm_response)
        except json.JSONDecodeError as e:
            st.write(f"Erreur de formatage JSON : {e}. Réponse brute :", llm_response)

def admin_page():
    st.sidebar.title("Administration")
    username = st.sidebar.text_input("Nom d'utilisateur", type="default")
    password = st.sidebar.text_input("Mot de passe", type="password")

    if not check_credentials(username, password):
        st.sidebar.warning("Identifiants incorrects. Veuillez réessayer.")
        return

    file1 = st.file_uploader("Importez le premier fichier:", type=["xlsx"])
    files = [file for file in [file1] if file]

    if files:
        dataframes = [pd.read_excel(file) for file in files]
        combined_data = pd.concat(dataframes)
        last_update_date = datetime.now()
        st.success("The data has been updated successfully!")
        st.write("Prévisualisation des données combinées :")
        st.write(combined_data)
        # Store in session state
        st.session_state.combined_data = combined_data
        st.session_state.last_update_date = last_update_date

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choisissez une page:", ["Affichage des données", "Administration"])

    if page == "Affichage des données":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
