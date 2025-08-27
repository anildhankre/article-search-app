st.write("✅ App loaded successfully")

import re
import math

def normalize_text(text):
    return re.sub(r'\W+', ' ', text).lower().strip()

def split_camel_case(text):
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', text)

def search_articles(articles, term):
    results = []

    # Split CamelCase and normalize
    words = split_camel_case(term)
    if not words:
        words = [term]
    norm_words = [normalize_text(w) for w in words]
    norm_term = normalize_text(term)

    for i, art in enumerate(articles, start=1):
        lower_art = art.lower()
        norm_art = normalize_text(art)
        score = 0
        freq = 0
        pos_boost = 0

        n = len(words)

        # --- Phrase priority: from longest → shortest ---
        for size in range(n, 0, -1):
            for start in range(0, n - size + 1):
                phrase = " ".join(words[start:start+size]).lower()
                if phrase in lower_art:
                    score += size * 20   # bigger n-gram → higher weight

        # --- Whole term matches ---
        occurrences = lower_art.count(term.lower())
        freq += occurrences
        score += 40 * occurrences

        norm_occurrences = norm_art.count(norm_term)
        freq += norm_occurrences
        score += 20 * norm_occurrences

        # --- Position boost (if in first 3 lines) ---
        summary = art.split("\n", 3)[:3]
        if any(term.lower() in s.lower() for s in summary):
            pos_boost += 1
            score += 10

        # --- Length normalization ---
        length_penalty = math.log(len(art) + 2)

        if score > 0:
            results.append(
                (i, art.strip(), score, freq, pos_boost, length_penalty)
            )

    # ✅ Fixed sorting (no reverse bug now)
    # Sort: score → frequency → position boost → shorter length
    results.sort(
        key=lambda x: (x[2], x[3], x[4], -x[5]),
        reverse=True
    )

    return results
