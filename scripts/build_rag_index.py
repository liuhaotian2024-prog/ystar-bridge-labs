#!/usr/bin/env python3.11
"""
build_rag_index.py — Layer 2: RAG vector index for local knowledge retrieval.

Scans markdown files from all three repos (ystar-bridge-labs, Y-star-gov,
gov-mcp), chunks them, embeds via Ollama nomic-embed-text, and stores in
a local ChromaDB collection. local_learn.py queries this index before
calling Gemma, injecting the most relevant chunks into context.

Usage:
  python3.11 scripts/build_rag_index.py                    # full rebuild
  python3.11 scripts/build_rag_index.py --query "CIEU audit"  # test query
  python3.11 scripts/build_rag_index.py --stats            # show index stats
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAG_DIR = Path.home() / ".ystar_rag"
CHROMA_DIR = RAG_DIR / "chroma_db"
OLLAMA_EMBED_MODEL = "nomic-embed-text"
OLLAMA_URL = "http://localhost:11434"
CHUNK_SIZE = 500  # chars per chunk
CHUNK_OVERLAP = 100

# Directories to index from each repo
SCAN_TARGETS = [
    # ystar-bridge-labs
    (REPO_ROOT, [
        "governance/*.md",
        "agents/*.md",
        "knowledge/**/*.md",
        "roadmap/*.md",
        "README.md",
        "reports/cto/*.md",
        "reports/ceo/*.md",
    ]),
    # Y-star-gov
    (REPO_ROOT.parent / "Y-star-gov", [
        "README.md",
        "docs/*.md",
        "docs/development/*.md",
    ]),
    # gov-mcp
    (REPO_ROOT.parent / "gov-mcp", [
        "README.md",
        "docs/*.md",
    ]),
]


def find_files():
    """Collect all markdown files from scan targets."""
    files = []
    for base_dir, patterns in SCAN_TARGETS:
        if not base_dir.exists():
            continue
        for pattern in patterns:
            for f in base_dir.glob(pattern):
                if f.is_file() and f.suffix == ".md" and f.name != "README.md" or f.name == "README.md":
                    files.append(f)
    return files


def chunk_text(text, source_path, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks with metadata."""
    chunks = []
    lines = text.split("\n")
    current_chunk = ""
    current_header = ""

    for line in lines:
        if line.startswith("## "):
            current_header = line.strip("# ").strip()
        current_chunk += line + "\n"

        if len(current_chunk) >= chunk_size:
            chunks.append({
                "text": current_chunk.strip(),
                "source": str(source_path),
                "header": current_header,
                "chunk_id": hashlib.md5(current_chunk.encode()).hexdigest()[:12],
            })
            # Keep overlap
            overlap_lines = current_chunk.split("\n")
            overlap_text = "\n".join(overlap_lines[-3:]) if len(overlap_lines) > 3 else ""
            current_chunk = overlap_text

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "source": str(source_path),
            "header": current_header,
            "chunk_id": hashlib.md5(current_chunk.encode()).hexdigest()[:12],
        })
    return chunks


def get_embedding(text, model=OLLAMA_EMBED_MODEL):
    """Get embedding vector from Ollama."""
    payload = json.dumps({
        "model": model,
        "input": text,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.loads(r.read().decode("utf-8"))
    embeddings = body.get("embeddings", [])
    if embeddings:
        return embeddings[0]
    return None


def build_index():
    """Build the full ChromaDB index from all repos."""
    import chromadb

    RAG_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # Delete old collection if exists
    try:
        client.delete_collection("ystar_knowledge")
    except Exception:
        pass
    collection = client.create_collection(
        name="ystar_knowledge",
        metadata={"hnsw:space": "cosine"},
    )

    files = find_files()
    print(f"Found {len(files)} files to index")

    total_chunks = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if len(text.strip()) < 50:
            continue

        # Make path relative for display
        try:
            rel = f.relative_to(REPO_ROOT.parent)
        except ValueError:
            rel = f

        chunks = chunk_text(text, rel)
        if not chunks:
            continue

        # Batch embed + add
        for chunk in chunks:
            try:
                embedding = get_embedding(chunk["text"][:1000])  # truncate for embed
                if embedding is None:
                    continue
                collection.add(
                    ids=[chunk["chunk_id"]],
                    embeddings=[embedding],
                    documents=[chunk["text"]],
                    metadatas=[{
                        "source": chunk["source"],
                        "header": chunk["header"],
                    }],
                )
                total_chunks += 1
            except Exception as e:
                # Skip duplicate IDs or other errors
                pass

        print(f"  {rel}: {len(chunks)} chunks")

    print(f"\nTotal: {total_chunks} chunks indexed in {CHROMA_DIR}")
    return total_chunks


def query_index(query_text, top_k=5):
    """Query the RAG index and return top-k results."""
    import chromadb

    if not CHROMA_DIR.exists():
        print("ERROR: index not built yet. Run without --query first.", file=sys.stderr)
        return []

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection("ystar_knowledge")

    embedding = get_embedding(query_text)
    if embedding is None:
        print("ERROR: could not get embedding", file=sys.stderr)
        return []

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
    )

    formatted = []
    for i in range(len(results["ids"][0])):
        formatted.append({
            "source": results["metadatas"][0][i].get("source", "?"),
            "header": results["metadatas"][0][i].get("header", ""),
            "text": results["documents"][0][i][:300],
            "distance": results["distances"][0][i] if results.get("distances") else None,
        })
    return formatted


def show_stats():
    """Show index statistics."""
    import chromadb

    if not CHROMA_DIR.exists():
        print("Index not built yet.")
        return

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection("ystar_knowledge")
    count = collection.count()
    print(f"Index: {CHROMA_DIR}")
    print(f"Chunks: {count}")
    print(f"Size: {sum(f.stat().st_size for f in CHROMA_DIR.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")


def main():
    p = argparse.ArgumentParser(description="Build/query RAG index for local knowledge")
    p.add_argument("--query", help="Test query against the index")
    p.add_argument("--top-k", type=int, default=5, help="Number of results (default: 5)")
    p.add_argument("--stats", action="store_true", help="Show index stats")
    args = p.parse_args()

    if args.stats:
        show_stats()
        return 0

    if args.query:
        results = query_index(args.query, args.top_k)
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['source']} :: {r['header']}")
            print(f"    {r['text'][:200]}...")
            if r['distance'] is not None:
                print(f"    distance: {r['distance']:.4f}")
        return 0

    # Full rebuild
    t0 = time.time()
    count = build_index()
    dt = time.time() - t0
    print(f"\nBuilt in {dt:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
