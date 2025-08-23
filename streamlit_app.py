import streamlit as st
import re

st.set_page_config(page_title="Article Search", layout="wide")

st.title("📄 Article Search & Q&A (Lightweight)")

uploaded_file = st.file_uploader("Upload your text file", type=["txt"])

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
    # Split into articles based on delimiters
    articles = re.split(r'`{5,}|={5,}|-{5,}', text)
    articles = [a.strip() for a in articles if a.strip()]

    st.success(f"Loaded {len(articles)} articles.")

    query = st.text_input("🔎 Ask a question or enter keywords:")

    if query:
        results = []
        for i, article in enumerate(articles):
            if query.lower() in article.lower():
                results.append((i, article))

        if results:
            st.subheader("Search Results")
            for idx, (i, res) in enumerate(results, 1):
                with st.expander(f"Result {idx} (Article {i+1})"):
                    st.write(res)   # show full article
        else:
            st.warning("No results found. Try another word.")
