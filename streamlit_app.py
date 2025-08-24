import os
import re
import requests
import streamlit as st

# -------------------------------
# GitHub Auth (optional)
# -------------------------------
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# -------------------------------
# Repo Info
# -------------------------------
ARTICLE_FILE = "articles.txt"  # keep in repo
BP_REPO = "anildhankre/Kinaxis-BestPractices"
BP_BRANCH = "main"
BP_PATH = ""   # folder where PDFs live

# -------------------------------
# Load Articles
# -------------------------------
def load_articles():
    try:
        with open(ARTICLE_FILE, "r", encoding="utf-8") as f:
            text = f.read()
        # split by lines of -----, =====, or backticks
        articles = re.split(r'`{5,}|={5,}|-{5,}', text)
        # clean junk
        articles = [a.strip() for a in articles if a.strip() and not set(a.strip()) <= {"`", "-", "="}]
        return articles
    except Exception as e:
        st.warning(f"⚠️ Failed to load articles file: {e}")
        return []

# -------------------------------
# Fetch Best Practices Files
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
            results.append((i, art.strip()))
    return results

# -------------------------------
# Search in Best Practices
# -------------------------------
def search_bp(bp_files, term):
    return [f for f in bp_files if term.lower() in f["name"].lower()]

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("📄 Article & Best Practices Search")

articles = load_articles()
bp_files = fetch_bp_files()

query = st.text_input("🔍 Enter search term (or type `Show Index` to see all articles)")

if query.strip().lower() == "show index":
    st.subheader("📑 Index of Articles")
    for i, art in enumerate(articles, start=1):
        st.write(f"**Article {i}** — {art.strip()[:80]}...")

elif query:
    st.subheader(f"🔎 Search results for: {query}")

    # --- Articles ---
    article_results = search_articles(articles, query)
    if article_results:
        st.markdown("### 📚 Articles")
        for idx, full_text in article_results:
            with st.expander(f"Article {idx} (click to expand)"):
                st.markdown(full_text)
    else:
        st.info("No matching articles found.")

    # --- Best Practices ---
    bp_results = search_bp(bp_files, query)
    if bp_results:
        st.markdown("### 📘 Best Practices")
        for r in bp_results:
            st.markdown(f"- [{r['name']}]({r['url']})")
    else:
        st.info("No matching Best Practice files found.")

else:
    st.write("👉 Type a search term above, or `Show Index` to see all articles.")
