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
    # Display of selected company details
    company_list = data['Navn'].dropna().unique()
    selected_company = st.selectbox('Choisir une compagnie:', company_list)
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

    # Pie chart visualization
    if st.checkbox("Voir la répartition par ville"):
        city_data = data['By'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(city_data, labels=city_data.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

    if st.checkbox("Voir la répartition par groupe débiteur"):
        group_data = data['Debitorprisgruppe'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(group_data, labels=group_data.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)
else:
    st.write("Veuillez télécharger un fichier pour voir les données.")


