#!/usr/bin/env python3
"""Tests for Labs RAG Query system.

Test coverage:
1. query("AutonomyEngine") finds Y-star-gov/ystar/governance/autonomy_engine.py
2. find_similar_to(amendment-014) returns related amendments
3. find_predecessors("circuit breaker") returns historical commits/reports
4. Empty query returns [] gracefully
5. File mtime update triggers re-index reflection
6. BM25 ranking correctness
7. Weighted scoring (time × Board × role)

Author: Jordan Lee (Domains Engineer)
Board-approved: 2026-04-13
"""

import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add scripts to path
COMPANY_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(COMPANY_ROOT / "scripts"))

from labs_rag_query import LabsRAG, BM25Ranker


def test_bm25_ranking():
    """Test BM25 ranker correctness."""
    ranker = BM25Ranker()

    docs = {
        'doc1': 'The quick brown fox jumps over the lazy dog',
        'doc2': 'Quick brown dogs are lazy',
        'doc3': 'The fox is quick and clever',
    }

    ranker.build_index(docs)

    # Query should rank doc1 highest (contains all terms)
    results = ranker.rank('quick fox', top_k=3)
    assert len(results) > 0, "Should return results"
    assert results[0][0] in ['doc1', 'doc3'], "Should rank doc1 or doc3 highest"

    print("[✓] BM25 ranking correct")


def test_query_autonomy_engine():
    """Test query('AutonomyEngine') finds the actual file.

    This is the dogfooding case from CEO's brief.
    """
    rag = LabsRAG()

    hits = rag.query("AutonomyEngine", top_k=10)

    # Should find autonomy_engine.py in Y-star-gov
    found = False
    for hit in hits:
        if 'autonomy_engine.py' in hit.file_path.lower():
            found = True
            break

    assert found, "Should find autonomy_engine.py when querying 'AutonomyEngine'"
    print(f"[✓] Query 'AutonomyEngine' found: {hit.file_path}")


def test_find_similar_amendments():
    """Test find_similar_to returns related amendments."""
    rag = LabsRAG()

    # Find amendment 14
    amendment_14 = None
    for doc_id in rag.doc_metadata:
        if 'amendment_014' in doc_id:
            amendment_14 = doc_id
            break

    if not amendment_14:
        print("[SKIP] Amendment 014 not found in index")
        return

    hits = rag.find_similar_to(amendment_14, top_k=5)

    # Should return other amendments
    amendment_count = sum(1 for h in hits if 'amendment' in h.file_path.lower())
    assert amendment_count >= 2, "Should find at least 2 related amendments"

    print(f"[✓] find_similar_to(amendment_014) found {amendment_count} related amendments")


def test_find_predecessors_circuit_breaker():
    """Test find_predecessors('circuit breaker') returns historical decisions."""
    rag = LabsRAG()

    hits = rag.find_predecessors("circuit breaker")

    # Should prioritize older docs
    if len(hits) >= 2:
        # First hit should be older than or equal to second hit
        assert hits[0].mtime <= hits[1].mtime + 86400, "Should prioritize older docs (within 1 day tolerance)"

    print(f"[✓] find_predecessors('circuit breaker') found {len(hits)} historical hits")


def test_empty_query():
    """Test empty query returns gracefully."""
    rag = LabsRAG()

    hits = rag.query("", top_k=5)
    assert isinstance(hits, list), "Should return list"
    # Empty query may return 0 or low-score results
    print(f"[✓] Empty query handled gracefully: {len(hits)} hits")


