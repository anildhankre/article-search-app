import os
import re
import requests
import streamlit as st

# -------------------------------
# Load GitHub Token from secrets
# -------------------------------
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# -------------------------------
# Repo Info
# -------------------------------
ARTICLE_FILE = "articles.txt"  # keep this file in the repo
BP_REPO = "anildhankre/Kinaxis-BestPractices"
BP_BRANCH = "main"
BP_PATH = ""   # root folder of PDFs

# -------------------------------
# Load Articles
# -------------------------------
def load_articles():
    try:
        with open(ARTICLE_FILE, "r", encoding="utf-8") as f:
            text = f.read()
        # split on common separators (-----, =====, ````)
        articles = re.split(r'`{5,}|={5,}|-{5,}', text)
        # clean out junk ones
        articles = [a.strip() for a in articles if a.strip() and not set(a.strip()) <= {"`", "-", "="}]
        return articles
    except Exception as e:
        st.warning(f"⚠️ Failed to load articles file: {e}")
        return []

# -------------------------------
# Fetch Best Practices Files from GitHub
# -------------------------------
def fetch_bp_files():
    url = f"https://api.github.com/repos/{BP_REPO}/contents/{BP_PATH}?ref={BP_BRANCH}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        pdfs = [{"name": f["name"], "url": f["download_url"]} for f in data if f["name"].endswith(".pdf")]
        return pdfs
    else:
        st.warning(f"⚠️ Failed to fetch files from GitHub (Status {r.status_code}) → {url}")
        return []

# -------------------------------
# Search in Articles
# -------------------------------
def search_articles(articles, term):
    results = []
    for i, art in enumerate(articles, start=1):
        if term.lower() in art.lower():
            results.append((i, art.strip()[:200] + "..."))
    return results

# -------------------------------
# Search in BP files
# -------------------------------
def search_bp(bp_files, term):
    return [f for f in bp_files if term.lower() in f["name"].lower()]

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📄 Article & Best Practices Search")

# Load data
articles = load_articles()
bp_files = fetch_bp_files()

query = st.text_input("🔍 Enter search term (use `BP:term` for Best Practices files)")

if query.strip().lower() == "show index":
    st.subheader("📑 Index of Articles")
    for i, art in enumerate(articles, start=1):
        st.write(f"**Article {i}** — {art.strip()[:60]}...")

elif query:
    if query.lower().startswith("bp:"):
        term = query[3:].strip()
        st.subheader(f"🔎 Best Practices Search for: {term}")
        results = search_bp(bp_files, term)
        if results:
            for r in results:
                st.markdown(f"- [{r['name']}]({r['url']})")
        else:
            st.info("No matching Best Practice files found.")
    else:
        st.subheader(f"🔎 Article Search for: {query}")
        results = search_articles(articles, query)
        if results:
            for idx, snippet in results:
                st.markdown(f"**Article {idx}:** {snippet}")
        else:
            st.info("No matching articles found.")
else:
    st.write("👉 Type a search term above, or `Show Index` to see all articles.")
