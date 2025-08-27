import os
import re
import requests
import streamlit as st
from openai import OpenAI

# -------------------------------
# Login Credentials
# -------------------------------
VALID_USERNAME = "SimbusRR"
VALID_PASSWORD = "Simbus@2025"

# -------------------------------
# OpenAI Client (ChatGPT)
# -------------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
        return text, articles
    except Exception as e:
        st.warning(f"⚠️ Failed to load articles file: {e}")
        return "", []

# -------------------------------
# Fetch Best Practices Files
# -------------------------------
def fetch_bp_files():
    url = f"https://api.github.com/repos/{BP_REPO}/contents/{BP_PATH}?ref={BP_BRANCH}"
    r = requests.get(url)
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
    variations = generate_variations(term)

    for i, art in enumerate(articles, start=1):
        art_lower = art.lower()
        # also normalize article text by removing spaces
        art_no_space = art_lower.replace(" ", "")
        if any(v in art_lower or v in art_no_space for v in variations):
            results.append((i, art.strip()))
    return results

# -------------------------------
# Search in Best Practices
# -------------------------------
def search_bp(bp_files, term):
    return [f for f in bp_files if term.lower() in f["name"].lower()]

# -------------------------------
# Generate Variations
# -------------------------------
def generate_variations(term):
    variations = {term.lower()}
    # Add spaced version (CamelCase → words)
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', term).lower()
    variations.add(spaced)
    # Add condensed version (remove spaces)
    condensed = term.replace(" ", "").lower()
    variations.add(condensed)
    return variations

# -------------------------------
# Highlight Matches
# -------------------------------
def highlight_text(text, term):
    variations = generate_variations(term)
    for v in variations:
        if not v.strip():
            continue
        regex = re.compile(re.escape(v), re.IGNORECASE)
        text = regex.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
    return text

# -------------------------------
# Ask ChatGPT
# -------------------------------
def ask_chatgpt(context_text, query):
    """Send query + articles.txt to ChatGPT and return answer."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # fast + cheap
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Use the provided context from articles.txt to answer user queries."},
                {"role": "user", "content": f"Context:\n{context_text[:15000]}\n\nQuestion: {query}\n\nAnswer based only on the context above."}
            ],
            max_tokens=400,
        )
        return response.choices[0].message.content
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
    st.stop()  # stop rest of app until logged in

# -------------------------------
# Main App (only after login)
# -------------------------------
st.title("📄 Article & Best Practices Search + ChatGPT")

context_text, articles = load_articles()
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
                highlighted = highlight_text(full_text, query)
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

    # --- ChatGPT Answer ---
    st.markdown("### 🤖 ChatGPT Answer")
    gpt_answer = ask_chatgpt(context_text, query)
    st.write(gpt_answer)

else:
    st.write("👉 Type a search term above, or `Show Index` to see all articles.")
