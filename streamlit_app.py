import streamlit as st
import requests

# =================================================
# 1) Load Articles (from articles.txt)
# =================================================
@st.cache_data
def load_articles():
    try:
        with open("articles.txt", "r", encoding="utf-8") as f:
            articles = [line.strip() for line in f if line.strip()]
        return articles
    except Exception as e:
        st.error(f"⚠️ Failed to load articles file: {e}")
        return []

articles = load_articles()

# =================================================
# 2) Fetch Best Practice (BP) Files from Kinaxis-BestPractices Repo
# =================================================
@st.cache_data
def fetch_bp_files():
    try:
        url = "https://api.github.com/repos/anildhankre/Kinaxis-BestPractices/contents/?ref=main"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            return [f["name"] for f in data if f["name"].lower().endswith(".pdf")]
        else:
            st.error(f"⚠️ Failed to fetch files from GitHub (Status {res.status_code}) → {url}")
            return []
    except Exception as e:
        st.error(f"⚠️ Error fetching files: {e}")
        return []

bp_files = fetch_bp_files()

# =================================================
# 3) Streamlit UI
# =================================================
st.title("📄 Article & Best Practices Search")

query = st.text_input("🔍 Enter search term (use `BP:term` for Best Practices files)")

if query:
    if query.lower().startswith("bp:"):
        term = query[3:].strip().lower()
        st.subheader(f"🔎 Searching Best Practices for: {term}")
        results = [f for f in bp_files if term in f.lower()]
        if results:
            for r in results:
                st.write(f"- {r}")
        else:
            st.warning("No matches found in Best Practices files.")
    else:
        term = query.strip().lower()
        st.subheader(f"🔎 Searching Articles for: {term}")
        results = [a for a in articles if term in a.lower()]
        if results:
            for i, r in enumerate(results, 1):
                st.write(f"Article {i}: {r}")
        else:
            st.warning("No matches found in Articles.")

# Show Index button
if st.button("Show Index"):
    st.subheader("📑 Index of Articles")
    for i, art in enumerate(articles, 1):
        st.write(f"Article {i} — {art}")

    st.subheader("📑 Index of Best Practices Files")
    for i, f in enumerate(bp_files, 1):
        st.write(f"BP File {i} — {f}")
