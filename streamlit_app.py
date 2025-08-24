import re
import pathlib
import streamlit as st

st.set_page_config(page_title="Article Search", layout="wide")
st.title("📄 Article Search (Shared File)")

# 1) Read your shared file that sits in the same repo
FILE_PATH = pathlib.Path(__file__).parent / "articles.txt"
if not FILE_PATH.exists():
    st.error("❌ 'articles.txt' not found in the repo (same folder as streamlit_app.py).")
    st.stop()

text = FILE_PATH.read_text(encoding="utf-8")

# 2) Split into articles by your delimiters: ```````````, ==========, -------
articles = re.split(r'`{5,}|={5,}|-{5,}', text)
articles = [a.strip() for a in articles if a.strip()]

st.success(f"Loaded {len(articles)} articles from your shared file.")

# 3) Search box
query = st.text_input("🔎 Enter keywords (case-insensitive):").strip()

def highlight(snippet: str, q: str) -> str:
    if not q:
        return snippet
    # simple case-insensitive bold highlight
    pattern = re.compile(re.escape(q), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", snippet)

if query:
    # 4) Keyword search
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
    st.info("Type something above to search your shared knowledge base.")
