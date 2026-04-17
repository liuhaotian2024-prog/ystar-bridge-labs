#!/usr/bin/env python3
"""
wisdom_search.py — CEO Wisdom Semantic Search (TF-IDF)

Usage:
    python3 scripts/wisdom_search.py "知行合一"
    python3 scripts/wisdom_search.py "how to make decisions under uncertainty"
    python3 scripts/wisdom_search.py --top 5 "structure vs discipline"

Design decision (CTO CZL-157):
    TF-IDF with character n-grams (2,4) chosen over:
    - Simple grep: no synonym/semantic proximity handling
    - Embedding vectors: requires external model/API, violates lightweight constraint
    Character n-grams handle mixed Chinese+English text well because
    Chinese bigrams naturally capture meaningful word units.
"""

import argparse
import os
import re
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

WISDOM_ROOT = Path(__file__).resolve().parent.parent / "knowledge" / "ceo" / "wisdom"


def discover_wisdom_files(root: Path) -> list[Path]:
    """Recursively find all .md files under wisdom root, excluding index files."""
    exclude = {"WISDOM_INDEX.md", "WHO_I_AM.md"}
    files = []
    for p in sorted(root.rglob("*.md")):
        if p.name not in exclude:
            files.append(p)
    return files


def parse_wisdom_file(path: Path) -> dict:
    """Extract structured fields from a wisdom .md file.

    Returns dict with keys: path, name, type, body, full_text (for indexing).
    """
    text = path.read_text(encoding="utf-8")

    # Parse YAML frontmatter
    name = ""
    wtype = ""
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        type_m = re.search(r"^type:\s*(.+)$", fm, re.MULTILINE)
        if name_m:
            name = name_m.group(1).strip()
        if type_m:
            wtype = type_m.group(1).strip()

    # Body = everything after frontmatter
    body = text
    if fm_match:
        body = text[fm_match.end():].strip()

    # If no name in frontmatter, derive from filename
    if not name:
        name = path.stem.replace("_", " ").title()

    # full_text combines name + body for richer matching
    full_text = f"{name}\n{body}"

    return {
        "path": path,
        "rel_path": str(path.relative_to(WISDOM_ROOT)),
        "name": name,
        "type": wtype,
        "body": body,
        "full_text": full_text,
    }


def build_index(entries: list[dict]) -> tuple:
    """Build TF-IDF index from wisdom entries.

    Uses character n-grams (2,4) to handle Chinese+English mixed text.
    Also adds word-level unigrams/bigrams for English phrase matching.
    """
    corpus = [e["full_text"] for e in entries]

    # Character n-grams: captures Chinese bigrams naturally
    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        max_features=8000,
        sublinear_tf=True,
    )
    char_matrix = char_vectorizer.fit_transform(corpus)

    # Word n-grams: captures English phrases
    word_vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
        token_pattern=r"(?u)\b\w+\b",  # single-char tokens OK for Chinese
    )
    word_matrix = word_vectorizer.fit_transform(corpus)

    return char_vectorizer, char_matrix, word_vectorizer, word_matrix


def search(
    query: str,
    entries: list[dict],
    char_vectorizer,
    char_matrix,
    word_vectorizer,
    word_matrix,
    top_n: int = 3,
) -> list[tuple[dict, float]]:
    """Search wisdom entries for query, return top_n results with scores."""
    # Transform query through both vectorizers
    q_char = char_vectorizer.transform([query])
    q_word = word_vectorizer.transform([query])

    # Compute similarities (weighted blend: 0.6 char + 0.4 word)
    char_sim = cosine_similarity(q_char, char_matrix).flatten()
    word_sim = cosine_similarity(q_word, word_matrix).flatten()
    combined = 0.6 * char_sim + 0.4 * word_sim

    # Boost entries that contain exact query substrings
    for i, entry in enumerate(entries):
        text_lower = entry["full_text"].lower()
        query_lower = query.lower()
        if query_lower in text_lower:
            combined[i] *= 1.5  # 50% boost for exact substring match

    # Get top_n indices
    top_indices = combined.argsort()[::-1][:top_n]

    results = []
    for idx in top_indices:
        if combined[idx] > 0.0:
            results.append((entries[idx], float(combined[idx])))

    return results


def format_results(results: list[tuple[dict, float]], query: str) -> str:
    """Format search results for human reading."""
    if not results:
        return f"No wisdom entries found matching: '{query}'"

    lines = [f"Query: \"{query}\"", f"Top {len(results)} matches:", ""]

    for rank, (entry, score) in enumerate(results, 1):
        lines.append(f"  [{rank}] {entry['name']}")
        lines.append(f"      Path: {entry['rel_path']}")
        lines.append(f"      Type: {entry['type'] or 'unknown'}")
        lines.append(f"      Score: {score:.4f}")
        # Show first 120 chars of body as preview
        preview = entry["body"][:120].replace("\n", " ").strip()
        if len(entry["body"]) > 120:
            preview += "..."
        lines.append(f"      Preview: {preview}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search CEO wisdom entries by semantic similarity"
    )
    parser.add_argument("query", help="Search query (Chinese or English)")
    parser.add_argument(
        "--top", type=int, default=3, help="Number of results (default: 3)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    args = parser.parse_args()

    # Discover and parse wisdom files
    files = discover_wisdom_files(WISDOM_ROOT)
    if not files:
        print(f"ERROR: No wisdom files found under {WISDOM_ROOT}", file=sys.stderr)
        sys.exit(1)

    entries = [parse_wisdom_file(f) for f in files]

    # Build index
    char_vec, char_mat, word_vec, word_mat = build_index(entries)

    # Search
    results = search(
        args.query, entries, char_vec, char_mat, word_vec, word_mat, top_n=args.top
    )

    # Output
    if args.json:
        import json

        out = []
        for entry, score in results:
            out.append(
                {
                    "name": entry["name"],
                    "path": entry["rel_path"],
                    "type": entry["type"],
                    "score": round(score, 4),
                }
            )
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(format_results(results, args.query))


if __name__ == "__main__":
    main()
