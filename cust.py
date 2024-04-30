import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim

# Function to load data from an uploaded Excel file
def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    else:
        return pd.DataFrame()

# Function to geocode an address (fallback if no coordinates in the dataset)
def geocode_address(address):
    geolocator = Nominatim(user_agent="my_geocoder")
    try:
        location = geolocator.geocode(address)
        return location.latitude, location.longitude
    except:
        return None, None

st.title('Gestionnaire de Clients')

# File uploader widget
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx'])
data = load_data(uploaded_file)

if not data.empty:
    # Selection of a company from the list
    company_list = data['Navn'].dropna().unique()
    selected_company = st.selectbox('Choisir une compagnie:', company_list)

    # Display of selected company details
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

    # Check if coordinates columns exist, otherwise geocode (this is simplified and would ideally be handled differently)
    if 'Latitude' not in data.columns or 'Longitude' not in data.columns:
        st.write("Geocoding addresses... this may take a while.")
        data['Latitude'], data['Longitude'] = zip(*data['Adresse'].map(geocode_address))

    # Filtering clients by country code
    countries = ['France', 'Belgium', 'Luxembourg', 'Monaco']
    filtered_data = data[data['Lande-/områdekode'].isin(countries)]

    # Map visualization of client locations
    st.write('### Map of Client Locations')
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=filtered_data['Latitude'].mean(),
            longitude=filtered_data['Longitude'].mean(),
            zoom=5,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=filtered_data,
                get_position='[Longitude, Latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=10000,
            ),
        ],
    ))
else:
    st.write("Veuillez télécharger un fichier pour voir les données.")


