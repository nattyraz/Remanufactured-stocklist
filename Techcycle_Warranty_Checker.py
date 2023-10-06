
import streamlit as st
from datetime import datetime, timedelta

# Titre de l'application
st.title("Teqcycle Warranty Checker")

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
            st.write("Fichier uploadé avec succès")
    else:
        st.write("Identifiants incorrects")

# Page Client
elif page == "Client":
    st.subheader("Page Client")
    serial_number = st.text_input("Entrer le numéro de série")
    if st.button("Vérifier"):
        purchase_date = datetime.now()  # À remplacer par la vraie date d'achat, si nécessaire
        warranty_end = purchase_date + timedelta(days=WARRANTY_DAYS)
        remaining_time = warranty_end - datetime.now()
            
        st.write(f"Date d'achat: {purchase_date.strftime('%Y-%m-%d')}")
        st.write(f"Début de la garantie: {purchase_date.strftime('%Y-%m-%d')}")
        st.write(f"Fin de la garantie: {warranty_end.strftime('%Y-%m-%d')}")
        st.write(f"Temps restant pour la garantie: {remaining_time.days} jours")
