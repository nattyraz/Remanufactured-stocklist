import streamlit as st

# Configuration de l'application
APP_CONFIG = {
    "page_title": "Stockliste",
    "page_icon": None,
    "layout": "wide"
}

# Fichiers de données
DATA_FILES = {
    "data": "data/combined_data.parquet",
    "meta": "data/meta.json"
}

# Configuration d'authentification
ADMIN_USERNAME = st.secrets["general_ADMIN_USERNAME"]
ADMIN_PASSWORD = st.secrets["general_ADMIN_PASSWORD"]

# Configuration API
OPENROUTER_CONFIG = {
    "api_key": st.secrets["openrouter_API_KEY"],
    "base_url": "https://openrouter.ai/api/v1",
    "model": "meta-llama/llama-3.2-11b-vision-instruct",
    "max_tokens": 1500
}

SEARCH_CONFIG = {
    "api_key": st.secrets["serpapi_API_KEY"],
    "num_results": 5
}

# Configuration des colonnes
COLUMN_MAPPING = {
    "Brand": "Brand",
    "Item Category Code": "Category",
    "Product Group Code": "Size/Format",
    "Condition": "Condition",
    "Keyboard Language": "Keyboard"
}

CURRENCY_COLUMNS = ["Promo Price EUR", "Promo Price DKK", "Promo Price GBP"]
COLUMNS_TO_REMOVE = ["Kunde land", "Brand"]