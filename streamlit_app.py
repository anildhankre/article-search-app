import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Article Search with ChatGPT")

query = st.text_input("Ask something from articles.txt")
if st.button("Search & Answer"):   # ✅ only run on button click
    with open("articles.txt", "r", encoding="utf-8") as f:
        articles = f.read()

    prompt = f"Answer the question based only on the following text:\n\n{articles}\n\nQuestion: {query}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        st.write(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error: {e}")
