import os
import re
import requests
import streamlit as st
import openai

# -------------------------------
# Login Credentials
# -------------------------------
VALID_USERNAME = "SimbusRR"
VALID_PASSWORD = "Simbus@2025"

# -------------------------------
# OpenAI Setup
# -------------------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
        articles = re.split(r'`{5,}|={5,}|-{5,}', text)
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
# Normalize search terms
# -------------------------------
def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())

# -------------------------------
# Search in Articles
# -------------------------------
def search_articles(articles, term):
    results = []
    norm_term = normalize(term)
    for i, art in enumerate(articles, start=1):
        norm_art = normalize(art)
        if norm_term in norm_art:
            highlighted = re.sub(
                f"(?i)({re.escape(term)})",
                r"**\1**",
                art,
                flags=re.IGNORECASE
            )
            results.append((i, highlighted.strip()))
    return results

# -------------------------------
# Search in Best Practices
# -------------------------------
def search_bp(bp_files, term):
    return [f for f in bp_files if term.lower() in f["name"].lower()]

# -------------------------------
# Ask ChatGPT with context
# -------------------------------
def ask_chatgpt(context_text, query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Use the provided context from articles.txt to answer user queries."},
                {"role": "user", "content": f"Context:\n{context_text[:15000]}\n\nQuestion: {query}\n\nAnswer based only on the context above."}
            ],
            max_tokens=400,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"⚠️ ChatGPT request failed: {e}"

# -------------------------------
# Login Page
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Login successful! Please continue.")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
    st.stop()

# -------------------------------
# Main App (only after login)
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
                st.markdown(full_text, unsafe_allow_html=True)
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

    # --- ChatGPT Answer ---
    if article_results:
        st.markdown("### 🤖 ChatGPT Answer (from articles.txt)")
        context_text = "\n\n".join(a for _, a in article_results)
        answer = ask_chatgpt(context_text, query)
        st.write(answer)

else:
    st.write("👉 Type a search term above, or `Show Index` to see all articles.")
