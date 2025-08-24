import re
import pathlib
import streamlit as st
from collections import Counter
import string
import requests

# -----------------------
# 🔐 Security (Login)
# -----------------------
st.set_page_config(page_title="Article & Best Practices Search", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "SimbusRR" and password == "Simbus@2025":
            st.session_state.authenticated = True
            st.success("✅ Login successful! Please reload the page.")
            st.stop()
        else:
            st.error("❌ Invalid credentials")
            st.stop()

# -----------------------
# 📄 Load Articles
# -----------------------
st.title("📄 Article & Best Practices Search")

FILE_PATH = pathlib.Path(__file__).parent / "articles.txt"
if not FILE_PATH.exists():
    st.error("❌ 'articles.txt' not found in the repo.")
    st.stop()

text = FILE_PATH.read_text(encoding="utf-8")

# Better splitting: avoid blank/garbage articles
articles = re.split(r'\n={3,}\n|\n-{3,}\n|\n`{3,}\n', text)
articles = [a.strip() for a in articles if a.strip() and len(a.strip()) > 30]

st.success(f"Loaded {len(articles)} articles from your shared file.")

# -----------------------
# 📂 Load Best Practices PDFs from GitHub
# -----------------------
GITHUB_OWNER = "anildhankre"
GITHUB_REPO = "Kinaxis-BestPractices"
GITHUB_PATH = ""   # 👈 if PDFs are inside a subfolder, put folder name here (e.g. "BestPractices")

API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{GITHUB_PATH}?ref=main"

bp_files = []
try:
    res = requests.get(API_URL)
    if res.status_code == 200:
        data = res.json()
        bp_files = [
            {
                "name": f["name"],
                "url": f["html_url"]
            }
            for f in data if f["name"].lower().endswith(".pdf")
        ]
        st.success(f"Fetched {len(bp_files)} Best Practices PDFs from GitHub.")
    else:
        st.warning(f"⚠️ Failed to fetch files from GitHub (Status {res.status_code}) → {API_URL}")
except Exception as e:
    st.warning(f"⚠️ GitHub fetch error: {e}")

# -----------------------
# 🔹 Keyword Extractor
# -----------------------
def extract_keywords(article: str, top_n: int = 5):
    words = article.lower().translate(str.maketrans("", "", string.punctuation)).split()
    stopwords = {"the", "and", "is", "a", "of", "to", "in", "on", "for", "at", "as", "by", "an", "with", "from"}
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    common = Counter(filtered).most_common(top_n)
    return [w for w, _ in common]

def highlight(snippet: str, q: str) -> str:
    if not q:
        return snippet
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", snippet)

# -----------------------
# 🔎 Input
# -----------------------
query = st.text_input("🔎 Enter keywords or type 'Show Index':").strip()

# -----------------------
# 📑 Logic
# -----------------------
if query.lower() == "show index":
    st.subheader("📑 Index of Articles")
    for i, article in enumerate(articles, start=1):
        keywords = extract_keywords(article)
        with st.expander(f"Article {i} — Keywords: {', '.join(keywords) if keywords else 'N/A'}"):
            st.markdown(article)

elif query:
    # Search in Articles
    matched_articles = []
    qlower = query.lower()
    for i, article in enumerate(articles, start=1):
        if qlower in article.lower():
            matched_articles.append((i, article))

    # Search in Best Practices filenames
    matched_bp = [f for f in bp_files if qlower in f["name"].lower()]

    # Show results
    if matched_articles or matched_bp:
        st.subheader(f"🔎 Search Results for: {query}")

        # Articles section
        if matched_articles:
            st.markdown("### 📄 Articles")
            for idx, (art_no, body) in enumerate(matched_articles, start=1):
                with st.expander(f"Article {art_no}"):
                    st.markdown(highlight(body, query))

        # Best Practices section
        if matched_bp:
            st.markdown("### 📚 Best Practices PDFs")
            for f in matched_bp:
                st.markdown(f"- [{f['name']}]({f['url']})")

    else:
        st.warning("No results found. Try a different word.")
else:
    st.info("Type keywords to search, or type **Show Index** to view all articles.")
