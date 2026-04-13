#!/usr/bin/env python3
"""Labs RAG Query — Semantic layer for Y* Bridge Labs knowledge retrieval

Builds on Maya's wisdom_extractor_v2 weighted scoring (time × Board × role).
Extends from one-time session-close ranking → real-time query API.

Three-layer insight architecture:
- Structure layer: Atlas (Leo) — file topology, dependency graph
- Semantic layer: THIS — query by meaning, find similar, trace precedents
- Action layer: Routing (AutonomyEngine) — what to do next

Design constraints (Iron Rule 1):
- NO LLM inference (embedding/generation)
- BM25 text ranking + Maya's weighting formula
- Memory-resident index (~10K docs Labs scale)
- Incremental update by mtime

Usage:
    from scripts.labs_rag_query import LabsRAG

    rag = LabsRAG()
    hits = rag.query("AutonomyEngine", top_k=5)
    similar = rag.find_similar_to("reports/proposals/charter_amendment_014_*.md")
    predecessors = rag.find_predecessors("circuit breaker")

CLI:
    python3 scripts/labs_rag_query.py "AutonomyEngine"
    python3 scripts/labs_rag_query.py --similar reports/proposals/charter_amendment_014_*.md
    python3 scripts/labs_rag_query.py --predecessors "circuit breaker"

Author: Jordan Lee (Domains Engineer)
Board-approved: 2026-04-13 (AMENDMENT-014 follow-up — semantic layer MVP)
"""

import sys
import time
import json
import pickle
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math


# ============================================================================
# Models
# ============================================================================

@dataclass
class RetrievalHit:
    """Single retrieval result."""
    file_path: str
    score: float
    snippet: str  # first 200 chars
    mtime: float
    match_context: str = ""  # why it matched

    def __repr__(self):
        return f"<Hit {self.file_path} score={self.score:.3f}>"


# ============================================================================
# BM25 Ranker (No LLM, pure text statistics)
# ============================================================================

