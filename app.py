import streamlit as st
import pandas as pd

# Fonction pour afficher le DataFrame dans Streamlit
def display_data(df):
    st.write(df)

# Application principale
def main():
    st.title("Gestionnaire de liste de prix")
    
    # Charger un fichier pour afficher et mettre à jour les données
    uploaded_file = st.file_uploader("Importez un fichier pour affichage et mise à jour:", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            
            # Vérifiez que le fichier chargé a la même structure que le fichier modèle
            # (Vous pouvez ajuster cette vérification selon vos besoins)
            expected_columns = ["No.", "Description", "Item Category Code", "Product Group Code", "Software Language", 
                                "Keyboard Language", "Graphics01", "Graphics02", "Condition", "Warranty", "Avail. Qty", "Promo Price EUR"]
            if list(df.columns) == expected_columns:
                display_data(df)
            else:
                st.error("La structure du fichier chargé ne correspond pas au modèle attendu!")
        
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de la lecture du fichier: {e}")

if __name__ == "__main__":
    main()
