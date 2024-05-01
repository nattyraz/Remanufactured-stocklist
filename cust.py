import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to load data from an uploaded Excel file
def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    else:
        return pd.DataFrame()

st.title('Gestionnaire de Clients')

# File uploader widget
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx'])
data = load_data(uploaded_file)

if not data.empty:
    # Pie chart for customer segmentation
    if 'Customer Segmentation' in data.columns and st.checkbox("Voir la répartition par segmentation de client"):
        segmentation_data = data['Customer Segmentation'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(segmentation_data, labels=segmentation_data.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1)
    
    # Bar chart for clients by city
    if 'By' in data.columns and st.checkbox("Voir le nombre de clients par ville"):
        city_counts = data['By'].value_counts()
        fig2, ax2 = plt.subplots()
        city_counts.plot(kind='bar', color='skyblue', ax=ax2)
        ax2.set_title('Nombre de Clients par Ville')
        ax2.set_xlabel('Ville')
        ax2.set_ylabel('Nombre de Clients')
        st.pyplot(fig2)

else:
    st.write("Veuillez télécharger un fichier pour voir les données.")


