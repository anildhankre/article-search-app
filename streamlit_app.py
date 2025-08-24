import streamlit as st
import requests
import pandas as pd

# ========================
# 🔐 Authentication
# ========================
VALID_USERNAME = "SimbusRR"
VALID_PASSWORD = "Simbus@2025"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_screen():
    st.title("🔒 Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

# ========================
# 📂 App Content
# ========================
def app_content():
    st.title("📄 Article & Best Practices Search")

    # Load Articles from CSV
    try:
        articles_df = pd.read_csv("articles.csv")  # replace with your articles file
        st.success(f"✅ Loaded {len(articles_df)} articles from your shared file.")
    except Exception as e:
        st.error(f"⚠️ Failed to load articles: {e}")
        articles_df = pd.DataFrame()

    # Load Best Practices from GitHub
    BP_REPO = "anildhankre/Kinaxis-BestPractices"
    BP_FOLDER = ""  # 🔹 change this if PDFs are inside a subfolder (e.g. "docs")
    BP_API_URL = f"https://api.github.com/repos/{BP_REPO}/contents/{BP_FOLDER}?ref=main"

    def load_best_practices():
        try:
            response = requests.get(BP_API_URL)
            if response.status_code == 200:
                files = response.json()
                return [f for f in files if f["name"].endswith(".pdf")]
            else:
                st.warning(f"⚠️ Failed to fetch files from GitHub (Status {response.status_code}) → {BP_API_URL}")
                return []
        except Exception as e:
            st.error(f"⚠️ Error fetching best practices: {e}")
            return []

    best_practice_files = load_best_practices()

    # 🔍 Search Input
    search_term = st.text_input("🔍 Enter search term")

    if search_term:
        st.subheader(f"🔎 Search Results for: {search_term}")

        # --- Articles Search
        if not articles_df.empty:
            article_results = articles_df[
                articles_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
            ]
            if not article_results.empty:
                st.markdown("### 📑 Articles")
                for _, row in article_results.iterrows():
                    st.markdown(f"**{row['Title']}** — {row['Summary']}")
            else:
                st.info("No matching articles found.")

        # --- Best Practices Search
        if best_practice_files:
            bp_results = [f for f in best_practice_files if search_term.lower() in f["name"].lower()]
            if bp_results:
                st.markdown("### 📘 Best Practices")
                for f in bp_results:
                    st.markdown(f"- [{f['name']}]({f['download_url']})")
            else:
                st.info("No matching best practices found.")

# ========================
# 🚀 Main App Flow
# ========================
if not st.session_state.authenticated:
    login_screen()
else:
    app_content()
