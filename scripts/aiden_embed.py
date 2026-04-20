#!/usr/bin/env python3
"""
Aiden Embedding Engine — Semantic field generation via nomic-embed-text.

Generates 768-dim embeddings for all brain nodes via local Ollama,
stores them in aiden_brain.db, enables cosine similarity-based activation.

Usage:
    aiden_embed.py              — embed all nodes
    aiden_embed.py --query "X"  — embed query + find semantically similar nodes
"""

import os
import sys
import json
import struct
import math
import time

sys.path.insert(0, os.path.dirname(__file__))
from aiden_brain import get_db, init_db, DB_PATH

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768


def _get_embedding(text: str) -> list:
    import urllib.request
    data = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("embedding", [])
    except Exception as e:
        print(f"  Embedding failed: {e}")
        return []


def _pack_embedding(emb: list) -> bytes:
    return struct.pack(f"{len(emb)}f", *emb)


def _unpack_embedding(data: bytes) -> list:
    n = len(data) // 4
    return list(struct.unpack(f"{n}f", data))


def _cosine_similarity(a: list, b: list) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def ensure_embedding_column():
    conn = get_db()
    cols = [r[1] for r in conn.execute("PRAGMA table_info(nodes)").fetchall()]
    if "embedding" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN embedding BLOB")
        conn.commit()
    conn.close()


def embed_all_nodes(db_path: str = DB_PATH):
    ensure_embedding_column()
    conn = get_db(db_path)
    nodes = conn.execute("SELECT id, name, summary FROM nodes").fetchall()
    embedded = 0
    for node in nodes:
        text = f"{node['name']}. {node['summary'] or ''}"
        emb = _get_embedding(text)
        if emb:
            conn.execute("UPDATE nodes SET embedding=? WHERE id=?",
                         (_pack_embedding(emb), node["id"]))
            embedded += 1
            if embedded % 10 == 0:
                print(f"  Embedded {embedded}/{len(nodes)}...")
    conn.commit()
    conn.close()
    print(f"Embedded {embedded}/{len(nodes)} nodes ({EMBED_DIM}-dim via {EMBED_MODEL})")


def semantic_search(query: str, top_n: int = 10, db_path: str = DB_PATH) -> list:
    """Find nodes semantically similar to query using cosine similarity."""
    q_emb = _get_embedding(query)
    if not q_emb:
        print("Failed to embed query")
        return []

    ensure_embedding_column()
    conn = get_db(db_path)
    nodes = conn.execute(
        "SELECT id, name, summary, file_path, embedding FROM nodes WHERE embedding IS NOT NULL"
    ).fetchall()
    conn.close()

    results = []
    for node in nodes:
        node_emb = _unpack_embedding(node["embedding"])
        sim = _cosine_similarity(q_emb, node_emb)
        results.append((node["id"], node["name"], sim,
                         node["file_path"] or "", node["summary"] or ""))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    if "--query" in sys.argv:
        idx = sys.argv.index("--query")
        query = " ".join(sys.argv[idx + 1:])
        results = semantic_search(query)
        print(f"=== Semantic Search: '{query}' ===")
        for nid, name, sim, fpath, summary in results:
            print(f"  [{sim:.3f}] {name[:55]}")
    else:
        print(f"Embedding all brain nodes via {EMBED_MODEL}...")
        embed_all_nodes()
