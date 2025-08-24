import streamlit as st
import json
import requests

# ======================================================
# 1) Load Articles (from uploaded/shared JSON file)
# ======================================================
@st.cache_data
def load_articles():
    try:
        with open("articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
        return articles
    except Exception as e:
        st.error(f"⚠️ Failed to load articles file: {e}")
        return []

articles = load_articles()


# ======================================================
# 2) Fetch BP Files from GitHub Repo
# ======================================================
@st.cache_data
def get_bp_files():
    repo_owner = "anildhankre"
    repo_name = "Kinaxis-BestPractices"
    branch = "main"

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    response = requests.get(url)

    if response.status_code == 200:
        files = response.json()
        pdfs = [f["name"] for f in files if f["name"].lower().endswith(".pdf")]
        return pdfs
    else:
        st.error(f"⚠️ Failed to fetch files from GitHub (Status {response.status_code})")
        return []

bp_files = get_bp_files()
GITHUB_BASE = "https://github.com/anildhankre/Kinaxis-BestPractices/blob/main/"


# ======================================================
# 3) Search Functions
# ======================================================
def search_articles(query):
    results = []
    for idx, article in enumerate(articles, start=1):
        if query.lower() in " ".join(article["keywords"]).lower():
            results.append((idx, article))
    return results

def search_bp_files(query):
    results = []
    for idx, fname in enumerate(bp_files, start=1):
        if query.lower() in fname.lower():
            url = f"{GITHUB_BASE}{fname.replace(' ', '%20')}"  # encode spaces
            results.append((idx, fname, url))
    return results


# ======================================================
# 4) Streamlit UI
# ======================================================
st.title("📄 Article & Best Practices Search")

query = st.text_input("🔍 Enter search term (use `BP:term` for Best Practices files)")

if query:
    if query.lower().startswith("bp:"):
        # ------------------------------
        # BP FILE SEARCH
        # ------------------------------
        bp_term = query[3:].strip()
        results = search_bp_files(bp_term)

        if results:
            st.subheader(f"📂 BP File Results ({len(results)})")
            for idx, fname, url in results:
                st.markdown(f"**{idx}. [{fname}]({url})**")
        else:
            st.warning("No matching BP files found.")
    else:
        # ------------------------------
        # ARTICLE SEARCH
        # ------------------------------
        results = search_articles(query)

        if results:
            st.subheader(f"📑 Article Results ({len(results)})")
            for idx, article in results:
                st.markdown(f"**Article {idx} — Keywords:** {', '.join(article['keywords'])}")
        else:
            st.warning("No matching articles found.")
