import streamlit as st
import pandas as pd
from datetime import datetime
import io
import openpyxl
from typing import Dict, Any, Optional

from src.config import (
    COLUMN_MAPPING,
    CURRENCY_COLUMNS,
    COLUMNS_TO_REMOVE
)
from src.data.data_manager import DataManager
from src.api.api_client import APIClient
from src.utils.auth import AuthManager

class Pages:
    @staticmethod
    def display_header():
        """Affiche l'en-tête de l'application."""
        col1, col2 = st.columns([1, 6])
        with col1:
            st.image("static/rflogo.jpg", width=100)
        with col2:
            title_col, stats_col = st.columns([2, 1])
            with title_col:
                st.title("Stockliste")
            return stats_col

    @staticmethod
    def display_stats(df: Optional[pd.DataFrame], stats_col) -> Any:
        """Affiche les statistiques de données."""
        total_refs = DataManager.get_total_refs(df)
        stats_col.write(f"Total références : {total_refs}")
        return stats_col.empty()

    @staticmethod
    def display_data_page():
        """Page principale d'affichage des données."""
        stats_col = Pages.display_header()
        filtered_placeholder = Pages.display_stats(
            st.session_state.combined_data,
            stats_col
        )

        # Affichage de la date de dernière mise à jour
        if st.session_state.last_update_date:
            st.write(
                f"Dernière mise à jour : "
                f"{st.session_state.last_update_date.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        # Vérification des données
        if (st.session_state.combined_data is None or 
            st.session_state.combined_data.empty):
            st.warning(
                "Aucune donnée disponible. "
                "Veuillez attendre une mise à jour de l'administrateur."
            )
            return

        # Recherche et filtrage
        combined_data = Pages._handle_search_and_filters(
            st.session_state.combined_data
        )

        # Affichage des données filtrées
        Pages._display_filtered_data(
            combined_data,
            filtered_placeholder,
            stats_col
        )

        # Recherche Lenovo PSREF
        Pages._handle_lenovo_search()

    @staticmethod
    def _handle_search_and_filters(df: pd.DataFrame) -> pd.DataFrame:
        """Gère la recherche et les filtres."""
        # Recherche textuelle
        search_query = st.text_input(
            "Rechercher par description ou No. (utilisez * dans vos recherches) :"
        )
        if search_query:
            df = DataManager.advanced_filter_data_by_search_query(
                df,
                search_query
            )

        # Renommage des colonnes
        df = df.rename(columns=COLUMN_MAPPING)

        # Filtres de colonnes
        col_brand, col_category, col_size_format, col_keyboard, col_condition = st.columns(5)
        filters = {
            "Brand": col_brand.multiselect("Brand", list(df["Brand"].unique())),
            "Category": col_category.multiselect("Category", list(df["Category"].unique())),
            "Size/Format": col_size_format.multiselect("Size/Format", list(df["Size/Format"].unique())),
            "Keyboard": col_keyboard.multiselect("Keyboard", list(df["Keyboard"].unique())),
            "Condition": col_condition.multiselect("Condition", list(df["Condition"].unique()))
        }

        # Application des filtres
        df = DataManager.apply_filters(df, filters)

        # Filtre de devise
        selected_currency = st.selectbox(
            "Sélectionnez une devise :",
            CURRENCY_COLUMNS
        )
        df = DataManager.filter_by_currency(df, selected_currency)

        return df

    @staticmethod
    def _display_filtered_data(
        df: pd.DataFrame,
        filtered_placeholder: Any,
        stats_col: Any
    ):
        """Affiche les données filtrées et options d'export."""
        # Mise à jour des statistiques
        filtered_refs = DataManager.get_filtered_quantity(df)
        with stats_col:
            filtered_placeholder.write(
                f"Quantité totale filtrée : {filtered_refs}"
            )

        # Préparation des données pour l'affichage
        display_df = DataManager.prepare_data_for_display(
            df,
            COLUMNS_TO_REMOVE,
            CURRENCY_COLUMNS,
            st.session_state.get("selected_currency", CURRENCY_COLUMNS[0])
        )

        # Affichage du tableau
        s = display_df.style.format({
            st.session_state.get(
                "selected_currency",
                CURRENCY_COLUMNS[0]
            ): "{:.2f}"
        })
        st.dataframe(s)

        # Export Excel
        if not df.empty:
            Pages._handle_excel_export(display_df)

    @staticmethod
    def _handle_excel_export(df: pd.DataFrame):
        """Gère l'export Excel des données."""
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Stock')
            worksheet = writer.sheets['Stock']
            
            for i, column in enumerate(df.columns, 1):
                max_length = max(
                    df[column].astype(str).map(len).max(),
                    len(column)
                ) + 2
                col_letter = openpyxl.utils.get_column_letter(i)
                worksheet.column_dimensions[col_letter].width = max_length

        st.download_button(
            label="Exporter en Excel",
            data=excel_buffer.getvalue(),
            file_name=f"stocklist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    @staticmethod
    def _handle_lenovo_search():
        """Gère la recherche Lenovo PSREF."""
        st.subheader("Recherche intelligente Lenovo PSREF (avec PDF)")
        
        psref_query = st.text_input(
            "Entre une référence Lenovo "
            "(ex: 'ThinkPad X1 Carbon' ou 'ThinkPad X1 Carbon avec 16 Go') :"
        )
        search_mode = st.radio(
            "Mode de recherche :",
            ["Focus sur le détail", "Général"],
            horizontal=True
        )

        if psref_query:
            api_client = APIClient()
            result = api_client.process_lenovo_search(psref_query, search_mode)
            
            if result is not None:
                if "success" in result and result["success"]:
                    data = result["data"]
                    st.write(f"PDF trouvé : {data['pdf_url']}")
                    st.subheader(
                        f"Résultats formatés pour '{psref_query}' ({data['mode']})"
                    )
                    st.dataframe(pd.DataFrame(data["results"]))
                else:
                    error_message = result.get("message", "Erreur lors de la recherche")
                    st.warning(error_message)
                    if "data" in result and isinstance(result["data"], dict):
                        if "raw_response" in result["data"]:
                            st.write("Réponse brute:", result["data"]["raw_response"])
            else:
                st.error("Erreur: Aucun résultat obtenu de l'API")

    @staticmethod
    @AuthManager.requires_admin
    def admin_page():
        """Page d'administration."""
        st.title("Administration")
        file1 = st.file_uploader(
            "Importez le fichier de stock :",
            type=["xlsx"]
        )
        
        if file1:
            try:
                data = pd.read_excel(file1)
                last_update_date = datetime.now()
                
                # Sauvegarde des données
                DataManager.save_persistent_data(data, last_update_date)
                
                # Mise à jour de l'état de session
                st.session_state.combined_data = data
                st.session_state.last_update_date = last_update_date
                
                # Confirmation
                st.success(
                    f"Données mises à jour avec succès le "
                    f"{last_update_date.strftime('%Y-%m-%d %H:%M:%S')} !"
                )
                
                # Prévisualisation
                st.write("Prévisualisation des données :")
                st.write(data)
            except Exception as e:
                st.error(f"Erreur lors de l'import : {str(e)}")