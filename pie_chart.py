import streamlit as st
import pandas as pd
from datetime import datetime
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
    # Display pie chart with 300x300 size
    fig, ax = plt.subplots(figsize=(3, 3))
    data_to_plot = data[column_name].value_counts()
    ax.pie(data_to_plot, labels=data_to_plot.index, startangle=90, counterclock=False, autopct='%1.1f%%')
    ax.set_title(f"Distribution of {column_name}")
    st.pyplot(fig)

def display_data_page():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("https://github.com/nattyraz/Remanufactured-stocklist/blob/main/logo%20foxway.png?raw=true", width=100)
    with col2:
        st.title("Remanufactured stocklist Lenovo Garantie Original")
    
    combined_data = get_combined_data()['data']
    last_update_date = get_last_update_date()['date']
    
    # Show last update date
    if last_update_date:
        st.write(f"Dernière mise à jour: {last_update_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show data in a table
    if combined_data is not None and not combined_data.empty:
        st.write(combined_data)
    
    # Show pie chart if data is available
    if combined_data is not None:
        st.write("## Distribution Chart")
        columns_for_pie_chart = ["Product Group Code", "Keyboard Language", "Condition", "Avail. Qty"]
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
