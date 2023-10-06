
import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta

# Fonction pour extraire les numéros de série
def extract_serial_numbers(text):
    serial_numbers = []
    lines = text.strip().split('\n')
    for line in lines:
        if line.startswith("SN:"):
            serial_numbers.extend(re.split(r'[\s/]', line[4:].strip()))
    return [sn for sn in serial_numbers if sn]  # Supprimer les éléments vides

# Titre de l'application
st.title("Techcycle Warranty Checker")

# Durée de la garantie en jours (3 ans)
WARRANTY_DAYS = 3 * 365

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
            df['Description'].to_csv("data.csv", index=False)
            st.write("Fichier uploadé avec succès")
    else:
        st.write("Identifiants incorrects")

# Page Client
elif page == "Client":
    st.subheader("Page Client")
    serial_number = st.text_input("Entrer le numéro de série")
    if st.button("Vérifier"):
        df = pd.read_csv("data.csv")
        all_serials = []
        for desc in df['Description']:
            all_serials.extend(extract_serial_numbers(str(desc)))
        if serial_number in all_serials:
            purchase_date = datetime.now()  # À remplacer par la vraie date d'achat
            warranty_end = purchase_date + timedelta(days=WARRANTY_DAYS)
            remaining_time = warranty_end - datetime.now()
            
            st.write(f"Date d'achat: {purchase_date.strftime('%Y-%m-%d')}")
            st.write(f"Début de la garantie: {purchase_date.strftime('%Y-%m-%d')}")
            st.write(f"Fin de la garantie: {warranty_end.strftime('%Y-%m-%d')}")
            st.write(f"Temps restant pour la garantie: {remaining_time.days} jours")
        else:
            st.write("Numéro de série non trouvé")
