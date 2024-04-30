import streamlit as st
import pandas as pd
import numpy as np

def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    else:
        return pd.DataFrame()

st.title('Gestionnaire de Clients')

# Widget de téléchargement de fichier
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx'])
data = load_data(uploaded_file)

if not data.empty:
    # Sélection de la compagnie
    company_list = data['Navn'].dropna().unique()
    selected_company = st.selectbox('Choisir une compagnie:', company_list)

    # Affichage des informations de la compagnie sélectionnée
    if selected_company:
        company_data = data[data['Navn'] == selected_company].iloc[0]
        st.write('### Détails de la Compagnie')
        st.write('**Nom:**', company_data['Navn'])
        st.write('**Contact:**', company_data['Kontakt'])
        st.write('**Email:**', company_data['Mail'])
        st.write('**Téléphone:**', company_data['Telefon'])
        st.write('**Ville:**', company_data['By'])
        st.write('**Dernier Contact:**', company_data['LastContact'])
        st.write('**Kreditmaximum:**', company_data['Kreditmaksimum (RV)'])
        st.write('**Groupe Débiteur:**', company_data['Debitorprisgruppe'])

    # Statistiques
    st.write('### Statistiques')
    active_clients = data[data['LastContact'] >= pd.Timestamp.now() - pd.DateOffset(months=12)]
    st.write('**Nombre de Clients Actifs (contactés dans les derniers 12 mois):**', len(active_clients))
    st.write('**Nombre Total de Clients:**', len(data))
else:
    st.write("Veuillez télécharger un fichier pour voir les données.")

# Pour exécuter, sauvegardez ce script dans un fichier .py et lancez-le avec `streamlit run votre_fichier.py`
