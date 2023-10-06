
import streamlit as st
from datetime import datetime, timedelta
import os
import base64
import pandas as pd

# Fonction pour convertir la date au format datetime
def convert_date(date_str):
    return datetime.strptime(date_str, "%d-%m-%Y")

# Titre de l'application
st.title("Techcycle Warranty Checker")

# Durée de la garantie en jours (3 ans)
WARRANTY_DAYS = 3 * 365

# Fichier de stockage des numéros de série et dates de livraison
storage_file = "serial_numbers_and_dates.txt"

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
            df = pd.read_excel(uploaded_file)
            shipment_date = df.loc[0, 'Shipment Date'].strftime("%d-%m-%Y")
            file_content = base64.b64encode(uploaded_file.read()).decode()
            with open(storage_file, "a") as f:
                f.write(f"{file_content}|{shipment_date}\n")
            st.write(f"Fichier uploadé avec succès. Date de livraison : {shipment_date}")
    else:
        st.write("Identifiants incorrects")

# Page Client
elif page == "Client":
    st.subheader("Page Client")
    serial_number = st.text_input("Entrer le numéro de série")
    if st.button("Vérifier"):
        if os.path.exists(storage_file):
            with open(storage_file, "r") as f:
                stored_data = f.read().splitlines()
            for record in stored_data:
                try:
                    stored_serial, stored_date = record.split("|")
                except ValueError:
                    continue
                
                try:
                    decoded_serial = base64.b64decode(stored_serial).decode()
                except UnicodeDecodeError:
                    st.write("Erreur lors du décodage du numéro de série.")
                    continue
                
                if serial_number == decoded_serial:
                    purchase_date = convert_date(stored_date)
                    warranty_end = purchase_date + timedelta(days=WARRANTY_DAYS)
                    remaining_time = warranty_end - datetime.now()
                    
                    st.write(f"Date d'achat: {purchase_date.strftime('%d-%m-%Y')}")
                    st.write(f"Début de la garantie: {purchase_date.strftime('%d-%m-%Y')}")
                    st.write(f"Fin de la garantie: {warranty_end.strftime('%d-%m-%Y')}")
                    st.write(f"Temps restant pour la garantie: {remaining_time.days} jours")
                    break
            else:
                st.write("Numéro de série non trouvé")
        else:
            st.write("Aucun numéro de série n'est encore stocké.")
