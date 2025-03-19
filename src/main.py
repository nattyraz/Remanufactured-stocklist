import streamlit as st
from src.config import APP_CONFIG
from src.ui.pages import Pages
from src.utils.auth import AuthManager
from src.data.data_manager import DataManager

def initialize_app():
    """Initialise l'application et ses états."""
    # Configuration de la page
    st.set_page_config(
        page_title=APP_CONFIG["page_title"],
        page_icon=APP_CONFIG["page_icon"],
        layout=APP_CONFIG["layout"]
    )

    # Initialisation de l'authentification
    AuthManager.initialize_session()

    # Chargement des données initiales
    if 'combined_data' not in st.session_state:
        st.session_state.combined_data = DataManager.load_persistent_data()
    if 'last_update_date' not in st.session_state:
        st.session_state.last_update_date = DataManager.load_last_update_date()

def main():
    """Point d'entrée principal de l'application."""
    initialize_app()

    # Barre latérale de navigation
    st.sidebar.title("Navigation")

    # Gestion de l'authentification
    is_admin, login_status = AuthManager.render_login_ui()

    # Affichage des messages de connexion
    if login_status["attempted"]:
        if login_status["success"]:
            st.sidebar.success(login_status["message"])
        else:
            st.sidebar.warning(login_status["message"])

    # Sélection de la page
    if is_admin:
        page = st.sidebar.radio(
            "Choisissez une page :",
            ["Affichage des données", "Administration"]
        )
    else:
        page = "Affichage des données"
        st.sidebar.write(
            "Affichage des données uniquement "
            "(connexion admin requise pour modifier)."
        )

    # Affichage de la page sélectionnée
    if page == "Affichage des données":
        Pages.display_data_page()
    elif page == "Administration" and is_admin:
        Pages.admin_page()

if __name__ == "__main__":
    main()