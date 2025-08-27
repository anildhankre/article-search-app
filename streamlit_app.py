import os
import re
import requests
import streamlit as st
from math import log

# -------------------------------
# Login Credentials
# -------------------------------
VALID_USERNAME = "SimbusRR"
VALID_PASSWORD = "Simbus@2025"

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
# Normalize Text Helper
# -------------------------------
def normalize_text(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


# -------------------------------
# Split CamelCase (PascalCase)
# -------------------------------
def split_camel_case(word):
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', word)


# -------------------------------
# Search in Articles with Scoring
# -------------------------------
def search_articles(articles, term):
    results = []

    # split query into words and also break CamelCase
    words = []
    for w in term.split():
        words.extend(split_camel_case(w))
    words = list(set(words + [term]))  # keep original term too
    norm_words = [normalize_text(w) for w in words]
    norm_term = normalize_text(term)

    for i, art in enumerate(articles, start=1):
        lower_art = art.lower()
        norm_art = normalize_text(art)

        score = 0

        # 1. Full exact match
        occurrences = lower_art.count(term.lower())
        if occurrences > 0:
            score += 5 * occurrences

        # 2. Normalized contiguous match
        norm_occurrences = norm_art.count(norm_term)
        if norm_occurrences > 0:
            score += 4 * norm_occurrences

        # 3. Individual word matches (including CamelCase parts)
        for w, nw in zip(words, norm_words):
            occ = lower_art.count(w.lower())
            nocc = norm_art.count(nw)
            score += 2 * occ + nocc

        # 4. Boost if all words found
        if all(w.lower() in lower_art for w in words):
            score += 10

        # 5. Boost if term in first 3 lines
        summary = art.split("\n", 3)[:3]
        if any(term.lower() in s.lower() for s in summary):
            score += 3

        adj_score = score / log(len(art) + 2)

        if score > 0:
            results.append((i, art.strip(), adj_score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results


# -------------------------------
# Search in Best Practices
# -------------------------------
def search_bp(bp_files, term):
    return [f for f in bp_files if term.lower() in f["name"].lower()]


# -------------------------------
# Underline Matches
# -------------------------------
def underline_matches(text, query):
    # split into words & also handle CamelCase
    words = []
    for w in query.split():
        words.extend(split_camel_case(w))
    words = list(set(words + [query]))

    for t in words:
        pattern = re.compile(re.escape(t), re.IGNORECASE)
        text = pattern.sub(lambda m: f"<u>{m.group(0)}</u>", text)
    return text


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
    st.stop()  # stop rest of app until logged in


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
        for idx, full_text, _ in article_results:
            with st.expander(f"Article {idx} (click to expand)"):
                st.markdown(underline_matches(full_text, query), unsafe_allow_html=True)
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
