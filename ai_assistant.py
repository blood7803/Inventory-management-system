import streamlit as st
from google import genai

# Create Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def show_ai_assistant():
    st.title("🤖 Inventory AI Assistant")

    prompt = st.chat_input("Ask me anything...")

    if prompt:
        st.chat_message("user").write(prompt)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        st.chat_message("assistant").write(response.text)