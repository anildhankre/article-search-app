def search_articles(articles, term):
    results = []

    # split query into words (CamelCase-aware)
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

        # --- Priority Hierarchy (generalized for any number of words) ---
        n = len(words)
        found_priority = False

        # Check from longest n-gram down to 1
        for size in range(n, 0, -1):
            for start in range(0, n - size + 1):
                phrase = " ".join(words[start:start+size]).lower()
                if phrase in lower_art:
                    score += size * 20   # bigger n-gram → more score
                    found_priority = True

        # --- Whole Term Matches (non-split version) ---
        occurrences = lower_art.count(term.lower())
        freq += occurrences
        score += 40 * occurrences

        norm_occurrences = norm_art.count(norm_term)
        freq += norm_occurrences
        score += 20 * norm_occurrences

        # --- Boost if term appears early ---
        summary = art.split("\n", 3)[:3]
        if any(term.lower() in s.lower() for s in summary):
            pos_boost += 1
            score += 10

        # --- Length normalization ---
        from math import log
        length_penalty = log(len(art) + 2)

        if score > 0:
            results.append(
                (i, art.strip(), score, freq, pos_boost, length_penalty)
            )

    # Multi-key sort:
    results.sort(
        key=lambda x: (x[2], x[3], x[4], -x[5]),
        reverse=True
    )

    return results
