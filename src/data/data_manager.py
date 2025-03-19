import pandas as pd
import json
from datetime import datetime
import os
import re
from typing import Optional, Dict, Any

from src.config import DATA_FILES

class DataManager:
    @staticmethod
    def load_persistent_data() -> Optional[pd.DataFrame]:
        """Charge les données du fichier parquet."""
        if os.path.exists(DATA_FILES["data"]):
            return pd.read_parquet(DATA_FILES["data"])
        return None

    @staticmethod
    def load_last_update_date() -> Optional[datetime]:
        """Charge la date de dernière mise à jour."""
        if os.path.exists(DATA_FILES["meta"]):
            with open(DATA_FILES["meta"], "r") as f:
                meta = json.load(f)
                return datetime.fromisoformat(meta["last_update_date"])
        return None

    @staticmethod
    def save_persistent_data(df: pd.DataFrame, last_update_date: datetime) -> None:
        """Sauvegarde les données et la date de mise à jour."""
        df.to_parquet(DATA_FILES["data"])
        with open(DATA_FILES["meta"], "w") as f:
            json.dump({"last_update_date": last_update_date.isoformat()}, f)

    @staticmethod
    def advanced_filter_data_by_search_query(df: pd.DataFrame, query: str) -> pd.DataFrame:
        """Filtre les données selon une requête de recherche avec support wildcard."""
        if not query:
            return df
            
        sub_queries = re.split(r'[ ]', query)
        filtered_df = df.copy()
        
        for sub_query in sub_queries:
            if sub_query:
                sub_query = sub_query.replace("*", ".*")
                pattern = re.compile(sub_query, re.IGNORECASE)
                filtered_df = filtered_df[
                    filtered_df.apply(
                        lambda row: row.astype(str).str.contains(pattern).any(), 
                        axis=1
                    )
                ]
        
        return filtered_df

    @staticmethod
    def apply_filters(df: pd.DataFrame, filters: Dict[str, list]) -> pd.DataFrame:
        """Applique les filtres sélectionnés aux données."""
        filtered_df = df.copy()
        for column, selected_values in filters.items():
            if selected_values:
                filtered_df = filtered_df[filtered_df[column].isin(selected_values)]
        return filtered_df

    @staticmethod
    def filter_by_currency(
        df: pd.DataFrame, 
        currency_column: str, 
        min_qty: int = 0
    ) -> pd.DataFrame:
        """Filtre les données par devise et quantité disponible."""
        return df[
            (df[currency_column].notna()) &
            (df[currency_column] != 0) &
            (df["Avail. Qty"] > min_qty)
        ]

    @staticmethod
    def prepare_data_for_display(
        df: pd.DataFrame,
        columns_to_remove: list,
        currency_columns: list,
        selected_currency: str
    ) -> pd.DataFrame:
        """Prépare les données pour l'affichage."""
        filtered_df = df.drop(columns=columns_to_remove, errors='ignore')
        columns_to_display = [
            col for col in filtered_df.columns 
            if col not in currency_columns
        ]
        columns_to_display.append(selected_currency)
        return filtered_df[columns_to_display]

    @staticmethod
    def get_total_refs(df: Optional[pd.DataFrame]) -> int:
        """Calcule le nombre total de références."""
        if df is not None and not df.empty:
            return len(df)
        return 0

    @staticmethod
    def get_filtered_quantity(df: pd.DataFrame) -> int:
        """Calcule la quantité totale filtrée."""
        if not df.empty:
            return int(df["Avail. Qty"].sum())
        return 0