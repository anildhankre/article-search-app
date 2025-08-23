import streamlit as st
from openai import OpenAI
import os

# Load OpenAI API key (set it as a Streamlit secret in cloud)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Load your articles file ---
@st.cache_data
def load_articles():
    with open("articles.txt", "r", encoding="utf-8") as f:
        text = f.read()
    # Split articles by separators
    import re
    articles = re.split(r"[-=]{5,}|`{5,}", text)
    return [a.strip() for a in articles if a.strip()]

articles = load_articles()

# --- Streamlit UI ---
st.title("📖 Article Q&A App")
st.write("Ask questions, and the app will answer based on `articles.txt`.")

user_q = st.text_input("Enter your question:")

if user_q:
    # 1. Create context by concatenating all articles (for small file)
    # For large files, you'd use embeddings search
    context = "\n\n".join(articles)

    # 2. Ask GPT with context
    prompt = f"""
You are a helpful assistant. Answer the question using the text below.
If the answer is not found, say 'I don't know based on the articles.'

Articles:
{context}

Question: {user_q}
Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheaper, faster ChatGPT
        messages=[{"role": "user", "content": prompt}],
    )

    st.write("### Answer:")
    st.write(response.choices[0].message.content)
