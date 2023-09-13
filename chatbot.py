
import streamlit as st
import openai

# The chatbot section for Streamlit
def chatbot_section(messages):
    st.title("Chatbot")
    
    # Display previous chat history
    for message in messages:
        if message['role'] == 'user':
            st.write(f"**You**: {message['content']}")
        else:
            st.write(f"**Assistant**: {message['content']}")
    
    # Get user input
    user_input = st.text_input("Ask the assistant:")
    
    if user_input:
        messages.append({"role": "user", "content": user_input})
        
        # Fetching the response from OpenAI (this is a mock; in real application, you'd call OpenAI here)
        response = "This is a mock response. In a real application, you'd fetch a response from OpenAI."
        
        # Adding the response to messages
        messages.append({"role": "assistant", "content": response})

# Starting messages
messages = [{"role": "assistant", "content": "Comment puis-je vous aider?"}]

# Run the chatbot section
chatbot_section(messages)
