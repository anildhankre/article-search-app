import re
import pathlib
import streamlit as st
from collections import Counter
import string

st.set_page_config(page_title="Article Search", layout="wide")
st.title("📄 Article Search (Shared File)")

# 1) Load file
FILE_PATH = pathlib.Path(__file__).parent / "articles.txt"
if not FILE_PATH.exists():
    st.error("❌ 'articles.txt' not found in the repo.")
    st.stop()

text = FILE_PATH.read_text(encoding="utf-8")

# 2) Split into articles
articles = re.split(r'`{5,}|={5,}|-{5,}', text)
articles = [a.strip() for a in articles if a.strip()]
st.success(f"Loaded {len(articles)} articles from your shared file.")

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
query = st.text_input("🔎 Enter keywords OR type 'Show Index':").strip()

def highlight(snippet: str, q: str) -> str:
    if not q:
        return snippet
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", snippet)

# -----------------
# 🔹 Logic
# -----------------
if query.lower() == "show index":
    st.subheader("📑 Index of Articles")
    for i, article in enumerate(articles, start=1):
        keywords = extract_keywords(article)
        with st.expander(f"Article {i} — Keywords: {', '.join(keywords) if keywords else 'N/A'}"):
            st.markdown(article[:500] + ("..." if len(article) > 500 else ""))  # preview

elif query:
    matched = []
    qlower = query.lower()
    for i, article in enumerate(articles, start=1):
        if qlower in article.lower():
            matched.append((i, article))

    if matched:
        st.subheader(f"Search Results ({len(matched)})")
        for idx, (art_no, body) in enumerate(matched, start=1):
            with st.expander(f"Result {idx} (Article {art_no})"):
                st.markdown(highlight(body, query))
    else:
        st.warning("No results found. Try a different word.")
else:
    st.info("Type keywords to search, or type **Show Index** to view all articles.")
