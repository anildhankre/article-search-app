import os
import re
import requests
import streamlit as st

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
# Highlight Matches
# -------------------------------
def highlight_matches(text, query):
    variations = generate_variations(query)
    for var in sorted(variations, key=len, reverse=True):  # longest first
        pattern = re.compile(re.escape(var), re.IGNORECASE)
        text = pattern.sub(lambda m: f"**:orange-background[{m.group(0)}]**", text)
    return text


# -------------------------------
# Generate Variations (for fuzzy search)
# -------------------------------
def generate_variations(term):
    variations = set()
    term = term.strip()
    variations.add(term)

    # no spaces
    variations.add(term.replace(" ", ""))

    # add spaces before uppercase letters
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", term)
    variations.add(spaced)

    return variations


# -------------------------------
# Normalize (remove spaces/punct for loose matching)
# -------------------------------
def normalize(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


# -------------------------------
# Search in Articles (with scoring)
# -------------------------------
def search_articles(articles, query):
    results = []
    norm_query = normalize(query)
    word_query = query.lower().split()

    for i, art in enumerate(articles, start=1):
        score = 0
        art_lower = art.lower()
        art_norm = normalize(art)

        # 1. Exact phrase match
        if query.lower() in art_lower:
            count = art_lower.count(query.lower())
            score += 5 * count

        # 2. Normalized (ignore spaces/punct) match
        if norm_query in art_norm:
            score += 4

        # 3. All words appear in order
        if all(w in art_lower for w in word_query):
            joined = ".*?".join(map(re.escape, word_query))
            if re.search(joined, art_lower):
                score += 2

        # 4. Frequency boost (each occurrence of words)
        for w in word_query:
            score += art_lower.count(w)

        if score > 0:
            highlighted = highlight_matches(art, query)
            results.append((i, art.strip(), score, highlighted))

    # sort by score descending
    results.sort(key=lambda x: x[2], reverse=True)
    return results


# -------------------------------
# Search in Best Practices
# -------------------------------
def search_bp(bp_files, term):
    return [f for f in bp_files if term.lower() in f["name"].lower()]


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
# Main App (after login)
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
        for idx, full_text, score, highlighted in article_results:
            with st.expander(f"Article {idx} (score: {score})"):
                st.markdown(highlighted, unsafe_allow_html=True)
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
