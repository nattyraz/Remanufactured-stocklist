import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim

# Function to load data from an uploaded Excel file
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        # Ajouter des colonnes si elles n'existent pas
        if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
            df['Latitude'] = None
            df['Longitude'] = None
        return df
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

# Geocode missing coordinates
def geocode_missing_coordinates(data):
    for i, row in data.iterrows():
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
            lat, lon = geocode_address(row['Adresse'])
            data.at[i, 'Latitude'] = lat
            data.at[i, 'Longitude'] = lon
    return data

st.title('Gestionnaire de Clients')

# File uploader widget
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type=['xlsx'])
data = load_data(uploaded_file)

if not data.empty:
    # Perform geocoding if necessary
    if data['Latitude'].isnull().any() or data['Longitude'].isnull().any():
        st.write("Geocoding addresses... this may take a while.")
        data = geocode_missing_coordinates(data)

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

    # Map visualization of client locations
    st.write('### Map of Client Locations')
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=data['Latitude'].mean(),
            longitude=data['Longitude'].mean(),
            zoom=5,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=data,
                get_position='[Longitude, Latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=10000,
                pickable=True
            ),
        ],
        tooltip={
            'html': '<b>Company:</b> {Navn}<br><b>Contact:</b> {Kontakt}<br><b>Email:</b> {Mail}',
            'style': {
                'backgroundColor': 'steelblue',
                'color': 'white'
            }
        }
    ))
else:
    st.write("Veuillez télécharger un fichier pour voir les données.")