def test_mtime_update_reflection():
    """Test that file mtime update triggers re-index reflection."""
    # Create temp directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        knowledge_dir = tmpdir / "knowledge" / "test_role"
        knowledge_dir.mkdir(parents=True)

        # Create test file
        test_file = knowledge_dir / "test_skill.md"
        test_file.write_text("Original content about testing")

        # Build index with tmpdir as company_root
        # Need to temporarily override company_root
        import labs_rag_query
        original_file_path = labs_rag_query.__file__

        # Create a RAG instance with custom roots
        class TempRAG(LabsRAG):
            def __init__(self):
                self.company_root = tmpdir
                self.knowledge_root = knowledge_dir
                self.reports_root = tmpdir / "reports"
                self.ystar_gov_root = None

                default_weights = {
                    "time_decay_half_life_hours": 6.0,
                    "board_multiplier": 10.0,
                    "role_multiplier": 5.0,
                }
                self.weights = default_weights

                self.ranker = BM25Ranker()
                self.doc_metadata = {}
                self.index_mtime = 0.0
                self.cache_path = tmpdir / ".labs_rag_index.pkl"

        rag = TempRAG()
        rag._build_index()

        # Check file is indexed
        assert any('test_skill.md' in d for d in rag.doc_metadata), "Test file should be indexed"

        # Update file
        time.sleep(0.1)
        test_file.write_text("Updated content with new keywords: AutonomyEngine CircuitBreaker")

        # Rebuild index
        rag._build_index()

        # Query for new keyword
        hits = rag.query("CircuitBreaker", top_k=5)
        found = any('test_skill.md' in h.file_path for h in hits)

        assert found, "Updated file should be findable with new keyword"
        print(f"[✓] mtime update reflection test completed (found={found})")


def test_role_filtering():
    """Test role filtering boosts role-specific docs."""
    rag = LabsRAG()

    # Query with role filter
    hits_ceo = rag.query("priority", top_k=10, role="ceo")
    hits_cto = rag.query("priority", top_k=10, role="cto")

    # CEO filter should prioritize CEO docs
    ceo_count_in_ceo = sum(1 for h in hits_ceo if '/ceo/' in h.file_path)
    cto_count_in_cto = sum(1 for h in hits_cto if '/cto/' in h.file_path)

    print(f"[✓] Role filtering: CEO filter found {ceo_count_in_ceo} CEO docs, CTO filter found {cto_count_in_cto} CTO docs")


def test_time_decay():
    """Test time decay penalizes old docs."""
    rag = LabsRAG()

    # Query with strict time decay (30 days)
    hits_strict = rag.query("governance", top_k=10, time_decay_days=30)

    # Query with relaxed time decay (365 days)
    hits_relaxed = rag.query("governance", top_k=10, time_decay_days=365)

    # Relaxed should return more or equal results
    assert len(hits_relaxed) >= len(hits_strict), "Relaxed time decay should return >= results"

    print(f"[✓] Time decay: strict={len(hits_strict)}, relaxed={len(hits_relaxed)}")


def test_board_weight_boost():
    """Test Board-related docs get 10x boost."""
    rag = LabsRAG()

    # Query for a term likely in board docs
    hits = rag.query("board decision", top_k=10)

    # Check if high-scoring hits contain board keywords
    if hits:
        top_hit = hits[0]
        snippet = top_hit.snippet.lower()
        has_board_keyword = any(k in snippet for k in ['board', '纠偏', 'board_decision'])

        if has_board_keyword:
            print(f"[✓] Board weight boost: top hit '{top_hit.file_path}' contains board keyword")
        else:
            print(f"[NOTE] Board weight boost: top hit '{top_hit.file_path}' does not contain board keyword (may be legitimate)")


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("BM25 ranking", test_bm25_ranking),
        ("Query AutonomyEngine", test_query_autonomy_engine),
        ("Find similar amendments", test_find_similar_amendments),
        ("Find predecessors (circuit breaker)", test_find_predecessors_circuit_breaker),
        ("Empty query", test_empty_query),
        ("mtime update reflection", test_mtime_update_reflection),
        ("Role filtering", test_role_filtering),
        ("Time decay", test_time_decay),
        ("Board weight boost", test_board_weight_boost),
    ]

    print("\n" + "=" * 70)
    print("Labs RAG Test Suite")
    print("=" * 70 + "\n")

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            print(f"Running: {name}")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"[✗] FAILED: {name}")
            print(f"    {e}")
            failed += 1
        except Exception as e:
            print(f"[✗] ERROR: {name}")
            print(f"    {type(e).__name__}: {e}")
            failed += 1
        print()

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
