import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon="favicon.ico",
    layout="wide"
)

# Use caching to store and retrieve the combined data
@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_last_update_date():
    return {'date': None}

def display_pie_chart(data, column_name):
    column_name_translations = {
        "Produits catégories": "Item Category Code",
        "Format": "Product Group Code"
    }
    internal_column_name = column_name_translations.get(column_name, column_name)
    
    if internal_column_name in data.columns:
        data_to_plot = data[internal_column_name].value_counts()
        fig, ax = plt.subplots()
        ax.pie(data_to_plot, labels=data_to_plot.index, startangle=90, counterclock=False, autopct='%1.1f%%')
        ax.set_title(f"Distribution of {column_name}")
        st.pyplot(fig)
    else:
        st.error(f"Column {column_name} not found in the data!")

def display_data_page():
    combined_data = get_combined_data()['data']
    
    # Show pie chart if data is available
    if combined_data is not None:
        columns_for_pie_chart = ["Format", "Produits catégories", "Software Language", "Keyboard Language", 
                                 "Graphics01", "Graphics02", "Condition", "Warranty"]
        column = st.selectbox("Select a column to display pie chart:", columns_for_pie_chart)
        display_pie_chart(combined_data, column)

def admin_page():
    st.title("Administration")
    
    # Upload files
    uploaded_files = st.file_uploader("Upload your Excel files (.xlsx)", type="xlsx", accept_multiple_files=True)
    
    if uploaded_files:
        dfs = [pd.read_excel(file) for file in uploaded_files]
        combined_data = pd.concat(dfs, ignore_index=True)
        
        # Update last update date
        get_last_update_date()['date'] = datetime.now()
        st.success("Data has been successfully loaded!")
        
        # Preview the combined data
        st.write("Data Preview:")
        st.write(combined_data)

        # Store the updated data using caching
        get_combined_data()['data'] = combined_data

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a page:", ["Data Visualization", "Administration"])
    
    if page == "Data Visualization":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()
