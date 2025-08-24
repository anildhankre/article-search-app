import re
import pathlib
import requests
import streamlit as st
from collections import Counter
import string

# -------------------------
# 🔐 Security Layer
# -------------------------
st.set_page_config(page_title="Article & Best Practices Search", layout="wide")

# Hardcoded credentials
USERNAME = "SimbusRR"
PASSWORD = "Simbus@2025"

# Session state for login
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_screen():
    st.title("🔒 Secure Login")
    st.write("Please enter your credentials to access the app.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password")

if not st.session_state.authenticated:
    login_screen()
    st.stop()  # 🚫 stop the app until login succeeds

# -------------------------
# 🔹 Main App (after login)
# -------------------------
st.title("📄 Article & Best Practices Search")

# 1) Load articles from local file
FILE_PATH = pathlib.Path(__file__).parent / "articles.txt"
articles = []
if FILE_PATH.exists():
    text = FILE_PATH.read_text(encoding="utf-8")
    articles = re.split(r'`{5,}|={5,}|-{5,}', text)
    articles = [a.strip() for a in articles if a.strip()]
    st.success(f"Loaded {len(articles)} articles from your shared file.")
else:
    st.error("❌ 'articles.txt' not found in the repo.")

# 2) Fetch Best Practices files from GitHub
GITHUB_OWNER = "anildhankre"
GITHUB_REPO = "Kinaxis-BestPractices"
GITHUB_PATH = ""  # root folder
API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{GITHUB_PATH}?ref=main"

bp_files = []
try:
    res = requests.get(API_URL)
    if res.status_code == 200:
        bp_files = [f for f in res.json() if f["name"].endswith(".pdf")]
        st.success(f"Fetched {len(bp_files)} Best Practices PDFs from GitHub.")
    else:
        st.warning(f"⚠️ Failed to fetch files from GitHub (Status {res.status_code}) → {API_URL}")
except Exception as e:
    st.error(f"⚠️ GitHub fetch error: {e}")

# -----------------
# 🔹 Keyword Extractor
# -----------------
def extract_keywords(article: str, top_n: int = 5):
    words = article.lower().translate(str.maketrans("", "", string.punctuation)).split()
    stopwords = {"the", "and", "is", "a", "of", "to", "in", "on", "for", "at", "as", "by", "an", "with", "from"}
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    common = Counter(filtered).most_common(top_n)
    return [w for w, _ in common]

# -----------------
# 🔹 Input box (single entry point)
# -----------------
query = st.text_input("🔍 Enter search term (shows both Articles & Best Practices):").strip()

def highlight(snippet: str, q: str) -> str:
    if not q:
        return snippet
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", snippet)

# -----------------
# 🔹 Search Logic
# -----------------
if query.lower() == "show index":
    st.subheader("📑 Index of Articles")
    for i, article in enumerate(articles, start=1):
        keywords = extract_keywords(article)
        with st.expander(f"Article {i} — Keywords: {', '.join(keywords) if keywords else 'N/A'}"):
            st.markdown(article[:1000] + ("..." if len(article) > 1000 else ""))  # longer preview

elif query:
    # Article search
    matched_articles = [(i, a) for i, a in enumerate(articles, start=1) if query.lower() in a.lower()]
    
    # BP search
    matched_bp = [f for f in bp_files if query.lower() in f["name"].lower()]
    
    # Show results
    if matched_articles:
        st.subheader(f"📄 Article Results ({len(matched_articles)})")
        for idx, (art_no, body) in enumerate(matched_articles, start=1):
            with st.expander(f"Result {idx} (Article {art_no})"):
                st.markdown(highlight(body, query))

    if matched_bp:
        st.subheader(f"📘 Best Practices Results ({len(matched_bp)})")
        for f in matched_bp:
            file_url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/main/{f['name']}?raw=true"
            st.markdown(f"- [{f['name']}]({file_url})")

    if not matched_articles and not matched_bp:
        st.warning("No results found. Try a different word.")
else:
    st.info("Type keywords to search, or type **Show Index** to view all articles.")
