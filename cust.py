import streamlit as st
import pandas as pd
import plotly.express as px

def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    else:
        return pd.DataFrame()

st.title('Gestionnaire de Clients')

# Téléchargement de fichier
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx'])
data = load_data(uploaded_file)

if not data.empty:
    # Visualisation des clients par ville
    st.write('## Distribution des Clients par Ville')
    fig = px.bar(data['By'].value_counts().reset_index(), x='index', y='By', labels={'index': 'Ville', 'By': 'Nombre de Clients'})
    st.plotly_chart(fig)

    # Analyse des contacts récents
    recent_contacts = data[data['LastContact'] >= pd.Timestamp.now() - pd.DateOffset(months=12)]
    st.write('## Contacts Récents')
    fig2 = px.line(recent_contacts, x='LastContact', y='Nummer', title='Activité des Contacts Récents')
    st.plotly_chart(fig2)

    # Autres sections de l'interface ici...
else:
    st.write("Veuillez télécharger un fichier pour voir les données.")

