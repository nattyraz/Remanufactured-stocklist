import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    else:
        return pd.DataFrame()

st.title('Dashboard des Ventes de Jeux')

# Téléchargement de fichier
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx'])
data = load_data(uploaded_file)

if not data.empty:
    # Distribution régionale des ventes
    st.write('## Distribution Régionale des Ventes')
    regions = data['Region'].value_counts().reset_index()
    fig = px.pie(regions, values='Region', names='index', title='Ventes par Région')
    st.plotly_chart(fig)
    
    # Top 10 des ventes de jeux
    st.write('## Top 10 des Ventes de Jeux')
    top_games = data.nlargest(10, 'Ventes')
    fig2 = px.bar(top_games, x='Jeu', y='Ventes', title='Top 10 des Jeux par Ventes')
    st.plotly_chart(fig2)

    # Tendance des ventes au fil du temps
    st.write('## Tendance des Ventes au Fil du Temps')
    fig3 = px.line(data, x='Année', y='Ventes', color='Jeu', title='Tendances des Ventes par Jeu')
    st.plotly_chart(fig3)

    # Dashboard numérique pour les ventes globales
    st.write('## Résumé des Ventes')
    total_sales = data['Ventes'].sum()
    st.metric(label="Ventes Totales", value=f"${total_sales:,.2f}")

else:
    st.write("Veuillez télécharger un fichier pour voir les données.")
