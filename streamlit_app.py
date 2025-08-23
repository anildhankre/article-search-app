import streamlit as st
import requests
import os

# Load Hugging Face API key from secrets
HF_API_KEY = st.secrets["HF_API_KEY"]

# Hugging Face model (free)
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def query_huggingface(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 300}
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        data = response.json()
        # HuggingFace returns a list of dicts
        return data[0]["generated_text"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# --- Streamlit UI ---
st.title("📄 Article Search with Hugging Face")

# Load your local articles.txt
with open("articles.txt", "r", encoding="utf-8") as f:
    articles = f.read()

user_input = st.text_input("Ask something from articles.txt")

if user_input:
    prompt = f"""
    Answer the following question using only this article content:

    {articles}

    Question: {user_input}
    """
    with st.spinner("Thinking..."):
        answer = query_huggingface(prompt)
    st.write("### Answer:")
    st.write(answer)
