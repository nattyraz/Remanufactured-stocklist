import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os

# Fonction pour convertir la date au format datetime
def convert_date(date_str):
    return datetime.strptime(date_str, "%d-%m-%Y")

# Titre de l'application
st.title("Techcycle Warranty Checker")

# Durée de la garantie en jours (3 ans)
WARRANTY_DAYS = 3 * 365

# Fichier de stockage des numéros de série et dates de livraison
storage_file = "global_serial_numbers.csv"

# Page de sélection
page = st.sidebar.selectbox("Sélectionner une page", ["Admin", "Client"])

# Page Admin avec authentification
if page == "Admin":
    st.subheader("Page Admin")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if username == "admin" and password == "Foxway2023":
        uploaded_file = st.file_uploader("Uploader un fichier Excel", type=["xlsx"])
        if uploaded_file:
            # À compléter: Code pour ajouter les données du fichier Excel au fichier CSV
            st.write("Fichier uploadé avec succès")
    else:
        st.write("Identifiants incorrects")

# Page Client
elif page == "Client":
    st.subheader("Page Client")
    serial_number = st.text_input("Entrer le numéro de série")
    if st.button("Vérifier"):
        if os.path.exists(storage_file):
            df = pd.read_csv(storage_file)
            matching_records = df[df['Serial'] == serial_number]
            
            if not matching_records.empty:
                purchase_date = convert_date(matching_records.iloc[0]['Shipment Date'])
                warranty_end = purchase_date + timedelta(days=WARRANTY_DAYS)
                remaining_time = warranty_end - datetime.now()
                
                st.write(f"Date d'achat: {purchase_date.strftime('%d-%m-%Y')}")
                st.write(f"Début de la garantie: {purchase_date.strftime('%d-%m-%Y')}")
                st.write(f"Fin de la garantie: {warranty_end.strftime('%d-%m-%Y')}")
                st.write(f"Temps restant pour la garantie: {remaining_time.days} jours")
            else:
                st.write("Numéro de série non trouvé")
        else:
            st.write("Aucun numéro de série n'est encore stocké.")
