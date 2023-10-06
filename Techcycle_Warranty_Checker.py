import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Chemin du fichier CSV où les données seront stockées
storage_file = "serial_numbers_and_dates.csv"

# Initialisation du DataFrame
columns = ["Invoice Number", "Serial Number", "Shipment Date"]
if not os.path.exists(storage_file):
    df = pd.DataFrame(columns=columns)
    df.to_csv(storage_file, index=False)
else:
    df = pd.read_csv(storage_file)

# Interface Streamlit
st.title("Techcycle Warranty Checker")

page = st.sidebar.selectbox("Sélectionner une page", ["Admin", "Client"])

# Page Admin
if page == "Admin":
    st.subheader("Page Admin")
    uploaded_file = st.file_uploader("Uploader un fichier Excel", type=["xlsx"])
    if uploaded_file:
        temp_df = pd.read_excel(uploaded_file, usecols=["F", "P", "Y"])
        invoice_number = temp_df.loc[0, "P"]
        shipment_date = temp_df.loc[0, "Y"]
        serial_numbers = temp_df["F"].dropna().values
        new_data = {
            "Invoice Number": [invoice_number]*len(serial_numbers),
            "Serial Number": serial_numbers,
            "Shipment Date": [shipment_date]*len(serial_numbers)
        }
        new_df = pd.DataFrame(new_data)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(storage_file, index=False)
        st.write("Données uploadées avec succès.")

# Page Client
elif page == "Client":
    st.subheader("Page Client")
    serial_number = st.text_input("Entrer le numéro de série")
    if st.button("Vérifier"):
        if os.path.exists(storage_file) and os.path.getsize(storage_file) > 0:
            df = pd.read_csv(storage_file)
            match = df[df["Serial Number"] == serial_number]
            if not match.empty:
                st.write(f"Date de livraison: {match.iloc[0]['Shipment Date']}")
                shipment_date = datetime.strptime(match.iloc[0]['Shipment Date'], "%d-%m-%Y")
                warranty_end = shipment_date + timedelta(days=3*365)
                st.write(f"Fin de garantie: {warranty_end.strftime('%d-%m-%Y')}")
            else:
                st.write("Numéro de série non trouvé.")
        else:
            st.write("Aucun numéro de série n'est encore stocké.")
