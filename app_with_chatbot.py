import streamlit as st
import pandas as pd
import openai
from datetime import datetime
import re  # For regular expression matching

# Constants for Admin Authentication
ADMIN_PASSWORD = st.secrets["general"]["ADMIN_PASSWORD"]
OPENAI_API_KEY = st.secrets["general"]["OPENAI_API_KEY"]

def check_credentials(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

# Set page configuration
st.set_page_config(
    page_title="Remanufactured Stocklist",
    page_icon="favicon.ico",
    layout="wide"
)

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_combined_data():
    return {'data': None}

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_last_update_date():
    return {'date': None}

def advanced_filter_data_by_search_query(df, query):
    sub_queries = re.split(r'[ *]', query)
    for sub_query in sub_queries:
        if sub_query:
            sub_query = sub_query.replace("*", ".*")
            pattern = re.compile(sub_query, re.IGNORECASE)
            df = df[df.apply(lambda row: row.astype(str).str.contains(pattern).any(), axis=1)]
    return df

# Function to get a response from GPT
def gpt_response_with_openai(query, data_frame, api_key=None):
    # Assuming you will use the openai library, here's a basic structure:
    openai.api_key = api_key if api_key else OPENAI_API_KEY
    
    # Some basic intents that use the data frame directly
    if "combien" in query and "produits" in query:
        return f"Il y a {len(data_frame)} produits dans la base de données."
    elif "caractéristiques" in query:
        return "Les produits ont différentes caractéristiques techniques. Veuillez spécifier un produit pour plus de détails."
    else:
        # Making a call to OpenAI's GPT to get the response
        response = openai.Completion.create(
          engine="davinci",  # You can choose other engines if you want
          prompt=query,
          max_tokens=150
        )
        return response.choices[0].text.strip()

# The advanced chatbot section for Streamlit using OpenAI's GPT
def advanced_chatbot_section(data_frame, last_update_date, api_key=None):
    st.title("Chatbot - Account Manager")
    
    # Using Streamlit's session state for simple memory
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Bonjour! Comment puis-je vous aider en tant que votre Account Manager?"}]
    
    # Display previous chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.write(f"**Vous**: {message['content']}")
        else:
            st.write(f"**Assistant**: {message['content']}")
    
    # Get user input
    user_input = st.text_input("Posez votre question:")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Generate response using the GPT function with OpenAI
        response = gpt_response_with_openai(user_input, data_frame, api_key)
        
        # Append the response to the chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# ... (pre-existing code remains unchanged)

def admin_page():
    st.sidebar.title("Administration")
    username = st.sidebar.text_input("Nom d'utilisateur", type="default")
    password = st.sidebar.text_input("Mot de passe", type="password")
    
    if not check_credentials(username, password):
        st.sidebar.warning("Identifiants incorrects. Veuillez réessayer.")
        return

    file1 = st.file_uploader("Importez le premier fichier:", type=["xlsx"])
    file2 = st.file_uploader("Importez le deuxième fichier:", type=["xlsx"])
    file3 = st.file_uploader("Importez le troisième fichier (optionnel):", type=["xlsx"])
    file4 = st.file_uploader("Importez le quatrième fichier (optionnel):", type=["xlsx"])
    
    files = [file for file in [file1, file2, file3, file4] if file]
    
    if files:
        dataframes = [pd.read_excel(file) for file in files]
        combined_data = pd.concat(dataframes)
        last_update_date = datetime.now()
        st.success("The data has been updated successfully!")
        st.write("Prévisualisation des données combinées :")
        st.write(combined_data)
        get_combined_data()['data'] = combined_data
        get_last_update_date()['date'] = last_update_date

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choisissez une page:", ["Affichage des données", "Administration"])
    
    if page == "Affichage des données":
        display_data_page()
    else:
        admin_page()

if __name__ == "__main__":
    main()

# Here's the corrected chatbot function:

# Function to get a response from GPT
def gpt_response_with_openai(query, data_frame, api_key=None):
    # Assuming you will use the openai library, here's a basic structure:
    openai.api_key = api_key if api_key else OPENAI_API_KEY
    
    # Some basic intents that use the data frame directly
    if "combien" in query and "produits" in query:
        return f"Il y a {len(data_frame)} produits dans la base de données."
    elif "caractéristiques" in query:
        return "Les produits ont différentes caractéristiques techniques. Veuillez spécifier un produit pour plus de détails."
    else:
        # Making a call to OpenAI's GPT to get the response
        response = openai.Completion.create(
          engine="davinci",  # You can choose other engines if you want
          prompt=query,
          max_tokens=150
        )
        return response.choices[0].text.strip()

# The advanced chatbot section for Streamlit using OpenAI's GPT
def advanced_chatbot_section(data_frame, last_update_date, api_key=None):
    st.title("Chatbot - Account Manager")
    
    # Using Streamlit's session state for simple memory
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Bonjour! Comment puis-je vous aider en tant que votre Account Manager?"}]
    
    # Display previous chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.write(f"**Vous**: {message['content']}")
        else:
            st.write(f"**Assistant**: {message['content']}")
    
    # Get user input
    user_input = st.text_input("Posez votre question:")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Generate response using the GPT function with OpenAI
        response = gpt_response_with_openai(user_input, data_frame, api_key)
        
        # Append the response to the chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Assuming the API key will be stored securely and passed when the function is called
advanced_chatbot_section(get_combined_data()['data'], get_last_update_date()['date'])

