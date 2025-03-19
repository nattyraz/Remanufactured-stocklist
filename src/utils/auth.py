import streamlit as st
from typing import Tuple, Dict, Any

from src.config import ADMIN_USERNAME, ADMIN_PASSWORD

class AuthManager:
    @staticmethod
    def check_credentials(username: str, password: str) -> bool:
        """Vérifie les identifiants de connexion admin."""
        return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

    @staticmethod
    def render_login_ui() -> Tuple[bool, Dict[str, Any]]:
        """Affiche et gère l'interface de connexion."""
        login_status = {
            "success": False,
            "message": "",
            "attempted": False
        }

        st.sidebar.subheader("Authentification Admin")
        username = st.sidebar.text_input(
            "Nom d'utilisateur", 
            key="username"
        )
        password = st.sidebar.text_input(
            "Mot de passe",
            type="password",
            key="password"
        )

        if st.sidebar.button("Connexion"):
            login_status["attempted"] = True
            if AuthManager.check_credentials(username, password):
                login_status["success"] = True
                login_status["message"] = "Connexion réussie !"
                st.session_state.is_admin = True
            else:
                login_status["message"] = "Identifiants incorrects."
                st.session_state.is_admin = False

        return st.session_state.get("is_admin", False), login_status

    @staticmethod
    def initialize_session() -> None:
        """Initialise les variables de session pour l'authentification."""
        if "is_admin" not in st.session_state:
            st.session_state.is_admin = False

    @staticmethod
    def is_admin() -> bool:
        """Vérifie si l'utilisateur actuel est admin."""
        return st.session_state.get("is_admin", False)

    @staticmethod
    def requires_admin(func):
        """Décorateur pour protéger les fonctions nécessitant des droits admin."""
        def wrapper(*args, **kwargs):
            if not AuthManager.is_admin():
                st.warning("Cette fonction nécessite des droits administrateur.")
                return None
            return func(*args, **kwargs)
        return wrapper