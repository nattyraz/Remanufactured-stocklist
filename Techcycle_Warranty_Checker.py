
import streamlit as st
from datetime import datetime, timedelta
import os
import base64
import pandas as pd
import re

# Function to convert the date to datetime format
def convert_date(date_str):
    return datetime.strptime(date_str, "%d-%m-%Y")

# App title
st.title("Techcycle Warranty Checker")

# Warranty duration in days (3 years)
WARRANTY_DAYS = 3 * 365

# File to store serial numbers and shipment dates
storage_file = "serial_numbers_and_dates.txt"

# Select page
page = st.sidebar.selectbox("Select a page", ["Admin", "Client"])

# Admin page with authentication
if page == "Admin":
    st.subheader("Admin Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if username == "admin" and password == "Foxway2023":
        uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            text_content = df.to_string(index=False)
            shipment_date_match = re.search(r"Shipment Date\s+(\d{2}-\d{2}-\d{4})", text_content)
            shipment_date = shipment_date_match.group(1) if shipment_date_match else "Unknown date"

            file_content = base64.b64encode(uploaded_file.read()).decode()
            with open(storage_file, "a") as f:
                f.write(f"{file_content}|{shipment_date}\n")
            st.write("File and date successfully uploaded")

    else:
        st.write("Incorrect credentials")

# Client page
elif page == "Client":
    st.subheader("Client Page")
    serial_number = st.text_input("Enter the serial number")
    if st.button("Check"):
        if os.path.exists(storage_file):
            with open(storage_file, "r") as f:
                stored_data = f.read().splitlines()
            for record in stored_data:
                try:
                    stored_serial, stored_date = record.split("|")
                except ValueError:
                    continue

                try:
                    decoded_serial = base64.b64decode(stored_serial).decode()
                except UnicodeDecodeError:
                    st.write("Error decoding the serial number.")
                    continue

                if serial_number == decoded_serial:
                    purchase_date = convert_date(stored_date)
                    warranty_end = purchase_date + timedelta(days=WARRANTY_DAYS)
                    remaining_time = warranty_end - datetime.now()

                    st.write(f"Purchase date: {purchase_date.strftime('%d-%m-%Y')}")
                    st.write(f"Warranty starts: {purchase_date.strftime('%d-%m-%Y')}")
                    st.write(f"Warranty ends: {warranty_end.strftime('%d-%m-%Y')}")
                    st.write(f"Remaining warranty time: {remaining_time.days} days")
                    break
            else:
                st.write("Serial number not found")
        else:
            st.write("No serial numbers have been stored yet.")
