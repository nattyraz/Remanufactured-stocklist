import streamlit as st
import pandas as pd
import smtplib

# 1. Lire le fichier Excel
data = pd.read_excel("chemin_du_fichier.xlsx")

# 2. Afficher les données
st.write(data)

# 3. Sélectionner une référence
ref_selected = st.selectbox("Sélectionnez une référence", data['colonne_de_reference'].unique())

if st.button("Envoyer par e-mail"):
    # 4. Envoyer un e-mail
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("votre_email@gmail.com", "votre_mot_de_passe")
        subject = "Demande de référence"
        body = f"La référence sélectionnée est {ref_selected}."
        msg = f"Subject: {subject}\n\n{body}"
        server.sendmail("votre_email@gmail.com", "account_manager_email@example.com", msg)
    st.write("E-mail envoyé avec succès!")

