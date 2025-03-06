import streamlit as st
import pandas as pd
from datetime import datetime
import re
from openai import OpenAI
import requests
import json
import pdfplumber
import os

# Constants for Admin Authentication
admin_username = st.secrets["general"]["ADMIN_USERNAME"]
admin_password = st.secrets["general"]["ADMIN_PASSWORD"]

# Configuration d'OpenRouter
client = OpenAI(
    api_key=st.secrets["openrouter"]["API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# Chemin pour stocker les données persistantes
DATA_FILE = "combined_data.parquet"  # Format Parquet pour efficacité
META_FILE = "meta.json"  # Pour stocker la date de mise à jour

def check_credentials(username, password):
    return username == admin_username and password == admin_password

# Charger les données persistantes
def load_persistent_data():
    if os.path.exists(DATA_FILE):
        return pd.read_parquet(DATA_FILE)
    return None

def load_last_update_date():
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            meta = json.load(f)
            return datetime.fromisoformat(meta["last_update_date"])
    return None

# Sauvegarder les données persistantes
def save_persistent_data(df, last_update_date):
    df.to_parquet(DATA_FILE)
    with open(META_FILE, "w") as f:
        json.dump({"last_update_date": last_update_date.isoformat()}, f)

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon="favicon.ico",
    layout="wide"
)

# Initialisation des données au démarrage
if 'combined_data' not in st.session_state:
    st.session_state.combined_data = load_persistent_data()
if 'last_update_date' not in st.session_state:
    st.session_state.last_update_date = load_last_update_date()
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ ]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

def search_serpapi(query):
    params = {
        "q": f"site:psref.lenovo.com {query} filetype:pdf",
        "api_key": st.secrets["serpapi"]["API_KEY"],
        "num": 5
    }
    url = "https://serpapi.com/search"
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else {"error": f"Erreur {response.status_code}"}

def extract_pdf_text(pdf_url):
    try:
        response = requests.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        with open("temp.pdf", "wb") as f:
            f.write(response.content)
        with pdfplumber.open("temp.pdf") as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)
        return text
    except Exception as e:
        return f"Erreur lors de l'extraction du PDF : {e}"