class BM25Ranker:
    """BM25 ranking without external dependencies.

    k1=1.5, b=0.75 are standard BM25 parameters.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs = defaultdict(int)  # term -> num docs containing it
        self.doc_lengths = {}  # doc_id -> length
        self.doc_term_freqs = {}  # doc_id -> {term: freq}
        self.avg_doc_length = 0.0
        self.num_docs = 0

    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase + split on non-alphanum."""
        text = text.lower()
        tokens = re.findall(r'\b[a-z0-9_]+\b', text)
        return tokens

    def build_index(self, documents: Dict[str, str]):
        """Build BM25 index from doc_id -> text mapping."""
        self.num_docs = len(documents)

        # First pass: compute term frequencies per doc
        for doc_id, text in documents.items():
            tokens = self.tokenize(text)
            term_freq = defaultdict(int)
            for token in tokens:
                term_freq[token] += 1

            self.doc_term_freqs[doc_id] = dict(term_freq)
            self.doc_lengths[doc_id] = len(tokens)

            # Update global doc frequencies
            for term in term_freq:
                self.doc_freqs[term] += 1

        # Compute average doc length
        if self.num_docs > 0:
            self.avg_doc_length = sum(self.doc_lengths.values()) / self.num_docs

    def score(self, query: str, doc_id: str) -> float:
        """Compute BM25 score for query against doc_id."""
        if doc_id not in self.doc_term_freqs:
            return 0.0

        query_tokens = self.tokenize(query)
        doc_term_freq = self.doc_term_freqs[doc_id]
        doc_length = self.doc_lengths[doc_id]

        score = 0.0
        for term in query_tokens:
            if term not in doc_term_freq:
                continue

            tf = doc_term_freq[term]
            df = self.doc_freqs.get(term, 0)

            # IDF component
            idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1.0)

            # TF component with BM25 normalization
            norm = self.k1 * (1 - self.b + self.b * (doc_length / max(self.avg_doc_length, 1)))
            tf_component = (tf * (self.k1 + 1)) / (tf + norm)

            score += idf * tf_component

        return score

    def rank(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Rank all documents by BM25 score."""
        scores = []
        for doc_id in self.doc_term_freqs:
            score = self.score(query, doc_id)
            if score > 0:
                scores.append((doc_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# ============================================================================
# Labs RAG (Semantic Layer)
# ============================================================================

class LabsRAG:
    """Labs knowledge retrieval system.

    Indexes:
    - knowledge/{role}/skills|lessons|decisions|theory|gaps|feedback/
    - reports/proposals/
    - reports/daily/
    - governance/
    - BOARD_PENDING.md, priority_brief.md, DISPATCH.md

    Excludes:
    - .gitignore patterns
    - __pycache__
    - *.bak, *.pyc, *.db
    """

    def __init__(
        self,
        knowledge_root: Optional[Path] = None,
        reports_root: Optional[Path] = None,
        weights: Optional[Dict] = None,
        ystar_gov_root: Optional[Path] = None,
    ):
        self.company_root = Path(__file__).parent.parent
        self.knowledge_root = knowledge_root or self.company_root / "knowledge"
        self.reports_root = reports_root or self.company_root / "reports"

        # Y-star-gov repo integration (sibling workspace)
        if ystar_gov_root is None:
            ystar_gov_root = self.company_root.parent / "Y-star-gov"
        self.ystar_gov_root = ystar_gov_root if ystar_gov_root.exists() else None

        # Weighting config (from Maya's wisdom_extractor_v2)
        default_weights = {
            "time_decay_half_life_hours": 6.0,
            "board_multiplier": 10.0,
            "role_multiplier": 5.0,
        }
        self.weights = weights or default_weights

        # Index state
        self.ranker = BM25Ranker()
        self.doc_metadata = {}  # doc_id -> {path, mtime, role, snippet}
        self.index_mtime = 0.0  # when index was built
        self.cache_path = self.company_root / ".labs_rag_index.pkl"

        # Build or load index
        self._load_or_build_index()

    def _is_indexable(self, path: Path) -> bool:
        """Check if file should be indexed."""
        name = path.name

        # Exclude patterns
        if any([
            name.startswith('.'),
            name.endswith('.bak'),
            name.endswith('.pyc'),
            name.endswith('.db'),
            '__pycache__' in str(path),
            'node_modules' in str(path),
            '.git' in str(path),
        ]):
            return False

        # Include only text files
        if path.suffix in ['.md', '.py', '.txt', '.json', '.yaml', '.yml']:
            return True

        # Special files
        if name in ['BOARD_PENDING.md', 'DISPATCH.md', 'priority_brief.md']:
            return True

        return False

    def _extract_role(self, path: Path) -> Optional[str]:
        """Extract agent role from path."""
        parts = path.parts
        if 'knowledge' in parts:
            idx = parts.index('knowledge')
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return None

    def _scan_files(self) -> Dict[str, Dict]:
        """Scan all indexable files and return metadata."""
        files = {}

        # Scan knowledge/
        if self.knowledge_root.exists():
            for f in self.knowledge_root.rglob('*'):
                if f.is_file() and self._is_indexable(f):
                    doc_id = str(f.relative_to(self.company_root))
                    files[doc_id] = {
                        'path': f,
                        'mtime': f.stat().st_mtime,
                        'role': self._extract_role(f),
                    }

        # Scan reports/
        if self.reports_root.exists():
            for f in self.reports_root.rglob('*'):
                if f.is_file() and self._is_indexable(f):
                    doc_id = str(f.relative_to(self.company_root))
                    files[doc_id] = {
                        'path': f,
                        'mtime': f.stat().st_mtime,
                        'role': None,
                    }

        # Scan governance/
        gov_dir = self.company_root / "governance"
        if gov_dir.exists():
            for f in gov_dir.rglob('*'):
                if f.is_file() and self._is_indexable(f):
                    doc_id = str(f.relative_to(self.company_root))
                    files[doc_id] = {
                        'path': f,
                        'mtime': f.stat().st_mtime,
                        'role': None,
                    }

        # Special files
        for special in ['BOARD_PENDING.md', 'DISPATCH.md', 'priority_brief.md']:
            special_path = self.company_root / special
            if special_path.exists():
                doc_id = special
                files[doc_id] = {
                    'path': special_path,
                    'mtime': special_path.stat().st_mtime,
                    'role': None,
                }

        # Y-star-gov repo (sibling workspace — index ystar/ source code)
        if self.ystar_gov_root:
            ystar_src = self.ystar_gov_root / "ystar"
            if ystar_src.exists():
                for f in ystar_src.rglob('*.py'):
                    if f.is_file() and self._is_indexable(f):
                        # Use relative path with Y-star-gov prefix
                        doc_id = f"Y-star-gov/{f.relative_to(self.ystar_gov_root)}"
                        files[doc_id] = {
                            'path': f,
                            'mtime': f.stat().st_mtime,
                            'role': None,
                        }

        return files

    def _build_index(self):
        """Build BM25 index from scratch."""
        files_meta = self._scan_files()
        documents = {}

        print(f"[LabsRAG] Indexing {len(files_meta)} files...", file=sys.stderr)

        for doc_id, meta in files_meta.items():
            try:
                text = meta['path'].read_text(errors='replace')
                documents[doc_id] = text

                # Store metadata
                snippet = text[:200].replace('\n', ' ')
                self.doc_metadata[doc_id] = {
                    'path': str(meta['path']),
                    'mtime': meta['mtime'],
                    'role': meta['role'],
                    'snippet': snippet,
                }
            except Exception as e:
                print(f"[WARN] Failed to index {doc_id}: {e}", file=sys.stderr)

        # Build BM25 index
        self.ranker.build_index(documents)
        self.index_mtime = time.time()

        # Save cache
        self._save_cache()

        print(f"[LabsRAG] Index built: {len(documents)} docs", file=sys.stderr)

    def _save_cache(self):
        """Save index to cache."""
        try:
            cache_data = {
                'ranker': self.ranker,
                'doc_metadata': self.doc_metadata,
                'index_mtime': self.index_mtime,
            }
            with open(self.cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"[WARN] Failed to save index cache: {e}", file=sys.stderr)

    def _load_cache(self) -> bool:
        """Load index from cache. Returns True if successful."""
        if not self.cache_path.exists():
            return False

        try:
            with open(self.cache_path, 'rb') as f:
                cache_data = pickle.load(f)

            self.ranker = cache_data['ranker']
            self.doc_metadata = cache_data['doc_metadata']
            self.index_mtime = cache_data['index_mtime']

            print(f"[LabsRAG] Loaded index cache: {len(self.doc_metadata)} docs", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[WARN] Failed to load index cache: {e}", file=sys.stderr)
            return False

    def _load_or_build_index(self):
        """Load from cache or build fresh index."""
        if not self._load_cache():
            self._build_index()

    def _compute_weighted_score(
        self,
        bm25_score: float,
        doc_id: str,
        role_filter: Optional[str],
        time_decay_days: int,
    ) -> float:
        """Apply Maya's weighting: time decay × Board × role."""
        meta = self.doc_metadata.get(doc_id, {})

        # Base BM25 score
        score = bm25_score

        # Time decay (newer = higher)
        now = time.time()
        doc_mtime = meta.get('mtime', now)
        age_hours = (now - doc_mtime) / 3600.0
        half_life = self.weights['time_decay_half_life_hours']
        time_weight = 1.0 / (1.0 + age_hours / half_life)

        # Enforce time_decay_days cutoff
        if time_decay_days > 0:
            age_days = age_hours / 24.0
            if age_days > time_decay_days:
                time_weight *= 0.1  # Heavy penalty for old docs

        # Board annotation (10x weight for board-related docs)
        board_weight = 1.0
        snippet = meta.get('snippet', '').lower()
        if any(k in snippet for k in ['board', '纠偏', 'board_decision', 'board_correction']):
            board_weight = self.weights['board_multiplier']

        # Role relevance (5x weight for matching role)
        role_weight = 1.0
        if role_filter and meta.get('role') == role_filter:
            role_weight = self.weights['role_multiplier']

        final_score = score * time_weight * board_weight * role_weight
        return final_score

    def query(
        self,
        q: str,
        top_k: int = 5,
        role: Optional[str] = None,
        time_decay_days: int = 90,
    ) -> List[RetrievalHit]:
        """Query knowledge base by keyword/phrase.

        Args:
            q: Query string
            top_k: Number of results to return
            role: Filter by agent role (ceo/cto/...)
            time_decay_days: Heavily penalize docs older than N days (0 = no penalty)

        Returns:
            List of RetrievalHit sorted by weighted score
        """
        # BM25 ranking
        bm25_results = self.ranker.rank(q, top_k=top_k * 3)  # Over-retrieve for reranking

        # Apply weighted scoring
        hits = []
        for doc_id, bm25_score in bm25_results:
            weighted_score = self._compute_weighted_score(
                bm25_score, doc_id, role, time_decay_days
            )

            meta = self.doc_metadata.get(doc_id, {})
            hit = RetrievalHit(
                file_path=doc_id,
                score=weighted_score,
                snippet=meta.get('snippet', ''),
                mtime=meta.get('mtime', 0.0),
                match_context=f"bm25={bm25_score:.2f}"
            )
            hits.append(hit)

        # Re-sort by weighted score
        hits.sort(key=lambda x: x.score, reverse=True)
        return hits[:top_k]

    def find_similar_to(self, file_path: str, top_k: int = 5) -> List[RetrievalHit]:
        """Find documents similar to given file.

        Uses first 500 chars of file as query.
        """
        target_path = Path(file_path)
        if not target_path.exists():
            # Try relative to company_root
            target_path = self.company_root / file_path

        if not target_path.exists():
            return []

        try:
            text = target_path.read_text(errors='replace')
            query_text = text[:500]  # Use first 500 chars as query
            return self.query(query_text, top_k=top_k + 1)  # +1 to exclude self
        except Exception as e:
            print(f"[ERROR] Failed to read {file_path}: {e}", file=sys.stderr)
            return []

    def find_predecessors(self, concept: str) -> List[RetrievalHit]:
        """Find historical decisions/discussions about concept.

        Prioritizes older docs (reverse time decay).
        """
        # Query with concept
        bm25_results = self.ranker.rank(concept, top_k=20)

        # Apply reverse time decay (older = higher)
        hits = []
        now = time.time()
        for doc_id, bm25_score in bm25_results:
            meta = self.doc_metadata.get(doc_id, {})
            doc_mtime = meta.get('mtime', now)

            # Reverse time weight (older = higher)
            age_days = (now - doc_mtime) / 86400.0
            time_weight = 1.0 + (age_days / 30.0)  # +1 per 30 days

            # Board weight
            board_weight = 1.0
            snippet = meta.get('snippet', '').lower()
            if any(k in snippet for k in ['board', 'decision', 'approved', 'rejected']):
                board_weight = 5.0

            weighted_score = bm25_score * time_weight * board_weight

            hit = RetrievalHit(
                file_path=doc_id,
                score=weighted_score,
                snippet=meta.get('snippet', ''),
                mtime=doc_mtime,
                match_context=f"predecessor bm25={bm25_score:.2f} age_days={age_days:.1f}"
            )
            hits.append(hit)

        hits.sort(key=lambda x: x.score, reverse=True)
        return hits[:10]

    def rebuild_index(self):
        """Force rebuild index (for testing or manual refresh)."""
        self._build_index()


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse

    ap = argparse.ArgumentParser(description="Labs RAG Query — Semantic layer")
    ap.add_argument('query', nargs='?', help='Query string (default mode)')
    ap.add_argument('--similar', metavar='PATH', help='Find files similar to PATH')
    ap.add_argument('--predecessors', metavar='CONCEPT', help='Find historical decisions about CONCEPT')
    ap.add_argument('--top-k', type=int, default=5, help='Number of results (default: 5)')
    ap.add_argument('--role', help='Filter by agent role (ceo/cto/...)')
    ap.add_argument('--time-decay-days', type=int, default=90, help='Penalize docs older than N days (0=no penalty)')
    ap.add_argument('--rebuild', action='store_true', help='Force rebuild index')
    args = ap.parse_args()

    # Initialize RAG
    rag = LabsRAG()

    if args.rebuild:
        print("Rebuilding index...")
        rag.rebuild_index()
        print("Index rebuilt.")
        return 0

    # Execute query mode
    if args.similar:
        hits = rag.find_similar_to(args.similar, top_k=args.top_k)
        print(f"\n=== Files similar to {args.similar} ===\n")
    elif args.predecessors:
        hits = rag.find_predecessors(args.predecessors)
        print(f"\n=== Historical decisions about '{args.predecessors}' ===\n")
    elif args.query:
        hits = rag.query(args.query, top_k=args.top_k, role=args.role, time_decay_days=args.time_decay_days)
        print(f"\n=== Query: '{args.query}' ===\n")
    else:
        ap.print_help()
        return 1

    # Display results
    if not hits:
        print("(No results found)")
        return 0

    for i, hit in enumerate(hits, 1):
        age_days = (time.time() - hit.mtime) / 86400.0
        print(f"{i}. {hit.file_path}")
        print(f"   Score: {hit.score:.3f} | Age: {age_days:.1f} days | {hit.match_context}")
        print(f"   Snippet: {hit.snippet[:150]}...")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
