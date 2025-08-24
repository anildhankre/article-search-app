import streamlit as st
import requests
import os
import json

# -------------------------------
# ✅ Login Credentials
# -------------------------------
VALID_USERNAME = "SimbusRR"
VALID_PASSWORD = "Simbus@2025"

# -------------------------------
# 🔑 Login Screen
# -------------------------------
def login_screen():
    st.title("🔒 Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
            st.rerun()   # go to main app
        else:
            st.error("❌ Invalid username or password")

# -------------------------------
# 📄 Load Articles from JSON file
# -------------------------------
def load_articles():
    try:
        with open("articles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# -------------------------------
# 📑 Fetch Best Practices from GitHub
# -------------------------------
def fetch_best_practices():
    url = "https://api.github.com/repos/anildhankre/Kinaxis-BestPractices/contents/?ref=main"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.warning(f"⚠️ Failed to fetch files from GitHub (Status {response.status_code}) → {url}")
        return []

# -------------------------------
# 🔍 Search Function
# -------------------------------
def search_articles_and_bp(query, articles, bp_files):
    results = []

    # Search Articles
    for idx, art in enumerate(articles, start=1):
        if query.lower() in art.get("summary", "").lower() or query.lower() in art.get("resolution", "").lower():
            results.append(f"📄 Article {idx}: {art.get('summary', 'No summary')}")

    # Search Best Practices
    for file in bp_files:
        if query.lower() in file["name"].lower():
            results.append(f"📘 Best Practice: [{file['name']}]({file['html_url']})")

    return results

# -------------------------------
# 🏠 Main Application
# -------------------------------
def main_app():
    st.title("📄 Article & Best Practices Search")

    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

    # Load Articles
    articles = load_articles()
    if articles:
        st.success(f"✅ Loaded {len(articles)} articles from your shared file.")
    else:
        st.error("❌ No articles found. Please upload or check articles.json")

    # Load Best Practices from GitHub
    bp_files = fetch_best_practices()

    # Search box
    query = st.text_input("🔍 Enter search term (searches both Articles & Best Practices)")
    if query:
        results = search_articles_and_bp(query, articles, bp_files)
        if results:
            st.subheader("🔎 Search Results")
            for r in results:
                st.markdown(r, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No matching results found.")

# -------------------------------
# 🚀 App Execution
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_screen()
else:
    main_app()