def get_llm_response(prompt):
    response = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        title_col, stats_col = st.columns([2, 1])
        with title_col:
            st.title("Foxway stocklist")
        with stats_col:
            combined_data = st.session_state.combined_data
            total_refs = len(combined_data) if combined_data is not None and not combined_data.empty else 0
            st.write(f"Total références : {total_refs}")
            filtered_placeholder = st.empty()

    last_update_date = st.session_state.last_update_date
    if last_update_date:
        st.write(f"Dernière mise à jour : {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")

    combined_data = st.session_state.combined_data
    if combined_data is None or combined_data.empty:
        st.warning("Aucune donnée disponible. Veuillez attendre une mise à jour de l'administrateur.")
        return

    search_query = st.text_input("Rechercher par description ou No. (utilisez * dans vos recherches) :")
    if search_query:
        combined_data = advanced_filter_data_by_search_query(combined_data, search_query)

    # Filtres et affichage (inchangé sauf adaptations mineures)
    rename_columns = {
        "Brand": "Brand",
        "Item Category Code": "Category",
        "Product Group Code": "Size/Format",
        "Condition": "Condition",
        "Keyboard Language": "Keyboard"
    }
    combined_data = combined_data.rename(columns=rename_columns)

    col_brand, col_category, col_size_format, col_keyboard, col_condition = st.columns(5)
    filters = {
        "Brand": col_brand.multiselect("Brand", list(combined_data["Brand"].unique())),
        "Category": col_category.multiselect("Category", list(combined_data["Category"].unique())),
        "Size/Format": col_size_format.multiselect("Size/Format", list(combined_data["Size/Format"].unique())),
        "Keyboard": col_keyboard.multiselect("Keyboard", list(combined_data["Keyboard"].unique())),
        "Condition": col_condition.multiselect("Condition", list(combined_data["Condition"].unique()))
    }

    filtered_data = combined_data.copy()
    for column, selected_values in filters.items():
        if selected_values:
            filtered_data = filtered_data[filtered_data[column].isin(selected_values)]

    currency_columns = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
    selected_currency = st.selectbox("Sélectionnez une devise :", currency_columns)
    filtered_data = filtered_data[
        (filtered_data[selected_currency].notna()) &
        (filtered_data[selected_currency] != 0) &
        (filtered_data["Avail. Qty"] > 0)
    ]

    filtered_refs = len(filtered_data)
    with stats_col:
        filtered_placeholder.write(f"Références filtrées : {filtered_refs}")

    columns_to_remove = ["Kunde land", "Brand"]
    filtered_data = filtered_data.drop(columns=columns_to_remove, errors='ignore')
    columns_to_display = [col for col in filtered_data.columns if col not in currency_columns]
    columns_to_display.append(selected_currency)
    s = filtered_data[columns_to_display].style.format({selected_currency: "{:.2f}"})
    st.dataframe(s)

    # Section Lenovo PSREF (inchangée, pas pertinente pour les corrections demandées)
    st.subheader("Recherche intelligente Lenovo PSREF (avec PDF)")
    psref_query = st.text_input("Entre une référence Lenovo (ex: 'ThinkPad X1 Carbon' ou 'ThinkPad X1 Carbon avec 16 Go') :")
    search_mode = st.radio("Mode de recherche :", ["Focus sur le détail", "Général"], horizontal=True)
    if psref_query:
        search_results = search_serpapi(psref_query)
        if "error" not in search_results:
            organic_results = search_results.get("organic_results", [])
            pdf_links = [result["link"] for result in organic_results if result["link"].endswith(".pdf")]
            if pdf_links:
                pdf_url = pdf_links[0]
                st.write(f"PDF trouvé : {pdf_url}")
                pdf_text = extract_pdf_text(pdf_url)
                st.write("Extrait du PDF :", pdf_text[:500] + "...")
            else:
                st.write("Aucun PDF trouvé. Résultats bruts :", "\n".join([f"{r['title']}: {r.get('snippet', '')}" for r in organic_results]))
                pdf_text = "Aucun contenu PDF disponible."
        else:
            st.write("Erreur lors de la recherche :", search_results["error"])
            pdf_text = "Aucune donnée récupérée."

        llm_prompt = f"..."  # (Prompt inchangé, raccourci ici pour lisibilité)
        llm_response = get_llm_response(llm_prompt).strip()
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
    st.sidebar.title("Authentification Admin")
    username = st.sidebar.text_input("Nom d'utilisateur", type="default")
    password = st.sidebar.text_input("Mot de passe", type="password")
    login_button = st.sidebar.button("Connexion")

    if login_button:
        if check_credentials(username, password):
            st.session_state.is_admin = True
            st.sidebar.success("Connexion réussie !")
        else:
            st.sidebar.warning("Identifiants incorrects.")

    if not st.session_state.is_admin:
        st.warning("Veuillez vous connecter en tant qu'administrateur.")
        return

    st.title("Administration")
    file1 = st.file_uploader("Importez le fichier de stock :", type=["xlsx"])
    if file1:
        data = pd.read_excel(file1)
        last_update_date = datetime.now()
        save_persistent_data(data, last_update_date)
        st.session_state.combined_data = data
        st.session_state.last_update_date = last_update_date
        st.success(f"Données mises à jour avec succès le {last_update_date.strftime('%Y-%m-%d %H:%M:%S')} !")
        st.write("Prévisualisation des données :")
        st.write(data)

def main():
    st.sidebar.title("Navigation")
    if st.session_state.is_admin:
        page = st.sidebar.radio("Choisissez une page :", ["Affichage des données", "Administration"])
    else:
        page = "Affichage des données"
        st.sidebar.write("Affichage des données uniquement (connexion admin requise pour modifier).")

    if page == "Affichage des données":
        display_data_page()
    elif page == "Administration" and st.session_state.is_admin:
        admin_page()

if __name__ == "__main__":
    main()
