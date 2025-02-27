import streamlit as st
import pandas as pd
from datetime import datetime
import re  # For regular expression matching
from openai import OpenAI
import requests
import json
import pdfplumber

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
        "q": f"site:psref.lenovo.com {query} filetype:pdf",
        "api_key": st.secrets["serpapi"]["API_KEY"],
        "num": 5  # Limite à 5 résultats
    }
    url = "https://serpapi.com/search"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Erreur {response.status_code}"}

# Fonction pour extraire le texte d'un PDF
def extract_pdf_text(pdf_url):
    try:
        response = requests.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        with pdfplumber.open("temp.pdf") as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Erreur lors de l'extraction du PDF : {e}"

# Fonction pour interagir avec le LLM OpenRouter
def get_llm_response(prompt):
    response = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500  # Pour gérer des PDFs longs
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

    # Section Recherche Lenovo PSREF avec lecture de PDF
    st.subheader("Recherche intelligente Lenovo PSREF (avec PDF)")
    psref_query = st.text_input("Entre une référence Lenovo (ex: 'ThinkPad X1 Carbon' ou 'ThinkPad X1 Carbon avec 16 Go') :")
    search_mode = st.radio("Mode de recherche :", ["Focus sur le détail", "Général"], horizontal=True)

    if psref_query:
        # Recherche avec SerpApi pour trouver un PDF
        search_results = search_serpapi(psref_query)
        if "error" not in search_results:
            organic_results = search_results.get("organic_results", [])
            pdf_links = [result["link"] for result in organic_results if result["link"].endswith(".pdf")]
            if pdf_links:
                pdf_url = pdf_links[0]  # Premier PDF trouvé
                st.write(f"PDF trouvé : {pdf_url}")
                pdf_text = extract_pdf_text(pdf_url)
                st.write("Extrait du PDF :", pdf_text[:500] + "...")  # Aperçu limité
            else:
                st.write("Aucun PDF trouvé. Résultats bruts :", "\n".join([f"{r['title']}: {r.get('snippet', '')}" for r in organic_results]))
                pdf_text = "Aucun contenu PDF disponible."
        else:
            st.write("Erreur lors de la recherche :", search_results["error"])
            pdf_text = "Aucune donnée récupérée."

        # Analyse par le LLM avec mode de recherche
        if search_mode == "Focus sur le détail" and "avec" in psref_query.lower():
            # Extraire le modèle et la spécificité
            model_part = psref_query.split("avec")[0].strip()
            spec_part = psref_query.split("avec")[1].strip()
            llm_prompt = f"""
            Voici le contenu extrait d'un PDF Lenovo PSREF pour '{psref_query}':
            {pdf_text}

            Recherche les informations spécifiques au modèle '{model_part}' avec un focus sur la spécificité '{spec_part}' (ex. mémoire, disque).
            Retourne un tableau structuré **au format JSON uniquement** avec les colonnes suivantes pour ce modèle :
            - "Modèle" : Nom exact du produit (doit correspondre à '{model_part}' ou être proche)
            - "Mémoire" : Quantité et type de mémoire (ex: "16 Go DDR4")
            - "Mémoire Modifiable" : "Oui" ou "Non" (si la mémoire peut être mise à jour)
            - "Disque" : Taille et type de stockage (ex: "512 Go SSD")
            - "Disque Modifiable" : "Oui" ou "Non" (si le disque peut être remplacé)
            - "Options Modifiables" : Liste des autres options modifiables (ex: "Batterie, Wi-Fi")
            - "Lien PSREF" : URL du PDF (utilise '{pdf_url}' si disponible)

            Mets un accent particulier sur '{spec_part}' dans les résultats. Si l'information est manquante, mets "Non spécifié". Si le modèle ou la spécificité n'est pas trouvé, retourne une liste vide [].
            """
        else:
            # Recherche générale
            llm_prompt = f"""
            Voici le contenu extrait d'un PDF Lenovo PSREF pour '{psref_query}':
            {pdf_text}

            Recherche les informations spécifiques au modèle '{psref_query}' dans ce texte.
            Retourne un tableau structuré **au format JSON uniquement** avec les colonnes suivantes pour ce modèle :
            - "Modèle" : Nom exact du produit (doit correspondre à '{psref_query}' ou être proche)
            - "Mémoire" : Quantité et type de mémoire (ex: "16 Go DDR4")
            - "Mémoire Modifiable" : "Oui" ou "Non" (si la mémoire peut être mise à jour)
            - "Disque" : Taille et type de stockage (ex: "512 Go SSD")
            - "Disque Modifiable" : "Oui" ou "Non" (si le disque peut être remplacé)
            - "Options Modifiables" : Liste des autres options modifiables (ex: "Batterie, Wi-Fi")
            - "Lien PSREF" : URL du PDF (utilise '{pdf_url}' si disponible)

            Si une information est manquante, mets "Non spécifié". Si le modèle n'est pas trouvé, retourne une liste vide [].
            """

        llm_response = get_llm_response(llm_prompt).strip()
        
        # Convertir la réponse JSON en DataFrame
        try:
            results_json = json.loads(llm_response)
            if isinstance(results_json, list) and results_json:
                df_results = pd.DataFrame(results_json)
                st.subheader(f"Résultats formatés pour '{psref_query}' ({search_mode})")
                st.dataframe(df_results)
                st.write("Liens PSREF (cliquez pour ouvrir) :")
                for index, row in df_results.iterrows():
                    st.link_button(f"Lien pour {row['Modèle']}", row["Lien PSREF"])
            else:
                st.write(f"Aucune donnée trouvée pour '{psref_query}' dans le PDF ({search_mode}). Réponse brute :", llm_response)
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
