import streamlit as st
import pandas as pd
import plotly.express as px

def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("Colonnes disponibles dans le fichier chargé:", df.columns)  # Affiche les noms des colonnes
        return df
    return pd.DataFrame()

st.title('Dashboard de Gestion des Clients')

uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx'])
data = load_data(uploaded_file)

if not data.empty:
    # Vérifier la présence des colonnes nécessaires
    required_columns = ['Region', 'Ventes', 'Jeu', 'Année']  # Assurez-vous que ces noms de colonnes correspondent exactement à votre fichier Excel.
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        st.error(f"Les colonnes suivantes sont manquantes dans le fichier Excel: {', '.join(missing_columns)}")
    else:
        # Distribution régionale des ventes
        try:
            st.write('## Distribution Régionale des Ventes')
            regions = data['Region'].value_counts().reset_index()
            fig = px.pie(regions, values='Region', names='index', title='Ventes par Région')
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Erreur lors de la création du graphique des ventes régionales: {e}")

        # Top 10 des ventes de jeux
        try:
            st.write('## Top 10 des Ventes de Jeux')
            top_games = data.nlargest(10, 'Ventes')
            fig2 = px.bar(top_games, x='Jeu', y='Ventes', title='Top 10 des Jeux par Ventes')
            st.plotly_chart(fig2)
        except Exception as e:
            st.error(f"Erreur lors de la création du graphique des top ventes de jeux: {e}")

        # Tendance des ventes au fil du temps
        try:
            st.write('## Tendance des Ventes au Fil du Temps')
            fig3 = px.line(data, x='Année', y='Ventes', color='Jeu', title='Tendances des Ventes par Jeu')
            st.plotly_chart(fig3)
        except Exception as e:
            st.error(f"Erreur lors de la création du graphique des tendances de ventes: {e}")
else:
    st.write("Veuillez télécharger un fichier pour voir les données.")
