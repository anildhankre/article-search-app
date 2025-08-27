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
ARTICLE_FILE = "articles.txt"
BP_REPO = "anildhankre/Kinaxis-BestPractices"
BP_BRANCH = "main"
BP_PATH = ""


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
# Normalize Text
# -------------------------------
def normalize_text(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


# -------------------------------
# Split CamelCase
# -------------------------------
def split_camel_case(word):
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', word)


# -------------------------------
# Search in Articles
# -------------------------------
def search_articles(articles, term):
    results = []

    # split query into words (CamelCase-aware)
    words = split_camel_case(term)
    if not words:
        words = [term]
    norm_words = [normalize_text(w) for w in words]
    norm_term = normalize_text(term)

    for i, art in enumerate(articles, start=1):
        lower_art = art.lower()
        norm_art = normalize_text(art)
        score = 0
        freq = 0
        pos_boost = 0

        # --- Priority Hierarchy ---
        if all(w.lower() in lower_art for w in words):
            score += 50
        if len(words) >= 2 and all(w.lower() in lower_art for w in words[:2]):
            score += 30
        if len(words) >= 2 and all(w.lower() in lower_art for w in words[-2:]):
            score += 20
        for w in words:
            if w.lower() in lower_art:
                score += 5

        # --- Whole Term Matches ---
        occurrences = lower_art.count(term.lower())
        freq += occurrences
        score += 40 * occurrences

        norm_occurrences = norm_art.count(norm_term)
        freq += norm_occurrences
        score += 20 * norm_occurrences

        # --- Boost if term appears early ---
        summary = art.split("\n", 3)[:3]
        if any(term.lower() in s.lower() for s in summary):
            pos_boost += 1
            score += 10

        # --- Length normalization ---
        length_penalty = log(len(art) + 2)

        if score > 0:
            results.append(
                (i, art.strip(), score, freq, pos_boost, length_penalty)
            )

    # Multi-key sort:
    # 1. Score (desc)
    # 2. Frequency count (desc)
    # 3. Position boost (desc)
    # 4. Length normalization (asc)
    results.sort(
        key=lambda x: (x[2], x[3], x[4], -x[5]),
        reverse=True
    )

    return results


# -------------------------------
# Search Best Practices
# -------------------------------
def search_bp(bp_files, term):
    return [f for f in bp_files if term.lower() in f["name"].lower()]


# -------------------------------
# Underline Matches
# -------------------------------
def underline_matches(text, query):
    words = split_camel_case(query)
    if not words:
        words = [query]
    words.append(query)  # also underline whole term
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
    st.stop()


# -------------------------------
# Main App
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

    article_results = search_articles(articles, query)
    if article_results:
        st.markdown("### 📚 Articles")
        for idx, full_text, _, _, _, _ in article_results:
            with st.expander(f"Article {idx} (click to expand)"):
                st.markdown(underline_matches(full_text, query), unsafe_allow_html=True)
    else:
        st.info("No matching articles found.")

    bp_results = search_bp(bp_files, query)
    if bp_results:
        st.markdown("### 📘 Best Practices")
        for r in bp_results:
            st.markdown(f"- [{r['name']}]({r['url']})")
    else:
        st.info("No matching Best Practice files found.")

else:
    st.write("👉 Type a search term above, or `Show Index` to see all articles.")
