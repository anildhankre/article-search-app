import re
import pathlib
import streamlit as st
from collections import Counter
import string
import requests

st.set_page_config(page_title="Article Search", layout="wide")
st.title("📄 Article & Best Practices Search")

# =================================================
# 1) Load Articles (from articles.txt in repo)
# =================================================
FILE_PATH = pathlib.Path(__file__).parent / "articles.txt"
if not FILE_PATH.exists():
    st.error("❌ 'articles.txt' not found in the repo.")
    st.stop()

text = FILE_PATH.read_text(encoding="utf-8")

# Split into articles
articles = re.split(r'`{5,}|={5,}|-{5,}', text)
articles = [a.strip() for a in articles if a.strip()]
st.success(f"Loaded {len(articles)} articles from your shared file.")

# =================================================
# 2) Fetch Best Practices (PDFs) from GitHub
# =================================================
@st.cache_data
def fetch_bp_files():
    url = "https://api.github.com/repos/anildhankre/Kinaxis-BestPractices/contents/?ref=main"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            return [
                {
                    "name": f["name"],
                    "url": f["html_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                }
                for f in data if f["name"].lower().endswith(".pdf")
            ]
        else:
            st.error(f"⚠️ Failed to fetch files from GitHub (Status {res.status_code}) → {url}")
            return []
    except Exception as e:
        st.error(f"⚠️ Error fetching BP files: {e}")
        return []

bp_files = fetch_bp_files()

# =================================================
# 3) Keyword Extractor
# =================================================
def extract_keywords(article: str, top_n: int = 5):
    words = article.lower().translate(str.maketrans("", "", string.punctuation)).split()
    stopwords = {"the", "and", "is", "a", "of", "to", "in", "on", "for", "at", "as", "by", "an", "with", "from"}
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    common = Counter(filtered).most_common(top_n)
    return [w for w, _ in common]

# =================================================
# 4) Highlight Helper
# =================================================
def highlight(snippet: str, q: str) -> str:
    if not q:
        return snippet
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", snippet)

# =================================================
# 5) Input (single entry)
# =================================================
query = st.text_input("🔎 Enter keywords OR type 'Show Index':").strip()

# =================================================
# 6) Logic
# =================================================
if query.lower() == "show index":
    st.subheader("📑 Index of Articles")
    for i, article in enumerate(articles, start=1):
        keywords = extract_keywords(article)
        with st.expander(f"Article {i} — Keywords: {', '.join(keywords) if keywords else 'N/A'}"):
            st.markdown(article[:500] + ("..." if len(article) > 500 else ""))  # preview

    st.subheader("📑 Index of Best Practices (PDFs)")
    for i, f in enumerate(bp_files, 1):
        st.markdown(f"- [BP File {i} — {f['name']}]({f['url']})")

elif query:
    matched_articles = []
    matched_pdfs = []

    qlower = query.lower()

    # --- Search Articles ---
    for i, article in enumerate(articles, start=1):
        if qlower in article.lower():
            matched_articles.append((i, article))

    # --- Search PDF file names ---
    for f in bp_files:
        if qlower in f["name"].lower():
            matched_pdfs.append(f)

    # --- Show Results ---
    if matched_articles or matched_pdfs:
        st.subheader(f"Search Results ({len(matched_articles)} Articles + {len(matched_pdfs)} PDFs)")

        # Article results
        for idx, (art_no, body) in enumerate(matched_articles, start=1):
            with st.expander(f"Article Result {idx} (Article {art_no})"):
                st.markdown(highlight(body, query))

        # PDF results
        if matched_pdfs:
            st.markdown("### 📂 Matching Best Practice PDFs")
            for f in matched_pdfs:
                st.markdown(f"- [{highlight(f['name'], query)}]({f['url']})")
    else:
        st.warning("No results found in either Articles or PDFs. Try a different word.")

else:
    st.info("Type keywords to search, or type **Show Index** to view all articles & PDFs.")
