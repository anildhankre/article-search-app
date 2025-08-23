if results:
    st.subheader("Search Results")
    for idx, (i, res) in enumerate(results, 1):
        with st.expander(f"Result {idx} (Article {i+1})"):
            st.write(res)   # show full article inside expandable box
else:
    st.warning("No results found. Try another word.")
